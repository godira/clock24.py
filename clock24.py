#! /usr/bin/python3
# coding: UTF-8

import Tkinter as tk
import math, time, datetime

# この場所のデータ
la = 34.8   # 緯度(度)。北緯は+,南緯は-
lo = 140.0  # 経度(度)。東経は+,西経は-
alt = 0.0   # 標高(m)
tdiff = 9.0   # グリニッジ標準時との時差

# 三角関数を度で計算
def sind(d):
	return math.sin(d*rad)
def cosd(d):
	return math.cos(d*rad)
def tand(d):
	return math.tan(d*rad)
	
# Julius year の計算(2000/1/1からの時間)
def jy(yy, mm, dd, h, m, s, tdiff):
	yy -= 2000
	if mm <= 2 :
		mm += 12
		yy -= 1
	k = 365 * yy + 30 * mm + dd - 33.5 - tdiff / 24.0 + math.floor(3 * (mm + 1) / 5.0) \
	+ math.floor(yy / 4.0) - math.floor(yy / 100.0) + math.floor(yy / 400.0)
	k += ((s / 60.0 + m) / 60.0 + h) / 24.0  # 時間をたす
	k += (65 + yy) / 86400.0  # delta T をたす
	return k / 365.25

# 太陽位置1 (celestial longitude, degree)
def spls(t):  # t Julius
	l = 280.4603 + 360.00769 * t \
	+ (1.9146 - 0.00005 * t) * sind(357.538 + 359.991 * t) \
	+ 0.0200 * sind(355.05 +  719.981 * t) \
	+ 0.0048 * sind(234.95 +   19.341 * t) \
	+ 0.0020 * sind(247.1  +  329.640 * t) \
	+ 0.0018 * sind(297.8  + 4452.67  * t) \
	+ 0.0018 * sind(251.3  +    0.20  * t) \
	+ 0.0015 * sind(343.2  +  450.37  * t) \
	+ 0.0013 * sind( 81.4  +  225.18  * t) \
	+ 0.0008 * sind(132.5  +  659.29  * t) \
	+ 0.0007 * sind(153.3  +   90.38  * t) \
	+ 0.0007 * sind(206.8  +   30.35  * t) \
	+ 0.0006 * sind( 29.8  +  337.18  * t) \
	+ 0.0005 * sind(207.4  +    1.50  * t) \
	+ 0.0005 * sind(291.2  +   22.81  * t) \
	+ 0.0004 * sind(234.9  +  315.56  * t) \
	+ 0.0004 * sind(157.3  +  299.30  * t) \
	+ 0.0004 * sind( 21.1  +  720.02  * t) \
	+ 0.0003 * sind(352.5  + 1079.97  * t) \
	+ 0.0003 * sind(329.7  +   44.43  * t)
	while l >= 360 :
		l -= 360
	while l < 0 :
		l += 360
	return l

# 太陽位置2 (distance, AU)
def spds(t):  # t Julius
	r = (0.007256 - 0.0000002 * t) * sind(267.54 + 359.991 * t) \
	+ 0.000091 * sind(265.1 +  719.98 * t) \
	+ 0.000030 * sind( 90.0) \
	+ 0.000013 * sind( 27.8 + 4452.67 * t) \
	+ 0.000007 * sind(254   +  450.4  * t) \
	+ 0.000007 * sind(156   +  329.6  * t)
	r = math.pow(10, r)
	return r

# 太陽位置3 (declination, degree)
def spal(t):  # t Julius
	ls = spls(t)
	ep = 23.439291 - 0.000130042 * t
	al = math.atan(tand(ls) * cosd(ep)) * 180.0 / math.pi
	if ls >= 0 and ls < 180 :
		while al < 0 :
			al += 180
		while al >= 180 :
			al -= 180
	else :
		while al < 180 :
			al += 180
		while al >= 360 :
			al -= 180
	return al

# 太陽位置4 (the right ascension, degree)
def spdl(t):  # t Julius
	ls = spls(t)
	ep = 23.439291 - 0.000130042 * t
	dl = math.asin(sind(ls) * sind(ep)) * 180.0 / math.pi
	return dl

# Calculate sidereal hour (degree)
def sh(t, h, m, s, l, tdiff):  # t julius, h hour, m minute, s second, l longitude, tdiff time difference
	d = ((s / 60.0 + m) / 60.0 + h) / 24.0  # elapsed hour (from 0:00 a.m)
	th = 100.4606 + 360.007700536 * t + 0.00000003879 * t * t - 15.0 * tdiff
	th += l + 360.0 * d
	while th >= 360 :
		th -= 360
	while th < 0 :
		th += 360
	return th

