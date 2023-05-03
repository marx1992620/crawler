import requests
import json
import os
import time
import pandas as pd
import random
import threading
from bs4 import BeautifulSoup
from queue import Queue
# from multiprocessing.dummy import Pool
# import numpy as np
# import xlsxwriter
# import re

if not os.path.exists('./work'):
    os.mkdir('./work')

url_Queue = Queue()
pages_Queue = Queue()
headers_Queue = Queue()
times_Queue = Queue()

for tt in range(1000):
    times_Queue.put(tt) # 建立編號Queue
df = pd.DataFrame(columns=['company', 'job_name', 'job_content', 'job_exp', 'job_require', 'job_welfare',
                           'job_contact', 'URL', 'Linux', 'Python', 'Hadoop', 'Mysql',
                           'MongoDB', 'Kafka', 'R', 'ETL', 'Docker', 'Tableau', 'PowerBI', 'Spark',
                           'Machine Learning', 'AI', 'cloud'])
def crawl_url():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    # print("請輸入關鍵字: ")
    # keyword = input() # 輸入技能搜尋相關職缺
    keyword = 'python'
    for n in range(1, 10): # 設定爬頁數
        url = f'https://www.104.com.tw/jobs/search/?ro=0&keyword={keyword}&order=1&asc=0&page={n}&mode=s&jobsource=2018indexpoc'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        page = soup.select('div[id="js-job-content"]')[0].select('h2[class="b-tit"] a')
        pages_Queue.put(page)

def crawl_content(url,headers):
    res = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(res.text,'html.parser')
    json_data = json.loads(soup.text) # 資料轉dict格式
    job_name = json_data['data']['header']['jobName']
    company = json_data['data']['header']['custName']
    job_contact = '聯絡人:' + json_data['data']['contact']['hrName'] + 'email:' + json_data['data']['contact']['email']
    job_require = "接受身分:" + "、".join([i['description'] for i in json_data['data']['condition']['acceptRole']['role']])
    job_welfare = json_data['data']['welfare']['welfare']
    job_content = json_data['data']['jobDetail']['jobDescription']
    job_exp = "工作經驗:" + json_data['data']['condition']['workExp']
    tech = [i['description'] for i in json_data['data']['condition']['specialty']]
    # 讀取同義字檔案 並建同義字字典
    synonym_dict = {}
    with open(r'./mydict.txt', 'r', encoding='utf-8') as syn:
        syn_str = syn.read().split("\n")
    for each_row in syn_str:
        synonym_dict[each_row.split(',')[0]] = [item for item in each_row.split(',')]
    # 搜索所需15個技能
    c = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # 配對技能要求: 0為沒有該要求 1為有要求
    for a in tech:
        t = 0
        for b in synonym_dict.values(): # 從同義字字典匹配技能項
            if a.lower() in b:
                c[t] = 1
            t += 1
    print(company,job_name)

    tt = times_Queue.get() # 從times Queue獲取編號 依序新增row資料
    df.loc[tt] = [company, job_name, job_content, job_exp, job_require, job_welfare, job_contact, url, c[0],
                     c[1], c[2], c[3],c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13], c[14]]
    time.sleep(random.randint(3,5)) # 每爬完一頁休息3~5秒
    df.to_csv(r'./work/craw_104.csv', index=0,encoding='utf-8-sig') # 轉成CSV檔
    df.to_excel(r'./work/craw_104.xlsx', engine='xlsxwriter') # 轉成xlsx檔

def crawl_thread():
    while pages_Queue.empty() is False:
        page = pages_Queue.get()
        for i in range(len(page)): # 從頁面得到每筆職缺url
            j = 'https:' + page[i]['href']
            header = {'Referer': 'https://www.104.com.tw/job/' + j[27:32]}
            headers_Queue.put(header) # 對應每個url的headers放進Queue
            url = 'https://www.104.com.tw/job/ajax/content/'+ j[27:32]
            url_Queue.put(url) # 每個職缺的url放進Queue
    threads = []
    for t in range(3): # 建3個執行緒
        t = thread_class("t"+str(t))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()# 主線程必須等到所有threads執行完畢才繼續執行

class thread_class(threading.Thread): # 此為python繼承語法
    def __init__(self, name): # 接受name參數
        threading.Thread.__init__(self) # initialize class
        self.name = name # 每條thread的名子
    def run(self): # thread啟動後執行函數
        while url_Queue.empty() is False:  # 檢查url_Queue不為空的話，獲取URL後parse
            url = url_Queue.get() # 從Queue依序取出url
            headers = headers_Queue.get() # 從Queue依序取出headers
            crawl_content(url,headers)

if __name__ == '__main__':
    tStart = time.time() # 起始時間
    print("start crawling url")
    crawl_url()
    print("start crawling content")
    crawl_thread()
    tEnd = time.time() # 結束時間
    print('Cost %d seconds' % (tEnd - tStart)) # 完成花費時間
