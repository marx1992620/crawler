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
import logging

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s : %(message)s',
    datefmt='%Y%m%dT%H%M%S',filename='mylog.txt')
logging.debug('debug')
logging.info('info')
logging.warning('warning')
logging.error('error')
logging.critical('critical')

q = Queue()

# 抓所有車網址
def crawl_page():
    # 讓driver等頁面內容5秒，超過5秒則跳過
    # element = WebDriverWait(driver,5).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,'abc-container')))
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = selenium.webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
    url='https://www.abccar.com.tw/search?tab=1&SearchType=1'
    driver.get(url)
    url_dict = {}

    for page in range(1,11): # 設定爬取10頁
        try:
            # 若網頁資料5秒後還未出現，便跳過此頁
            element = WebDriverWait(driver,5).until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/main/form/section[3]/section/div[2]/div[3]/div[3]/div[3]/button')))
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source,'html.parser')
            url_list = soup.select('div[class="row row--10 ng-scope"]')[0].select('a[itemprop="mainEntityOfPage"]')

            for i in range(len(url_list)):
                url = url_list[i]['href']
                id = url[30:37]
                if id in url_dict:
                    pass
                else:
                    url_dict[id]=[url]
            # 點擊下一頁，降低被網站重複推薦同物件
            driver.find_element_by_xpath('/html/body/main/form/section[3]/section/div[2]/div[3]/div[3]/div[3]/button').click()
        except Exception as e:
            print(e,page)
        except :
            print("系統error",page)
        print(f"第{page}頁")
    print(len(url_dict))
    js = json.dumps(url_dict)
    with open(r'./abcCar_url.txt', 'w', encoding='utf-8') as f:
        f.write(js)
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


if __name__ == '__main__':
    tStart = time.time() # 起始時間
    logging.debug('debug')
    logging.info('info')
    logging.warning('warning')
    logging.error('error')
    logging.critical('critical')
    print("start crawling url and content")
    crawl_page()
    crawl_img_thread()
    tEnd = time.time() # 結束時間
    print('Cost %d seconds' % (tEnd - tStart)) # 完成花費時間