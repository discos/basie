#coding=utf-8

import unittest

from basie.frame import EQ, HOR
from astropy.units import MHz
from basie.radiotelescopes import SRT
from basie.scanmode import subscan, maps
from basie.valid_angles import VAngle


class TestMapScan(unittest.TestCase):

    def setUp(self):
        self._length_x = VAngle(0.4)
        self._length_y = VAngle(0.4)
        self._spacing = VAngle(0.06)
        self._scans_per_beam = 3
        self._scan_fixed = maps.MapScan(EQ, "TL", "LON",
                                        self._length_x,
                                        self._length_y,
                                        self._spacing)
        self._scan_dynamic = maps.MapScan(EQ, "TL", "LON",
                                        self._length_x,
                                        self._length_y,
                                        self._scans_per_beam)

    def test_single_feed_fixed_spacing(self):
        self._scan_fixed._get_spacing(SRT.receivers["K"], [18 * MHz]) 
        scan_length_x = self._scan_fixed.offset_x[-1] - \
                        self._scan_fixed.offset_x[0]
        scan_length_y = self._scan_fixed.offset_y[-1] - \
                        self._scan_fixed.offset_y[0]
        self.assertGreaterEqual(scan_length_x, self._length_x)
        self.assertGreaterEqual(scan_length_y, self._length_y)
        for i in range(len(self._scan_fixed.offset_x) - 1):
            self.assertAlmostEqual(self._spacing, 
                                   self._scan_fixed.offset_x[i+1] -\
                                   self._scan_fixed.offset_x[i]) 
        for i in range(len(self._scan_fixed.offset_y) - 1):
            self.assertAlmostEqual(self._spacing, 
                                   self._scan_fixed.offset_y[i+1] -\
                                   self._scan_fixed.offset_y[i]) 

    def test_multi_feed_fixed_spacing(self):
        rec = SRT.receivers["KM"]
        self._scan_fixed._get_spacing(rec, [18 * MHz]) 
        scan_length_x = self._scan_fixed.offset_x[-1] - \
                        self._scan_fixed.offset_x[0]
        scan_length_y = self._scan_fixed.offset_y[-1] - \
                        self._scan_fixed.offset_y[0]
        self.assertGreaterEqual(scan_length_x + rec.feed_extent * 2, self._length_x)
        self.assertGreaterEqual(scan_length_y + rec.feed_extent * 2, self._length_y)

    def test_single_feed_dynamic_spacing(self):
        self._scan_dynamic._get_spacing(SRT.receivers["K"], [18 * MHz]) 
        scan_length_x = self._scan_dynamic.offset_x[-1] - \
                        self._scan_dynamic.offset_x[0]
        scan_length_y = self._scan_dynamic.offset_y[-1] - \
                        self._scan_dynamic.offset_y[0]
        self.assertGreaterEqual(scan_length_x, self._length_x)
        self.assertGreaterEqual(scan_length_y, self._length_y)

    def test_multi_feed_dynamic_spacing(self):
        rec = SRT.receivers["KM"]
        self._scan_dynamic._get_spacing(rec, [18 * MHz]) 
        scan_length_x = self._scan_dynamic.offset_x[-1] - \
                        self._scan_dynamic.offset_x[0]
        scan_length_y = self._scan_dynamic.offset_y[-1] - \
                        self._scan_dynamic.offset_y[0]
        self.assertGreaterEqual(scan_length_x + rec.feed_extent * 2, self._length_x)
        self.assertGreaterEqual(scan_length_y + rec.feed_extent * 2, self._length_y)
        #check uniform sampling within receiver extent
        spb = self._scans_per_beam
        for j in range(self._scan_dynamic.dimension_x / spb):
            for i in range(spb - 2):
                self.assertAlmostEqual(self._scan_dynamic.offset_x[j*spb + i+1].deg - \
                                       self._scan_dynamic.offset_x[j*spb + i].deg, 
                                       self._scan_dynamic.offset_x[j*spb + i+2].deg - \
                                       self._scan_dynamic.offset_x[j*spb + i+1].deg)
        for j in range(self._scan_dynamic.dimension_y / spb):
            for i in range(spb - 2):
                self.assertAlmostEqual(self._scan_dynamic.offset_y[j*spb + i+1].deg - \
                                       self._scan_dynamic.offset_y[j*spb + i].deg, 
                                       self._scan_dynamic.offset_y[j*spb + i+2].deg - \
                                       self._scan_dynamic.offset_y[j*spb + i+1].deg)
        #check uniform sampling accross receiver positions
        for j in range(self._scan_dynamic.dimension_x / spb - 1):
            pre = j * self._scans_per_beam
            fol = pre + self._scans_per_beam
            self.assertAlmostEqual(self._scan_dynamic.offset_x[fol].deg, 
                                   self._scan_dynamic.offset_x[pre].deg +\
                                   rec.feed_extent.deg * 2 +\
                                   rec.interleave.deg + \
                                   self._scan_dynamic.spacing.deg)
        for j in range(self._scan_dynamic.dimension_y / spb - 1):
            pre = j * self._scans_per_beam
            fol = pre + self._scans_per_beam
            self.assertAlmostEqual(self._scan_dynamic.offset_y[fol].deg, 
                                   self._scan_dynamic.offset_y[pre].deg +\
                                   rec.feed_extent.deg * 2 +\
                                   rec.interleave.deg + \
                                   self._scan_dynamic.spacing.deg)
