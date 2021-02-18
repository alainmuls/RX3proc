#!/usr/bin/env python

import sys
import os
import argparse
from termcolor import colored
import logging
import json
from typing import Tuple
import shutil
from nested_lookup import nested_lookup
from datetime import datetime

from gfzrnx import gfzrnx_constants as gfzc
from ampyutils import gnss_cmd_opts as gco

from ampyutils import am_config as amc
from ampyutils import amutils, location
from plot import obsstat_plot
from gfzrnx import rnxobs_analysis
from ltx import ltx_obstab_reporting

__author__ = 'amuls'


def treatCmdOpts(argv):
    """
    Treats the command line options

    :param argv: the options
    :type argv: list of string
    """
    baseName = os.path.basename(__file__)
    amc.cBaseName = colored(baseName, 'yellow')

    helpTxt = amc.cBaseName + ' creates observation tabular/statistics file for selected GNSSs'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('-r', '--rnxobsf', help='RINEX observation file', type=str, required=True)

    parser.add_argument('-g', '--gnsss', help='select (1 or more) GNSS(s) to use (out of {gnsss:s}, default {gnss:s})'.format(gnsss='|'.join(gfzc.lst_GNSSs), gnss=colored(gfzc.lst_GNSSs[0], 'green')), default=gfzc.lst_GNSSs[0], type=str, required=False, action=gco.gnss_action, nargs='+')
    # parser.add_argument('-t', '--types_obs', help='select observation types(s) to use (out of {osbtypes:s}, default {osbtype:s})'.format(osbtypes='|'.join(gfzc.lst_obstypes), osbtype=colored(gfzc.lst_obstypes[0], 'green')), default=gfzc.lst_obstypes[0], type=str, required=False, action=gco.obstype_action, nargs='+')

    # parser.add_argument('-p', '--plot', help='displays interactive plots (default False)', action='store_true', required=False, default=False)

    parser.add_argument('-l', '--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv[1:])

    # return arguments
    return args.rnxobsf, args.gnsss, args.logging


def create_tabular_observations(gfzrnx: str, obsf: str, gnss: str, logger: logging.Logger = None) -> Tuple[str, str]:
    """
    create_create_tabular_observations creates for the selected GNSSs the tabular observation file and returns its name
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # create the observation tabular file
    obs_tabf = '{basen:s}_{gnss:s}.obstab'.format(basen=os.path.splitext(obsf)[0], gnss=gnss)

    args4GFZRNX = [gfzrnx, '-finp', obsf, '-tab_obs', '-fout', obs_tabf, '-f', '-tab_sep', ',', '-satsys', gnss]

    if logger is not None:
        logger.info('{func:s} creating observation tabular file {obstab:s}'.format(obstab=colored(obs_tabf, 'blue'), func=cFuncName))
    # run program
    err_code, proc_out = amutils.run_subprocess_output(sub_proc=args4GFZRNX, logger=logger)
    if err_code != amc.E_SUCCESS:
        logger.error('{func:s}: error {err!s} creating observation tabular file {obstab:s}'.format(err=err_code, obstab=colored(obs_tabf, 'blue'), func=cFuncName))
        sys.exit(err_code)
    else:
        print('proc_out = \n{!s}'.format(proc_out))

    # create the observation statistics file
    # gfzrnx -finp COMB00XXX_R_20191340000_01D_01S_MO.rnx -stk_obs -obs_types S
    obs_statf = '{basen:s}_{gnss:s}.obsstat'.format(basen=os.path.splitext(obsf)[0], gnss=gnss)
    args4GFZRNX = [gfzrnx, '-finp', obsf, '-stk_obs', '-fout', obs_statf, '-f', '-satsys', gnss]

    if logger is not None:
        logger.info('{func:s} creating observation statistics file {obstab:s}'.format(obstab=colored(obs_statf, 'blue'), func=cFuncName))
    # run program
    err_code, proc_out = amutils.run_subprocess_output(sub_proc=args4GFZRNX, logger=logger)
    if err_code != amc.E_SUCCESS:
        logger.error('{func:s}: error {err!s} creating observation statistics file {obstab:s}'.format(err=err_code, obstab=colored(obs_statf, 'blue'), func=cFuncName))
        sys.exit(err_code)
    else:
        print('proc_out = \n{!s}'.format(proc_out))

    return obs_tabf, obs_statf


def rnx_tabular(argv):
    """
    rnx2obstab adds statistics to RINEX file, makes ::RX3:: format and crates the observation tabular file
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # store parameters in dicttionaries
    dGFZRNX = {}
    dGFZRNX['info'] = {}
    dGFZRNX['cli'] = {}
    dGFZRNX['bin'] = {}
    dGFZRNX['hdr'] = {}
    dGFZRNX['ltx'] = {}
    dGFZRNX['obstab'] = {}

    # treat command line options
    dCLI = {}
    rnx3obsf, dCLI['GNSSs'], logLevels = treatCmdOpts(argv)
    dCLI['obsf'] = os.path.basename(rnx3obsf)
    dCLI['path'] = os.path.dirname(rnx3obsf)
    dGFZRNX['cli'] = dCLI

    # create logging for better debugging
    logger, log_name = amc.createLoggers(baseName=os.path.basename(__file__), logLevels=logLevels)

    # get RINEX dir and RINEX file name separately
    # dGFZRNX['path'], dGFZRNX['obsf'] = os.path.split(os.path.abspath(obsf))

    # external program
    dGFZRNX['bin']['gfzrnx'] = location.locateProg(progName='gfzrnx', logger=logger)

    # check & change to rnx path
    if not amutils.changeDir(dGFZRNX['cli']['path']):
        logger.error('{func:s}: changing to directory {dir:s} failed'.format(dir=dGFZRNX['path'], func=cFuncName))
        sys.exit(amc.E_DIR_NOT_EXIST)

    # check accessibilty of observation file
    if not amutils.file_exists(fname=dGFZRNX['cli']['obsf'], logger=logger):
        logger.error('{func:s}: observation file {file:s} not accessible'.format(file=dGFZRNX['cli']['obsf'], func=cFuncName))
        sys.exit(amc.E_FILE_NOT_EXIST)

    # create dir for storing the latex sections
    dGFZRNX['ltx']['path'] = os.path.join(dGFZRNX['cli']['path'], 'ltx')
    if not amutils.mkdir_p(dGFZRNX['ltx']['path']):
        logger.error('{func:s}: cannot create directory {dir:s} failed'.format(dir=dGFZRNX['ltx']['path'], func=cFuncName))
        sys.exit(amc.E_FAILURE)

    # examine the header of the RX3 observation file
    dGFZRNX['hdr'] = rnxobs_analysis.RX3obs_header_info(gfzrnx=dGFZRNX['bin']['gfzrnx'], obs3f=dGFZRNX['cli']['obsf'], logger=logger)

    logger.info('{func:s}: dGFZRNX[hdr] =\n{json!s}'.format(func=cFuncName, json=json.dumps(dGFZRNX['hdr'], sort_keys=False, indent=4, default=amutils.json_convertor)))

    # extract information from the header useful for later usage
    obs_date = nested_lookup(key='first', document=dGFZRNX['hdr'])[0]
    dGFZRNX['info']['obs_date'] = datetime.strptime(obs_date.split('.')[0], '%Y %m %d %H %M %S').strftime('%d %B %Y')
    print(dGFZRNX['cli']['obsf'])
    dGFZRNX['info']['marker'] = dGFZRNX['cli']['obsf'][:9]
    dGFZRNX['info']['yyyy'] = int(dGFZRNX['cli']['obsf'][12:16])
    dGFZRNX['info']['doy'] = int(dGFZRNX['cli']['obsf'][16:19])

    logger.info('{func:s}: dGFZRNX =\n{json!s}'.format(func=cFuncName, json=json.dumps(dGFZRNX, sort_keys=False, indent=4, default=amutils.json_convertor)))

    sec_script = ltx_obstab_reporting.obstab_script_information(dCli=dGFZRNX['cli'], dHdr=dGFZRNX['hdr'], dInfo=dGFZRNX['info'], script_name=os.path.basename(__file__))

    dGFZRNX['ltx']['script'] = os.path.join(dGFZRNX['ltx']['path'], 'script_info')
    sec_script.generate_tex(dGFZRNX['ltx']['script'])

    # create the tabular observation file for the selected GNSSs
    for gnss in dGFZRNX['cli']['GNSSs']:
        dGFZRNX['obstab'][gnss] = {}
        # create names for obs_tab and obs_stat files for current gnss
        obs_tabf = 'obs_{gnss:s}_tabf'.format(gnss=gnss)
        obs_statf = 'obs_{gnss:s}_statf'.format(gnss=gnss)
        dGFZRNX['obstab'][gnss][obs_tabf], dGFZRNX['obstab'][gnss][obs_statf] = create_tabular_observations(gfzrnx=dGFZRNX['bin']['gfzrnx'], obsf=dGFZRNX['cli']['obsf'], gnss=gnss, logger=logger)

        # plot the observation statistics
        # obsstat_plot.obsstat_plot_obscount(obs_statf=dGFZRNX['obstab'][obs_statf], gnss=gnss, gfzrnx=dGFZRNX['bin']['gfzrnx'], show_plot=show_plot, logger=logger)

    # report to the user
    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dGFZRNX, sort_keys=False, indent=4, default=amutils.json_convertor)))

    shutil.copyfile(log_name, os.path.join(dGFZRNX['cli']['path'], '{:s}.log'.format(os.path.basename(__file__).replace('.', '_'))))
    os.remove(log_name)

    return dGFZRNX['obstab']


if __name__ == "__main__":  # Only run if this file is called directly
    dObstabs = rnx_tabular(sys.argv)

    print('dObstabs = {!s}'.format(dObstabs))
