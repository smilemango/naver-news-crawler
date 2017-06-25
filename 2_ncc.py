#news contents crawler

import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
from urllib.parse import urlparse


conn = sqlite3.connect("articles.sqlite3")

cur = conn.cursor()
cur.execute("SELECT * FROM article_title")

next = True
for row in cur:
    params_str = str(row[1]).split('?')[1].split("&")
    oid = None
    aid = None
    for var_str in params_str:
        if 'oid=' in var_str:
            oid = var_str.split('=')[1]
        elif 'aid=' in var_str:
            aid = var_str.split('=')[1]

    #에러난 이후부터 시작하도록 하자!
    if next :
        if aid == "0003594208" :
            next = False
        else:
            continue

    news_site = None
    dir_postfix = None
    #네이버 뉴스 링크가 아닌 경우
    if aid == None or oid == None :
        o = urlparse(row[1])
        if o.hostname == 'www.gjdream.com' :
            # 광주드림 뉴스
            news_site = "gjdream"
            #http://www.gjdream.com/v2/news/view.html?news_type=201&uid=480802
            dir_postfix="gjdream_" + params_str[0].split('=')[1] + "_" + params_str[1].split('=')[1] + ".news"
        elif o.hostname == 'news1.kr':
            #뉴스1
            news_site = "news1"
            # http://news1.kr/articles/?3023732
            dir_postfix = "news1_" + params_str[0] + ".news"
        elif o.hostname == 'view.asiae.co.kr':
            #아시아경제
            news_site = "asiae"
            #http://view.asiae.co.kr/news/view.htm?idxno=2017061813385889015
            dir_postfix = "asiae_"+ params_str[0].split('=')[1] + ".news"
        else :
            print("Unknown news site. FATAL ERROR ===> %s" % row[1])
            exit(-1)
    else :
        news_site = "naver"
        dir_postfix = oid + "_" + aid + ".news"


    # 파일을 다운로드 합시다!
    print("Try downloading %s" %( dir_postfix ))

    # 파일을 다 읽고나서 존재여부를 체크하는것보다 로컬에서 먼저 검색하고나서 체크하는 것이 효율적인듯 하다.
    for root, dirs, files in os.walk("articles"):
        for file in files:
            if str(file) == dir_postfix:
                print("File is alread exists : %s " % str(os.path.join(root, file)))
                print("SKIP")
                continue

    res = requests.get(row[1])

    if news_site == "naver":
        bs = BeautifulSoup(res.text, 'html.parser')
        title = bs.select("h3#articleTitle")[0].text
        base_dtm = bs.select("div.sponsor > span.t11")[0].text
        contents = ""

        for elmnt in bs.select("div#articleBodyContents")[0].contents:
            if type(elmnt) == NavigableString:
                if str(elmnt).strip() != '':
                    contents += str(elmnt).strip() + "\n"

    elif news_site == "gjdream":
        text = res.text.encode('latin-1').decode('cp949')
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("table > tr > td > font")[0].text
        base_dtm = bs.select("table > tr > td.f5")[1].text.split(' : ')[1].strip()
        contents = ""

        for elmnt in bs.select("div#content")[0].contents:
            if type(elmnt) == NavigableString:
                if str(elmnt).strip() != '':
                    contents += str(elmnt).strip() + "\n"

    elif news_site == "news1":
        bs = BeautifulSoup(res.text, 'html.parser')
        title = bs.select("div.title > h2")[0].text
        lst_base_dtm = bs.select("div.info")[0].contents[-1].strip().split(' ')[0:2]
        base_dtm = lst_base_dtm[0] + " " + lst_base_dtm[1]
        contents = ""

        for elmnt in bs.select("div#articles_detail")[0].contents:
            if type(elmnt) == NavigableString:
                if str(elmnt).strip() != '':
                    contents += str(elmnt).strip() + "\n"

    elif news_site == 'asiae':
        text = res.text.encode('latin-1').decode('cp949')
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("div.area_title > h1")[0].text
        #<p><span>최종수정</span> 2017.06.18 13:39
        #<span class="f">기사입력</span> 2017.06.18 13:39</p>
        lst_base_dtm = str(bs.select("div.area_title > p")[0].contents[-1]).strip().replace('.','-')
        base_dtm = lst_base_dtm[0] + " " + lst_base_dtm[1]
        contents = ""

        for elmnt in bs.select("div.article > div")[0].contents:
            if type(elmnt) == NavigableString:
                if str(elmnt).strip() != '':
                    contents += str(elmnt).strip() + "\n"

    else:
        print("Unknown news site. FATAL ERROR")
        exit(-1)

    sub_dir = base_dtm[0:4]
    if not os.path.isdir("articles/" + sub_dir):
        os.mkdir("articles/" + sub_dir)
    dest_file = "articles/" + sub_dir + "/" + dir_postfix

    if os.path.isfile(dest_file) :
        continue
    else :
        f = open(dest_file,'w',encoding="utf-8")
        f.write(title+"\n")
        f.write(base_dtm+"\n")
        f.write(contents)
        f.close()




