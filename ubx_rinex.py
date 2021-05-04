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
from datetime import datetime

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

    parser.add_argument('--marker', help='marker name (4 chars)', required=True, type=str, action=gco.marker_action)
    parser.add_argument('--year', help='Year (4 digits)', required=True, type=int, action=gco.year_action)
    parser.add_argument('--doy', help='day-of-year [1..366]', required=True, type=int, action=gco.doy_action)

    parser.add_argument('--startepoch', help='specify start epoch hh:mm:ss (default {start:s})'.format(start=colored('00:00:00', 'green')), required=False, type=str, default='00:00:00', action=gco.epoch_action)
    parser.add_argument('--endepoch', help='specify end epoch hh:mm:ss (default {end:s})'.format(end=colored('23:59:59', 'green')), required=False, type=str, default='23:59:59', action=gco.epoch_action)

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv)

    # return arguments
    return args.ubxfile, args.rnxdir, args.marker, args.year, args.doy, args.startepoch, args.endepoch, args.logging


def checkValidityArgs(logger: logging.Logger) -> bool:
    """
    checks for existence of dirs/files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # change to baseDir, everything is relative to this directory
    logger.info('{func:s}: check existence of ubxDir {root:s}'.format(func=cFuncName, root=dRnx['dirs']['ubx']))

    # expand the directories
    for k, v in dRnx['dirs'].items():
        dRnx['dirs'][k] = os.path.expanduser(v)

    # check if SBF dire exists
    if not os.path.exists(dRnx['dirs']['ubx']):
        logger.error('{func:s}   !!! Dir {basedir:s} does not exist.'.format(func=cFuncName, basedir=dRnx['dirs']['ubx']))
        return amc.E_INVALID_ARGS

    # make the coplete filename by adding to ubxDir and check existence of binary file to convert
    logger.info('{func:s}: check existence of binary file {bin:s} to convert'.format(func=cFuncName, bin=os.path.join(dRnx['dirs']['ubx'], dRnx['ubxf'])))
    if not os.access(os.path.join(dRnx['dirs']['ubx'], dRnx['ubxf']), os.R_OK):
        logger.error('{func:s}   !!! binary observation file {bin:s} not accessible.'.format(func=cFuncName, bin=dRnx['ubxf']))
        return amc.E_FILE_NOT_EXIST

    # check existence of rnxdir and create if needed
    logger.info('{func:s}: check existence of rnxdir {rinex:s} and create if needed'.format(func=cFuncName, rinex=dRnx['dirs']['rnx']))
    amutils.mkdir_p(dRnx['dirs']['rnx'])

    return amc.E_SUCCESS


def sbf2rinex(logger: logging.Logger) -> list:
    """
    sbf2rinex converts a SBF file to rinex according to the GNSS systems selected
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # using the '-l' option the converted RINEX files are put in the current diretcory, so change first to the YYDOY dir
    amutils.changeDir(directory=dRnx['dirs']['rnx'])

    # convert to RINEX for selected GNSS system
    logger.info('{func:s}: RINEX conversion from UBX binary'.format(func=cFuncName))

    # we'll convert always by for only GPS & Galileo, excluding other GNSSs (G:GPS,R:GLONASS,E:Galileo,J:QZSS,S:SBAS,C:BeiDou)
    excludeGNSSs = 'RSCJ'


def main_ubx2rnx3(argv):
    """
    main_ubx2rnx3 converts raw data from UBX/UBlox to RINEX

    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    ubxfile, rnxdir, marker, yyyy, doy, startepoch, endepoch, logLevels, = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), logLevels=logLevels)

    # store cli parameters
    dRnx['dirs'] = {}
    dRnx['dirs']['ubx'] = os.path.dirname(Path(ubxfile).resolve())
    dRnx['dirs']['rnx'] = Path(rnxdir).resolve()

    dRnx['ubxf'] = os.path.basename(ubxfile)
    dRnx['marker'] = marker

    dRnx['time'] = {}
    if endepoch < startepoch:
        logger.error('{func:s}: startepoch {start:s} must be before endepoch {end:s}'.format(start=colored(startepoch, 'red'), end=colored(endepoch, 'red'), func=cFuncName))
        sys.exit(amc.E_INCORRECT_TIMES)

    dRnx['time']['YYYY'] = yyyy
    dRnx['time']['DOY'] = doy
    dRnx['time']['date'] = datetime.strptime('{year:04d}-{doy:03d}'.format(year=dRnx['time']['YYYY'], doy=dRnx['time']['DOY']), "%Y-%j")

    dRnx['time']['startepoch'] = startepoch
    dRnx['time']['endepoch'] = endepoch

    logger.info('{func:s}: arguments processed: dRnx = {drtk!s}'.format(func=cFuncName, drtk=dRnx))

    # check validity of passed arguments
    retCode = checkValidityArgs(logger=logger)
    if retCode != amc.E_SUCCESS:
        logger.error('{func:s}: Program exits with code {error:s}'.format(func=cFuncName, error=colored('{!s}'.format(retCode), 'red')))
        sys.exit(retCode)

    # locate the conversion programs SBF2RIN and CONVBIN
    dRnx['bin'] = {}
    # dRnx['bin']['CONVBIN'] = location.locateProg('convbin', logger)
    dRnx['bin']['CONVBIN'] = location.locateProg('convbin', logger)

    # convert binary file to rinex
    logger.info('{func:s}: convert binary file to rinex'.format(func=cFuncName))
    lst_rnx_files = ubf2rinex(logger=logger)


if __name__ == "__main__":  # Only run if this file is called directly
    rnx_obsf, rnx_navf = main_ubx2rnx3(argv=sys.argv[1:])
