# -*- encoding:utf-8 -*-

"""
Efficient geohash computing library based on bitwise operation with python
integer.

```python
>>> from Gryd import geohash
>>> dublin = geohash.geoh(-6.272877, 53.344606, bits=50)
>>> dublin
<01111010110011111101000111011100000001001111100111>
>>> geohash.as_str(dublin)
'gc7x3r04z7'
>>> geohash.geohash(-6.272877, 53.344606, digit=10)
'gc7x3r04z7'
```

Geohash can be encoded with a custom 32-element-sized base.

```python
>>> import random
>>> base = list("0123456789bcdefghjkmnpqrstuvwxyz")
>>> random.shuffle(base)
>>> base = "".join(base)
>>> base
'tjcbwq2uev8n7r9gmdf1sy05kzxh4p63'
>>> geohash.geohash(-6.272877, 53.344606, digit=10, base=base)
'gnupb5tw3u'
```
"""

import math


#: Popular Visualisation Spheroid radius (epsg #7059 ellipsoid)
EARTH_RADIUS = 6378137.0


class GeoH(int):
    """
    Integer that keeps info about leading zero bits.
    """

    @staticmethod
    def join(a, b):
        return join(a, b)

    def __init__(self, *args, **kwargs):
        int.__init__(self)
        self._bit_length = self.bit_length()

    def __repr__(self):
        return "<%s%s>" % (
            (self._bit_length - self.bit_length()) * "0",
            bin(self)[2:]
        )

    def precision(self):
        """
        Return metter precision tuple for longitude and latitude based on
        Popular Visualisation Spheroid radius (epsg #7059 ellipsoid).
        """
        if not hasattr(self, "_precision"):
            n = self._bit_length // 2
            delta = math.radians(90. / pow(2, n-1)) * EARTH_RADIUS
            self._precision = (
                delta * (1 if self._bit_length % 2 else 2),
                delta
            )
        return self._precision


def geoh(lon, lat, bits=25):
    """
    Return a python integer representing geohashed coordinates longitude and
    latitude with a given precision.

    Arguments:
        lon (float): longitude
        lat (float): latitude
        bits (int): length of the geohash in bit
    Returns:
        `Gryd.geohash.GeoH`
    """
    min_lon, max_lon = -180., 180.
    min_lat, max_lat = -90., 90.
    mid_lon, mid_lat = 0., 0.
    odd = False
    geoh = 0
    mask = 1 << (bits - 1)

    while mask > 0:
        if not odd:
            if lon >= mid_lon:
                min_lon = mid_lon
                geoh |= mask
            else:
                max_lon = mid_lon
            mid_lon = (min_lon + max_lon) / 2
        else:
            if lat >= mid_lat:
                min_lat = mid_lat
                geoh |= mask
            else:
                max_lat = mid_lat
            mid_lat = (min_lat + max_lat) / 2
        mask >>= 1
        odd = not odd

    geoh = GeoH(geoh)
    geoh._bit_length = bits
    return geoh


def lonlat(value, centered=False):
    """
    Return longitude and latitude and precision from a geohash integer.

    Arguments:
        value (Gryd.geohash.GeoH or int): geohash value
        centered (bool): returns bottom-left corner (if `False`) or center (if
                         `True`) of geohash surface
    Returns:
        longitude, latitude and precision as (dlon, dlat) tuple
    """
    if not isinstance(value, GeoH):
        value = GeoH(value)

    eps_lon, eps_lat = 360./2., 180./2.
    min_lon, max_lon = -180., 180.
    min_lat, max_lat = -90., 90.
    odd = False
    mid_lon, mid_lat = 0., 0.
    mask = 1 << (value.bit_length() - 1)

    for i in range(value._bit_length - value.bit_length()):
        if not odd:
            max_lon = mid_lon
            mid_lon = (min_lon + max_lon) / 2.
            eps_lon /= 2.
        else:
            max_lat = mid_lat
            mid_lat = (min_lat + max_lat) / 2.
            eps_lat /= 2.
        odd = not odd

    while mask > 0:
        if not odd:
            if mask & value == mask:
                min_lon = mid_lon
            else:
                max_lon = mid_lon
            mid_lon = (min_lon + max_lon) / 2.
            eps_lon /= 2.
        else:
            if mask & value == mask:
                min_lat = mid_lat
            else:
                max_lat = mid_lat
            mid_lat = (min_lat + max_lat) / 2.
            eps_lat /= 2.
        mask >>= 1
        odd = not odd

    if centered:
        eps_lon /= 2.
        eps_lat /= 2.
        return mid_lon + eps_lon, mid_lat + eps_lat, (eps_lon, eps_lat)
    else:
        return mid_lon, mid_lat, (eps_lon, eps_lat)


def as_str(value, base="0123456789bcdefghjkmnpqrstuvwxyz"):
    if not isinstance(value, GeoH):
        value = GeoH(value)

    geoh = bytearray() if isinstance(base, bytes) else []
    value = value >> (value._bit_length % 5)
    while value > 0:
        geoh.append(base[value & 0b11111])
        value >>= 5

    geoh = reversed(geoh)
    return bytes(geoh) if isinstance(base, bytes) else "".join(geoh)


def as_int(geoh, base="0123456789bcdefghjkmnpqrstuvwxyz"):
    if not isinstance(geoh, type(base)):
        raise TypeError("base and geohash have to be from same type")

    first = base.index(geoh[0])
    value = 0 | first
    for c in geoh[1:]:
        value <<= 5
        value |= base.index(c)

    value = GeoH(value)
    value._bit_length += 5 - first.bit_length()
    return value


def split(value):
    if not isinstance(value, GeoH):
        value = GeoH(value)

    lon, lon_bit_length = 0, 0
    lat, lat_bit_length = 0, 0
    odd = False
    mask = 1 << (value._bit_length - 1)

    while mask > 0:
        if not odd:
            lon <<= 1
            lon_bit_length += 1
            lon |= 1 if mask & value else 0
        else:
            lat <<= 1
            lat_bit_length += 1
            lat |= 1 if mask & value else 0
        mask >>= 1
        odd = not odd

    lon = GeoH(lon)
    lon._bit_length = lon_bit_length
    lat = GeoH(lat)
    lat._bit_length = lat_bit_length
    return lon, lat


def join(lon, lat):
    if not isinstance(lon, GeoH):
        lon = GeoH(lon)
    if not isinstance(lat, GeoH):
        lat = GeoH(lon)

    geoh = 0
    odd = False
    lon_mask = 1 << (lon._bit_length - 1)
    lat_mask = 1 << (lat._bit_length - 1)

    while lon_mask > 0 or lat_mask > 0:
        geoh <<= 1
        if not odd:
            geoh |= 1 if lon_mask & lon else 0
            lon_mask >>= 1
        else:
            geoh |= 1 if lat_mask & lat else 0
            lat_mask >>= 1
        odd = not odd

    geoh = GeoH(geoh)
    geoh._bit_length = lon._bit_length + lat._bit_length
    return geoh


def geohash(lon, lat, digit=10, base="0123456789bcdefghjkmnpqrstuvwxyz"):
    return as_str(geoh(lon, lat, digit * 5), base)


def geodesic(geoh, base="0123456789bcdefghjkmnpqrstuvwxyz", centered=True):
    return lonlat(as_int(geoh, base), centered=centered)


#: backward compatibility
to_geohash = geohash
#: backward compatibility
from_geohash = geodesic
