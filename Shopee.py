import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *
import pandas as pd
import time

# scroll time
scroll_pause_time = 1

# search until page
PAGE_SEARCH = 4

# list of data
title_list = []
price_list = []
sold_list = []

#launch url
url = "https://shopee.co.th/%E0%B8%AA%E0%B8%B1%E0%B8%95%E0%B8%A7%E0%B9%8C%E0%B9%80%E0%B8%A5%E0%B8%B5%E0%B9%89%E0%B8%A2%E0%B8%87-cat.2083"

# create a new chrome session
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)

# choose language English
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.XPATH, "//div[@class='language-selection__list-item']/button[text()='English']"))).click()

while True:

    # automatic scroll page to bottom-down
    ct_page = 8

    for _ in range(ct_page):
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, window.scrollY + 500);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            driver.execute_script("window.scrollTo(0, window.scrollY + 500);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")

    # convert collected html to BS.
    full_html = BeautifulSoup(driver.page_source, 'html.parser')

    # get current and last page
    current_page = full_html.find('span', class_='shopee-mini-page-controller__current').text
    last_page = full_html.find('span', class_='shopee-mini-page-controller__total').text

    # finding all element on each category
    get_titles = full_html.find_all('div', class_='O6wiAW')
    get_prices = full_html.find_all('div', class_='_1w9jLI _37ge-4 _2ZYSiu')
    get_sold = full_html.find_all('div', class_='_18SLBt')

    # extract data in each category
    # get text title
    for _ in get_titles:
        list_title = _.find('div')
        title_list.append(list_title.text)

    # get text price
    for _ in get_prices:
        new_string = ''
        list_price = _.find_all('span', class_='_341bF0')
        temp = []
        for __ in list_price:
            temp.append(__.text)
        new_string = temp[0]+'-'+temp[1] if len(temp) == 2 else temp[0]
        price_list.append(new_string)

    # get text sold
    for _ in get_sold:
        new_string = _.text
        index = new_string.find('k')
        # fix of unknown sold
        new_string = 0 if index == -1 else (float(new_string[:index]) * 1000)
        sold_list.append(new_string)

    # automatic next page
    if int(current_page) == PAGE_SEARCH or int(current_page) == last_page:
        break
    elif int(current_page) != last_page:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[4]/div[2]/div/div[1]/div[2]/button[2]'))).click()


# show collected data.
for _ in range(len(title_list)):
    print(title_list[_])
    print(price_list[_])
    print(sold_list[_])

DF = pd.DataFrame({'สินค้า': title_list, 'ราคาสินค้า(บาท)': price_list, 'ยอดการขาย(ชิ้น)': sold_list})
DF.to_excel('Ploy.xlsx', encoding="utf-8-sig", header=True)

driver.implicitly_wait(5)
driver.quit()
