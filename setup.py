# -*- coding:utf-8 -*-
import sys
from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext


class CTypes(Extension):
    pass


class build_ctypes_ext(build_ext):

    def build_extension(self, ext):
        self._ctypes = isinstance(ext, CTypes)
        return super().build_extension(ext)

    def get_export_symbols(self, ext):
        if self._ctypes:
            return ext.export_symbols
        return super().get_export_symbols(ext)

    def get_ext_filename(self, ext_name):
        if self._ctypes:
            return ext_name + (
                '.dll' if sys.platform.startswith("win") else ".so"
            )
        return super().get_ext_filename(ext_name)


f = open("./VERSION", "r")
long_description = open("./README.md", "r")

kw = {
    "version": f.read().strip(),
    "name": "Gryd",
    "keywords": [
        "epsg", "utm", "mgrs", "bng", "ing", "map", "interpolation",
        "projection", "great", "circle", "geohash", "georef", "GARS",
        "maidenhead"
    ],
    "author": "Bruno THOORENS",
    "author_email": "moustikitos@gmail.com",
    "maintainer": "Bruno THOORENS",
    "maintainer_email": "moustikitos@gmail.com",
    "url": "https://moustikitos.github.io/gryd/",
    "download_url": "https://github.com/Moustikitos/gryd",
    "description":
        "Efficient great circle computation and projection library for x86"
        " or x64 platform on Windows or Ubuntu.",
    "long_description": long_description.read(),
    "long_description_content_type": "text/markdown",
    "packages": ["Gryd"],
    "include_package_data": True,
    "ext_modules": [
        CTypes(
            'Gryd.geoid',
            extra_compile_args=[],
            include_dirs=['src/'],
            sources=[
                "src/geoid.c"
            ]
        ),
        CTypes(
            'Gryd.proj',
            extra_compile_args=[],
            include_dirs=['src/'],
            sources=[
                "src/tmerc.c",
                "src/miller.c",
                "src/eqc.c",
                "src/merc.c",
                "src/lcc.c"
            ]
        )
    ],
    "cmdclass": {"build_ext": build_ctypes_ext},
    "license": "Copyright 2015-2021, THOORENS Bruno, BSD licence",
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
}

long_description.close()
f.close()

setup(**kw)
