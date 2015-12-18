#coding=utf-8

import unittest

from basie import utils
from basie.valid_angles import VAngle


class TestUtils(unittest.TestCase):
    def test_ceil_to_odd(self):
        self.assertEqual(utils.ceil_to_odd(4.2), 5)
        self.assertEqual(utils.ceil_to_odd(3.2), 5)
        self.assertEqual(utils.ceil_to_odd(-4.2), -3)

    def test_extrude_from_rectangle(self):
        extremes = [(0,0), (5,0), (5,3), (0,3)]
        x = 1
        y = 0
        _x, _y = utils.extrude_from_rectangle(x, y, extremes, 10)
        self.assertEqual(_x, 1)
        self.assertEqual(_y, -10)

    def test_ceil_to_odd_valid_angle(self):
        a = VAngle(4.2)
        b = utils.ceil_to_odd(a)
        self.assertEqual(a.original_unit, b.original_unit)
        self.assertEqual(a.sexa, b.sexa)
        self.assertEqual(b.deg, 5)
        a = VAngle(5.2)
        b = utils.ceil_to_odd(a)
        self.assertEqual(b.deg, 7)


