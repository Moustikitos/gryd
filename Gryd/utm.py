# -*- encoding:utf-8 -*-
# Universal Tranverse Mercator
"""Copyright© 2015, THOORENS Bruno
All rights reserved"""

from . import *
from math import pi, radians, degrees

ENGINE_F = tmerc_forward
ENGINE_I = tmerc_inverse

def forward(ellipsoid, lla, crs):
	ZoneNumber = _UTMZoneNumber((lla.longitude+pi) - int((lla.longitude+pi)/(2*pi))*2*pi - pi, lla.latitude)
	area = "%d%c" % (ZoneNumber, _UTMLetterDesignator(lla.latitude))
	xya = ENGINE_F(
		ellipsoid, lla,
		Crs(x0=500000.0, y0=10000000.0 if lla.latitude < 0 else 0., k0=0.9996, lambda0=(ZoneNumber-1)*6-180+3, phi0=0.)
	)
	return Grid(
		northing = xya.y,
		easting = xya.x,
		altitude = lla.altitude,
		area = area
	)

def inverse(ellipsoid, grid, crs):
	return ENGINE_I(
		ellipsoid, Geographic(x=grid.easting, y=grid.northing, altitude=grid.altitude), 
		Crs(x0=500000.0, y0=10000000.0 if grid.area[-1] < 'N' else 0., k0=0.9996, lambda0=(int(grid.area[:-1])-1)*6-180+3, phi0=0.)
	)

def _UTMZoneNumber(lambd_, phi):
	lambd_, phi = degrees(lambd_), degrees(phi)
	if phi >= 56.0 and phi < 64.0 and lambd_ >= 3.0 and lambd_ < 12.0:
		return 32
	# Special zones for Svalbard
	if phi >= 72.0 and phi < 84.0:
		if   lambd_ >= 0.0  and lambd_ < 9.0:  return 31
		elif lambd_ >= 9.0  and lambd_ < 21.0: return 33
		elif lambd_ >= 21.0 and lambd_ < 33.0: return 35
		elif lambd_ >= 33.0 and lambd_ < 42.0: return 37

	return int((lambd_+180)/6)+1

def _UTMLetterDesignator(lat):
	"""
	This routine determines the correct UTM letter designator for the given latitude
	returns 'Z' if latitude is outside the UTM limits of 84N to 80S
	"""
	lat = degrees(lat)
	if   84  >= lat >= 72:  return 'X'
	elif 72  >  lat >= 64:  return 'W'
	elif 64  >  lat >= 56:  return 'V'
	elif 56  >  lat >= 48:  return 'U'
	elif 48  >  lat >= 40:  return 'T'
	elif 40  >  lat >= 32:  return 'S'
	elif 32  >  lat >= 24:  return 'R'
	elif 24  >  lat >= 16:  return 'Q'
	elif 16  >  lat >= 8:   return 'P'
	elif 8   >  lat >= 0:   return 'N'
	elif 0   >  lat >= -8:  return 'M'
	elif -8  >  lat >= -16: return 'L'
	elif -16 >  lat >= -24: return 'K'
	elif -24 >  lat >= -32: return 'J'
	elif -32 >  lat >= -40: return 'H'
	elif -40 >  lat >= -48: return 'G'
	elif -48 >  lat >= -56: return 'F'
	elif -56 >  lat >= -64: return 'E'
	elif -64 >  lat >= -72: return 'D'
	elif -72 >  lat >= -80: return 'C'
	else:                   return 'Z' # if the Latitude is outside the UTM limits

