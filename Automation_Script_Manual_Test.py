import os
import re
import time
import requests
from PIL import Image
from io import BytesIO
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from collections import Counter
import pillow_avif  # Required for AVIF image handling

##### Constants #####
ChromeDriver_Path = "chromedriver.exe"  #Add your chrome driver path
URL = "https://elpais.com/"   #Base URL
Save_Img_To_Dir = "Cover_Image" #Add path to store the cover images
RAPIDAPI_KEY = "API_KEY" #Add Your Secret API Key
RAPIDAPI_HOST = "rapid-translate-multi-traduction.p.rapidapi.com"


#### Step: 1 Setup Selenium ####
def setup_driver():
    service = Service(ChromeDriver_Path)
    driver = webdriver.Chrome(service=service)
    return driver


#### Step: 2 Visit the URL and Scrape the Articles ####
def scrape_articles(driver):
    driver.get(URL)

    # Handle cookies acceptance prompt
    try:
        cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='didomi-notice-agree-button']"))
        )
        cookies_button.click()
        print("Cookies prompt accepted.") #to notify cookies prompt accepted
    except:
        print("No cookies prompt found.")

    # Ensure website load correctly
    assert "EL PAÍS: el periódico global" in driver.title, "Website title does not match"

    # Ensure website text is displayed in Spanish
    html_lang = driver.find_element(By.TAG_NAME, "html").get_attribute("lang")
    assert html_lang == "es-ES", "Website text is not displayed in Spanish"

    # Navigate to the Opinion section of the website
    opinion_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Opinión"))
    )
    opinion_section.click()

    page_source = driver.page_source
    # Extract First 5 Articles using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")
    articles = soup.select("article")[:5]  # Select the first 5 articles
    article_data = []

    for article in articles:
        try:
            # Extract article title and link
            title_element = article.select_one("h2")
            title = title_element.get_text(strip=True) if title_element else "No title found"
            link_element = title_element.find("a")
            link = link_element["href"] if link_element else None

            # Fetch article content using Selenium for the linked page
            if link:
                driver.get(link)

                time.sleep(2)  # Wait for images to be visible in the article before proceeding
                article_page_source = driver.page_source
                article_soup = BeautifulSoup(article_page_source, "html.parser")
                content_element = article_soup.find("article")
                content = content_element.get_text(strip=True) if content_element else "No content found"

                # Extract the cover image
                image_url = None
                image_elements = article_soup.find_all("img", src=True)

                if image_elements:
                    for img in image_elements:
                        src = img.get("src")
                        srcset = img.get("srcset")

                        # Check if the image has a srcset, and prioritize it if available
                        if srcset:
                            image_url = srcset.split(",")[-1].split(" ")[0]  # Get the largest image from the srcset
                            break
                        elif src and not image_url:
                            # Return to the first available src if no srcset is found
                            image_url = src

                if image_url:
                    save_image(title, image_url)
                else:
                    print(f"No image found for article '{title}'")

                # Append article data
                article_data.append({"title": title, "content": content, "image_url": image_url})
        except Exception as e:
            print(f"Error processing articlae: {e}")
        finally:
            driver.get("https://elpais.com/opinion/")  # Return to the Opinion section
            time.sleep(3)
    return article_data


#### Step: 3 Save Image Function ####
def save_image(title, image_url):
    # If image_url is empty or doesn't start with 'http', handle it
    if not image_url.startswith('http'):
        image_url = urljoin(URL, image_url)

    if not os.path.exists(Save_Img_To_Dir):
        os.mkdir(Save_Img_To_Dir)

    clean_title = re.sub(r'[^a-zA-Z0-9]', '_', title[:30])
    image_path = os.path.join(Save_Img_To_Dir, f"{clean_title}.jpg")

    try:
        # Fetch image data from the URL
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))

        # As I noticed images are (.avif) format so need to convert in .jpg
        if image.format.lower() == "avif":
            image = Image.open(BytesIO(image_data)).convert("RGBA")

        # Save image
        image.save(image_path)
        #print(f"Image Saved: {image_path}") to ensure Image is saved at right path
    except Exception as e:
        print(f"Failed to save image for {title}: {e}")


#### Step: 4 Translate Titles By Integrating Rapid Translate API ####
def translate_titles_rapidapi(titles, RAPIDAPI_KEY):
    url = "https://rapid-translate-multi-traduction.p.rapidapi.com/t"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }

    # Store the translated titles in list
    translated_titles = []

    for title in titles:
        payload = {
            "from": "es",  # Source language
            "to": "en",  # Target language
            "q": title  # The text to translate
        }

        try:
            # Make the API request
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Parse the JSON response
            result = response.json()
            if isinstance(result, list):  # If the result is a list
                translated_titles.append(result[0])  # Append the first item (translation)
            else:
                print(f"Unexpected response format for '{title}'. Response: {result}")
                translated_titles.append("Translation unavailable")

        except requests.exceptions.RequestException as e:
            print(f"Failed to translate '{title}': {e}")
            translated_titles.append("Translation failed")

        # Sleep to avoid rate limits (adjust as needed)
        time.sleep(2)

    return translated_titles


#### Step: 5 Analyze Translated Titles ####
def analyze_titles(translated_titles):
    all_words = " ".join(translated_titles).split()
    word_counts = Counter(word.lower() for word in all_words if len(word) > 2)
    repeated_words = {word: count for word, count in word_counts.items() if count > 2}
    return repeated_words


#### Main Function ####
def main():
    driver = setup_driver()
    try:
        # Scrape articles
        articles = scrape_articles(driver)

        # Extract titles
        titles = [article["title"] for article in articles]

        # Print scraped data
        print("\n=== Scraped Articles From Opinion Section ===")
        for article in articles:
            print(f"Title (Spanish): {article['title']}")
            print(f"Content (Spanish): {article['content']}...")
            if article["image_url"]:
                print(f"Image URL: {article['image_url']}") #Showing URL of cover image of article
            print("")

        # Translate titles
        translated_titles = translate_titles_rapidapi(titles, RAPIDAPI_KEY)

        # Print original and translated titles
        print("\n=== Article Titles ===")
        print("Original Titles (Spanish):")
        for title in titles:
            print(f"- {title}")

        print("\nTranslated Titles (English):")
        for translated_title in translated_titles:
            print(f"- {translated_title}")

        # Analyze repeated words in translated headers
        repeated_words = analyze_titles(translated_titles)
        print("\nRepeated Words in Translated Titles ===")
        for word, count in repeated_words.items():
            print(f"{word}: {count}")
            print("==========")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
