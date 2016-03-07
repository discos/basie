#coding=utf-8

import unittest2 as unittest

from basie.radiotelescopes import SRT
from basie.valid_angles import VAngle

class TestReceiver(unittest.TestCase):
    def setUp(self):
        self.receiver = SRT.receivers["KM"]

    def test_get_beamsize(self):
        beamsize = VAngle(self.receiver.beamsize)
        self.assertTrue(beamsize >= VAngle(0))
