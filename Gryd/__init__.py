# -*- coding: utf-8 -*-

"""
# EPSG dataset

All epsg dataset linked to these projections are available through python API
using epsg id or name:

 + Mercator
 + Transverse Mercator
 + Lambert Conformal Conic.
 + Miller

# Grids

Four main grids are available:

 + Universal Transverse Mercator
 + Military Grid Reference System
 + British National Grid
 + Irish National Grid.

# Image-map interpolation

`Gryd.Crs` also provides functions for map coordinates interpolation using
calibration `Points` (two minimum are required).

# Quick view
```python
>>> import Gryd
>>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
>>> dublin
<lon=-006°15'33.973" lat=+053°21'2.754" alt=0.000>
>>> utm = Gryd.Crs(epsg=3395, projection="utm")
>>> utm(dublin)
<area=29U E=682406.211 N=5914792.531, alt=0.000>
>>> mgrs = Gryd.Crs(epsg=3395, projection="mgrs")
>>> mgrs(dublin)
<area=29U PV E=82406.211 N=14792.531, alt=0.000>
>>> bng = Gryd.Crs(projection="bng")
>>> bng(dublin)
<area=SG E=16572.029 N=92252.917, alt=0.000>
>>> ing = Gryd.Crs(projection="ing")
>>> ing(dublin)
<area=O E=15890.887 N=34804.964, alt=0.000>
```
"""

import os
import sys
import imp
import math
import ctypes
import sqlite3

from Gryd.geodesy import Geodesic

__author__ = "Bruno THOORENS"
# Major.minor.micro version number. The micro number is bumped for API
# changes, for new functionality, and for interim project releases. The minor
# number is bumped whenever there is a significant project release. The major
# number will be bumped when the project is feature-complete, and perhaps if
# there is a major change in the design.
__version__ = "1.2.1"
# add C projection functions here
__c_proj__ = ["tmerc", "merc", "lcc", "eqc", "miller"]
# add python projection modules here
__py_proj__ = ["utm", "mgrs", "bng", "ing"]

_TORAD = math.pi/180.0
_TODEG = 180.0/math.pi


def main_is_frozen():
    """
    Return True if it runs from a frozen script (py2exe, cx_Freeze...)
    """
    return (
        hasattr(sys, "frozen") or     # new py2exe
        hasattr(sys, "importers") or  # old py2exe
        imp.is_frozen("__main__")     # tools/freeze
    )


# find data file
def get_data_file(name):
    """
    Find data file according to package (frozen or not) installation path.
    """
    if main_is_frozen():
        return os.path.join(os.path.dirname(sys.executable), name)
    else:
        for path in __path__:
            filename = os.path.join(path, name)
            if os.path.exists(filename):
                return filename
        raise IOError("%s data file not found" % name)


# Create a table of n ctypes and return pointer
def t_byref(ctype, n, *args):
    return ctypes.cast((ctype * n)(*args), ctypes.POINTER(ctype))


#: Connection to epsg database
EPSG_CON = sqlite3.connect(get_data_file("db/epsg.sqlite"))
EPSG_CON.row_factory = sqlite3.Row


class Geocentric(ctypes.Structure):
    """
    `ctypes` structure for geocentric coordinates. This reference is generaly
    used as a transition for datum conversion.

    Attributes:
        x (float): X-axis value
        y (float): Y-axis value
        z (float): Z-axis value

    ```python
    >>> Gryd.Geocentric(4457584, 429216, 4526544)
    <X=4457584.000 Y=429216.000 Z=4526544.000>
    >>> Gryd.Geocentric(x=4457584, y=429216, z=4526544)
    <X=4457584.000 Y=429216.000 Z=4526544.000>
    ```
    """
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double)
    ]

    def __repr__(self):
        return "<X=%.3f Y=%.3f Z=%.3f>" % (
            self.x, self.y, self.z
        )


