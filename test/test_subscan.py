#coding=utf-8

import unittest

from schedulecreator import frame, target_parser
from schedulecreator.scanmode import subscan
from schedulecreator.valid_angles import VAngle

SCANTYPE, TARGET, = target_parser._parse_target_line("3C386 otfmap1 EQ 1:00:00.0h 10:00:00 offset_frame=eq offset_lon=0.1d offset_lat=0.0d") 
DELTA = 1e-10 #we tolerate angles rounding errors

class TestSubscan(unittest.TestCase):
    def test_get_tsys(self):
        offset_lon = VAngle(0.5)
        offset_lat = VAngle(0.5)
        offset_coord = frame.Coord(frame.EQ, offset_lon , offset_lat)
        tsys_offset = frame.Coord(frame.EQ, VAngle(0.5 + 0.1), VAngle(0.5))
        _ss = subscan.get_tsys(TARGET, offset_lon, offset_lat)
        self.assertEqual(_ss.target.label, "Tsys")
        self.assertAlmostEqual(_ss.target.offset_coord.lon.deg,
                               tsys_offset.lon.deg,
                              delta=DELTA)
        self.assertAlmostEqual(_ss.target.offset_coord.lat.deg,
                               tsys_offset.lat.deg,
                               delta=DELTA)
        self.assertAlmostEqual(_ss.target.offset_coord.lon.deg,
                         tsys_offset.lon.deg, delta=DELTA)
        self.assertAlmostEqual(TARGET.offset_coord.lon.deg, 0.1, delta=DELTA)

    def test_get_cen_otf(self):
        duration = 10.0
        length = VAngle(3.0)
        offset = VAngle(0.2)
        const_axis = "LON"
        offset_coord = frame.Coord(frame.EQ, VAngle(0.3), VAngle(0.0))
        direction = "INC"
        scan_frame = frame.EQ
        _ss = subscan.get_cen_otf(
                                  TARGET,
                                  duration,
                                  length,
                                  offset,
                                  const_axis,
                                  direction,
                                  scan_frame,
                                 )
        self.assertAlmostEqual(_ss.lat2.deg, length.deg, delta=DELTA)
        self.assertAlmostEqual(_ss.lon2.deg, VAngle(0.0).deg, delta=DELTA)
        self.assertAlmostEqual(_ss.target.offset_coord.lon.deg,
                               offset_coord.lon.deg, delta=DELTA)



