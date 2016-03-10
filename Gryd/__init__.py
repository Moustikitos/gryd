# -*- encoding:utf-8 -*-
# http://bruno.thoorens.free.fr/licences/gryd.html
# Copyright© 2015-2016, THOORENS Bruno
# All rights reserved.

"""Gryd package provides efficient great circle computation and projection
library.

EPSG dataset
============

All epsg dataset linked to these projections are available through
python API using epsg id or name. Available projections are Mercator,
Transverse Mercator and Lambert Conformal Conic. 

Grids
=====

The four main grids are available : Universal Transverse Mercator,
Military Grid Reference System, British National Grid and Irish
National Grid.

>>> from Gryd import *
>>> dublin = Geodesic(-6.259437, 53.350765, 0.)
>>> utm = Crs(epsg=3395, projection="utm")
>>> utm(dublin)
Grid point area=29U E=682406.211 N=5914792.531, alt=0.000
>>> mgrs = Crs(epsg=3395, projection="mgrs")
>>> mgrs(dublin)
Grid point area=29U PV E=82406.211 N=14792.531, alt=0.000
>>> bng = Crs(projection="bng")
>>> bng(dublin)
Grid point area=SG E=16572.029 N=92252.917, alt=0.000
>>> ing = Crs(projection="ing")
>>> ing(dublin)
Grid point area=O E=15890.887 N=34804.964, alt=0.000

Image-map interpolation
=======================

``Gryd.Crs`` class also provides functions for map coordinates
interpolation using calibration points. Two points minimum are
required.
"""

__author__  = "Bruno THOORENS"
# Major.minor.micro version number. The micro number is bumped for API
# changes, for new functionality, and for interim project releases.  The minor
# number is bumped whenever there is a significant project release.  The major
# number will be bumped when the project is feature-complete, and perhaps if
# there is a major change in the design.
__version__ = "1.1.1"

# add C projection functions here
__c_proj__ = ["omerc", "tmerc", "merc", "lcc", "eqc", "miller"]

# add python projection modules here
__py_proj__ = ["utm", "mgrs", "bng", "ing"]

from .geodesy import *
import os, sys, imp, math
import ctypes, sqlite3
__dll_ext__ = "dll" if sys.platform.startswith("win") else \
              "so" if sys.platform.startswith("linux") else \
              "so"
