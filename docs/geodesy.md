<a name="Gryd.geodesy"></a>
# Gryd.geodesy

<a name="Gryd.geodesy.Geodesic"></a>
## Geodesic Objects

```python
class Geodesic(ctypes.Structure)
```

`ctypes` structure for geodesic coordinates

**Attributes**:

  + longitude
  + latitude
  + altitude
  
```python
>>> dublin = Gryd.Geodesic(-6.272877, 53.344606, 0.)
>>> dublin
>>> Gryd.Geodesic(45.5, 5.5, 105)
```

<a name="Gryd.geodesy.Geodesic.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(*args, **kwargs)
```

Angular value must be given in degree here (more human values).

<a name="Gryd.geodesy.Geodesic.Geohash"></a>
#### Geohash

```python
 | Geohash(digit=10, base="0123456789bcdefghjkmnpqrstuvwxyz")
```

Convert coordinates to geohash.
>>> dublin.Geohash() # by default on 10 digit for metric precision
gc7x3r04z7
>>> dublin.Geohash(14) # why not on 14 digit for millimetric precision
gc7x3r04z77csw

<a name="Gryd.geodesy.Geodesic.Maidenhead"></a>
#### Maidenhead

```python
 | Maidenhead(level=4)
```

Convert coordinates to maidenhead.
>>> dublin.Maidenhead()
'IO63ui72gq'
>>> dublin.Maidenhead(level=6)
'IO63ui72gq19dh'

<a name="Gryd.geodesy.Geodesic.Georef"></a>
#### Georef

```python
 | Georef(digit=8)
```

Convert coordinates to georef.
>>> dublin.Georef()
'MKJJ43322037'
>>> dublin.Georef(digit=6)
'MKJJ433203'

<a name="Gryd.geodesy.Geodesic.Gars"></a>
#### Gars

```python
 | Gars()
```

Get the associated GARS Area.
>>> dublin.Gars()
'348MY16'

<a name="Gryd.geodesy.from_geohash"></a>
#### from\_geohash

```python
from_geohash(geohash, base="0123456789bcdefghjkmnpqrstuvwxyz")
```

return Geodesic object from geohash

<a name="Gryd.geodesy.from_maidenhead"></a>
#### from\_maidenhead

```python
from_maidenhead(maidenhead)
```

Return Geodesic object from maidenhead.

<a name="Gryd.geodesy.from_georef"></a>
#### from\_georef

```python
from_georef(georef)
```

Return Geodesic object from georef.

<a name="Gryd.geodesy.from_gars"></a>
#### from\_gars

```python
from_gars(gars, anchor="")
```

Return Geodesic object from gars. Optional anchor value to define where to
handle 5minx5min tile.

<a name="Gryd.geohash"></a>
# Gryd.geohash

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

<a name="Gryd.geohash.EARTH_RADIUS"></a>
#### EARTH\_RADIUS

Popular Visualisation Spheroid radius (epsg `7059` ellipsoid)

<a name="Gryd.geohash.GeoH"></a>
## GeoH Objects

```python
class GeoH(int)
```

Integer that keeps info about leading zero bits.

<a name="Gryd.geohash.GeoH.precision"></a>
#### precision

```python
 | precision()
```

Return metter precision tuple for longitude and latitude based on
Popular Visualisation Spheroid radius (epsg `7059` ellipsoid).

<a name="Gryd.geohash.geoh"></a>
#### geoh

```python
geoh(lon, lat, bits=25)
```

Return a python integer representing geohashed coordinates longitude and
latitude with a given precision.

**Arguments**:

- `lon` _float_ - longitude
- `lat` _float_ - latitude
- `bits` _int_ - length of the geohash in bit

**Returns**:

  `Gryd.geohash.GeoH`

<a name="Gryd.geohash.lonlat"></a>
#### lonlat

```python
lonlat(value, centered=False)
```

Return longitude and latitude and precision from a geohash integer.

**Arguments**:

- `value` _Gryd.geohash.GeoH or int_ - geohash value
- `centered` _bool_ - returns bottom-left corner (if `False`) or center (if
  `True`) of geohash surface

**Returns**:

  longitude, latitude and precision as (dlon, dlat) tuple

<a name="Gryd.geohash.to_geohash"></a>
#### to\_geohash

backward compatibility

<a name="Gryd.geohash.from_geohash"></a>
#### from\_geohash

backward compatibility

