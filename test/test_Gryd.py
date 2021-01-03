# -*- coding: utf-8 -*-

import Gryd

import random
import unittest


class Test(unittest.TestCase):

    def test_dms(self):
        for i in range(100):
            value = random.random() * 360.
            self.assertAlmostEqual(value, float(Gryd.dms(value)), places=10)
            self.assertAlmostEqual(-value, float(Gryd.dms(-value)), places=10)

    def test_dmm(self):
        for i in range(100):
            value = random.random() * 360.
            self.assertAlmostEqual(value, float(Gryd.dmm(value)), places=10)
            self.assertAlmostEqual(-value, float(Gryd.dmm(-value)), places=10)
