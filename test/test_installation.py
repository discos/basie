#coding=utf-8

try:
    import unittest2 as unittest
except ImportError:
    import unittest
import basie

class TestInstallation(unittest.TestCase):
    def test_version(self):
        self.assertEqual(basie.VERSION, "1.0dev")

    def test_astropy_version(self):
        import astropy
        av = astropy.__version__.split('.')
        assert int(av[0]) >= 1
        # self.assertEqual(av[0], '1')
        #self.assertEqual(av[1], '0')
