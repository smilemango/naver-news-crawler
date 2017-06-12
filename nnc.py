
import requests
from bs4 import BeautifulSoup
import pprint as pp




def search_news(keyword='산업은행', start_date='1990-01-01', end_date='1990-12-31', page=1):
    #      http://news.naver.com/main/search/search.nhn?detail=1&query=%BB%EA%BE%F7%C0%BA%C7%E0&startDate=1990-01-01&endDate=1999-12-31
    url = "http://news.naver.com/main/search/search.nhn"
    params = {
            'page' : page,
            'detail' : 1,
            'startDate': start_date,
            'endDate':end_date,
            'query' :  keyword.encode('cp949')

    }
    #http://news.naver.com/main/search/search.nhn
    # ?refresh=&so=rel.dsc&stPhoto=&stPaper=&stRelease=
    # &ie=MS949&detail=0&rcsection=&query=%BB%EA%BE%F7%C0%BA%C7%E0
    # &x=22&y=13&sm=all.basic&pd=4
    # &startDate=1960-01-01&endDate=1999-12-31
    r = requests.get(url,params=params)

    return r


page = 1
while True:
    bs = BeautifulSoup(search_news(page=page).text,'html.parser')
    #bs.select("a.tit")
    #bs.select("div.paging > a")

    for tit in bs.select("a.tit"):
        print("%s : %s" %(tit.text, tit.attrs['href']))

    #for tag in bs.select("div.paging > a"):
    #    pp.pprint(tag)

    if bs.select("div.paging > a")[-1].text != '다음':
         if page == int(bs.select("div.paging > *")[-1].text):
             break

    page+=1


