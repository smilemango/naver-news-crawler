import matplotlib
matplotlib.use('TkAgg')

import os
from konlpy.tag import Twitter
import nltk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import rc, font_manager
from gensim.models.word2vec import Word2Vec
import tkinter as Tk
import gensim
import sklearn
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import numpy as np
import platform


if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)

plt.rcParams['axes.unicode_minus'] = False

t = Twitter()


dest_dir = [
    "articles/1990",
    "articles/1991",
    "articles/1992",
    "articles/1993",
    "articles/1994",
    "articles/1995",
    "articles/1996",
    "articles/1997",
    "articles/1998",
    "articles/1999",
    "articles/2000",
    "articles/2001",
    "articles/2002",
    "articles/2003",
    "articles/2004",
    "articles/2005",
"articles/2006",
"articles/2007",
"articles/2008",
"articles/2009",
"articles/2010",
"articles/2011",
"articles/2012",
# "articles/2013",
# "articles/2014",
"articles/2015",
"articles/2016",
"articles/2017",
            ]

files = []
for a_dest_dir in dest_dir:
    files = files + [(a_dest_dir +"/" + f) for f in os.listdir(a_dest_dir) if f.endswith('.news')]

count = 0
contents = []
for file in files:
    f = open(file,mode='r',encoding='utf-8')
    contents.append(f.read())
    print("READ : %s" % file )

    count +=1
    #if count == 100 :
    #    break

print("형태소 분석 시작")

ignore_words = ['무단','전재','c','▲','배포','저작권','발행','연합뉴스','금지','시','또','\'','천만','한편','분','부','억',
                '금','총','천억원','산','날','며','"','주','후','이','뒤','천','비','이','세','에서','연','말','개','와',
                '은','각','위해','점','못','조','억원','크게','로','종','때','각각','추가','한','백','월','차','인','및',
                '의','전','단','당시','기자','데','때문','계속','과','일','별','것','오전','이후','채','수','년',
                '이번','작년','지난해','앞','선','따라서','여부','방식','위','씨','대해','그러나','를','율','주요',
                '당초','를','사','만','사','도','최근','재','씨','앞','백만','계','관','임','명','내','로부터',
                '국','회','중','고','그','원','달','일반','행','등','제','자','단계','함','지난','가장','또한',
                '형태','감안','통한','뿐','나','지난달','다시','외','보','약','액','폭','투','률','통해','확보','만큼',
                '직접','월말','경우','예정','현재','이상','회의','수준','관련','과정','올해','연합','가능성',
                '가운데','관계','상황','적극','확정','조치','정도','과정','포인트','내년','규모','추진','관계자','여신',
                '보두','기간','일부','사실','내용','조건','상태','결과','전체','추진','조원','모두','가격','수석','애널',
                '리스트','B','C','S','P','천만원','백만원','인하','건강','신규','백억원','유','리','A','지표','전략','기준',
                '폐지','홍','초과','가치','분담','장비','공모','절반','나머지','집행','예비','최','정','임원','시기',
                '홍','의견','설','위험','고려','단기','호','외국인','자유','심사','운영','차장','팀','반','가입','불',
                '사례','허가','차장','자료','직업','업무','공','이하','용','지지','표시','이용','통신','표','개별','별로',
                '규정','의무','퇴','주로','비교','둔화','작','배','오후','다른','다음','작업','확대','설립','영업','유치',
                '방안','안','하반기','상반기','더','돈','지금','기존','두','합의','만원','물론','끝','라며','면서',
                '자체','기존','모든','방향','부분','문제','이유','요인','관심','다소','바','차원','지속',
                '공통','통합','스','대표','김','마련','무','기능','업','Copyright','방침','대한','요구','분기',
                '순','현','분야','동안','어려움','효과','중심','각종','시간','방법','본격','장','하지만','입장','논란',
                '제기','주장','저','알','기본','예','목표','곳','대부분','반면','분석','거의','현실','오히려','제대로',
                '볼','달리','수도','자율','사항','책임','주의','결정','수도','사람','온','노력','줄','위기','진','이전',
                '허용','지정','신','개월','우려','영향','참여','시각','처음','이중','여','하향','내달','논의',
                '설명','동시','직','게','아직','역시','모습','분위기','실제','전혀','매우','일시','M','과거','사정','그동안',
                '긍정','새','일단','마무리','올','연말','가지','역할','의미','해','첫','차례','치','까지','준','이내',
                '건','최종','금액','뉴','합','포','권','상','D','양','처','더욱','지적','전문가','구축','부문','비중','감소',
                '년말','보고','중앙','어치','기록','협회','전날','마감','발인','원장','지수','계약','체결','서비스','정보',
                '취급','거래','공정','목적','주거','시행','시스템','기술','소재','음','원칙','시점','능력','성과','효율','개편',
                '신설','별도','아','향후','불안','주도','심리','사태','강','상승','급락','하락','반등','강세','급','역',
                '증시','주식시장','전망','예상','실적','기','MoneyToday','내부','외부','체제','해결','이제','화의','연간',
                '책','보이','움직임','포함','후보','개사','일이','자신','이기','로서','이제','변화','힘','경기','여건','전반',
                '회복','움직임','보이','동의','연장','도래','장기','상품','적용','대상','해당','운용','재정','비율','All',
                '대상','해당','지급','현금','대금','열사','매매','금사','유입','호전','급등','오른','호전','성공','남','뜻','달라',
                '계기','필요','동향','점검','발표','신문','방문','점포','층','간담','초','가량','앞서','실무','생각','쪽','먼저',
                '중단','계획','제안','일정','변경','자리','연구','위원','연구원','연구소','완료','승인','금년','그리고','다만','결론',
                '절차','활성화','촉진','우선','지원','처리','보고서','대비','흑자','적자','순이익','손실','이익','the','상대로',
                '평균','개방','평가','자본금','최고','주인','준비','고위','컨소시엄','의사','개선','조직','문','구','물',
                '조기','유도','공시','출범','분리','여명','명의','선정','상당','의지','해소','매수','매도','머니투데이','rights',
                '상승세','매각','전제','종목','물량','특혜','업종','노','당','반발','bp','천억','뉴시스','연합인포맥스',
                '추정','대화','측','BBB','부친상','겸','창','소','행','특별','요청','유지','주간','아이',
                '차지','전화','연속','공개','사고','하루','실','입','활동','흐름','기조',
                '부사','간','바로','약세','기대','감','추세','매물','선물','상대','경험','모친상',
                '단지','신속','검','측은','모','분','평','사이','적','빚','여기','기회','여러',
                '얘기','이처럼','차이','반응','대응','속','수용','접수','순위','무엇','편입','진행',
                '조만간','현안','진행중','오늘','확인','정기','최대','처분','현안','공동','손','주가',
                '셈','교환','엄','금감','회수','사용','독자','edaily','내일','그리고','먼저']

