#coding=utf-8

#
#
#    Copyright (C) 2013  INAF -IRA Italian institute of radioastronomy, bartolini@ira.inaf.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
logger = logging.getLogger(__name__)

from numpy import interp
from astropy import units as u 
from persistent import Persistent

from valid_angles import VAngle
from errors import *

from frame import Coord, HOR

class Receiver(Persistent):
    """
    represents a receiver and its characteristics
    """
    def __init__(self, name, fmin, fmax, 
                 beamsizetable=[[0.0],[0.0]], 
                 nfeed=1,
                 npols=2, #polarizations per feed
                 feed_offsets = [Coord(HOR, VAngle(0.0), VAngle(0.0))],
                 has_derotator = False):
        """
        Constructor
        @param name: the receiver name, used as an unique ID
        @type name: string
        @param fmin: receiver minimum usable sky frequency (MHz)
        @type fmin: float
        @param fmax: receiver maximum usable sky frequency (MHz)
        @type fmax: float
        @param beamsizetable: a table of (frequency, beamsize) couples
        @type beamsizetable: L{utils.KVTable}
        @param feed_offsets: a list of offsets [(olon, olat)] of each feed
        in relation to central feed. 0 place should always be [(0.0, 0.0)]
        @type feed_offsets: [(angles.Angle, angles.Angle) ... ] 
        @param has_derotator: True if the receiver can derotate
        """
        self.name = name
        self.fmin = fmin * u.MHz
        self.fmax = fmax * u.MHz
        self.nfeed = nfeed
        self.npols = npols
        self.feed_offsets = feed_offsets
        self.beamsize_table = beamsizetable
        self.has_derotator = has_derotator
        self.feed_extent = 0
        self.interleave = 0
        if len(self.feed_offsets) < self.nfeed:
            logger.warning("adding default offset (0.0, 0.0) to receiver %s" %
                           (self.name,))
            for i in range(self.nfeed - len(self.feed_offsets)):
                self.feed_offsets.append(Coord(HOR, VAngle(0.0), VAngle(0.0)))

    @property
    def nifs(self):
        """
        How many IFs out of this receiver (nfeed * npol)
        """
        return self.nfeed * self.npols

    def set_feed_offsets(self, feed_number, offsets, frame=HOR):
        """
        Set the feed offset for one feed
        @param offsets: (offset_lon, offset_lat)
        @raise ReceiverError: if feed_number is too high
        """
        if feed_number > self.nfeed:
            raise ReceiverError("Receiver %s has no feed %d" % (self.name,
                feed_number))
        self.feed_offsets[feed_number] = Coord(frame,
                                               VAngle(offsets[0]),
                                               VAngle(offsets[1]))

    @property
    def beamsize(self):
        """
        Get receiver default beamsize (calculated at self.fmin)
        """
        return self.get_beamsize()

    def get_beamsize(self, freq=None):
        """
        Get the beamsize for this receiver at a given frequency. 
        Read from beamsize_table the nearest frequency value.
        If freq is None defauls to self.fmin
        @param freq: frequency (MHz)
        @type freq: float
        @return: beamsize at given frequency
        """
        if not freq:
            logger.warning("RECEIVER %s using default beamsize at min frequency" %
                           (self.name,))
            freq = self.fmin.value
        if not self.fmin.value <= freq <= self.fmax.value:
            logger.warning("RECEIVER %s beamsize at frequency %f out of range" %
                           (self.name, freq,))
        logger.debug("Getting beamsize\nfreq: %s\nt0: %s\nt1: %s" % \
                     (freq, self.beamsize_table[0], self.beamsize_table[1]))
        return interp(freq,
                      self.beamsize_table[0],
                      self.beamsize_table[1])

    def is_multifeed(self):
        """
        True if the receiver has multiple feeds, False otherwise.
        """
        return self.nfeed > 1

