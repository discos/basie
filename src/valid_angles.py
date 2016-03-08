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
This module implements logics related to angle representations and calculation
inside the schedule creator.
It enriches the Angle class defined in astropy.coordinates.Angle adding validating
options to the validate module and conversions from and to string.
"""

import logging
logger = logging.getLogger(__name__)

from astropy import units as u
from astropy.coordinates import Angle

ANGLE_DECIMALS = 4
"""
CONSTANT. Decimal angles digits used in string fomratting
"""

SEXA_SEPARATOR = ':'
"""
CONSTANT. separator used in angle hour and sexagesimal representation
"""

class VAngle(Angle):
    def __new__(cls, angle, unit=u.deg, wrap_angle=360 * u.deg, **kwargs):
        self = super(VAngle, cls).__new__(cls, angle, unit=unit, **kwargs)
        self.original_unit = unit
        if unit == u.hour or isinstance(angle, tuple):
            self.sexa = True
        else:
            self.sexa = False
        return self

    def __init__(self, *args, **kwargs):
        super(VAngle, self).__init__(*args, **kwargs)

    def __array_finalize__(self, obj):
        super(VAngle, self).__array_finalize__(obj)
        if obj is None:return
        self.original_unit = getattr(obj, "original_unit", None)
        self.sexa = getattr(obj, "sexa", None)

    def __copy__(self):
        res = VAngle(self.deg)
        res.original_unit = self.original_unit
        res.sexa = self.sexa
        return res

    def __deepcopy__(self, *args):
        return self.__copy__()

    def __str__(self):
        return self.fmt()

    def fmt_dec(self):
        """
        Return the decimal string representation of the angle
        """
        _a_str = self.to_string(unit=u.deg, decimal=True, precision=ANGLE_DECIMALS)
        return _a_str + "d"

    def fmt_hms(self):
        """
        Return the sexagesimal string representation of the angle in hours
        """
        _a_str = self.to_string(unit=u.hour, sep=SEXA_SEPARATOR, pad=True, 
                              precision=ANGLE_DECIMALS)
        return _a_str + "h"

    def fmt_dms(self):
        """
        Return the sexagesimal string representation of the angle
        """
        _a_str = self.to_string(unit=u.deg, sep=SEXA_SEPARATOR, precision=ANGLE_DECIMALS)
        return _a_str

    def fmt(self):
        """
        Return the string representation of the angle according to its original
        format
        """
        if self.original_unit == u.hour:
            return self.fmt_hms()
        elif self.sexa:
            return self.fmt_dms()
        else:
            return self.fmt_dec()

    def is_hour_angle(self):
        return self.original_unit == u.hour


ZERO_ANGLE = VAngle(0.0)
"""
CONSTANT, used in schedule creator to represent the zero angle.
"""
