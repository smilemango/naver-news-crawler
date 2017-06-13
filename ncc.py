#news contents crawler

import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString


conn = sqlite3.connect("articles.sqlite3")

cur = conn.cursor()
cur.execute("SELECT * FROM article_title")

for row in cur:
    params_str = str(row[1]).split('?')[1].split("&")
    oid = None
    aid = None
    for var_str in params_str:
        if 'oid=' in var_str:
            oid = var_str.split('=')[1]
        elif 'aid=' in var_str:
            aid = var_str.split('=')[1]

    dir_postfix = oid + "_" + aid + ".news"
    if os.path.isfile("articles/"+dir_postfix) :
        continue
    else :
        # 파일을 다운로드 합시다!
        print(oid, aid)

        res = requests.get(row[1])
        bs = BeautifulSoup(res.text,'html.parser')
        title = bs.select("h3#articleTitle")[0].text
        base_dtm = bs.select("div.sponsor > span.t11")[0].text
        contents = ""

        for elmnt in bs.select("div#articleBodyContents")[0].contents:
            if type(elmnt) == NavigableString :
                if str(elmnt).strip() != '':
                    contents += str(elmnt).strip() + "\n"

        f = open("articles/"+dir_postfix,'w',encoding="utf-8")
        f.write(title+"\n")
        f.write(base_dtm+"\n")
        f.write(contents)
        f.close()




