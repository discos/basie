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

__all__ = ['Schedule']

import logging
logger = logging.getLogger(__name__)
import os
from astropy import units
from persistent import Persistent

import templates
import procedures
import utils
from .errors import *
import layout
from . import VERSION, NURAGHE_TAG, ESCS_TAG
import scan
import backend
from .radiotelescopes import radiotelescopes

class Schedule(Persistent):
    def __init__(self,
                 projectID = "defaultProject",
                 observer = "defaultObserver",
                 scheduleLabel = "defaultSchedule",
                 repetitions = 1,
                 tsys = 1,
                 scheduleRuns = 1,
                 restFrequency = [0.0],
                 scantypes = {},
                 backends = {},
                 radiotelescope = "SRT", #should we change this?
                 receiver = "C", #should we change this?
                 outputFormat = "fits",
                 targetsFile = "targets.txt",
                 ):
        logger.debug("creating schedule")
        self.projectID = projectID
        self.observer = observer
        self.label = scheduleLabel
        self.repetitions = repetitions
        self.tsys = tsys
        self.runs = scheduleRuns,
        self.restFrequency = restFrequency
        self.scantypes = scantypes
        self.backends = backends
        self.radiotelescope = radiotelescopes[radiotelescope.upper()]
        logger.debug("GOT RADIOTELESCOPE: %s" % (self.radiotelescope,))
        self.receiver = self.radiotelescope.receivers[receiver.upper()]
        self.base_dir = os.path.abspath('.') #default 
        self.scans = []
        self._configure_totalpower_sections()
        logger.info("Scheduling %s radiotelescope using receiver %s" %
                (self.radiotelescope.name, self.receiver.name))
        self.targetsFile = targetsFile
        self.outputFormat = outputFormat

    def _configure_totalpower_sections(self):
        for name, bck in self.backends.iteritems():
            if isinstance(bck, backend.TotalPowerBackend):
                bck.set_sections(self.receiver.nifs)

    def add_scan(self, _target, _scantype, _backend):
        self.scans.append(
            scan.Scan(_target,
                 self.scantypes[_scantype],
                 self.receiver,
                 self.frequency,
                 self.backends[_backend],
                 _target.repetitions or self.repetitions,
                 _target.tsys or self.tsys,
                )
        )

        #explode 'BOTH' scans into 2 separate scans
        #for _scan_name, _scan_definition in self.scan_definitions.iteritems():
        #   logger.debug("examinating %s || %s" % (_scan_name,
        #                                          type(_scan_definition)))
        #   if isinstance(_scan_definition, tuple): #only BOTH scans return a tuple
        #       logger.info("exploding scan %s in 2 separate scans" % (_scan_name,))
        #       self.scan_definitions.pop(_scan_name)
        #       if ((_scan_name + "_lon" in self.scan_definitions) or 
        #           (_scan_name + "_lat" in self.scan_definitions)):
        #           raise ScheduleError("Cannot explode scan %s in separate subscans" % (_scan_name,))
        #       self.scan_definitions[_scan_name + "_lon"] = _scan_definition[0]
        #       self.scan_definitions[_scan_name + "_lat"] = _scan_definition[1]
        #       #explode 'BOTH' targets into 2 separate targets
        #       while _scan_name in [_target_scan_name 
        #                            for (_, _target_scan_name, _)
        #                            in self.targets]:
        #           index = [_tsn for (_, _tsn, _) in self.targets].index(_scan_name)
        #           _target, _scan_name, _line = self.targets[index]
        #           logger.info("Exploding target %s in two separate targets" % (_target.label,))
        #           self.targets[index] = (_target,
        #                                  _scan_name + "_lat",
        #                                  _line)
        #           self.targets.insert(index, (_target, 
        #                                       _scan_name + "_lon",
        #                                       _line))


    def set_base_dir(self, base_path):
        """
        Set the output directory for the schedule files.
        Creates the directory if it does not exist
        @param base_path: the path (relative or absolute) of the output
        directory
        """
        abs_path = os.path.abspath(base_path)
        if not os.path.isdir(abs_path):
            os.mkdir(abs_path)
        logger.debug("base output path set to %s" % (abs_path,))
        self.base_dir = abs_path

    def _get_filename(self, extension):
        return os.path.join(self.base_dir, "%s.%s" % (self.label, extension))

    def _write_schedule_files(self):
        """
        Method including the logics of schedule file creation.
        """
        # GET OUTPUT FILE NAMES
        scdfilename = self._get_filename("scd")
        lisfilename = self._get_filename("lis")
        cfgfilename = self._get_filename("cfg") 
        #datfilename = self._get_filename("dat") 
        bckfilename = self._get_filename("bck")
        scdfile = open(scdfilename, "wt")
        lisfile = open(lisfilename, "wt")
        #datfile = open(datfilename, "wt")
        #WRITE VERSION INFO IN SCD COMMENT
        scdfile.write("# Generated with basie version %s\n" % VERSION)
        scdfile.write("# compatible nuraghe version: %s\n" % NURAGHE_TAG)
        scdfile.write("# compatible escs version: %s\n" % ESCS_TAG)
        #WRITE SCD HEADER
        scdfile.write(templates.scd_header.substitute(
                              dict(
                                projectID = self.projectID,
                                observer = self.observer,
                                lisfilename = os.path.basename(lisfilename),
                                cfgfilename = os.path.basename(cfgfilename),
                                bckfilename = os.path.basename(bckfilename),
                                initproc = procedures.INIT.execute(),
                                  )))

        #WRITE SCAN AND SUBSCANS INFORMATIONS SEQUENTIALLY
        scan_number = 1
        _used_procedures = set() #stores every used procedure without repetitions
        _used_procedures.add(procedures.INIT) #default procedure
        _used_backends = set()
        #BEGIN SCANS LOOP
        for _scan in self.scans:
            logger.info("wrting %s" % (_scan.scanmode,))
            subscan_number = 1
            #WRITE SCD SCAN HEADER
            scdfile.write(templates.scd_scan_header.substitute(dict(scan_number=scan_number,
                                                                    target_label=_scan.target.label)))
            scanlayout = "scanlayout_%d_%s" % (scan_number, _scan.target.label)
            data_writer = "MANAGEMENT/FitsZilla"
            scdfile.write("%s:%s\t%s\n" %
                          (_scan.backend.name, data_writer, scanlayout,))
            _used_backends.add(_scan.backend)
            #BEGIN SUBSCANS LOOP
            subscans_set = set() #all subscans in this scan
            for _subscan in _scan.subscans:
                _subscan.SEQ_ID = subscan_number
                #if isinstance(_subscan, OTFSubscan):
                    #ADD WAIT post subscan proceudure
                    #wait_time = ((_scan._scanmode.speed / 60.0) /
                    #    self.radiotelescope.max_acc *
                    #    self.radiotelescope.acc_scale_factor)
                    #wait_time = utils.ceil_to_half(wait_time)
                    #_subscan.add_post_procedure(procedures.WAIT(wait_time))
                #ADD SUBSCAN PROCEDURES TO THE SET OF USED ONES
                _used_procedures.add(_subscan.pre_procedure)
                _used_procedures.add(_subscan.post_procedure)
                #ADD THE SUBSCAN TO THE SET OF USED ONES
                subscans_set.add(_subscan)
                #WRITE SUBSCAN IN SCD FILE
                scdfile.write("%d_%d\t%f\t%d\t%s\t%s\n" % (
                                                            scan_number,
                                                            _subscan.SEQ_ID,
                                                            _subscan.duration,
                                                            _subscan.ID,
                                                            _subscan.pre_procedure.execute(),
                                                            _subscan.post_procedure.execute(),
                                                            ))
                subscan_number += 1
                #END SUBSCANS LOOP
            #WRITE SUBSCANS TO LIS FILE
            subscans_list = list(subscans_set)
            subscans_list.sort(key = lambda x: x.ID) #GET SUBSCANS SORTED BY ID
            lisfile.write("#%s\n" % (_scan.target.label,))
            for _subscan in subscans_list:
                lisfile.write(str(_subscan))
                lisfile.write("\n")
            # WRITE DAT FILE
            _layout = layout.get_layout_params(_scan, subscans_list)
            #datfile.write(templates.format_layout(scanlayout, _layout))
            # GO TO NEXT SCAN
            scan_number += 1
            #END SCANS LOOP
        scdfile.close()
        lisfile.close()
        #datfile.close()
        #write to file used procedures
        with open(cfgfilename, "wt") as cfgfile:
            for _p in _used_procedures:
                cfgfile.write(str(_p))
        #write to file used backends
        with open(bckfilename, "wt") as bckfile:
            for _b in _used_backends:
                bckfile.write(str(_b))

