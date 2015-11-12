#coding utf-8

import logging
logger = logging.getLogger(__name__)

from persistent import Persistent
from astropy import units as u

import frame
import copy

"""
Unites a scanmode with a target and produces subscans
"""
class Scan(Persistent):
    def __init__(self, 
                 _target, 
                 _scanmode, 
                 _receiver, 
                 _frequency,
                 _backend,
                 _repetitions,
                 _tsys,
                ):
        self.target = _target
        self.scanmode = _scanmode
        self.receiver = _receiver
        self.backend = _backend
        self.frequency = _frequency
        self.repetitions = _repetitions
        self.tsys = _tsys
        if self.target.offset_coord.frame == frame.NULL:
            try:
                self.target.offset_coord.frame = _scanmode.frame
            except: #scanmode does not define a frame
                self.target.offset_coord.frame = self.target.coord.frame

    @property
    def subscans(self):
        """
        return the correct subscans sequence for this scan based on tsys and
        repetitions parameters
        @param receiver: the receiver used in the observation
        @type receiver: receiver.Receiver
        """
        subscans = []
        base_subscans = self.scanmode._do_scan(self.target, 
                                                self.receiver, 
                                                self.frequency)
        for rep in xrange(self.repetitions):
            for sn, ss in enumerate(base_subscans):
                logger.debug("REP: %d SUBSCAN: %d" % (rep, sn))
                subscan_number = rep * self.scanmode.unit_subscans + sn
                logger.debug("subscan_number %d" % (subscan_number,))
                yield_tsys = False
                if subscan_number == 0 and self.tsys >= 0:
                    yield_tsys = True
                elif self.tsys > 0 and not(subscan_number % self.tsys):
                    yield_tsys = True
                if yield_tsys:
                    subscans.append(copy.deepcopy(ss[1]))
                subscans.append(copy.deepcopy(ss[0]))
        return subscans

