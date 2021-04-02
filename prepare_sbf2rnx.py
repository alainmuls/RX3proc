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
from ampyutils import amutils, compress_utils, location

from sbf_daily import main_combine_sbf
from sbf_rinex import main_sbf2rnx3

__author__ = 'amuls'


# global used dictionary
global dProc
dProc = {}


def treatCmdOpts(argv: list):
    """
    Treats the command line options
    """
    baseName = os.path.basename(__file__)

    helpTxt = baseName + ' Combining and conversion of SBF files to RINEX v3.x Obs/Nav files'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('--root_dir', help='Root directory of SBF data collection (default {:s})'.format(colored(gco.ROOTDIR, 'green')), required=False, type=str, default=gco.ROOTDIR)

    parser.add_argument('--marker', help='marker name (4 chars)', required=True, type=str, action=gco.marker_action)
    parser.add_argument('--year', help='Year (4 digits)', required=True, type=int, action=gco.year_action)
    parser.add_argument('--doy', help='day-of-year [1..366]', required=True, type=int, action=gco.doy_action)

    parser.add_argument('--startepoch', help='specify start epoch hh:mm:ss (default {start:s})'.format(start=colored('00:00:00', 'green')), required=False, type=str, default='00:00:00', action=gco.epoch_action)
    parser.add_argument('--endepoch', help='specify end epoch hh:mm:ss (default {end:s})'.format(end=colored('23:59:59', 'green')), required=False, type=str, default='23:59:59', action=gco.epoch_action)

    parser.add_argument('--rnxdir', help='Directory for RINEX output (default {:s})'.format(colored('YYDOY subdir', 'green')), required=False, type=str, default='RNXDIR')

    parser.add_argument('--compress', help='compress obtained RINEX files', default=False, required=False, action='store_true')
    parser.add_argument('--overwrite', help='overwrite daily SBF file (default False)', action='store_true', required=False)

    parser.add_argument('--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv)

    # return arguments
    return args.root_dir, args.marker, args.year, args.doy, args.startepoch, args.endepoch, args.rnxdir, args.compress, args.overwrite, args.logging


def check_arguments(logger: logging.Logger = None):
    """
    check_arguments checks validity os setup and creates if needed dir for storing the rnx files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # check whether the directory exists in which the raw SBF files to combine/convert are located
    dProc['dirs']['sbf'] = os.path.expanduser(os.path.join(dProc['dirs']['root'], dProc['cli']['marker'], '{yy:02d}{doy:03d}'.format(yy=(dProc['cli']['yyyy'] % 100), doy=dProc['cli']['doy'])))

    if not amutils.CheckDir(directory=dProc['dirs']['sbf']):
        logger.error('{func:s}: SBF directory {sbfd:s} does not exist'.format(sbfd=colored(dProc['dirs']['sbf'], 'red'), func=cFuncName))
        sys.exit(amc.E_DIR_NOT_EXIST)

    # # chech rnx directory
    # dProc['dirs']['yydoy'] = os.path.expanduser(os.path.join(dProc['dirs']['root'], dProc['cli']['marker'], 'rinex', '{yy:02d}{doy:03d}'.format(yy=(dProc['cli']['yyyy'] % 100), doy=dProc['cli']['doy'])))

    # if not amutils.CheckDir(directory=dProc['dirs']['yydoy']):
    #     # create directory
    #     amutils.mkdir_p(dProc['dirs']['yydoy'])
    # if not amutils.changeDir(directory=dProc['dirs']['yydoy']):
    #     logger.error('{func:s}: problem changing to rnx directory {rnxd:s}'.format(rnxd=colored(dProc['dirs']['yydoy'], 'red'), func=cFuncName))
    #     sys.exit(amc.E_DIR_NOT_EXIST)


def combine_sbffiles(sbfdir: str, overwrite: bool = False, logger: logging.Logger = None) -> str:
    """
    combine_sbffiles callss sbf_dauly.py to combine (six-)hourly files into a daily file
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    sys.argv = ['--dir', sbfdir]
    if overwrite:
        sys.argv += ['--overwrite']

    if logger is not None:
        logger.info('=== {func:s}: passing control to {scr:s} (options: {opts!s}) ==='.format(scr=colored('sbf_daily.py', 'red'), opts=colored(' '.join(sys.argv), 'blue'), func=cFuncName))

    sbff = main_combine_sbf(argv=sys.argv)

    if sbff is None:
        logger.info('=== {func:s}: {scr:s} returned without combined SBF file'.format(scr=colored('sbf_daily.py', 'red'), func=cFuncName))
        sys.exit(amc.E_SBF2RIN_ERRCODE)

    return sbff


def sbf_rnx3(sbffile: str, sbfdir: str, rnxdir: str, start_ep: str, end_ep: str, logger: logging.Logger = None) -> Tuple[str, str]:
    """
    sbf_rnx3 converts created SBF file to a RNX 3 observation/navigation file by calling sbf_rinex.py
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    sys.argv = ['--sbff', os.path.join(sbfdir, sbffile), '--rnxdir', rnxdir]

    if start_ep != '00:00:00':
        sys.argv += ['--startepoch', start_ep]
    if end_ep != '23:59:59':
        sys.argv += ['--endepoch', end_ep]

    if logger is not None:
        logger.info('=== {func:s}: passing control to {scr:s}  (options: {opts!s}) ==='.format(scr=colored('sbf_rinex.py', 'red'), opts=colored(' '.join(sys.argv), 'blue'), func=cFuncName))

    rnx_obs3f, rnx_nav3f = main_sbf2rnx3(argv=sys.argv)

    return rnx_obs3f, rnx_nav3f


def main_prepare_rnx_data(argv):

    """
    creates a combined SBF file from hourly or six-hourly SBF files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    dProc['dirs'] = {}
    dProc['cli'] = {}
    dProc['rnx'] = {}

    dProc['dirs']['root'], dProc['cli']['marker'], dProc['cli']['yyyy'], dProc['cli']['doy'], dProc['cli']['startepoch'], dProc['cli']['endepoch'], rnxdir, dProc['cli']['compress'], dProc['cli']['overwrite'], logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), logLevels=logLevels)

    # check cli arguments
    check_arguments(logger=logger)

    # combine the SBF files in daily files
    dProc['sbffile'] = combine_sbffiles(sbfdir=dProc['dirs']['sbf'], overwrite=dProc['cli']['overwrite'], logger=logger)
    logger.info('>>>>>> {func:s}: obtained daily SBF file = {sbff:s}'.format(sbff=colored(dProc['sbffile'], 'yellow'), func=cFuncName))

    # check rnx directory
    if rnxdir == 'RNXDIR':
        dProc['dirs']['rnxdir'] = os.path.expanduser(os.path.join(dProc['dirs']['root'], dProc['cli']['marker'], 'rinex', '{yy:02d}{doy:03d}'.format(yy=(dProc['cli']['yyyy'] % 100), doy=dProc['cli']['doy'])))
    else:
        dProc['dirs']['rnxdir'] = rnxdir

    # convert the daily SBFFile to RINEX v3.x observation and navigation file
    dProc['rnx']['obs3f'], dProc['rnx']['nav3f'] = sbf_rnx3(sbffile=dProc['sbffile'], sbfdir=dProc['dirs']['sbf'], start_ep=dProc['cli']['startepoch'], end_ep=dProc['cli']['endepoch'], rnxdir=dProc['dirs']['rnxdir'], logger=logger)
    logger.info('>>>>>> {func:s}: obtained RINEX observation file = {obs3f:s}'.format(obs3f=colored(dProc['rnx']['obs3f'], 'yellow'), func=cFuncName))
    logger.info('>>>>>> {func:s}: obtained RINEX navigation files = {nav3f:s}'.format(nav3f=colored(dProc['rnx']['nav3f'], 'yellow'), func=cFuncName))

    # check whether to perform compression of RINEX files
    if dProc['cli']['compress']:
        dProc['bin'] = {}
        dProc['bin']['rnx2crz'] = location.locateProg('rnx2crz', logger)
        dProc['bin']['gzip'] = location.locateProg('gzip', logger)

        # observation file
        dProc['rnx']['obs3fc'] = compress_utils.compress_rnx_obs(rnx2crz=dProc['bin']['rnx2crz'], obsf=dProc['rnx']['obs3f'], rnxdir=dProc['dirs']['rnxdir'], logger=logger)
        logger.info('>>>>>> {func:s}: compressed RINEX observation file = {obs3fc:s}'.format(obs3fc=colored(dProc['rnx']['obs3fc'], 'yellow'), func=cFuncName))

        # navigation file
        dProc['rnx']['nav3fc'] = compress_utils.gzip_compress(gzip=dProc['bin']['gzip'], ungzipf=dProc['rnx']['nav3f'], dir=dProc['dirs']['rnxdir'], logger=logger)
        logger.info('>>>>>> {func:s}: compressed RINEX navigation file = {nav3fc:s}'.format(nav3fc=colored(dProc['rnx']['nav3fc'], 'yellow'), func=cFuncName))

    # report to the user
    logger.info('{func:s}: SBF preparation information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dProc, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # copy temp log file to the rnxdir directory
    copyfile(log_name, os.path.join(dProc['dirs']['rnxdir'], '{scrname:s}.log'.format(scrname=os.path.splitext(os.path.basename(__file__))[0])))
    os.remove(log_name)


if __name__ == "__main__":
    errcode = main_prepare_rnx_data(sys.argv[1:])

    sys.exit(errcode)
