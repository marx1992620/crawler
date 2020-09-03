from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import selenium.webdriver
from selenium.webdriver import Chrome
import time
import requests
import os
import pandas as pd
import json

options = selenium.webdriver.ChromeOptions()
options.add_argument('--headless')
driver = selenium.webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
with open(r'./abcCar_url.txt', "r",encoding='utf-8')as file:
    js = file.read() # 讀取已爬下的車網址
url_dict = json.loads(js)
list = [i[0] for i in url_dict.values()] # 將網址放在串列
for j in range(len(list)):
    url = list[j] # 依序從各網址爬下車子內容
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    id = url[30:37]
    article = soup.select('section[class="abc-container"]')[3].select('div[class="col col-auto"]')
    brand = soup.select('span[itemprop="name"]')[2].text
    model = soup.select('span[itemprop="name"]')[3].text
    year = article[0].text.replace("\n", "")[4:8]
    print(brand,model,url)
    try:
        if not os.path.exists(f'./group_work/{brand}/{model}/{year}'):
            os.makedirs(f'./group_work/{brand}/{model}/{year}') # 如果資料夾不存在 則建新的
        img_list = [i['src'] for i in soup.select('div[class="slick-track"]')[0].select('img[class="img-responsive"]')]
        print(brand,model,year)
        k = 0
        for i in img_list:
            k += 1 # 存圖片並給編號
            res_img = requests.get(url=i)
            img_content = res_img.content

            with open(f'./group_work/{brand}/{model}/{year}/' + f'{brand}_{model}_{year}_{k}_{id}_m.jpg',
                      'wb') as f:  # 依廠牌 車型 年分存入，wb 像二進制文字檔寫入
                f.write(img_content)
    except Exception as e:
        print(e, url)
        with open(r'./abcCar_img_error.txt', 'a', encoding='utf-8') as f:
            f.write(f'{url}\n') # 出錯便將網址另存檔以供檢查


