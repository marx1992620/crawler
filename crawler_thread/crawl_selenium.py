from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium import webdriver
from queue import Queue
from datetime import datetime
import time
import requests
import os
import json
import re
import pandas as pd
import traceback
import threading


work_Queue = Queue()
res = [["原始資料順序","國内/國外","交通方式","搭乘起點","搭乘終點","運輸距離(mi)","運輸公里數(km)"]] # 爬蟲後輸出的表格欄位名稱


def set_work(): # 建立要被爬蟲的項目queue

    df = pd.read_excel("raw.xlsx") # 如待爬蟲的工作項目的excel
    for index,row in df.iterrows():
        print(index,row[2],row[3])
        lis = [index] + [row[0]] + [row[1]] + [row[2]] + [row[3]]
        work_Queue.put(lis)
    print("len:",work_Queue.qsize())


def set_driver(chrome_driver_path='chromedriver.exe',headless=True): # 爬蟲chrome設定 基本上不用改動
    chrome_options = webdriver.ChromeOptions()
    prefs = {"": ""}
    prefs["credentials_enable_service"] = False
    prefs["profile.password_manager_enabled"] = False
    if headless==True:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_experimental_option("prefs", prefs)  # 關掉密碼彈窗
    chrome_options.add_argument('--disable-gpu')  # 谷歌文檔提到需要加上這個屬性來規避bug
    chrome_options.add_argument('lang=zh_CN.UTF-8')  # 設置默認編碼爲utf-8
    chrome_options.add_experimental_option('useAutomationExtension', False)  # 取消chrome受自動控制提示
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])  # 取消chrome受自動控制提示
    driver = webdriver.Chrome(options=chrome_options,executable_path=chrome_driver_path)
    driver.implicitly_wait(20) # 隱式 等待20秒
    return driver


def crawl_worker(driver,row): # 這裡定義每個thread的爬蟲工作

    try: # 爬蟲內容
        mile = ""
        kmm = ""
        key = row[3] + "-" + row[4]
        url=f'http://www.gcmap.com/dist?P={key}&DU=mi&DM=&SG=&SU=mph'
        driver.get(url)
        time.sleep(0.01)
        mi = driver.find_element(By.XPATH,'//*[@id="mdist"]/tbody/tr/td[7]')
        mile = mi.text.replace(" mi","").replace(",","")

        url2 = url.replace("&DU=mi","&DU=km")
        driver.get(url2)
        time.sleep(0.01)
        km = driver.find_element(By.XPATH,'//*[@id="mdist"]/tbody/tr/td[7]')
        kmm = km.text.replace(" km","").replace(",","")

        print(row,mile,kmm)
        res.append([row[0]] + [row[1]] + [row[2]] + [row[3]] + [row[4]] + [mile] + [kmm]) #將爬蟲的內容用 按照欄位順序放入res的list 如: [data1]+[data2]...

    except: # 出錯時的報錯內容
        print("-"*30)
        traceback.print_exc()
        print(row[0],row[3],row[4])
        print("-"*30)



def set_thread(): # 設定thread 基本不用更動

    threads = []
    for t in range(8): # 建8個thread
        t = thread_class("t"+str(t))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join() # 主線程必須等到所有threads執行完畢才繼續執行

class thread_class(threading.Thread): # 讓每個thread繼承名稱
    def __init__(self, name): # 接受name參數
        threading.Thread.__init__(self) # initialize class
        self.name = name # 每條thread的名子

    def run(self): # thread啟動後執行函數
        driver=set_driver(headless=True) # 設定False會看到網頁被打開 不想看到就設True
        
        while work_Queue.empty() is False:  # 給每個thread的工作項目或url
            row = work_Queue.get() # 從Queue依序取出項目
            crawl_worker(driver,row) # 看要將什麼參數丟給爬蟲thread執行

if __name__ == '__main__':
    tStart = time.time() # 起始時間
    set_work() # 建立所有帶爬蟲的工作項目 放入queue
    set_thread() # 建立thread
    new_df = pd.DataFrame(res) # 將res list 轉為dataframe 並輸出excel
    output_filname = "NEW_output" + "_"+str(datetime.now()).replace(" ","_").replace(":","")[5:17] +".xlsx"
    new_df.to_excel(output_filname,header=False,index=False)
    tEnd = time.time() # 結束時間
    print('Cost %d seconds' % (tEnd - tStart)) # 完成花費時間
    print("Processes all done.")
    