class Geographic(ctypes.Structure):
    """
    `ctypes` structure for geographic coordinates. 2D coordinates on flattened
    earth (using a projection system) with elevation as third dimension.

    Attributes:
        x (float): X-projection-axis value
        y (float): Y-projection-axis value
        altitude (float): elevation in meters

    ```python
    >>> Gryd.Geographic(5721186, 2948518, 105)
    <X=5721186.000 Y=2948518.000 alt=105.000>
    >>> Gryd.Geographic(x=5721186, y=2948518, altitude=105)
    <X=5721186.000 Y=2948518.000 alt=105.000>
    ```
    """
    _fields_ = [
        ("x",        ctypes.c_double),
        ("y",        ctypes.c_double),
        ("altitude", ctypes.c_double)
    ]

    def __repr__(self):
        return "<X=%.3f Y=%.3fs alt=%.3f>" % (self.x, self.y, self.altitude)


class Grid(ctypes.Structure):
    """
    `ctypes` structure for grided coordinates. Another coordinates system
    applied on flattened earth. It is defined by an area, 2D coordinates and
    elevation.

    Attributes:
        area (str): string region
        easting (float): X-grid-axis value
        northing (float): Y-grid-axis value
        altitude (float): elevation in meters

    ```python
    >>> Gryd.Grid(area="31T", easting=925595, northing=5052949, altitude=105)
    <area=31T E=925595.000 N=5052949.000, alt=105.000>
    ```
    """
    area = ""
    _fields_ = [
        ("easting",  ctypes.c_double),
        ("northing", ctypes.c_double),
        ("altitude", ctypes.c_double),
    ]

    def __repr__(self):
        return "<area=%s E=%.3f N=%.3f, alt=%.3f>" % (
            self.area, self.easting, self.northing, self.altitude
        )


class Point(ctypes.Structure):
    """
    `ctypes` structure for calibration point. It is used for coordinates
    interpolation on a referenced raster image. Two points minimum are
    required.

    Attributes:
        px (float): pixel column position
        py (float): pixel row position
        lla (Gryd.Geodesic): geodesic coordinates associated to the pixel
                             coordinates
        xya (Gryd.Geographic): geographic coordinates associated to the pixel
                               coordinates
    """
    _fields_ = [
        ("px",  ctypes.c_double),
        ("py",  ctypes.c_double),
        ("lla", Geodesic),
        ("xya", Geographic)
    ]

    def __repr__(self):
        return "<px=%.0f py=%.0f\n%r\n%r\n>" % (
            self.px, self.py, self.lla, self.xya
        )


class Vincenty_dist(ctypes.Structure):
    """
    Great circle distance computation result using Vincenty formulae.
    `Vincenty_dist` structures are returned by `Gryd.Ellipsoid.distance`
    function.

    Attributes:
        distance (float): great circle distance in meters
        initial_bearing (float): initial bearing in degrees
        final_bearing (float): final bearing in degrees
    """
    _fields_ = [
        ("distance",        ctypes.c_double),
        ("initial_bearing", ctypes.c_double),
        ("final_bearing",   ctypes.c_double)
    ]

    def __repr__(self):
        return "<Distance %.3fkm initial bearing=%.1f° final bearing=%.1f°>" %\
            (
                self.distance/1000,
                math.degrees(self.initial_bearing),
                math.degrees(self.final_bearing)
            )


class Vincenty_dest(ctypes.Structure):
    """
    Great circle destination computation result using Vincenty formulae.
    `Vincenty_dist` structures are returned by `Gryd.Ellipsoid.destination`
    function.

    Attributes:
        longitude (float): destinatin longitude in degrees
        latitude (float): destination latitude in degrees
        destination_bearing (float): destination bearing in degrees
    """
    _fields_ = [
        ("longitude",           ctypes.c_double),
        ("latitude",            ctypes.c_double),
        ("destination_bearing", ctypes.c_double)
    ]

    def __repr__(self):
        return "<Destination lon=%r lat=%r end bearing=%.1f°>" % (
            dms(math.degrees(self.longitude)),
            dms(math.degrees(self.latitude)),
            math.degrees(self.destination_bearing)
        )


class Dms(ctypes.Structure):
    """
    Degrees Minutes Seconde value of a float value. `Dms` structure are
    returned by `Gryd.dms` function.

    ```python
    >>> d = Gryd.dms(-60.42286847222222)
    >>> d
    -060°25'22.326"
    >>> float(d)
    -60.42286847222222
    ```
    """
    _fields_ = [
        ("sign",   ctypes.c_short),
        ("degree", ctypes.c_double),
        ("minute", ctypes.c_double),
        ("second", ctypes.c_double)
    ]

    def __repr__(self):
        return "%s%03d°%02d'%00.3f\"" % (
            "+" if self.sign > 0 else "-",
            self.degree, self.minute, self.second
        )

    def __float__(self):
        return (1 if self.sign > 0 else -1) * (
            ((self.second / 60.) + self.minute) / 60. + self.degree
        )


