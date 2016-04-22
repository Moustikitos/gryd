# -*- encoding:utf-8 -*-
# Copyright© 2015-2016, THOORENS Bruno
# All rights reserved.
import os, sys, math, json, ctypes, sqlite3
import functools
reduce = functools.reduce

# Popular Visualisation Spheroid radius (epsg #7059 ellipsoid)
EARTH_RADIUS = 6378137.0
# precision according to geohash serial number (for serial only)
SERIAL_GRIDSIZE = dict([n, math.radians(90./pow(2,(n-1)/2))*EARTH_RADIUS] for n in range(1, 56, 2))
# precision according to geohash digit number
GRIDSIZE = dict([k//5, SERIAL_GRIDSIZE[k]] for k in sorted(SERIAL_GRIDSIZE.keys()) if k%5 == 0)

_next = lambda serial: bin(int(serial, base=2) + 1)[2:].zfill(len(serial))[-len(serial):]
_prev = lambda serial: bin(int(serial, base=2) - 1)[2:].zfill(len(serial))[-len(serial):]
serialize   = lambda geohash,base="0123456789bcdefghjkmnpqrstuvwxyz":"".join((bin(base.index(c))[2:].zfill(5) for c in geohash))
unserialize = lambda serial,base="0123456789bcdefghjkmnpqrstuvwxyz": "".join((base[int(serial[i:i+5], base=2)] for i in range(0, len(serial), 5)))
neighbors = lambda geohash: (unserialize(serial) for serial in _neighbors(serialize(geohash)))

def _mix(serial1, serial2):
    serial = ""
    for i in range(len(serial1)):
        try: serial += serial1[i] + serial2[i]
        except IndexError: serial += serial1[-1]
    return serial

def _neighbors(serial):
    lon_h, lat_h = serial[0::2], serial[1::2]
    for h1 in [_prev(lon_h), lon_h, _next(lon_h)]:
        for h2 in [_prev(lat_h), lat_h, _next(lat_h)]:
            yield _mix(h1, h2)

def to_geohash(longitude, latitude, digit=10, base="0123456789bcdefghjkmnpqrstuvwxyz"):
    min_lon, max_lon = -180., 180.
    min_lat, max_lat = -90., 90.
    mid_lon, mid_lat = 0., 0.

    geohash = ""
    even = False
    while len(geohash) < digit:
        val = 0
        for mask in [0b10000,0b01000,0b00100,0b00010,0b00001]:
            if not even:
                if longitude >= mid_lon:
                    min_lon = mid_lon
                    val = mask if val == 0 else val|mask
                else:
                    max_lon = mid_lon
                mid_lon = (min_lon+max_lon)/2
            else:
                if latitude >= mid_lat:
                    min_lat = mid_lat
                    val = mask if val == 0 else val|mask
                else:
                    max_lat = mid_lat
                mid_lat = (min_lat+max_lat)/2
            even = not even
        geohash += base[val]
    return geohash

def from_geohash(geohash, base="0123456789bcdefghjkmnpqrstuvwxyz", center=True):
    """return Geodesic object from geohash"""
    eps_lon, eps_lat = 360./2., 180./2.
    min_lon, max_lon = -180., 180.
    min_lat, max_lat = -90., 90.
    mid_lon, mid_lat = 0., 0.

    even = False
    for digit in geohash:
        val = base.index(digit)
        for mask in [0b10000,0b01000,0b00100,0b00010,0b00001]:
            if not even:
                if mask & val == mask: min_lon = mid_lon
                else: max_lon = mid_lon
                mid_lon = (min_lon+max_lon)/2.
                eps_lon /= 2.
            else:
                if mask & val == mask: min_lat = mid_lat
                else: max_lat = mid_lat
                mid_lat = (min_lat+max_lat)/2.
                eps_lat /= 2.
            even = not even

    if center: return mid_lon + eps_lon/2, mid_lat + eps_lat/2
    else: return mid_lon, mid_lat, eps_lon, eps_lat

def define_search_area(lon, lat, radius=100000.):
    for n in SERIAL_GRIDSIZE:
        if SERIAL_GRIDSIZE[n]/2. < radius:
            radius = SERIAL_GRIDSIZE[n]/2.
            break

    delta = math.degrees(radius/EARTH_RADIUS)

    # © THOORENS Bruno : "geohash serial star search"
    # r = 1.49*delta*math.sqrt(2)
    # sin45 = cos(45) = math.sqrt(2)/2
    # r*cos(45) = r*sin(45) = 1.49*delta*2/2
    n += 6           # +6 : scale effect
    k = 1.49*delta/3 # /3 : scale effect
    area = set([])
    area.update(_neighbors(serialize(to_geohash(lon+k, lat+k))[:n]))
    area.update(_neighbors(serialize(to_geohash(lon+k, lat-k))[:n]))
    area.update(_neighbors(serialize(to_geohash(lon-k, lat-k))[:n]))
    area.update(_neighbors(serialize(to_geohash(lon-k, lat+k))[:n]))

    return area

def as_uint(geohash):
    return int(serialize(geohash), base=2)

# class Geohash(ctypes.Structure):
#     _fields_ = [
#         ("hash",  ctypes.c_ulonglong),
#         ("longitude", ctypes.c_double),
#         ("latitude",  ctypes.c_double),
#     ]
#     def __str__(self): return self.serial()
#     __repr__ = __str__

#     def serial(self): return bin(self.hash)[2:]
#     def next(self): return self.hash+1
#     def prev(self): return self.hash-1
#     def neighbors(self): return (Geohash(int(elem, base=2)) for elem in _neighbors(bin(self.hash)[2:]))


class CachePoint():
    ext = ".chp"

    def __init__(self, path, **kwargs):
        if not path.endswith(CachePoint.ext): path += CachePoint.ext
        self.path = os.path.abspath(path)
        self.connexion = sqlite3.connect(self.path)
        self.save = self.connexion.commit
        self.connexion.row_factory = sqlite3.Row
        self.cursor = self.connexion.cursor()
        self.cursor.executescript("""
CREATE TABLE IF NOT EXISTS points(geohash TEXT, serial TEXT, category TEXT, data TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS points_index ON points(geohash, serial, category);
CREATE TABLE IF NOT EXISTS density(serial TEXT, category TEXT, value INTEGER);
CREATE UNIQUE INDEX IF NOT EXISTS density_index ON density(serial, category);
""")

    def __repr__(self):
        return self.path

    def __del__(self):
        try: self.close()
        except: pass

    def __call__(self, *args, **kw):
        return self.cursor.execute(*args, **kw).fetchall()

    def _add_many_sequencer(self, sequence):
        for item in sequence:
            lon, lat, cat, data = item
            geoh = to_geohash(lon, lat, digit=10)
            serial = serialize(geoh)
            yield (geoh, serial, cat, json.dumps(data))

    def _guess_density(self, longitude, latitude, category=False):
        guess_area = [s[:13] for s in define_search_area(longitude, latitude, radius=SERIAL_GRIDSIZE[13])]
        return sum([rec[0] for rec in self("SELECT value FROM density WHERE serial IN ('%s');" % "','".join(guess_area))])

    def add_many(self, sequence):
        seq1 = list(self._add_many_sequencer(sequence))
        seq2 = [(e[1][:13],e[2]) for e in seq1]
        self.cursor.executemany("INSERT OR REPLACE INTO points(geohash, serial, category, data) VALUES(?,?,?,?);", seq1)
        self.cursor.executemany("INSERT OR IGNORE INTO density(serial, category, value) VALUES(?,?,0);", seq2)
        self.cursor.executemany("UPDATE density SET value = value +1 WHERE serial=? AND category=?;", seq2)

    def add(self, longitude, latitude, category, data):
        geoh = to_geohash(longitude, latitude, digit=10)
        serial = serialize(geoh)
        self("INSERT OR REPLACE INTO points(geohash, serial, category, data) VALUES(?,?,?,?);", (geoh, serial, category, json.dumps(data)))
        self("INSERT OR IGNORE INTO density(serial, category, value) VALUES(?,?,0);", (serial[:13], category))
        self("UPDATE density SET value = value +1 WHERE serial=? AND category=?;", (serial[:13], category))

    def close(self):
        for category in [rec[0] for rec in self("SELECT DISTINCT category FROM points;")]:
            self("""
CREATE VIEW IF NOT EXISTS %(cat)s AS SELECT
points.geohash AS geohash,
points.serial  AS serial,
points.data    AS data FROM points WHERE category='%(cat)s';
""" % {"cat":category,})
        self.connexion.commit()
        self.connexion.close()

    def distance(self, ll1, ll2):
        (lon1, lat1), (lon2, lat2) = ll1, ll2
        dLat, dLon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(dLat/2.) * math.sin(dLat/2.) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2.) * math.sin(dLon/2.)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return 6371. * c

    def get_nearby(self, longitude, latitude, category=False):
        cmd, found, n = "SELECT geohash, data FROM points WHERE serial LIKE ?" if not category else ("SELECT geohash, data FROM "+category+" WHERE serial LIKE ?"), False, 21
        if self._guess_density(longitude, latitude, category) == 0:
            n = 11
        while not found and n > 0:
            nearby = reduce(list.__add__, [self.cursor.execute(cmd, (s+r"%",)).fetchall() for s in define_search_area(longitude, latitude, radius=SERIAL_GRIDSIZE[n])])
            if len(nearby): found = True
            else: n -= 2
        return [(from_geohash(rec[0])[:2], rec[1]) for rec in nearby]

    def get_closest(self, longitude, latitude, category=False):
        nearby = self.get_nearby(longitude, latitude, category)
        if len(nearby):
            return sorted([[n[0], n[1], self.distance((longitude, latitude), n[0])] for n in nearby], key = lambda e:e[-1])[0]
