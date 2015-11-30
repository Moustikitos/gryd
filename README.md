<img src="http://bruno.thoorens.free.fr/img/gryd.png" height="100px" />

# `Gryd`
[![pypi](https://img.shields.io/pypi/l/Gryd.svg?style=flat-square)](http://bruno.thoorens.free.fr/licences/gryd.html)

[![pypi](https://img.shields.io/pypi/pyversions/Gryd.svg?style=flat-square)](https://pypi.python.org/pypi/Gryd)

[![pypi](https://img.shields.io/pypi/v/Gryd.svg?style=flat-square)](https://pypi.python.org/pypi/Gryd)
[![pypi](https://img.shields.io/pypi/dm/Gryd.svg?style=flat-square)](https://pypi.python.org/pypi/Gryd)
[![pypi](https://img.shields.io/badge/wheel-yes-brightgreen.svg?style=flat-square)](https://pypi.python.org/pypi/Gryd)

[<img src="https://assets.gratipay.com/gratipay.svg?etag=3tGiSB5Uw_0-oWiLLxAqpQ~~" />](https://gratipay.com/Gryd)

## Why this package ?
`Gryd` package provides efficient great circle computation and projection library.

### Vincenty formulae
They are two related iterative methods used in geodesy to calculate
the distance between two points on the surface of a spheroid.

### EPSG dataset
All epsg dataset linked to these projections are available through
python API using epsg id or name. Available projections are Mercator,
Transverse Mercator and Lambert Conformal Conic. 

### Grid
The four main grids are available : Universal Transverse Mercator,
Military Grid Reference System, British National Grid and Irish
National Grid.

### Image-map interpolation

`Gryd.Crs` class also provides functions for map coordinates
interpolation using calibration points. Two points minimum are
required.

### API Doc
http://bruno.thoorens.free.fr/gryd/doc/index.html

## Contributing
### Bug report & feedback
Use project issues.

### Add / modify / fix code
1. open a issue to propose your contribution
2. once issue is granted
  + fork this repository
  + edit your contribution
  + start a pull request

## TODO
+ implement oblique mercator
+ implement epsg database maintainer
