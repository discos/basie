#coding=utf-8

import unittest

from basie.radiotelescopes import SRT
from basie.valid_angles import VAngle

class TestReceiver(unittest.TestCase):
    def setUp(self):
        self.receiver = SRT.receivers["KM"]

    def test_get_beamsize(self):
        beamsize = VAngle(self.receiver.beamsize)
        self.assertTrue(beamsize >= VAngle(0))

    def test_valid_pairs(self):
        self.assertTrue(self.receiver.is_valid_pair((1,5),"90"))
        self.assertTrue(self.receiver.is_valid_pair((5,1),"90"))
        self.assertFalse(self.receiver.is_valid_pair((1,3),"90"))
        self.assertFalse(self.receiver.is_valid_pair((3,1),"90"))



if __name__ == "__main__":
    unittest.main()

