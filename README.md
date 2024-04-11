# Basie

[![DOI](https://zenodo.org/badge/19074/discos/basie.svg)](https://zenodo.org/badge/latestdoi/19074/discos/basie)
[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)
[![Build Status](https://travis-ci.org/discos/basie.svg?branch=master)](https://travis-ci.org/discos/basie)

Basie is a software package conceived to implement scheduling of
italian radiotelescopes via the creation of schedule files.

While previous ScheduleCreator software was conceived as a simple compiler
which translated instructions into telescope schedules, *basie* consists
of a complete Object Oriented model of the radiotelescope operations, opening
new possibilities and giving users and developers a major flexibility.

## USER MANUAL

You can
[download the user manual](http://github.com/discos/basie/raw/master/Basie_user_manual.pdf) directly from this repository.

## INSTALLATION INSTRUCTIONS

### Preliminary information
Basie  can  run on python >= 3.8

We *strongly* recommend to install `basie` in a virtual environment, using [`conda`](https://www.anaconda.com/download/),
[`venv`](https://docs.python.org/3/library/venv.html), or equivalent systems. This will avoid conflicts with system libraries or
Python versions installed as part of other packages (e.g. CASA, see below in the Known Issues).

#### Venv
To create a virtual environment using `venv`, you can follow these steps:

1. Open your terminal or command prompt.

2. Navigate to the directory where you want to create your virtual environment. This could be the root directory of your project or any other location of your choice.

3. Run the following command to create a new virtual environment:
    ```$ python3 -m venv myenv```

   Here, `myenv` is the name you choose for your virtual environment, and `python3` is the executable of the chosen (we recommend recent) Python version. You can replace it with any name you prefer.

4. Once the command completes, a new directory named myenv (or the name you chose) will be created in your current directory. This directory will contain all the necessary files and folders for your virtual environment.

5. Activate the virtual environment by running the appropriate command based on your operating system, typically `source /path/to/myenv/bin/activate`

#### Conda
If you installed `anaconda` or `miniconda`, the process will be as simple as

```
$ conda create -n my_fancy_environment python=3.11
$ conda activate my_fancy_environment
```

### Installing basie

Before installing the package make sure you download and extract the package
archive at
http://github.com/discos/basie/

Installation instructions can be reduced to:

```
$ pip install .
```

Note that, in some systems, you may need to have root privileges for installing python packages.
If you want to know more or you experience some issue, please go on reading.

You can remove the downloaded package or clean build products via:

```
$ pip uninstall basie
```

## KNOWN ISSUES

1. `NRAO CASA` is known to install its own version of Python and `pip`. We recommend installing CASA in its own `venv` or `conda` virtual environment to avoid conflicts.
In principle, it should be possible to install `basie` with `CASA`'s `pip`.

If you find an issue, please report it through [our Github Issue tracker](https://github.com/discos/basie/issues)

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