# Calculating the seeming horizon altitude "sa"(degree)
def eandp(alt, ds):  # subfunction for altitude and parallax
	e = 0.035333333 * math.sqrt(alt)
	p = 0.002442818 / ds
	return p - e

def sa(alt, ds):  # alt: altitude (m), ds: solar distance (AU)
	s = 0.266994444 / ds
	r = 0.585555555
	k = eandp(alt, ds) - s - r
	return k

# Calculating solar alititude (degree)
def soal(la, th, al, dl):  # la latitude, th sidereal hour, al solar declination, dl right ascension
	h = sind(dl) * sind(la) + cosd(dl) * cosd(la) * cosd(th - al)
	h = math.asin(h) * 180.0 / math.pi
	return h

# Calculating solar direction (degree)
def sodr(la, th, al, dl):  # la latitude, th sidereal hour, al solar declination, dl right ascension
	t = th - al
	dc = - cosd(dl) * sind(t)
	dm = sind(dl) * sind(la) - cosd(dl) * cosd(la) * cosd(t)
	if dm == 0 :
		st = sind(t)
		if st > 0 :
			dr = -90
		if st == 0 :
			dr = 9999
		if st < 0 :
			dr = 90
	else :
		dr = math.atan(dc / dm) * 180.0 / math.pi
		if dm < 0 :
			dr += 180
	if dr < 0 :
		dr += 360
	return dr

# 今日の日の出日没時刻計算(sunrize_h 日の出時, sunrize_m 日の出分, sunset_h 日没時, sunset_m 日没分,
#							meridian_h 南中時, meridiann_m 南中分)
def sunpos():
	global la, lo, alt, tdiff
	# 今日の年月日
	td = datetime.datetime.today()
	yy = td.year
	mm = td.month
	dd = td.day
	
	# 日の出、日没の計算
	t = jy(yy, mm, dd-1, 23, 59, 0, tdiff)
	th = sh(t, 23, 59, 0, lo, tdiff)
	ds = spds(t)
	ls = spls(t)
	alp = spal(t)
	dlt = spdl(t)
	pht = soal(la, th, alp, dlt)
	pdr = sodr(la, th, alp, dlt)
	
	for hh in range(0, 24):
		for m in range(0, 60):
			t = jy(yy, mm, dd, hh, m, 0, tdiff)
			th = sh(t, hh, m, 0, lo, tdiff)
			ds = spds(t)
			ls = spls(t)
			alp = spal(t)
			dlt = spdl(t)
			ht = soal(la, th, alp, dlt)
			dr = sodr(la, th, alp, dlt)
			tt = eandp(alt, ds)
			ts = sa(alt, ds)
			if pht < ts and ht > ts :
				sunrize_h = hh
				sunrize_m = m
			if pdr < 180 and dr > 180 :
				meridian_h = hh
				meridian_m = m
			if pht > ts and ht < ts :
				sunset_h = hh
				sunset_m = m
			pht = ht
			pdr = dr
	return (sunrize_h, sunrize_m, sunset_h, sunset_m, meridian_h, meridian_m, yy, mm, dd)

    # 太陽マーク
def sun_mark():
	sun_r_h, sun_r_m, sun_s_h, sun_s_m, sun_me_h, sun_me_m, yy, mm, dd = sunpos()
	print(yy, "年", mm, "月", dd, "日")
	print("日の出  ", sun_r_h, "時", sun_r_m, "分")
	print("日の入　", sun_s_h, "時", sun_s_m, "分")
	print("南　中　", sun_me_h, "時", sun_me_m, "分")
	print()
	# 夜
	sun_r = 18 - sun_r_h - sun_r_m / 60.0
	sunrize = sun_r * 15
	sun_s = 18 - sun_s_h - sun_s_m / 60.0
	sunset = sun_s * 15
	night = c0.create_arc(5, 5, win_size - 5, win_size - 5, start = sunrize, extent = 360 - sunrize + sunset, fill = 'darkgray', outline = 'darkgray')
	c0.tag_raise(night, circle) # これがないと目盛りや針が隠れてしまう
	# 南中太陽
	k = 5 # 太陽マークの半径
	n = (24 - sun_me_h - sun_me_m / 60.0) * 15
	x = 100 * math.sin(rad * n)
	y = 100 * math.cos(rad * n)
	sun = c0.create_oval(x - k, y + k, x + k, y - k, fill = 'yellow', outline = 'yellow')
	return night, sun

