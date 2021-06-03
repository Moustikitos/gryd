# -*- encoding:utf-8 -*-
# Universal Tranverse Mercator

from . import *
from math import pi, radians, degrees

ENGINE_F = tmerc_forward
ENGINE_I = tmerc_inverse


def forward(crs, lla):
    ZoneNumber = _UTMZoneNumber(
        (lla.longitude + pi) - int(
            (lla.longitude + pi) / (2 * pi)
        ) * 2 * pi - pi,
        lla.latitude
    )

    if crs.datum.ellipsoid.a == 0:
        crs.datum = "WGS 84"

    crs.lambda0 = radians((ZoneNumber-1)*6-180+3)
    crs.phi0 = 0.
    crs.y0 = 10000000.0 if lla.latitude < 0 else 0.
    crs.x0 = 500000.0
    crs.k0 = 0.9996

    xya = ENGINE_F(crs, lla)
    return Grid(
        northing=xya.y, easting=xya.x, altitude=lla.altitude,
        area="%d%c" % (ZoneNumber, _UTMLetterDesignator(lla.latitude))
    )


def inverse(crs, grid):
    if crs.datum.ellipsoid.a == 0:
        crs.datum = "WGS 84"
    crs.lambda0 = radians((int(grid.area[:-1]) - 1) * 6 - 180 + 3)
    crs.phi0 = 0.
    crs.y0 = 10000000.0 if grid.area[-1] < 'N' else 0.
    crs.x0 = 500000.0
    crs.k0 = 0.9996

    return ENGINE_I(
        crs,
        Geographic(x=grid.easting, y=grid.northing, altitude=grid.altitude)
    )


def _UTMZoneNumber(lambd_, phi):
    lambd_, phi = degrees(lambd_), degrees(phi)
    # if phi >= 56.0 and phi < 64.0 and lambd_ >= 3.0 and lambd_ < 12.0:
    if 64.0 > phi >= 56.0 and 12.0 > lambd_ >= 3.0:
        return 32
    # Special zones for Svalbard
    # if phi >= 72.0 and phi < 84.0:
    if 72.0 <= phi < 84.0:
        if   0.0 <= lambd_ < 9.0:
            return 31
        elif lambd_ < 21.0:
            return 33
        elif lambd_ < 33.0:
            return 35
        elif lambd_ < 42.0:
            return 37
    return int((lambd_ + 180) / 6) + 1


def _UTMLetterDesignator(lat):
    """
    This routine determines the correct UTM letter designator for the given
    latitude returns 'Z' if latitude is outside the UTM limits of 84N to 80S
    """
    lat = degrees(lat)
    if lat >= 84:
        return 'Z'
    elif lat >= 72:
        return 'X'
    elif lat >= 64:
        return 'W'
    elif lat >= 56:
        return 'V'
    elif lat >= 48:
        return 'U'
    elif lat >= 40:
        return 'T'
    elif lat >= 32:
        return 'S'
    elif lat >= 24:
        return 'R'
    elif lat >= 16:
        return 'Q'
    elif lat >= 8:
        return 'P'
    elif lat >= 0:
        return 'N'
    elif lat >= -8:
        return 'M'
    elif lat >= -16:
        return 'L'
    elif lat >= -24:
        return 'K'
    elif lat >= -32:
        return 'J'
    elif lat >= -40:
        return 'H'
    elif lat >= -48:
        return 'G'
    elif lat >= -56:
        return 'F'
    elif lat >= -64:
        return 'E'
    elif lat >= -72:
        return 'D'
    elif lat >= -80:
        return 'C'
    else:
        return 'Z'  # if the Latitude is outside the UTM limits
