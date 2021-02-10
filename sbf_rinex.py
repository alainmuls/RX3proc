#!/usr/bin/env python

import sys
import os
import argparse
from termcolor import colored
import json
import logging
from shutil import copyfile
import glob

from ampyutils import am_config as amc
from ampyutils import amutils, location

__author__ = 'amuls'

# global used dict
global dRnx
dRnx = {}


# class interval_action(argparse.Action):
#     def __call__(self, parser, namespace, interval, option_string=None):
#         if not 5 <= int(interval) <= 60:
#             raise argparse.ArgumentError(self, "interval must be in 5..60 minutes")
#         setattr(namespace, self.dest, interval)


class logging_action(argparse.Action):
    def __call__(self, parser, namespace, log_actions, option_string=None):
        choices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        for log_action in log_actions:
            if log_action not in choices:
                raise argparse.ArgumentError(self, "log_actions must be in {!s}".format(choices))
        setattr(namespace, self.dest, log_actions)


def treatCmdOpts(argv: list):
    """
    Treats the command line options
    """
    baseName = os.path.basename(__file__)
    amc.cBaseName = colored(baseName, 'yellow')

    helpTxt = baseName + ' convert binary raw data from SBF to RINEX Obs & Nav files'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('-s', '--sbfdir', help='SBF directory (default {:s})'.format(colored('.', 'green')), required=False, type=str, default='.')
    parser.add_argument('-f', '--file', help='Binary SBF file', required=True, type=str)

    parser.add_argument('-r', '--rnxdir', help='Directory for RINEX output (default {:s})'.format(colored('.', 'green')), required=False, type=str, default='.')

    parser.add_argument('-l', '--logging', help='specify logging level console/file (default {:s})'.format(colored('INFO DEBUG', 'green')), nargs=2, required=False, default=['INFO', 'DEBUG'], action=logging_action)

    # drop argv[0]
    args = parser.parse_args(argv)

    # return arguments
    return args.sbfdir, args.file, args.rnxdir, args.logging


