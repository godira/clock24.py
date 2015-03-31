#! /usr/bin/python
# coding: UTF-8
#from Tkinter import *
import Tkinter as tk
import math, time

# グローバル変数
win_size = 200
#sin_table = []
#cos_table = []
backboard = []
radian = 3.1415/180

# メインウィンドウ
root = tk.Tk()
root.title(u'24時計')
root.minsize(160, 160)
root.maxsize(400, 400)

# キャンバス
c0 = tk.Canvas(root, width = 200, height = 200, bg = 'darkgreen')
c0.pack(expand = True, fill = tk.BOTH)

# 図形の生成
circle = c0.create_oval(5, 5, 195, 195, fill = 'lightgray', outline = 'lightgray')
#     夜
sunrise = 150
sunset = 10 + 360
night = c0.create_arc(5, 5, 195, 195, start = sunrise, extent = sunset - sunrise, fill = 'darkgray')
#     文字盤
dial0 = c0.create_text(100, 195, text = '0', anchor = 's')
dial6 = c0.create_text(5, 100, text = '6', anchor = 'w')
dial12 = c0.create_text(100, 5, text = '12', anchor = 'n')
dial18 = c0.create_text(195, 100, text = '18', anchor = 'e')

for i in range( 12 ):
    backboard.append(c0.create_line(i, i, 135, 135, width = 2.0))
hour = c0.create_line(100, 100, 100, 60, fill = 'blue', width = 3.0)
min  = c0.create_line(100, 100, 100, 50, fill = 'green', width = 2.0)
sec  = c0.create_line(100, 100, 100, 45, fill = 'red')

# データの初期化
#def init_data():
#    for i in range(720):
#        rad = 3.14 / 360 * i
#        sin_table.append(math.sin(rad))
#        cos_table.append(math.cos(rad))


# 背景の描画
def draw_backboard():
    r = win_size / 2
    # 円
    c0.coords(circle, 5, 5, win_size - 5, win_size - 5)
    # 夜
    c0.coords(night, 5, 5, win_size - 5, win_size - 5)
    # 目盛(30度ピッチ)
    for i in range(12):
        n = i * 30
        x1 = r + (r - 25) * math.sin(radian * n)
        y1 = r + (r - 25) * math.cos(radian * n)
        x2 = r + (r - 25) * 4 / 5 * math.sin(radian * n)
        y2 = r + (r - 25) * 4 / 5 * math.cos(radian * n)
        c0.coords(backboard[i], x1, y1, x2, y2)
    # 文字盤
    c0.coords(dial0, r, win_size - 8)
    c0.coords(dial6, 10, r)
    c0.coords(dial12, r, 8)
    c0.coords(dial18, win_size - 8, r)

# 針を描く
def draw_hand():
    t = time.localtime()
    r = win_size / 2
    rs = r * 7 / 10
    rm = r * 6 / 10
    rh = r * 5 / 10
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
    h = h + 12
    n = h * 15 + t[4] * 0.25
    x = r + rh * math.sin(radian * n)
    y = r - rh * math.cos(radian * n)
    c0.coords(hour, r, r, x, y)

# 大きさの変更
def change_size(event):
    global win_size
    w = c0.winfo_width()
    h = c0.winfo_height()
    if w < h:
        win_size = w
    else:
        win_size = h
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
