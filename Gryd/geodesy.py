# -*- encoding:utf-8 -*-
# Copyright© 2015-2016, THOORENS Bruno
# All rights reserved.
import math, ctypes
from . import geohash as geoH
try: import urllib.request as urllib
except ImportError: import urllib

_TORAD = math.pi/180.0
_TODEG = 180.0/math.pi

class Geodesic(ctypes.Structure):
	"""ctypes structure for geodesic coordinates. Attributes :
 * longitude
 * latitude
 * altitude

>>> dublin = Gryd.Geodesic(-6.272877, 53.344606, 0.)
>>> dublin
Geodesic point lon=-006°16'22.357'' lat=+053°20'40.582'' alt=0.000
>>> Gryd.Geodesic(45.5, 5.5, 105)
Geodesic point lon=+045°30´0.00´´ lat=+005°30´0.00´´ alt=105.000"""
	_fields_ = [
		("longitude", ctypes.c_double),
		("latitude",  ctypes.c_double),
		("altitude",  ctypes.c_double)
	]

	def __init__(self, *args, **kwargs):
		"Angular value must be given in degree here (more human values)."
		args = list(args)
		for i in range(min(2, len(args))): args[i] *= _TORAD
		for key in [k for k in kwargs if k in ["longitude", "latitude"]]: kwargs[key] *= _TORAD
		ctypes.Structure.__init__(self, *args, **kwargs)
	
	def __repr__(self):
		return "Geodesic point lon=%.6f lat=%.6f alt=%.3f" % (self.longitude*_TODEG, self.latitude*_TODEG, self.altitude)

	def Geohash(self, digit=10, base="0123456789bcdefghjkmnpqrstuvwxyz"):
		"""Convert coordinates to geohash.
>>> dublin.Geohash() # by default on 10 digit for metric precision
gc7x3r04z7
>>> dublin.Geohash(14) # why not on 14 digit for milimetric precision
gc7x3r04z77csw
"""
		longitude = self.longitude*_TODEG
		latitude = self.latitude*_TODEG
		return geoH.to_geohash(longitude, latitude, digit, base)
		# min_lon, max_lon = -180., 180.
		# min_lat, max_lat = -90., 90.
		# mid_lon, mid_lat = 0., 0.

		# geohash = ""
		# even = False
		# while len(geohash) < digit:
		# 	val = 0
		# 	for mask in [0b10000,0b01000,0b00100,0b00010,0b00001]:
		# 		if not even:
		# 			if longitude >= mid_lon:
		# 				min_lon = mid_lon
		# 				val = mask if val == 0 else val|mask
		# 			else:
		# 				max_lon = mid_lon
		# 			mid_lon = (min_lon+max_lon)/2
		# 		else:
		# 			if latitude >= mid_lat:
		# 				min_lat = mid_lat
		# 				val = mask if val == 0 else val|mask
		# 			else:
		# 				max_lat = mid_lat
		# 			mid_lat = (min_lat+max_lat)/2
		# 		even = not even
		# 	geohash += base[val]
		# return geohash

	def Maidenhead(self, level=4):
		"""Convert coordinates to maidenhead.
>>> dublin.Maidenhead()
'IO63ui72gq'
>>> dublin.Maidenhead(level=6)
'IO63ui72gq19dh'
"""
		base = "ABCDEFGHIJKLMNOPQRSTUVWX"
		longitude = (self.longitude*_TODEG+180) % 360
		latitude = (self.latitude*_TODEG+90) % 180

		result = ""

		lon_idx = longitude / 20
		lat_idx = latitude / 10
		result += base[int(math.floor(lon_idx))] + base[int(math.floor(lat_idx))]

		coef = 10.
		for l in range(level):
			if coef == 10.:
				lon_idx = (lon_idx - math.floor(lon_idx)) * 10
				lat_idx = (lat_idx - math.floor(lat_idx)) * 10
				result += "%d%d" % (math.floor(lon_idx), math.floor(lat_idx))
				coef = 24.
			else:
				lon_idx = (lon_idx - math.floor(lon_idx)) * 24
				lat_idx = (lat_idx - math.floor(lat_idx)) * 24
				result += (base[int(math.floor(lon_idx))] + base[int(math.floor(lat_idx))]).lower()
				coef = 10.
		return result

	def encrypt(self, key=""):
		base = list("0123456789bcdefghjkmnpqrstuvwxyz")
		newbase = ""
		for c in key.lower(): newbase += "" if c not in base else base.pop(base.index(c))
		newbase += "".join(reversed(base))
		return self.Geohash(15, newbase)

	def Georef(self, digit=8):
		"""Convert coordinates to georef.
>>> dublin.Georef()
'MKJJ43322037'
>>> dublin.Georef(digit=6)
'MKJJ433203'
"""
		base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
		longitude = (self.longitude*_TODEG+180) % 360
		latitude = (self.latitude*_TODEG+90) % 180

		result = ""

		lon_idx = longitude / 15.
		lat_idx = latitude / 15.
		result += base[int(math.floor(lon_idx))] + base[int(math.floor(lat_idx))]

		lon_idx = (lon_idx - math.floor(lon_idx)) * 15.
		lat_idx = (lat_idx - math.floor(lat_idx)) * 15.
		result += base[int(math.floor(lon_idx))] + base[int(math.floor(lat_idx))]

		lon_idx = (lon_idx - math.floor(lon_idx)) * 60.
		lat_idx = (lat_idx - math.floor(lat_idx)) * 60.

		lon = "%02d" % lon_idx
		lat = "%02d" % lat_idx
		if digit == 6:
			lon_idx = 10 - (lon_idx - math.floor(lon_idx)) * 10.
			lat_idx = 10 - (lat_idx - math.floor(lat_idx)) * 10.
			lat += "%01d" % math.floor(lon_idx)
			lon += "%01d" % math.floor(lat_idx)
		elif digit == 8:
			lon_idx = 100 - (lon_idx - math.floor(lon_idx)) * 100.
			lat_idx = 100 - (lat_idx - math.floor(lat_idx)) * 100.
			lat += "%02d" % math.floor(lon_idx)
			lon += "%02d" % math.floor(lat_idx)

		return result + lon + lat

	def Gars(self):
		"""Get the associated GARS Area.
>>> dublin.Gars()
'348MY16'
"""
		base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
		longitude = (self.longitude*_TODEG+180) % 360
		latitude = (self.latitude*_TODEG+90) % 180

		lon_idx = longitude / 0.5
		lat_idx = latitude / 0.5

		quadrant = "%03d" % (lon_idx+1) + base[int(math.floor(lat_idx//24))] + base[int(math.floor(lat_idx%24))]
		
		lon_num_idx = (lon_idx - math.floor(lon_idx)) * 2.
		lat_num_idx = (lat_idx - math.floor(lat_idx)) * 2.
		j = math.floor(lon_num_idx)
		i = 1-math.floor(lat_num_idx)
		number = i*(j+1)+j+1

		lon_key_idx = (lon_num_idx - math.floor(lon_num_idx)) * 3.
		lat_key_idx = (lat_num_idx - math.floor(lat_num_idx)) * 3.
		j = math.floor(lon_key_idx)
		i = 2-math.floor(lat_key_idx)
		key = i*(j+1)+j+1

		return quadrant+str(number)+str(key)

	def dump_location(self, tilename, zoom=15, size="256x256", mcolor="0xff00ff", format="png", scale=1):
		latitude, longitude = self.latitude, self.longitude
		try:
			urllib.urlretrieve(
				"https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=%s&size=%s&markers=color:%s%%7C%s,%s&format=%s&scale=%s" % (
					latitude, longitude, zoom, size, mcolor, latitude, longitude, format, scale
				),
				os.path.splitext(tilename)[0] + "."+format
			)
		except:
			pass

def from_geohash(geohash, base="0123456789bcdefghjkmnpqrstuvwxyz"):
	"""return Geodesic object from geohash"""
	# eps_lon, eps_lat = 360./2., 180./2.
	# mid_lon, mid_lat = 0., 0.
	# min_lon, max_lon = -180., 180.
	# min_lat, max_lat = -90., 90.

	# even = False
	# for digit in geohash:
	# 	val = base.index(digit)
	# 	for mask in [0b10000,0b01000,0b00100,0b00010,0b00001]:
	# 		if not even:
	# 			if mask & val == mask: min_lon = mid_lon
	# 			else: max_lon = mid_lon
	# 			mid_lon = (min_lon+max_lon)/2.
	# 			eps_lon /= 2.
	# 		else:
	# 			if mask & val == mask: min_lat = mid_lat
	# 			else: max_lat = mid_lat
	# 			mid_lat = (min_lat+max_lat)/2.
	# 			eps_lat /= 2.
	# 		even = not even

	mid_lon, mid_lat, eps_lon, eps_lat = geoH.from_geohash(geohash, base)
	result = Geodesic(longitude=mid_lon, latitude=mid_lat)
	setattr(result, "precision", (eps_lon, eps_lat))
	return result

def from_maidenhead(maidenhead):
	"""return Geodesic object from maidenhead"""
	base = "ABCDEFGHIJKLMNOPQRSTUVWX"
	longitude = latitude = 0
	eps = 18./2.
	lon_str = list(reversed(maidenhead[0::2].upper()))
	lat_str = list(reversed(maidenhead[1::2].upper()))

	for i,j in zip(lon_str[:-1],lat_str[:-1]):
		if i in "0123456789":
			longitude = (longitude + int(i))/10.
			latitude = (latitude + int(j))/10.
			eps /= 10. 
		else:
			longitude = (longitude + base.index(i))/24.
			latitude = (latitude + base.index(j))/24.
			eps /= 24. 

	longitude = (longitude + base.index(lon_str[-1]))*20. + eps
	latitude = (latitude + base.index(lat_str[-1]))*10. + eps

	result = Geodesic(longitude=longitude-180, latitude=latitude-90)
	setattr(result, "precision", (eps, eps))
	return result

def from_georef(georef):
	"""return Geodesic object from georef"""
	base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
	eps = 1./2./60.

	if len(georef) == 12:
		longitude = (1-int(georef[10:])/100. + int(georef[4:6]))/60.
		latitude = (1-int(georef[6:8])/100. + int(georef[8:10]))/60.
		eps /= 100.
	elif len(georef) == 10:
		longitude = (1-int(georef[9])/10. + int(georef[4:6]))/60.
		latitude = (1-int(georef[6])/10. + int(georef[7:9]))/60.
		eps /= 10.
	else:
		longitude = int(georef[4:6])/60.
		latitude = int(georef[6:])/60.

	longitude = ((longitude + base.index(georef[2]))/15. + base.index(georef[0]))*15. + eps
	latitude = ((latitude + base.index(georef[3]))/15. + base.index(georef[1]))*15. + eps

	result = Geodesic(longitude=longitude-180, latitude=latitude-90)
	setattr(result, "precision", (eps, eps))
	return result

def from_gars(gars, anchor=""):
	"""return Geodesic object from gars. Optional anchor value to define where to handle 5minx5min tile"""
	base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
	longitude = 5./60. * (0 if "w" in anchor else 1 if "e" in anchor else 0.5)
	latitude = 5./60. * (0 if "s" in anchor else 1 if "n" in anchor else 0.5)

	key = gars[6]
	longitude += 5./60. * (0 if key in "147" else 1 if key in "258" else 2)
	latitude += 5./60. * (0 if key in "789" else 1 if key in "456" else 2)
	
	number = gars[5]
	longitude += 15./60. * (0 if number in "13" else 1)
	latitude += 15./60. * (0 if number in "34" else 1)

	longitude += (int(gars[:3])-1)*0.5
	latitude += (base.index(gars[3])*24 + base.index(gars[4]))*0.5

	return Geodesic(longitude=longitude-180, latitude=latitude-90)

def decrypt(encrypted, key=""):
	base = list("0123456789bcdefghjkmnpqrstuvwxyz")
	newbase = ""
	for c in key.lower(): newbase += "" if c not in base else base.pop(base.index(c))
	newbase += "".join(reversed(base))
	return from_geohash(encrypted, newbase)
