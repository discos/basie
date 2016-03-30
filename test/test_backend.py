#coding=utf-8

import unittest2 as unittest
from io import StringIO

from basie.backend import *
from basie.radiotelescopes import *

class TestRoachBackend(unittest.TestCase):
    def setUp(self):
        self.name = "prova"
        self.configuration = "RCONFIG"
        self.roach_backend = RoachBackend(self.name, self.configuration)

    def test_roach_backend_instructions(self):
        backend_instructions = ""
        self.assertEqual(self.roach_backend._get_backend_instructions(), 
                         backend_instructions)

    def test_roach_backend_bck_file(self):
        bck_file = "%s:BACKENDS/Roach{\n}\n" % (self.name,)
        self.assertEqual(str(self.roach_backend),
                         bck_file)

class TestTotalPowerBackend(unittest.TestCase):
    def setUp(self):
        self.backend = TotalPowerBackend("TP", 10, 10, 300)

    def test_total_power_set_sections(self):
        n_sections = 2
        self.backend.set_sections(n_sections)
        self.assertEqual(len(self.backend.sections), n_sections)

    def test_total_power_set_sections_enable(self):
        self.backend.set_sections(2)
        instructions = StringIO(unicode(self.backend._get_backend_instructions()))
        lines = instructions.readlines()
        enable_line = lines[-1].strip()
        self.assertTrue(enable_line.startswith("enable"))


