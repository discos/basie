import logging
logger = logging.getLogger(__name__)
import itertools
from numpy import ceil, floor

from basie import utils, frame
from basie.valid_angles import VAngle

from scanmode import ScanMode
from ..frame import Coord
import subscan

class MapScan(ScanMode):
    """
    MapScan superclass used for OTF and RASTER maps
    """
    def __init__(self, frame, start_point, scan_axis,
              length_x, length_y, spacing):
        """
        Constructor
        @param frame: scan frame
        @type frame: frame.Frame
        @param start_point: one of TL, TR, BL, BR
        @param scan_axis: one of LON LAT RA DEC AZ EL BOTH, the constant axis of
        each subscan
        @param length_x: map width in degrees
        @type length_x: VAngle
        @param length_y: map height in degrees
        @type length_y: VAngle
        @param spacing: separation between subsequent subscans
        @type spacing: VAngle
        """
        ScanMode.__init__(self)
        self.frame = frame
        self.start_point = start_point
        self.scan_axis = scan_axis
        self.length_x = length_x
        self.length_y = length_y
        self.spacing = spacing

    def _get_spacing(self, receiver, frequency):
        self.beamsize = VAngle(receiver.get_beamsize(max(frequency)))
        if receiver.is_multifeed() and receiver.has_derotator:
            #we can exploit multifeed derotator optimization 
            logger.info("applying multifeed derotator optimization for map generation")
            if not isinstance(self.spacing, VAngle):
                approx_spacing = self.beamsize / self.spacing
                scans_per_beam = ceil(receiver.interleave / approx_spacing)
                self.spacing = receiver.interleave / scans_per_beam
            else:
                scans_per_beam = floor(receiver.interleave / self.spacing)
            #this is necessary for tsys and offsets
            self.beamsize = receiver.feed_extent * 2
            #if scans_per_beam == 1:
            #    logger.warning("Rounding to two scans between each feed")
            #    scans_per_beam = 2
            #    self.spacing = receiver.interleave / scans_per_beam
            if scans_per_beam == 0:
                logger.warning("Spacing is too high for this recevier")
                scans_per_beam = 1
                self.spacing = 0
            major_spacing = recevier.feed_extent * 2 + receiver.interleave + self.spacing
            _offset_x = (-1 * (self.length_x / 2)) + receiver.feed_extent
            self.dimension_x = 0
            self.offset_x = []
            while (_offset_x + receiver.feed_extent) <= (self.length_x / 2):
                for i in range(scans_per_beam):
                    self.offset_x.append(_offset_x + i * self.spacing)
                _offset_x += major_spacing
            self.dimension_x = len(self.offset_x)
            _offset_y = (-1 * (self.length_y / 2)) + receiver.feed_extent
            self.dimension_y = 0
            self.offset_y = []
            while (_offset_y + recevier.feed_extent) <= (self.length_y / 2):
                for i in range(scans_per_beam):
                    self.offset_y.append(_offset_y + i * self.spacing)
                _offset_y += major_spacing
            self.dimension_y = len(self.offset_y)
        else:
            if not isinstance(self.spacing, VAngle):
                self.spacing = self.beamsize / self.spacing
            self.dimension_x = utils.ceil_to_odd(self.length_x.deg / self.spacing.deg)
            self.dimension_y = utils.ceil_to_odd(self.length_y.deg / self.spacing.deg)
            logger.debug("Scan {0:d} dim_x {1:f} dim_y {2:f}".format(self.ID, self.dimension_x,
                                               self.dimension_x))
            self.offset_x = [i * self.spacing
                             for i in range(int(-1 * (self.dimension_x // 2)), 
                                            int((self.dimension_x // 2) + 1))]
            self.offset_y = [i * self.spacing
                             for i in range(int(-1 * (self.dimension_y // 2)), 
                                            int((self.dimension_y // 2) + 1))]


class OTFMapScan(MapScan):
    def __init__(self, frame, start_point, scan_axis, 
                 length_x, length_y, spacing, speed):
        MapScan.__init__(self, frame, start_point,
                         scan_axis, length_x, length_y, spacing)
        self.speed = speed
        self.duration_x = length_x.deg / speed * 60
        self.duration_y = length_y.deg / speed * 60
    
    def _do_scan(self, _target, _receiver, _frequency):
        self._get_spacing(_receiver, _frequency)
        if self.scan_axis == "LON":
            self.unit_subscans = self.dimension_y
        elif self.scan_axis == "LAT":
            self.unit_subscans = self.dimension_x
        _subscans = []
        logger.debug("scan axis: %s" % (self.scan_axis,))

        if self.scan_axis == self.frame.lon_name or self.scan_axis == "LON":
            _const_axis = 'LAT'
            if self.start_point == "TL" or self.start_point == "TR":
                _offsets = reversed(self.offset_y)
            else:
                _offsets = self.offset_y
            if self.start_point == "TL" or self.start_point == "BL":
                if self.frame == frame.EQ or self.frame == frame.GAL: #RA and GAL-LON are reversed!!
                    _directions = ("DEC", "INC")
                else:
                    _directions = ("INC", "DEC")
            else:
                if self.frame == frame.EQ or self.frame == frame.GAL:
                    _directions = ("INC", "DEC")
                else:
                    _directions = ("DEC", "INC")
            for _offset, _direction in itertools.izip(_offsets,
                                                      itertools.cycle(_directions)):
                logger.debug("OTF: %d offset %s direction %s" % (self.ID,
                                                                 _offset,
                                                                 _direction))
                _subscans.append(subscan.get_cen_otf_tsys(_target,
                                                          self.duration_x,
                                                          self.length_x,
                                                          _offset,
                                                          _const_axis,
                                                          _direction,
                                                          self.frame,
                                                          self.beamsize))
        elif self.scan_axis == self.frame.lat_name or self.scan_axis == "LAT":
            _const_axis = 'LON'
            if self.start_point == "TR" or self.start_point == "BR":
                if self.frame == frame.EQ or self.frame == frame.GAL:
                    _offsets = self.offset_x
                else:
                    _offsets = reversed(self.offset_x)
            else:
                if self.frame == frame.EQ or self.frame == frame.GAL:
                    _offsets = reversed(self.offset_x)
                else:
                    _offsets = self.offset_x
            if self.start_point == "BL" or self.start_point == "BR":
                _directions = ("INC", "DEC")
            else:
                _directions = ("DEC", "INC")
            for _offset, _direction in itertools.izip(_offsets,
                                                      itertools.cycle(_directions)):
                logger.debug("OTF: %d offset %s direction %s" % (self.ID,
                                                                 _offset,
                                                                 _direction))
                _subscans.append(subscan.get_cen_otf_tsys(_target,
                                                          self.duration_y,
                                                          self.length_y,
                                                          _offset,
                                                          _const_axis,
                                                          _direction,
                                                          self.frame,
                                                          self.beamsize))
        return _subscans

class RasterMapScan(MapScan):
    def __init__(self, frame, start_point, scan_axis, 
                 length_x, length_y, spacing, duration):
        MapScan.__init__(self, frame, start_point, scan_axis,
                  length_x, length_y, spacing)
        self.duration = duration

    def _get_offsets(self):
        """
        Get ordered offsets for each point of the raster scan
        @return: [(X0, Y0), (X1, Y1) .... (Xdim, Ydim)]
        """
        res = [] #resulting offsets
        if self.start_point == "TL" or self.start_point == "BL":
            if self.frame == frame.EQ or self.frame == frame.GAL:
                xoffsets = list(reversed(self.offset_x))
            else:
                xoffsets = self.offset_x
        else:
            if self.frame == frame.EQ or self.frame == frame.GAL:
                xoffsets = self.offset_x
            else:
                xoffsets = list(reversed(self.offset_x))
        if self.start_point == "TL" or self.start_point == "TR":
            yoffsets = list(reversed(self.offset_y))
        else:
            yoffsets = self.offset_y

        if self.scan_axis == "LON" or self.scan_axis == self.frame.lon_name:
            for i, _y in enumerate(yoffsets):
                if i % 2 == 0:
                    _xoffsets = xoffsets
                else:
                    _xoffsets = reversed(xoffsets)
                for _x in _xoffsets:
                    res.append((_x, _y))
        elif self.scan_axis == "LAT" or self.scan_axis == self.frame.lat_name:
            for i, _x in enumerate(xoffsets):
                if i % 2 == 0:
                    _yoffsets = yoffsets
                else:
                    _yoffsets = reversed(yoffsets)
                for _y in _yoffsets:
                    res.append((_x, _y))
        for _x, _y in res:
            logger.debug("\toffset\t %f\t%f" % (_x.deg, _y.deg))
        return res

    def _do_scan(self, _target, _receiver, _frequency):
        self._get_spacing(_receiver, _frequency)
        self.extremes = list(itertools.product(
                                               [self.offset_x[0].deg,
                                                self.offset_x[-1].deg],
                                               [self.offset_y[0].deg,
                                                self.offset_y[-1].deg]
                                              ))
        self._offsets = self._get_offsets()
        _subscans = []
        for offset_lon, offset_lat in self._offsets:
            logger.debug("OFFSETS: %f %f" % (offset_lon.deg, offset_lat.deg))
            _offset = Coord(self.frame, offset_lon, offset_lat)
            _subscans.append(subscan.get_sid_tsys(_target, 
                                                  _offset,
                                                  self.extremes,
                                                  self.duration,
                                                  self.beamsize))
        return _subscans