pos_doc = []
sentence = []
for a_content in contents:
    for p in t.pos(a_content):
        if p[1] == 'Josa' or p[1] =='Punctuation' or p[1] == 'Suffix' or p[1] == 'Eomi' \
                or p[1] == 'Number' or p[1] == 'Verb' or p[1] =='Adjective' or p[1] == 'Adverb'\
                or p[1] == 'PreEomi' or p[1] == 'Foreign' \
                or p[0] in ignore_words:
            continue
        else :
            sentence.append( "/".join(p) )

    pos_doc.append(sentence)
    sentence = []

pos_doc.append(sentence)

model = Word2Vec(pos_doc,sg=0, size=700, window=1000,min_count=3500,iter=10)
tsne = sklearn.manifold.TSNE(n_components=2, random_state=0)
all_word_vectors_matrix_2d = tsne.fit_transform(model.wv.syn0)

import pandas as pd

points = pd.DataFrame(
            [
                (word, coords[0], coords[1])
                for word, coords in [
                    (word, all_word_vectors_matrix_2d[model.wv.vocab[word].index])
                    for word in model.wv.vocab
                ]
            ],
            columns=["word", "x", "y"]
        )



root = Tk.Tk()
root.wm_title("Embedding in TK")

from matplotlib.figure import Figure

f = Figure(figsize=(5, 4), dpi=100)
ax = f.add_subplot(111)


kmeans = KMeans(n_clusters=10, n_init=1, random_state=0)
# cluster_idx = kmeans.fit_predict(points[["x","y"]])
kmeans.fit(points[["x", "y"]])
cluster_idx = kmeans.labels_

points['cluster'] = pd.Series(np.asarray(cluster_idx))

cluster = {}
for idx, point in points.iterrows():
    if point['cluster'] in cluster:
        cluster[point['cluster']].append(idx)
    else:
        cluster[point['cluster']] = []
        cluster[point['cluster']].append(idx)

for c in cluster:
    points_by_cluster = pd.DataFrame(columns=('x', 'y', 'word', 'cluster'))
    for idx in cluster[c]:
        points_by_cluster = points_by_cluster.append(points.iloc[[idx]])
    # list = [points.iloc[[idx]] for idx in cluster[c]]
    ax.scatter(points_by_cluster['x'], points_by_cluster['y'], alpha=0.7)

text_labels = []
for i, point in points.iterrows():
    t = ax.text(point.x + 0.0001, point.y, point.word, fontsize=10, alpha=0.8,
                url="http://www.instagram.com/" + point.word)
    t.set_visible(False)
    text_labels.append(t)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

def on_key_event(event):
    print('you pressed %s' % event.key)
    key_press_handler(event, canvas, toolbar)


toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
canvas.mpl_connect('key_press_event', on_key_event)

bottom_panel = Tk.PanedWindow(master=root)
bottom_panel.pack(side=Tk.BOTTOM)

def toggle_label():
    if btnToggle.config('text')[-1] == '라벨 감추기':
        btnToggle.config(text='라벨 보여주기')
    else:
        btnToggle.config(text='라벨 감추기')

    if btnToggle.config('text')[-1] == '라벨 감추기':
        for label in text_labels:
            label.set_visible(True)
    else:
        for label in text_labels:
            label.set_visible(False)
    canvas.draw()


btnToggle = Tk.Button(master=bottom_panel, text="라벨 보여주기", width=12, command=toggle_label)
btnToggle.pack(side=Tk.LEFT)


Tk.mainloop()