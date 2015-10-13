#coding=utf-8

import unittest
import schedulecreator

class TestInstallation(unittest.TestCase):
    def test_version(self):
        self.assertEqual(schedulecreator.VERSION, "0.4.2 astropy")

    def test_astropy_version(self):
        import astropy
        av = astropy.__version__.split('.')
        self.assertEqual(av[0], '1')
        self.assertEqual(av[1], '0')
