#coding=utf-8

"""
Radiotelescopes definitions and constants.
These should match values you find in the CDB.
Each radiotelescope is represented a dictionary containing:
    - max_acc: maximum acceleration obtained as root square sum of max
      acceleration in both axis
    - acc_scale_factor: scale factor used to overstimate maximum acceleration
    - receivers: receivers as defined in L{receiver} module
"""
from __future__ import absolute_import

__all__ = ["MED", "SRT", "NOTO", "radiotelescopes"]

import math
from persistent import Persistent
from astropy import units as u

from .receiver import Receiver
from .valid_angles import VAngle

class Radiotelescope(Persistent):
    def __init__(self, name=""):
        self.receivers = {}
        self.name = name
        self.coord = None
        self.max_acc = 0.0
        self.acc_scale_factor = 15 #this value is highly abundant
        self.address = ""
        self.long_name = name

MED = Radiotelescope("MED")
MED.address = " Via Fiorentina 3513 I-40059 Medicina (BO) "
MED.max_acc = math.sqrt(0.4 ** 2 + 0.5 ** 2)
MED.long_name = "Medicina VLBI telescope"
MED.receivers = {
    'C' : Receiver('C', 4700.0, 5500.0, [[5000.0, 6000.0], [0.125, 0.1166667]], 1, 2),
    'CL': Receiver('CL', 4700.0, 5850.0, [[5000.0, 6000.0], [0.125, 0.1166667]], 1, 2),
    'X' : Receiver('X', 8180.0, 8980.0, [[8300.0], [0.08333333]], 1, 2),
    'K' : Receiver('K', 18000.0, 26000.0, [[22000.0], [0.03]], 1, 2),
    'KM' : Receiver('K', 18000.0, 26000.0, [[22000.0], [0.03]], 2, 2),
}
MED.receivers["KM"].has_derotator = False
MED.receivers["KM"].feed_extent = VAngle(0.037545204) #FIXME: wrong value


NOTO = Radiotelescope("NOTO")
NOTO.max_acc = math.sqrt(0.4 ** 2 + 0.5 ** 2)
NOTO.acc_scale_factor = 10
NOTO.receivers = {
    'C' : Receiver('C', 4620.0, 5020.0, [[4620.0], [0.133]], 1, 2),
    'M': Receiver('M', 4700.0, 5850.0, [[4700.0], [0.13]], 1, 2),
    'K' : Receiver('K', 21500.0, 23000.0, [[23000.0], [0.028]], 1, 2),
    'Q' : Receiver('Q', 38000.0, 43500.0, [[43500.0], [0.015]], 1, 2),
                 }


SRT = Radiotelescope("SRT")
SRT.long_name = "Sardinia radiotelescope"
SRT.max_acc = math.sqrt(0.4 ** 2 + 0.25 ** 2)
SRT.receivers = {
       'P' : Receiver('P', 305.0, 410.0, 
                      [[300.0, 350.0, 410.0],
                       [1.070, 0.937, 0.818]],
                      1, 2),
       'L' : Receiver('L', 1300.0, 1800.0, 
                      [[1300.0, 1550.0, 1800.0],
                       [0.252, 0.210, 0.187]],
                      1, 2),
       'C' : Receiver('C', 5700.0, 7700.0, 
                      [[5700.0, 6700.0, 7700.0],
                       [0.053, 0.047, 0.043]],
                      1, 2),
       'K' : Receiver('K', 18000.0, 26500.0, 
                      [[18000.0, 22000.0, 26000.0],
                       [0.016, 0.014, 0.012]],
                      1, 2),
       'KM' : Receiver('KM', 18000.0, 26500.0, 
                      [[18000.0, 22000.0, 26000.0],
                       [0.016, 0.014, 0.012]],
                      7, 2),
       #This is so ugly but it's resulting really useful
       'TEST': Receiver("TEST", 0, 100,
                     [[0.0, 100.0], [0.5, 0.5]],
                     nfeed = 7,
                     npols = 2,
                     has_derotator = True)
      }
SRT.receivers["TEST"].feed_extent = VAngle(3)
SRT.receivers["TEST"].interleave = VAngle(1)
SRT.receivers["KM"].has_derotator = True
SRT.receivers["KM"].feed_extent = VAngle(0.037545204)
"""
Feed extent represents the Y-distance between the central feed and the most
distant lateral feed in BSC configuration
"""
SRT.receivers["KM"].interleave = SRT.receivers["KM"].feed_extent / 3.0
"""
Receiver interleave represents the Y-spacing between each feed in the BSC
configuration
"""
SRT.receivers["KM"].set_feed_offsets(0, (VAngle(0, u.rad), 
                                         VAngle(0, u.rad)))
SRT.receivers["KM"].set_feed_offsets(1, (VAngle(0.00033355202, u.rad),
                                         VAngle(-0.00057772859, u.rad)))
SRT.receivers["KM"].set_feed_offsets(2, (VAngle(-0.00033355205, u.rad),
                                         VAngle(-0.00057772859, u.rad)))
SRT.receivers["KM"].set_feed_offsets(3, (VAngle(-0.00066710365, u.rad),
                                         VAngle(0, u.rad)))
SRT.receivers["KM"].set_feed_offsets(4, (VAngle(-0.00033355205, u.rad),
                                         VAngle(0.00057772859, u.rad)))
SRT.receivers["KM"].set_feed_offsets(5, (VAngle(0.00033355205, u.rad),
                                         VAngle(0.00057772859, u.rad)))
SRT.receivers["KM"].set_feed_offsets(6, (VAngle(0.00066710365, u.rad),
                                         VAngle(0.0, u.rad)))

"""
MLA: Adding data for supporting multi-feed nodding mode.
"""
print('Adding data to SRT KM feed')
SRT.receivers["KM"].set_valid_pairs(
    {
        '0': [(0,3),(0,6),(1,2),(3,6),(4,5)],
        '30':[(3,5), (2,6)],
        '60':[(0,2),(0,5),(1,6),(2,5),(3,4)],
        '90':[(1,5),(2,4)],
        '-30':[(1,3),(4,6)],
        '-60':[(0,1),(0,4),(1,4),(2,3),(5,6)]

    }
)

radiotelescopes = {
                   "SRT" : SRT,
                   "MED" : MED,
                   "NOTO" : NOTO,
                  }



