import logging
logger = logging.getLogger(__name__)

from scanmode import ScanMode
import subscan
from .. import procedures
from basie.valid_angles import VAngle

class CrossScan(ScanMode):
    def __init__(self, 
                 frame, 
                 length, 
                 speed):
        """
        @param frame: The scan L{frame}
        @type frame: L{frame.Frame}
        @param length: length of each otf subscan in decimal degrees
        @type length: angles.Angle
        @param speed: speed of each otf subscan in degrees per minute
        """
        ScanMode.__init__(self)
        self.length = length
        self.frame = frame
        self.speed = speed
        #duration is expressed in seconds
        self.duration = self.length.deg / self.speed * 60
        logger.debug("scan %d duration: %f" % (self.ID, self.duration))
        #The minimum observation is composed of 4 subscans
        # to form a cross over the source in both directions
        self.unit_subscans = 4

    def _do_scan(self, _target, _receiver, _frequency):
        beamsize = VAngle(_receiver.get_beamsize(max(_frequency)))
        _subscans = []
        #Fill informations for each OTF subscan in the 4 directions
        #This is a default implementation, maybe one day we could parametrize
        #this if needed
        for _const_axis, _direction in [('LON', 'INC'), 
                                        ('LON', 'DEC'), 
                                        ('LAT', 'INC'), 
                                        ('LAT', 'DEC')]:
            _subscans.append(subscan.get_cen_otf_tsys(_target,
                                                      self.duration,
                                                      self.length,
                                                      VAngle(0.0),
                                                      _const_axis,
                                                      _direction,
                                                      self.frame,
                                                      beamsize))
        return _subscans

class PointScan(CrossScan):
    def __init__(self, 
                 frame, 
                 length, 
                 speed):
        super(PointScan, self).__init__(frame, length, speed)
        
    def _do_scan(self, _target, _receiver, _frequency):
        beamsize = VAngle(_receiver.get_beamsize(max(_frequency)))
        _subscans = []
        #Fill informations for each OTF subscan in the 4 directions
        #This is a default implementation, maybe one day we could parametrize
        #this if needed
        for _const_axis, _direction in [('LON', 'INC'), 
                                        ('LAT', 'INC')]:
            _subscans.append(subscan.get_cen_otf_tsys(_target,
                                                      self.duration,
                                                      self.length,
                                                      VAngle(0.0),
                                                      _const_axis,
                                                      _direction,
                                                      self.frame,
                                                      beamsize))
        return _subscans
