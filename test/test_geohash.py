# -*- coding: utf-8 -*-

import Gryd

import random
import unittest


class Test(unittest.TestCase):

    def test_Geoh(self):
        longitude = -6.272877
        latitude = 53.344606
        dublin = Gryd.geohash.geoh(longitude, latitude, bits=115)
        self.assertEqual(dublin._bit_length, 115)
        lon, lat, (dlon, dlat) = Gryd.geohash.lonlat(dublin)
        self.assertAlmostEqual(longitude, lon)
        self.assertAlmostEqual(latitude, lat)

    def test_as_str(self):
        longitude = -6.272877
        latitude = 53.344606
        dublin = Gryd.geohash.geoh(longitude, latitude, bits=115)
        test = Gryd.geohash.as_int(Gryd.geohash.as_str(dublin))
        self.assertEqual(dublin, test)

    def test_custom_base(self):
        longitude = -6.272877
        latitude = 53.344606
        dublin = Gryd.geohash.geoh(longitude, latitude, bits=115)
        base = list("0123456789bcdefghjkmnpqrstuvwxyz")
        random.shuffle(base)
        base = "".join(base)
        test = Gryd.geohash.as_int(Gryd.geohash.as_str(dublin, base), base)
        self.assertEqual(dublin, test)
