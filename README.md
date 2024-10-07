# An AI Powered Pedigree Automation Tool
This is a python script to help automate the spec taking process which includes answering questions based off of specs claimed on manufacturer's websites.
This automation tool uses the following:
* Python
* ChatGPT 4 for deciding the correct URL used and answering the questions
* Selenium for navigating and web scraping the websites
* Google search api for getting the list of google search result links to feed to chatgpt
* The requests api for using a get request on the filtered google search site from the api
* pyperclip for copying the data to the clipboard automatically
* urllib for an easy way to get the domain name of sites
* Webdriver manager which manages the drivers for web browser in this case Chrome
