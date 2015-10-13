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
Schedulecreator is a software package conceived to implement scheduling of
italian radiotelescopes via the creation of schedule files.

INDEX
=====

    - installation instructions
        - easy_install and pip 
            - distutils on windows
            - distutils on linux
        - install package dependencies
        - install
    - usage
    - sc-wiz
    - build documentation


INSTALLATION INSTRUCTIONS
=========================

Schedule creator can run on python  versions >= 2.4 but it has some dependencies on
external modules, and some modules which got into standard python in later
releases but provide backports for 2.4. 
The package is not tested on any python 3.x version.
Before installing the package make sure you download and extract the package
archive at
U{http://www.ira.inaf.it/~bartolini/schedulecreator/schedulecreator-0.3.tar.gz}

Installation instructions can be reduced to:

    >>> make dep
    >>> make install

Note that you may need to have root privileges for installing python packages.
If you wanna know more or you experience some issue, please go on reading.

EASY_INSTALL AND PIP
--------------------

We suggest to install dependencies via distutils.

DISTUTILS ON WINDOWS
~~~~~~~~~~~~~~~~~~~~

From a command prompt try to execute the command

>>> C:\your path\> easy_install

This will tell you if easy_install is installed on your Windows PC
If not just donwload and install python-setuptools package from
https://pypi.python.org/pypi/setuptools , go to the bottom of the page
and grab the .exe related to your python version. 
If you're unsure which python version you are running from a command
prompt execute 

>>> C:\your path\> python --version

DISTUTILS ON LINUX
~~~~~~~~~~~~~~~~~~

On linux you should find setuptools prepackaged on most modern distros. 

On debian-based distros:

>>> you@yourpc# sudo apt-get install python-setuptools

On RH based distros:

>>> root@yourpc# yum install python-setuptools

Once easy_install is installed, instructions are the same for every
OS, so just follow the steps from command prompt or user shell. 

If possible we will use 'pip', a more friendly python package manager. 
Install it with:

>>> easy_install pip

NOTE FOR PYTHON 2.4
~~~~~~~~~~~~~~~~~~~

For B{Python2.4} users, use  pip version 1.1 which can be downloaded from
U{https://pypi.python.org/packages/source/p/pip/pip-1.1.tar.gz} and install
manually via 

>>> python setup.py install


INSTALL PACKAGE DEPENDENCIES
----------------------------

The package depends on other python packages which can be installed manually
or via distutils.

Required packages are:
    - U{argparse<https://pypi.python.org/pypi/argparse/>}
    - U{configobj<https://pypi.python.org/pypi/configobj/>}
    - U{validate<https://pypi.python.org/pypi/validate/>}
    - U{pyephem<https://pypi.python.org/pypi/pyephem/>}
    - U{angles<https://pypi.python.org/pypi/angles/>}

You can install every dependecy via (note that you may need to be root): 

>>> make dep

Or you can download and install individual packages from
U{B{pypi}<https://pypi.python.org/pypi>}
or using the package manager of your OS.

If you don't have access to make command (i.e. on Windows) you can also install
dependencies using pip from the command line for each individual package

>>> pip install argparse
>>> pip install configobj
>>> pip install validate
>>> pip install angles
>>> pip install pyephem

or every package at once:

>>> pip install argparse configobj validate angles pyephem

INSTALL
-------

From the package directory just run

>>> python setup.py install 

or

>>> make install

to install the package in the current python environment.
Now you can remove the downloaded package or clean build products via:

>>> make clean

USAGE
=====

Once installed, the package comes with an executable 'schedulecreator'

>>> schedulecreator --help 

The schedulecreator takes in input a configuration file formatted according to a
specific syntax and generates 4 files used by antenna control system as the
schedule.

    1. Fetch a precompiled configuration template 
        
        >>> schedulecreator [-f] -t <destination_directory>
        
        Creates <destination_directory> and copy configuration.txt and targets.txt user
        templates into the folder. If run with -f it will override eventual existing
        files.
        Modify these files according to the comments you will find to generate a new schedule.

    2. Generate a new schedule

        >>> schedulecreator [-f] -s <input_configuration_file_path> <destination_directory>

        Generates the schedule files into the destination directory, creating the
        folder if necessary. 
        <input_configuration_file_path> is the path to a valid configuration file as copied
        and modified from user template in step 1.
        if run with -f overrides eventual existing files.

SC-WIZ
======

On linux you get accesso to a I{B{sc-wiz}} (Schedule Creator Wizard) command which will guide you through
a serie of graphical dialogs to the creation of a schedule.
sc-wiz is built with U{zenity<https://help.gnome.org/users/zenity/stable/>} so
make sure you have it installed for your distro.

BUILD DOCUMENTATION
===================

You can generate a local copy of the developer documentation using epydoc via

>>> make doc

You will find the doc under doc/html/ 

@version: 0.4
@status: testing (pre-release)
@authors: Paolo Libardi, Simona Righini, Marco Bartolini
@organization: INAF -IRA
@copyright: INAF - IRA (c) 2013
@license: gpl v3.0
@contact: bartolini@ira.inaf.it
"""

VERSION = "0.4.3"
NURAGHE_TAG = "nuraghe-0.5"
ESCS_TAG = "escs-0.5"

def cmd_line():
    import argparse
    import logging
    import os
    import sys

    import schedule, rich_validator, utils

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
        print "schedulecreator version: %s" % (VERSION,)
        sys.exit()
    #setting logger level and format
    if ns.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
    logger = logging.getLogger("schedulecreator")
    logger.info("Running with options:")
    for k,v in vars(ns).iteritems():
        logger.info("\t%s:\t%s" % (k, str(v),))

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
            logger.info("generating schedule from user input file")
            configuration_file = os.path.abspath(ns.configuration_file)
            if not os.path.exists(configuration_file):
                raise IOError("cannot find file %s" % configuration_file)
            src_directory = os.path.dirname(configuration_file)
            dst_directory = os.path.abspath(ns.directory)
            conf = rich_validator.validate_configuration(configuration_file)
            #setting target file in the same directory as schedule file
            conf['targetsFile'] = os.path.join(src_directory, conf['targetsFile'])
            _schedule = schedule.Schedule(conf)
            _schedule.set_base_dir(dst_directory)
            _schedule._write_schedule_files()
        logger.info('closing gently')
    except Exception, e:
        logger.info("exiting with error")
        logger.error(str(e))
        if ns.debug:
            raise
