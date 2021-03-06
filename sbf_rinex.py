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

    helpTxt = baseName + ' convert binary raw data from SBF to RINEX Obs & Nav files'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    # parser.add_argument('-s', '--sbfdir', help='SBF directory (default {:s})'.format(colored('.', 'green')), required=False, type=str, default='.')
    parser.add_argument('--sbffile', help='Binary SBF file', required=True, type=str)

    parser.add_argument('--rnxdir', help='Directory for RINEX output (default {:s})'.format(colored('.', 'green')), required=False, type=str, default='.')

    parser.add_argument('--startepoch', help='specify start epoch hh:mm:ss (default {start:s})'.format(start=colored('00:00:00', 'green')), required=False, type=str, default='00:00:00', action=gco.epoch_action)
    parser.add_argument('--endepoch', help='specify end epoch hh:mm:ss (default {end:s})'.format(end=colored('23:59:59', 'green')), required=False, type=str, default='23:59:59', action=gco.epoch_action)

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv)

    # return arguments
    return args.sbffile, args.rnxdir, args.startepoch, args.endepoch, args.logging


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

    if dRnx['time']['startepoch'] != '00:00:00':
        args4SBF2RIN += ['-b', dRnx['time']['startepoch']]
    if dRnx['time']['endepoch'] != '23:59:59':
        args4SBF2RIN += ['-e', dRnx['time']['endepoch']]

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
    list_of_rnx3_files = sorted(glob.glob(os.path.join(dRnx['dirs']['rnx'], '*.rnx')), key=os.path.getmtime)
    logger.info('{func:s}: sorted list (by modification time) of rnx files:\n{lst:s}'.format(lst='\n'.join(list_of_rnx3_files), func=cFuncName))

    return list_of_rnx3_files[-2:]


def main_sbf2rnx3(argv):
    """
    main_sbf2rnx3 converts raw data from SBF/UBlox to RINEX

    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    sbffile, rnxdir, startepoch, endepoch, logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), logLevels=logLevels)

    # store cli parameters
    dRnx['dirs'] = {}
    dRnx['dirs']['sbf'] = os.path.dirname(Path(sbffile).resolve())
    dRnx['sbff'] = os.path.basename(sbffile)
    dRnx['dirs']['rnx'] = Path(rnxdir).resolve()
    dRnx['time'] = {}

    if endepoch < startepoch:
        logger.error('{func:s}: startepoch {start:s} must be before endepoch {end:s}'.format(start=colored(startepoch, 'red'), end=colored(endepoch, 'red'), func=cFuncName))
        sys.exit(amc.E_INCORRECT_TIMES)

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
    copyfile(log_name, os.path.join(dRnx['dirs']['rnx'], '{scrname:s}.log'.format(scrname=os.path.basename(__file__).replace('.', '_'))))
    os.remove(log_name)

    return dRnx['obs3f'], dRnx['nav3f']


if __name__ == "__main__":  # Only run if this file is called directly
    rnx_obsf, rnx_navf = main_sbf2rnx3(argv=sys.argv[1:])
