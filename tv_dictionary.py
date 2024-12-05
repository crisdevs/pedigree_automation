import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        return False
    return True

def brand_logic(brand, driver):
    tv_dictionary = {
        'lg':[By.XPATH, '//*[@id="simple-tabpanel-3"]'],
        'vizio': [By.XPATH, '//*[@id="main-content"]/div/div/div/div/div[3]/tech-specs-element/div/div[2]'],
        'tcl': [By.TAG_NAME, 'body'],
        'hisense': [By.TAG_NAME, 'body'],
        'toshiba': [By.XPATH, '//*[@id="specifications-drawer"]/div[2]'],
        'roku': [By.XPATH, '//*[@id="main"]/main/div'],
        'panasonic': [By.XPATH, '//*[@id="rn_AnswerText"]'],
        'sharp': [By.XPATH, '//*[@id="syndi_powerpage"]/syndigo-powerpage//div/div[2]/div[5]/div/div/div[1]/div/table/tbody/tr[19]/td[1]/div/span/span/p'],
    }
    if brand in tv_dictionary:
        return tv_dictionary[brand]
    else:
        if brand == 'sony':
            #Zoom out so needed element can be in view at all times
            driver.execute_script("document.body.style.zoom='25%'")
            time.sleep(2)
            #Clicks the specs button so that it will scroll down to the specs section
            driver.find_element(By.XPATH, '//*[@id="cx-main"]/app-product-details-page/div/app-pdptab-nav/div/div/div/ul/li[3]/a').click()
            time.sleep(2)
            #Checks to see if modal showing ad pop up. If so will then close the modal
            if check_exists_by_xpath('//*[@id="contentfulModalClose"]', driver):
                driver.find_element(By.XPATH, '//*[@id="contentfulModalClose"]').click()  
            driver.find_element(By.XPATH, '//*[@id="cx-main"]/app-product-details-page/div/app-product-specification/div/div[2]/div[2]/button').click()
            return [By.XPATH, '/html/body/app-root/ngb-modal-window/div/div/div']
        elif brand == 'samsung':
            #Checks to see if element exists
            #//*[@id="#specDetails"]
            #//*[@id="pdp-page"]/div/div/div/section[8]/div[2]
            if check_exists_by_xpath('//*[@id="#specs"]', driver):
                return [By.XPATH, '//*[@id="#specs"]']
            elif check_exists_by_xpath('//*[@id="#specDetails"]', driver):
                return [By.XPATH, '//*[@id="#specDetails"]']
            return [By.XPATH, '//*[@id="pdp-page"]/div/div/div/section[7]']
            

        elif brand == 'bestbuy':
            time.sleep(2)
            #Finds and saves reference to 'show specs' button element
            spec_button = driver.find_element(By.CLASS_NAME, 'show-full-specs-btn')
            #Needed for using action methods
            actions = ActionChains(driver)
            #Scrolls to the referenced element (The button)
            actions.move_to_element(spec_button).perform()
            time.sleep(2)
            spec_button.click()
            time.sleep(2)
            return [By.XPATH, '//*[@id="pdp-drawer-overlay-backdrop"]/div/div/div[4]']