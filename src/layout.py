#coding: utf-8

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

__all__ = ['COMMON_CONSTANTS', 'CROSS_CONSTANTS', 'get_wcs_params',
            'get_layout_params']

import frame
import scanmode

COMMON_CONSTANTS = dict(
                       WOBUSED = 0,
                       WOBTHROW = 0.0,
                       WOBDIR = '',
                       WOBCYCLE = 0.0,
                       WOBMODE = '',
                       WOBPATT = '',
                       PERIDATE = 0,
                       PERIDIST = 0,
                       LONGASC = 0,
                       OMEGA = 0,
                       INCLINAT = 0,
                       ECCENTR = 0,
                       ORBEPOCH = 0,
                       ORBEQNOX = 0,
                       DISTANCE = 0,
                       NPHASES = 1,
                       PHASEn = 'NONE',
                       FRTHRWLO = 0.0,
                       FRTHRWHI = 0.0,
                       TBLANK = 0.0,
                       TSYNC = 0.0,
#Maybe the following are not constants by definition
                       BASISPROJECTION = 'SFL/SFL',
                       NATIVEPROJECTION = 'SFL/SFL',
                       ZIGZAG = 1,
                       CRVAL1 = 0.0,
                       SCANROT = 0.0,
                      )
"""
Common parameters for every scan. Some of these in the future will be derived
from runtime informations.
"""

CROSS_CONSTANTS = dict(
                       SCANTYPE = 'POINT',
                       SCANMODE = 'OTF',
                       SCANGEOM = 'CROSS',
                       SCANDIR = '',
                       SCANLINE = 2,
                       SCANRPTS = 2,
                       SCANYSPC = 0.0,
                       SCANSKEW = 0.0,
                       CROCYCLE = 'O',
                      )
"""
Costants used for cross scans.
"""

def get_wcs_params(_scan):
    params = {}
    _target = _scan.target
    if _scan.scanmode.frame == frame.HOR and not _target.coord.frame == frame.HOR:
        native_system = "DESCRIP"
        params['MOVEFRAM'] = 1
    else:
        native_system = "ABSOLUT"
    if _target.coord.frame == frame.EQ:
        params['WCSNAME'] = "%s EQUATORIAL" % (native_system,)
        params['CTYPE'] = 'RA/DEC'
    elif _target.coord.frame == frame.GAL:
        params['WCSNAME'] = "%s GALACTIC" % (native_system,)
        params['CTYPE'] = 'GLON/GLAT'
    elif _target.coord.frame == frame.HOR:
        params['WCSNAME'] = "%s HORIZONTAL" % (native_system,)
        params['CTYPE'] = 'ALON/ALAT'
        params['BLONGOBJ'] = _target.coord.lon.deg
        params['BLATOBJ'] = _target.coord.lat.deg
    if _scan.scanmode.frame == frame.EQ:
        params['CTYPEN'] = 'RA/DEC'
        params['CTYPEOFF'] = 'RA/DEC'
    elif _scan.scanmode.frame == frame.GAL:
        params['CTYPEN'] = 'GLON/GLAT'
        params['CTYPEOFF'] = 'GLON/GLAT'
    elif _scan.scanmode.frame == frame.HOR:
        params['CTYPEN'] = 'ALON/ALAT'
        params['CTYPEOFF'] = 'ALON/ALAT'
    return params

def get_layout_params(_scan, _subscans):
    params = {}
    params.update(COMMON_CONSTANTS)
    params.update(get_wcs_params(_scan))
    if isinstance(_scan.scanmode, scanmode.CrossScan):
        params.update(CROSS_CONSTANTS)
    return params
