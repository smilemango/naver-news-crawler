import matplotlib
matplotlib.use('TkAgg')

import os
from konlpy.tag import Twitter
import nltk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import rc
from gensim.models.word2vec import Word2Vec
import tkinter as Tk
import gensim
import sklearn
from sklearn.manifold import TSNE


rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

t = Twitter()

files = [f for f in os.listdir('articles') if f.endswith('.news')]
count = 0
contents = ""
for file in files:
    f = open("articles/"+file,mode='r',encoding='utf-8')
    contents += f.read()
    print("READ : %s" % "articles/"+file )

    count +=1
    if count == 2000 :
        break

print("형태소 분석 시작")
pos_doc = []
sentence = []
for p in t.pos(contents):
    if p[1] == 'Josa' or p[1] =='Punctuation' or p[1] == 'Suffix' or p[1] == 'Eomi' or p[1] == 'Number':
        continue
    else :
        sentence.append( "/".join(p) )

    if len(sentence) == 10 :
        pos_doc.append(sentence)
        sentence = []

pos_doc.append(sentence)

model = Word2Vec(pos_doc,sg=1, size=400, window=50, min_count=100)
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

from sklearn.cluster import KMeans
import numpy as np

kmeans = KMeans(n_clusters=10 if len(points) >= 10 else len(points), n_jobs=-1, random_state=0)
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
    t.set_visible(True)
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


Tk.mainloop()