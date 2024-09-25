import requests, bs4, pyperclip, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from openai import OpenAI
from selenium.common.exceptions import NoSuchElementException

API_KEY = open("API_KEY.txt", "r").read()
GOOGLE_API_KEY = open("google_api_key.txt", "r").read()
CSE_ID = "31695611ea8bf4daa"

DRIVER_PATH = 'chromedriver-win64/chromedriver.exe'
client = OpenAI(api_key= API_KEY)
service = Service(executable_path=DRIVER_PATH)
options = webdriver.ChromeOptions()
options.add_argument('--kiosk')

def insertMultiple(arr, index, val, quantity):
  for i in range(quantity):
    arr.insert(index, val)

def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        print(f"Element:{xpath}  was not found")
        return False
    return True

def url_check (url):
    response = requests.get(url, verify=False)
    print(response.status_code)
    return response.status_code == 200

def navigate_to_url(xpath_arr, driver):
    for i in xpath_arr:
        driver.find_element(By.XPATH, i).click()

def lg(driver = None):
    return '//*[@id="simple-tabpanel-3"]'

def sony(driver):
    navigate_to_url(['//*[@id="cx-main"]/app-product-details-page/div/app-pdptab-nav/div/div/div/ul/li[3]/a'], driver)    
    if check_exists_by_xpath('//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[3]/button', driver) == False:
        return
    time.sleep(5)
    if check_exists_by_xpath('//*[@id="contentfulModalClose"]', driver):
        driver.find_element(By.XPATH, '//*[@id="contentfulModalClose"]').click()  
    if check_exists_by_xpath('//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[3]/button', driver):
        # body = driver.find_element(By.TAG_NAME, 'body')  
        # body.send_keys(Keys.PAGE_DOWN)
        # body.send_keys(Keys.PAGE_DOWN)
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[3]/button').click()
 
    return '/html/body/app-root/ngb-modal-window/div/div/div'

def samsung(driver):
    if check_exists_by_xpath('//*[@id="#specs"]', driver):
        return '//*[@id="#specs"]'
    elif check_exists_by_xpath('//*[@id="pdp-page"]/div/div/div/section[7]', driver):
        return '//*[@id="pdp-page"]/div/div/div/section[7]'


def vizio(driver = None):
    return '//*[@id="main-content"]/div/div/div/div/div[3]/tech-specs-element/div/div[2]' 

def tcl(driver = None):
    return '//*[@id="cmp-tabs"]/div[3]/div/div/div'

def hisense(driver = None):
    return '//*[@id="ProductDetailsBox8"]'

def toshiba(driver = None):
    return '//*[@id="specifications-drawer"]/div[2]'

def roku(driver = None):
    return '//*[@id="main"]/main/div'
    
def panasonic(driver = None):
    return '//*[@id="rn_AnswerText"]'

def google_search(query, api_key, cse_id):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query
    }
    response = requests.get(url, params=params)
    results = response.json()
    # print(results)
    search_links = []
    if 'items' in results:
        for item in results['items']:
            search_links.append(item['link'])
    return search_links
 
def get_url(brand, model):
    query = f"{brand} {model}"
    url  = None
    
    # Perform Google search
    search_results = google_search(query, GOOGLE_API_KEY, CSE_ID)
    # print(search_results)
    if not search_results:
        url = input('Please enter correct url\n')
        return url
    
    # Get response from OpenAI using the search results
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Here is some information I found on the web:\n{search_results}\n\nNow, based on this information, answer the following question: 'What is the product page link for the {brand} {model} TV and only return the url'"
            }
        ]
        )
    url = completion.choices[0].message.content
    isCorrectURL = input(f'Is this the correct URL?(Y/N):{url}\n')
    if isCorrectURL.lower() == 'no' or isCorrectURL.lower() == 'n':
        url = input('Please enter correct url\n')
    if brand == "lg":
        url+= "#pdp_specs"
    return url
    
    
def main():
  tv = input("Please enter brand and model\n")
  brand = tv.split()[0].lower()
  model = tv.split()[1]
