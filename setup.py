# -*- coding:utf-8 -*-
try:
	from setuptools import setup, Extension
except ImportError:
	from distutils.core import setup, Extension
import os, sys, platform

kw = {}

bits, linkage = platform.architecture()
print(bits, linkage)

if sys.platform.startswith("win"): libext = ".dll"; opt = "-Wl,-subsystem,windows"
elif sys.platform.startswith("linux"): libext = ".so"; opt = ""
else: libext = ".lib"; opt = ""

if not(2**32//2-1 == sys.maxsize):
	libext, opt = ".64" + libext, "-fPIC -m64 " + opt
	if sys.platform.startswith("win"):
		os.environ["PATH"] += (";" if not os.environ["PATH"].endswith(";") else "") + r"C:\MinGW-w64\x86_64-5.3.0-posix-seh-rt_v4-rev0\mingw64\bin;"
elif sys.platform.startswith("win"):
	os.environ["PATH"] += (";" if not os.environ["PATH"].endswith(";") else "") + r"C:\MinGW\bin;"

if "sdist" not in sys.argv:
	if not os.path.exists("Gryd/geoid%s" % libext):
		os.system("gcc -o Gryd/geoid%s -s -shared Gryd/geoid.c %s -O3" % (libext, opt))
	if not os.path.exists("Gryd/proj%s" % libext):
		os.system("gcc -o Gryd/proj%s -s -shared Gryd/tmerc.c Gryd/merc.c Gryd/lcc.c %s -O3" % (libext, opt))


f = open("Gryd/VERSION", "r")
long_description = open("./rst/pypi.rst", "r")
kw.update(**{
	"version": f.read().strip(),
	"name": "Gryd",
	"keywords": ["epsg", "utm", "mgrs", "bng", "ing", "map", "interpolation", "projection", "great", "circle", "geohash", "georef", "GARS", "maidenhead"],
	"author": "Bruno THOORENS",
	"author_email": "bruno.thoorens@free.fr",
	"maintainer": "Bruno THOORENS",
	"maintainer_email": "bruno.thoorens@free.fr",
	"url": "http://bruno.thoorens.free.fr",
	"download_url": "https://github.com/Moustikitos/gryd",
	# "bugtrack_url": "https://github.com/Moustikitos/gryd/issues",
	"description": "Efficient great circle computation and projection library for x86 or x64 platform on Windows or Ubuntu.",
	"long_description": long_description.read(),
	"packages": ["Gryd"],
	"package_data": {"Gryd": ["VERSION", "*.html", "*.sqlite", "*.dll", "*.so"] if "sdist" not in sys.argv else \
	                         ["VERSION", "*.c", "*.h", "*.html", "*.sqlite", "rest/*.*", "test/*.*"]}, # "*%s"%libext
	"license": "Copyright 2015-2016, THOORENS Bruno, BSD licence",
	"classifiers": [
		'Development Status :: 6 - Mature',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: BSD License',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: C',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: Scientific/Engineering :: GIS',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
})
long_description.close()
f.close()

setup(**kw)