class Dmm(ctypes.Structure):
    """
    Degrees Minutes value of a float value. `Dmm` structure are returned by
    `Gryd.dmm` function.

    ```python
    >>> d = Gryd.dmm(-60.42286847222222)
    >>> d
    -060°25.372108'
    >>> float(d)
    -60.42286847222222
    ```
    """
    _fields_ = [
        ("sign",   ctypes.c_short),
        ("degree", ctypes.c_double),
        ("minute", ctypes.c_double)
    ]

    def __repr__(self):
        return "%s%03d°%00.6f'" % (
            "+" if self.sign > 0 else "-",
            self.degree, self.minute
        )

    def __float__(self):
        return (1 if self.sign > 0 else -1) * (
            self.minute / 60. + self.degree
        )


class Epsg(ctypes.Structure):
    """
    `ctypes` structure with a sqlite connection to EPSG database for
    initialization purpose.
    """
    #: Shared sqlite database to be linked with
    sqlite = EPSG_CON.cursor()
    #: The table database name where `__init__` will find data
    table = ""

    def __init__(self, *args, **pairs):
        """
        If list of values is given as `*args`, structure members are
        initialized in the order of the field definition. If `*args` only
        contains one value:

         + it is a `dict` then it is used as a reccord
         + it is an `int` then try to get a record from database using epsg id
         + it is a `str` then try to get a record from database using epsg name

        All values in `**pairs` are merged in the record before attributes
        initialization.
        """
        record = {}
        # in case a dict is given at initialization
        if len(args) == 1:
            if isinstance(args[0], dict):
                record = args[0]
            elif isinstance(args[0], int):
                pairs["epsg"] = args[0]
            elif isinstance(args[0], (bytes, str)):
                pairs["name"] = args[0]
            args = ()
        # try to find data in database using epsg or name
        try:
            if "epsg" in pairs:
                record = Epsg.sqlite.execute(
                    "SELECT * from %s WHERE epsg=?" % self.table,
                    (pairs.pop("epsg"),)
                ).fetchall()[0]
            elif "name" in pairs:
                record = Epsg.sqlite.execute(
                    "SELECT * from %s WHERE name=?" % self.table,
                    (pairs.pop("name"),)
                ).fetchall()[0]
        except IndexError:
            pass

        # merge database record with eventually given pairs
        pairs = dict(record, **pairs)
        # initialize in the order of _fields_ attribute
        ctypes.Structure.__init__(self, *args)
        for key, value in sorted(pairs.items(), key=lambda e: e[0]):
            if key == "lambda":
                key, value = "longitude", math.radians(value)
            elif key in ["lambda0", "phi0", "phi1", "phi2", "azimut"]:
                value = math.radians(value)
            elif key in ["rf", "1/f", "invf"]:
                key, value = ("f", 1./value) if value != 0. else ("f", 0.)
            setattr(self, key, value)


class Unit(Epsg):
    """
    Unit ratio relative to meter.

    ```python
    >>> Gryd.Unit(9001)
    <Unit epsg=9001 ratio=1.0>
    >>> Gryd.Unit(epsg=9001).name
    'metre'
    >>> Gryd.Unit(name="foot")
    <Unit epsg=9002 ratio=3.2808693302666354>
    >>> float(Gryd.Unit(name="foot"))
    3.2808693302666354
    ```
    """
    table = "unit"
    _fields_ = [
        ("epsg",  ctypes.c_int),
        ("ratio", ctypes.c_double)
    ]

    def __repr__(self):
        return "<Unit epsg=%d ratio=%r>" % (self.epsg, self.ratio)

    def __float__(self):
        return self.ratio


class Prime(Epsg):
    """
    Prime meridian.

    ```python
    >>> prime = Gryd.Prime(epsg=8902)
    >>> prime
    <Prime meridian epsg=8902 longitude=-009°07'54.862">
    >>> prime.name
    'Lisbon'
    ```
    """
    table = "prime"
    _fields_ = [
        ("epsg",      ctypes.c_int),
        ("longitude", ctypes.c_double)
    ]

    def __repr__(self):
        return "<Prime meridian epsg=%d longitude=%r>" % (
            self.epsg, dms(math.degrees(self.longitude))
        )