# 背景の描画
def draw_backboard():
	sun_r_h, sun_r_m, sun_s_h, sun_s_m, sun_me_h, sun_me_m, yy, mm, dd = sunpos()
	r = win_size / 2
	# 円
	c0.coords(circle, 5, 5, win_size - 5, win_size - 5)
	# 夜
	c0.coords(night, 5, 5, win_size - 5, win_size - 5)
	# 南中太陽
	k = 5 # 太陽マークの半径
	n = (24 - sun_me_h - sun_me_m / 60.0) * 15
	x = r + (r - 30) * math.sin(rad * n)
	y = r + (r - 30) * math.cos(rad * n)
	c0.coords(sun, x - k, y + k, x + k, y - k)
	# 目盛(30度ピッチ)
	for i in range(12):
		n = i * 30
		x1 = r + (r - 25) * math.sin(rad * n)
		y1 = r + (r - 25) * math.cos(rad * n)
		x2 = r + (r - 25) * 4 / 5 * math.sin(rad * n)
		y2 = r + (r - 25) * 4 / 5 * math.cos(rad * n)
		c0.coords(backboard[i], x1, y1, x2, y2)
	# 中間目盛り
	for i in range(12):
		n = i * 30 + 15
		x1 = r + (r - 25) * 9 / 10 * math.sin(rad * n)
		y1 = r + (r - 25) * 9 / 10 * math.cos(rad * n)
		x2 = r + (r - 25) * 4 / 5 * math.sin(rad * n)
		y2 = r + (r - 25) * 4 / 5 * math.cos(rad * n)
		c0.coords(backboard1[i], x1, y1, x2, y2)
	# 文字盤
	c0.coords(dial0, r, win_size - 8)
	c0.coords(dial6, 10, r)
	c0.coords(dial12, r, 8)
	c0.coords(dial18, win_size - 8, r)

# 針を描く
def draw_hand():
	global win_size, rad, h, h_old
	t = time.localtime()
	r = win_size / 2
	rs = r * 7 / 10
	rm = r * 6 / 10
	rh = r * 5 / 10
	# 秒(1秒で6度)
	n = t[5] * 6
	x = r + rs * math.sin(rad * n)
	y = r - rs * math.cos(rad * n)
	c0.coords(sec, r, r, x, y)
	# 分(1分で6度+1秒で0.1度)
	n = t[4] * 6 + t[5] * 0.1
	x = r + rm * math.sin(rad * n)
	y = r - rm * math.cos(rad * n)
	c0.coords(min, r, r, x, y)
	# 時 (２４時間表示で下が０時)
	h = t[3]
	h1 = h + 12
	n = h1 * 15 + t[4] * 0.25
	x = r + rh * math.sin(rad * n)
	y = r - rh * math.cos(rad * n)
	c0.coords(hour, r, r, x, y)
	
	sun = 0
	if h == 0 and h != h_old :
		sun = 1
	h_old = h
	return sun

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
	sun_flag = draw_hand()

# 表示
def show_time():
	sun_flag = draw_hand()
	if sun_flag == 1 :
		night, sun = sun_mark()
		draw_backboard()
	root.after(1000, show_time)

# グローバル変数
win_size = 200
backboard = []
backboard1 = []
rad = math.pi/180

# 太陽計算インターバルのための初期化
start_time = time.localtime()
h = start_time[3]
h_old = h - 1
if h_old < 0 :
	h_old = 23

# 24時時計
# メインウィンドウ
root = tk.Tk()
root.title(u'  和時計')
root.minsize(160, 160)
root.maxsize(400, 400)

# キャンバス
c0 = tk.Canvas(root, width = 200, height = 200, bg = 'lightblue')
c0.pack(expand = True, fill = tk.BOTH)

    # 時計下地
circle = c0.create_oval(5, 5, 195, 195, fill = 'lightgray', outline = 'lightgray')

    # 文字盤
dial0 = c0.create_text(100, 195, text = u'子', anchor = 's')
dial6 = c0.create_text(5, 100, text = u'卯', anchor = 'w')
dial12 = c0.create_text(100, 5, text = u'午', anchor = 'n')
dial18 = c0.create_text(195, 100, text = u'酉', anchor = 'e')

    # 目盛り
for i in range( 12 ):
    backboard.append(c0.create_line(i, i, 135, 135, width = 2.0))

	# 中間目盛り
for i in range( 12 ):
	backboard1.append(c0.create_line(i, i, 135, 135, width = 2.0))

    # 針
hour = c0.create_line(100, 100, 100, 60, fill = 'blue', width = 4.0)
min  = c0.create_line(100, 100, 100, 50, fill = 'green', width = 3.0)
sec  = c0.create_line(100, 100, 100, 45, fill = 'red', width = 2.0)

# バインディング
root.bind('<Configure>', change_size)

# 最初の起動

night, sun = sun_mark()
draw_backboard()
show_time()

# メインループ
root.mainloop()

# (C) 2015 SiRaKaWa
# 参考文献
# 太陽位置計算部分： www.hoshi-lab.info/env/solar.html
# 時計部分： www.geocities.jp/m_hiroi/light/pytk07.html
