# -*- coding: utf-8 -*-

import Gryd

import math
import random
import unittest


class Test(unittest.TestCase):

    def test_dms(self):
        for i in range(100):
            value = random.random() * 360.
            # precision +/- 0.31 mm on WGS 84 equator
            self.assertAlmostEqual(value, float(Gryd.dms(value)), places=10)
            self.assertAlmostEqual(-value, float(Gryd.dms(-value)), places=10)

    def test_dmm(self):
        for i in range(100):
            value = random.random() * 360.
            # precision +/- 0.31 mm on WGS 84 equator
            self.assertAlmostEqual(value, float(Gryd.dmm(value)), places=10)
            self.assertAlmostEqual(-value, float(Gryd.dmm(-value)), places=10)

    def test_Vincenty(self):
        wgs84 = Gryd.Ellipsoid("WGS 84")
        dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
        london = Gryd.Geodesic(-0.127005, 51.518602, 0.)
        vdist = wgs84.distance(dublin, london)
        vdest = wgs84.destination(
            london, math.degrees(vdist.final_bearing) + 180, vdist.distance
        )
        # precision +/- 3.1 cm on WGS 84 equator
        self.assertAlmostEqual(vdest.longitude, dublin.longitude, places=8)
        self.assertAlmostEqual(vdest.latitude, dublin.latitude, places=8)

    def test_Geodetics(self):
        wgs84 = Gryd.Datum("WGS 84")
        airy = Gryd.Datum(epsg=4277)
        dublin = Gryd.Geodesic(-6.259437, 53.350765, 0.)
        dubl_2 = wgs84.lla(wgs84.xyz(dublin))
        dubl_3 = airy.transform(wgs84, wgs84.transform(airy, dublin))
        # precision +/- 3.1 cm on WGS 84 equator
        self.assertAlmostEqual(dublin.longitude, dubl_2.longitude, places=8)
        self.assertAlmostEqual(dublin.latitude, dubl_2.latitude, places=8)
        self.assertAlmostEqual(dublin.longitude, dubl_3.longitude, places=8)
        self.assertAlmostEqual(dublin.latitude, dubl_3.latitude, places=8)
