#! /usr/bin/python3
# coding: UTF-8
from Tkinter import *
import math, time

# メインウィンドウ
root = Tk()
root.title(u'時計')
root.minsize(100, 100)
root.maxsize(400, 400)

# グローバル変数
width = 140
sin_table = []
cos_table = []
backboard = []
radian = 3.1415/180

# キャンバス
c0 = Canvas(root, width = 140, height = 140, bg = 'darkgreen')
c0.pack(expand = True, fill = BOTH)

# 図形の生成
circle = c0.create_oval(5, 5, 135, 135, fill = 'darkgray', outline = 'darkgray')
for i in range( 12 ):
    backboard.append(c0.create_line(i, i, 135, 135, width = 2.0))
hour = c0.create_line(70, 70, 70, 30, fill = 'blue', width = 3.0)
min  = c0.create_line(70, 70, 70, 20, fill = 'green', width = 2.0)
sec  = c0.create_line(70, 70, 70, 15, fill = 'red')

# データの初期化
#def init_data():
#    for i in range(720):
#        rad = 3.14 / 360 * i
#        sin_table.append(math.sin(rad))
#        cos_table.append(math.cos(rad))


# 背景の描画
def draw_backboard():
    r = width / 2
    # 円
    c0.coords(circle, 5, 5, width - 5, width - 5)
    # 目盛(30度ピッチ)
    for i in range(12):
        n = i * 30
        x1 = r + (r - 5) * math.sin(radian * n)
        y1 = r + (r - 5) * math.cos(radian * n)
        x2 = r + (r - 5) * 4 / 5 * math.sin(radian * n)
        y2 = r + (r - 5) * 4 / 5 * math.cos(radian * n)
        c0.coords(backboard[i], x1, y1, x2, y2)

# 針を描く
def draw_hand():
    t = time.localtime()
    r = width / 2
    rs = r * 7 / 8
    rm = r * 6 / 8
    rh = r * 5 / 8
    # 秒(1秒で6度)
    n = t[5] * 6
    x = r + rs * math.sin(radian * n)
    y = r - rs * math.cos(radian * n)
    c0.coords(sec, r, r, x, y)
    # 分(1分で6度+1秒で0.1度)
    n = t[4] * 6 + t[5] * 0.1
    x = r + rm * math.sin(radian * n)
    y = r - rm * math.cos(radian * n)
    c0.coords(min, r, r, x, y)
    # 時 (２４時間表示で下が０時)
    h = t[3]
#    if h >= 12: h -= 12
#    n = h * 60 + t[4]
    h = h - 12
    if h < 0: h += 24
    n = h * 15 + t[4] * 0.25
    x = r + rh * math.sin(radian * n)
    y = r - rh * math.cos(radian * n)
    c0.coords(hour, r, r, x, y)

# 大きさの変更
def change_size(event):
    global width
    w = c0.winfo_width()
    h = c0.winfo_height()
    if w < h:
        width = w
    else:
        width = h
    draw_backboard()
    draw_hand()

# 表示
def show_time():
    draw_hand()
    root.after(1000, show_time)

# バインディング
root.bind('<Configure>', change_size)

# データの初期化
#init_data()

# 最初の起動
draw_backboard()
show_time()

# メインループ
root.mainloop()
