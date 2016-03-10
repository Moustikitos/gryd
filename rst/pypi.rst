``Gryd`` package provides functions for :

+ great circle computation
+ projection and grid coordinates
+ advanced geodesy

Changes
=======

1.1.1

+ ``Geodesic`` class can now dump thumbanil location from google staticmap API
+ bugfix in unit usage for classic projection (other than grid)

1.1.0

+ projection core changes (simpler & faster)
+ added ``miller`` and ``eqc`` projection
+ 64 bit support for Windows
+ encrypt/decrypt geodesic coordinates

>>> point = Gryd.Geodesic(-6.23, 53.63)
>>> point.encrypt("your encryption key")
'mwszncbe9g2tu29'
>>> Gryd.decrypt('mwszncbe9g2tu29', key="hacking...") # gives coordinates but not the good ones
Geodesic point lon=+025°22'0.011'' lat=-086°36'35.290'' alt=0.000
>>> Gryd.decrypt('mwszncbe9g2tu29', key="your encryption key")
Geodesic point lon=-006°13'48.000'' lat=+053°37'48.000'' alt=0.000
>>> point
Geodesic point lon=-006°13'48.000'' lat=+053°37'48.000'' alt=0.000

1.0.11

+ bugfix for ``mgrs.inverse`` function
+ ``utm`` and ``mgrs`` grid tweaks

1.0.10

+ ``Gryd.Geodesic`` exports itself in ``geohash``, ``maidenhead``, ``georef`` and ``gars``
+ ``Gryd.Geodesic`` created from ``geohash``, ``maidenhead``, ``georef`` and ``gars``

1.0.9

+ ``bng`` and ``ing`` grid tweaks

1.0.8

+ bugfix for ``utm`` and ``mgrs`` grid computation
+ ``Crs.unit`` value is now used in computation

1.0.7

+ Provide a multiplatform wheel (32 and 64 bit for Windows and Ubuntu)
+ Python sources released

1.0.6

+ Added API doc

1.0.5

+ All ``Gryd`` objects are pickle-able

