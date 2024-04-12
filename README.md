# NBA Gameday Generator

Generates high-quality .psd templates for NBA basketball posters 🏀

_Libraries/APIs:_

Selenium ✅

ChromeWebDriver 🚗

BeautifulSoup 🍲

Dropbox's REST  API 📦

Adobe Photoshop's REST API 🎨

All of these libraries work together in the gamedayparser.py file to scrape the required data from the internet, modify the files, and read/write/upload the files as required

## How it works

**gamedayparser.py** 

The main file. This brings all the elements together. It starts with fetching NBA Data from websites like NBA LockerVision and statmuse, and then stores that data as local variables. From there, it makes API calls to generate download and upload links, and then modifies JSON files to make layer-level edits using the Photoshop API. All these edits are processed through a cURL command

**colorextraction.py**

This file is run yearly to get the most recent color schemes of NBA jerseys. It extracts the two most prominent colors in the jersey image and converts them to RGB values for gamedayparser.py to use.

**JSON Files**

There are 3 JSON files used in this project. action_request.json, text_request.json, and image_request.json. 
- The action_request takes care of modifying the colors based on the jerseys worn.
- The text_request takes care of modifying the team names, last 5, record, seeding, date, etc.
- The image_request takes care of modifying the team and arena logos.

**Images and Logos**

All images and logos are stored on dropbox and are referred to when needed

## Important API Documentation
Throughout the project, I referred to the following API documentation:

**Photoshop API Documentation**

https://developer.adobe.com/photoshop/photoshop-api-docs/api/

**Dropbox API Documentation**

https://dropbox.github.io/dropbox-api-v2-explorer/#files_get_temporary_link

https://dropbox.github.io/dropbox-api-v2-explorer/#files_get_temporary_upload_link

