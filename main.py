import requests, pyperclip, time
from API_KEYS import api_keys, CSE_ID
from tv_dictionary import brand_logic
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
from openai import OpenAI

from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service()
options = webdriver.ChromeOptions()


#To help inserting values multiple times in the list.
def insertMultiple(arr, index, val, quantity):
  for i in range(quantity):
    arr.insert(index, val)

#Function for doing the google search.
def google_search(query, api_key, cse_id):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query
    }
    response = requests.get(url, params=params)
    results = response.json()
    search_links = []
    #Checks to see if the items property exists within results(dictionary). If not then there were no results found.
    if 'items' in results:
        #Looping through a list of items(The search results) inside of the items property inside of the results dictionary
        for item in results['items']:
            #Each array contains a dictionary with the link property which we will append to the search_links list
            search_links.append(item['link'])
    return search_links
#Function for asking chatGPT. Prompt is the prompt that you would like to ask ChatGPT
def ask_chatgpt(prompt):
    client = OpenAI(api_key= api_keys['chat_gpt'])
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
        )
    output = completion.choices[0].message.content
    return output
 
def get_url(brand, model):
    product_type = 'TV'
    query = f"{brand} {model}"
    url  = None
    # Will perform a google search using the brand and model entered by the user.
    search_results = google_search(query, api_keys['google_search'], CSE_ID)
    if not search_results:
        url = input('URL not found please manually search and enter URL below\n')
        return url
    url = ask_chatgpt(f"""
                      Here is some information I found on the web:\n{search_results}\n\n
                      Now, based on this information, answer the following question: 
                      'What is the product page link for the {brand} {model} {product_type} and only return the url. 
                      Prioritize website links from the manufacturer website first and if you cannot find the 
                      website url from the manufacturer then prioritize URLs from best buy.'
                      """)
    isCorrectURL = input(f'Is this the correct URL?(Y/N):{url}\n')
    if isCorrectURL.lower() == 'no' or isCorrectURL.lower() == 'n':
        url = input('Please enter correct url\n')
    return url
#This is to format the response from chatgpt to have answers in the right place in the excel workbook
def format_pedigree_answer(answer):
  #Seperates pedigree answers into a list
  pedigree_specs_arr = answer.split(",")
  final_pedigree_specs_arr = []
  #This was a quick way I found to remove spaces found at the start of each of the answers returned from chatgpt
  for i in pedigree_specs_arr:
        #If the first character was a space in the list
        if i[0] == " ":
            #Append the character after the space in the new list which should be the actual start of the answer
            final_pedigree_specs_arr.append(i[1:])
        #If the first character was not a space then just add to the final list
        else:
            final_pedigree_specs_arr.append(i)
  #Add multiple spaces so that answers will be under the right question in excel
  insertMultiple(final_pedigree_specs_arr, 1, " ", 2)
  insertMultiple(final_pedigree_specs_arr, 4, " ", 2)
  insertMultiple(final_pedigree_specs_arr, 19, " ", 11)
  insertMultiple(final_pedigree_specs_arr, 31, " ", 5)
  #Make the list into a string again but seperated by tabs(cells) for excel
  final_pedigree_specs = "\t".join(final_pedigree_specs_arr)
  
  return final_pedigree_specs

def main():
  #Pedigree questions are held in a seperate file that is not tracked by Git.
  pedigree_questions = None
  with open('./files/pedigree_questions.txt', 'r') as file:
      pedigree_questions = file.read()
  file.close()
  product = input("Please enter brand and model\n")
  #Grabs the brand portion of the string entered by the user
  brand = product.split()[0].lower()
  #Does the same as above but for the model
  model = product.split()[1]
  product_link = get_url(brand, model)
  #This was a quick and easy way to get the domain name in the URL
  domain = urlparse(product_link).netloc
  if domain == 'www.bestbuy.com':
      brand = 'bestbuy'
  elif domain == 'www.lg.com':
      #Have to add #pdp_specs to the URL so that it automatically takes us to the specs section
      product_link += '#pdp_specs'

  #Get the latest driver of Chrome so that it does not need to be included with source code
#   driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
  driver = webdriver.Chrome(service=service, options=options)
  driver.maximize_window()
  driver.get(product_link)
  time.sleep(2)
  #Get the xpath from the function. Driver needs to be passed for some of the models since we might need to click a button for some of them.
  spec_path = brand_logic(brand, driver)
  #spec_path[0] = By.XPATH or BY.TAG_NAME, spec_path[1] = element xpath(Reference of html element of specs) or 'body'
  product_specs = driver.find_element(spec_path[0], spec_path[1]).get_attribute('textContent')
  final_url = driver.current_url
  pedigree_answers = ask_chatgpt(f"""{product_specs}\n I have provided some unfiltered data web scraped from the {brand} {model} TV product page. Based off of this data can you answer the following questions and please only provide the answers seperated by commas and exclude the question numbers. 
                                 For each question there will be a list of directions on how to answer each question inside parentheses. Please follow those directions and do not create any data that is not listed in the web scraped data. Here are the questions:\n{pedigree_questions}""")
  #Add the link of the url used to the answers
  pedigree_answers += f', {final_url}'
  #Format answers
  final_pedigree_specs = format_pedigree_answer(pedigree_answers)
  pyperclip.copy(f"{final_pedigree_specs}")
  print(final_pedigree_specs)
  driver.quit()
  print("Specs were copied please paste the results into the tv workbook")
  #Gives it time so that user can see message
  time.sleep(5)
main()