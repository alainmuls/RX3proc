#!/usr/bin/env python

import os
import argparse
import sys
from termcolor import colored
from shutil import copyfile
import logging
from typing import Tuple
import json

from ampyutils import am_config as amc
from ampyutils import gnss_cmd_opts as gco
from gfzrnx import gfzrnx_constants as gfzc

from ampyutils import amutils, compress_utils, location

from rnx15_combine import combine_rnx15
__author__ = 'amuls'


# global used dictionary
global dProc
dProc = {}


def treatCmdOpts(argv: list):
    """
    Treats the command line options
    """
    baseName = os.path.basename(__file__)

    helpTxt = baseName + ' Combining partial (15 minutes) RINEX v3.x Obs/Nav files'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('--root_dir', help='Directory of 15 min P3RS2 data collection (default {:s})'.format(colored(gco.P3RS2PVTLSDIR, 'green')), required=False, type=str, default=gco.P3RS2PVTLSDIR)
    parser.add_argument('--rnx_dir', help='Root directory of P3RS2 RINEX files (default {:s})'.format(colored(gco.P3RS2RNXDIR, 'green')), required=False, type=str, default=gco.P3RS2RNXDIR)

    parser.add_argument('--marker', help='marker name (4 chars)', required=True, type=str, action=gco.marker_action)
    parser.add_argument('--year', help='Year (4 digits)', required=True, type=int, action=gco.year_action)
    parser.add_argument('--doy', help='day-of-year [1..366]', required=True, type=int, action=gco.doy_action)

    parser.add_argument('--obs_crux', help='CRUX template file for updating RINEX headers (default {crux:s})'.format(crux=colored(gfzc.crux_tmpl, 'green')), required=False, type=str, default=gfzc.crux_tmpl)

    parser.add_argument('--compress', help='compress obtained RINEX files', default=False, required=False, action='store_true')

    parser.add_argument('--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv)

    # return arguments
    return args.root_dir, args.rnx_dir, args.marker, args.year, args.doy, args.obs_crux, args.compress, args.logging


def check_arguments(logger: logging.Logger = None):
    """
    check_arguments checks validity os setup and creates if needed dir for storing the rnx files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # check whether the directory exists in which the partial P3RS2 files to combine/convert are located
    dProc['dirs']['pvt'] = os.path.expanduser(dProc['dirs']['pvt'])

    if not amutils.CheckDir(directory=dProc['dirs']['pvt']):
        if logger is not None:
            logger.error('{func:s}: P3RS2 log pvt directory {pvtd:s} does not exist'.format(pvtd=colored(dProc['dirs']['pvt'], 'red'), func=cFuncName))
        sys.exit(amc.E_DIR_NOT_EXIST)

    # check if given crux file exists
    dProc['cli']['cruxf'] = os.path.expanduser(os.path.join(os.getcwd(), dProc['cli']['cruxf']))
    if not amutils.CheckFile(filename=dProc['cli']['cruxf']):
        if logger is not None:
            logger.error('{func:s}: observation crux file {crux:s} does not exist'.format(crux=colored(dProc['cli']['cruxf'], 'red'), func=cFuncName))
        sys.exit(amc.E_FILE_NOT_EXIST)

    # # chech / create rnx directory
    # dProc['dirs']['yydoy'] = os.path.expanduser(os.path.join(gco.P3RS2RNXDIR, '{yy:02d}{doy:03d}'.format(yy=(dProc['cli']['yyyy'] % 100), doy=dProc['cli']['doy'])))

    # if not amutils.CheckDir(directory=dProc['dirs']['yydoy']):
    #     # create directory
    #     amutils.mkdir_p(dProc['dirs']['yydoy'])
    # if not amutils.changeDir(directory=dProc['dirs']['yydoy']):
    #     logger.error('{func:s}: problem changing to yydoy directory {rnxd:s}'.format(rnxd=colored(dProc['dirs']['yydoy'], 'red'), func=cFuncName))
    #     sys.exit(amc.E_DIR_NOT_EXIST)


def combine_P3RS2_data(p3rs2_dir: str, rnx_dir: str, marker: str, year: int, doy: int, cruxf: str, logger: logging.Logger = None) -> Tuple[str, str, str]:
    """
    calls rnx15_combine to get the ::RX3:: corrected P3RS2 files for this day
    """
    # usage: rnx15_combine.py [-h] [-f FROM_DIR] [-r RNX_DIR] -m MARKER -y YEAR -d DOY [-c CRUX] [-l LOGGING LOGGING]
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # prepare the options to call rnx15_combine.py
    sys.argv = ['--from_dir', p3rs2_dir, '--rnx_dir', rnx_dir, '--marker', marker, '--year', str(year), '--doy', str(doy), '--crux', cruxf]

    if logger is not None:
        logger.info('=== {func:s}: passing control to {scr:s} (options: {opts!s}) ==='.format(scr=colored('rnx15_combine.py', 'red'), opts=colored(' '.join(sys.argv), 'blue'), func=cFuncName))

    rnxdir, obs3f, nav3f = combine_rnx15(argv=sys.argv)

    return rnxdir, obs3f, nav3f


def main_prepare_P3RS2_data(argv) -> Tuple[str, str, str]:

    """
    combines the 15 min data files from P3RS2
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    dProc['dirs'] = {}
    dProc['cli'] = {}
    dProc['rnx'] = {}

    dProc['dirs']['pvt'], dProc['dirs']['rnx_root'], dProc['cli']['marker'], dProc['cli']['yyyy'], dProc['cli']['doy'], dProc['cli']['cruxf'], dProc['cli']['compress'], logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), logLevels=logLevels)

    # check cli arguments
    check_arguments(logger=logger)

    # # yydoy directory
    # dProc['dirs']['yydoy'] = os.path.expanduser(os.path.join(gco.P3RS2RNXDIR, '{yy:02d}{doy:03d}'.format(yy=(dProc['cli']['yyyy'] % 100), doy=dProc['cli']['doy'])))

    # call combination of partial rnx files
    dProc['dirs']['yydoy'], dProc['rnx']['obs3f'], dProc['rnx']['nav3f'] = combine_P3RS2_data(p3rs2_dir=dProc['dirs']['pvt'], rnx_dir=dProc['dirs']['rnx_root'], marker=dProc['cli']['marker'], year=dProc['cli']['yyyy'], doy=dProc['cli']['doy'], cruxf=dProc['cli']['cruxf'], logger=logger)

    logger.info('>>>>>> {func:s}: RINEX directory = {rnxd:s}'.format(rnxd=colored(dProc['dirs']['yydoy'], 'yellow'), func=cFuncName))
    logger.info('>>>>>> {func:s}: obtained RINEX observation file = {obs3f:s}'.format(obs3f=colored(dProc['rnx']['obs3f'], 'yellow'), func=cFuncName))
    logger.info('>>>>>> {func:s}: obtained RINEX navigation files = {nav3f:s}'.format(nav3f=colored(dProc['rnx']['nav3f'], 'yellow'), func=cFuncName))

    # check whether to perform compression of RINEX files
    print("dProc[cli][compress] = {!s}".format(dProc['cli']['compress']))
    if dProc['cli']['compress']:
        dProc['bin'] = {}
        dProc['bin']['rnx2crz'] = location.locateProg('rnx2crz', logger)
        dProc['bin']['gzip'] = location.locateProg('gzip', logger)

        # observation file
        obs3fc = compress_utils.compress_rnx_obs(rnx2crz=dProc['bin']['rnx2crz'], obsf=dProc['rnx']['obs3f'], rnxdir=dProc['dirs']['yydoy'], logger=logger)
        dProc['rnx']['obs3fc'] = os.path.basename(obs3fc)
        logger.info('>>>>>> {func:s}: compressed RINEX observation file = {obs3fc:s}'.format(obs3fc=colored(dProc['rnx']['obs3fc'], 'yellow'), func=cFuncName))

        # navigation file
        nav3fc = compress_utils.gzip_compress(gzip=dProc['bin']['gzip'], ungzipf=dProc['rnx']['nav3f'], dir=dProc['dirs']['yydoy'], logger=logger)
        dProc['rnx']['nav3fc'] = os.path.basename(nav3fc)
        logger.info('>>>>>> {func:s}: compressed RINEX navigation file = {nav3fc:s}'.format(nav3fc=colored(dProc['rnx']['nav3fc'], 'yellow'), func=cFuncName))

    # report to the user
    logger.info('{func:s}: SBF preparation information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dProc, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # copy temp log file to the YYDOY directory
    copyfile(log_name, os.path.join(dProc['dirs']['yydoy'], '{scrname:s}.log'.format(scrname=os.path.splitext(os.path.basename(__file__))[0])))
    os.remove(log_name)

    if not dProc['cli']['compress']:
        return dProc['dirs']['yydoy'], dProc['rnx']['obs3f'], dProc['rnx']['nav3f']
    else:
        return dProc['dirs']['yydoy'], dProc['rnx']['obs3fc'], dProc['rnx']['nav3fc']


if __name__ == "__main__":
    rnxdir, obs3f, nav3f = main_prepare_P3RS2_data(sys.argv[1:])
