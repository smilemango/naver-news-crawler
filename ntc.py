import requests
from bs4 import BeautifulSoup
import sqlite3

#New Title Crawler

conn = sqlite3.connect("articles.sqlite3")


def search_news(keyword='산업은행', start_date='1991-01-01', end_date='1999-12-31', page=1):
    #      http://news.naver.com/main/search/search.nhn?detail=1&query=%BB%EA%BE%F7%C0%BA%C7%E0&startDate=1990-01-01&endDate=1999-12-31
    url = "http://news.naver.com/main/search/search.nhn"
    params = {
            'page' : page,
            'detail' : 1,
            'startDate': start_date,
            'endDate':end_date,
            'query' :  keyword.encode('cp949')
    }
    r = requests.get(url,params=params)

    return r


page = 1
while True:
    bs = BeautifulSoup(search_news(page=page).text,'html.parser')
    #bs.select("a.tit")
    #bs.select("div.paging > a")
    cur = conn.cursor()
    count = 0
    for tit in bs.select("a.tit"):
        if 'http://sports.' in str(tit.attrs['href']):
            #스포츠 뉴스는 거른다.
            continue
        qry = "INSERT OR IGNORE INTO article_title (url, title) VALUES ('%s','%s')" % ( str(tit.attrs['href']).replace("'","''"),str(tit.text).replace("'","''"))
        cur.execute(qry)
        count += 1
    conn.commit()
    print("%d rows inserted." % count )
    #for tag in bs.select("div.paging > a"):
    #    pp.pprint(tag)
    if bs.select("div.paging > a")[-1].text != '다음':
         if page == int(bs.select("div.paging > *")[-1].text):
             break
    page+=1


