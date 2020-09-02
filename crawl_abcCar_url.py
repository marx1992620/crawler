from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import selenium.webdriver
import time
import json
import pandas as pd

def grab_url():
    with open(r'./abcCar_url.txt', "r", encoding='utf-8')as file:
        js = file.read()
    url_dict = json.loads(js) # 讀取上次儲存的物件網址
    # url_dict = {}
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = selenium.webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
    url='https://www.abccar.com.tw/search?tab=1&SearchType=1'
    driver.get(url)

    for page in range(180):

        try:
            element = WebDriverWait(driver,5).until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/main/form/section[3]/section/div[2]/div[3]/div[3]/div[3]/button')))
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source,'html.parser')
            # 抓下該頁面所有車子物件的網址
            url_list = soup.select('div[class="row row--10 ng-scope"]')[0].select('a[itemprop="mainEntityOfPage"]')

            for i in range(len(url_list)):
                url = url_list[i]['href']
                id = url[30:37]
                if id in url_dict:
                    pass # 已有的網址pass，避免網站重複推薦車款，而抓取重複物件
                else:
                    url_dict[id]=[url] # 儲存新的網址
            # 點擊下一頁
            driver.find_element_by_xpath('/html/body/main/form/section[3]/section/div[2]/div[3]/div[3]/div[3]/button').click()
        except Exception as e:
            print(e,page)
        except :
            print("系統error",page)
        print(f"第{page}頁")

    print(len(url_dict))
    js = json.dumps(url_dict)
    with open(r'./abcCar_url.txt', 'w', encoding='utf-8') as f:
        f.write(js) # 儲存所有車物件網址

grab_url()

