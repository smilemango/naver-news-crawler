#news contents crawler

import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString
from urllib.parse import urlparse
from urllib.parse import parse_qs
import httputil
import io
import chardet


conn = sqlite3.connect("articles.sqlite3")

cur = conn.cursor()
cur.execute("SELECT * FROM article_title where (is_downloaded = 0 or is_downloaded is null) and URL like 'http://biz.chosun.c%';")

next = True
for row in cur.fetchall():
    aid = None
    oid = None

    news_url = row[1]
    url_qry = None
    if '?' in row[1] :
        url_qry = parse_qs(row[1].split('?')[1])
    else :
        #parse_qs로 파싱이 안되는 경우
        try:
            params_str = str(row[1]).split('?')[1].split("&")
        except IndexError as e:
            params_str = [str(row[1]).split('/')[-1] ]

    if not url_qry is None:
        if not url_qry.get('oid') == None:
            oid = url_qry.get('oid')[0]
            aid = url_qry.get('aid')[0]

    news_site = None
    dir_postfix = None
    #네이버 뉴스 링크가 아닌 경우
    if aid == None or oid == None :
        o = urlparse(row[1])
        if o.hostname == 'www.gjdream.com' :
            # 광주드림 뉴스
            news_site = "gjdream"
            #http://www.gjdream.com/v2/news/view.html?news_type=201&uid=480802
            dir_postfix="gjdream_" + url_qry.get('news_type')[0] + "_" + url_qry.get('uid')[0] + ".news"
        elif o.hostname == 'news1.kr':
            #뉴스1
            news_site = "news1"
            # http://news1.kr/articles/?3023732
            dir_postfix = "news1_" + params_str[0] + ".news"
        elif o.hostname == 'view.asiae.co.kr' or o.hostname == 'www.asiae.co.kr' :
            #아시아경제
            news_site = "asiae"
            #http://view.asiae.co.kr/news/view.htm?idxno=2017061813385889015
            #http://www.asiae.co.kr/uhtml/read.jsp?idxno=181892&ion=S1N53&ion2=S2N213
            dir_postfix = news_site + "_" + url_qry.get('idxno')[0]  + ".news"

        elif o.hostname == 'news.heraldcorp.com':
            # 헤럴드경제
            news_site = "heraldcorp"
            # http://news.heraldcorp.com/village/view.php?ud=201706141855012313875_12
            dir_postfix = "heraldcorp_" + url_qry.get('ud')[0] + ".news"
        elif o.hostname == 'www.mt.co.kr':
            # 머니투데이
            news_site = "mt"
            # http://www.mt.co.kr/view/mtview.php?type=1&no=2017060815500512576&outlink=1
            dir_postfix = news_site + "_" + url_qry.get('no')[0] + ".news"

        elif o.hostname == 'www.newsis.com':
            # 뉴시스
            news_site = "newsis"
            # http://www.newsis.com/view/?id=NISX20170615_0000013759&cID=10812&pID=10800
            dir_postfix = news_site + "_" + url_qry.get('id')[0] + ".news"

        elif o.hostname == 'www.edaily.co.kr':
            # 이데일리
            news_site = "edaily"
            # http://www.edaily.co.kr/news/newspath.asp?newsid=04391926615962048
            if not url_qry.get('newsid') == None :
                dir_postfix = news_site + "_" + url_qry.get('newsid')[0] + ".news"
            #http://www.edaily.co.kr/news/related_article.edy?uid=1175703&mcd=01
            elif not url_qry.get('uid') == None:
                dir_postfix = news_site + "_"+ url_qry.get('uid')[0] +"_" + url_qry.get('mcd')[0] + ".news"

        elif o.hostname == 'news.mk.co.kr':
            # 매경
            news_site = "mk"
            # http://news.mk.co.kr/newsRead.php?&year=2017&no=357698
            dir_postfix = news_site + "_" + url_qry.get('year')[0] + "_" + url_qry.get('no')[0] + ".news"

        elif o.hostname == 'www.fnnews.com':
            # 파이낸셜뉴스
            news_site = "fnnews"
            # http://www.fnnews.com/news/201705312021291702
            dir_postfix = news_site + "_" + params_str[0] + ".news"

        elif o.hostname == 'www.hankyung.com':
            # 한국경제
            news_site = "hankyung"
            # http://www.hankyung.com/news/app/newsview.php?aid=2017053129361
            dir_postfix = news_site + "_" + url_qry.get('aid')[0] + ".news"

        elif o.hostname == 'www.newspim.com':
            # newspim
            news_site = "newspim"
            # http://www.newspim.com/sub_view.php?cate1=3&cate2=6&news_id=100534
            dir_postfix = news_site + "_" + url_qry.get('cate1')[0] +"_" + url_qry.get('cate2')[0] + "_" + url_qry.get('news_id')[0]  + ".news"
            news_url  = "http://www.newspim.com/news/view/" + url_qry.get('news_id')[0]

        elif o.hostname == 'www.etoday.co.kr':
            # etoday
            news_site = "etoday"
            # http://www.etoday.co.kr/news/section/newsview.php?TM=news&SM=0404&idxno=308376
            dir_postfix = news_site + "_" + url_qry.get('TM')[0] +"_" + url_qry.get('SM')[0] + "_" + url_qry.get('idxno')[0]  + ".news"

        elif o.hostname == 'app.yonhapnews.co.kr':
            # 연합뉴스
            news_site = "yonhapnews"
            # http://app.yonhapnews.co.kr/YNA/Basic/SNS/r.aspx?c=AKR20170606076600002&did=1195m
            dir_postfix = news_site + "_" + url_qry.get('c')[0]  + ".news"

        elif o.hostname == 'biz.chosun.com':
            # 비즈조선
            news_site = "biz.chosun"
            # http://biz.chosun.com/site/data/html_dir/2011/07/14/2011071401906.html
            dir_postfix = news_site + "_"  + row[1].split('html_dir/')[1][:-5].replace('/','_')  + ".news"

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
                if os.stat(str(os.path.join(root, file))).st_size > 0 : #파일 사이즈가 0보다 크면
                    print("File is alread exists : %s " % str(os.path.join(root, file)))
                    print("SKIP")
                    qry = "UPDATE article_title set is_downloaded = 1 where id = %d ;" % row[0]
                    cur.execute(qry)
                    conn.commit()
                    continue

    res = requests.get(news_url)
    return_val = 1

    if news_site == "naver":
        bs = BeautifulSoup(res.text, 'html.parser')
        try:
            title = bs.select("h3#articleTitle")[0].text
            base_dtm = bs.select("div.sponsor > span.t11")[0].text
            contents = ""
            for elmnt in bs.select("div#articleBodyContents")[0].contents:
                if type(elmnt) == NavigableString:
                    if str(elmnt).strip() != '':
                        contents += str(elmnt).strip() + "\n"
        except IndexError as e:
            #연예면 기사의 경우 형식이 조금 다르다
            title = bs.select("h2.end_tit")[0].text
            base_dtm = bs.select("div#content > div.end_ct > div > div.article_info > span > em")[0].text.replace('.','-')
            contents = bs.select("div#articeBody")[0].text

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
        try:
            title = bs.select("div.title > h2")[0].text
            lst_base_dtm = bs.select("div.info")[0].contents[-1].strip().split(' ')[0:2]
            base_dtm = lst_base_dtm[0] + " " + lst_base_dtm[1]
            contents = ""

            for elmnt in bs.select("div#articles_detail")[0].contents:
                if type(elmnt) == NavigableString:
                    if str(elmnt).strip() != '':
                        contents += str(elmnt).strip() + "\n"
        except IndexError as e :
            if not "http404" in bs.select("img#img")[0].attrs["src"]:
                #page not found
                continue


    elif news_site == 'asiae':
        if res.text.startswith('<script') and res.url.startswith('http://www.asiae'):
            bs = BeautifulSoup(res.text, 'html.parser')
            new_url = 'http://www.asiae.co.kr' + bs.select('script')[0].text.split("'")[1]
            res = requests.get(new_url)

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
        try:
            title = bs.select("div.article_tbx > h1")[0].text

            base_dtm = bs.select("div.date")[0].text[3:]
            contents = bs.select("div.article_bx > div.view_text > div#textBody")[0].text
        except IndexError as e :
            if "GISA FILE NOT EXISTS" in bs.select("p.mgt18")[0].text:
                #기사가 삭제됨
                print("Article was deleted.")
                continue

    elif news_site == 'edaily':
        text = res.text.encode('latin-1').decode('cp949')
        bs = BeautifulSoup(text, 'html.parser')
        if bs.select('div#viewarea > h4'):
            title = bs.select("div#viewarea > h4")[0].text

            base_dtm = bs.select("div#viewarea > div.pr > p.newsdate")[0].text.split('|')[1].replace('.','-').strip()
            contents = bs.select("span#viewcontent_inner")[0].text.encode('utf-8','ignore').decode('utf-8') #깨진문자가 있다면 이과정에서 무시된다.
        elif len(bs.select("div.left > p > a > img")) > 0:
            # 사진 기사
            """"""
            return_val =2
        elif len(bs.select('h4.newstitle')) > 0 :
            title = bs.select("h4.newstitle")[0].text

            base_dtm = bs.select("p.newsdate")[0].text.split('|')[1].replace('.','-').strip()
            contents = bs.select("span#viewcontent_inner")[0].text


    elif news_site == 'mk':
        text = res.text.encode('latin-1').decode('cp949')
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("div#top_header > div > div > h1")[0].text

        base_dtm = bs.select("div#top_header > div > div > div.news_title_author > ul > li.lasttime")[0].text.split(' :')[1].strip().replace('.','-')
        contents = bs.select("div#article_body")[0].text

    elif news_site == 'fnnews':# finanncial news
        text = res.text
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("div#container > div > div.article_head > h1")[0].text

        base_dtm = bs.select("div#container > div > div.article_head > div > em")[1].text.split(' :  ')[1].replace('.','-')
        contents = bs.select("div#article_content > div")[0].text

    elif news_site == 'hankyung':# 한국경제
        # 얘네는 응답이 chunked reponse로 온다.
        # 이경우
        # [byte수]\r\n
        # 데이터
        # \r\n[byte수]\r\n
        # 데이터
        # 반복...
        # \r\n0\r\n\r\n

        type = None
        if res.text.startswith('<!'):
            if res.request.url.startswith('http://hei'):
                type = 'hei' #한경 연예면
                text = res.content.decode()
            elif res.request.url.startswith('http://plus'):
                type = 'plus' #한경 플러스
                text = res.text.encode('latin-1').decode('cp949')
            else :
                text = res.text
        else:
            gzipped_bytes = res.content
            text =  b''.join(httputil.read_body_stream(io.BytesIO(gzipped_bytes), chunked=True, compression=httputil.GZIP)).decode()

        bs = BeautifulSoup(text, 'html.parser')

        if type == None:
            title = bs.select('div#container > div.artlcle_top > h2.tit')[0].text

            base_dtm = bs.select('div#container > div.wrap_container > div > div.info_article > div.date > span')[0].text[3:]
            contents = bs.select('div#newsView')[0].text

        elif type == 'hei':
            title = bs.select('div#container > section > h1')[0].text
            base_dtm = bs.select('div#container > section > div > div.atc-info > span')[0].text[3:]

            contents = bs.select('article#newsView')[0].text
        elif type == 'plus':
            title = bs.select('section#container > section.service_cnt > article > article > header > h2')[0].text
            base_dtm = bs.select('section#container > section.service_cnt > article > article > p.info > span')[1].text

            contents = bs.select('div.articleContent')[0].text

    elif news_site == 'newspim':# newspim
        text = res.text
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("div.bodynews_title > h1")[0].text

        base_dtm = bs.select("div.bodynews_title > ul > li.writetime")[0].text.split(' : ')[1].replace('년','-').replace('월','-').replace('일','')
        contents = bs.select("div#news_contents")[0].text

    elif news_site == 'etoday':# etoday
        text = res.text
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.select("#article_title")[0].text

        base_dtm = bs.select("#ViewHeader > div.byline > em")[0].text.split(' : ')[1]
        contents = bs.select("#block_body > div > div > div.cont_left_article")[0].text

    elif news_site == 'yonhapnews':#yonhapnews
        if '/photos/' in res.url: #사진 기사일경우 스크랩하지 않는다.
            return_val = 2
        else:
            text = res.content.decode()
            bs = BeautifulSoup(text, 'html.parser')
            title = bs.select("#articleWrap > h1")[0].text

            base_dtm = bs.select("div.share-info > span > em")[0].text.replace('/','-')
            contents = bs.select("#articleWrap > div.article")[0].text

    elif news_site == 'biz.chosun':# biz chosun
        if res.text.startswith('<meta'):
            #<meta http-equiv="Refresh" Content="0;url=http://premium.chosun.com/site/data/html_dir/2012/01/29/2012012967006.html"/>
            next_url = res.text.split('url=')[1][:-3]
            res = requests.get(next_url)
            text =res.content.decode()
            bs = BeautifulSoup(text, 'html.parser')
            title = bs.select("#title_text")[0].text

            base_dtm = bs.select("span.date_text")[0].text.split(' : ')[1].strip().replace('.','-')
            contents = bs.select("#par")[0].text

        else :
            text =res.content.decode()
            bs = BeautifulSoup(text, 'html.parser')

            if bs.select('head > title')[0].text == '404 Not Found':
                return_val = 3

            else:
                title = bs.select("#title_text")[0].text
                base_dtm = bs.select("#date_text")[0].text.split(' : ')[1].strip().replace('.','-')
                contents = bs.select("#article_2011")[0].text

    else:
        print("Unknown news site. FATAL ERROR")
        exit(-1)

    if return_val == 1:
        sub_dir = base_dtm[0:4]
        if not os.path.isdir("articles/" + sub_dir):
            os.mkdir("articles/" + sub_dir)
        dest_file = "articles/" + sub_dir + "/" + dir_postfix

        if not os.path.isfile(dest_file) or ( os.path.isfile(dest_file) and os.stat(dest_file).st_size == 0 ):
            f = open(dest_file,'w',encoding="utf-8")
            f.write(title+"\n"+ base_dtm+"\n"+ contents)
            f.close()

            # is_downloaeded
            # 0: not downloaded
            # 1: downloaeded
            # 2: not need to download
            # 3: 404 not found
            qry = "UPDATE article_title set is_downloaded = %d where id = %d ;" % (return_val, row[0])
            cur.execute(qry)
            conn.commit()







