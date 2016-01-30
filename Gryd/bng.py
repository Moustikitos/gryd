# -*- encoding:utf-8 -*-
# British National Grid
"""Copyright© 2015, THOORENS Bruno
All rights reserved"""

from . import *
from math import radians, floor, degrees

ENGINE_F = tmerc_forward
ENGINE_I = tmerc_inverse
CRS = Crs(epsg=27700)

def forward(ellipsoid, lla, crs):
	return _grid(ENGINE_F(CRS.datum.ellipsoid, lla, CRS))

def inverse(ellipsoid, grid, crs):
	return ENGINE_I(CRS.datum.ellipsoid, _inv_grid(grid), CRS)

inv_grid_500 = {
	"A": (-2., 3.),  "B": (-1., 3.),  "C": (0., 3.),  "D": (1., 3.),  "E": (2., 3.),
	"F": (-2., 2.),  "G": (-1., 2.),  "H": (0., 2.),  "J": (1., 2.),  "K": (2., 2.),
	"L": (-2., 1.),  "M": (-1., 1.),  "N": (0., 1.),  "O": (1., 1.),  "P": (2., 1.),
	"Q": (-2., 0.),  "R": (-1., 0.),  "S": (0., 0.),  "T": (1., 0.),  "U": (2., 0.),
	"V": (-2., -1.), "W": (-1., -1.), "X": (0., -1.), "Y": (1., -1.), "Z": (2., -1.)
}

inv_grid_100 = {
	"A": (0., 4.), "B": (1., 4.), "C": (2., 4.), "D": (3., 4.), "E": (4., 4.),
	"F": (0., 3.), "G": (1., 3.), "H": (2., 3.), "J": (3., 3.), "K": (4., 3.),
	"L": (0., 2.), "M": (1., 2.), "N": (2., 2.), "O": (3., 2.), "P": (4., 2.),
	"Q": (0., 1.), "R": (1., 1.), "S": (2., 1.), "T": (3., 1.), "U": (4., 1.),
	"V": (0., 0.), "W": (1., 0.), "X": (2., 0.), "Y": (3., 0.), "Z": (4., 0.)
}

grid_500 = dict((v,k) for (k,v) in inv_grid_500.items())
grid_100 = dict((v,k) for (k,v) in inv_grid_100.items())

def _grid(xya):
	nb5e = floor(xya.x/500000)
	xya.x -= nb5e*500000
	nb1e = floor(xya.x/100000)
	xya.x -= nb1e*100000

	nb5n = floor(xya.y/500000)
	xya.y -= nb5n*500000
	nb1n = floor(xya.y/100000)
	xya.y -= nb1n*100000

	return Grid(area = grid_500[nb5e,nb5n]+grid_100[nb1e,nb1n], easting = xya.x, northing=xya.y, altitude=xya.altitude)

def _inv_grid(grid):
	area5, area1 = grid.area
	e1, n1 = (e*100000 for e in inv_grid_100[area1])
	e5, n5 = (e*500000 for e in inv_grid_500[area5])
	return Geographic(x=grid.easting+e5+e1, y=grid.northing+n5+n1, altitude=grid.altitude)

