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
        self.can_tsys = True

    def _get_backend_instructions(self):
        raise NotImplementedError

    def __str__(self):
        res = "%s:BACKENDS/%s{\n" % (self.name, self.backend_type)
        res += self._get_backend_instructions()
        res += "}\n"
        return res

    def __eq__(self, other):
        return self._get_hash_params() == other._get_hash_params()

    def __hash__(self):
        return hash(self._get_hash_params())

    def _get_hash_params(self):
        return (
            self.name,
            self.backend_type,
            self.can_activate_switching_mark,
            self.can_tsys,
        )


class XBackend(Backend):
    def __init__(self, name, configuration):
        Backend.__init__(self, name, "XBackends")
        self.configuration = configuration
        self.can_activate_switching_mark = False
        self.can_tsys = False

    def _get_backend_instructions(self):
        if self.configuration.strip().upper() !='GENERIC':
            
            res = "\tinitialize=%s\n" % (self.configuration,)
        else:
            res = ""  
        
        return res

    def _get_hash_params(self):
        params = (
            self.configuration,
            self.can_activate_switching_mark,
            self.can_tsys,
        ) 
        return params + super(XBackend, self)._get_hash_params()



class RoachBackend(Backend):
    def __init__(self, name, configuration,integration,bandwidth,frequencybins):
        Backend.__init__(self, name, "Sardara")
        self.configuration = configuration
        self.can_activate_switching_mark = False
        self.valid_filters = (420.0,1500.0)
        self.valid_frequencybins=(1024,16384)
        self.bandwidth=float(bandwidth)
        self.frequencybins=float(frequencybins)
        self.can_tsys = False
        self.integration=float(integration)
        self.sections = [] 
    def set_sections(self,nifs,bandwidth=None):

        if self.configuration[-1].upper()=='S' or self.configuration=='GENERICSTOKES' :
            nifs /=2  
     
        if bandwidth is None:
            bandwidth = self.bandwidth
        if not bandwidth in self.valid_filters:
            msg = "not a valid bandwidth: %f" % (bandwidth,)
            logger.error(msg)
            raise ScheduleError(msg)
        for i in range(nifs):
            logger.debug("set section %d: %f" % (i, float(bandwidth)))
            self.sections.append((i, float(bandwidth)))
    def _get_backend_instructions(self):
        '''
        initialize=SK00
        setSection=0,*,420,*,*,840,*
        setSection=1,*,420,*,*,840,*

        integration=100

        setSection=0,*,420,*,*,840,*
        setSection=1,*,420,*,*,840,*

        
        '''
        
        configuration_skip_kw=('GENERIC','GENERICSTOKES',
                                'MULTIBEAM','MULTIBEAMSTOKES',
                                'NODDING','NODDINGSTOKES')
        if self.configuration.strip().upper() not in configuration_skip_kw:
            
            res = "\tinitialize=%s\n" % (self.configuration,)
        else:
            res =''
        
        for i, (_id, _bw) in enumerate(self.sections):
                res += "\tsetSection=%d,*,%f,*,*,%f,%f\n" % (_id, _bw,
                                                        _bw*2,self.frequencybins
                                                          ,)
        res += "\tintegration=%d\n" % (self.integration,)
        
        
        return res        
        
    
    
    
    def _get_hash_params(self):
        params = (
            self.configuration,
            self.can_activate_switching_mark,
            self.can_tsys,
            self.integration,
            self.frequencybins,
            self.bandwidth,
        ) 
        return params + super(RoachBackend, self)._get_hash_params()

class TotalPowerBackend(Backend):
    def __init__(self, name, integration, samplingInterval, bandwidth):
        Backend.__init__(self, name, "TotalPower")
        self.integration = float(integration)
        self.samplingInterval = float(samplingInterval)
        self.sections = []
        self.valid_filters = (300.0, 730.0, 1250.0, 2000.0)
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
            logger.debug("set section %d: %f" % (i, float(bandwidth)))
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

    def _get_hash_params(self):
        params = (
            self.integration,
            self.samplingInterval,
            tuple(self.sections),
            self.valid_filters,
            self.can_activate_switching_mark,
            self.bandwidth,
            self._empty_sections,
        ) 
        return params + super(TotalPowerBackend, self)._get_hash_params()


def BackendFactory(configuration_dict):
    if not "type" in configuration_dict:
        raise ScheduleError("missing Backend type")
    _type = configuration_dict.pop('type').upper()
    if _type == 'TOTALPOWER':
        return TotalPowerBackend(**configuration_dict)
    elif _type == 'XARCOS':
        return XBackend(**configuration_dict)
    elif _type == 'SARDARA':
        return RoachBackend(**configuration_dict)
    else:
        raise ScheduleError("invalid Backend type: %s" % (_type,))

