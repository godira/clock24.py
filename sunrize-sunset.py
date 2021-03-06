#!/use/bin/python
# coding: UTF-8
# Original program www.hoshi-lab.info/env/solar.html

# この場所のデータ
la = 34.8   # 緯度(度)。北緯は+,南緯は-
lo = 140.0  # 経度(度)。東経は+,西経は-
alt = 0.0   # 標高(m)
tdiff = 9.0   # グリニッジ標準時との時差

import math, time, datetime

# グローバル変数
rad = math.pi/180.0

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
def sh(t, h, m, s, l, tdiff):  # t julius, h hour, m minute, s second, l longitude, i time difference
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

# main
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

sunrize_h = 0
sunrize_m = 0
sunset_h = 0
sunset_m = 0
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
		if pht > ts and ht < ts :
			sunset_h = hh
			sunset_m = m
		pht = ht
		pdr = dr

print "Sunrize %d, %d" % (sunrize_h, sunrize_m)
print "Sunset  %d, %d" % (sunset_h, sunset_m)
