# -*- coding:utf-8 -*-
try:
	from setuptools import setup, Extension
	from bindist import wheel
	kw = {"cmdclass":{'bindist_wheel':wheel}}
except ImportError:
	from distutils.core import setup, Extension
	kw = {}

from wheel.pep425tags import get_abbr_impl, get_impl_ver
from distutils.util import get_platform
import os, sys

# if "bindist_wheel" in sys.argv:
# 	idx = sys.argv.index("bindist_wheel")
# 	sys.argv.insert(idx+1, "--python-tag=%s" % get_abbr_impl()+get_impl_ver())
# 	sys.argv.insert(idx+1, "--plat-name=%s" % get_platform())

if sys.platform.startswith("win"): libext = ".dll"; opt = "-Wl,-subsystem,windows"
elif sys.platform.startswith("linux"): libext = ".so"; opt = ""
else: libext = ".lib"
if not(2**32//2-1 == sys.maxsize): libext, opt = ".64" + libext, "-fPIC " + opt

os.environ["PATH"] += (";" if not os.environ["PATH"].endswith(";") else "") + r"C:\MinGW\bin;"

if "sdist" not in sys.argv:
	if not os.path.exists("Gryd/geoid%s" % libext):
		os.system("gcc -o Gryd/geoid%s -s -shared Gryd/geoid.c %s -O3" % (libext, opt))
	if not os.path.exists("Gryd/proj%s" % libext):
		os.system("gcc -o Gryd/proj%s -s -shared Gryd/tmerc.c Gryd/merc.c Gryd/lcc.c %s -O3" % (libext, opt))


f = open("Gryd/VERSION", "r")
long_description = open("./Gryd/rest/pypi.rst", "r")
kw.update(**{
	"version": f.read().strip(),
	"name": "Gryd",
	"keywords": ["epsg", "utm", "mgrs", "bng", "ing", "map", "interpolation", "projection", "great", "circle"],
	"author": "THOORENS Bruno",
	"author_email": "bruno.thoorens@free.fr",
	"home_page": "http://bruno.thoorens.free.fr",
	"description": "Efficient great circle computation and projection library for x86 or x64 platform on Windows or Ubuntu.",
	"long_description": long_description.read(),
	"packages": ["Gryd"],
	"package_data": {"Gryd": ["VERSION", "*.html", "*.sqlite", "*.dll", "*.so"] if "sdist" not in sys.argv else \
	                         ["VERSION", "*.c", "*.h", "*.html", "*.sqlite", "rest/*.*", "test/*.*"]}, # "*%s"%libext
	"license": "Copyright 2015, THOORENS Bruno, BSD licence",
	"classifiers": [
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: BSD License',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: Scientific/Engineering :: GIS',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
})
long_description.close()
f.close()

setup(**kw)
