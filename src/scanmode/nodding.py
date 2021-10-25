from __future__ import absolute_import

from builtins import range
from .scanmode import ScanMode
from . import subscan
from .. import frame
from ..errors import ScanError

class NoddingScan(ScanMode):
    def __init__(self, feeds, duration, sequence, derotator_angle = None):
        ScanMode.__init__(self)
        self.feed_a = feeds[0]
        self.feed_b = feeds[1]
        self.duration = duration
        self.sequence = sequence
        self.unit_subscans = sum(el[0] for el in self.sequence)
        self.frame = frame.NULL
        self.derotator_angle = derotator_angle
    def _do_scan(self, _target, _receiver, _frequency):
        if not _target.offset_coord.is_null():
            if not _target.offset_coord.frame == frame.HOR:
                raise ScanError("cannot perform nodding on target with offsets")
        if not _receiver.is_multifeed():
            raise ScanError("cannot execute nodding scan with single feed receiver")

        #MLA: Here you should get the derotator angle and check that the pair is valid!!!!!
        print('Feed_a ' + str(self.feed_a) + ' Feed_b' + str(self.feed_b))
        offset_a = _receiver.feed_offsets[self.feed_a]
        offset_b = _receiver.feed_offsets[self.feed_b]
        #MLA: Here you should get the derotator angle and check that the pair is valid!!!!!
        _subscans = []
        for element in self.sequence:
            if element[1] == "a":
                offset = -offset_a #the sign must be opposite to the feed displacement  
            else:
                offset = -offset_b #the sign must be opposite to the feed displacement
            self.offset=offset
            ss = subscan.get_sidereal(_target,
                                      offset,
                                      self.duration,
                                      is_cal=element[2])
            st = subscan.get_tsys(_target,
                                  offset)
            for repetitions in range(element[0]):
                _subscans.append((ss, st))
        return _subscans
