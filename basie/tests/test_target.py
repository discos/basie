#coding=utf-8

import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from basie import target_parser
from basie import frame
from basie.valid_angles import VAngle

LINE = "3C386 otfmap1 TP EQ 10.0d 1:00:00.0h repetitions=3 tsys=4 offset_lon=0.0d offset_lat=0.3d offset_frame=eq"
# TARGETS_PATH = "basie/user_templates/targets.txt"
curdir = os.path.abspath(os.path.dirname(__file__))
TARGETS_PATH = os.path.join(curdir, "..", "user_templates", "targets.txt")

class TestTarget(unittest.TestCase):
    def test_parse_line(self):
        _scantype, _backend, _target = target_parser._parse_target_line(LINE)
        self.assertEqual(_scantype, "otfmap1")
        self.assertEqual(_target.label, "3C386")
        #self.assertEqual(_target.coord, frame.Coord(frame.EQ, 10.0, 15.0))
        self.assertEqual(_target.repetitions, 3)
        self.assertEqual(_target.tsys, 4)
        self.assertEqual(_target.offset_coord, frame.Coord(frame.EQ, 0.0, 0.3))

    def test_parse_file(self):
        targets = target_parser.parse_file(TARGETS_PATH)
        self.assertNotEqual(targets, [])
        t_zero, scan_zero, _, _ = targets[0]
        self.assertEqual(t_zero.label, "Alpha")
        self.assertEqual(scan_zero, "EqCross1_3")
        self.assertEqual(t_zero.coord.lon.fmt(), "12:00:00.0000h")
        t_gamma, _, _, _= targets[8]
        self.assertEqual(t_gamma.tsys, 2)
        self.assertEqual(t_gamma.repetitions, 4)
        t_offset, _, _, _ = targets[9]
        self.assertEqual(t_offset.offset_coord.lon, VAngle(-0.5))

    def test_parse_file_negative_coord(self):
        targets = target_parser.parse_file(TARGETS_PATH)
        self.assertNotEqual(targets, [])
        t_zero, scan_zero, _, _ = targets[2]
        self.assertEqual(t_zero.label, "Alpha")
        self.assertEqual(scan_zero, "DownSkydip")
        self.assertEqual(t_zero.coord.lon.fmt(), "00:03:00.0000h")
        self.assertEqual(t_zero.coord.lat.fmt(), "-00:00:03.0000")
        t_zero, scan_zero, _, _ = targets[3]
        self.assertEqual(t_zero.coord.lon.fmt(), "00:00:02.0000h")
        self.assertEqual(t_zero.coord.lat.fmt(), "-00:03:00.0000")


if __name__ == "__main__":
    unittest.main()

