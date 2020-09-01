import requests
from bs4 import BeautifulSoup
import os
if not os.path.exists('./pttgossip'):
    os.mkdir('./pttgossip') # 建資料夾

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
url = 'https://www.ptt.cc/bbs/Gossiping/index.html'
ss = requests.session() # 取得COOKIE再接著訪問頁面同樣有效
ss.cookies['over18'] = '1' # 取得COOKIE

page = 8 # 爬取頁數
for i in range(0,page):
    res = ss.get(url, headers=headers)  # 訪問頁面
    soup = BeautifulSoup(res.text, 'html.parser')  # 轉可讀的html
    title_html_list = soup.select('div.title')  # 取得所有TITLE

    try:

        for each_article in title_html_list:

            title=each_article.text # 取得TITLE
            print(title)
            html = "https://www.ptt.cc" + each_article.a['href'] # 取得網址
            # print(html)

            # print(html) # 開頭標籤a可用.a 內容須用XX=YY 或["XX"]索引
            res_article= ss.get(html,headers=headers)
            soup_article= BeautifulSoup(res_article.text,'html.parser')
            content_list= soup_article.select('div#main-content')
            content= content_list[0].text.split('--')[0]
            # print(content)

            push_up = 0
            push_down = 0
            score = push_up - push_down
            author = ''
            title = ''
            datetime = ''
            try:

                push_info_list = soup_article.select('div[class="push"] span')
                # push_info_list2 = soup_article.select('div[class="push"]')
                # print(push_info_list)
                # print(push_info_list2) # 沒有span tag結果list就會是文字沒有","分隔

                for info in push_info_list:
                    if info.text == "推 " :
                        push_up += 1
                    elif info.text == "噓 ":
                        push_down += 1
                    # print(info.text)
                article_info_list = soup_article.select('div[class="article-metaline"] span')
                article_info = article_info_list
                # print(article_info)
                author = article_info_list[1].text
                title = article_info_list[3].text
                datetime = article_info_list[5].text
                url = 'https://www.ptt.cc' + soup.select('div[class="btn-group btn-group-paging"] a')[1]['href']  # 網頁連結

                content += "\n---split---\n"
                content += f'推: {push_up}\n'
                content += f'噓: {push_down}\n'
                content += f'分數: {score}\n'
                content += f'{article_info_list[0].text} : {author}\n'
                content += f'{article_info_list[2].text} : {title}\n'
                content += f'{article_info_list[4].text} : {datetime}\n'
                content += f'網頁連結: {url}\n'

                title_2=title.replace("/", '').replace("?","").replace(":","").replace("!","") # 非法字元(\\/:*?"<>|\r\n)造成寫入標題出錯
                try:
                    with open( fr'./pttgossip/{title_2}', 'a', encoding='utf-8') as f:
                        f.write(content)
                except OSError as o:
                    print('==========')
                    print(o.args)
                    print('==========')

            except AttributeError as e:
                print('==========')
                print()
                print(e.args)
                print('==========')

    except TypeError as t:
        print('==========')
        print(t.args)
        print('==========')
    url = 'https://www.ptt.cc' + soup.select('div[class="btn-group btn-group-paging"] a')[1]['href'] # 網頁連結


