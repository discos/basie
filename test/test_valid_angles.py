import unittest

from basie.valid_angles import VAngle
from basie import angle_parser
from astropy import units as u


class TestAngles(unittest.TestCase):
    def test_creation(self):
        float_val = 10.0
        angle = VAngle(float_val)
        self.assertEqual(float_val, angle.deg)
        self.assertEqual(angle.original_unit, u.degree)
        copied = VAngle(angle)
        self.assertEqual(angle.radian, copied.radian)

    def test_parsing_hour(self):
        ang = angle_parser.check_hms_angle("01:00:00.0h")
        self.assertAlmostEqual(ang.deg, VAngle(15.0).deg) 

    def test_parsing_dec(self):
        ang = angle_parser.check_dec_angle("15.0d")
        self.assertEqual(ang.deg, VAngle(15.0).deg)

    def test_parsing_deg(self):
        ang = angle_parser.check_dms_angle("15:00:00.0")
        self.assertEqual(ang.deg, VAngle(15.0).deg)

    def test_parsing(self):
        ang = VAngle(15.0)
        dec = angle_parser.check_angle("15.0d")
        dms = angle_parser.check_angle("15:00:00.0")
        hms = angle_parser.check_angle("01:00:00.0h")
        self.assertEqual(ang.radian, dec.radian)
        self.assertEqual(ang.radian, dms.radian)
        self.assertEqual(ang.radian, hms.radian)

    def test_fmt_dec(self):
        ang = VAngle(15.0)
        self.assertEqual(ang.fmt_dec(), u"15.000d")

    def test_fmt_dms(self):
        ang = VAngle(15.0)
        self.assertEqual(ang.fmt_dms(), u"15:00:00.000")

    def test_fmt_hms(self):
        ang = VAngle(15.0)
        _str = ang.fmt_hms()
        self.assertEqual(_str, u"01:00:00.000h")
        #self.assertEqual(_str[-1], u"h")

    def test_sum(self):
        a = VAngle(10.0)
        b = VAngle(5.0)
        c = a + b
        self.assertEqual(c.deg, a.deg + b.deg)

    def test_sum_is_vangle(self):
        a = VAngle(10.0)
        b = VAngle(5.0)
        c = a + b
        self.assertTrue(isinstance(c, type(a)))

    def test_sum_keeps_attributes(self):
        a = VAngle(10.0)
        b = VAngle(5.0)
        c = a + b
        self.assertTrue(hasattr(c, "original_unit"))
        self.assertTrue(hasattr(c, "sexa"))
        self.assertEqual(a.original_unit, c.original_unit)
        self.assertEqual(a.sexa, c.sexa)


if __name__ == "__main__":
    unittest.main()

