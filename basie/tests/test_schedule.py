try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
import shutil
from basie import schedule
from basie.radiotelescopes import radiotelescopes
from basie.rich_validator import validate_configuration
from basie import target_parser

BASE_PATH = ".basie_test"
curdir = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_PATH = os.path.join(curdir, "..", "user_templates")

class TestSchedule(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(BASE_PATH, True) #ignores errors
        os.makedirs(BASE_PATH)
        self.conf = validate_configuration(os.path.join(TEMPLATE_PATH, "configuration_SR.txt"))

        targetsFile = os.path.join(TEMPLATE_PATH, self.conf.pop('targetsFile'))
        parsed_targets = target_parser.parse_file(targetsFile)
        backends = self.conf.pop("backends")
        scantypes = self.conf.pop("scantypes")
        self.sched = schedule.Schedule(**self.conf)
        self.sched.backends = backends
        self.sched.scantypes = scantypes
        for _target, _scanmode, _backend, _  in parsed_targets:
            self.sched.add_scan(_target, _scanmode, _backend)
        self.sched.set_base_dir(BASE_PATH)

    def tearDown(self):
        shutil.rmtree(BASE_PATH, True) #ignores errors

    def test_schedule_parameters(self):
        self.assertEqual(self.sched.projectID, self.conf['projectID'])

    def test_write_schedule_files(self):
        self.sched._write_schedule_files()
        self.assertTrue(os.path.exists(self.sched._get_filename("scd")))
        self.assertTrue(os.path.exists(self.sched._get_filename("lis")))
        self.assertTrue(os.path.exists(self.sched._get_filename("bck")))
        self.assertTrue(os.path.exists(self.sched._get_filename("cfg")))

    def test_schedule_files_do_not_contain_whitespaces(self):
        self.sched._write_schedule_files()
        with open(self.sched._get_filename("scd"), "rt") as scd:
            for line in scd.readlines():
                if not line.startswith("#"):
                    self.assertNotIn(" ", line)
        with open(self.sched._get_filename("lis"), "rt") as lis:
            for line in lis.readlines():
                if not line.startswith("#"):
                    self.assertNotIn(" ", line)
        with open(self.sched._get_filename("bck"), "rt") as bck:
            for line in bck.readlines():
                if not line.startswith("#"):
                    self.assertNotIn(" ", line)
        with open(self.sched._get_filename("cfg"), "rt") as cfg:
            for line in cfg.readlines():
                if not line.startswith("#"):
                    self.assertNotIn(" ", line)

