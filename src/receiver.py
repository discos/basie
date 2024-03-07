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

#   Starting editing from MLA

from __future__ import absolute_import
from builtins import range
import logging
logger = logging.getLogger(__name__)
import math
from numpy import interp
from astropy import units as u 
from persistent import Persistent

from .valid_angles import VAngle
from .errors import *

from .frame import Coord, HOR
from .procedures import *

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
        self.feeds_valid_pairs = None
        if len(self.feed_offsets) < self.nfeed:
            logger.debug("adding default offset (0.0, 0.0) to receiver %s" %
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
    #   Methods for Nodding mode 
    def set_valid_pairs(self, pairs_table):
        """
        Set the valid pairs for each derotator position.
        The valid data structure is:
        {
            '0':[(0,3), (0,6),(1,2)...]
        }
        @param pair_tables: Data structure containing the valid pairs for each derotator angle {
            '0':[(0,3), (0,6),(1,2)...]
        }
        """
        if self.nfeed < 2:
            raise ReceiverError("Cannot define valid pairs for nodding with single feed.")
        
        self.feeds_valid_pairs = pairs_table

    def get_valid_pairs(self):
        return self.feeds_valid_pairs


    def is_valid_pair(self, pair):
        """
        This function checks if a pair is valid w.r.t derotator angle.
        @param pair. A tuple containing a feed pair (3,2)
        @param derotator. A String containing the derotator angle
        """
        try:
           # p = self.feeds_valid_pairs[derotator.strip()]
            for p in self.feeds_valid_pairs:
                #print(p)
                for vp in self.feeds_valid_pairs[p]:
                    if sorted(list(vp)) == (list(pair)):
                        return True

            #Exiting for means no equal pairs found

            return False

        except Exception as e:
            print('Error :' + str(e))
            return False


    def get_feed_offset(self, feed_number, feed_pair, frame=HOR):
        derotator_angle = 0.0
        valid_pair = False
        if self.nfeed < 2:
            raise ReceiverError("Cannot get offset for single feed recevier.")

        if self.feeds_valid_pairs is None:
            raise ReceiverError("Feed table not properly setted. None is found.")

        if feed_number not in feed_pair:
            raise ReceiverError("Data mismatch between pair and feed")
        #Getting the feed and the derotator angle


        try:
           # p = self.feeds_valid_pairs[derotator.strip()]
            for p in self.feeds_valid_pairs:
                #print(p)
                for vp in self.feeds_valid_pairs[p]:
                    if sorted(list(vp)) == (list(feed_pair)):
                        derotator_angle = p
                        valid_pair = True

        except Exception as e:
            print('Error :' + str(e))
            return False

        if valid_pair == False:
            raise ReceiverError('Invalid configuration of the feeds pair')
        print('Derotator: ' + str(derotator_angle))
        try:
            derotator_angle = float(derotator_angle)
            coord = self.feed_offsets[feed_number]
            return Coord(frame, 
            coord.lon*math.cos(-derotator_angle*math.pi/180) - coord.lat*math.sin(-derotator_angle*math.pi/180), 
            coord.lon*math.sin(-derotator_angle*math.pi/180) + coord.lat*math.cos(-derotator_angle*math.pi/180))

        except:
            raise ReceiverError("Invalid configuration or invalid derotator angle provided.")
        pass    

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
        @type freq: Quantity
        @return: beamsize at given frequency
        """
        if not freq:
            logger.warning("RECEIVER %s using default beamsize at min frequency" %
                           (self.name,))
            freq = self.fmin
        if((not self.fmin <= freq <= self.fmax) and (freq > 0 * u.MHz)):
            logger.warning("RECEIVER %s beamsize at frequency %f out of range" %
                           (self.name, freq.value,))
        logger.debug("Getting beamsize\nfreq: %s\nt0: %s\nt1: %s" % \
                     (freq.value, self.beamsize_table[0], self.beamsize_table[1]))
        return interp(freq.value,
                      self.beamsize_table[0],
                      self.beamsize_table[1])

    def is_multifeed(self):
        """
        True if the receiver has multiple feeds, False otherwise.
        """
        return self.nfeed > 1

    def getDerotatorProcedure(self,feed_pair):

        #Getting the derotator angle and put it in the procedure
        valid_pair = False
        try:
           # p = self.feeds_valid_pairs[derotator.strip()]
            for p in self.feeds_valid_pairs:
                #print(p)
                for vp in self.feeds_valid_pairs[p]:
                    if sorted(list(vp)) == (list(feed_pair)):
                        derotator_angle = p
                        valid_pair = True

        except Exception as e:
            raise ReceiverError('Error while getting derotator angle')

        if valid_pair == False:
            raise ReceiverError('Error while getting derotator angle')
        #cambia il nome!!! Perchè potrebbe aver bisogno di avere la stessa proc con stesso nome
        return Procedure("DEROTATORFIXED_%s"%str(float(derotator_angle)).replace('.',''), 0, "\tderotatorSetConfiguration=FIXED\n\tderotatorSetPosition=%sd\n"%str(float(derotator_angle)), True)
        