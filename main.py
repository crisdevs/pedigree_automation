import requests, pyperclip, time
from API_KEYS import api_keys, CSE_ID
from tv_dictionary import brand_logic
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from openai import OpenAI
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager
import threading
from ctypes import windll
import re

#Fix the blurryness of text
windll.shcore.SetProcessDpiAwareness(1)

brands = [
  'Samsung',
  'LG',
  'Vizio',
  'TCL',
  'Sony',
  'Panasonic',
  'Hisense',
  'Roku',
  'Toshiba'
]

with open('./files/unfiltered_pedigree_questions.txt', 'r') as file:
      tv_questions = file.read()
file.close()
tv_questions = tv_questions.split('\n')
def loading_window(task_name, task, *args):
    loading = tk.Toplevel(root)
    #Set up window size for loading window
    loading.geometry('600x200')
    #Set up layout of window
    loading.columnconfigure(0, weight=1)
    loading.rowconfigure(0, weight=1)
    
    loading_frame = tk.Frame(loading)
    loading_frame.grid(row=0, column=0, sticky="nsew")
    loading_frame.columnconfigure(0, weight=1)
    loading_frame.rowconfigure(0, weight=1)
    loading_frame.rowconfigure(1, weight=1)
    
    # Bring window to the front
    loading.lift()          
    # Force focus on window
    loading.focus_force()    
    # Prevents interaction with main window
    loading.grab_set()   
    #Set up text and layout of label and progress bar
    task_label = Label(loading_frame, text= 'Working on: ' + task_name)
    task_label.grid(row=0, column=0, pady=(10 , 2), sticky= "nsew")
    progressbar = ttk.Progressbar(loading_frame, mode="indeterminate")
    progressbar.grid(row=1, column=0, padx=20, sticky="new")
    progressbar.start()
    #Need to create another thread so chatgpt api calls can run in the background without freezing UI
    task_thread =  threading.Thread(target=lambda:task(*args), daemon=True)
    task_thread.start()
        # Periodically check if thread is done Will be considered done when data from chatgpt is retrieved.
    def check_if_done():
        if not task_thread.is_alive():  # If thread has finished
            loading.destroy()  # Close the loading window
        else:
            loading.after(500, check_if_done)  # Check again after 500ms (Will call itself)

    check_if_done() 
# Will make the api call to the custom google search and will feed the results to 
# chatgpt(API call) and ask for the manufacturer link 
def get_url(brand, model):
    product_type = 'TV'
    #Used as the search term when calling the google search api
    query = f"{brand} {model}"
    url  = None
    # Will perform a google search using the brand and model entered by the user.
    search_results = google_search(query, api_keys['google_search'], CSE_ID)
    url = ask_chatgpt(f"""
                      Here is some information I found on the web:\n{search_results}\n\n
                      Now, based on this information, answer the following question: 
                      'What is the product page link for the {brand} {model} {product_type} and only return the url. 
                      Prioritize website links from the manufacturer website first and if you cannot find the 
                      website url from the manufacturer then prioritize URLs from best buy.'
                      """)
    return url

def manual_text_window(brand, model, url, prev_window):
    prev_window.destroy()
    manual_text_win = tk.Toplevel(root)
    manual_text_win.geometry('900x900')
    manual_text_win.rowconfigure(0, weight=1)
    manual_text_win.columnconfigure(0, weight=1)
    manual_text_win.lift()          
    manual_text_win.focus_force()    
    manual_text_win.grab_set()
       
    manual_text_frame = tk.Frame(manual_text_win)
    manual_text_frame.rowconfigure(0, weight=1)
    manual_text_frame.rowconfigure(1, weight=1)
    manual_text_frame.rowconfigure(2, weight=1)
    manual_text_frame.columnconfigure(0, weight=1)
    manual_text_frame.grid(column=0, row= 0, sticky="nsew")
    
    label = tk.Label(manual_text_frame, text= "Enter text below")
    label.columnconfigure(0, weight=1)
    entry = tk.Text(manual_text_frame, width=70, height= 20)
    
    def manual_text_processing(brand, model, text, url, text_window):
        # entry.get("1.0", "end")
       final_pedigree_answers = get_pedigree_answers(brand,model,text,url)
       text_window.destroy()
       open_result_window(final_pedigree_answers)
       
    
    button = tk.Button(manual_text_frame, text= "Get answers", command= lambda: loading_window("Answering pedigree questions", manual_text_processing, brand, model, entry.get("1.0", "end") ,url, manual_text_win))
    
    label.grid(row=0, column=0, sticky="nsew")
    entry.grid(row=1, column=0)
    button.grid(row=2, column=0)

