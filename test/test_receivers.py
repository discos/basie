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
        print(self.receiver.get_valid_pairs())
        #self.assertTrue(self.receiver.is_valid_pair((1,5),"90"))



if __name__ == "__main__":
    unittest.main()