class Ellipsoid(Epsg):
    """
    ```python
    >>> wgs84 = Gryd.Ellipsoid("WGS 84")
    >>> wgs84
    <Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
    ```
    """
    table = "ellipsoid"
    _fields_ = [
        ("epsg", ctypes.c_int),
        ("a",    ctypes.c_double),
        ("b",    ctypes.c_double),
        ("e",    ctypes.c_double),
        ("f",    ctypes.c_double)
    ]

    def __repr__(self):
        return "<Ellispoid epsg=%d a=%.6f 1/f=%.8f>" % (
            self.epsg, self.a, (1 / self.f if self.f != 0. else 0.)
        )

    def __setattr__(self, attr, value):
        Epsg.__setattr__(self, attr, value)
        if attr == "b":
            Epsg.__setattr__(self, "f", (self.a-value) / self.a)
            Epsg.__setattr__(self, "e", math.sqrt(2 * self.f - self.f**2))
        elif attr == "e":
            Epsg.__setattr__(
                self, "b", math.sqrt(self.a**2 * (1 - value**2))
            )
            Epsg.__setattr__(self, "f", (self.a - self.b) / self.a)
        elif attr == "f":
            Epsg.__setattr__(self, "e", math.sqrt(2 * value - value**2))
            Epsg.__setattr__(
                self, "b", math.sqrt(self.a**2 * (1 - self.e**2))
            )

    def distance(self, lla0, lla1):
        """
        ```
        >>> london = Gryd.Geodesic(-0.127005, 51.518602, 0.)
        >>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
        >>> wgs84.distance(dublin, london)
        <Distance 464.025km initial bearing=113.6 final bearing=118.5>
        ```
        """
        return distance(self, lla0, lla1)

    def destination(self, lla, bearing, distance):
        """
        ```python
        >>> wgs84.destination(
        ...     london, math.degrees(vdist.final_bearing) + 180, vdist.distance
        ... )
        <Destination lon=-006°15'33.973" lat=+053°21'2.754" end bearing=-66.4°>
        >>> dublin
        <lon=-006°15'33.973" lat=+053°21'2.754" alt=0.000>
        ```
        """
        return destination(
            self, lla, Vincenty_dist(distance, math.radians(bearing))
        )

    def npoints(self, lla0, lla1, n):
        """
        ```python
        >>> for p in wgs84.npoints(dublin, londre, 4): print(p)
        ...
        <Destination lon=-006°15'33.973" lat=+053°21'2.754" end bearing=113.6>
        <Destination lon=-004°59'32.422" lat=+053°00'36.687" end bearing=114.6>
        <Destination lon=-003°44'43.501" lat=+052°39'22.715" end bearing=115.6>
        <Destination lon=-002°31'7.792" lat=+052°17'22.201" end bearing=116.6>
        <Destination lon=-001°18'45.650" lat=+051°54'36.502" end bearing=117.5>
        <Destination lon=-000°07'37.218" lat=+051°31'6.967" end bearing=118.5>
        ```
        """
        result = ()
        pts = npoints(self, lla0, lla1, n)
        for i in range(n + 2):
            result += (pts[i], )
        return result


