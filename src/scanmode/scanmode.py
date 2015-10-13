#coding: utf-8

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

"""
Module implementing scan geometries and their methods to get subscans for
specific targets
"""

import logging
logger = logging.getLogger(__name__)

class ScanMode(object):
    """
    Base class for all Scan types. Gives a unique ID to the scan and implements
    L{iter_subscans<self.iter_subscans>} method valid for all subclasses.
    """
    ID = 0
    def __init__(self):
        """
        """
        self.ID = ScanMode.ID
        ScanMode.ID += 1 #increment instance counter
        self.unit_subscans = 1 #number of logically grouped subscans
        self.subscans = []
        self.current_target = None
        self.name = "SCAN"
        #TODO: manca self.frame - devo inserirlo qui?

    def __lt__(self, other):
        return self.ID < other.ID

    def __eq__(self, other):
        return self.ID == other.ID

    def __str__(self):
        return "Scan %d type %s" % (self.ID, str(self.__class__))

    def do_scan(self, _target, _receiver, _frequency):
        """
        Set the current taraget and calls the L{_do_scan} implementation of the
        specific subclass
        @param _target: the current target
        @type _target: L{target.Target}
        @param _receiver: the selected receiver
        @param _frequency: the selected frequency
        @raise ScanError: if frequency is not within receiver range
        """
        logger.info("scheduling %s on target %s" % (self.name, _target.label))
        self._do_scan(_target, _receiver, _frequency)

    def _do_scan(self, _target, _receiver, _frequency):
        """
        This is meant to be overridden by subclasses
        Implements logics used to get all the subscans starting from scan and
        target specifications.
        """
        raise NotImplementedError

