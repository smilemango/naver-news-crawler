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
    try:
        params_str = str(row[1]).split('?')[1].split("&")
    except IndexError as e:
        params_str = [str(row[1]).split('/')[-1] ]

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
        elif o.hostname == 'news.heraldcorp.com':
            # 헤럴드경제
            news_site = "heraldcorp"
            # http://news.heraldcorp.com/village/view.php?ud=201706141855012313875_12
            dir_postfix = "heraldcorp_" + params_str[0].split('=')[1] + ".news"
        elif o.hostname == 'www.mt.co.kr':
            # 머니투데이
            news_site = "mt"
            # http://www.mt.co.kr/view/mtview.php?type=1&no=2017060815500512576&outlink=1
            dir_postfix = news_site + "_" + params_str[1].split('=')[1] + ".news"

        elif o.hostname == 'www.newsis.com':
            # 뉴시스
            news_site = "newsis"
            # http://www.newsis.com/view/?id=NISX20170615_0000013759&cID=10812&pID=10800
            dir_postfix = news_site + "_" + params_str[0].split('=')[1] + ".news"

        else :
            #일단 넘기자
            continue
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
        base_dtm = str(bs.select("div.area_title > p")[0].contents[-1]).strip().replace('.','-')
        contents = bs.select("div.article > div")[0].text

    elif news_site == 'heraldcorp':
        text = res.text
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("div.view_top_t2 > ul > li > h1")[0].text

        raw_base_dtm = bs.select("div.view_top_t2 > ul > li.ellipsis")[0].contents[0]
        if str(raw_base_dtm).startswith('기사입력 ') :
            raw_base_dtm= str(raw_base_dtm)[5:].strip()
        base_dtm = raw_base_dtm

        contents = ""
        for elmnt in bs.select("#articleText")[0].contents:
            if type(elmnt) == NavigableString:
                if str(elmnt).strip() != '':
                    contents += str(elmnt).strip() + "\n"

    elif news_site == 'mt':
        text = res.text.encode('latin-1').decode('cp949')
        bs = BeautifulSoup(text, 'html.parser')
        try:
            title = bs.select("div#article > h1")[0].text

            base_dtm = bs.select("span.num")[0].text[2:].replace('.','-')
            contents = bs.select("div#textBody")[0].text
        except IndexError as e:
            #다른 페이지로 이동하게 되는 경우이다. 왜이리 번거롭게 만들어놨냐
            #<script>location.href="http://the300.mt.co.kr/newsView.html?no=2016100411237629327&ref=%3A%2F%2F"</script>
            next_url = bs.contents[0].text.split('"')[1]
            res = requests.get(next_url)
            text = res.text.encode('latin-1').decode('cp949')
            bs = BeautifulSoup(text, 'html.parser')
            title = bs.select("div#article > h1")[0].text
            try:
                base_dtm = bs.select("span.date")[0].text.replace('.','-')
            except IndexError as e2:
                base_dtm = bs.select("span.num")[0].text[2:].replace('.','-')
            contents = bs.select("div#textBody")[0].text


    elif news_site == 'newsis':
        text = res.text
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("div.article_tbx > h1")[0].text

        base_dtm = bs.select("div.date")[0].text[3:]
        contents = bs.select("div.article_bx > div.view_text > div#textBody")[0].text

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




