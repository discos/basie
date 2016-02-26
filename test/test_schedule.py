import unittest2 as unittest
import os
import shutil
from basie import schedule
from basie.radiotelescopes import radiotelescopes
from basie.rich_validator import validate_configuration

BASE_PATH = "/tmp/basie_test"
shutil.rmtree(BASE_PATH, True) #ignores errors
os.mkdir(BASE_PATH)

class TestSchedule(unittest.TestCase):
    def test_schedule_generation(self):
        conf = validate_configuration("src/user_templates/configuration.txt")
        conf.pop("targetsFile")
        backends = conf.pop("backends")
        scantypes = conf.pop("scantypes")
        sched = schedule.Schedule(**conf)
        sched.backends = backends
        sched.scantypes = scantypes
        self.assertEqual(sched.projectID, conf['projectID'])
        sched.set_base_dir(BASE_PATH)
        sched._write_schedule_files()
        self.assertTrue(os.path.exists(sched._get_filename("scd")))

