#coding=utf-8

import re
import logging
logger = logging.getLogger(__name__)

import valid_angles
from valid_angles import VAngle
import angle_parser
import rich_validator
from target import ObservedTarget
import frame
import velocity

"""
string pattern identifying an option.
Matches everything separated by a \'=\' sign excluding whitespaces
"""
OPTION_RE = "(?P<opt>\S+)\s*=\s*(?P<val>\S+)\s*"

"""
string pattern identifying a target line.
The line must be composed of \'label\' \'scantype\' \'frame\' \'longitude\'
\'latitude\' and multiple \'key = value\' optional parameters.
"""
TARGET_RE = "^(?P<label>\S+)\s+" + \
            "(?P<scantype>\S+)\s+" + \
            "(?P<frame>eq|hor|gal)\s+" +\
            "(?P<longitude>\S+)\s+" +\
            "(?P<latitude>\S+)\s*" +\
            "(?P<optionals>.*)$"

TARGET_PATTERN = re.compile(TARGET_RE, re.I)
OPTION_PATTERN = re.compile(OPTION_RE)

def _parse_options(line):
    """
    parse optional parameters from target line. 
    Options are specified as key-value pairs, key can be one of: 
    repetitions, tsys, offset_frame, offset_lon, offset_lat
    """
    options = {}
    matches = OPTION_PATTERN.findall(line)
    for key, val in matches:
        if key == 'offset_lon':
            options['offset_lon'] = angle_parser.check_dec_angle(val)
        elif key == 'offset_lat':
            options['offset_lat'] = angle_parser.check_dec_angle(val)
        elif key == 'tsys':
            options['tsys'] = int(val)
        elif key == 'repetitions':
            options['repetitions'] = int(val)
        elif key == 'offset_frame':
            options['offset_frame'] = rich_validator.check_frame(val)
        elif key == 'vframe':
            options['vframe'] = rich_validator.check_vframe(val)
        elif key == 'vdef':
            options['vdef'] = rich_validator.check_vdef(val)
        elif key == 'svel':
            options['svel'] = float(val)
        elif key == ['derot']:
            options['derot'] = rich_validator.check_angle(val)
    return options

def _parse_target_line(line):
    """
    Validate and parse a line of a txt file specifying a target
    of the schedule
    """
    matches = TARGET_PATTERN.match(line)
    if not matches:
        logger.warning("invalid target line: " + line)
        return None, None
    else:
        logger.info("parsing target line: " + line)
        target_args = matches.groupdict()
        option_string = target_args.pop('optionals')
        option_args = (_parse_options(option_string))
        obs_target = ObservedTarget(
                                label = target_args['label'],
                                coord = frame.Coord(
                                        rich_validator.check_frame(target_args['frame']),
                                        angle_parser.check_angle(target_args['longitude']),
                                        angle_parser.check_angle(target_args['latitude']),
                                                   ),
                                offset = frame.Coord(
                                        option_args.get("offset_frame",
                                                        frame.NULL),
                                        option_args.get("offset_lon",
                                                        VAngle(0.0)),
                                        option_args.get("offset_lat",
                                                        VAngle(0.0)),
                                                    ),
                                vel = velocity.Velocity(), #TODO: implement this!!
                                repetitions = option_args.get('repetitions',
                                                              None),
                                tsys = option_args.get('tsys', None),
                               )
        return target_args['scantype'], obs_target

def parse_file(filename, check_values=True):
    """
    Parse a target txt file into a list of ObservedTarget objects associated to
    their corresponding scan type.
    """
    with open(filename, "r") as _file:
        lines = _file.readlines()
    #escapes whitespaces and special chars
    lines = [l.strip() for l in lines]
    #remove commented and empty lines
    lines = [l for l in lines if ((not l.startswith("#")) and (not l == ""))]
    targets = [] #targets is a list so that it mantains the same ordering as in the file lines
    for l in lines:
        scantype, target = _parse_target_line(l)
        if target: # not None
            if check_values:
                target.check_consistency()
            targets.append((target, scantype, l))
    return targets

