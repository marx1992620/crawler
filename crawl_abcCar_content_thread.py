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
import threading
from queue import Queue
import random

times = Queue() # 用Queue讓執行緒依序取物件進行任務
titles = Queue()
df = pd.DataFrame(columns=['link','id','brand','type','seller','price','year','miles','locate','cc','sys',
                               'power','color','gas','people','window','hid','led','l_chair','auto_chair',
                               'keyless','media','air_con','gps','multi_wheel','epb','slide_door',
                               'light','abs','safe_bag','trc','tpms','back_screen','ss','blind_spot','ldws','acc',
                                'cd','back_radar','alu','tcs','aeb','hud','auto_windows','auto_side','alert','es',
                                'isofix','auto_park','silde_door','female_used','turbo','warranty','fog_lights',
                                'electric_tailgate','whole_window','lcd','shift_paddles'])
# 抓所有車網址
def grab_url():
    # 讓driver等頁面內容5秒，超過5秒則跳過
    # element = WebDriverWait(driver,5).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,'abc-container')))
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = selenium.webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
    url='https://www.abccar.com.tw/search?tab=1&SearchType=1'
    driver.get(url)
    url_dict = {}

    for page in range(1,10):
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
# 由已抓下的車網址，抓車物件內容
def crawl_content(url,n):
    options = selenium.webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = selenium.webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')

    try:
        driver.get(url)
        time.sleep(random.randint(3,10))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        article = soup.select('section[class="abc-container"]')[3].select('div[class="col col-auto"]')
        id = url[30:37]
        brand = soup.select('span[itemprop="name"]')[2].text
        model = soup.select('span[itemprop="name"]')[3].text
        price = soup.select('div[class="col col-auto abc-theme__info"]')[0].select('span[class="abc-article__price__num"]')[
            0].text.strip().replace("萬","")
        try: # 抓車商資料
            str = soup.select('a[class="store_name"]')[0].text
            pos = str.find("車") + 1
            if pos > 3:
                seller = str[0:pos].replace("【", "")
            elif len(str) > 6:
                seller = str.replace("【", "").replace("】","")
            else :
                seller = soup.select('span[class="abc-article__dealer__member__text"]')[0].text[4:]
        except Exception as e:
            seller = soup.select('span[class="abc-article__dealer__member__text"]')[0].text[4:]
            print(e,seller)
        year = article[0].text.replace("\n", "")[4:8]
        km = article[1].text.replace("\n", "")[3:].replace(",","").replace("公里","")
        location = article[2].text.replace("\n", "")[5:]
        if len(location)<1:
            location = None
        discharge = int(eval(article[3].text.replace("\n", "")[3:].replace("L",""))*1000)
        sys = article[4].text.replace("\n", "")[4:]
        if "四" in article[5].text.replace("\n", ""):
            power = 4
        else:
            power = 2
        color = article[6].text.replace("\n", "")[4:]
        if len(color)<1:
            color = None
        fue = article[7].text.replace("\n", "")[2:]
        people = article[8].text.replace("\n", "")[4:5]

        c = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        t = 0
        for k in range(9, 31):
            if len(article[k].i['class'][0]) == 28:
                c[t] = 1 # 有配備為1 沒此配備為0
            else:
                c[t] = 0
            t += 1
        print(price, brand, model, year, seller)
        # 從times Queue取序號，依序新增row資料
        df.loc[n] = [url, id, brand, model, seller, price, year, km, location, discharge, sys,
                     power, color, fue, people, c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9],
                     c[10], c[11], c[12], c[13], c[14], c[15], c[16], c[17], c[18], c[19], c[20], c[21],c[22],
                     c[23],c[24],c[25],c[26],c[27],c[28],c[29],c[30],c[31],c[32],c[33],c[34],c[35],c[36],c[37],
                     c[38],c[39],c[40],c[41],c[42]]

        df.to_csv(r'./test.csv', index=0, encoding='utf-8-sig')
    except Exception as e:
        print("已下架", e, url) # 物件下架便抓不到資料
        with open(r'./abcCar_url_error.txt', 'a', encoding='utf-8') as f:
            f.write(f'{url}\n') # 存下網址供檢查
    except:
        print("系統error", url)
        with open(r'./abcCar_url_error.txt', 'a', encoding='utf-8') as f:
            f.write(f'{url}\n') # 存下網址供檢查
# 建執行緒
def crawl_content_thread():
    with open(r'./abcCar_url.txt', "r", encoding='utf-8')as file: # 讀取已抓下的車網址
        js = file.read()
    url_dict = json.loads(js)
    list = [i[0] for i in url_dict.values()]
    for j in range(len(list)):
        current_url = list[j]
        titles.put(current_url)
        times.put(j) # 依順序times Queue放入編號
    threads = []
    for t in range(5): # 建5個執行緒
        t = thread_class("t"+str(t))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join() # 主線程必須等到所有threads執行完畢才繼續執行

class thread_class(threading.Thread): # 此為python繼承語法
    def __init__(self, name): # 接受 name 參數
        threading.Thread.__init__(self) # initialize class
        self.name = name # 每條thread的名子
    def run(self): # thread啟動後執行函數
        while titles.empty() is False:  #檢查titles queue不為空的話，獲取URL後parse
            url = titles.get() # 從Queue中取url給每條thread
            n = times.get() # 從Queue中取編號給給每條thread
            crawl_content(url,n)

if __name__ == '__main__':
    tStart = time.time() # 起始時間
    print("start crawling url and content")
    # grab_url()
    crawl_content_thread()
    tEnd = time.time() # 結束時間
    print('Cost %d seconds' % (tEnd - tStart)) # 完成花費時間







