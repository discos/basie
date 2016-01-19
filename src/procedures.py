#coding=utf-8

#
#
#    Copyright (C) 2013  INAF -IRA Italian institute of radioastronomy, bartolini@ira.inaf.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re
import copy
import functools

from errors import *

TSYS_WAIT_TIME = 2
"""
Time to wait before issuing a tsys command (sec.)
"""

PROC_PREFIX = "PROCEDURE_"
"""
Prefix for procedures name
"""

def inc_arguments(expr, inc=1):
    """
    Increment $n substitutions of a fixed amount
    i.e. $1 will be substituted by $2 ecc ... 
    In general we will have every $(n) -> $(n + inc)
    """
    #a little criptic but effective, just believe it ;)
    return re.subn("\$\d+", lambda x: "$" + str(int(x.group()[1:]) + inc), expr)[0]

class Procedure(object):
    """Class representing a procedure template.
    Remeber that the module already defines some standard procedures!
    Use it like this:

        >>> import procedures
        >>> myproc = procedures.Procedure(\"myp\", 1, \"\\tcomm=$1\\n\\tend_comm\\n\")
        >>> str(myproc) 
        \'MYP(1){\\n\\tcomm=$1\\n\\tend_comm\\n}\\n\'
        >>> myproc(10)  
        \'MYP=10\'


    """
    def __init__(self, name, nparams, body, spec=False):
        """
        Constructor.
        @param name: name of the procedure as will be defined in schedule files
        @param nparams: number of parameters accepted by the procedure
        @param body: the body of the procedure, that's to say the list of
        commands the procedure executes
        @param spec: True if the object can be specialized
        """
        self.name = name.upper()
        self.nparams = nparams
        self.body = body
        self._spec = spec

    def execute(self, *args):
        """
        Used to get the procedure syntax as it has to be called from within the
        .scd schedule file
        """
        if not len(args) == self.nparams:
            raise TypeError("Procedure %s takes exactly %d params (%d given)" %
                            (self.name, self.nparams, len(args)))
        res = PROC_PREFIX + self.name
        if self.nparams > 0:
            res += '=' 
            for _arg in args:
                res += str(_arg) + ","
            res = res[:-1]
        return res

    def is_null(self):
        return ((self.nparams == 0) and (self.body == ""))

    def __str__(self):
        """
        Used for getting the procedure definition as it must be added to the
        .cfg schedule file
        """
        res = PROC_PREFIX + self.name
        if self.nparams > 0:
            res += "(%d)" % self.nparams
        res += "{\n"
        res += self.body
        res += "}\n"
        return res

    def __add__(self, other):
        if other.is_null(): #caso degenere
            return self
        if self.is_null():
            return other
        res_name = "%s_%s" % (self.name, other.name)
        res_nparams = self.nparams + other.nparams
        if self.nparams > 0 and other.nparams > 0:
            modified_body = inc_arguments(other.body, self.nparams)
            res_body = self.body + modified_body
        else:
            res_body = self.body + other.body
        if self._spec or other._spec:
            res_spec = True
        else:
            res_spec = False
        return Procedure(res_name, res_nparams, res_body, res_spec)

    def __eq__(self, other):
        return type(self) == type(other) and self.body == other.body and self.nparams == other.nparams and self.name == other.name

    def __hash__(self):
        """
        Redefined for correct inclusion into set objects.
        """
        return hash((self.name, self.nparams, self.body))

    def __call__(self, *args):
        if self._spec:
            res = copy.deepcopy(self)
            if not hasattr(res.execute, "args"):
                res.execute = functools.partial(self.execute, *args)
            res._spec = False
            return res
        else:
            raise ProcedureError("Procedure %s cannot be specialized" % self.name)

FTRACK = Procedure("FTRACK", 1, "\tftrack=$1\n", True)
"""
Standard B{ftrack} procedure
"""

RSTFREQ = Procedure("restFrequency", 1, "\trestFrequency=$1\n", True)
"""
Standard B{restFrequency} procedure
"""

DEROTATOR = Procedure("DEROTATOR", 1, "\tderotatorSetConfiguration=$1\n", True)
"""
Standard B{derotator} procedure for configuration setup
"""

#TODO: correct procedure sum and remove these two
#TODO: should we set derotator position to 0?
DEROTATORFIXED = Procedure("DEROTATORFIXED", 0, "\tderotatorSetConfiguration=FIXED\n", True)
DEROTATORBSC = Procedure("DEROTATORBSC", 0, "\tderotatorSetConfiguration=BSC\n", True)

WAIT = Procedure("WAIT", 1, "\twait=$1\n", True)
"""
Standard B{wait} procedure
"""

TSYS = Procedure("TSYS", 0, "\twait=%f\n\ttsys\n\twait=1\n" % (TSYS_WAIT_TIME,))
"""
Standard B{tsys} procedure
"""

INIT = Procedure("INIT", 0, "\tnop\n")
"""
Standard B{init} procedure
"""

CALON = Procedure("CALON", 0, "\tcalon\n")
"""
Standard B{calon} procedure
"""

CALOFF = Procedure("CALOFF", 0, "\tcaloff\n")
"""
Standard B{caloff} procedure
"""

NULL = Procedure("NULL", 0, "")
"""
Standard B{null} procedure
"""

