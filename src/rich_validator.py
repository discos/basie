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
This module extends the validate options used to parse schedule creator
arguments from configuration file.
In particular it adds new possible instances to be used in the .ini schemas
files.
"""

import logging
logger = logging.getLogger(__name__)

import os
import re
import datetime
import configobj
import validate as v

import angle_parser
import frame
from scanmode import *
import utils
from backend import BackendFactory

valid_list_element = re.compile("\[.+\]|[^\s,]+")
"""
regular expression matching list items separated by whitespace characters or
\',\' items enclosed in square brackets are kept intact.
"""

valid_nodding_element = re.compile("(\d*)(a|b)(_cal)?")
"""
regular expression matching valid position switch geometries
"""

valid_onoff_element = re.compile("(\d*)(on|off)(_cal)?")
"""
regular expression matching valid onoff geometries
"""

def string2list(value):
    """
    @param value: a list of items separated by \',\' or whitespaces
    @type value: string
    @return: [first, second, third ... ]
    """
    value_list = valid_list_element.findall(value)
    return value_list

def check_frame(value):
    """
    Convert a string to a frame.Frame instance.
    Used as a validating function
    """
    if isinstance(value, list):
        raise v.ValidateError("expected frame value, found list")
    value = value.upper()
    if not value in frame.frames:
        raise v.ValidateError("%s is not a valid frame" % (value,))
    return frame.frames[value]

def check_vdef(value):
    if isinstance(value, list):
        raise v.ValidateError("expected frame value, found list")
    _value = value.upper()
    if not _value in velocity.VDEFS:
        raise v.ValidateError("%s is not a valid velocity definition" % (_value,))
    return _value

def check_vref(value):
    if isinstance(value, list):
        raise v.ValidateError("expected frame value, found list")
    _value = value.upper()
    if not _value in velocity.VREFS:
        raise v.ValidateError("%s is not a valid velocity reference" % (_value,))
    return _value

def check_cross_scan(value):
    if not isinstance(value, list):
        raise v.ValidateError("expected list, found  %s" % (value,))
    _frame = check_frame(value[0])
    length = angle_parser.check_angle(value[1])
    speed = v.is_float(value[2])
    return CrossScan(_frame, length, speed)

def check_otf_map(value):
    if not isinstance(value, list):
        raise v.ValidateError("expected list, found  %s" % (value,))
    _frame = check_frame(value[0]) 
    scan_axis = value[1].upper()
    logger.debug("scan axis: %s" % (scan_axis,))
    if not scan_axis in frame.axes:
        raise v.ValidateError("not a valid axis: %s" % (scan_axis,))
    start_point = value[2].upper()
    if not start_point in START_POINTS:
        raise v.ValidateError("not a valid start point: %s" % (start_point,))
    length_x = angle_parser.check_angle(value[3])
    length_y = angle_parser.check_angle(value[4])
    speed = v.is_float(value[5], min=0)
    scans_per_beam = v.is_integer(value[6], min=1)
    if scan_axis == "BOTH":
        logger.debug("exploding into separate scans")
        return (OTFMapScan(_frame, start_point, _frame.lon_name, length_x, length_y,
                           scans_per_beam, speed),
                OTFMapScan(_frame, start_point, _frame.lat_name, length_x, length_y,
                           scans_per_beam, speed))
    else:
        logger.debug("got otf map")
        return OTFMapScan(_frame, start_point, scan_axis, length_x, length_y,
                           scans_per_beam, speed)

def check_raster_map(value):
    if not isinstance(value, list):
        raise v.ValidateError("expected list, found  %s" % (value,))
    _frame = check_frame(value[0]) 
    scan_axis = value[1].upper()
    if not scan_axis in frame.axes:
        raise v.ValidateError("not a valid axis: %s" % (scan_axis,))
    start_point = value[2].upper()
    if not start_point in START_POINTS:
        raise v.ValidateError("not a valid start point: %s" % (start_point,))
    length_x = angle_parser.check_angle(value[3])
    length_y = angle_parser.check_angle(value[4])
    duration = v.is_float(value[5], min=0)
    points_per_beam = v.is_integer(value[6], min=1)
    return RasterMapScan(_frame, start_point, scan_axis, length_x, length_y,
                       points_per_beam, duration)

def check_nodding_sequence(value):
    if not isinstance(value, list):
        value = string2list(value.lower())
    nodding_elements = []
    for val in value:
        m = valid_nodding_element.match(val)
        if not m:
            raise v.ValidateError("not a valid position switch element %s" %
                    (val, ))
        if m.groups()[0]:
            repetitions = int(m.groups()[0])
        else:
            repetitions = 1
        on_feed = m.groups()[1]
        if m.groups()[2]:
            is_cal = True
        else:
            is_cal = False
        nodding_elements.append((repetitions, on_feed, is_cal))
    return nodding_elements

def check_nodding(value):
    if not isinstance(value, list):
        raise v.ValidateError("expected list, found  %s" % (value,))
    feed_a = v.is_integer(value[0], min=0)
    feed_b = v.is_integer(value[1], min=0)
    duration = v.is_float(value[2], min=0)
    sequence = check_nodding_sequence(value[3][1:-1]) #strip [ and ]
    return NoddingScan((feed_a, feed_b), duration, sequence)

def check_onoff_sequence(value):
    if not isinstance(value, list):
        value = string2list(value.lower())
    onoff_elements = []
    for val in value:
        m = valid_onoff_element.match(val)
        if not m:
            raise v.ValidateError("not a valid onoff element: %s" % (val, ))
        if m.groups()[0]:
            repetitions = int(m.groups()[0])
        else:
            repetitions = 1
        subscan_type = m.groups()[1]
        if m.groups()[2]:
            is_cal = True
        else:
            is_cal = False
        onoff_elements.append((repetitions, subscan_type, is_cal))
    return onoff_elements

def check_onoff(value):
    if not isinstance(value, list):
        raise v.ValidateError("expected list, found  %s" % (value,))
    duration = v.is_float(value[0], min=0)
    offset_frame = check_frame(value[1]) 
    offset_lon = angle_parser.check_angle(value[2])
    offset_lat = angle_parser.check_angle(value[3])
    sequence = check_onoff_sequence(value[4][1:-1]) #strip [ and ]
    return OnOffScan(duration, offset_lon, offset_lat, offset_frame, sequence)

def check_scantype(value):
    logger.info("parsing scan line: %s" % (value,))
    if isinstance(value, list):
        #this is aginst a bug in the validate module
        #AKA a brutal workaround
        value = ' '.join(value)
    value = string2list(value)
    logger.debug("got value: %s" % (value,))
    scantype = value[0].upper()
    if scantype == "CROSS":
        return check_cross_scan(value[1:])
    elif scantype == "OTFMAP":
        return check_otf_map(value[1:])
    elif scantype == "RASTERMAP":
        return check_raster_map(value[1:])
    elif scantype == "ONOFF":
        return check_onoff(value[1:])
    elif scantype == "NODDING":
        return check_nodding(value[1:])
    raise v.ValidateError("unknow scan type %s" % (scantype,))

def check_file(value):
    if isinstance(value, list):
        raise v.ValidateError("expected value filename, found list")
    if not os.path.isfile(value):
        raise v.ValidateError("%s is not a valid file" % (value,))
    return value

filename_pattern = re.compile("^[" + os.sep + "_a-zA-Z0-9.-]+$")
def check_filename(value):
    if isinstance(value, list):
        raise v.ValidateError("expected value filename, found list")
    if not filename_pattern.match(value):
        raise v.ValidateError("not a valid filename: %s" % (value,))
    return value

date_pattern = re.compile("^\d{2}-\d{2}-\d{4}")
def check_date(value):
    if isinstance(value, list):
        raise v.ValidateError("expected date value, found list")
    if not date_pattern.match(value):
        raise v.ValidateError("not a valid date format: %s" % (value,))
    try:
        date = datetime.datetime.strptime(value, "%d-%m-%Y")
        date = date.date()
    except:
        raise v.ValidateError("not a valid date: %s" % (value,))
    return date

def check_future_date(value):
    date = check_date(value)
    if date < datetime.date.today():
        raise v.ValidateError("date %s is in the past" % (value,))
    return date

valid_types = {
    'frame' : check_frame,
    'scantype' : check_scantype,
    'file' : check_file,
    'filename' : check_filename,
    'date' : check_date,
    'future_date' : check_future_date,
}

valid_types.update(angle_parser.validate_options)
rich_validator = v.Validator(valid_types)


def validate(filename, specfilename):#, error_stream=sys.stderr):
    conf = configobj.ConfigObj(filename, configspec=specfilename)
    res = conf.validate(rich_validator, preserve_errors=True)
    if not res:
        flat_errs = configobj.flatten_errors(conf, res)
        for _, var, ex in flat_errs:
            logger.error("%s : %s\n" % (var, str(ex)))
        raise v.ValidateError("Could not validate %s vs %s" % (filename, specfilename))
    for k,v in conf["backends"].iteritems():
        v["name"] = k
        conf["backends"][k] = BackendFactory(v)    
    return conf

def validate_configuration(filename):
    return validate(filename, os.path.join(utils.SCHEMA_DIR, "schedule.ini"))