>>> import pickle
>>> data = pickle.dumps(wgs84)
>>> data
b'\x80\x03c_ctypes\n_unpickle\nq\x00cGryd\nEllipsoid\nq\x01}q\x02X\x04\x00\x00\x
00nameq\x03X\x06\x00\x00\x00WGS 84q\x04sC(v\x1b\x00\x00\x00\x00\x00\x00\x00\x00\
x00@\xa6TXA\xd0\x97\x1c\x14\xc4?XA\x9a\xaf\xda<\x1a\xf2\xb4?(\xe1\xf3\x84Zwk?q\x
05\x86q\x06\x86q\x07Rq\x08.'
>>> pickle.loads(data)
Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356

1.0.4

+ bugfix ``Gryd.Vincenty_dest`` representation
+ wheel distribution fix

1.0.3

+ linux (ubuntu) fix

1.0.2

+ ``Gryd.Geodesic`` class takes degrees arguments for longitude and latitude values
+ better objects representation
+ speed improvement
+ added ``__float__`` operator for ``Gryd.Dms`` and ``Gryd.Dmm`` objects

>>> float(Gryd.Dms(1, 5, 45, 23))
5.756388888888889
>>> "%.6f" % Gryd.Dms(-1, 5, 45, 23)
'-5.756389'

1.0.1

+ minor changes in C extensions
+ bugfix ``geoid.dms`` and ``geoid.dmm`` function

1.0.0

+ first public binary release (``win32`` and ``linux`` platform)

Vicenty application
===================

>>> from Gryd import *
>>> import math
>>> wgs84 = Ellipsoid(name="WGS 84") # WGS 84 ellipsoid
>>> wgs84
Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356
>>> london = Geodesic(-0.127005, 51.518602, 0.)
>>> dublin = Geodesic(-6.259437, 53.350765, 0.)
>>> vdist = wgs84.distance(dublin, london)
>>> vdist
Distance 464.025km initial bearing=113.6 final bearing=118.5
>>> vdist.distance, vdist.initial_bearing, vdist.final_bearing
(464025.2235062019, 1.9826304238310775, 2.0675106301597674)
>>> vdest = wgs84.destination(london, math.degrees(vdist.final_bearing)+180, vdist.distance)
>>> vdest
Destination lon=-006°15'33.973'' lat=+053°21'2.754'' end bearing=-66.4
>>> dublin
Geodesic point lon=-006°15'33.973'' lat=+053°21'2.754'' alt=0.000
>>> vdest.longitude, vdest.latitude, vdest.destination_bearing
(-0.10924778507143726, 0.9311465077339985, -1.1589622298392817)
>>> for p in wgs84.npoints(dublin, londre, 4): print(p)
...
Destination lon=-006°15'33.973'' lat=+053°21'02.754'' end bearing=113.6
Destination lon=-004°59'32.422'' lat=+053°00'36.687'' end bearing=114.6
Destination lon=-003°44'43.501'' lat=+052°39'22.715'' end bearing=115.6
Destination lon=-002°31'07.792'' lat=+052°17'22.201'' end bearing=116.6
Destination lon=-001°18'45.650'' lat=+051°54'36.502'' end bearing=117.5
Destination lon=-000°07'37.218'' lat=+051°31'06.967'' end bearing=118.5

EPSG dataset
============

All epsg dataset linked to Mercator, Transverse Mercator and Lambert
Conformal Conic projections are available through python API using epsg
id or name.

>>> unit = Gryd.Unit(epsg=9002)
>>> unit
Unit epsg=9002 ratio=3.2808693302666354
>>> wgs84 = Gryd.Ellipsoid(epsg=7030)
>>> wgs84
Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356
>>> Datum(epsg=4326)
Datum epsg=4326:
- <Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
- <Prime meridian epsg=8901 longitude=0.000000>
- to wgs84 0.0,0.0,0.0,0.0,0.0,0.0,0.0
>>> osgb36 = Crs(epsg=27700)
>>> osgb36
Crs epsg=27700:
- <Datum epsg=4277:
- <Ellispoid epsg=7001 a=6377563.396000 1/f=299.32496460>
- <Prime meridian epsg=8901 longitude=0.000000>
- to wgs84 446.45,-125.16,542.06,-20.49,0.15,0.25,0.84>
- <Unit epsg=9001 ratio=1.0>
- <Projection 'tmerc'>

Grids
=====

The four main grids are available : Universal Transverse Mercator,
Military Grid Reference System, British National Grid and Irish
National Grid.

>>> utm = Crs(projection="utm")
>>> utm(dublin)
Grid point area=29U E=682406.211 N=5914792.531, alt=0.000
>>> mgrs = Crs(projection="mgrs")
>>> mgrs(dublin)
Grid point area=29U PV E=82406.211 N=14792.531, alt=0.000
>>> bng = Crs(projection="bng")
>>> bng(dublin)
Grid point area=SG E=16572.029 N=92252.917, alt=0.000
>>> ing = Crs(projection="ing")
>>> ing(dublin)
Grid point area=O E=15890.887 N=34804.964, alt=0.000


Advanced geodesy functions
==========================

>>> dublin = Gryd.Geodesic(-6.272877, 53.344606, 0.)
>>> dublin.Geohash(), dublin.Geohash(digit=15)
('gc7x3r04z7', 'gc7x3r04z77csws')
>>> dublin.Maindenhead(), dublin.Maindenhead(level=6)
('IO63ui72gq', 'IO63ui72gq19dh')
>>> dublin.Georef(), dublin.Georef(digit=6)
('MKJJ43322037', 'MKJJ433203')
>>> dublin.Gars()
'348MY16'
>>> Gryd.from_geohash('gc7x3r04z77csws')
Geodesic point lon=-006°16'22.357'' lat=+053°20'40.582'' alt=0.000
>>> Gryd.from_maidenhead('IO63ui72gq')
Geodesic point lon=-006°16'21.938'' lat=+053°20'40.563'' alt=0.000
>>> Gryd.from_maidenhead('IO63ui72gq19dh')
Geodesic point lon=-006°16'22.357'' lat=+053°20'40.583'' alt=0.000
>>> Gryd.from_georef('MKJJ43322037')
Geodesic point lon=-006°16'21.900'' lat=+053°20'41.100'' alt=0.000
>>> Gryd.from_georef('MKJJ433203')
Geodesic point lon=-006°16'15.000'' lat=+053°20'45.000'' alt=0.000
>>> Gryd.from_gars('348MY16') # center of 5minx5min tile
Geodesic point lon=-006°17'30.000'' lat=+053°22'30.000'' alt=0.000
>>> Gryd.from_gars('348MY16', anchor="sw") # south west of 5minx5min tile
Geodesic point lon=-006°20'00.000'' lat=+053°20'00.000'' alt=0.000

Image-map interpolation
=======================

``Gryd.Crs`` class also provides functions for map coordinates
interpolation using calibration points. Two points minimum are
required.

>>> pvs = Crs(epsg=3785) # Popular Visualisation Crs
>>> pvs.add_map_point(0,0, Geodesic(-179.999, 85))
>>> pvs.add_map_point(512,512, Geodesic(179.999, -85))
>>> g = pvs.map2crs(256+128, 256+128)
>>> g
Geodesic point lon=+089°59'58.20'' lat=-066°23'43.74'' alt=0.000
>>> pvs.crs2map(g)
Reference point px=384 py=384
- <Geodesic point lon=+089°59'58.20'' lat=-066°23'43.74'' alt=0.000>
- <Geographic point X=10018698.512 Y=-9985934.440s alt=0.000>
>>> g = pvs.map2crs(256-128, 256+128, geographic=True)
>>> g
Geographic point X=-10018698.512 Y=-9985934.440s alt=0.000
>>> pvs.crs2map(g)
Reference point px=128 py=384
- <Geodesic point lon=-089°59'58.20'' lat=-066°23'43.74'' alt=0.000>
- <Geographic point X=-10018698.512 Y=-9985934.440s alt=0.000>

All ``Gryd`` objects are `ctypes Structure`_ and can be directly used in C code.

>>> [f[0] for f in london._fields_]
['longitude', 'latitude', 'altitude']
>>> london.longitude
-0.002216655416495398
>>> [f[0] for f in wgs84._fields_]
['epsg', 'a', 'b', 'e', 'f']
>>> [f[0] for f in osgb36._fields_]
['datum', 'unit', 'epsg', 'lambda0', 'phi0', 'phi1', 'phi2', 'k0', 'x0', 'y0', 'azimut']

API Doc
=======

+ `From Python 3.5 Module doc`_

Todo
====

+ implement oblique mercator
+ implement epsg database maintainer

.. _ctypes Structure: https://docs.python.org/3/library/ctypes.html#structures-and-unions
.. _From Python 3.5 Module doc: http://bruno.thoorens.free.fr/gryd/doc/index.html

Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/gratipay.png
   :target: https://gratipay.com/gryd

---

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png

3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D

.. image:: http://bruno.thoorens.free.fr/img/wallet.png
