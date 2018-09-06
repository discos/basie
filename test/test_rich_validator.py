#coding=utf-8

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import basie.rich_validator as rv
from basie import frame
from basie import scan

class TestRichValidator(unittest.TestCase):
    def test_string2list(self):
        l = "primo,secondo terzo\tquarto "
        res = rv.string2list(l)
        self.assertEqual(res, ["primo", "secondo", "terzo", "quarto"])

    def test_check_frame(self):
        feq = rv.check_frame("EQ")
        fhor = rv.check_frame("HOR")
        fgal = rv.check_frame("gal")
        self.assertEqual(feq, frame.EQ)
        self.assertEqual(fhor, frame.HOR)
        self.assertEqual(fgal, frame.GAL)

if __name__ == "__main__":
    unittest.main()

