# -*- coding: utf-8 -*-

import Gryd

import os
import math
import unittest


class Test(unittest.TestCase):

    def test_base32(self):
        for i in range(100):
            self.assertEqual(len(set(Gryd.geodesy.base32(os.urandom(8)))), 32)

    def test_Geodesic_init(self):
        g1 = Gryd.Geodesic(-0.127005, 51.518602, 0.)
        g2 = Gryd.Geodesic(latitude=51.518602, longitude=-0.127005)

        self.assertEqual(g1.longitude, g2.longitude)
        self.assertEqual(g1.latitude, g2.latitude)
        self.assertEqual(g1.altitude, g2.altitude)

        self.assertEqual(math.degrees(g1.longitude), -0.127005)
        self.assertEqual(math.degrees(g1.latitude), 51.518602)
        self.assertEqual(g2.altitude, 0)

    def test_Geodesic_encrypt(self):
        dublin = Gryd.Geodesic(-6.259437, 53.350765, 0)
        test = Gryd.Geodesic.decrypt(
            dublin.encrypt(15, "secret passphrase"),
            "secret passphrase"
        )
        self.assertAlmostEqual(dublin.longitude, test.longitude)
        self.assertAlmostEqual(dublin.latitude, test.latitude)

    def test_Geodesic_geoh(self):
        dublin = Gryd.Geodesic(-6.259437, 53.350765, 0)
        test = Gryd.Geodesic.from_geohash(dublin.geohash(15))
        self.assertAlmostEqual(dublin.longitude, test.longitude)
        self.assertAlmostEqual(dublin.latitude, test.latitude)

    def test_Geodesic_maidenhead(self):
        dublin = Gryd.Geodesic(-6.259437, 53.350765, 0)
        test = Gryd.Geodesic.from_maidenhead(dublin.maidenhead(8))
        self.assertAlmostEqual(dublin.longitude, test.longitude)
        self.assertAlmostEqual(dublin.latitude, test.latitude)

    def test_Geodesic_georef(self):
        dublin = Gryd.Geodesic(-6.259437, 53.350765, 0)
        test = Gryd.Geodesic.from_georef(dublin.georef(8))
        self.assertAlmostEqual(dublin.longitude, test.longitude, places=5)
        self.assertAlmostEqual(dublin.latitude, test.latitude, places=5)

    def test_Geodesic_gars(self):
        dublin = Gryd.Geodesic(-6.259437, 53.350765, 0)
        test = Gryd.Geodesic.from_gars(dublin.gars())
        self.assertAlmostEqual(dublin.longitude, test.longitude, places=2)
        self.assertAlmostEqual(dublin.latitude, test.latitude, places=2)
