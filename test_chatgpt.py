import requests, bs4, pyperclip, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from openai import OpenAI
from selenium.common.exceptions import NoSuchElementException

API_KEY = open("API_KEY", "r").read()
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
        return False
    return True

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
    if tvs.get(brand) == None :
        return None

    if brand == 'lg':
        series = None
        #Checks in model name what kind of tv
        if model[:4] == "oled":
            series = 'oled'
        elif model[2:6] == 'qned':
            series = 'qned'
        else:
            series = 'uhd'
        #Assigns this variable to the nested dictionary
        finalURL = tvs[brand]
        #For LG only
        return {
            'google': f'https://www.google.com/search?q={brand}+{model}',
            'website': finalURL[series]
        }

    #For every other brand
    return {
        'google': f'https://www.google.com/search?q={brand}+{model}',
        'website': tvs[brand]
        }
    


def main():
  # Prompt for the link
  tv = input("Please enter brand and model\n")
  brand = tv.split()[0].lower()
  model = tv.split()[1]
  print(f'This is the brand: {brand} and the model is {model}')
  tv_link = generate_url(brand, model)
  # Open chrome window
  driver = webdriver.Chrome(service=service, options=options)
  # # Navigate to the link that was entered by the user
  driver.get(tv_link['website'])
  time.sleep(5)
  element_xpath = None
  
  if brand == 'lg':
    element_xpath = '//*[@id="simple-tabpanel-3"]'
  elif brand == 'samsung':
      driver.find_element(By.XPATH, '//*[@id="pf-page"]/div[1]/div/div/div/section/div[7]/div[3]/div[1]/ul/li/div/div[2]/h3/a').click()
      time.sleep(5)
      element_xpath = '//*[@id="#specDetails"]/div/ul'
  elif brand == 'sony':
      driver.find_element(By.XPATH, '//*[@id="cx-main"]/app-product-details-page/div/app-pdptab-nav/div/div/div/ul/li[3]/a').click()
      time.sleep(5)
      if check_exists_by_xpath('//*[@id="contentfulModalClose"]', driver):
          driver.find_element(By.XPATH, '//*[@id="contentfulModalClose"]').click()
      driver.find_element(By.XPATH, '//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[3]/button').click()
      element_xpath = '/html/body/app-root/ngb-modal-window/div/div/div'
  elif brand == 'vizio':
    element_xpath = '//*[@id="main-content"]/div/div/div/div/div[3]/tech-specs-element/div/div[2]'
  elif brand == 'tcl':
      driver.find_element(By.XPATH, '//*[@id="search-results"]/div/h4/a').click()
      driver.find_element(By.XPATH, '//*[@id="cmp-tabs"]/div[1]/div/ol/li[2]').click()
      element_xpath = '//*[@id="cmp-tabs"]/div[3]/div/div/div'


  tv_specs = driver.find_element(By.XPATH, element_xpath).get_attribute('textContent')
  
  print(f'This is the tv specs {tv_specs}')
  completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {
              "role": "user",
              "content": f"Here is some unfiltered data here:{tv_specs}. Based off of this data can you answer the following questions and please only provide the answers seperated by commas and exclude the question numbers.: Question 1: What is the screen size and only provide the whole number value nothing else? Question 2: Is this an OLED panel (Can only answer 'OLED' or 'LCD (LED)' or 'NS' if you can't find it). Question 3: What is the native resolution of this TV (Can only answer 7680x4320, 3840x2160, 1920x1080, 1366x768 and if not found leave blank ). Question 4: What is the TV weight with the stand (Just the number in pounds or if not found leave it blank). Question 5: What is the TV width with the stand (Just the decimal number in inches or if not found leave it blank). Question 6: What is the TV height with the stand (Just the decimal number in inches or if not found leave it blank). Question 7: What is the TV depth with the stand (Just the decimal number in inches or if not found leave it blank). Question 8: What is the width without the stand (Just the decimal number in inches or if not found leave it blank). Question 9: What is the height without the stand (Just the decimal number in inches or if not found leave it blank). Question 10: What is the depth without the stand (Just the decimal number in inches or if not found leave it blank). Question 11: Has ATSC 3 or Nextgen TV feature (Answer Yes or No if not found). Question 12: Has Variable Refresh Rate feature (Answer Yes or No if not found). Question 13:Has any form of FreeSync (Can only answer FreeSync, FreeSync Premium, FreeSync Premium Pro, or None if not found ). Question 14: Has any form of G-Sync (Can only answer G-Sync Compatible, G-Sync, G-Sync Ultimate, or None if not found). Question 15: What is the Highest WiFi Standard (Can only answer: 802.11n/WiFi 4,802.11ac/WiFi 5, 802.11ax/WiFi 6, 802.11ax/WiFi 6E and if not found answer 'NS' for this question)."
          }
      ]
    )
  
  print(completion.choices[0].message.content)
  pedigree_specs = completion.choices[0].message.content
  pedigree_specs = pedigree_specs.split(",")
  insertMultiple(pedigree_specs, 1, " ", 2)
  insertMultiple(pedigree_specs, 4, " ", 2)
  pedigree_specs = "\t".join(pedigree_specs)
  print(pedigree_specs)
  pyperclip.copy(f"{pedigree_specs}")
  print("Specs were copied please paste the results into the tv workbook")

  driver.quit()
main()