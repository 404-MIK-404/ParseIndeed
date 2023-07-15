from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup


option = webdriver.ChromeOptions()
option.add_argument(" — incognito")
option .add_argument('--no-sandbox')
option .add_argument('start-maximized')
option .add_argument('enable-automation')
option .add_argument('--disable-infobars')
option .add_argument('--disable-dev-shm-usage')
option .add_argument('--disable-browser-side-navigation')
option .add_argument("--remote-debugging-port=9222")
# options.add_argument("--headless")
option .add_argument('--disable-gpu')
option .add_argument("--log-level=3")
option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43")

browser = webdriver.Chrome(options=option)

def get_url(position, function):
    template = 'https://www.indeed.com/jobs?q={}&l={}'
    url = template.format(position, function)
    return url
url = get_url('product analyst', 'remote')
#url = 'https://github.com/TheDancerCodes'
browser.get(url)
print(browser.page_source)
# Wait 20 seconds for page to load
timeout = 50
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='avatar width-full rounded-2']")))
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

# find_elements_by_xpath returns an array of selenium objects.
#titles_element = browser.find_element("//a[@class=’text-bold’]")
# use list comprehension to get the actual repo titles and not the selenium objects.
#titles = [x.text for x in titles_element]
# print out all the titles.
#print('titles:')
#print(titles, '\n')