if not(2**32//2-1 == sys.maxsize): __dll_ext__ = "64." + __dll_ext__

_TORAD = math.pi/180.0
_TODEG = 180.0/math.pi

def main_is_frozen():
	"Return True if it runs from a frozen script (py2exe, cx_Freeze...)"
	return (
		hasattr(sys, "frozen") or    # new py2exe
		hasattr(sys, "importers") or # old py2exe
		imp.is_frozen("__main__")    # tools/freeze
	)

# find data file
def get_data_file(name):
	"Find data file according to package (frozen or not) installation path"
	if main_is_frozen():
		return os.path.join(os.path.dirname(sys.executable), name)
	else:
		for path in __path__:
			filename = os.path.join(path, name)
			if os.path.exists(filename): return filename
		raise IOError("%s data file not found"%name)

# create and configure connection to epsg database
EPSG_CON = sqlite3.connect(get_data_file("epsg.sqlite"))
EPSG_CON.row_factory = sqlite3.Row

# Create a table of n ctypes and return pointer
t_byref = lambda ctype, n, *args: ctypes.cast((ctype * n)(*args), ctypes.POINTER(ctype))

class Geocentric(ctypes.Structure):
	"""ctypes structure for geocentric coordinates. Attributes :
 * x -> X-axis value
 * y -> Y-axis value
 * z -> Z-axis value

>>> Gryd.Geocentric(x=4457584, y=429216, z=4526544)
Geocentric point X=4457584.000 Y=429216.000 Z=4526544.000"""
	_fields_ = [
		("x", ctypes.c_double),
		("y", ctypes.c_double),
		("z", ctypes.c_double)
	]

	def __repr__(self):
		return "Geocentric point X=%.3f Y=%.3f Z=%.3f" % (self.x, self.y, self.z)

class Geographic(ctypes.Structure):
	"""ctypes structure for geographic coordinates. 2D coordinates on flattened
earth (usng a projection system) with altitude as third dimension. Attributes :
 * x -> X-projection-axis value
 * y -> Y-projection-axis value
 * altitude

>>> Gryd.Geographic(x=5721186, y=2948518, altitude=105)
Geographic point X=5721186.000 Y=2948518.000 alt=105.000"""
	_fields_ = [
		("x",        ctypes.c_double),
		("y",        ctypes.c_double),
		("altitude", ctypes.c_double)
	]

	def __repr__(self):
		return "Geographic point X=%.3f Y=%.3fs alt=%.3f" % (self.x, self.y, self.altitude)

class Grid(ctypes.Structure):
	"""ctypes structure for grided coordinates. Another coordinates system
applied on flattened earth. It is defined by an area, a 2D coordinates and
altitude. Attributes :
 * area -> string region
 * easting -> X-grid-axis value
 * northing -> Y-grid-axis value

>>> Gryd.Grid(area="31T", easting=925595, northing=5052949, altitude=105)
Grid point area=31T E=925595.000 N=5052949.000, alt=105.000"""
	area = ""
	_fields_ = [
		("easting",  ctypes.c_double),
		("northing", ctypes.c_double),
		("altitude", ctypes.c_double),
	]

	def __repr__(self):
		return "Grid point area=%s E=%.3f N=%.3f, alt=%.3f" % (self.area, self.easting, self.northing, self.altitude)

def _Geodesic__repr(obj):
	return "Geodesic point lon=%r lat=%r alt=%.3f" % (dms(math.degrees(obj.longitude)), dms(math.degrees(obj.latitude)), obj.altitude)
setattr(Geodesic, "__repr__", _Geodesic__repr)


class Point(ctypes.Structure):
	"""ctypes structure for calibration point. Attributes :
 * px -> pixel column position
 * py -> pixel row position
 * lla -> Gryd.Geodesic associated to the pixel coordinates
 * xya -> Gryd.Geographic associated to the pixel coordinates"""
	_fields_ = [
		("px",  ctypes.c_double),
		("py",  ctypes.c_double),
		("lla", Geodesic),
		("xya", Geographic)
	]

	def __repr__(self):
		return "Reference point px=%.0f py=%.0f\n- <%r>\n- <%r>" % (self.px, self.py, self.lla, self.xya)

class Vincenty_dist(ctypes.Structure):
	""">>> wgs84 = Gryd.Ellipsoid(name="WGS 84") # WGS 84 ellipsoid
>>> london = Gryd.Geodesic(-0.127005, 51.518602, 0.)
>>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
>>> vdist = wgs84.distance(dublin, london)
>>> vdist
Distance 464.025km initial bearing=113.6 final bearing=118.5
>>> vdist.distance, vdist.initial_bearing, vdist.final_bearing
(464025.2235062019, 1.9826304238310775, 2.0675106301597674)"""
	_fields_ = [
		("distance",        ctypes.c_double),
		("initial_bearing", ctypes.c_double),
		("final_bearing",   ctypes.c_double)
	]

	def __repr__(self):
		return "Distance %.3fkm initial bearing=%.1f final bearing=%.1f" % (self.distance/1000, math.degrees(self.initial_bearing), math.degrees(self.final_bearing))

class Vincenty_dest(ctypes.Structure):
	""">>> vdest = wgs84.destination(london, math.degrees(vdist.final_bearing)+180, vdist.distance)
>>> vdest
Destination lon=-006°15'33.973'' lat=+053°21'2.754'' end bearing=-66.4
>>> dublin
Geodesic point lon=-006°15'33.973'' lat=+053°21'2.754'' alt=0.000
>>> vdest.longitude, vdest.latitude, vdest.destination_bearing
(-0.10924778507143726, 0.9311465077339985, -1.1589622298392817)"""
	_fields_ = [
		("longitude",           ctypes.c_double),
		("latitude",            ctypes.c_double),
		("destination_bearing", ctypes.c_double)
	]

	def __repr__(self):
		return "Destination lon=%r lat=%r end bearing=%.1f" % (dms(math.degrees(self.longitude)), dms(math.degrees(self.latitude)), math.degrees(self.destination_bearing))

class Dms(ctypes.Structure):
	""">>> Gryd.Dms(sign=1, degree=60, minute=25, second=22.3265)
+060°25´22.33´´
>>> Gryd.Dms(0, 60, 25, 22.3265)
-060°25´22.33´´
>>> float(Gryd.Dms(0, 60, 25, 22.3265))
-60.42286847222222"""
	_fields_ = [
		("sign",   ctypes.c_short),
		("degree", ctypes.c_double),
		("minute", ctypes.c_double),
		("second", ctypes.c_double)
	]

	def __repr__(self):
		return "%s%03d°%02d'%00.3f''" % ("+" if self.sign>0 else "-", self.degree, self.minute, self.second)
	
	def __float__(self):
		return (1 if self.sign>0 else -1) * (((self.second/60)+self.minute)/60 + self.degree)

class Dmm(ctypes.Structure):
	""">>> Gryd.Dmm(sign=1, degree=60, minute=25.372108333333188)
+060°25.3721083´
>>> Gryd.Dmm(0, 60, 25.372108333333188)
-060°25.3721083´
>>> float(Gryd.Dmm(0, 60, 25.372108333333188))
-60.42286847222222"""
	_fields_ = [
		("sign",   ctypes.c_short),
		("degree", ctypes.c_double),
		("minute", ctypes.c_double)
	]

	def __repr__(self): 
		return "%s%03d°%00.6f'" % ("+" if self.sign>0 else "-", self.degree, self.minute)

	def __float__(self):
		return (1 if self.sign>0 else -1) * (self.minute/60 + self.degree)


class Structure(ctypes.Structure):
	"""ctypes structure with a sqlite connection for initialization purpose."""
	sqlite = EPSG_CON.cursor() # Shared sqlite database to be linked with
	table = "" # The table database name where __init__ will find data

	def __init__(self, *args, **pairs):
		"""if keyword argument is given, it searches in sqlite database an entry matching
the given pair. If list of values is given, structure members are initialized in the
order of the field definition."""
		ctypes.Structure.__init__(self, *args)
		s = {}
		# if name or epsg id is given
		if "epsg" in pairs: s["epsg"], key = pairs.pop("epsg"), "epsg"
		elif "name" in pairs: s["name"], key = pairs.pop("name"), "name"
		if len(s) == 1:
			record = Structure.sqlite.execute("SELECT * from %s WHERE %s=?" % (self.table, key), (s[key],)).fetchall()
			# if something found
			if len(record) > 0:
				tmp = dict(record[0])
				tmp.update(**pairs)
				pairs = tmp
			else:
				raise Exception("Nothing found in %s table with %s=%s" % (self.table, key, s[key]))
		elif len(s) == 2:
			raise Exception("Can not initialize %s with epsg and name in the same time" % self.__class__)

		for key,value in sorted(pairs.items(), key=lambda e:e[0]):
			if key == "lambda": key, value = "longitude", math.radians(value)
			elif key in ["lambda0", "phi0", "phi1", "phi2", "azimut"]: value = math.radians(value)
			elif key in ["rf", "1/f", "invf"]: key, value = ("f", 1./value) if value != 0. else ("f", 0.)
			setattr(self, key, value)

class Unit(Structure):
	""">>> Gryd.Unit(epsg=9001)
Unit epsg=9001 ratio=1.0
>>> Gryd.Unit(epsg=9001).name
'metre'
>>> Gryd.Unit(name="foot")
Unit epsg=9002 ratio=3.2808693302666354
>>> Gryd.Unit(epsg=9002).name
'foot'
>>> float(Gryd.Unit(name="foot"))
3.2808693302666354"""
	table = "unit"
	_fields_ = [
		("epsg",  ctypes.c_int),
		("ratio", ctypes.c_double)
	]

	def __repr__(self):
		return "Unit epsg=%d ratio=%r" % (self.epsg, self.ratio)

	def __float__(self):
		return self.ratio

class Prime(Structure):
	""">>> Gryd.Prime(longitude=3.1416)
Prime meridian epsg=0 longitude=180.000421
>>> Gryd.Prime(epsg=8902)
Prime meridian epsg=8902 longitude=-9.131906
>>> Gryd.Prime(epsg=8902).name
'Lisbon'
>>> float(Gryd.Prime(epsg=8902))
-0.15938182862188002"""

	table = "prime"
	_fields_ = [
		("epsg",      ctypes.c_int),
		("longitude", ctypes.c_double)
	]

	def __repr__(self):
		return "Prime meridian epsg=%d longitude=%.6f" % (self.epsg, math.degrees(self.longitude))

	def __float__(self):
		return self.longitude

class Ellipsoid(Structure):
	""">>> wgs84 = Gryd.Ellipsoid(name="WGS 84")
>>> wgs84
Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356"""
	table = "ellipsoid"
	_fields_ = [
		("epsg", ctypes.c_int),
		("a",    ctypes.c_double),
		("b",    ctypes.c_double),
		("e",    ctypes.c_double),
		("f",    ctypes.c_double)
	]

	def __repr__(self):
		return "Ellispoid epsg=%d a=%.6f 1/f=%.8f" % (self.epsg, self.a, (1/self.f if self.f != 0. else 0.))

	def __setattr__(self, attr, value):
		Structure.__setattr__(self, attr, value)
		if attr  == "b":
			Structure.__setattr__(self, "f", (self.a-value) / self.a)
			Structure.__setattr__(self, "e", math.sqrt(2*self.f - self.f**2))
		elif attr == "e":
			Structure.__setattr__(self, "b", math.sqrt(self.a**2 * (1 - value**2)))
			Structure.__setattr__(self, "f", (self.a - self.b) / self.a)
		elif attr == "f":
			Structure.__setattr__(self, "e", math.sqrt(2*value - value**2))
			Structure.__setattr__(self, "b", math.sqrt(self.a**2 * (1 - self.e**2)))

	def distance(self, lla0, lla1):
		""">>> london = Gryd.Geodesic(-0.127005, 51.518602, 0.)
>>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
>>> wgs84.distance(dublin, london)
Distance 464.025km initial bearing=113.6 final bearing=118.5"""
		return distance(self, lla0, lla1)

	def destination(self, lla, bearing, distance):
		""">>> wgs84.destination(london, math.degrees(vdist.final_bearing)+180, vdist.distance)
Destination lon=-006°15'33.973'' lat=+053°21'2.754'' end bearing=-66.4
>>> dublin
Geodesic point lon=-006°15'33.973'' lat=+053°21'2.754'' alt=0.000"""
		return destination(self, lla, Vincenty_dist(distance, math.radians(bearing)))

	def npoints(self, lla0, lla1, n):
		""">>> for p in wgs84.npoints(dublin, londre, 4): print(p)
...
Destination lon=-006°15'33.973'' lat=+053°21'2.754'' end bearing=113.6
Destination lon=-004°59'32.422'' lat=+053°00'36.687'' end bearing=114.6
Destination lon=-003°44'43.501'' lat=+052°39'22.715'' end bearing=115.6
Destination lon=-002°31'7.792'' lat=+052°17'22.201'' end bearing=116.6
Destination lon=-001°18'45.650'' lat=+051°54'36.502'' end bearing=117.5
Destination lon=-000°07'37.218'' lat=+051°31'6.967'' end bearing=118.5
"""
		result = ()	
		pts = npoints(self, lla0, lla1, n)
		for i in range(n+2): result += (pts[i],)
		return result

class Datum(Structure):
	""">>> Gryd.Datum(epsg=4326)
Datum epsg=4326:
- <Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
- <Prime meridian epsg=8901 longitude=0.000000>
- to wgs84 0.0,0.0,0.0,0.0,0.0,0.0,0.0"""
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
		return "Datum epsg=%d:\n- <%r>\n- <%r>\n- to wgs84 %s" % (self.epsg, self.ellipsoid, self.prime, ",".join(str(getattr(self, attr)) for attr in ["dx","dy","dz","ds","rx","ry","rz"]))

	def __setattr__(self, attr, value):
		if attr == "ellipsoid":
			if isinstance(value, dict): value = Ellipsoid(**value)
			elif isinstance(value, int): value = Ellipsoid(epsg=value)
			elif isinstance(value, (str, bytes)): value = Ellipsoid(name=value)
			elif not isinstance(value, Ellipsoid): raise Exception("Cannot configure Datum with ellipsoid %r" % value)
		elif attr == "prime":
			if isinstance(value, int): value = Prime(epsg=value)
			elif isinstance(value, (str, bytes)): value = Prime(name=value)
			elif not isinstance(value, Prime): raise Exception("Cannot configure Datum with prime %r" % value)
		Structure.__setattr__(self, attr, value)

	def xyz(self, lla):
		""">>> wgs84.xyz(london)
Geocentric point X=3977018.848 Y=-8815.695 Z=4969650.564"""
		lla.longitude += self.prime.longitude
		return geocentric(self.ellipsoid, lla)

	def lla(self, xyz):
		""">>> wgs84.lla(wgs84.xyz(london))
Geodesic point lon=-000°07'37.218'' lat=+051°31'6.967'' alt=0.000
>>> london
Geodesic point lon=-000°07'37.218'' lat=+051°31'6.967'' alt=0.000"""
		lla = geodesic(self.ellipsoid, xyz)
		lla.longitude -= self.prime.longitude
		return lla

	def transform(self, dst, lla):
		""">>> airy = Gryd.Datum(epsg=4277)
>>> wgs84.transform(airy, london)
Geodesic point lon=-000°07'31.431'' lat=+051°31'5.137'' alt=-46.118"""
		return dst.lla(dat2dat(self, dst, self.xyz(lla)))

class Crs(Structure):
	""">>> pvs = Gryd.Crs(epsg=3785)
>>> osgb36 = Gryd.Crs(epsg=27700)
>>> osgb36.datum.xyz(london)
Geocentric point X=3976632.017 Y=-8814.837 Z=4969286.446
>>> osgb36.datum.ellipsoid.distance(dublin, london)
Distance 463.981km initial bearing=113.6 final bearing=118.5
>>> osgb36
Crs epsg=27700:
- <Datum epsg=4277:
- <Ellispoid epsg=7001 a=6377563.396000 1/f=299.32496460>
- <Prime meridian epsg=8901 longitude=0.000000>
- to wgs84 446.45,-125.16,542.06,-20.49,0.15,0.25,0.84>
- <Unit epsg=9001 ratio=1.0>
- <Projection 'tmerc'>"""
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
		if hasattr(self, "forward"): self.__dict__.pop("forward")
		if hasattr(self, "inverse"): self.__dict__.pop("inverse")
		return Structure.__reduce__(self)

	def __repr__(self):
		return "Crs epsg=%d:\n- <%r>\n- <%r>\n- <Projection %r>" % (self.epsg, self.datum, self.unit, self.projection)

	def __init__(self, *args, **kwargs):
		self._points = []
		self.projection = "latlong"
		Structure.__init__(self, *args, **kwargs)
		self.unit = kwargs.pop("unit", 9001)

	def __setattr__(self, attr, value):
		if attr == "datum":
			if isinstance(value, dict): value = Datum(**value)
			elif isinstance(value, int): value = Datum(epsg=value)
			elif isinstance(value, (str, bytes)): value = Datum(name=value)
			elif not isinstance(value, Datum): raise Exception("Cannot configure Crs with datum %r" % value)
		elif attr == "unit":
			if isinstance(value, int): value = Unit(epsg=value)
			elif isinstance(value, (str, bytes)): value = Unit(name=value)
			elif not isinstance(value, Unit): raise Exception("Cannot configure Crs with unit %r" % value)
		elif attr == "projection":
			record = Structure.sqlite.execute("SELECT * from projection WHERE epsg=%r;" % value).fetchall()
			if len(record) > 0: value = record[0]["typeproj"]
			if value in __c_proj__:
				eval('Structure.__setattr__(self, "forward", %s_forward)' % value)
				eval('Structure.__setattr__(self, "inverse", %s_inverse)' % value)
			elif value in __py_proj__:
				module = __import__('Gryd.'+value, globals(), locals(), [value], 0)
				Structure.__setattr__(self, "forward", module.forward)
				Structure.__setattr__(self, "inverse", module.inverse)
			else:
				value = "latlong"
				Structure.__setattr__(self, "forward", lambda ellps,lla,o=self:Geographic(lla.longitude*ellps.a,lla.latitude*ellps.b,lla.altitude))
				Structure.__setattr__(self, "inverse", lambda ellps,xya,o=self:Geodesic(xya.x/ellps.a,xya.y/ellps.b,xya.altitude))
		Structure.__setattr__(self, attr, value)

	def __call__(self, element):
		""">>> osgb36(london) # projection of Geodesic point
Geographic point X=529939.106 Y=181680.962s alt=0.000
>>> osgb36(osgb36(london)) # deprojection of Geographic point
Geodesic point lon=-000°07'37.218'' lat=+051°31'6.967'' alt=0.000"""
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
			else: pass
		except AttributeError:
			setattr(self, "projection", getattr(self, "projection", None))
			return self(element)

	def transform(self, dst, xya):
		""">>> osgb36.transform(pvs, osgb36(london))
Geographic point X=-14317.072 Y=6680144.273s alt=-13015.770
>>> pvs.transform(osgb36, osgb36.transform(pvs, osgb36(london)))
Geographic point X=529939.101 Y=181680.963s alt=0.012
>>> osgb36(london)
Geographic point X=529939.106 Y=181680.962s alt=0.000"""
		return dst(self.datum.transform(dst.datum, self(xya)))

	def add_map_point(self, px, py, point):
		""">>> pvs.add_map_point(0,0, Geodesic(-179.999, 85))
>>> pvs.add_map_point(512,512, Geodesic(179.999, -85))"""

		if px in [p.px for p in self._points]: return
		if py in [p.py for p in self._points]: return
		if isinstance(point, Geodesic):
			self._points.append(Point(px, py, point, self(point)))
		elif isinstance(point, Geographic):
			self._points.append(Point(px, py, self(point), point))

	def delete_map_point(self, px=None, py=None, index=None):
		if px == py == index == None: return [self._points.pop(0)]
		elif px != None and py != None: return [p for p in self._points if p.px == px and p.py == py]
		elif isinstance(index, int): return [self._points.pop(min(len(self._points)-1, index))]
		return []

	def map2crs(self, px, py, geographic=False):
		""">>> pvs.map2crs(256+128, 256+128)
Geodesic point lon=+089°59'58.20'' lat=-066°23'43.74'' alt=0.000
>>> pvs.map2crs(256-128, 256+128, geographic=True)
Geographic point X=-10018698.512 Y=-9985934.440s alt=0.000
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
			if geographic: return Geographic(x, y, 0)
			else: return self(Geographic(x, y, 0))
		else:
			raise Exception("no enough calibration points in this Crs")

	def crs2map(self, point):
		""">>> pvs.crs2map(pvs.map2crs(256+128, 256+128))
Reference point px=384 py=384
- <Geodesic point lon=+089°59'58.20'' lat=-066°23'43.74'' alt=0.000>
- <Geographic point X=10018698.512 Y=-9985934.440s alt=0.000>
"""
		if isinstance(point, Geodesic):
			point = self(point)
		elif isinstance(point, Grid):
			raise Exception("only works with Geographic or Geodesic points (Grid points given instead)")

		if len(self._points) >= 2:
			n = len(self._points)
			return Point(
				lagrange(
					point.x,
					t_byref(ctypes.c_double, n, *[p.xya.x for p in self._points]),
					t_byref(ctypes.c_double, n, *[p.px for p in self._points]),
					n
				),
				lagrange(
					point.y,
					t_byref(ctypes.c_double, n, *[p.xya.y for p in self._points]),
					t_byref(ctypes.c_double, n, *[p.py for p in self._points]),
					n
				),
				self(point),
				point
			)
		else:
			raise Exception("no enough calibration points in this Crs")


# loading libgeoid library
geoid = ctypes.CDLL(get_data_file("geoid.%s"%__dll_ext__))
# shortcuts
dms = geoid.dms
dmm = geoid.dmm
geocentric = geoid.geocentric
geodesic = geoid.geodesic
distance = geoid.distance
destination = geoid.destination
dat2dat = geoid.dat2dat
npoints = geoid.npoints
lagrange = geoid.lagrange
# prototypes
dms.argtypes = [ctypes.c_double]
dms.restype = Dms
dmm.argtypes = [ctypes.c_double]
dmm.restype = Dmm
geocentric.argtypes = [ctypes.POINTER(Ellipsoid), ctypes.POINTER(Geodesic)]
geocentric.restype = Geocentric
geodesic.argtypes = [ctypes.POINTER(Ellipsoid), ctypes.POINTER(Geocentric)]
geodesic.restype = Geodesic
distance.argtypes = [ctypes.POINTER(Ellipsoid), ctypes.POINTER(Geodesic), ctypes.POINTER(Geodesic)]
distance.restype = Vincenty_dist
destination.argtypes = [ctypes.POINTER(Ellipsoid), ctypes.POINTER(Geodesic), ctypes.POINTER(Vincenty_dist)]
destination.restype = Vincenty_dest
dat2dat.argtypes = [ctypes.POINTER(Datum), ctypes.POINTER(Datum), ctypes.POINTER(Geocentric)]
dat2dat.restype = Geocentric
npoints.argtypes = [ctypes.POINTER(Ellipsoid), ctypes.POINTER(Geodesic), ctypes.POINTER(Geodesic), ctypes.c_int]
npoints.restype = ctypes.POINTER(Vincenty_dest)
lagrange.argtypes = [ctypes.c_double, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int]
lagrange.restype = ctypes.c_double
# loading projection library
proj = ctypes.CDLL(get_data_file("proj.%s"%__dll_ext__))
for name in __c_proj__:
	exec("""
%(name)s_forward = proj.%(name)s_forward
%(name)s_forward.argtypes = [ctypes.POINTER(Crs), ctypes.POINTER(Geodesic)]
%(name)s_forward.restype = Geographic
%(name)s_inverse = proj.%(name)s_inverse
%(name)s_inverse.argtypes = [ctypes.POINTER(Crs), ctypes.POINTER(Geographic)]
%(name)s_inverse.restype = Geodesic
""" % {"name":name})