def searchWithBrandModel (brand, model, is_manual):
   url = get_url(brand, model)
   
   new_window = tk.Toplevel(root)
   new_window.geometry('1200x250')
   new_window.title('URL Entry')
   new_window.columnconfigure(0, weight=1)
   new_window.rowconfigure(0, weight=1)

   confirm_url_frame = tk.Frame(new_window)
   confirm_url_frame.grid(row=0, column=0, sticky="nsew")
   confirm_url_frame.columnconfigure(0, weight=1)
   confirm_url_frame.rowconfigure(0, weight=1)
   confirm_url_frame.rowconfigure(1, weight=1)
   confirm_url_frame.rowconfigure(2, weight=1)
   

   new_url_label = tk.Label(confirm_url_frame, text = "Confirm That this is the correct url you wish to grab specs from").grid(row=0, column=0)
   new_url_text = tk.Entry(confirm_url_frame, width=70)
   new_url_text.grid(row=1, column=0)
   new_url_text.insert(0, url)
   button_frame = tk.Frame(confirm_url_frame)
   button_frame.grid(row=2, column=0)
   button_func = None
   func_text = None
   args = None
   print(is_manual)
   if is_manual == True:
       func_text = "loading text window"
       button_func = manual_text_window
       args = [brand, model, new_url_text.get(), new_window]
   else:
       func_text = 'Retrieving specs from model page.'
       button_func = main
       args = [brand, model, new_url_text.get(), new_window]
       
   enter_url = tk.Button(button_frame, text = "Confirm", command=lambda:loading_window(func_text, button_func, *args))
   copy_url = tk.Button(button_frame, text = "Copy URL", command=lambda:pyperclip.copy(new_url_text.get()))
   enter_url.grid(row=0, column=0, padx=30)
   copy_url.grid(row=0, column=1, padx=30)
   new_window.grab_set()
    
# #To help inserting values multiple times in the list.
def insertMultiple(arr, index, val, quantity):
  for i in range(quantity):
    arr.insert(index, val)

