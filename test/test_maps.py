#coding=utf-8
from __future__ import print_function, division
from builtins import range
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from basie.frame import EQ, HOR
from astropy.units import MHz
from basie.radiotelescopes import SRT
from basie.scanmode import subscan, maps
from basie.valid_angles import VAngle
from basie.receiver import Receiver

class TestMapScan(unittest.TestCase):

    def setUp(self):
        self._recv = Receiver("TEST", 0, 100,
                             [[0.0, 100.0], [5.0, 5.0]],
                             nfeed = 7,
                             npols = 2,
                             has_derotator = True)
        self._recv.feed_extent = VAngle(30)
        self._recv.interleave = VAngle(10)
        self._srecv = Receiver("TEST", 0, 100,
                             [[0.0, 100.0], [5.0, 5.0]],
                             nfeed = 1,
                             npols = 2,
                             has_derotator = False)
        self._length_x = VAngle(150)
        self._length_y = VAngle(150)
        self._spacing = VAngle(1)
        self._scans_per_beam = 5
        self._scan_fixed = maps.MapScan(EQ, "TL", "LON",
                                        self._length_x,
                                        self._length_y,
                                        self._spacing)
        self._scan_dynamic = maps.MapScan(EQ, "TL", "LON",
                                        self._length_x,
                                        self._length_y,
                                        self._scans_per_beam)

    def test_single_feed_fixed_spacing(self):
        self._scan_fixed._get_spacing(self._srecv, [18 * MHz])
        scan_length_x = self._scan_fixed.offset_x[-1] - \
                        self._scan_fixed.offset_x[0]
        scan_length_y = self._scan_fixed.offset_y[-1] - \
                        self._scan_fixed.offset_y[0]
        self.assertGreaterEqual(scan_length_x, self._length_x)
        self.assertGreaterEqual(scan_length_y, self._length_y)
        for i in range(len(self._scan_fixed.offset_x) - 1):
            self.assertAlmostEqual(self._spacing.deg,
                                   self._scan_fixed.offset_x[i+1].deg -\
                                   self._scan_fixed.offset_x[i].deg)
        for i in range(len(self._scan_fixed.offset_y) - 1):
            self.assertAlmostEqual(self._spacing.deg,
                                   self._scan_fixed.offset_y[i+1].deg -\
                                   self._scan_fixed.offset_y[i].deg)

    def test_multi_feed_fixed_spacing(self):
        self._scan_fixed._get_spacing(self._recv, [18 * MHz])
        scan_length_x = self._scan_fixed.offset_x[-1] - \
                        self._scan_fixed.offset_x[0]
        scan_length_y = self._scan_fixed.offset_y[-1] - \
                        self._scan_fixed.offset_y[0]
        self.assertGreaterEqual(scan_length_x + self._recv.feed_extent * 2, self._length_x)
        self.assertGreaterEqual(scan_length_y + self._recv.feed_extent * 2, self._length_y)

    def test_single_feed_dynamic_spacing(self):
        self._scan_dynamic._get_spacing(self._srecv, [18 * MHz])
        scan_length_x = self._scan_dynamic.offset_x[-1] - \
                        self._scan_dynamic.offset_x[0]
        scan_length_y = self._scan_dynamic.offset_y[-1] - \
                        self._scan_dynamic.offset_y[0]
        self.assertGreaterEqual(scan_length_x, self._length_x)
        self.assertGreaterEqual(scan_length_y, self._length_y)

    def test_multi_feed_dynamic_spacing(self):
        rec = self._recv
        self._scan_dynamic._get_spacing(rec, [18 * MHz])
        scan_length_x = self._scan_dynamic.offset_x[-1] - \
                        self._scan_dynamic.offset_x[0]
        scan_length_y = self._scan_dynamic.offset_y[-1] - \
                        self._scan_dynamic.offset_y[0]
        self.assertGreaterEqual(scan_length_x + rec.feed_extent * 2, self._length_x)
        self.assertGreaterEqual(scan_length_y + rec.feed_extent * 2, self._length_y)
        #check uniform sampling within receiver extent
        spb = int(rec.interleave / self._scan_dynamic.spacing)
        for j in range(self._scan_dynamic.dimension_x // spb):
            for i in range(spb - 2):
                self.assertAlmostEqual(self._scan_dynamic.offset_x[j*spb + i+1].deg - \
                                       self._scan_dynamic.offset_x[j*spb + i].deg,
                                       self._scan_dynamic.offset_x[j*spb + i+2].deg - \
                                       self._scan_dynamic.offset_x[j*spb + i+1].deg,
                                       msg = "j: {0} i: {1}".format(j,i))
        for j in range(self._scan_dynamic.dimension_y // spb):
            for i in range(spb - 2):
                self.assertAlmostEqual(self._scan_dynamic.offset_y[j*spb + i+1].deg - \
                                       self._scan_dynamic.offset_y[j*spb + i].deg,
                                       self._scan_dynamic.offset_y[j*spb + i+2].deg - \
                                       self._scan_dynamic.offset_y[j*spb + i+1].deg)
        #check uniform sampling accross receiver positions
        for j in range(self._scan_dynamic.dimension_x // spb - 1):
            pre = j * spb
            fol = pre + spb
            self.assertAlmostEqual(self._scan_dynamic.offset_x[fol].deg,
                                   self._scan_dynamic.offset_x[pre].deg +\
                                   rec.feed_extent.deg * 2 +\
                                   rec.interleave.deg + \
                                   self._scan_dynamic.spacing.deg)
        for j in range(self._scan_dynamic.dimension_y // spb - 1):
            pre = j * spb
            fol = pre + spb
            self.assertAlmostEqual(self._scan_dynamic.offset_y[fol].deg,
                                   self._scan_dynamic.offset_y[pre].deg +\
                                   rec.feed_extent.deg * 2 +\
                                   rec.interleave.deg + \
                                   self._scan_dynamic.spacing.deg)
