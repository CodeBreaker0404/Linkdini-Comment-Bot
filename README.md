# Linkdini-Comment-Bot
This project is a Python automation script using Selenium to auto-post comments on LinkedIn posts using your existing Chrome profile. It reads a list of posts and their corresponding comments from a CSV file and posts them one by one with a 1-minute delay between each to avoid spam detection.

##  Features
-  Uses your logged-in Chrome profile – no password or API needed
-  Scrolls and clicks comment buttons reliably using JS fallbacks
-  Supports robust typing into LinkedIn comment boxes
-  Reads post URLs and comments from a CSV file
-  Built-in **60 second delay** between each comment
-  Safe and simple to test


##  Requirements
- Python 3.8 or later
- Google Chrome installed
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) matching your Chrome version
- Python dependencies:
  - `selenium`
  - `pandas`
 
