#coding=utf-8

try:
    import unittest2 as unittest
except ImportError:
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
        #self.assertTrue(False)



if __name__ == "__main__":
    unittest.main()