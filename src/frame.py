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
Module incapsulating all coordinates logics. 
Depends on astropy for coordinate conversions between galactic and equatorial
systems.

exported classes:
    - Frame - a coordinate frame
    - Coord - coordinates with a frame
exported constants:
    - frames
    - EQ, GAL, HOR
    - axes
"""

import logging
logger = logging.getLogger(__name__)
import copy

from astropy import coordinates as coord

from .valid_angles import VAngle, ZERO_ANGLE
from .errors import *

class Frame(object):
    """
    Frame object containing coordinates names for a given frame
    """
    def __init__(self, name , lon, lat, offset, allocator):
        """
        Constructor
        @param name: one of EQ, GAL, HOR the frame system name
        @param lon: one of RA, LON, AZ longitude coordinate name
        @param lat: one of DEC, LAT, EL latitude coordinate name
        @param offset: the label used in the schedule to make an offset frame
        @param allocator: an astropy.coordinates reference system class
        """
        self.name = name
        self.lon_name = lon
        self.lat_name = lat
        self.offset_name = offset
        self.allocator = allocator

    @property
    def axes(self):
        """
        (self.lon_name, self.lat_name)
        """
        return (self.lon_name, self.lat_name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

EQ = Frame('EQ', 'RA', 'DEC', '-EQOFFS', coord.ICRS)
"""
Equaltorial coordinate frame
"""

GAL = Frame('GAL', 'LON', 'LAT', '-GALOFFS', coord.Galactic)
"""
Galactic coordinate frame
"""

HOR = Frame('HOR', 'AZ', 'EL', '-HOROFFS', coord.AltAz)
"""
Horizontal coordinate frame
"""

NULL = Frame('NULL', 'NULL', 'NULL', '-NULLOFFS', None)
"""
Empty frame, used sometimes as default when no frame is specified for a couple
of coordinates.
"""

frames = {
    'EQ' : EQ,
    'GAL' : GAL,
    'HOR' : HOR,
    'NULL': NULL,
}
"""
frames dictionary
"""

axes = ('LON', 'LAT', 'RA', 'DEC', 'AZ', 'EL', 'BOTH')
"""
All possible value for axis label, including \"BOTH\"
"""

class Coord(object):
    """
    Stores a coordinate couple associated with their reference frame and epoch.
    @param frame: a coordinate frame
    @type frame: Frame
    @param lon: longitude component
    @type lon: VAngle
    @param lat: latitude component
    @type lat: VAngle
    @param epoch: coordinates epoch defaults to j2000
    """
    def __init__(self, frame, lon, lat, epoch="j2000"):
        self.frame = frame
        self.epoch = epoch
        if not isinstance(lon, VAngle):
            self.lon = VAngle(lon)
        else:
            self.lon = lon
        if not isinstance(lat, VAngle):
            self.lat = VAngle(lat)
        else:
            self.lat = lat
    
    def __lt__(self, other):
        if not isinstance(other, Coord):
            return NotImplemented
        if not self.frame == other.frame:
            raise CoordinateError("cannot compare coordinates of different frames: %s & %s" 
                                  % (self.frame.name, other.frame.name))
        #TODO: should we try and force coordinate conversion?
        return ((self.lon.deg, self.lat.deg) <
                (other.lon.deg, other.lat.deg))
    
    def __gt__(self, other):
        return not self.__lt__(other)

    def __eq__(self, other):
        return not self.__lt__(other) and not other.__lt__(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __str__(self):
        res = "%s lon: %s lat: %s" % (self.frame.name, 
                                      self.lon.fmt(),
                                      self.lat.fmt(),
                                     )
        return res

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if not isinstance(other, Coord):
            raise CoordinateError("cannot sum Coord with object of type: %s" %
                                  type(other))
        if self.is_null():
            return other
        if other.is_null():
            return self
        _other = copy.deepcopy(other)
        if self.frame == NULL:
            dest_frame = other.frame
        else:
            dest_frame = self.frame
            if not _other.frame == NULL:
                _other.transform(self.frame)
        return Coord(dest_frame, 
                     self.lon + _other.lon,
                     self.lat + _other.lat)

    def __sub__(self, other):
        if not isinstance(other, Coord):
            raise CoordinateError("cannot sum Coord with object of type: %s" %
                                  type(other))
        if self.is_null():
            return other
        if other.is_null():
            return self
        _other = copy.deepcopy(other)
        if self.frame == NULL:
            dest_frame = other.frame
        else:
            dest_frame = self.frame
            if not _other.frame == NULL:
                _other.transform(self.frame)
        return Coord(dest_frame, 
                     self.lon - _other.lon,
                     self.lat - _other.lat)

    def is_null(self):
        """
        Tell if this coordinate pair evaluates to something or not. 
        @return True: if both coordinates are 0.0 
        @return False: otherwise
        """
        if (
            (self.lat == ZERO_ANGLE) and 
            (self.lon == ZERO_ANGLE)):
            return True
        return False

    def transform(self, dest_frame):
        """
        conversion between different coordinate frame systems
        @param dest_frame: the output frame system 
        @type dest_frame: Frame
        """
        logger.debug("transofrm coordinates from %s to %s" % (self.frame.name,
                                                              dest_frame.name))
        if dest_frame == self.frame:
            return #nothing to do 
        legal = True
        #astro_coord = self.frame.allocator(self.lon, self.lat)
        astro_coord = coord.SkyCoord(self.lon, self.lat, frame=self.frame.allocator)
        if self.frame == EQ:
            if dest_frame == GAL:
                self.lon = VAngle(astro_coord.galactic.data.lon)
                self.lat = VAngle(astro_coord.galactic.data.lat)
                self.frame = GAL
            else:
                legal = False
        elif self.frame == GAL:
            if dest_frame == EQ:
                self.lon = VAngle(astro_coord.icrs.data.lon)
                self.lat = VAngle(astro_coord.icrs.data.lat)
                self.frame = EQ
            else:
                legal = False
        else: #self.frame == frame.HOR
            legal = False #cannot convert to celestial coordinates without date
        if not legal:
            msg = "Cannot convert coordinates from %s to %s" % (self.frame.name, dest_frame.name,)
            logger.error(msg)
            raise CoordinateError(msg)

NULL_COORD = Coord(NULL, ZERO_ANGLE, ZERO_ANGLE)
