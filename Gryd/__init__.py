# -*- coding: utf-8 -*-

"""
# EPSG dataset

All epsg crs linked to these projections are available through python API
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

# Raster map interpolation

`Gryd.Crs` also provides functions for raster map coordinates interpolation
using calibration `Points` (two minimum are required).

## Geodesic object

[See `Gryd.geodesy` module](geodesy.md)
"""

import os
import sys
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
        ".zip" in __path__ or
        ".egg" in __path__
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


# Connection to epsg.sqlite database
EPSG_CON = sqlite3.connect(get_data_file("db/epsg.sqlite"))
EPSG_CON.row_factory = sqlite3.Row


def names(cls):
    """
    Return list of tuples (name and epsg reference) available in the sqlite
    database.

    Arguments:
        cls (Gryd.Epsg): Epsg instance
    Returns:
        (`str`, `int`) list
    """
    if not hasattr(cls, "_names"):
        setattr(cls, "_names", [
            (r["name"], r["epsg"]) for r in Epsg.sqlite.execute(
                "SELECT * from %s" % cls.table,
            ).fetchall()
        ])
    return getattr(cls, "_names")


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

    x = property(
        lambda cls: cls.easting,
        lambda cls, value: setattr(cls, "easting", value),
        None,
        ""
    )
    y = property(
        lambda cls: cls.northing,
        lambda cls, value: setattr(cls, "northing", value),
        None,
        ""
    )

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

    # def __hash__(self):
    #     return hash(self.px) ^ hash(self.py) ^ hash(self.lla) ^ hash()

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
        return "<Dist %.3fkm initial bearing=%.1f° final bearing=%.1f°>" %\
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
        longitude (float): destination longitude in degrees
        latitude (float): destination latitude in degrees
        destination_bearing (float): destination bearing in degrees
    """
    _fields_ = [
        ("longitude",           ctypes.c_double),
        ("latitude",            ctypes.c_double),
        ("destination_bearing", ctypes.c_double)
    ]

    def __repr__(self):
        return "<Dest lon=%r lat=%r end bearing=%.1f°>" % (
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
    -060°25'22.326''
    >>> float(d)
    -60.42286847222222
    ```

    Attributes:
        sign (int): `1` if positive, `-1` if negative
        degree (float): integer parts of value
        minute (float): `1/60` fractions of value
        second (float): `1/3600` fractions of value
    """
    _fields_ = [
        ("sign",   ctypes.c_short),
        ("degree", ctypes.c_double),
        ("minute", ctypes.c_double),
        ("second", ctypes.c_double)
    ]

    def __repr__(self):
        return "%0+4d°%02d'%00.3f''" % (
            self.sign * self.degree, self.minute, self.second
        )

    def __float__(self):
        return self.sign * (
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

    Attributes:
        sign (int): `1` if positive, `-1` if negative
        degree (float): integer parts of value
        minute (float): `1/60` fractions of value
    """
    _fields_ = [
        ("sign",   ctypes.c_short),
        ("degree", ctypes.c_double),
        ("minute", ctypes.c_double)
    ]

    def __repr__(self):
        return "%0+4d°%00.6f'" % (self.sign * self.degree, self.minute)

    def __float__(self):
        return self.sign * (self.minute / 60. + self.degree)


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

        if an attribute is not defined in the `_fields_` list, it is set to the
        python part of the class, not the `ctypes` structure.
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

    Attributes:
        epsg (int): EPSG reference
        ratio (float): coeficient to apply for metter conversion
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
    <Prime meridian epsg=8902 longitude=-009°07'54.862''>
    >>> prime.name
    'Lisbon'
    ```

    Attributes:
        epsg (int): EPSG reference
        longitude (float): latitude value
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
    Ellipsoid model. If initialized with no args nor keyword args, it is a
    6378137-meters-radius sphere.

    ```python
    >>> wgs84 = Gryd.Ellipsoid("WGS 84")
    >>> wgs84
    <Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
    ```

    Attributes:
        epsg (int): EPSG reference
        a (float): semi major axis
        b (float): semi minor axis
        e (float): exentricity
        f (float): flattening
    """
    table = "ellipsoid"
    _fields_ = [
        ("epsg", ctypes.c_int),
        ("a",    ctypes.c_double),
        ("b",    ctypes.c_double),
        ("e",    ctypes.c_double),
        ("f",    ctypes.c_double)
    ]

    def __init__(self, *args, **pairs):
        if len(args) == len(pairs) == 0:
            pairs["a"] = pairs["b"] = 6378137.
        Epsg.__init__(self, *args, **pairs)

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
        Return Vincenty distance between two geodesic points.

        ```
        >>> london = Gryd.Geodesic(-0.127005, 51.518602, 0.)
        >>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
        >>> wgs84.distance(dublin, london)
        <Dist 464.025km initial bearing=113.6 final bearing=118.5°>
        ```

        Arguments:
            lla0 (Gryd.Geodesic): point A
            lla1 (Gryd.Geodesic): point B
        Returns:
            `Gryd.Vincenty_dist` structure
        """
        return distance(self, lla0, lla1)

    def destination(self, lla, bearing, distance):
        """
        Return Vincenty destination from geodesic start point following
        specific bearing for a determined distance.

        ```python
        >>> wgs84.destination(
        ...     london, math.degrees(vdist.final_bearing) + 180, vdist.distance
        ... )
        <Dest lon=-006°15'33.973'' lat=+053°21'2.754'' end bearing=-66.4°>
        >>> dublin
        <lon=-006°15'33.973'' lat=+053°21'2.754'' alt=0.000>
        ```

        Arguments:
            lla (Gryd.Geodesic): start point
            bearing (float): start bearing in degrees
            distance (float): distance in meters
        Returns:
            `Gryd.Vincenty_dest` structure
        """
        return destination(
            self, lla, Vincenty_dist(distance, math.radians(bearing))
        )

    def npoints(self, lla0, lla1, n):
        """
        Return number of intermediary geodesic coordinates points between two
        points using Vincenty formulae.

        ```python
        >>> for p in wgs84.npoints(dublin, londre, 4): print(p)
        ...
        <Dest lon=-006°15'33.973'' lat=+053°21'2.754'' end bearing=113.6>
        <Dest lon=-004°59'32.422'' lat=+053°00'36.687'' end bearing=114.6>
        <Dest lon=-003°44'43.501'' lat=+052°39'22.715'' end bearing=115.6>
        <Dest lon=-002°31'7.792'' lat=+052°17'22.201'' end bearing=116.6>
        <Dest lon=-001°18'45.650'' lat=+051°54'36.502'' end bearing=117.5>
        <Dest lon=-000°07'37.218'' lat=+051°31'6.967'' end bearing=118.5>
        ```
        Arguments:
            lla0 (Gryd.Geodesic): start point
            lla1 (Gryd.Geodesic): end point
            n (int): number uf intermediary points
        Returns:
            list of `Gryd.Vincenty_dest`
        """
        result = ()
        pts = npoints(self, lla0, lla1, n)
        for i in range(n + 2):
            result += (pts[i], )
        return result


class Datum(Epsg):
    """
    Datum is defined by an ellipsoid, a prime meridian and a set of seven
    parameters to convert geodesic coordinates to wgs84.

    ```python
    >>> Gryd.Datum(epsg=4326)
    <Datum epsg=4326:
    <Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
    <Prime meridian epsg=8901 longitude=0.000000>
    to wgs84: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0>
    ```

    Attributes:
        epsg (int): EPSG reference
        prime (Gryd.Prime): prime meridian
        ellispoid (Gryd.Ellipsoid): ellipsoid
        ds (float): expansion coef
        dx (float): x-axis translation coef
        dy (float): y-axis translation coef
        dz (float): z-axis translation coef
        rx (float): x-axis rotation coef
        ry (float): y-axis rotation coef
        rz (float): z-axis rotation coef
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
        Convert geodesic coordinates to geocentric coordinates.

        ```python
        >>> wgs84.xyz(london)
        <X=3977018.848 Y=-8815.695 Z=4969650.564>
        ```

        Arguments:
            lla (Gryd.Geodesic): geodesic coordinates
        Returns:
            `Gryd.Geocentric` coordinates
        """
        lla.longitude += self.prime.longitude
        return geocentric(self.ellipsoid, lla)
    geographic = xyz

    def lla(self, xyz):
        """
        Convert geocentric coordinates to geodesic coordinates.

        ```python
        >>> wgs84.lla(wgs84.xyz(london))
        <lon=-000°07'37.218'' lat=+051°31'6.967'' alt=0.000>
        >>> london
        <lon=-000°07'37.218'' lat=+051°31'6.967'' alt=0.000>
        ```

        Arguments:
            xyz (Gryd.Geodesic): geocentric coordinates
        Returns:
            `Gryd.Geodesic` coordinates
        """
        lla = geodesic(self.ellipsoid, xyz)
        lla.longitude -= self.prime.longitude
        return lla
    geodesic = lla

    def transform(self, dst, lla):
        """
        Transform geodesic coordinates to another datum.

        ```python
        >>> airy = Gryd.Datum(epsg=4277)
        >>> wgs84.transform(airy, london)
        <lon=-000°07'31.431'' lat=+051°31'5.137'' alt=-46.118>
        ```

        Arguments:
            dst (Gryd.Datum): destination datum
            lla (Gryd.Geodesic): geodesic coordinates to transform
        Returns:
            `Gryd.Geodesic` coordinates
        """
        return dst.lla(dat2dat(self, dst, self.xyz(lla)))


class Crs(Epsg):
    """
    Coordinate reference system object allowing projection of geodesic
    coordinates to flat map (geographic coordinates).

    ```python
    >>> pvs = Gryd.Crs(epsg=3785)
    >>> osgb36 = Gryd.Crs(epsg=27700)
    >>> osgb36.datum.xyz(london)
    <X=3976632.017 Y=-8814.837 Z=4969286.446>
    >>> osgb36.datum.ellipsoid.distance(dublin, london)
    <Dist 463.981km initial bearing=113.6° final bearing=118.5°>
    >>> osgb36
    <Crs epsg=27700:
    <Datum epsg=4277:
    <Ellispoid epsg=7001 a=6377563.396000 1/f=299.32496460>
    <Prime meridian epsg=8901 longitude=0.000000>
    to wgs84 446.45,-125.16,542.06,-20.49,0.15,0.25,0.84>
    <Unit epsg=9001 ratio=1.0>
    Projection 'tmerc'>
    ```

    Attributes:
        epsg (int): EPSG reference
        datum (Gryd.Datum): prime used in crs
        unit (Gryd.Unit): unit used in crs
        lambda0 (float): tmerc projection coef
        phi0 (float): tmerc and omerc projection coef
        phi1 (float): lcc projection coef
        phi2 (float): lcc projection coef
        k0 (float): tmerc projection coef
        x0 (float): false northing
        y0 (float): false easting
        azimut (float): omerc projection coef
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

    proj = property(
        lambda cls: getattr(cls, "projection"),
        lambda cls, value: setattr(cls, "projection", value),
        None,
        ""
    )

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
        self.map_points = []
        self.projection = "latlong"
        Epsg.__init__(self, *args, **kwargs)
        self.unit = kwargs.pop("unit", 9001)

    def __setattr__(self, attr, value):
        if attr == "datum" and not isinstance(value, Datum):
            value = Datum(value)
        elif attr == "unit" and not isinstance(value, Unit):
            value = Unit(value)
        elif attr == "projection":
            if isinstance(value, int):
                record = Epsg.sqlite.execute(
                    "SELECT * from projection WHERE epsg=%r;" % value
                ).fetchall()
                if len(record) > 0:
                    value = record[0]["typeproj"]
                else:
                    raise Exception("EPSG projection #%d unknown" % value)
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
        Heuristic transformation according to crs properties.

        ```python
        >>> osgb36(london)  # projection of Geodesic point
        <X=529939.106 Y=181680.962s alt=0.000>
        >>> osgb36(osgb36(london))  # deprojection of Geographic point
        <lon=-000°07'37.218'' lat=+051°31'6.967'' alt=0.000>
        ```

        Arguments:
            element (Gryd.Geodesic or Gryd.Geographic): coordinates to be
                                                        transformed
        Returns:
            `Gryd.Geographic` or `Gryd.Geodesic` coordinates
        """
        if not hasattr(self, "forward"):
            setattr(self, "projection", getattr(self, "projection", None))

        ratio = self.unit.ratio
        if isinstance(element, Geodesic):
            xya = self.forward(self, element)
            xya.x /= ratio
            xya.y /= ratio
            return xya
        else:
            element.x *= ratio
            element.y *= ratio
            return self.inverse(self, element)

    def transform(self, dst, xya):
        """
        Transform geographical coordinates to another coordinate reference
        system.

        ```python
        >>> london_pvs = osgb36.transform(pvs, osgb36(london))
        >>> london_pvs
        <X=-14317.072 Y=6680144.273s alt=-13015.770>
        >>> pvs.transform(osgb36, london_pvs)
        <X=529939.101 Y=181680.963s alt=0.012>
        >>> osgb36(london)
        <X=529939.106 Y=181680.962s alt=0.000>
        ```

        Arguments:
            dst (Gryd.Crs): destination coordinate reference system
            xya (Gryd.Geographic): geographic coordinates to transform
        Returns:
            `Gryd.Geographic` coordinates
        """
        return dst(self.datum.transform(dst.datum, self(xya)))

    def _xiyi(self):
        points = self.map_points
        geographics = [p.xya for p in self.map_points]
        n = len(points)
        self._pxi = t_byref(ctypes.c_double, n, *[p.px for p in points])
        self._pyi = t_byref(ctypes.c_double, n, *[p.py for p in points])
        self._Xi = t_byref(ctypes.c_double, n, *[p.x for p in geographics])
        self._Yi = t_byref(ctypes.c_double, n, *[p.y for p in geographics])

    def add_map_point(self, px, py, point):
        """
        Add a calibration point to coordinate reference system. Calibration
        points maps a specific pixel coordinates from a raster image (top left
        reference) to a geodesic coordinates and its associated geographic
        ones.

        ```python
        >>> # 512x512 pixel web map mercator
        >>> pvs.add_map_point(0,0, Gryd.Geodesic(-179.999, 85))
        >>> pvs.add_map_point(512,512, Gryd.Geodesic(179.999, -85))
        >>> pvs.map_points
        [<px=0 py=0
        <lon=-179°59'56.400'' lat=+085°00'0.000'' alt=0.000>
        <X=-20037397.023 Y=19971868.880s alt=0.000>
        >, <px=512 py=512
        <lon=+179°59'56.400'' lat=-085°00'0.000'' alt=0.000>
        <X=20037397.023 Y=-19971868.880s alt=0.000>
        >]
        ```

        Arguments:
            px (float): pixel column position
            py (float): pixel row position
            point (Gryd.Geodesic or Gryd.Geographic): geodesic or geographic
                                                      coordinates
        """
        if px in [p.px for p in self.map_points] or \
           py in [p.py for p in self.map_points]:
            raise Exception("pixel row or column already referenced")
        if isinstance(point, Geodesic):
            geodesic = point
            geographic = self(point)
        else:
            geodesic = self(point)
            geographic = point
        self.map_points.append(Point(px, py, geodesic, geographic))
        self._xiyi()

    def delete_map_point(self, *points_or_indexes):
        """
        Delete multiple calibration points using index (starting with 1) or
        `Gryd.Point` reference.

        ```python
        pvs.delete_map_point(0)
        [<px=512 py=512
        <lon=+179°59'56.400'' lat=-085°00'0.000'' alt=0.000>
        <X=20037397.023 Y=-19971868.880s alt=0.000>
        >]
        >>> pvs.delete_map_point(pvs.map_points[0])
        [<px=0 py=0
        <lon=-179°59'56.400'' lat=+085°00'0.000'' alt=0.000>
        <X=-20037397.023 Y=19971868.880s alt=0.000>
        >]
        >>> pvs.map_points
        []
        ```
        Arguments:
            *points_or_indexes (int or Gryd.Point): index (starting with 1)
                                                      or point reference
        Returns:
            `list` of deleted `Gryd.Point`
        """
        result = []
        for point_or_index in points_or_indexes:
            if isinstance(point_or_index, int) and \
               point_or_index <= len(self.map_points):
                result.append(self.map_points.pop(point_or_index - 1))
            elif point_or_index in self.map_points:
                result.append(
                    self.map_points.pop(
                        self.map_points.index(point_or_index)
                    )
                )
        self._xiyi()
        return result

    def map2crs(self, px, py, geographic=False):
        """
        Geodesic or geographic interpolation on raster image from pixel
        coordinates.

        ```python
        >>> pvs.map2crs(256+128, 256+128)
        <lon=+089°59'58.20'' lat=-066°23'43.74'' alt=0.000>
        >>> pvs.map2crs(256-128, 256+128, geographic=True)
        <point X=-10018698.512 Y=-9985934.440s alt=0.000>
        ```

        Arguments:
            px (float): pixel column position
            py (float): pixel row position
            geographic (bool): determine coordinates type returned
        Returns:
            `Gryd.Geographic` if `geographic` is True else `Gryd.Geodesic`
        """
        n = len(self.map_points)
        if n >= 2:
            x = lagrange(px, self._pxi, self._Xi, n)
            y = lagrange(py, self._pyi, self._Yi, n)
            if geographic:
                return Geographic(x, y, 0)
            else:
                return self(Geographic(x, y, 0))
        else:
            raise Exception("no enough calibration points in this Crs")

    def crs2map(self, point):
        """
        Pixel interpolation on raster image from geodesic point.

        ```python
        >>> pvs.crs2map(london)
        <px=256 py=170
        <lon=-000°07'37.218'' lat=+051°31'6.967'' alt=0.000>
        <X=-14138.132 Y=6713546.215s alt=0.000>
        >
        >>> pvs.crs2map(dublin)
        <px=247 py=166
        <lon=-006°15'33.973'' lat=+053°21'2.754'' alt=0.000>
        <X=-696797.339 Y=7048145.354s alt=0.000>
        >
        ```

        Arguments:
            point (Gryd.Geodesic or Gryd.Geographic): geodesic or geographic
                                                      coordinates
        Returns:
            `Gryd.Point`
        """
        if isinstance(point, Geodesic):
            geodesic_point = point
            point = self(point)
        elif isinstance(point, (Grid, Geographic)):
            geodesic_point = self(point)
            point = point
        else:
            raise Exception("not a valid point")

        n = len(self.map_points)
        if n >= 2:
            return Point(
                lagrange(point.x, self._Xi, self._pxi, n),
                lagrange(point.y, self._Yi, self._pyi, n),
                geodesic_point,
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
