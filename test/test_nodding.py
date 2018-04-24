#coding=utf-8

import unittest2 as unittest

from basie.frame import EQ, HOR
from astropy.units import MHz
from basie.radiotelescopes import SRT
from basie.scanmode import subscan, maps,nodding
from basie.valid_angles import VAngle
from basie.receiver import Receiver
from basie import frame, target_parser

class TestNoddingScan(unittest.TestCase):

   def setUp(self):
      feed_a=3
      feed_b=0
      self._recv = Receiver("TEST", 0, 100,
                             [[0.0, 100.0], [5.0, 5.0]],
                             nfeed = 7,
                             npols = 2,
                             has_derotator = True)
      seq=[(2,'a',0),(2,'a',1),(2,'b',0),(2,'b',1)]
      self._nodding=nodding.NoddingScan([feed_a,feed_b],30,seq)
      self._offset=self._recv.feed_offsets[feed_b]
      LINE = "3C386 otfmap1 TP EQ 10.0d 1:00:00.0h"
      self.SCANTYPE, self.BACKEND, self.TARGET = target_parser._parse_target_line(LINE)
   def test_nodding(self):
      self._nodding._do_scan(self.TARGET,self._recv,20.000)
      self.assertEqual(self._nodding.offset,-self._offset)
    
    