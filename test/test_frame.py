#coding=utf-8

import unittest
import copy
from astropy.coordinates import Angle
from astropy import units as u

from basie import frame
from basie import valid_angles as va

class TestFrame(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(frame.EQ, frame.frames["EQ"])

class TestCoord(unittest.TestCase):
    def test_equality(self):
        c = frame.Coord(frame.EQ, 10, 20)
        d = frame.Coord(frame.EQ, 10, 20)
        e = frame.Coord(frame.EQ, 5.0 + 5.0, 10.0 + 10.0)
        f = frame.Coord(frame.EQ, va.VAngle(10.0),
                        va.VAngle(20.0))
        self.assertEqual(c, d)
        self.assertEqual(c, e)
        self.assertEqual(c, f)
        self.assertEqual(e, f)

    def test_constructor(self):
        c = frame.Coord(frame.EQ, 5.0, 6.0)
        self.assertEqual(c.lon.deg, Angle(5.0, u.deg).deg)

    def test_copy(self):
        c = frame.Coord(frame.EQ, 5.0, 6.0)
        d = copy.deepcopy(c)
        self.assertEqual(c, d)
        d.lon = va.VAngle(10.0)
        self.assertEqual(c.lon.deg, Angle(5.0, u.deg).deg)
        self.assertEqual(d.lon.deg, Angle(10.0, u.deg).deg)

if __name__ == "__main__":
    unittest.main()
