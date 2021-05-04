#!/usr/bin/env python

import sys
import os
import argparse
from termcolor import colored
import json
import logging
from shutil import copyfile
from pathlib import Path
import glob

from ampyutils import gnss_cmd_opts as gco

from ampyutils import am_config as amc
from ampyutils import amutils, location

__author__ = 'amuls'

# global used dict
global dRnx
dRnx = {}


def treatCmdOpts(argv: list):
    """
    Treats the command line options
    """
    baseName = os.path.basename(__file__)
    amc.cBaseName = colored(baseName, 'yellow')

    helpTxt = baseName + ' convert binary raw data from UBX to RINEX Obs & Nav files'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    # parser.add_argument('-s', '--ubxdir', help='UBX directory (default {:s})'.format(colored('.', 'green')), required=False, type=str, default='.')
    parser.add_argument('--ubxfile', help='Binary UBX file', required=True, type=str)

    parser.add_argument('--rnxdir', help='Directory for RINEX output (default {:s})'.format(colored('.', 'green')), required=False, type=str, default='.')

    parser.add_argument('--startepoch', help='specify start epoch hh:mm:ss (default {start:s})'.format(start=colored('00:00:00', 'green')), required=False, type=str, default='00:00:00', action=gco.epoch_action)
    parser.add_argument('--endepoch', help='specify end epoch hh:mm:ss (default {end:s})'.format(end=colored('23:59:59', 'green')), required=False, type=str, default='23:59:59', action=gco.epoch_action)

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv)

    # return arguments
    return args.ubxfile, args.rnxdir, args.startepoch, args.endepoch, args.logging


def main_ubx2rnx3(argv):
    """
    main_ubx2rnx3 converts raw data from UBX/UBlox to RINEX

    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    ubxfile, rnxdir, startepoch, endepoch, logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), logLevels=logLevels)

    # store cli parameters
    dRnx['dirs'] = {}
    dRnx['dirs']['ubx'] = os.path.dirname(Path(ubxfile).resolve())
    dRnx['ubxf'] = os.path.basename(ubxfile)
    dRnx['dirs']['rnx'] = Path(rnxdir).resolve()
    dRnx['time'] = {}

    if endepoch < startepoch:
        logger.error('{func:s}: startepoch {start:s} must be before endepoch {end:s}'.format(start=colored(startepoch, 'red'), end=colored(endepoch, 'red'), func=cFuncName))
        sys.exit(amc.E_INCORRECT_TIMES)

    dRnx['time']['startepoch'] = startepoch
    dRnx['time']['endepoch'] = endepoch

    logger.info('{func:s}: arguments processed: dRnx = {drtk!s}'.format(func=cFuncName, drtk=dRnx))


if __name__ == "__main__":  # Only run if this file is called directly
    rnx_obsf, rnx_navf = main_ubx2rnx3(argv=sys.argv[1:])
