#!/usr/bin/env python

import sys
import os
import argparse
from termcolor import colored
import logging
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

from gfzrnx import gfzrnx_constants as gfzc
from ampyutils import gnss_cmd_opts as gco

from ampyutils import am_config as amc
from ampyutils import amutils
from tle import tle_visibility, tle_plot

__author__ = 'amuls'


def treatCmdOpts(argv):
    """
    Treats the command line options

    :param argv: the options
    :type argv: list of string
    """
    baseName = os.path.basename(__file__)
    amc.cBaseName = colored(baseName, 'yellow')

    helpTxt = amc.cBaseName + ' analyses observation tabular/statistics file for selected GNSSs'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('-o', '--obsstat', help='observation statistics file', type=str, required=True)

    parser.add_argument('-f', '--freqs', help='select frequencies to use (out of {freqs:s}, default {freq:s})'.format(freqs='|'.join(gfzc.lst_freqs), freq=colored(gfzc.lst_freqs[0], 'green')), default=gfzc.lst_freqs[0], type=str, required=False, action=gco.freqtype_action, nargs='+')

    parser.add_argument('-i', '--interval', help='measurement interval in seconds (default {interv:s}s)'.format(interv=colored('1', 'green')), required=False, default=1., type=float, action=gco.interval_action)

    parser.add_argument('-c', '--cutoff', help='curoff angle in degrees (default {mask:s})'.format(mask=colored('5', 'green')), default=5, type=int, required=False, action=gco.cutoff_action)

    parser.add_argument('-p', '--plot', help='displays interactive plots (default False)', action='store_true', required=False, default=False)

    parser.add_argument('-l', '--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv[1:])

    # return arguments
    return args.obsstat, args.freqs, args.interval, args.cutoff, args.plot, args.logging


def check_arguments(logger: logging.Logger = None):
    """
    check arhuments and change working directory
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # check & change working dir
    dStat['dir'] = os.path.dirname(Path(dStat['cli']['obsstatf']).resolve())
    dStat['obsstatf'] = os.path.basename(dStat['cli']['obsstatf'])

    if not amutils.changeDir(dStat['dir']):
        if logger is not None:
            logger.error('{func:s}: changing to directory {dir:s} failed'.format(dir=dStat['dir'], func=cFuncName))
        sys.exit(amc.E_DIR_NOT_EXIST)

    # check accessibilty of observation statistics file
    if not amutils.file_exists(fname=dStat['obsstatf'], logger=logger):
        if logger is not None:
            logger.error('{func:s}: observation file {file:s} not accessible'.format(file=dStat['obsstatf'], func=cFuncName))
        sys.exit(amc.E_FILE_NOT_EXIST)

    # create dir for storing the latex sections
    dStat['ltx']['path'] = os.path.join(dStat['dir'], 'ltx')
    if not amutils.mkdir_p(dStat['ltx']['path']):
        if logger is not None:
            logger.error('{func:s}: cannot create directory {dir:s} failed'.format(dir=dStat['ltx']['path'], func=cFuncName))
        sys.exit(amc.E_FAILURE)

    # extract YY and DOY from filename
    dStat['time']['YYYY'] = int(dStat['obsstatf'][12:16])
    dStat['time']['DOY'] = int(dStat['obsstatf'][16:19])
    # converting to date
    dStat['time']['date'] = datetime.strptime('{year:04d}-{doy:03d}'.format(year=dStat['time']['YYYY'], doy=dStat['time']['DOY']), "%Y-%j")


def read_obsstat(logger: logging.Logger = None):
    """
    read_obsstat reads the SNR for the selected frequencies into a dataframe
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    dfTmp = pd.read_csv(dStat['obsstatf'], delim_whitespace=True)

    if logger is not None:
        amutils.logHeadTailDataFrame(df=dfTmp, dfName='dfTmp', callerName=cFuncName, logger=logger)

    # select the SNR colmuns for the selected frequencies
    col_names = dfTmp.columns.tolist()
    print(col_names)
    cols2keep = col_names[:4]
    for freq in dStat['cli']['freqs']:
        cols2keep += [col for col in col_names[4:] if col.startswith('S{freq:s}'.format(freq=freq))]

    return dfTmp[cols2keep]


def rnxobs_analyse(argv):
    """
    rnxobs_analyse analyses the created OBSSTAT files and compares with TLE data
    """

    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    global dStat
    dStat = {}
    dStat['cli'] = {}
    dStat['time'] = {}
    dStat['ltx'] = {}

    dStat['cli']['obsstatf'], dStat['cli']['freqs'], dStat['time']['interval'], dStat['cli']['mask'], show_plot, logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(baseName=os.path.basename(__file__), logLevels=logLevels)

    # verify input
    check_arguments(logger=logger)

    # read obsstat into a dataframe and select the SNR for the selected frequencies
    dfObsStat = read_obsstat(logger=logger)
    amutils.logHeadTailDataFrame(df=dfObsStat, dfName='dfObsStat', callerName=cFuncName, logger=logger)

    # get the observation time spans based on TLE values
    dfTLE = tle_visibility.PRNs_visibility(prn_lst=dfObsStat.TYP.unique(), cur_date=dStat['time']['date'], interval=dStat['time']['interval'], cutoff=dStat['cli']['mask'], logger=logger)
    amutils.logHeadTailDataFrame(df=dfTLE, dfName='dfTLE', callerName=cFuncName, logger=logger)
    # store the observation info from TLE in CVS file
    tle_name = '{base:s}.tle'.format(base=os.path.basename(dStat['obsstatf']).split('.')[0])
    dfTLE.to_csv(tle_name, index=True)
    # plot the TLE arcs
    tle_plot.tle_plot_arcs(dfTle=dfTLE, dTime=dStat['time'], show_plot=show_plot, logger=logger)

    # report to the user
    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dStat, sort_keys=False, indent=4, default=amutils.json_convertor)))


if __name__ == "__main__":  # Only run if this file is called directly
    rnxobs_analyse(sys.argv)
