
from scanmode import ScanMode
import subscan

class NoddingScan(ScanMode):
    def __init__(self, feeds, duration, sequence):
        ScanMode.__init__(self)
        self.feed_a = feeds[0]
        self.feed_b = feeds[1]
        self.duration = duration
        self.sequence = sequence
        self.unit_subscans = sum(el[0] for el in self.sequence)

    def _do_scan(self, _target, _receiver, _frequency):
        offset_a = _receiver.get_offset_for_feed(self.feed_a)
        offset_b = _receiver.get_offset_for_feed(self.feed_b)
        _subscans = []
        for element in self.sequence:
            for repetitions in range(element[0]):
                if element[1] == "a":
                    offset = offset_a
                else:
                    offset = offset_b
                ss = subscan.get_sidereal_subscan(_target,
                                                  offset.lon,
                                                  offset.lat,
                                                  self.duration,
                                                  element[2])
                st = subscan.get_tsys_subscan(_target,
                                                  offset.lon,
                                                  offset.lat)
                _subscans.append((ss, st))
        return _subscans
