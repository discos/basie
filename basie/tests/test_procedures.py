#coding=utf-8

from builtins import str
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from basie.procedures import Procedure, PROC_PREFIX, FTRACKALL

class TestProcedures(unittest.TestCase):
    def setUp(self):
        self.simple_procedure = Procedure("SIMPLE", 0, "\tnop\n")
        self.simple_procedure_two = Procedure("SIMPLE_TWO", 0, "\tnop_two\n")
        self.one_param_procedure = Procedure("ONE_PARAM", 1, "\tparam=$1\n",
                                             True)

    def test_simple_procedure_definition(self):
        self.assertEqual(str(self.simple_procedure),
                         "%sSIMPLE{\n\tnop\n}\n" % (PROC_PREFIX,))
        self.assertEqual(self.simple_procedure.execute(),
                         "%sSIMPLE" % (PROC_PREFIX,))

    def test_simple_procedure_sum(self):
        sum_procedure = self.simple_procedure + self.simple_procedure_two
        self.assertEqual(str(sum_procedure),
                         "%sSIMPLE_SIMPLE_TWO{\n\tnop\n\tnop_two\n}\n" %
                         (PROC_PREFIX,))
        self.assertEqual(sum_procedure.execute(),
                         "%sSIMPLE_SIMPLE_TWO" % (PROC_PREFIX,))

    def test_one_param_procedure_definition(self):
        self.assertEqual(str(self.one_param_procedure),
                         "%sONE_PARAM(1){\n\tparam=$1\n}\n" % (PROC_PREFIX,))

    def test_one_param_procedure_execution(self):
        one_param = self.one_param_procedure("test")
        self.assertEqual(str(one_param),
                         "%sONE_PARAM(1){\n\tparam=$1\n}\n" % (PROC_PREFIX,))
        self.assertEqual(one_param.execute(),
                         "%sONE_PARAM=test" % (PROC_PREFIX,))

    def test_sum_simple_one_param_definition(self):
        sum_procedure = self.simple_procedure + self.one_param_procedure
        self.assertEqual(str(sum_procedure),
                         "%sSIMPLE_ONE_PARAM(1){\n\tnop\n\tparam=$1\n}\n" %
                         (PROC_PREFIX,))

    def test_sum_simple_one_param_execution(self):
        # i want this to work eventually
        #sum_procedure = self.simple_procedure + \
        #                self.one_param_procedure("test")
        sum_procedure = (self.simple_procedure + \
                        self.one_param_procedure)("test")
        self.assertEqual(str(sum_procedure),
                         "%sSIMPLE_ONE_PARAM(1){\n\tnop\n\tparam=$1\n}\n" %
                         (PROC_PREFIX,))
        self.assertEqual(sum_procedure.execute(),
                         "%sSIMPLE_ONE_PARAM=test" % (PROC_PREFIX,))
    #MLA add test derotator



if __name__ == '__main__':
    DEROTATOR = Procedure("DEROTATOR", 1, "\tderotatorSetConfiguration=$1\n", True)
    print(str(DEROTATOR.execute(5)))
    s = FTRACKALL + DEROTATOR

    print(str(s.execute(5)))
    print(str(s))