class Datum(Epsg):
    """

    ```python
    >>> Gryd.Datum(epsg=4326)
    <Datum epsg=4326:
    <Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
    <Prime meridian epsg=8901 longitude=0.000000>
    to wgs84: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0>
    ```
    """
    table = "datum"
    _fields_ = [
        ("ellipsoid", Ellipsoid),
        ("prime",     Prime),
        ("epsg",      ctypes.c_int),
        ("ds",        ctypes.c_double),
        ("dx",        ctypes.c_double),
        ("dy",        ctypes.c_double),
        ("dz",        ctypes.c_double),
        ("rx",        ctypes.c_double),
        ("ry",        ctypes.c_double),
        ("rz",        ctypes.c_double)
    ]

    def __repr__(self):
        return "<Datum epsg=%d:\n%r\n%r\nto wgs84: %s>" % (
            self.epsg,
            self.ellipsoid,
            self.prime,
            ", ".join(str(getattr(self, attr)) for attr in [
                "dx", "dy", "dz", "ds", "rx", "ry", "rz"
            ])
        )

    def __setattr__(self, attr, value):
        if attr == "ellipsoid" and not isinstance(value, Ellipsoid):
            value = Ellipsoid(value)
        elif attr == "prime" and not isinstance(value, Prime):
            value = Prime(value)
        Epsg.__setattr__(self, attr, value)

    def xyz(self, lla):
        """
        ```python
        >>> wgs84.xyz(london)
        <X=3977018.848 Y=-8815.695 Z=4969650.564>
        ```
        """
        lla.longitude += self.prime.longitude
        return geocentric(self.ellipsoid, lla)

    def lla(self, xyz):
        """
        ```python
        >>> wgs84.lla(wgs84.xyz(london))
        <lon=-000°07'37.218" lat=+051°31'6.967" alt=0.000>
        >>> london
        <lon=-000°07'37.218" lat=+051°31'6.967" alt=0.000>
        ```
        """
        lla = geodesic(self.ellipsoid, xyz)
        lla.longitude -= self.prime.longitude
        return lla

    def transform(self, dst, lla):
        """
        ```python
        >>> airy = Gryd.Datum(epsg=4277)
        >>> wgs84.transform(airy, london)
        <lon=-000°07'31.431'' lat=+051°31'5.137'' alt=-46.118>
        ```
        """
        return dst.lla(dat2dat(self, dst, self.xyz(lla)))


