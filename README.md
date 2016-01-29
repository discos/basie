# Basie

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)

Basie is a software package conceived to implement scheduling of
italian radiotelescopes via the creation of schedule files.

While previous ScheduleCreator software was conceived as a simple compiler
which translated instructions into telescope schedules, *basie* consists
of a complete Object Oriented model of the radiotelescope operations, opening
new possibilities and giving users and developers a major flexibility. 

## INSTALLATION INSTRUCTIONS

Basie (previously called ScheduleCreator) depends on Astropy and can thus run on
python >= 2.6.5  If you have multiple 2.x python version, please make sure to use the same one for install basie and its deps.
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