# #Function for doing the google search.
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
    completion =  client.chat.completions.create(
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
 

# #This is to format the response from chatgpt to have answers in the right place in the excel workbook
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

def get_spec_info(brand, product_link):  
  
  #Get the latest driver of Chrome so that it does not need to be included with source code
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
  driver.maximize_window()
  driver.get(product_link)
  time.sleep(2)
  #Get the xpath from the function. Driver needs to be passed for some of the models since we might need to click a button for some of them.
  spec_path = brand_logic(brand, driver)
  #spec_path[0] = By.XPATH or BY.TAG_NAME, spec_path[1] = element xpath(Reference of html element of specs) or 'body'
#   product_specs = driver.find_element(spec_path[0], spec_path[1]).get_attribute('textContent')
  product_specs = driver.find_element(By.TAG_NAME, "body").get_attribute('textContent')
  product_specs = re.sub(r'<[^>]+>', '', product_specs)
  product_specs = re.sub(r'\{[^}]*\}', '', product_specs)
  product_specs = re.sub(r'\[[^\]]*\]', '', product_specs)
  product_specs = re.sub(r'\s+', ' ', product_specs).strip()
  driver.quit()
  return product_specs

def get_pedigree_answers(brand, model, data, url):
    #Pedigree questions are held in a seperate file that is not tracked by Git.
    pedigree_questions = None
    with open('./files/pedigree_questions.txt', 'r') as file:
        pedigree_questions = file.read()
    file.close()
    # spec_obj['specs']
    pedigree_answers = ask_chatgpt(f"""{data}\n I have provided some unfiltered data web scraped from the {brand} {model} TV product page. Based off of this data can you answer the following questions and please only provide the answers separated by commas and exclude the question numbers. 
                                    For each question there will be a list of directions on how to answer each question inside parentheses. Please follow those directions and do not create any data that is not listed in the web scraped data. Here are the questions:\n{pedigree_questions}""")
    #Add the link of the url used to the answers
    pedigree_answers += f', {url}'
    #Format answers
    final_pedigree_specs = format_pedigree_answer(pedigree_answers)
    return final_pedigree_specs

def main(brand, model, product_link, prev_window):
  prev_window.destroy()
  
  #This was a quick and easy way to get the domain name in the URL
  domain = urlparse(product_link).netloc
  if domain == 'www.bestbuy.com':
      brand = 'bestbuy'
  elif domain == 'www.lg.com':
      #Have to add #pdp_specs to the URL so that it automatically takes us to the specs section
      product_link += '#pdp_specs'
  specs = get_spec_info(brand, product_link)
  final_pedigree_specs = get_pedigree_answers(brand, model, specs, product_link)
  open_result_window(final_pedigree_specs)

def open_result_window (results):
    # results = main(brand, model, product_link)
    result_window = tk.Toplevel(root)
    result_window.geometry('1200x1200')

    # Bring to front
    result_window.lift()          
    # Force focus
    result_window.focus_force()    
    # Prevents interaction with main window
    result_window.grab_set()   

    results_arr = results.split("\t")
    
    result_window.columnconfigure(0, weight=1)
    result_window.rowconfigure(0, weight=1)
    
    result_window_frame = tk.Frame(result_window, bd=0, highlightthickness=0)
    result_window_frame.grid(row=0,column=0, sticky="nsew")
    result_window_frame.columnconfigure(0, weight=1)
    result_window_frame.rowconfigure(0, weight=1)
    result_window_frame.rowconfigure(1, weight=0)
    
    result_tree = ttk.Treeview(result_window_frame)
    style = ttk.Style(result_window)
    style.configure("Treeview", rowheight=60)
    result_tree.grid(row=0,column=0, sticky="nsew")
    result_tree['column'] = ['Question', 'Answer']
    result_tree['show'] = 'headings'
    
    copy_button = tk.Button(result_window_frame, text="Copy Specs", command=lambda:copy_to_clipboard(results))
    copy_button.grid(column=0, row=1, pady=10)

    for col in result_tree['column']:
      result_tree.heading(col, text=col)
      result_tree.column(col, width=250)
    i = 0
    while(i < len(tv_questions)):
      result_tree.insert("", "end", values=(tv_questions[i], results_arr[i]))
      i+=1
      
    result_scrollbar = tk.Scrollbar(result_window_frame, orient="vertical", command=result_tree.yview)
    result_tree.configure(yscrollcommand=result_scrollbar.set)
    result_scrollbar.grid(row=0, column=1,sticky="ns", pady=0)

    def copy_to_clipboard(results):
       pyperclip.copy(results)
       messagebox.showinfo('Copy to clipboard', 'Specs were copied to clipboard')


root = tk.Tk()
#Set window size
root.geometry('500x400')
root.title('ChatGPT Pedigree Taker')
root.iconbitmap('CR_logo.ico')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
search_frame = tk.Frame(root)
search_frame.grid(row=0, column=0, sticky="nsew")
search_frame.columnconfigure(0, weight=1)
brandLabel = Label(search_frame, text = 'Brand')
brandInput = ttk.Combobox(search_frame, value=brands)
brandInput.current(0)
brandInput.config(state='readonly')
modelLabel = Label(search_frame, text="Model")
modelInput = Entry(search_frame, width = 23)
is_manual = BooleanVar()
manual_text_mode = Radiobutton(root, text = "Manual text mode", variable = is_manual, value=True)
web_scraping_mode = Radiobutton(root, text = "Web Scraping Mode", variable =is_manual, value=False)

brandLabel.grid(row=0,column=0)
brandInput.grid(row=1,column=0)
modelLabel.grid(row=2,column=0)
modelInput.grid(row=3,column=0)
manual_text_mode.grid(row=4, column=0)
web_scraping_mode.grid(row=5, column=0)


searchButton = tk.Button(search_frame, text="Search", command=lambda:searchWithBrandModel(brandInput.get().lower(), modelInput.get(), is_manual.get())).grid(row=4, column=0, pady=10)
root.mainloop()
