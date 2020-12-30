<a name="Gryd"></a>
# Gryd

__EPSG dataset__


All epsg dataset linked to these projections are available through python API
using epsg id or name:

 + Mercator
 + Transverse Mercator
 + Lambert Conformal Conic.
 + Oblique Mercator
 + Miller

__Grids__


Four main grids are available:

 + Universal Transverse Mercator
 + Military Grid Reference System
 + British National Grid
 + Irish National Grid.

__Image-map interpolation__


`Gryd.Crs` also provides functions for map coordinates interpolation using
calibration `Points` (two minimum are required).

__Quick view__

```python
>>> import Gryd
>>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
>>> dublin
<lon=-006Â°15'33.973" lat=+053Â°21'2.754" alt=0.000>
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

<a name="Gryd.EPSG_CON"></a>
#### EPSG\_CON

Connection to epsg database

<a name="Gryd.Geocentric"></a>
## Geocentric Objects

```python
class Geocentric(ctypes.Structure)
```

`ctypes` structure for geocentric coordinates. This reference is generaly
used as a transition for datum conversion.

**Attributes**:

- `x` _float_ - X-axis value
- `y` _float_ - Y-axis value
- `z` _float_ - Z-axis value
  
```python
>>> Gryd.Geocentric(4457584, 429216, 4526544)
<X=4457584.000 Y=429216.000 Z=4526544.000>
>>> Gryd.Geocentric(x=4457584, y=429216, z=4526544)
<X=4457584.000 Y=429216.000 Z=4526544.000>
```

<a name="Gryd.Point"></a>
## Point Objects

```python
class Point(ctypes.Structure)
```

`ctypes` structure for calibration point. It is used for coordinates
interpolation on a referenced raster image. Two points minimum are
required.

**Attributes**:

- `px` _float_ - pixel column position
- `py` _float_ - pixel row position
- `lla` _Gryd.Geodesic_ - geodesic coordinates associated to the pixel
  coordinates
- `xya` _Gryd.Geographic_ - geographic coordinates associated to the pixel
  coordinates

<a name="Gryd.Vincenty_dist"></a>
## Vincenty\_dist Objects

```python
class Vincenty_dist(ctypes.Structure)
```

Great circle distance computation result using Vincenty formulae.
`Vincenty_dist` structures are returned by `Gryd.Ellipsoid.distance`
function.

**Attributes**:

- `distance` _float_ - great circle distance in meters
- `initial_bearing` _float_ - initial bearing in degrees
- `final_bearing` _float_ - final bearing in degrees
  
```python
>>> wgs84 = Gryd.Ellipsoid(name="WGS 84") # WGS 84 ellipsoid
>>> london = Gryd.Geodesic(-0.127005, 51.518602, 0.)
>>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
>>> vdist = wgs84.distance(dublin, london)
>>> vdist
<Distance 464.025km initial bearing=113.6 final bearing=118.5>
```

<a name="Gryd.Vincenty_dest"></a>
## Vincenty\_dest Objects

```python
class Vincenty_dest(ctypes.Structure)
```

Great circle destination computation result using Vincenty formulae.
`Vincenty_dist` structures are returned by `Gryd.Ellipsoid.destination`
function.

**Attributes**:

- `longitude` _float_ - destinatin longitude in degrees
- `latitude` _float_ - destination latitude in degrees
- `destination_bearing` _float_ - destination bearing in degrees
  
```python
>>> wgs84.destination(
...     london, math.degrees(vdist.final_bearing) + 180, vdist.distance
... )
<Destination lon=-006Â°15'33.973" lat=+053Â°21'2.754" end bearing=-66.4>
>>> dublin
<lon=-006Â°15'33.973" lat=+053Â°21'2.754" alt=0.000>
```

<a name="Gryd.Dms"></a>
## Dms Objects

```python
class Dms(ctypes.Structure)
```

Degrees Minutes Seconde value of a float value. `Dms` structure are
returned by `Gryd.dms` function.

```python
>>> d = Gryd.dms(-60.42286847222222)
>>> d
-060Â°25'22.326"
>>> float(d)
-60.42286847222222
```

<a name="Gryd.Dmm"></a>
## Dmm Objects

```python
class Dmm(ctypes.Structure)
```

Degrees Minutes value of a float value. `Dmm` structure are returned by
`Gryd.dmm` function.

```python
>>> d = Gryd.dmm(-60.42286847222222)
>>> d
-060Â°25.372108'
>>> float(d)
-60.42286847222222
```

<a name="Gryd.Epsg"></a>
## Epsg Objects

```python
class Epsg(ctypes.Structure)
```

`ctypes` structure with a sqlite connection to EPSG database for
initialization purpose.

<a name="Gryd.Epsg.sqlite"></a>
#### sqlite

Shared sqlite database to be linked with

<a name="Gryd.Epsg.table"></a>
#### table

The table database name where `__init__` will find data

<a name="Gryd.Epsg.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(*args, **pairs)
```

If list of values is given as `*args`, structure members are
initialized in the order of the field definition. If `*args` only
contains one value:

 + it is a `dict` then all fields are initialized
 + it is an `int` then try to get a record from database using epsg id
 + it is a `str` then try to get a record from database using epsg name

All values in `**pairs` are merged before attributes initialization.

<a name="Gryd.Unit"></a>
## Unit Objects

```python
class Unit(Epsg)
```

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

<a name="Gryd.Prime"></a>
## Prime Objects

```python
class Prime(Epsg)
```

Prime meridian.

