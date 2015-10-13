#coding=utf-8
import re
import logging
logger = logging.getLogger(__name__)
import validate

from astropy import units as u

from valid_angles import VAngle

dec_angle_pattern = "^[+-]?\d+(.\d+)?d$"
dec_angle_re = re.compile(dec_angle_pattern)
"""
Regular espression matching angle valid decimal representation
"""

dms_angle_pattern = "^(?P<deg>[+-]?\d{1,3}):" +\
                    "(?P<min>\d{2}):" +\
                    "(?P<sec>\d{2}(.\d+)?)$"
dms_angle_re = re.compile(dms_angle_pattern)
"""
Regular espression matching angle valid sexagesimal representation in degrees
units
"""

hms_angle_pattern = "^(?P<hour>[0-2]?\d)" +\
                    ":(?P<min>\d{2})" +\
                    ":(?P<sec>\d{2}(.\d+)?)h$"
hms_angle_re = re.compile(hms_angle_pattern)
"""
Regular espression matching angle valid sexagesimal representation in hour units
"""

class VdtAngleError(validate.ValidateError):
    """
    Raised when trying to parse a wrongly formatted angle
    """
    pass

def dms_to_angle(dms):
    """
    Get the angle from a tuple of numbers or strings giving its sexagesimal
    representation in degrees
    @param dms: (degrees, minutes, seconds)
    """
    angle_deg = int(dms[0])
    angle_min = int(dms[1])
    angle_sec = float(dms[2])
    if not 0 <= angle_min < 60:
        raise VdtAngleError("not a valid value for minutes: " + str(angle_min))
    if not 0 <= angle_sec < 60:
        raise VdtAngleError("not a valid value for seconds: " + str(angle_sec))
    return VAngle((angle_deg, angle_min, angle_sec), unit=u.deg)

def hms_to_angle(hms):
    """
    Get the angle from a tuple of numbers or strings giving its sexagesimal
    representation in hours
    @param hms: (degrees, minutes, seconds)
    """
    angle_hour = int(hms[0])
    angle_min = int(hms[1])
    angle_sec = float(hms[2])
    if not 0 <= angle_hour < 24:
        raise VdtAngleError("not a valid value for hours: " + str(angle_hour))
    if not 0 <= angle_min < 60:
        raise VdtAngleError("not a valid value for minutes: " + str(angle_min))
    if not 0 <= angle_sec < 60:
        raise VdtAngleError("not a valid value for seconds: " + str(angle_sec))
    return VAngle((angle_hour, angle_min, angle_sec), unit=u.hour)

def check_dec_angle(value):
    """
    Validating function for angle decimal representation.
    Used in the rich_validator
    """
    if isinstance(value, list):
        raise validate.ValidateError("expected value angle, found list")
    if not dec_angle_re.match(value):
        raise VdtAngleError("not a valid decimal angle: %s" % value)
    return VAngle(float(value[:-1]))

def check_dms_angle(value):
    """
    Validating function for angle sexagesimal representation in degrees.
    Used in the rich_validator
    """
    if isinstance(value, list):
        raise validate.ValidateError("expected value angle, found list")
    match = dms_angle_re.match(value)
    if not match:
        raise VdtAngleError("not a valid degrees angle: %s" % value)
    return dms_to_angle(match.groups())

def check_hms_angle(value):
    """
    Validating function for angle sexagesimal representation in hours.
    Used in the rich_validator
    """
    if isinstance(value, list):
        raise validate.ValidateError("expected value angle, found list")
    match = hms_angle_re.match(value)
    if not match:
        raise VdtAngleError("not a valid hour angle: %s" % value)
    return hms_to_angle(match.groups())

def check_angle(value):
    """
    validate a string to create an angles.Angle object
    tries in order: decimal, sexagesimal degrees and hours
    @return: the Angle object created
    @raise VdtAngleError: if value is not valid
    """
    try:
        a = check_dec_angle(value)
        logger.debug("got dec angle %s" % (a.fmt(),))
    except:
        try:
            a = check_dms_angle(value)
            logger.debug("got dms angle %s" % (a.fmt(),))
        except:
            try:
                a = check_hms_angle(value)
                logger.debug("got hms angle %s" % (a.fmt(),))
            except:
                raise
    return a

validate_options = {
    'angle' : check_angle,
    'dec_angle' : check_dec_angle,
    'dms_angle' : check_dms_angle,
    'hms_angle' : check_hms_angle,
}
"""
options added to the rich_validator and usable in .ini files
"""

