#coding=utf-8

import unittest2 as unittest
import copy
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

    def test_set_addition(self):
        # https://github.com/discos/basie/issues/28
        s = set()
        s.add(self.backend)
        backend_copy = copy.copy(self.backend)
        backend_copy.name += 'CT'
        backend_copy_2nd = copy.copy(self.backend)
        backend_copy_2nd.name += 'CT'
        s.add(backend_copy)
        s.add(backend_copy_2nd)
        self.assertEqual(len(s), 2)
