#coding utf-8

import logging
logger = logging.getLogger(__name__)

from persistent import Persistent
from astropy import units as u

import frame
import copy

class Scan(Persistent):
    """
    Unites a scanmode with a target and produces subscans
    """
    def __init__(self, 
                 target, 
                 scanmode, 
                 receiver, 
                 frequency,
                 backend,
                 schedule_repetitions = 1,
                 schedule_tsys = 0,
                ):
        self.target = target
        self.scanmode = scanmode
        self.receiver = receiver
        self.backend = backend
        self.frequency = frequency
        self.repetitions = target.repetitions or schedule_repetitions
        self.tsys = target.tsys or schedule_tsys
        if self.target.offset_coord.is_null():
            try:
                self.target.offset_coord.frame = scanmode.frame
            except: #scanmode does not define a frame
                self.target.offset_coord.frame = self.target.coord.frame
        if self.tsys >= 0 and not self.backend.can_tsys:
            logger.warning("Tsys measurement is disabled for target %s because\n\tbackend %s cannot perform Tsys measurements" %
                            (self.target.label, self.backend.backend_type))
            self.tsys = -1

    @property
    def subscans(self):
        """
        return the correct subscans sequence for this scan based on tsys and
        repetitions parameters
        @param receiver: the receiver used in the observation
        @type receiver: receiver.Receiver
        """
        subscans = []
        base_subscans = self.scanmode.do_scan(self.target, 
                                              self.receiver, 
                                              self.frequency)
        counter = 0
        for rep in xrange(self.repetitions):
            for sn, ss in enumerate(base_subscans):
                #logger.debug("REP: %d SUBSCAN: %d" % (rep, sn))
                #subscan_number = rep * self.scanmode.unit_subscans + sn
                yield_tsys = False
                #should we add a TSYS subscan?
                if rep == 0 and sn == 0 and self.tsys >= 0:
                    yield_tsys = True
                elif self.tsys > 0 and not(counter % self.tsys):
                    yield_tsys = True
                if yield_tsys:
                    subscans.append(copy.deepcopy(ss[1]))
                subscans.append(copy.deepcopy(ss[0]))
                counter += 1
        return subscans

