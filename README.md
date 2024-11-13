# An AI Powered Pedigree Automation Tool
This is a python script to help automate the spec taking process which includes answering questions based off of specs claimed on manufacturer's websites.
This automation tool uses the following:
* Python
* ChatGPT 4 for deciding the correct URL used and answering the questions
* Selenium for navigating and web scraping the websites
* Google search api for getting the list of google search result links to feed to chatgpt
* The requests api for using a get request on the filtered google search site from the api
* pyperclip for copying the data to the clipboard automatically
* Webdriver manager which manages the drivers for web browser in this case Chrome
## How to use
1. First clone this repo
2. Then open a command line terminal and navigate to the saved cloned repo
3. Run `pip install -r ./files/requirements.txt` to download the needed packages
4. This script uses google search api and openai's chatgpt api so api keys will be needed for these packages
5. You will need a seperate file called API_KEYS.py and it should look something like this:
```
 api_keys = {
 "chat_gpt": ENTER API KEY HERE,
 "google_search": ENTER API KEY HERE
} 
CSE_ID = ENTER CSE ID for the google search package
```
7. You should now be able to run the python file and follow the prompts as they display
## A High Level of how it works
1. When you run the Python application the application will prompt you to enter the Brand and model.
2. Enter the brand and model and then the script will use the custom Google search made through the Google search API to make a search using the entered brand and model.
3. Then we will either get no results or a dictionary full of different properties relating to the search results.
4. In this case, we will extract only the links of each result from the Google search.
5. We will then send those list of URLs to chatGPT and prompt ChatGPT to pick the most appropriate URL for that model.
6. Chatgpt will return one URL it has chosen.
7. We will then confirm with the user whether the correct URL is for that model.
8. If:
   - The correct URL then we will continue
   - The wrong URL then it will prompt the user to enter the correct URL
9. Once the URL has been confirmed then it will use selenium to go to the URL
10. Then depending on the brand it will have to navigate to the specs by pressing buttons.
11. It will then web-scrape the specs by getting the text content from the referenced HTML element.
12. It will then send the text content from the website to ChatGPT along with a list of questions located in a different file.
13. Chatgpt will return its answers.
14. Then it will format the answers so each answer can be in the right column in Excel.
15. The formatted answers will then be automatically copied for the user to paste those results into the Excel workbook.
