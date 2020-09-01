import requests
import json
from urllib import request #urllib 不用到headers易被網頁擋住

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
url = 'https://www.dcard.tw/service/api/v2/forums/game/posts?limit=30&before=233743555' #只給id 233743555之前的文章
# method = get ,不用 post 帶form data
res=requests.get(url,headers=headers)

# print(res.text)
json_data=json.loads(res.text)

# for k in json_data[0]: # 用迴圈印出字典所有 key
#     print(k)
# get title "id":233743547,"title":"遊戲vs女友誰獲勝？","excerpt":"相信各位弟兄朋友們，都曾因為遊戲和女友吵架的經驗，如果沒有就是沒交過女朋友，沒關係，哥會等你，有遇過那種拔插頭 斷網路 關螢幕的，我就是沒遇過影片這種的rrrrr，（覺得羨慕），這樣也忍得下去，算你厲","anonymousSchool":false,"anonymousDepartment":true...
for t in json_data:
    title_name = t['title']
    print(title_name) # 取 key 為 title 的值 t['title']
    article_url = 'https://www.dcard.tw/f/game/p/' + str(t['id'])
    print(article_url)
# get images url in list
    image_url_list = [img['url'] for img in t['mediaMeta']]

# download img
    for image_url in image_url_list:
        # request.urlretrieve(image_url, './dcardimg/' + image_url.split('/')[-1]) urllib被擋
        res_img = requests.get(image_url,headers=headers)
        img_content = res_img.content
        with open('./dcardimg/' + image_url.split('/')[-1], 'wb') as f: # wb 像二進制文字檔寫入
            f.write(img_content)