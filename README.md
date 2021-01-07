# Gryd

[![pypi](https://img.shields.io/pypi/l/Gryd.svg)](https://htmlpreview.github.io/?https://github.com/Moustikitos/gryd/blob/master/gryd.html)

[![pypi](https://img.shields.io/pypi/pyversions/Gryd.svg)](https://pypi.python.org/pypi/Gryd)
[![pypi](https://img.shields.io/pypi/v/Gryd.svg)](https://pypi.python.org/pypi/Gryd)
[![Downloads](https://pepy.tech/badge/gryd/week)](https://pepy.tech/project/gryd)

### Support this project
 + Patron me directly:
   * [X] [![Liberapay receiving](https://img.shields.io/liberapay/receives/Toons)](https://liberapay.com/Toons/donate)
 + [Buy &#1126;](https://bittrex.com/Account/Register?referralCode=NW5-DQO-QMT) and:
   * [X] Send &#1126; to `AUahWfkfr5J4tYakugRbfow7RWVTK35GPW`
   * [X] Vote `arky` on [Ark blockchain](https://explorer.ark.io) and [earn &#1126; weekly](http://arky-delegate.info/arky)

## Why this package ?
`Gryd` package provides efficient great circle computation and projection library.
It is lightweight (less than 500Ko) and does not rely on third party dependencies.

## Documentation
[The Gryd Project [WIP]](https://moustikitos.github.io/gryd/)

## Installation

### from source distribution
```bash
$ python setup.py install
```

### from pip
```bash
$ python -m pip install Gryd
```

## Contribute
### Bug report & feedback
Use project issues.

### Add / modify / fix code
Guidance words: keep it simple and solid!

1. open a issue to propose your contribution
2. once issue is granted
    + fork this repository
    + edit your contribution
    + start a pull request

## History

### 2.0.0
 + documentation API change
 + binary source released
 + code improvement
 + dump location api change

```python
>>> import Gryd
>>> dublin = Gryd.Geodesic(-6.272877, 53.344606, 105.)
>>> # mapbox static map api url
>>> url = "https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/static/"\
...       "pin-s+f74e4e(%(lon)f,%(lat)f)/%(lon)f,%(lat)f,%(zoom)d,0/"\
...       "%(width)dx%(height)d?access_token=%(token)s"
>>> # see https://docs.mapbox.com/api/overview/#access-tokens-and-token-scopes
>>> token = "pk.eyJ1IjoibW91c2lr[...]nJtcHlyejFrNXd4In0.JIyrV6sWjehsRHKVMBDFaw"
>>> dublin.dump_location("test/dublin.png", url, zoom=15, width=300, height=200, token=token)
```

![Here is Dublin](https://raw.githubusercontent.com/Moustikitos/gryd/master/test/dublin.png)

 + `geohash` module improvement
   * implementation based on python integers
   * better encryption interface

### 1.2.0
 + added `geohash` module

### 1.1.1
 + `Geodesic` class can now dump thumbanil location from google staticmap API
 + bugfix in unit usage for classic projection (other than grid)

### 1.1.0
 + projection core changes (simpler & faster)
 + added ``miller`` and ``eqc`` projection
 + 64 bit support for Windows
 + encrypt/decrypt geodesic coordinates

```python
>>> point = Gryd.Geodesic(-6.23, 53.63)
>>> point.encrypt("your encryption key")
'mwszncbe9g2tu29'
>>> Gryd.decrypt('mwszncbe9g2tu29', key="hacking...") # gives coordinates but not the good ones
Geodesic point lon=+025°22'0.011'' lat=-086°36'35.290'' alt=0.000
>>> Gryd.decrypt('mwszncbe9g2tu29', key="your encryption key")
Geodesic point lon=-006°13'48.000'' lat=+053°37'48.000'' alt=0.000
>>> point
Geodesic point lon=-006°13'48.000'' lat=+053°37'48.000'' alt=0.000
```

### 1.0.11
 + bugfix for `mgrs.inverse` function
 + `utm` and `mgrs` grid tweaks

### 1.0.10
 + `Gryd.Geodesic` exports itself in `geohash`, `maidenhead`, `georef` and `gars`
 + `Gryd.Geodesic` created from `geohash`, `maidenhead`, `georef` and `gars`

### 1.0.9
 + `bng` and `ing` grid tweaks

### 1.0.8
 + bugfix for `utm` and `mgrs` grid computation
 + `Crs.unit` value is now used in computation

### 1.0.7
 + Provide a multiplatform wheel (32 and 64 bit for Windows and Ubuntu)
 + Python sources released

### 1.0.6
 + Added API doc

### 1.0.5
 + All `Gryd` objects are pickle-able

```python
>>> import pickle
>>> data = pickle.dumps(wgs84)
>>> data
b'\x80\x03c_ctypes\n_unpickle\nq\x00cGryd\nEllipsoid\nq\x01}q\x02X\x04\x00\x00\x00nameq\x03X\x06\x00\x00\x00WGS 84q\x04sC(v\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00@\xa6TXA\xd0\x97\x1c\x14\xc4?XA\x9a\xaf\xda<\x1a\xf2\xb4?(\xe1\xf3\x84Zwk?q\x05\x86q\x06\x86q\x07Rq\x08.'
>>> pickle.loads(data)
Ellispoid epsg=7030 a=6378137.000000 1/f=298.25722356
```

### 1.0.4
 + bugfix `Gryd.Vincenty_dest` representation
 + wheel distribution fix

### 1.0.3
+ linux (ubuntu) fix

### 1.0.2
 + `Gryd.Geodesic` class takes degrees arguments for longitude and latitude values
 + better objects representation
 + speed improvement
 + added `__float__` operator for `Gryd.Dms` and `Gryd.Dmm` objects

```python
>>> float(Gryd.Dms(1, 5, 45, 23))
5.756388888888889
>>> "%.6f" % Gryd.Dms(-1, 5, 45, 23)
'-5.756389'
```

### 1.0.1
 + minor changes in C extensions
 + bugfix `geoid.dms` and `geoid.dmm` function

### 1.0.0
 + first public binary release (`win32` and `linux` platform)
