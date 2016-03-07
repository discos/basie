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
Subscan related classes and funcions:
B{Classes}
    - SubscanError
    - Subscan: a generic subscan 
        - OTFSubscan: a generic on the fly subscan
        - SiderealSubscan: a generic sidereal subscan
B{Functions}
Used to get subscan classes instances. Subscans are often returned in couples
together with their associated Tsys sidereal subscan.
    - get_cen_otf_subscan
    - get_ss_otf_subscan (not implemented)
    - get_sidereal_subscan
    - get_tsys_subscan
    - get_couple_subscan
    - get_sid_couple_subscan
"""

import logging
logger = logging.getLogger(__name__)
import copy

from persistent import Persistent

from ..valid_angles import VAngle
from .. import templates, frame, utils, procedures
from ..errors import ScheduleError, ScanError
from ..frame import NULL_COORD, Coord, EQ, GAL, HOR, NULL


TSYS_SIGMA = 5
"""
Used for calculating TSYS subscans coordinate offsets as TSYS_SIGMA * beamsize
"""

class Subscan(Persistent):
    """
    Generic subscan. Contains common subscan attributes and is meant to be
    override by specific subscan classes
    """
    ID = 1 #static counter attribute 
    def __init__(self, _target, duration=0.0, is_tsys=False,
            is_cal=False):
        """
        Constructor.
        Give the subscan a unique ID.
        """
        self.ID = Subscan.ID #This value will be the same found in the lis file
        Subscan.ID += 1
        self.target = _target
        self.is_tsys = is_tsys
        self.duration = duration
        #self.SEQ_ID = 0 #position in the respective scan, default value 0
        self.is_cal = is_cal
        if self.is_cal and self.is_tsys:
            raise ScheduleError("Subscan cannot be tsys and cal at the same time")
        if self.is_cal:
            self.pre_procedure = procedures.CALON
            self.post_procedure = procedures.CALOFF
        elif self.is_tsys:
            self.pre_procedure = procedures.NULL
            self.post_procedure = procedures.TSYS
        else: #Default
            self.pre_procedure = procedures.NULL
            self.post_procedure = procedures.NULL

    def add_post_procedure(self, proc):
        if self.post_procedure == procedures.NULL:
            self.post_procedure = proc
        else:
            self.post_procedure = self.post_procedure + proc

    def add_pre_procedure(self, proc):
        if self.pre_procedure == procedures.NULL:
            self.pre_procedure = proc
        else:
            self.pre_procedure = self.pre_procedure + proc

    def __hash__(self):
        return self.ID

    def __cmp__(self, other):
        return cmp(self.ID, other.ID)

    def __eq__(self, other):
        return self.ID == other.ID

class OTFSubscan(Subscan):
    """
    On the flight sunbscan class
    """
    def __init__(self, _target, lon2, lat2, descr, scan_frame,
                 geom, direction, duration, is_tsys=False, is_cal=False):
        """
        Constructor.
        @type lon2: VAngle
        @type lat2: VAngle
        """
        Subscan.__init__(self, _target, duration, is_tsys, is_cal)
        self.typename = "OTF"
        self.scan_frame = scan_frame
        #check that offset frame and scan frame are equal
        if self.target.offset_coord.frame == frame.NULL:#default behaviour
            self.target.offset_coord.frame = self.scan_frame
        if not self.target.offset_coord.frame == self.scan_frame:
            msg = "offset frame %s different from scan frame %s" % (self.target.offset_coord.frame.name, self.scan_frame)
            logger.debug(msg)
            raise ScheduleError(msg)
        self.lon2 = lon2
        self.lat2 = lat2
        self.descr = descr.upper()
        #check consistnecy of frames specifications
        #we already know that offset and scan 
        if not self.target.coord.frame == self.scan_frame:#possible mistake!
            logger.warning("SUBSCAN %d : scan_frame and coordinates_frame are different" % (self.ID,))
            if (self.target.coord.frame == frame.EQ and 
                self.descr == "CEN" and 
                self.scan_frame == frame.HOR):
                pass #OK - only success condition
            else:
                raise ScheduleError("not compatible frame types")#very bad!
        self.geom = geom
        self.direction = direction

    def __str__(self):
        return templates.otf_subscan.substitute(
                    dict(
                         ID = self.ID,
                         target = self.target.label,
                         lon1 = self.target.coord.lon.fmt(),
                         lat1 = self.target.coord.lat.fmt(),
                         lon2 = self.lon2.fmt(),
                         lat2 = self.lat2.fmt(),
                         frame = self.target.coord.frame.name,
                         s_frame = self.scan_frame.name,
                         geom = self.geom,
                         descr = self.descr,
                         direction = self.direction,
                         duration = str(self.duration),
                         offset_frame = self.target.offset_coord.frame.offset_name,
                         offset_lon = self.target.offset_coord.lon.fmt(),
                         offset_lat = self.target.offset_coord.lat.fmt(),
                         vel = str(self.target.velocity),
                    )
                )

class SiderealSubscan(Subscan):
    def __init__(self, _target, duration=0.0, is_tsys=False, is_cal=False):
        Subscan.__init__(self, _target, duration, is_tsys, is_cal)
        self.typename = "SID"

    def __str__(self):
        if self.target.coord.frame == frame.EQ:
            _epoch = str(self.target.coord.epoch) + '\t'
        else:
            _epoch = ""
        return templates.sidereal_subscan.substitute(
            dict(
                 ID = self.ID,
                 target = self.target.label,
                 frame = self.target.coord.frame.name,
                 longitude = self.target.coord.lon.fmt(),
                 latitude = self.target.coord.lat.fmt(),
                 epoch = _epoch,
                 offset_frame = self.target.offset_coord.frame.offset_name,
                 offset_lon = self.target.offset_coord.lon.fmt(),
                 offset_lat = self.target.offset_coord.lat.fmt(),
                 vel = str(self.target.velocity),
            )
        )

def get_cen_otf(_target, 
                duration, 
                length, 
                offset, 
                const_axis, 
                direction,
                scan_frame):
    """
    Get an I{OTF} subscan with description I{CEN}.
    @type length: VAngle
    @type offset: VAngle
    @return: an L{OTFSubscan} instance
    """
    __target = copy.deepcopy(_target)
    if const_axis == "LON":
        __target.offset_coord.lon = _target.offset_coord.lon + offset
        logger.debug("offset lon: %f" % (__target.offset_coord.lon.deg,))
        lon2 = VAngle(0.0)
        lat2 = length
    elif const_axis == "LAT":
        __target.offset_coord.lat = _target.offset_coord.lat + offset
        logger.debug("offset lat: %f" % (__target.offset_coord.lat.deg,))
        lon2 = length
        lat2 = VAngle(0.0)
    attr = dict(_target = __target,
                descr = 'CEN',
                duration = duration,
                lon2 = lon2,
                lat2 = lat2,
                geom = const_axis,
                direction = direction,
                scan_frame = scan_frame,
               )
    return OTFSubscan(**attr)

def get_ss_otf(*args, **kwargs):
    """
    @raise NotImplementedError: we still have no useful case for implemting this
    function
    """
    raise NotImplementedError("is there any useful case for implementing this?")

def get_sidereal(_target, offset=NULL_COORD, duration=0.0,
        is_tsys=False, is_cal=False):
    """
    @param _target: the subscan target
    @type _target: target.Target
    @param offset_lon: additional longitude offset
    @type offset_lon: VAngle
    @param offset_lat: additional latitude offset
    @type offset_lat: VAngle
    """
    __target = copy.deepcopy(_target)
    #import ipdb;ipdb.set_trace()
    __target.offset_coord += offset
    return SiderealSubscan(__target, duration, is_tsys, is_cal)

def get_tsys(_target, offset, duration=0.0):
    """
    Get a Tsys subscan.
    This basically returns a SIDEREAL subscan where source name is I{Tsys} and
    duration is I{0.0}
    @type offset_lon: VAngle
    @type offset_lat: VAngle
    """
    __target = copy.deepcopy(_target)
    __target.label = "Tsys"
    st = get_sidereal(__target, offset, duration=0.0,
                              is_tsys=True)
    st.post_procedure = procedures.TSYS
    return st

def get_cen_otf_tsys(_target, 
                     duration, 
                     length, 
                     offset, 
                     const_axis, 
                     direction,
                     scan_frame, 
                     beamsize):
    """
    Get a couple composed of a CEN_OTF subscan and its relative SIDEREAL TSYS
    subscan.
    @return: (otf_subscan, tsys_subscan)
    @type length: VAngle
    @type offset: Coord
    @type beamsize: VAngle
    """
    logger.debug("get couple subscan offset: %s " % (offset,))
    negative_offset = VAngle(-1 * (length.deg / 2.0 + beamsize.deg * TSYS_SIGMA))
    positive_offset = VAngle(length.deg / 2.0 + beamsize.deg * TSYS_SIGMA)
    if const_axis == "LAT":
        _offset_lat = offset
        if direction == "INC":
            _offset_lon = negative_offset
        elif direction == "DEC":
            _offset_lon = positive_offset
    elif const_axis == "LON":
        _offset_lon = offset
        if direction == "INC":
            _offset_lat = negative_offset
        elif direction == "DEC":
            _offset_lat = positive_offset
    _offset = Coord(scan_frame, _offset_lon, _offset_lat)
    ss = get_cen_otf(_target, duration, length, offset, const_axis, direction,
                    scan_frame)
    st = get_tsys(_target, _offset)
    return ss, st

def get_sid_tsys(_target, 
                 offset,
                 extremes, 
                 duration,
                 beamsize):
    """
    Get a couple of sidereal subscans, where the first is an actual subscan and the
    second is a tsys subscan obtained pointing the antenna out of a rectangular
    polygon containing the source.
    @param _target: the source to be observed
    @type _target: L{target.Target}
    @param offset_lon: longitude offset of the subscan
    @type offset_lon: VAngle
    @param offset_lat: latitude offset of the subscan
    @type offset_lat: VAngle
    @param extremes: An array containing the offsets of the extremes of the rectangular polygon
    containing the source (i.e. the borders of a raster map) 
    @type extremes: [(x0,y0), (x1,y1), (x2,y2), (x3,y3)]
    @param duration: subscan duration (Sec. ) 
    @type duration: float
    @param beamsize: beam size used to calculated tsys subscan offsets
    @type beamsize: VAngle
    """
    ss = get_sidereal(_target, offset, duration)
    tsys_offsets = utils.extrude_from_rectangle(offset.lon.deg, 
                                                offset.lat.deg,
                                                extremes, 
                                                beamsize.deg * TSYS_SIGMA)
    _offsets = Coord(offset.frame,
                     VAngle(tsys_offsets[0]),
                     VAngle(tsys_offsets[1]))
    st = get_tsys(_target, _offsets)
    return ss, st

def get_off_tsys(_target,
                 offset,
                 extremes,
                 duration,
                 beamsize):
    extremes_offsets = utils.extrude_from_rectangle(offset.lon.deg, 
                                                offset.lat.deg,
                                                extremes, 
                                                beamsize.deg * TSYS_SIGMA)
    _offsets = Coord(offset.frame,
                     VAngle(extremes_offsets[0]),
                     VAngle(extremes_offsets[1]))
    ss = get_sidereal(_target, _offsets, duration)
    st = get_tsys(_target, _offsets)
    return ss, st

