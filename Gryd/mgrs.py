# -*- encoding:utf-8 -*-
# Military Grid Reference System
"""Copyright© 2015-2016, THOORENS Bruno
All rights reserved"""

from . import Grid, Geodesic, ctypes, utm, geoid
from math import radians

MD = geoid.MD # meridian distance
MD.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
MD.restype = ctypes.c_double

ENGINE_F = utm.forward
ENGINE_I = utm.inverse

def forward(crs, lla):
	grid = ENGINE_F(crs, lla)

	col = int(grid.easting//100000.0)
	row = int(grid.northing//100000.0)
	grid.easting -= (col*100000.0)
	grid.northing -= (row*100000.0)

	E_band = E_letter[int(grid.area[:-1])%3]
	N_band = (N_shifted_letter if crs.datum.ellipsoid.epsg in [7004, 7006, 7008, 7012] else N_letter)[int(grid.area[:-1])%2]

	grid.area = "%s %s" % (grid.area, E_band[col-1] + N_band[row%len(N_band)])
	return grid

def inverse(crs, grid):
	fuseau, area = grid.area.split()
	fuseau, zone = int(fuseau[:-1]), fuseau[-1]

	ellipsoid = crs.datum.ellipsoid
	k0 = crs.k0

	col = E_letter[fuseau%3].index(area[0])+1
	row = (N_shifted_letter if ellipsoid.epsg in [7004, 7006, 7008, 7012] else N_letter)[fuseau%2].index(area[-1])

	northing = k0 * MD(ellipsoid.a, ellipsoid.e, radians(float(UTM_letter[zone])))
	grid.easting += col * 100000.
	grid.northing += ((northing//2000000)*20 + row) * 100000.

	grid.area = "%s%s" % (fuseau, zone)
	return ENGINE_I(crs, grid)

 
E_letter = {
	# key = UTMZONENUMBER%3
	1.: ["A", "B", "C", "D", "E", "F", "G", "H"],
	2.: ["J", "K", "L", "M", "N", "P", "Q", "R"],
	0.: ["S", "T", "U", "V", "W", "X", "Y", "Z"]
}

N_letter = {
	# key = UTMZONENUMBER%2
	1.: ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V"],
	0.: ["F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "A", "B", "C", "D", "E"]
}

# for specific ellipsoid :
# Bessel 1841 (Ethiopia, Indonesia)
# Bessel 1841 (Namibia)
# Clarke 1866
# Clarke 1880
N_shifted_letter = {
	# key = UTMZONENUMBER%2
	1.: ["L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "A", "B", "C", "D", "E", "F", "G", "H", "J", "K"],
	0.: ["R", "S", "T", "U", "V", "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q"]
}

UTM_letter = {
	"X": 72, "W": 64,  "V": 56,  "U": 48,  "T": 40,  "S": 32,  "R": 24,  "Q": 16,  "P": 8,   "N": 0,
	"M": -8, "L": -16, "K": -24, "J": -32, "H": -40, "G": -48, "F": -56, "E": -64, "D": -72, "C": -80
}
