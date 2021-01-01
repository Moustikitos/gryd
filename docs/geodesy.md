<a name="Gryd.geodesy"></a>
# Gryd.geodesy

<a name="Gryd.geodesy.base32"></a>
#### base32

```python
base32(secret)
```

Return a 32-length of unique bytes from secret hash.

<a name="Gryd.geodesy.Geodesic"></a>
## Geodesic Objects

```python
class Geodesic(ctypes.Structure)
```

`ctypes` structure for geodesic coordinates

**Attributes**:

- `longitude` _float_ - longitude value of geodesic coordinates in degrees
- `latitude` _float_ - latitude value of geodesic coordinates in degrees
- `altitude` _float_ - elevation of the geodesic coordinates in meters
  
```python
>>> dublin = Gryd.Geodesic(-6.272877, 53.344606, 105.)
>>> dublin
<lon=-006°16'22.357" lat=+053°20'40.582" alt=105.000>
```

<a name="Gryd.geodesy.Geodesic.encrypt"></a>
#### encrypt

```python
 | encrypt(digit, secret)
```

Encrypt geodesic coordinates. It uses geohash with a custom
32-length base initialized by `Gryd.geodesy.base32`.


```python
>>> g = Gryd.geodesy.Geodesic(-5.412300, 45.632100)
>>> g.encrypt(23, "secret")
b'\xbda\xe0\xa3\xe9\xbd\x1d\x86\xe0_a1\x8bV2\xe0aV\xbd2\xcd\xe0\xe0'
```

**Arguments**:

- `digit` _int_ - result bytes-length
- `secret` _bytes or str_ - secret used to encrypt geodesic coordinates

**Returns**:

  `bytes` data

<a name="Gryd.geodesy.Geodesic.decrypt"></a>
#### decrypt

```python
 | @staticmethod
 | decrypt(encrypted, secret)
```

Decrypt geodesic from encrypted. It uses geohash with a custem
32-length base initialized by `Gryd.geodesy.base32`.


```python
>>> enc = b'\xbda\xe0\xa3\xe9\xbd\x1d\x86\xe0_a1\x8bV2\xe0aV\xbd2\xcd'\
...       b'\xe0\xe0'
>>> geo.Geodesic.decrypt(enc, "secret")
<lon=-5.412300 lat=45.632100 alt=0.000>
```

**Arguments**:

- `encrypted` _bytes_ - encrypted geodesic coordinates
- `secret` _bytes or str_ - secret used to encrypt geodesic coordinates

**Returns**:

  `Gryd.geodesy.Geodesic` coordinates

<a name="Gryd.geodesy.Geodesic.geohash"></a>
#### geohash

```python
 | geohash(digit=10)
```

Convert coordinates to geohash.


```python
>>> dublin.geohash() # by default on 10 digit for metric precision
'gc7x3r04z7'
>>> dublin.geohash(14) # why not on 14 digit for millimetric precision
'gc7x3r04z77csw'
```

**Arguments**:

- `digit` _int_ - total digit to use in the geohash

**Returns**:

  Geohash `str`

<a name="Gryd.geodesy.Geodesic.from_geohash"></a>
#### from\_geohash

```python
 | @staticmethod
 | from_geohash(geoh)
```

Return Geodesic object geohash.


```python
>>> Gryd.Geodesic.from_geohash('gc7x3r04z7')
<lon=-006°16'22.347" lat=+053°20'40.590" alt=0.000>
>>> Gryd.Geodesic.from_geohash('gc7x3r04z77csw')
<lon=-006°16'22.357" lat=+053°20'40.582" alt=0.000>
```

**Arguments**:

- `geoh` _str_ - georef string

**Returns**:

  `Gryd.geodesy.Geodesic` coordinates

<a name="Gryd.geodesy.Geodesic.maidenhead"></a>
#### maidenhead

```python
 | maidenhead(level=4)
```

Convert coordinates to maidenhead.


```python
>>> dublin.maidenhead()
'IO63ui72gq'
>>> dublin.maidenhead(level=6)
'IO63ui72gq19dh'
```

**Arguments**:

- `level` _int_ - precision level of maidenhead

**Returns**:

  Maidenhead `str`

<a name="Gryd.geodesy.Geodesic.from_maidenhead"></a>
#### from\_maidenhead

```python
 | @staticmethod
 | from_maidenhead(maidenhead)
```

Return Geodesic object from maidenhead string.

**Arguments**:

- `maidenhead` _str_ - maidenhead string

**Returns**:

  `Gryd.geodesy.Geodesic` coordinates

<a name="Gryd.geodesy.Geodesic.georef"></a>
#### georef

```python
 | georef(digit=8)
```

Convert coordinates to georef.


```python
>>> dublin.georef()
'MKJJ43322037'
>>> dublin.georef(digit=6)
'MKJJ433203'
```

**Arguments**:

- `digit` _int_ - digit number of georef (can be 4, 6 or 8)

**Returns**:

  Georef `str`

<a name="Gryd.geodesy.Geodesic.from_georef"></a>
#### from\_georef

```python
 | @staticmethod
 | from_georef(georef)
```

Return Geodesic object from georef.


```python
>>> Gryd.Geodesic.from_georef('MKJJ43322037')
<lon=-006°16'21.900" lat=+053°20'41.100" alt=0.000>
>>> Gryd.Geodesic.from_georef('MKJJ433220')    
<lon=-006°15'57.000" lat=+053°22'45.000" alt=0.000>
```

**Arguments**:

- `georef` _str_ - georef string

**Returns**:

  `Gryd.geodesy.Geodesic` coordinates

<a name="Gryd.geodesy.Geodesic.gars"></a>
#### gars

```python
 | gars()
```

Get the associated GARS Area (5minx5min tile).

```python
>>> dublin.gars()
'348MY16'
```

<a name="Gryd.geodesy.Geodesic.from_gars"></a>
#### from\_gars

```python
 | @staticmethod
 | from_gars(gars, anchor="")
```

Return Geodesic object from gars. Optional anchor value to define
where to handle 5minx5min tile.


```python
>>> Gryd.Geodesic.from_gars('348MY16', anchor="nw")
<lon=-006°20'0.000" lat=+053°25'0.000" alt=0.000>
>>> Gryd.Geodesic.from_gars('348MY16')
<lon=-006°17'30.000" lat=+053°22'30.000" alt=0.000>
```

**Arguments**:

- `gars` _str_ - gars string
- `anchor` _str_ - tile anchor (nesw)

**Returns**:

  `Gryd.geodesy.Geodesic` coordinates

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

