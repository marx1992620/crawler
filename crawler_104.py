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

config = {}
df = ""
url_Queue = Queue()
pages_Queue = Queue()
headers_Queue = Queue()
times_Queue = Queue()


def setting():
    global df,config
    if not os.path.exists('./output'):
        os.mkdir('./output')

    # 讀取104_config
    if not os.path.exists(r'./104_config.json'):
        return
    try:
        with open(r'./104_config.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
        print("------------------config------------------")
        print(config)
    except Exception as e:
        print(f"read config occurs exception as: {str(e)}")

    config["max_rows"] = int(config["max_pages"]) * 60
    for tt in range(int(config["max_rows"])):
        times_Queue.put(tt) # 建立編號Queue

    for key in config["job_skills"]:
        if key not in config["synonym_dic"]:
            config["synonym_dic"][key]=[key.lower()]
    for skill_column in config["synonym_dic"]:
        if skill_column not in config["job_skills"]:
            config["job_skills"].append(skill_column)

    df = pd.DataFrame(columns=['company', 'job_name', 'job_content', 'job_exp', 'job_require', 'job_welfare',
                            'job_contact', 'URL'] + config["job_skills"])

def crawl_url():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    keyword = config["job_keyword"] # 搜尋相關職缺

    for n in range(1, int(config["max_pages"])): # 設定爬頁數
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
    job_skills = [i['description'] for i in json_data['data']['condition']['specialty']]

    # 搜索所需技能
    c = [0 for _ in range(len(config["job_skills"]))]
    # times為配對技能要求次數
    for job_skill in job_skills:
        times = 0
        for b in config["synonym_dic"].values(): # 從同義字字典匹配技能項
            if job_skill.lower() in b:
                c[times] = 1
            times += 1
    print(company,job_name)

    tt = times_Queue.get() # 從times Queue獲取編號 依序新增row資料
    df.loc[tt] = [company, job_name, job_content, job_exp, job_require, job_welfare, job_contact, url] + c
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
    setting()
    print("start crawling url")
    crawl_url()
    print("start crawling content")
    crawl_thread()
    tEnd = time.time() # 結束時間
    print('Cost %d seconds' % (tEnd - tStart)) # 完成花費時間
