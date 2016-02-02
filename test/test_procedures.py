#coding=utf-8

import unittest

from basie.procedures import Procedure

class TestProcedures(unittest.TestCase):
    def setUp(self):
        self.simple_procedure = Procedure("SIMPLE", 0, "\tnop\n")
        self.simple_procedure_two = Procedure("SIMPLE_TWO", 0, "\tnop_two\n")
        self.one_param_procedure = Procedure("ONE_PARAM", 1, "\tparam=$1\n",
                                             True)

    def test_simple_procedure_definition(self):
        self.assertEqual(str(self.simple_procedure), "PROCEDURE_SIMPLE{\n\tnop\n}\n")
        self.assertEqual(self.simple_procedure.execute(), "PROCEDURE_SIMPLE")

    def test_simple_procedure_sum(self):
        sum_procedure = self.simple_procedure + self.simple_procedure_two
        self.assertEqual(str(sum_procedure),
                         "PROCEDURE_SIMPLE_SIMPLE_TWO{\n\tnop\n\tnop_two\n}\n")
        self.assertEqual(sum_procedure.execute(), "PROCEDURE_SIMPLE_SIMPLE_TWO")

    def test_one_param_procedure_definition(self):
        self.assertEqual(str(self.one_param_procedure),
                         "PROCEDURE_ONE_PARAM(1){\n\tparam=$1\n}\n")

    def test_one_param_procedure_execution(self):
        one_param = self.one_param_procedure("test")
        self.assertEqual(str(one_param),
                         "PROCEDURE_ONE_PARAM(1){\n\tparam=$1\n}\n")
        self.assertEqual(one_param.execute(), "PROCEDURE_ONE_PARAM=test")

    def test_sum_simple_one_param_definition(self):
        sum_procedure = self.simple_procedure + self.one_param_procedure
        self.assertEqual(str(sum_procedure),
                         "PROCEDURE_SIMPLE_ONE_PARAM(1){\n\tnop\n\tparam=$1\n}\n")
 
    def test_sum_simple_one_param_execution(self):
        sum_procedure = self.simple_procedure + \
                        self.one_param_procedure("test")
        self.assertEqual(str(sum_procedure),
                         "PROCEDURE_SIMPLE_ONE_PARAM(1){\n\tnop\n\tparam=$1\n}\n")
        self.assertEqual(sum_procedure.execute(),
                         "PROCEDURE_SIMPLE_ONE_PARAM=test")


