#news contents crawler

import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString


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


    dir_postfix = oid + "_" + aid + ".news"

    # 파일을 다운로드 합시다!
    print("Try downloading oid=%s, aid=%s" %( oid, aid))

    # 파일을 다 읽고나서 존재여부를 체크하는것보다 로컬에서 먼저 검색하고나서 체크하는 것이 효율적인듯 하다.
    for root, dirs, files in os.walk("articles"):
        for file in files:
            if str(file) == dir_postfix:
                print("File is alread exists : %s " % str(os.path.join(root, file)))
                print("SKIP")
                continue

    res = requests.get(row[1])
    bs = BeautifulSoup(res.text, 'html.parser')
    title = bs.select("h3#articleTitle")[0].text
    base_dtm = bs.select("div.sponsor > span.t11")[0].text
    contents = ""

    for elmnt in bs.select("div#articleBodyContents")[0].contents:
        if type(elmnt) == NavigableString:
            if str(elmnt).strip() != '':
                contents += str(elmnt).strip() + "\n"

    sub_dir = base_dtm[0:4]
    if os.path.isdir("articles/"+sub_dir) == False :
        os.mkdir("articles/"+ sub_dir)
    dest_file="articles/"+sub_dir+"/"+dir_postfix
    if os.path.isfile(dest_file) :
        continue
    else :
        f = open(dest_file,'w',encoding="utf-8")
        f.write(title+"\n")
        f.write(base_dtm+"\n")
        f.write(contents)
        f.close()




