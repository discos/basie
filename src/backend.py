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

import logging
logger=logging.getLogger(__name__)

from persistent import Persistent

from errors import *


class Backend(Persistent):
    def __init__(self, name, backend_type = "INVALID"):
        self.name = name
        self.backend_type = backend_type
        self.can_activate_switching_mark = False

    def _get_backend_instructions(self):
        raise NotImplementedError

    def __str__(self):
        res = "%s:BACKENDS/%s{\n" % (self.name, self.backend_type)
        res += self._get_backend_instructions()
        res += "}\n"
        return res


class XBackend(Backend):
    def __init__(self, name, configuration):
        Backend.__init__(self, name, "XBackend")
        self.configuration = configuration
        self.can_activate_switching_mark = False

    def _get_backend_instructions(self):
        res = "\tinitialize=%s\n" % (self.configuration,)
        return res

class RoachBackend(Backend):
    def __init__(self, name, configuration):
        Backend.__init__(self, name, "Roach")
        self.configuration = configuration
        self.can_activate_switching_mark = False

    def _get_backend_instructions(self):
        res = "\tinitialize=%s\n" % (self.configuration,)
        return res

class TotalPowerBackend(Backend):
    def __init__(self, name, integration, samplingInterval, bandwidth):
        Backend.__init__(self, name, "TotalPower")
        self.integration = float(integration)
        self.samplingInterval = float(samplingInterval)
        self.sections = []
        self.valid_filters = [300.0, 730.0, 1250.0, 2000.0]
        self.can_activate_switching_mark = True
        self.bandwidth = float(bandwidth)
        self._empty_sections = 0

    def set_sections(self, nifs, bandwidth=None):
        if bandwidth is None:
            bandwidth = self.bandwidth
        if not bandwidth in self.valid_filters:
            msg = "not a valid bandwidth: %f" % (bandwidth,)
            logger.error(msg)
            raise ScheduleError(msg)
        for i in range(nifs):
            self.sections.append((i, float(bandwidth)))

    def _get_backend_instructions(self):
        res = ""
        enable_string = "\tenable="
        for i, (_id, _bw) in enumerate(self.sections):
            res += "\tsetSection=%d,*,%f,*,*,%f,*\n" % (_id, _bw,
                                                        (1.0 /
                                                        (self.samplingInterval
                                                            * 1000.0)),)
            if i > 0:
                enable_string += ";"
            enable_string += "1"
        for i in range(self._empty_sections):
            enable_string += ";0"
        enable_string += "\n"
        res += "\tintegration=%d\n" % (self.integration,)
        res += enable_string
        return res
            
def BackendFactory(configuration_dict):
    if not "type" in configuration_dict:
        raise ScheduleError("missing Backend type")
    _type = configuration_dict.pop('type').upper()
    if _type == 'TOTALPOWER':
        return TotalPowerBackend(**configuration_dict)
    elif _type == 'XARCOS':
        return XBackend(**configuration_dict)
    elif _type == 'ROACH':
        return RoachBackend(**configuration_dict)
    else:
        raise ScheduleError("invalid Backend type: %s" % (_type,))

