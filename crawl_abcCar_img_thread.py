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
from queue import Queue
import threading

q = Queue()
def crawl_img(url):
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = selenium.webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')

    try:
        driver.get(url)
        time.sleep(6)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        id = url[30:37]
        article = soup.select('section[class="abc-container"]')[3].select('div[class="col col-auto"]')
        brand = soup.select('span[itemprop="name"]')[2].text
        model = soup.select('span[itemprop="name"]')[3].text
        year = article[0].text.replace("\n", "")[4:8]
        if not os.path.exists(f'./group_work/filter_all'):
            os.makedirs(f'./group_work/filter_all') # 如果該資料夾不存在則新增
        img_list = [i['src'] for i in soup.select('div[class="slick-track"]')[0].select('img[class="img-responsive"]')]
        print(brand,model,year)
        k = 0
        for i in img_list:
            k += 1 # 給圖片編號
            res_img = requests.get(url=i)
            img_content = res_img.content
            with open(f'./group_work/filter_all/' + f'{brand}_{model}_{year}_{k}_{id}_m.jpg',
                      'wb') as f:  # 依廠牌 車型 年分存入，wb二進制文字檔寫入圖片
                f.write(img_content)

    except ConnectionResetError as c:
        print(c)
        options = selenium.webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = selenium.webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
    except Exception as e:
        print(e, url)
        with open(r'./abcCar_img_error.txt', 'a', encoding='utf-8') as f:
            f.write(f'{url}\n')

def crawl_img_thread():
    with open(r'./abcCar_url.txt', "r", encoding='utf-8')as file:
        js = file.read()
    url_dict = json.loads(js)
    list = [i[0] for i in url_dict.values()]
    for j in range(len(list)):
        current_url = list[j]
        q.put(current_url) # 將網址放在Queue
    threads = []
    for t in range(3): # 建3個執行緒
        t = Parser("t"+str(t))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join() # 主線程必須等到所有threads執行完畢才繼續執行

class Parser(threading.Thread): # 此為python繼承語法

    def __init__(self, name): # 接受 name 參數
        threading.Thread.__init__(self) # initialize class
        self.name = name # 每條Parser的名子

    def run(self): # thread啟動後執行函數
        while q.empty() is False:  #檢查titles queue不為空的話，獲取URL後parse
            url = q.get() # 從Queue取網址
            crawl_img(url)

crawl_img_thread()