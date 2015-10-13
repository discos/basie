import logging
logger = logging.getLogger(__name__)
import itertools

from schedulecreator import utils, frame
from schedulecreator.valid_angles import VAngle

from scanmode import ScanMode
import subscan

class MapScan(ScanMode):
    """
    MapScan superclass used for OTF and RASTER maps
    """
    def __init__(self, frame, start_point, scan_axis,
              length_x, length_y, scans_per_beam):
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
        @param scans_per_beam: number of subscans per beamsize
        @type scans_per_beam: int
        """
        ScanMode.__init__(self)
        self.frame = frame
        self.start_point = start_point
        self.scan_axis = scan_axis
        self.length_x = length_x
        self.length_y = length_y
        self.scans_per_beam = scans_per_beam

    def _get_spacing(self, receiver, frequency):
        self.beamsize = receiver.get_beamsize(frequency)
        if receiver.is_multifeed() and receiver.has_derotator:
            self.spacing = receiver.feed_extent / self.scans_per_beam
            self.dimension_x = utils.ceil_to_odd((self.length_x /
                                                  self.spacing).value)
            self.dimension_y = utils.ceil_to_odd((self.length_y /
                                                  self.spacing).value)
            logger.debug("%d dim_x %d dim_y %d" % (self.ID, self.dimension_x,
                                               self.dimension_x))
            #we can exploit multifeed derotator optimization 
            logger.info("applying multifeed derotator optimization for map generation")
            logger.info("we are considering derotator extend instead of beamsize")
            empty_subscans = self.scans_per_beam * receiver.nfeed
            self.offset_x = []
            self.offset_y = []
            offset_x = -1 * self.dimension_x // 2 * self.spacing
            while (offset_x < ((self.length_x / 2.0) 
                                + receiver.feed_extent)):
                for i in range(self.scans_per_beam): 
                    self.offset_x.append(offset_x + i * self.spacing)
                offset_x = offset_x + receiver.nfeed * receiver.feed_extent
            offset_y = -1 * self.dimension_y // 2 * self.spacing
            while (offset_y < ((self.length_y / 2.0) 
                               + receiver.feed_extent)):
                for i in range(self.scans_per_beam): 
                    self.offset_y.append(offset_y + i * self.spacing)
                offset_y = offset_y + receiver.nfeed * receiver.feed_extent
        else:
            self.spacing = self.beamsize / self.scans_per_beam
            self.dimension_x = utils.ceil_to_odd(self.length_x.deg / self.spacing.deg)
            self.dimension_y = utils.ceil_to_odd(self.length_y.deg / self.spacing.deg)
            logger.debug("%d dim_x %d dim_y %d" % (self.ID, self.dimension_x,
                                               self.dimension_x))
            self.offset_x = [i * self.spacing
                             for i in range(-1 * (self.dimension_x // 2), 
                                            (self.dimension_x // 2) + 1)]
            self.offset_y = [i * self.spacing.deg
                             for i in range(-1 * (self.dimension_y // 2), 
                                            (self.dimension_y // 2) + 1)]

class OTFMapScan(MapScan):
    def __init__(self, frame, start_point, scan_axis, 
                 length_x, length_y, spacing, speed):
        MapScan.__init__(self, frame, start_point,
                         scan_axis, length_x, length_y, spacing)
        self.speed = speed
        self.duration_x = length_x.deg / speed * 60
        self.duration_y = length_y.deg / speed * 60
        if scan_axis == "LON":
            self.unit_subscans = self.dimension_y
        elif scan_axis == "LAT":
            self.unit_subscans = self.dimension_x
    
    def _do_scan(self, _target, _receiver, _frequency):
        self._get_spacing(_receiver, _frequency)
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
        self.extremes = list(itertools.product(
                                               [self.offset_x[0].deg,
                                                self.offset_x[-1].deg],
                                               [self.offset_y[0].deg,
                                                self.offset_y[-1].deg]
                                              ))
        self._offsets = self._get_offsets()

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
        _subscans = []
        for offset_lon, offset_lat in self._offsets:
            for _x, _y in self._offsets:
                logger.debug("\toffset\t %f\t%f" % (_x.deg, _y.deg))
            logger.debug("OFFSETS: %f %f" % (offset_lon.deg, offset_lat.deg))
            _subscans.append(subscan.get_sid_tsys(_target, 
                                                      offset_lon,
                                                      offset_lat,
                                                      self.extremes,
                                                      self.duration,
                                                      self.beamsize))
        return _subscans