class Crs(Epsg):
    """
    ```python
    >>> pvs = Gryd.Crs(epsg=3785)
    >>> osgb36 = Gryd.Crs(epsg=27700)
    >>> osgb36.datum.xyz(london)
    <X=3976632.017 Y=-8814.837 Z=4969286.446>
    >>> osgb36.datum.ellipsoid.distance(dublin, london)
    <Distance 463.981km initial bearing=113.6 final bearing=118.5>
    >>> osgb36
    <Crs epsg=27700:
    <Datum epsg=4277:
    <Ellispoid epsg=7001 a=6377563.396000 1/f=299.32496460>
    <Prime meridian epsg=8901 longitude=0.000000>
    to wgs84 446.45,-125.16,542.06,-20.49,0.15,0.25,0.84>
    <Unit epsg=9001 ratio=1.0>
    Projection 'tmerc'>
    ```
    """
    table = "grid"
    _fields_ = [
        ("datum",   Datum),
        ("unit",    Unit),
        ("epsg",    ctypes.c_int),
        ("lambda0", ctypes.c_double),
        ("phi0",    ctypes.c_double),
        ("phi1",    ctypes.c_double),
        ("phi2",    ctypes.c_double),
        ("k0",      ctypes.c_double),
        ("x0",      ctypes.c_double),
        ("y0",      ctypes.c_double),
        ("azimut",  ctypes.c_double)
    ]

    def __reduce__(self):
        """
        special method that allows `Gryd.Crs` instance to be pickled
        """
        if hasattr(self, "forward"):
            self.__dict__.pop("forward")
        if hasattr(self, "inverse"):
            self.__dict__.pop("inverse")
        return Epsg.__reduce__(self)

    def __repr__(self):
        return "<Crs epsg=%d:\n%r\n%r\nProjection %r>" % (
            self.epsg, self.unit, self.datum, self.projection
        )

    def __init__(self, *args, **kwargs):
        self._points = []
        self.projection = "latlong"
        Epsg.__init__(self, *args, **kwargs)
        self.unit = kwargs.pop("unit", 9001)

    def __setattr__(self, attr, value):
        if attr == "datum" and not isinstance(value, Datum):
            value = Datum(value)
        elif attr == "unit" and not isinstance(value, Unit):
            value = Unit(value)
        elif attr == "projection":
            record = Epsg.sqlite.execute(
                "SELECT * from projection WHERE epsg=%r;" % value
            ).fetchall()
            if len(record) > 0:
                value = record[0]["typeproj"]
            if value in __c_proj__:
                Epsg.__setattr__(self, "forward", getattr(
                    sys.modules[__name__], value + "_forward"
                ))
                Epsg.__setattr__(self, "inverse", getattr(
                    sys.modules[__name__], value + "_inverse"
                ))
            elif value in __py_proj__:
                module = __import__(
                    'Gryd.' + value, globals(), locals(), [value], 0
                )
                Epsg.__setattr__(self, "forward", module.forward)
                Epsg.__setattr__(self, "inverse", module.inverse)
            else:
                value = "latlong"
                Epsg.__setattr__(
                    self, "forward",
                    lambda ellps, lla, o=self:
                        Geographic(
                            lla.longitude * ellps.a,
                            lla.latitude * ellps.b,
                            lla.altitude
                        )
                )
                Epsg.__setattr__(
                    self, "inverse",
                    lambda ellps, xya, o=self:
                        Geodesic(
                            xya.x / ellps.a,
                            xya.y / ellps.b,
                            xya.altitude
                        )
                )
        Epsg.__setattr__(self, attr, value)

    def __call__(self, element):
        """
        ```python
        >>> osgb36(london)  # projection of Geodesic point
        <X=529939.106 Y=181680.962s alt=0.000>
        >>> osgb36(osgb36(london))  # deprojection of Geographic point
        <lon=-000°07'37.218" lat=+051°31'6.967" alt=0.000>
        ```
        """
        try:
            ratio = self.unit.ratio
            if isinstance(element, Geodesic):
                xya = self.forward(self, element)
                if isinstance(xya, Grid):
                    xya.easting /= ratio
                    xya.northing /= ratio
                elif isinstance(xya, Geographic):
                    xya.x /= ratio
                    xya.y /= ratio
                return xya
            elif isinstance(element, Grid):
                element.easting *= ratio
                element.northing *= ratio
                return self.inverse(self, element)
            elif isinstance(element, Geographic):
                element.x *= ratio
                element.y *= ratio
                return self.inverse(self, element)
            else:
                pass
        except AttributeError:
            setattr(self, "projection", getattr(self, "projection", None))
            return self(element)

    def transform(self, dst, xya):
        """
        ```python
        >>> osgb36.transform(pvs, osgb36(london))
        <X=-14317.072 Y=6680144.273s alt=-13015.770>
        >>> pvs.transform(osgb36, osgb36.transform(pvs, osgb36(london)))
        <X=529939.101 Y=181680.963s alt=0.012>
        >>> osgb36(london)
        <X=529939.106 Y=181680.962s alt=0.000>
        ```
        """
        return dst(self.datum.transform(dst.datum, self(xya)))

    def add_map_point(self, px, py, point):
        """
        ```python
        >>> pvs.add_map_point(0,0, Geodesic(-179.999, 85))
        >>> pvs.add_map_point(512,512, Geodesic(179.999, -85))
        ```
        """
        if px in [p.px for p in self._points]:
            return
        if py in [p.py for p in self._points]:
            return
        if isinstance(point, Geodesic):
            self._points.append(Point(px, py, point, self(point)))
        elif isinstance(point, Geographic):
            self._points.append(Point(px, py, self(point), point))

    def delete_map_point(self, px=None, py=None, index=None):
        if px == py == index is None:
            return [self._points.pop(0)]
        elif px is not None and py is not None:
            return [p for p in self._points if p.px == px and p.py == py]
        elif isinstance(index, int):
            return [self._points.pop(min(len(self._points) - 1, index))]
        return []

    def map2crs(self, px, py, geographic=False):
        """
        ```python
        >>> pvs.map2crs(256+128, 256+128)
        <lon=+089°59'58.20'' lat=-066°23'43.74'' alt=0.000>
        >>> pvs.map2crs(256-128, 256+128, geographic=True)
        <point X=-10018698.512 Y=-9985934.440s alt=0.000>
        ```
        """
        if len(self._points) >= 2:
            n = len(self._points)
            x = lagrange(
                px,
                t_byref(ctypes.c_double, n, *[p.px for p in self._points]),
                t_byref(ctypes.c_double, n, *[p.xya.x for p in self._points]),
                n
            )
            y = lagrange(
                py,
                t_byref(ctypes.c_double, n, *[p.py for p in self._points]),
                t_byref(ctypes.c_double, n, *[p.xya.y for p in self._points]),
                n
            )
            if geographic:
                return Geographic(x, y, 0)
            else:
                return self(Geographic(x, y, 0))
        else:
            raise Exception("no enough calibration points in this Crs")

    def crs2map(self, point):
        """
        ```python
        >>> pvs.crs2map(pvs.map2crs(256+128, 256+128))
        <px=384 py=384
        - <lon=+089°59'58.20'' lat=-066°23'43.74'' alt=0.000>
        - <X=10018698.512 Y=-9985934.440s alt=0.000>
        >
        ```
        """
        if isinstance(point, Geodesic):
            point = self(point)
        elif isinstance(point, Grid):
            raise Exception(
                "only works with Geographic or Geodesic points "
                "(Grid points given instead)"
            )

        if len(self._points) >= 2:
            n = len(self._points)
            return Point(
                lagrange(
                    point.x,
                    t_byref(
                        ctypes.c_double, n, *[p.xya.x for p in self._points]
                    ),
                    t_byref(ctypes.c_double, n, *[p.px for p in self._points]),
                    n
                ),
                lagrange(
                    point.y,
                    t_byref(
                        ctypes.c_double, n, *[p.xya.y for p in self._points]
                    ),
                    t_byref(ctypes.c_double, n, *[p.py for p in self._points]),
                    n
                ),
                self(point),
                point
            )
        else:
            raise Exception("no enough calibration points in this Crs")


