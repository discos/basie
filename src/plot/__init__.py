##coding=utf-8

import logging
from basie import VERSION

def cmd_line():
    import argparse
    import os
    import sys

    #Adding command line options
    parser = argparse.ArgumentParser(description="Plot .lis files of radiotelescope schedules")
    parser.add_argument('-d', action='store_true', help="enable debug messages",
                        dest='debug')
    parser.add_argument('--version', action='store_true', dest='show_version',
                        help='print version information and exit')
    parser.add_argument('filename', default="TestSched.lis", nargs='?',
                        help="The .lis file from where to extract plots")
    #parsing command line arguments
    ns = parser.parse_args()
    if ns.show_version:
        print "basie-plot-lis version: %s" % (VERSION,)
        sys.exit()
    #setting logger level and format
    if ns.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.INFO)
    logger = logging.getLogger("basie.plot")
    logger.debug("Running with options:")
    for k,v in vars(ns).iteritems():
        logger.debug("\t%s:\t%s" % (k, str(v),))

    #imports are here as logging has already been configured
    if not os.path.exists(ns.filename):
        logger.error("cannot find file %s" % (ns.filename,))
        sys.exit(1)



