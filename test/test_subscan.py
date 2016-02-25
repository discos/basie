#coding=utf-8

import unittest2 as unittest

from basie import frame, target_parser
from basie.scanmode import subscan
from basie.valid_angles import VAngle


class TestSubscan(unittest.TestCase):
    def setUp(self):
        LINE = "3C386 otfmap1 TP EQ 10.0d 1:00:00.0h"
        self.SCANTYPE, self.BACKEND, self.TARGET = target_parser._parse_target_line(LINE)
        self.DELTA = 1e-10 #we tolerate angles rounding errors

    def test_get_tsys(self):
        offset_lon = VAngle(0.5)
        offset_lat = VAngle(0.5)
        offset_coord = frame.Coord(frame.EQ, offset_lon , offset_lat)
        tsys_offset = frame.Coord(frame.EQ, VAngle(0.5 + 0.1), VAngle(0.5))
        _ss = subscan.get_tsys(self.TARGET, tsys_offset)
        self.assertEqual(_ss.target.label, "Tsys")
        self.assertAlmostEqual(_ss.target.offset_coord.lon.deg,
                               tsys_offset.lon.deg,
                              delta=self.DELTA)
        self.assertAlmostEqual(_ss.target.offset_coord.lat.deg,
                               tsys_offset.lat.deg,
                               delta=self.DELTA)
        self.assertAlmostEqual(_ss.target.offset_coord.lon.deg,
                         tsys_offset.lon.deg, delta=self.DELTA)

    def test_get_cen_otf(self):
        duration = 10.0
        length = VAngle(3.0)
        offset = VAngle(0.2)
        const_axis = "LON"
        direction = "INC"
        scan_frame = frame.EQ
        _ss = subscan.get_cen_otf(
                                  self.TARGET,
                                  duration,
                                  length,
                                  offset,
                                  const_axis,
                                  direction,
                                  scan_frame,
                                 )
        self.assertAlmostEqual(_ss.lat2.deg, length.deg, delta=self.DELTA)
        self.assertAlmostEqual(_ss.lon2.deg, VAngle(0.0).deg, delta=self.DELTA)
        self.assertAlmostEqual(_ss.target.offset_coord.lon.deg,
                               offset.deg, delta=self.DELTA)



