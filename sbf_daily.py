#!/usr/bin/env python

import os
import argparse
import sys
import glob
import shutil
from termcolor import colored
from shutil import copyfile

from ampyutils import am_config as amc

__author__ = 'amuls'


class logging_action(argparse.Action):
    def __call__(self, parser, namespace, log_actions, option_string=None):
        choices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        for log_action in log_actions:
            if log_action not in choices:
                raise argparse.ArgumentError(self, "log_actions must be in {!s}".format(choices))
        setattr(namespace, self.dest, log_actions)


def treatCmdOpts(argv: list):
    """
    Treats the command line options and sets the global variables according to the CLI args

    :param argv: the options (without argv[0])
    :type argv: list of string
    """
    helpTxt = os.path.basename(__file__) + ' creates a daily SBF file based on (six) hourly SBF files found in given directory'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('--dir', help='Directory of SBF file (defaults to .)', required=False, default='.')
    parser.add_argument('--overwrite', help='overwrite daily SBF file (default False)', action='store_true', required=False)

    parser.add_argument('--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], action=logging_action)

    args = parser.parse_args(argv)

    return args.dir, args.overwrite, args.logging


def main_combine_sbf(argv):
    """
    main_combine_sbf creates a combined SBF file from hourly or six-hourly SBF files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    dirSBF, overwrite, logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), logLevels=logLevels)

    # change to the directory dirSBF if it exists
    workDir = os.getcwd()
    if dirSBF != '.':
        workDir = os.path.normpath(os.path.join(workDir, dirSBF))
    logger.info('{func:s}: working directory is {dir:s}'.format(func=cFuncName, dir=workDir))

    if not os.path.exists(workDir):
        logger.error('{func:s}: directory {dir:s} does not exists.'.format(func=cFuncName, dir=colored(workDir, 'red')))
        sys.exit(amc.E_DIR_NOT_EXIST)
    else:
        os.chdir(workDir)
        logger.info('{func:s}: changed to directory {dir:s}'.format(func=cFuncName, dir=workDir))

    # file that will be created
    dailySBF = None

    # find the files corresponsing to hourly SBF logged data, else serach for 6-hourly data
    # print(' hour = {!s}'.format(glob.glob(r"????[0-9][0-9][0-9][A-X].[0-9][0-9]_")))
    # print('6hour = {!s}'.format(glob.glob(r"????[0-9][0-9][0-9][1-4].[0-9][0-9]_")))
    hourlySBFs = sorted(glob.glob(r"????[0-9][0-9][0-9][A-X].[0-9][0-9]_"))
    sixHourlySBFs = sorted(glob.glob(r"????[0-9][0-9][0-9][1-4].[0-9][0-9]_"))

    # combine the files to create the daily SBF file
    logger.info('{func:s}: combine SBF (six-)hourly files to daily SBF file'.format(func=cFuncName))
    if len(hourlySBFs) > 0:
        dailySBF = hourlySBFs[0][:7] + '0' + hourlySBFs[0][8:]

        if not os.path.isfile(dailySBF) or overwrite:
            logger.info('{func:s}: creating daily SBF file {daily:s}'.format(func=cFuncName, daily=colored(dailySBF, 'green')))

            fDaily = open(dailySBF, 'wb')
            for i, hourlySBF in enumerate(hourlySBFs):
                fHourly = open(hourlySBF, 'rb')
                shutil.copyfileobj(fHourly, fDaily, 65536)
                fHourly.close()
            fDaily.close()
        else:
            logger.info('{func:s}: reusing daily SBF file {daily:s}'.format(func=cFuncName, daily=colored(dailySBF, 'green')))
    elif len(sixHourlySBFs) > 0:
        dailySBF = sixHourlySBFs[0][:7] + '0' + sixHourlySBFs[0][8:]

        if not os.path.isfile(dailySBF) or overwrite:
            logger.info('{func:s}: creating daily SBF file {daily:s}'.format(func=cFuncName, daily=colored(dailySBF, 'green')))

            fDaily = open(dailySBF, 'wb')
            for i, sixHourlySBF in enumerate(sixHourlySBFs):
                fSixHourly = open(sixHourlySBF, 'rb')
                shutil.copyfileobj(fSixHourly, fDaily, 65536)
                fSixHourly.close()
            fDaily.close()
        else:
            logger.info('{func:s}: reusing daily SBF file {daily:s}'.format(func=cFuncName, daily=colored(dailySBF, 'green')))
    else:
        # check whether a combined daily file is available
        dailySBF = sorted(glob.glob(r"????[0-9][0-9][0-9]0.[0-9][0-9]_"))[0]

        if dailySBF == '':
            logger.info('{func:s}: No SBF files found with syntax STATDOYS.YY_'.format(func=cFuncName))

    # copy temp log file to the YYDOY directory
    copyfile(log_name, os.path.join(workDir, '{scrname:s}.log'.format(scrname=os.path.splitext(os.path.basename(__file__))[0])))
    os.remove(log_name)

    # return created SBF filename
    return dailySBF


if __name__ == "__main__":
    daily_sbf = main_combine_sbf(argv=sys.argv[1:])

    print('daily_sbf = {!s}'.format(daily_sbf))
