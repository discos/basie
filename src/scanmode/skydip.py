import logging
logger = logging.getLogger(__name__)

from scanmode import ScanMode
import subscan
from .. import procedures
from basie.valid_angles import VAngle
from basie.frame import NULL_COORD, Coord, HOR


class SkydipScan(ScanMode):
    def __init__(self, 
                 start, 
                 stop, 
                 duration,
                 offset = Coord(HOR, 
                                VAngle(1),
                                VAngle(0))):
        """
        @param start: elevation start 
        @type start: VAngle
        @param stop: elevation stop
        @type stop: stop
        @param duration: skydip duration
        @type duration: seconds
        @param offset: skydip offset from specified target
        @type offset: frame.Coord
        """
        ScanMode.__init__(self)
        self.start = start
        self.stop = stop
        self.duration = duration
        self.offset = offset
        # The minimum observation is composed of 2 subscans
        # one sidereal subscan to position the antenna in 
        # proximity of the source, and one OTF subscan to perform
        # the skydip acquisition
        self.unit_subscans = 2

    def _do_scan(self, _target, _receiver, _frequency):
        beamsize = VAngle(_receiver.get_beamsize(max(_frequency)))
        _subscans = []
        null_offset = Coord(_target.coord.frame,
                            VAngle(0),
                            VAngle(0))
        _subscans.append((subscan.get_sidereal(_target, 
                                              null_offset,
                                              0,
                                              is_cal = False),
                          subscan.get_tsys(_target,
                                           null_offset)))
        _subscans.append(subscan.get_skydip_tsys(_subscans[0][0].ID,
                                                 _target,
                                                 self.duration,
                                                 self.start,
                                                 self.stop,
                                                 self.offset))
        return _subscans

