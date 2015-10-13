#!/usr/bin/env python
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
from distutils.core import setup

setup(
      name = "schedulecreator",
      version = "0.4.3",
      description = "schedule creator for italian radiotelescopes",
      author = "Marco Bartolini, Simona Righini",
      author_email = "bartolini@ira.inaf.it",
      maintainer = "Marco Bartolini",
      mainteiner_email =" bartolini@ira.inaf.it",
      license = "gpl-3.0",
      url = "http://www.ira.inaf.it/~bartolini/schedulecreator/",
      packages = ["schedulecreator", "schedulecreator.scanmode"],
      package_dir = {"schedulecreator" : "src"},
      package_data = {"schedulecreator" : ["schemas/*.ini",
                                          "user_templates/*.txt"]},
      scripts = ["scripts/schedulecreator", "scripts/sc-wiz"],
      requires = ["configobj", "validate", "astropy", "zodb"],
     )
