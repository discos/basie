from basie.valid_angles import VAngle
from basie.errors import ScheduleError

from scanmode import ScanMode
from ..frame import NULL, Coord
import subscan

class OnOffScan(ScanMode):
    def __init__(self, duration, offset_lon, offset_lat, offset_frame, sequence):
        ScanMode.__init__(self)
        self.offset_lon = offset_lon
        self.offset_lat = offset_lat
        if (not offset_frame) or offset_frame == NULL:
            self.offset_frame = self.frame
        else:
            self.offset_frame = offset_frame
        self.unit_subscans = sum(el[0] for el in sequence) 
        self.sequence = sequence
        self.duration = duration
        self.frame = NULL

    def _do_scan(self, _target, _receiver, _frequency):
        _subscans = []
        for element in self.sequence:
            if element[1] == "on": #ON SOURCE
                ss = subscan.get_sidereal(
                        _target, 
                        Coord(self.offset_frame,
                              VAngle(0.0),
                              VAngle(0.0)),
                        self.duration,
                        is_cal = element[2])
            elif element[1] == "off": #OFF SOURCE
                ss = subscan.get_sidereal(
                        _target, 
                        Coord(self.offset_frame,
                              self.offset_lon,
                              self.offset_lat),
                        self.duration,
                        is_cal=element[2])
            else:
                raise ScheduleError("unknown onoff position: %s" % (element[1],))
            #TSYS is calculated at off position
            st = subscan.get_tsys(_target,
                    Coord(self.offset_frame,
                          self.offset_lon,
                          self.offset_lat))
            for repetitions in range(element[0]):
                _subscans.append((ss, st))
        return _subscans

