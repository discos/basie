
from scanmode import ScanMode
from . import subscan
from .. import frame
from ..errors import ScanError

class NoddingScan(ScanMode):
    def __init__(self, feeds, duration, sequence):
        ScanMode.__init__(self)
        self.feed_a = feeds[0]
        self.feed_b = feeds[1]
        self.duration = duration
        self.sequence = sequence
        self.unit_subscans = sum(el[0] for el in self.sequence)
        self.frame = frame.NULL

    def _do_scan(self, _target, _receiver, _frequency):
        #import ipdb;ipdb.set_trace()
        if not _target.offset.is_null():
            if not _target.offset.frame == frame.HOR:
                raise ScanError("cannot perform nodding on target with offsets")
        offset_a = _receiver.feed_offsets[self.feed_a]
        offset_b = _receiver.feed_offsets[self.feed_b]
        _subscans = []
        for element in self.sequence:
            for repetitions in range(element[0]):
                if element[1] == "a":
                    offset = offset_a
                else:
                    offset = offset_b
                ss = subscan.get_sidereal(_target,
                                          offset,
                                          self.duration,
                                          element[2])
                st = subscan.get_tsys(_target,
                                      offset)
                _subscans.append((ss, st))
        return _subscans
