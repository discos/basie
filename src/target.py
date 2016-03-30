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
Module containig target objects definitions
exposed classes: 
    - Target 
    - ObservedTarget
"""

import logging
logger = logging.getLogger(__name__)

from persistent import Persistent

from valid_angles import VAngle
from . import frame as fr
from velocity import ZERO_VELOCITY
from errors import *

class Target(Persistent):
    def __init__(self, label, coord, velocity = ZERO_VELOCITY):
        """
        Constructor
        @param label: target name
        @param coord: source coordinates
        @type coord: frame.Coordinates
        @param velocity: target velocity
        @type velocity: velocity.Velocity
        """
        self.label = label
        self.coord = coord
        self.velocity = velocity
        if (self.coord.frame == fr.EQ and 
            not self.coord.lon.is_hour_angle() and
            self.coord.lon.sexa):
            logger.warning("Target %s specifies EQ frame but RA is not in hours" % (
                            self.label,))

    def __str__(self):
        _lon, _lat = self.coord.fmt()
        res = "target %s lon: %s lat: %s" % (self.label, _lon, _lat)
        return res

    def transform(self, dest_frame):
        """
        Tries to change coordinate frame
        @param dest_frame: the frame we want to change into
        @type dest_frame: frame.Frame or frame name as a string
        """
        if not isinstance(dest_frame, fr.Frame):
            dest_frame = fr.frames[dest_frame.upper()]
        logger.debug("transform coordinates of target %s from %s to %s" %
                     (self.label, self.coord.frame.name, dest_frame.name,))
        self.coord.transform(dest_frame)

    def check_consistency(self):
        """
        if FRAME = HOR and LON is hours => error
        if FRAME = EQ|GAL ==> 0 < deg < 360 per LON && -90 < deg < 90 per LAT
        (posso controllarlo dopo averli trasformati in angoli - occhio che si leggono
        anche le ore!!!
        if FRAME = HOR ==> 0 < deg < 360 per AZ && 0 < deg < 90 per EL
        """
        if self.coord.frame == fr.HOR:
            if self.coord.lon.fmt == "hms":
                raise ScheduleError("Horizontal frame does not accept longitude hours")
        if not (0 <= self.coord.lon.deg <= 360):
            raise ScheduleError("Longitude must be 0 <= lon <= 360")
        if self.coord.frame == fr.EQ or self.coord.frame == fr.GAL:
            if not (-90 <= self.coord.lat.deg <= 90):
                raise ScheduleError("Latitude must be -90 <= lat <= 90")
        else:
            if not (0 <= self.coord.lat.deg <= 90):
                raise ScheduleError("Latitude must be 0 <= lat <= 90")

class ObservedTarget(Target):
    def __init__(self, label, coord, offset, velocity=ZERO_VELOCITY, 
                 repetitions=1, tsys=1):
        """
        basically a target with velocity, tsys and repetitions added
        @type offset: frame.Coord
        @type velocity: velocity.Velocity
        @default velocity: ZERO_VELOCITY
        """
        Target.__init__(self, label, coord, velocity)
        self.repetitions = repetitions
        self.tsys = tsys
        self.offset_coord = offset