#   print(f'This is the brand: {brand} and the model is {model}')
  tv_link = get_url(brand, model)
  tv_dict = {
    'lg':lg,
    'sony':sony,
    'samsung': samsung,
    'vizio': vizio,
    'tcl': tcl,
    'hisense': hisense,
    'toshiba':toshiba,
    'roku': roku,
    'panasonic': panasonic
}
#   print(tv_link)
  driver = webdriver.Chrome(service=service, options=options)
  driver.get(tv_link)
  time.sleep(5)
  tv_func = tv_dict[brand]
  spec_xpath = tv_func(driver)
  tv_specs = driver.find_element(By.XPATH, spec_xpath).get_attribute('textContent')
  final_url = driver.current_url
#   print(tv_specs + '\n\n\n\n')
  completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Here is some unfiltered data here:{tv_specs} for the {brand} {model} TV. Based off of this data can you answer the following questions and please only provide the answers seperated by commas and exclude the question numbers.: Question 1: What is the screen size and only provide the whole number value rounded up and nothing else? Question 2: Is this TV an OLED panel (Can only answer 'OLED' or 'LCD (LED)'). Question 3: What is the native resolution of this TV (Can only answer 7680x4320, 3840x2160, 1920x1080, 1366x768 and if not found leave blank ). Question 4: What is the TV weight with the stand (Just the number in pounds or if not found leave it blank). Question 5: What is the TV width with the stand (Just the decimal number in inches or if not found leave it blank). Question 6: What is the TV height with the stand (Just the decimal number in inches or if not found leave it blank). Question 7: What is the TV depth with the stand (Just the decimal number in inches or if not found leave it blank). Question 8: What is the width without the stand (Just the decimal number in inches or if not found leave it blank). Question 9: What is the TV height without the stand and if there is multiple positions listed please answer with the shorter measurement (Just the decimal number in inches or if not found leave it blank). Question 10: What is the depth without the stand (Just the decimal number in inches or if not found leave it blank). Question 11: Does this TV support ATSC 3 or Nextgen TV (Answer Yes or No if not found). Question 12: Does this TV support the Variable Refresh Rate feature also known as VRR (Only answer 'Yes' or 'No' if not found). Question 13: Does this TV have any form of the VRR feature FreeSync (Can only answer FreeSync, FreeSync Premium, FreeSync Premium Pro, or None if not found ). Question 14: Does this TV have any form of the VRR feature G-Sync (Can only answer G-Sync Compatible, G-Sync, G-Sync Ultimate, or None if not found). Question 15: What is the Highest Wi-fi standard this TV supports (Can only answer: '802.11n/WiFi 4','802.11ac/WiFi 5', '802.11ax/WiFi 6', '802.11ax/WiFi 6E', and 'NS' if you cannot find a wi-fi standard in the data provided). Question 16: Does this TV have an 'Auto Low Latency Mode' also known as 'ALLM' feature (Can only answer 'Yes' or 'No')."
            }
        ]
        )
#   print(completion.choices[0].message.content)
  pedigree_specs_arr = completion.choices[0].message.content.split(",")
  final_pedigree_specs_arr = []
  for i in pedigree_specs_arr:
        if i[0] == " ":
            final_pedigree_specs_arr.append(i[1:])
        else:
            final_pedigree_specs_arr.append(i)
  insertMultiple(final_pedigree_specs_arr, 1, " ", 2)
  insertMultiple(final_pedigree_specs_arr, 4, " ", 2)
  final_pedigree_specs_arr.insert(len(final_pedigree_specs_arr), final_url)
  insertMultiple(final_pedigree_specs_arr, 19, " ", 11)
  insertMultiple(final_pedigree_specs_arr, 31, " ", 5)
  final_pedigree_specs = "\t".join(final_pedigree_specs_arr)
  pyperclip.copy(f"{final_pedigree_specs}")
  print(final_pedigree_specs)
  driver.quit()
  print("Specs were copied please paste the results into the tv workbook")
  time.sleep(5)

main()