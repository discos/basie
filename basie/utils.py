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

"""
Utitlity functions. (This is the classical module where you put random things
that do not fit anywhere else)

functions:
    - get_user_templates: copy user template files
    - ceil_to_odd(dec): returns the nearest bigger odd int
    - ceil_to_half(dec): nearest bigger half unit
    - extrude_from_rectange: get a point outside of a rectangle, used for tsys 
"""

import logging
import os
import shutil
logger = logging.getLogger(__name__)

import numpy as np
from basie.valid_angles import VAngle

PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))
USER_TEMPLATES_DIR = os.path.join(PACKAGE_DIR, "user_templates/")
SCHEMA_DIR = os.path.join(PACKAGE_DIR, "schemas/")

def get_user_templates(dst, force=False):
    """
    copy user template files into destination directory.
    If destination directory does not exists tries to create it.
    @param dst: the destination directory
    @param force: if True override present files
    """
    filenames = ("configuration.txt",
                 "targets.txt",)
    dst = os.path.abspath(dst)
    if not os.path.isdir(dst):
        logger.info("creating destination directory for templates: %s" % (dst,))
        os.makedirs(dst)
    for filename in filenames:
        write = True
        dstfile = os.path.join(dst, filename)
        srcfile = os.path.abspath(os.path.join(USER_TEMPLATES_DIR, filename))
        if os.path.isfile(dstfile):
            if not force:
                logger.warning("File exists %s" % (dstfile,))
                write = False
            else:
                logger.warning("Overriding file %s" % (dstfile,))
        if write:
            logger.info("write file: %s" % (dstfile,))
            logger.debug("copying %s to %s" % (srcfile, dstfile))
            shutil.copyfile(srcfile, dstfile)

def ceil_to_odd(dec):
    """
    @param dec: a floating point number or angle
    @type dec: VAngle or float
    @return: the minor integer odd number greater then dec.
    """
    _ceil = np.ceil(dec)
    #TODO: there must be a better way for broadcasting divmod operations to all
    #types 
    if isinstance(dec, VAngle):
        _is_angle = True
        _is_even = (_ceil.value % 2 == 0)
    else:
        _is_angle = False
        _is_even = (_ceil % 2 == 0)
    if _is_even:
        if _is_angle:
            return _ceil + VAngle(1)
        else:
            return _ceil + 1
    else:
        return _ceil

def ceil_to_half(dec):
    """
    @param dec: a floating point number
    @type dec: float
    @return: the minor half unit bigger then dec
    """
    _ceil = np.ceil(dec)
    if (_ceil - 0.5) >= dec:
        return _ceil - 0.5
    else:
        return _ceil

def extrude_from_rectangle(x, y, extremes, delta):
    """
    project a point to the nearest side of a containing rectangle defined by the
    point in extremes
    @param x: x coordinate of the inner point
    @param y: y coordinate of the inner point
    @param extremes: [[x0, y0], ... [x3,y3]] coordinates of the extremes of a
    rectangle containing the point
    @param delta: how much to extrude the point from the polygon
    """
    #get distances from rectangle sides
    delta_x = [abs(x - e[0]) for e in extremes]
    delta_y = [abs(y - e[1]) for e in extremes]
    minx = min(delta_x)
    miny = min(delta_y)
    if minx <= miny: #we extrude moving on longitude axis
        _x = extremes[delta_x.index(minx)][0]
        if _x < x:
            _x -= delta
        elif _x > x:
            _x += delta
        else:#we are on right of left side of the rectangle
            left = True #suppose we are on the left side
            for _e in extremes:
                if _e[0] < _x:
                    left = False #we are on the right side
            if left:
                _x -= delta
            else:
                _x += delta
        ext = [_x, y]
    else: #we extrude moving on latitude axis
        _y_index = delta_y.index(miny)
        _y = extremes[_y_index][1]
        if _y < y:
            _y -= delta
        elif _y > y:
            _y += delta
        else:# We are on top of bottom side of the rectangle
            bottom = True #suppose we are on bottom side
            for _e in extremes:
                if _e[1] < _y:
                    bottom = False#we are on top side
            if bottom:
                _y -= delta
            else:
                _y += delta
        ext = [x, _y]
    return ext

