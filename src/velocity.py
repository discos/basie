#coding=utf-8

import string
import logging
logger = logging.getLogger(__name__)

from persistent import Persistent

VREFS = ["BARI", "LSRK", "LSRD", "GALCEN", "TOPCEN"]
VDEFS = ["OP", "RD", "Z"]

class Velocity(Persistent):
    def __init__(self, val=0.0, vdef=VDEFS[0], vref=VREFS[0]):
        self.vdef = vdef.upper()
        self.vref = vref.upper()
        self.val = val

    def __str__(self):
        return "-VRAD %f %s %s" % (self.val, 
                                   self.vref,
                                   self.vdef)

ZERO_VELOCITY = Velocity()