def _Geodesic__repr(obj):
    return "<lon=%r lat=%r alt=%.3f>" % (
        dms(math.degrees(obj.longitude)),
        dms(math.degrees(obj.latitude)),
        obj.altitude
    )


setattr(Geodesic, "__repr__", _Geodesic__repr)


#######################
# loading C libraries #
#######################
# defining library name
__dll_ext__ = "dll" if sys.platform.startswith("win") else \
              "so" if sys.platform.startswith("linux") else \
              "so"
geoid = ctypes.CDLL(get_data_file("geoid.%s" % __dll_ext__))
proj = ctypes.CDLL(get_data_file("proj.%s" % __dll_ext__))

dms = geoid.dms
dms.argtypes = [ctypes.c_double]
dms.restype = Dms

dmm = geoid.dmm
dmm.argtypes = [ctypes.c_double]
dmm.restype = Dmm

geocentric = geoid.geocentric
geocentric.argtypes = [ctypes.POINTER(Ellipsoid), ctypes.POINTER(Geodesic)]
geocentric.restype = Geocentric

geodesic = geoid.geodesic
geodesic.argtypes = [ctypes.POINTER(Ellipsoid), ctypes.POINTER(Geocentric)]
geodesic.restype = Geodesic

distance = geoid.distance
distance.argtypes = [
    ctypes.POINTER(Ellipsoid),
    ctypes.POINTER(Geodesic),
    ctypes.POINTER(Geodesic)
]
distance.restype = Vincenty_dist

destination = geoid.destination
destination.argtypes = [
    ctypes.POINTER(Ellipsoid),
    ctypes.POINTER(Geodesic),
    ctypes.POINTER(Vincenty_dist)
]
destination.restype = Vincenty_dest

dat2dat = geoid.dat2dat
dat2dat.argtypes = [
    ctypes.POINTER(Datum),
    ctypes.POINTER(Datum),
    ctypes.POINTER(Geocentric)
]
dat2dat.restype = Geocentric

npoints = geoid.npoints
npoints.argtypes = [
    ctypes.POINTER(Ellipsoid),
    ctypes.POINTER(Geodesic),
    ctypes.POINTER(Geodesic),
    ctypes.c_int
]
npoints.restype = ctypes.POINTER(Vincenty_dest)

lagrange = geoid.lagrange
lagrange.argtypes = [
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_int
]
lagrange.restype = ctypes.c_double

for name in __c_proj__:
    forward_name = name + "_forward"
    inverse_name = name + "_inverse"

    setattr(
        getattr(proj, forward_name), "argtypes",
        [ctypes.POINTER(Crs), ctypes.POINTER(Geodesic)]
    )
    setattr(getattr(proj, forward_name), "restype", Geographic)
    setattr(sys.modules[__name__], forward_name, getattr(proj, forward_name))

    setattr(
        getattr(proj, inverse_name), "argtypes",
        [ctypes.POINTER(Crs), ctypes.POINTER(Geographic)]
    )
    setattr(getattr(proj, inverse_name), "restype", Geodesic)
    setattr(sys.modules[__name__], inverse_name, getattr(proj, inverse_name))
