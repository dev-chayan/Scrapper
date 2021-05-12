from selenium import webdriver
# pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import sys


##### Set up



custom_options = webdriver.ChromeOptions()
#custom_options.add_argument("headless")  # screen hide

prefs = {
"translate_whitelists": {"it": "en"},
"translate": {"enabled": "true"}
}
custom_options.add_experimental_option("prefs", prefs)

# driver = webdriver.Chrome(chrome_path,options=custom_options)
driver = webdriver.Chrome("C:/Users/Chayan/.wdm/drivers/chromedriver/win32/89.0.4389.23/chromedriver.exe",
                              options=custom_options)
# driver = webdriver.Chrome(ChromeDriverManager().install())

driver.set_window_position(-3000, 0)
##### Functions

def get_url(text):
    # translate in english


    if "www" in text or "http" in text:   # that means it is a URL
        url = text
    else:                # if it a search item by name
        driver.get('https://www.tripadvisor.in/search?q={}'.format(text.replace(" ", "_")))
        driver.implicitly_wait(20)
        driver.find_element_by_xpath('//*[@class="result-title"]').click()   # get the first tab and open it another page by clicking
        time.sleep(5)
        title = driver.find_element_by_xpath('//*[@class="result-title"]').text
        if text in title.lower():
            print("hehe")
            print(driver.current_url)
            newURl = driver.window_handles[1]  # shifted to new page and closed old one
            driver.switch_to.window(newURl)    # switched all operations to new window
            url = driver.current_url
        else:
            sys.exit("Sorry! no pages are available..")
    return url


  # take time to load the url

# function to check if the button is on the page, to avoid miss-click problem
def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def get_final_dataframe(page_url,reviews_number = 20):

    print(page_url)
    driver.get(page_url)  # goto the url

    time.sleep(5)

    reviews_count = 0
    ratings = []
    reviews = []
    driver.maximize_window()  # //For maximizing window

    # put no. of pages here
    for i in range(1000000):
        if reviews_count < reviews_number:
            print(reviews_count)
        # expand comments by clicking see more or read more button
            try:
                try:
                    driver.find_element_by_xpath("//span[@class='taLnk ulBlueLinks']").click()
                except:
                    driver.find_element_by_xpath("//span[@class='_3maEfNCR']").click()
            except:
                continue

            time.sleep(5)

            #review boxes basically there are three types of boxes so we wrote all three types by if conditions
            container = driver.find_elements_by_xpath("//div[@class='review-container']")
            if len(container) == 0:
                #driver.implicitly_wait(15)
                container = driver.find_elements_by_xpath("//div[@class='_2wrUUKlw _3hFEdNs8']")
                if len(container) == 0:
                    driver.implicitly_wait(15)
                    container = driver.find_elements_by_xpath("//div[@class='Dq9MAugU T870kzTX LnVzGwUB']")


            num_page_items = len(container);
            print(num_page_items)
            # reviews_count = reviews_count + num_page_items

            print(container)
            for j in range(num_page_items):
                # to save the rating
                print(container[j].find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]"))
                string = container[j].find_element_by_xpath(
                    ".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class")
                #print(string) # string is like 'ui_bubble_rating bubble_50'
                data = string.split("_")
                # to save in a csv file readable the star and the review [Ex: 50,"I love this place"]
                ratings.append(int(data[-1])/10)
                #reviews
                try:
                    reviews.append(container[j].find_element_by_xpath(".//q[@class='IRsGHoPm']").text.replace("\n", ""))
                except:
                    reviews.append(container[j].find_element_by_xpath(".//p[@class='partial_entry']").text.replace("\n", ""))
                reviews_count += 1

            # to change the page

            if (check_exists_by_xpath('//a[@class="ui_button nav next primary "]')):
                driver.find_element_by_xpath('//a[@class="ui_button nav next primary "]').click()

            if (check_exists_by_xpath('//a[contains(@class , "nav next ui_button primary")]')):
                driver.find_element_by_xpath('//a[contains(@class , "nav next ui_button primary")]').click()

            time.sleep(5)
        else:
            break

    df = pd.DataFrame({"Ratings" : ratings , "Review" : reviews})

    return df


###### scaraing reviews
url = get_url("https://www.tripadvisor.in/Hotel_Review-g297618-d299356-Reviews-Apple_Country_Resort-Manali_Manali_Tehsil_Kullu_District_Himachal_Pradesh.html")
df_reviews = get_final_dataframe(url,reviews_number= 20)
df_reviews.to_csv("reviews_final.csv")

driver.close()