```python
>>> prime = Gryd.Prime(epsg=8902)
>>> prime
<Prime meridian epsg=8902 longitude=-009Â°07'54.862">
>>> prime.name
'Lisbon'
```

<a name="Gryd.Ellipsoid"></a>
## Ellipsoid Objects

```python
class Ellipsoid(Epsg)
```

```python
>>> wgs84 = Gryd.Ellipsoid("WGS 84")
>>> wgs84
<Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
```

<a name="Gryd.Ellipsoid.distance"></a>
#### distance

```python
 | distance(lla0, lla1)
```

```
>>> london = Gryd.Geodesic(-0.127005, 51.518602, 0.)
>>> dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
>>> wgs84.distance(dublin, london)
<Distance 464.025km initial bearing=113.6 final bearing=118.5>
```

<a name="Gryd.Ellipsoid.destination"></a>
#### destination

```python
 | destination(lla, bearing, distance)
```

```python
>>> wgs84.destination(
...     london, math.degrees(vdist.final_bearing)+180, vdist.distance
... )
<Destination lon=-006Â°15'33.973" lat=+053Â°21'2.754" end bearing=-66.4>
>>> dublin
<lon=-006Â°15'33.973" lat=+053Â°21'2.754" alt=0.000>
```

<a name="Gryd.Ellipsoid.npoints"></a>
#### npoints

```python
 | npoints(lla0, lla1, n)
```

```python
>>> for p in wgs84.npoints(dublin, londre, 4): print(p)
...
<Destination lon=-006Â°15'33.973" lat=+053Â°21'2.754" end bearing=113.6>
<Destination lon=-004Â°59'32.422" lat=+053Â°00'36.687" end bearing=114.6>
<Destination lon=-003Â°44'43.501" lat=+052Â°39'22.715" end bearing=115.6>
<Destination lon=-002Â°31'7.792" lat=+052Â°17'22.201" end bearing=116.6>
<Destination lon=-001Â°18'45.650" lat=+051Â°54'36.502" end bearing=117.5>
<Destination lon=-000Â°07'37.218" lat=+051Â°31'6.967" end bearing=118.5>
```

<a name="Gryd.Datum"></a>
## Datum Objects

```python
class Datum(Epsg)
```

>>> Gryd.Datum(epsg=4326)
<Datum epsg=4326:
    <Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356>
    <Prime meridian epsg=8901 longitude=0.000000>
    to wgs84: 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
>

<a name="Gryd.Datum.xyz"></a>
#### xyz

```python
 | xyz(lla)
```

```python
>>> wgs84.xyz(london)
<X=3977018.848 Y=-8815.695 Z=4969650.564>
```

<a name="Gryd.Datum.lla"></a>
#### lla

```python
 | lla(xyz)
```

```python
>>> wgs84.lla(wgs84.xyz(london))
<lon=-000Â°07'37.218" lat=+051Â°31'6.967" alt=0.000>
>>> london
<lon=-000Â°07'37.218" lat=+051Â°31'6.967" alt=0.000>
```

<a name="Gryd.Datum.transform"></a>
#### transform

```python
 | transform(dst, lla)
```

```python
>>> airy = Gryd.Datum(epsg=4277)
>>> wgs84.transform(airy, london)
<lon=-000Â°07'31.431'' lat=+051Â°31'5.137'' alt=-46.118>
```

<a name="Gryd.Crs"></a>
## Crs Objects

```python
class Crs(Epsg)
```

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
>
<Unit epsg=9001 ratio=1.0>
<Projection 'tmerc'>
>
```

<a name="Gryd.Crs.__call__"></a>
#### \_\_call\_\_

```python
 | __call__(element)
```

```python
>>> osgb36(london)  # projection of Geodesic point
<X=529939.106 Y=181680.962s alt=0.000>
>>> osgb36(osgb36(london))  # deprojection of Geographic point
<lon=-000Â°07'37.218" lat=+051Â°31'6.967" alt=0.000>
```

<a name="Gryd.Crs.transform"></a>
#### transform

```python
 | transform(dst, xya)
```

```python
>>> osgb36.transform(pvs, osgb36(london))
<X=-14317.072 Y=6680144.273s alt=-13015.770>
>>> pvs.transform(osgb36, osgb36.transform(pvs, osgb36(london)))
<X=529939.101 Y=181680.963s alt=0.012>
>>> osgb36(london)
<X=529939.106 Y=181680.962s alt=0.000>
```

<a name="Gryd.Crs.add_map_point"></a>
#### add\_map\_point

```python
 | add_map_point(px, py, point)
```

```python
>>> pvs.add_map_point(0,0, Geodesic(-179.999, 85))
>>> pvs.add_map_point(512,512, Geodesic(179.999, -85))
```

<a name="Gryd.Crs.map2crs"></a>
#### map2crs

```python
 | map2crs(px, py, geographic=False)
```

```python
>>> pvs.map2crs(256+128, 256+128)
<lon=+089Â°59'58.20'' lat=-066Â°23'43.74'' alt=0.000>
>>> pvs.map2crs(256-128, 256+128, geographic=True)
<point X=-10018698.512 Y=-9985934.440s alt=0.000>
```

<a name="Gryd.Crs.crs2map"></a>
#### crs2map

```python
 | crs2map(point)
```

```python
>>> pvs.crs2map(pvs.map2crs(256+128, 256+128))
<px=384 py=384
- <lon=+089Â°59'58.20'' lat=-066Â°23'43.74'' alt=0.000>
- <X=10018698.512 Y=-9985934.440s alt=0.000>
>
```

