# Selenium_Web_Scraping_Script
This repository contains two script 1. Selenium+Python script that demonstrates how to run cross-browser tests using BrowserStack. 2. a script to test using Chromedriver. It allows you to test a website across multiple browsers (desktop and mobile) as specified in a config.yaml file. The script uses Selenium WebDriver and integrates with BrowserStack to execute tests on real devices and different browser versions.

# Requirements
Before running the script, make sure you have the following installed:

Python 3.x (Version 3.7 or later)
Selenium: A Python library for automating web browsers.
BrowserStack Local: A BrowserStack utility to test local or private servers.
Need to install required libraries(Requirement.txt)


# Setup Instructions
Sign Up for BrowserStack:
Create an account at BrowserStack. Once signed up, you'll need your username and access key.

Download and Configure ChromeDriver: If you plan to run tests locally on Chrome, download the ChromeDriver for your system from here. Ensure the ChromeDriver_Path is set correctly in the script.

# Create config.yaml:
The config.yaml file holds the configuration for browsers you want to test on BrowserStack. This file should contain your BrowserStack credentials (username and access key) and the browser capabilities (browsers, versions, OS, etc.).

Update ChromeDriver_Path: In the script, set the path to your local chromedriver if you're running tests locally.

# Running the Script
  1.Once you have the environment set up, follow these steps to run the script:

  2.Ensure that you have the config.yaml file in the same directory as the script.
  3.Run the script using the following command:
    python script_name.py

  This will:
    -Read the browser capabilities from config.yaml.
    -Launch tests on the specified browsers in BrowserStack.
    -Scrape the articles from the El Pais website.
    -Save images associated with the articles.
    -Translate article titles using the Rapid API.
    -Analyze the translated titles for repeated words.
    -Return the each repeated words along with its count.

# Best Practices
Ensure the Chromedriver version matches your Chrome browser version.

Handle API rate limits by adjusting delays in the script.

Keep your API key secure and do not share it publicly.
