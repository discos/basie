#coding=utf-8

import unittest

from basie import utils

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

