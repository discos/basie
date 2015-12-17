import unittest
import os
import shutil
from basie import schedule
from basie.rich_validator import validate_configuration

BASE_PATH = "/tmp/sctest"
shutil.rmtree(BASE_PATH)
os.mkdir(BASE_PATH)

class TestSchedule(unittest.TestCase):
    def test_schedule_generation(self):
        conf = validate_configuration("src/user_templates/configuration.txt")
        conf['targetsFile'] = "src/user_templates/targets.txt"
        sched = schedule.Schedule(conf)
        self.assertEqual(sched.projectID, conf['projectID'])
        sched.set_base_dir(BASE_PATH)
        sched._write_schedule_files()
        self.assertTrue(os.path.exists(sched._get_filename("scd")))

