#!/usr/bin/env python
#coding=utf-8
from distutils.core import setup

setup(
      name = "basie",
      version = "1.0dev",
      description = "schedule creator for italian radiotelescopes",
      author = "Marco Bartolini, Simona Righini",
      author_email = "bartolini@ira.inaf.it",
      maintainer = "Sergio Poppi",
      maintainer_email = "sergio.poppi@inaf.it",
      license = "License :: OSI Approved :: BSD License",
      url = "http://github.com/discos/basie/",
      packages = ["basie", "basie.scanmode", "basie.configobj"],
      package_dir = {"basie" : "src", "basie.scanmode" : "src/scanmode",
                     "basie.configobj": "src/configobj"},
      package_data = {"basie" : ["schemas/*.ini",
                                 "user_templates/*.txt"]},
      scripts = ["scripts/basie"],
     )
