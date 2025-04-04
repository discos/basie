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

"""
Module containing templates (as defined in standard string module) used to transorm classes instances into the
representation used in the schedule files by ACS
"""

from builtins import str
import string
import logging
logger = logging.getLogger(__name__)

scd_header = string.Template("PROJECT:\t\t${projectID}\n" +
                             "OBSERVER:\t\t${observer}\n" +
                             "SCANLIST:\t\t${lisfilename}\n" +
                             "PROCEDURELIST:\t\t${cfgfilename}\n" +
                             "BACKENDLIST:\t\t${bckfilename}\n" +
                             "MODE:\t\t\tSEQ\n" +
                             "SCANTAG:\t\t1\n" +
                             "INITPROC:\t\t${initproc}\n")
"""
Used to convert a L{schedule.Schedule} instance into its representation in the .scd
file header
"""
elevation_limits = string.Template("ELEVATIONLIMITS:\t${minElevation}\t${maxElevation}\n")

scd_scanlayout = string.Template("SCANLAYOUT:\t${datfilename}\n")

scd_scan_header = string.Template("\nSC:\t${scan_number}\t${target_label}\t")

sidereal_subscan = string.Template("${ID}\t" +
                                    "SIDEREAL\t" +
                                    "${target}\t" +
                                    "${frame}\t" +
                                    "${longitude}\t" +
                                    "${latitude}\t" +
                                    "${epoch}" + #\t is added in the code as
                                    # this param is optional!!!
                                    "${offset_frame}\t" +
                                    "${offset_lon}\t"+
                                    "${offset_lat}\t" +
                                    "${vel}")
"""
Used to convert an instance of L{subscan.SiderealSubscan} into its representation
in the .lis file
"""

otf_subscan = string.Template("${ID}\t" +
                               "OTF\t" +
                               "${target}\t" +
                               "${lon1}\t" +
                               "${lat1}\t" +
                               "${lon2}\t" +
                               "${lat2}\t" +
                               "${frame}\t" +
                               "${s_frame}\t" +
                               "${geom}\t" +
                               "${descr}\t" +
                               "${direction}\t" +
                               "${duration}\t" +
                               "${offset_frame}\t" +
                               "${offset_lon}\t" +
                               "${offset_lat}\t" + 
                               "${vel}")
"""
Used to convert an instance of L{subscan.OTFSubscan} into its representation
in the .lis file
"""

skydip_subscan = string.Template("${ID}\t" +
                                 "SKYDIP\t" +
                                 "${target_subscan}\t" +
                                 "${start_elevation}\t" +
                                 "${stop_elevation}\t" +
                                 "${duration}\t" +
                                 "${offset_frame}\t" +
                                 "${offset_lon}\t" +
                                 "${offset_lat}")
"""
Used to convert an instance of L{subscan.SkydipSubscan} into its representation
in the .lis file
"""

def format_layout(name, conf):
    """
    Format a layout dictionary for writing to .dat file
    @param name: layout name as in .lis file
    @param conf: layout configuration
    @type conf: dictionary
    """
    res = "%s {\n" % (name, )
    # Take subscans info from conf dictionary
    subscans = conf.pop("subscans", [])
    logger.debug("got subscans info %s" % (str(subscans),))
    #TODO: add subscans info in dat file
    for k, v in conf.items():
        res += "\t%s=%s\n" % (str(k), str(v),)
    res += "}\n\n"
    return res
