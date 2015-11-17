# -*- encoding:utf-8 -*-
# Irish National Grid
# @http://en.wikipedia.org/wiki/Irish_grid_reference_system
# @http://www.gridreference.ie
"""Copyright© 2015, THOORENS Bruno
All rights reserved"""

from . import *
from math import radians, floor, degrees

ENGINE_F = tmerc_forward
ENGINE_I = tmerc_inverse
CRS = Crs(epsg=29900)

def forward(ellipsoid, lla, crs):
	return _grid(ENGINE_F(ellipsoid, lla, CRS))

def inverse(ellipsoid, grid, crs):
	return ENGINE_I(ellipsoid, _inv_grid(grid), CRS)

inv_grid_100 = {
	"A": (0., 4.), "B": (1., 4.), "C": (2., 4.), "D": (3., 4.), "E": (4., 4.),
	"F": (0., 3.), "G": (1., 3.), "H": (2., 3.), "J": (3., 3.), "K": (4., 3.),
	"L": (0., 2.), "M": (1., 2.), "N": (2., 2.), "O": (3., 2.), "P": (4., 2.),
	"Q": (0., 1.), "R": (1., 1.), "S": (2., 1.), "T": (3., 1.), "U": (4., 1.),
	"V": (0., 0.), "W": (1., 0.), "X": (2., 0.), "Y": (3., 0.), "Z": (4., 0.)
}

grid_100 = dict((v,k) for (k,v) in inv_grid_100.items())

def _grid(xya):
	nb1e = floor(xya.x/100000)
	xya.x -= nb1e*100000

	nb1n = floor(xya.y/100000)
	xya.y -= nb1n*100000

	return Grid(area = grid_100[nb1e,nb1n], easting=xya.x, northing=xya.y, altitude=xya.altitude)

def _inv_grid(grid):
	e1, n1 = (e*100000 for e in inv_grid_100[grid.area])
	return Geographic(x=e1+grid.easting, y=n1+grid.northing, altitude=grid.altitude)

