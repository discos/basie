##coding=utf-8

"""
# Basie

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

Basie is a software package conceived to implement scheduling of
italian radiotelescopes via the creation of schedule files.

## INSTALLATION INSTRUCTIONS

Basie (previously called ScheduleCreator) depends on Astropy and can thus run on
python >= 2.6.5
The package is not tested on any python 3.x version.
Before installing the package make sure you download and extract the package
archive at
http://github.com/discos/basie/

Installation instructions can be reduced to:

```
$ make dep
$ make install
```

Note that you may need to have root privileges for installing python packages.
If you wanna know more or you experience some issue, please go on reading.

### EASY_INSTALL AND PIP

We suggest to install dependencies via distutils.

#### DISTUTILS ON WINDOWS

From a command prompt try to execute the command

```
C:\your path\> easy_install
```

This will tell you if easy_install is installed on your Windows PC
If not just donwload and install python-setuptools package from
https://pypi.python.org/pypi/setuptools , go to the bottom of the page
and grab the .exe related to your python version.
If you're unsure which python version you are running from a command
prompt execute

```
C:\your path\> python --version
```

#### DISTUTILS ON LINUX

On linux you should find setuptools prepackaged on most modern distros.

On debian-based distros:

```bash
you@yourpc$ sudo apt-get install python-setuptools
```

On RH based distros:

```
root@yourpc$ yum install python-setuptools
```

Once easy_install is installed, instructions are the same for every
OS, so just follow the steps from command prompt or user shell.

If possible we will use 'pip', a more friendly python package manager.
Install it with:

```
$ easy_install pip
```

### INSTALL PACKAGE DEPENDENCIES

The package depends on other python packages which can be installed manually
or via distutils.

Required packages are listed in "requirements.txt" file fourinished along with
these sources
You can install every dependecy via (note that you may need to be root):

```
$ make dep
```
Or simply:

```
$ pip install -r requirements.txt
```

Or you can download and install individual packages from
pypi at https://pypi.python.org/pypi or using the package manager of your OS.

If you don't have access to make command (i.e. on Windows) you can also install
dependencies using pip from the command line for each individual package:

```
$ pip install configobj
$ pip install validate
$ pip install astropy
$ pip install zodbpickle
$ pip install ZODB
...
```

or every package at once:

```
$ pip install configobj validate astropy ZODB ...
```

### INSTALL

From the package directory just run

```
$ python setup.py install
```

or

```
$ make install
```

to install the package in the current python environment.
Now you can remove the downloaded package or clean build products via:

```
$ make clean
```

## USAGE

Once installed, the package comes with an executable called 'basie'

```
$ basie --help
```

The schedulecreator takes in input a configuration file formatted according to a
specific syntax and generates 4 files used by antenna control system as the
schedule.

1. Fetch a precompiled configuration template
    ```
    $ basie [-f] -t <destination_directory>
    ```
    Creates <destination_directory> and copy configuration.txt and targets.txt user
    templates into the folder. If run with -f it will override eventual existing
    files.
    Modify these files according to the comments you will find to generate a new schedule.

2. Generate a new schedule
    ```
    $ basie [-f] -s <input_configuration_file_path> <destination_directory>
    ```
    Generates the schedule files into the destination directory, creating the
    folder if necessary.
    <input_configuration_file_path> is the path to a valid configuration file as copied
    and modified from user template in step 1.
    if run with -f overrides eventual existing files.


## BUILD DOCUMENTATION

You can generate a local copy of the developer documentation using epydoc via

```
$make doc
```

You will find the doc under doc/html/

@version: 0.6.5
@status: stable
@authors: Marco Bartolini, Simona Righini
@organization: INAF -IRA
@copyright: INAF - IRA (c) 2016
@license: gpl v3.0
@contact: bartolini@ira.inaf.it
"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
VERSION = "0.7b1"
NURAGHE_TAG = "nuraghe-0.6"
ESCS_TAG = "escs-0.6"
ESCS_NOTO_TAG = "escs-noto-0.2"

import logging

def cmd_line():
    import argparse
    import os
    import sys

    #Adding command line options
    parser = argparse.ArgumentParser(description="Create schedule files for italian radiotelescopes")
    parser.add_argument('-d', action='store_true', help="enable debug messages",
                        dest='debug')
    parser.add_argument('-t', '--get_templates', action='store_true',
                        dest="get_templates",
                        help="copy user templates into supplied directory, does not generate any schedule. Creates directory if it does not exist.")
    parser.add_argument('-c', '--configuration_file', dest='configuration_file',
                        default='configuration.txt',
                        help='user schedule configuration input file.')
    parser.add_argument('-f', action='store_true', dest='force',
                        help='force override of existing files')
    parser.add_argument('--version', action='store_true', dest='show_version',
                        help='print version information and exit')
    parser.add_argument('directory', default=".", nargs='?',
                        help="directory for schedule files or user templates")


    #parsing command line arguments
    ns = parser.parse_args()
    if ns.show_version:
        print("basie version: %s" % (VERSION,))
        sys.exit()
    #setting logger level and format
    if ns.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
    logger = logging.getLogger("basie")
    #if debugging show command line parameters
    logger.debug("Running with options:")
    for k,v in vars(ns).items():
        logger.debug("\t%s:\t%s" % (k, str(v),))

    #imports are here as logging has already been configured
    from . import schedule, rich_validator, utils, target_parser, receiver
    from .radiotelescopes import radiotelescopes

    try:
        if ns.get_templates:
            #Copy user template files into directory
            logger.info("copying package user templates")
            if ns.directory == os.curdir:
                dst_directory = os.path.join(os.curdir)
                dst_directory = os.path.abspath(dst_directory)
            else:
                dst_directory = os.path.abspath(ns.directory)
            utils.get_user_templates(dst_directory, ns.force)
        else:
            #generating schedule from user file
            configuration_file = os.path.abspath(ns.configuration_file)
            if not os.path.exists(configuration_file):
                raise IOError("cannot find file %s" % configuration_file)
            logger.info("generating schedule from user input file: {0}".format(ns.configuration_file))
            src_directory = os.path.dirname(configuration_file)
            dst_directory = os.path.abspath(ns.directory)
            conf = rich_validator.validate_configuration(configuration_file)
            #setting target file in the same directory as schedule file
            targetsFile = os.path.join(src_directory, conf.pop('targetsFile'))
            parsed_targets = target_parser.parse_file(targetsFile)
            logger.debug("parsed targets: %s" % (parsed_targets,))
            #prepare Schedule contructor arguments
            schedule_params = conf
            radiotelescope_name = conf.pop("radiotelescope").upper()
            radiotelescope = radiotelescopes[radiotelescope_name]
            try:
                receiver = radiotelescope.receivers[conf["receiver"]]
            except:
                raise ScheduleError("radiotelescope does not have specified receiver")
            schedule_params["radiotelescope"] = radiotelescope_name
            schedule_params.receiver = receiver
            backends = schedule_params.pop("backends")
            scantypes = schedule_params.pop("scantypes")
            logger.debug(schedule_params)
            _schedule = schedule.Schedule(**schedule_params)
            _schedule.backends = backends
            _schedule.scantypes = scantypes
            for _target, _scanmode, _backend, _  in parsed_targets:
                _schedule.add_scan(_target, _scanmode, _backend)
            _schedule.set_base_dir(dst_directory)
            _schedule._write_schedule_files()
        logger.info('closing gently')
    except Exception as e:
        logger.info("exiting with error")
        logger.error(str(e))
        if ns.debug:
            raise
