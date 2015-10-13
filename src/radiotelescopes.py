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

__all__ = ["MED", "SRT", "NOTO"]

import math
from persistent import Persistent

from receiver import Receiver
from valid_angles import VAngle

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
    'C' : Receiver('C', 4700.0, 5500.0, [[5000.0], [2.0]], 1, 2),
    'CL': Receiver('CL', 4700.0, 5850.0, [[5200.0], [1.8]], 1, 2),
    'X' : Receiver('X', 8180.0, 8980.0, [[8500.0], [0.8]], 1, 2),
    'K' : Receiver('K', 18000.0, 26000.0, [[23000.0], [0.2]], 2, 2),
}


NOTO = Radiotelescope("NOTO")
NOTO.max_acc = math.sqrt(0.4 ** 2 + 0.5 ** 2)
NOTO.acc_scale_factor = 10
NOTO.receivers = {
                  #TODO: fill this table with noto info
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
      }
SRT.receivers["KM"].has_derotator = True
SRT.receivers["KM"].feed_extent = VAngle(0.037545204)
SRT.receivers["KM"].interleave = SRT.receivers["KM"].feed_extent / 3.0

