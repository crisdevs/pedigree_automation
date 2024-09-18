import requests, bs4, pyperclip, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from openai import OpenAI
from selenium.common.exceptions import NoSuchElementException

API_KEY = open("API_KEY.txt", "r").read()
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

def generate_url(brand, model):
    final_URL = None
    #URL has model as uppercases and includes dashes
    if brand == "vizio" or brand == "tcl":
            model = model.upper()
    else:
            #Make model number all lower case
            model = model.lower()
            #Remove dashes in model number
            model = model.replace("-","")

    tvs = {
        'lg': {
            'uhd':f'https://www.lg.com/us/tvs/lg-{model}-4k-uhd-tv#pdp_specs',
            'oled':f'https://www.lg.com/us/tvs/lg-{model}-oled-4k-tv#pdp_specs',
            'qned': f'https://www.lg.com/us/tvs/lg-{model}-qned-4k-tv#pdp_specs'
            },
        'samsung': f'https://www.samsung.com/us/search/searchMain/?search={model}#',
        'sony': f'https://electronics.sony.com/tv-video/televisions/all-tvs/p/{model}',
        'vizio': f'https://www.vizio.com/en/tv/4k/{model}',
        'hisense': f'https://www.hisense-usa.com/televisions',
        'roku': 'https://www.roku.com/products/roku-tv/roku-made-tvs',
        'tcl': f'https://www.tcl.com/us/en/search?search={model}#cmp-tabs'
        }
    #If tv brand is not found in current dictionary
    # if tvs.get(brand) == None :
    #     finalURL = input('URL not found please enter URL for TV under test\n')
    #     return finalURL
    finalURL = tvs[brand]
    if brand == 'lg':
        series = None
        #Checks in model name what kind of tv
        if model[:4] == "oled":
            series = 'oled'
        elif model[2:6] == 'qned':
            series = 'qned'
        else:
            series = 'uhd'
        #For LG only
        return finalURL[series]

    #For every other brand
    return finalURL

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
    driver.find_element(By.XPATH, '//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[3]/button').click()
    return '/html/body/app-root/ngb-modal-window/div/div/div'

def samsung(driver):
    navigate_to_url(['//*[@id="pf-page"]/div[1]/div/div/div/section/div[9]/div[3]/div[2]/ul/li/div/div[2]/h3/a'], driver)
    time.sleep(5)
    return '//*[@id="#specDetails"]/div/ul'

def vizio(driver = None):
    return '//*[@id="main-content"]/div/div/div/div/div[3]/tech-specs-element/div/div[2]' 

def tcl(driver):
    if check_exists_by_xpath('//*[@id="search-results"]/div/h4/a', driver) == False:
            return    
    driver.find_element(By.XPATH, '//*[@id="search-results"]/div/h4/a').click()
    # if check_exists_by_xpath('//*[@id="cmp-tabs"]/div[1]/div/ol/li[2]', driver) == False :
    #     return
    # driver.find_element(By.XPATH, '//*[@id="cmp-tabs"]/div[1]/div/ol/li[2]').click()
    return '//*[@id="cmp-tabs"]/div[3]/div/div/div'

def main():
  tv = input("Please enter brand and model\n")
  brand = tv.split()[0].lower()
  model = tv.split()[1]
  print(f'This is the brand: {brand} and the model is {model}')
  tv_link = generate_url(brand, model)
  tv_dict = {
    'lg':lg,
    'sony':sony,
    'samsung': samsung,
    'vizio': vizio,
    'tcl': tcl
}
  # Open chrome window
  is_url_valid = url_check(tv_link)
  url_checked = tv_link
  if not is_url_valid:
      url_checked = input('Website stored came back with a 404 please enter valid website\n')
  driver = webdriver.Chrome(service=service, options=options)
  driver.get(url_checked)
  time.sleep(5)
  tv_func = tv_dict[brand]
  spec_xpath = tv_func(driver)
  tv_specs = driver.find_element(By.XPATH, spec_xpath).get_attribute('textContent')
  final_url = driver.current_url
  print(f'This is the tv specs {tv_specs}')
  completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Here is some unfiltered data here:{tv_specs} for the {brand} {model} TV. Based off of this data can you answer the following questions and please only provide the answers seperated by commas and exclude the question numbers.: Question 1: What is the screen size and only provide the whole number value nothing else? Question 2: Is this an OLED panel (Can only answer 'OLED' or 'LCD (LED)' or 'NS' if you can't find it). Question 3: What is the native resolution of this TV (Can only answer 7680x4320, 3840x2160, 1920x1080, 1366x768 and if not found leave blank ). Question 4: What is the TV weight with the stand (Just the number in pounds or if not found leave it blank). Question 5: What is the TV width with the stand (Just the decimal number in inches or if not found leave it blank). Question 6: What is the TV height with the stand (Just the decimal number in inches or if not found leave it blank). Question 7: What is the TV depth with the stand (Just the decimal number in inches or if not found leave it blank). Question 8: What is the width without the stand (Just the decimal number in inches or if not found leave it blank). Question 9: What is the height without the stand (Just the decimal number in inches or if not found leave it blank). Question 10: What is the depth without the stand (Just the decimal number in inches or if not found leave it blank). Question 11: Has ATSC 3 or Nextgen TV feature (Answer Yes or No if not found). Question 12: Has Variable Refresh Rate feature (Answer Yes or No if not found). Question 13:Has any form of FreeSync (Can only answer FreeSync, FreeSync Premium, FreeSync Premium Pro, or None if not found ). Question 14: Has any form of G-Sync (Can only answer G-Sync Compatible, G-Sync, G-Sync Ultimate, or None if not found). Question 15: What is the Highest WiFi Standard (Can only answer: 802.11n/WiFi 4,802.11ac/WiFi 5, 802.11ax/WiFi 6, 802.11ax/WiFi 6E and if not found answer 'NS' for this question. Does this TV have an 'Auto Low Latency Mode' also known as 'ALLM' feature (Can only answer 'Yes' or 'No'))."
            }
        ]
        )
  print(completion.choices[0].message.content)
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
  #   print(pedigree_specs)
  pyperclip.copy(f"{final_pedigree_specs}")
  print("Specs were copied please paste the results into the tv workbook")
  print(f'This is the url used\n{final_url}')
  driver.quit()
main()