def checkValidityArgs(logger: logging.Logger) -> bool:
    """
    checks for existence of dirs/files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # change to baseDir, everything is relative to this directory
    logger.info('{func:s}: check existence of sbfDir {root:s}'.format(func=cFuncName, root=dRnx['dirs']['sbf']))

    # expand the directories
    for k, v in dRnx['dirs'].items():
        dRnx['dirs'][k] = os.path.expanduser(v)

    # check if SBF dire exists
    if not os.path.exists(dRnx['dirs']['sbf']):
        logger.error('{func:s}   !!! Dir {basedir:s} does not exist.'.format(func=cFuncName, basedir=dRnx['dirs']['sbf']))
        return amc.E_INVALID_ARGS

    # make the coplete filename by adding to sbfDir and check existence of binary file to convert
    logger.info('{func:s}: check existence of binary file {bin:s} to convert'.format(func=cFuncName, bin=os.path.join(dRnx['dirs']['sbf'], dRnx['sbff'])))
    if not os.access(os.path.join(dRnx['dirs']['sbf'], dRnx['sbff']), os.R_OK):
        logger.error('{func:s}   !!! binary observation file {bin:s} not accessible.'.format(func=cFuncName, bin=dRnx['sbff']))
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
    logger.info('{func:s}: RINEX conversion from SBF binary'.format(func=cFuncName))

    # we'll convert always by for only GPS & Galileo, excluding other GNSSs
    excludeGNSSs = 'RSCJI'

    # convert to RINEX observable file
    args4SBF2RIN = [dRnx['bin']['SBF2RIN'], '-f', os.path.join(dRnx['dirs']['sbf'], dRnx['sbff']), '-x', excludeGNSSs, '-s', '-D', '-v', '-R3', '-l', '-O', 'BEL']
    # run the sbf2rin program
    logger.info('{func:s}: creating RINEX observation file'.format(func=cFuncName))
    err_code, proc_out = amutils.run_subprocess_output(sub_proc=args4SBF2RIN, logger=logger)
    if err_code != amc.E_SUCCESS:
        logger.error('{func:s}: error {err!s} converting {sbff:s} to RINEX observation ::RX3::'.format(err=err_code, sbff=dRnx['sbff'], func=cFuncName))
        sys.exit(err_code)
    else:
        if len(proc_out.strip()) > 0:
            print('   process output = {!s}'.format(proc_out))

    # convert to RINEX NAVIGATION file
    args4SBF2RIN = [dRnx['bin']['SBF2RIN'], '-f', os.path.join(dRnx['dirs']['sbf'], dRnx['sbff']), '-x', excludeGNSSs, '-s', '-D', '-v', '-n', 'P', '-R3', '-l', '-O', 'BEL']
    # run the sbf2rin program
    logger.info('{func:s}: creating RINEX navigation file'.format(func=cFuncName))
    err_code, proc_out = amutils.run_subprocess_output(sub_proc=args4SBF2RIN, logger=logger)
    if err_code != amc.E_SUCCESS:
        logger.error('{func:s}: error {err!s} converting {sbff:s} to RINEX navigation ::RX3::'.format(err=err_code, sbff=dRnx['sbff'], func=cFuncName))
        sys.exit(err_code)
    else:
        if len(proc_out.strip()) > 0:
            print('   process output = {!s}'.format(proc_out))

    # RINEX files are created in the SBF directory, have to move them to RNX dir
    list_of_rnx_files = glob.glob(os.path.join(dRnx['dirs']['rnx'], '*.rnx'))

    return list_of_rnx_files[:2]


def sbf2rnx3(argv):
    """
    pyconvbin converts raw data from SBF/UBlox to RINEX

    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    sbfDir, sbffile, rnxdir, logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), logLevels=logLevels)

    # store cli parameters
    dRnx['dirs'] = {}
    dRnx['dirs']['sbf'] = sbfDir
    dRnx['sbff'] = sbffile
    dRnx['dirs']['rnx'] = rnxdir

    logger.info('{func:s}: arguments processed: dRnx = {drtk!s}'.format(func=cFuncName, drtk=dRnx))

    # check validity of passed arguments
    retCode = checkValidityArgs(logger=logger)
    if retCode != amc.E_SUCCESS:
        logger.error('{func:s}: Program exits with code {error:s}'.format(func=cFuncName, error=colored('{!s}'.format(retCode), 'red')))
        sys.exit(retCode)

    # locate the conversion programs SBF2RIN and CONVBIN
    dRnx['bin'] = {}
    # dRnx['bin']['CONVBIN'] = location.locateProg('convbin', logger)
    dRnx['bin']['SBF2RIN'] = location.locateProg('sbf2rin', logger)
    # dRnx['bin']['GFZRNX'] = location.locateProg('gfzrnx', logger)
    # dRnx['bin']['RNX2CRZ'] = location.locateProg('rnx2crz', logger)
    # dRnx['bin']['COMPRESS'] = location.locateProg('compress', logger)
    # dRnx['bin']['GZIP'] = location.locateProg('gzip', logger)

    # convert binary file to rinex
    logger.info('{func:s}: convert binary file to rinex'.format(func=cFuncName))
    lst_rnx_files = sbf2rinex(logger=logger)

    dRnx['obs3f'] = lst_rnx_files[0]
    dRnx['nav3f'] = lst_rnx_files[1]

    # report to the user
    logger.info('{func:s}: dRnx =\n{json!s}'.format(func=cFuncName, json=json.dumps(dRnx, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # store the json structure
    jsonName = os.path.join(dRnx['dirs']['rnx'], '{scrname:s}.json'.format(scrname=os.path.splitext(os.path.basename(__file__))[0]))
    with open(jsonName, 'w+') as f:
        json.dump(dRnx, f, ensure_ascii=False, indent=4, default=amutils.json_convertor)

    # clean up
    os.remove(log_name)

    return dRnx['obs3f'], dRnx['nav3f']


if __name__ == "__main__":  # Only run if this file is called directly
    rnx_obsf, rnx_navf = sbf2rnx3(argv=sys.argv[1:])
