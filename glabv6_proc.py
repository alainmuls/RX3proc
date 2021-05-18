#!/usr/bin/env python

import sys
import os
import argparse
from termcolor import colored
import json
import logging
import pathlib
from string import Template

from ampyutils import am_config as amc
from gfzrnx import gfzrnx_constants as gfzc
from ampyutils import amutils, location
from ampyutils import gnss_cmd_opts as gco

__author__ = 'amuls'


def treatCmdOpts(argv):
    """
    Treats the command line options

    :param argv: the options
    :type argv: list of string
    """
    baseName = os.path.basename(__file__)
    amc.cBaseName = colored(baseName, 'yellow')

    helpTxt = amc.cBaseName + ' gLAB (v6) processing of receiver position based on a template configuration file'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('--igsdir', help='Root IGS directory (default {igs:s}))'
                                         .format(igs=colored(gco.dir_igs, 'green')),
                        required=False,
                        type=str,
                        default=gco.dir_igs)

    parser.add_argument('--year', help='Year (4 digits)',
                        required=True, type=int,
                        action=gco.year_action)

    parser.add_argument('--doy', help='day-of-year [1..366]',
                        required=True, type=int,
                        action=gco.doy_action)

    parser.add_argument('--gnss', help='select GNSS(s) to use (out of {gnsss:s}, default {gnss:s})'
                                       .format(gnsss='|'.join(gfzc.lst_GNSSs),
                                               gnss=colored(gfzc.lst_GNSSs[0], 'green')),
                        default=gfzc.lst_GNSSs[0],
                        type=str,
                        required=False,
                        action=gco.gnss_action,
                        nargs='+')

    parser.add_argument('--cutoff', help='cutoff angle (default {cutoff:s})'
                                         .format(cutoff=colored('5 deg', 'green')),
                        required=False,
                        default=5,
                        type=int,
                        action=gco.cutoff_action)

    parser.add_argument('--template', help='glab template file (out of {tmpls:s}, default {tmpl:s})'
                                           .format(tmpls='|'.join(gco.dGLab_tmpls.values()),
                                                   tmpl=colored(gco.dGLab_tmpls['kin'], 'green')),
                        required=False,
                        type=str,
                        default=gco.dGLab_tmpls['kin'])

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'
                                          .format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')),
                        nargs=2,
                        required=False,
                        default=gco.lst_logging_choices[3:5],
                        action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv[1:])

    # return arguments
    return args.igsdir, args.year, args.doy, args.gnss, args.cutoff, args.template, args.logging


def check_arguments(logger: logging.Logger) -> int:
    """
    check_arguments checks the given arguments wether they are valid. return True or False
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # check whether the given dir_rnx exist
    # root directory for processing
    amc.dRTK['proc'] = {}

    amc.dRTK['proc']['dir_rnx'] = os.path.join(os.path.expanduser("~"), 'RxTURP/BEGPIOS', amc.dRTK['options']['rxtype'], 'rinex', '{yy:s}{doy:03d}'.format(yy=str(amc.dRTK['options']['year'])[-2:], doy=amc.dRTK['options']['doy']))
    path = pathlib.Path(amc.dRTK['proc']['dir_rnx'])
    if not path.is_dir():
        logger.info('{func:s}: root directory {root:s} does not exist'.format(root=colored(amc.dRTK['proc']['dir_rnx'], 'red'), func=cFuncName))
        return amc.E_DIR_NOT_EXIST
    else:  # change to directory
        os.chdir(path)

    # check whether the given IGS dir exist
    amc.dRTK['proc']['dir_igs'] = os.path.join(amc.dRTK['options']['igs_root'], '{yy:s}{doy:03d}'.format(yy=str(amc.dRTK['options']['year'])[-2:], doy=amc.dRTK['options']['doy']))
    path = pathlib.Path(amc.dRTK['proc']['dir_igs'])
    if not path.is_dir():
        logger.info('{func:s}: IGS directory {igs:s} does not exist'.format(igs=colored(amc.dRTK['proc']['dir_igs'], 'red'), func=cFuncName))
        return amc.E_DIR_NOT_EXIST

    # path to the glab directory, create it of not existing
    amc.dRTK['proc']['dir_glab'] = os.path.join(amc.dRTK['proc']['dir_rnx'], 'glab')
    path = pathlib.Path(amc.dRTK['proc']['dir_glab'])
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)
        logger.info('{func:s}: Created glab directory {glab:s} does not exist'.format(glab=colored(amc.dRTK['proc']['dir_glab'], 'green'), func=cFuncName))

    # check whether the template file exists
    path = pathlib.Path(amc.dRTK['options']['template'])
    if not path.is_file():
        logger.info('{func:s}: gLAB template file {tmpl:s} does not exist'.format(tmpl=colored(amc.dRTK['options']['template'], 'red'), func=cFuncName))
        return amc.E_FILE_NOT_EXIST

    # create the RINEX obs name and check whether it exists
    amc.dRTK['proc']['cmp_obs'] = '{marker:s}{doy:03d}0.{yy:s}D.Z'.format(marker=amc.dRTK['options']['marker'], yy=str(amc.dRTK['options']['year'])[-2:], doy=amc.dRTK['options']['doy'])

    # determine the options for GNSS and codes / freqs
    amc.dRTK['proc']['marker'] = amc.dRTK['options']['marker']
    amc.dRTK['proc']['gnss'] = [gnss for gnss in amc.dRTK['options']['gnss']]
    amc.dRTK['proc']['cmp_nav'] = []
    for gnss in amc.dRTK['proc']['gnss']:
        # determine the navigation files used (currently using the IGS NAV files - should be changed)
        amc.dRTK['proc']['cmp_nav'].append('BRUX00BEL_R_{year:04d}{doy:03d}0000_01D_{gnss:s}N.rnx.gz'.format(year=amc.dRTK['options']['year'], doy=amc.dRTK['options']['doy'], gnss=gnss))

    # get the codes used and corresponding frequency numbers
    amc.dRTK['proc']['codes'] = [code for code in amc.dRTK['options']['prcodes']]
    amc.dRTK['proc']['freqs'] = [prcode[1:2] for prcode in amc.dRTK['proc']['codes']]

    # name for glab output file
    amc.dRTK['proc']['glab_out'] = '{marker:s}-{gnss:s}-{codes:s}.out'.format(marker=amc.dRTK['proc']['marker'], gnss=''.join(amc.dRTK['proc']['gnss']), codes='-'.join(amc.dRTK['proc']['codes']))
    amc.dRTK['proc']['glab_cfg'] = amc.dRTK['proc']['glab_out'][:-3] + 'cfg'

    return amc.E_SUCCESS


def create_session_template(logger: logging.Logger):
    """
    create_session_template creates the configuration file for glabng
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # create dict used for replacing the template keywords
    dTemplate = {}
    dTemplate['CMP_OBS_FILE'] = os.path.join(amc.dRTK['proc']['dir_rnx'], amc.dRTK['proc']['obs'])
    dTemplate['CMP_NAV_FILES'] = ''
    for nav_file in amc.dRTK['proc']['nav']:
        dTemplate['CMP_NAV_FILES'] += ' ' + os.path.join(amc.dRTK['proc']['dir_igs'], nav_file)
    dTemplate['CUTOFF_ANGLE'] = amc.dRTK['options']['cutoff']
    dTemplate['GNSS'] = ''.join(amc.dRTK['proc']['gnss'])
    if len(amc.dRTK['proc']['codes']) == 1:
        dTemplate['PRCODES'] = '-'.join(amc.dRTK['proc']['codes'])
    else:
        dTemplate['PRCODES'] = 'PC' + ''.join(amc.dRTK['proc']['freqs']) + '-' + '-'.join(amc.dRTK['proc']['codes'])
    dTemplate['GLAB_OUT'] = os.path.join(amc.dRTK['proc']['dir_glab'], amc.dRTK['proc']['glab_out'])

    # report to the user
    # logger.info('{func:s}: creating config file {cfg:s} using:\n{json!s}'.format(cfg=colored(amc.dRTK['proc']['glab_cfg'], 'green'), func=cFuncName, json=json.dumps(dTemplate, sort_keys=False, indent=4, default=amutils.DT_convertor)))

    # create the configuration file
    try:
        f_tmpl = open(amc.dRTK['options']['template'])
        glab_templ = Template(f_tmpl.read())

        # substitute the variables in the template file
        glab_cfg = glab_templ.substitute(dTemplate)

        # save to configuration file
        fd_cfg = open(os.path.join(amc.dRTK['proc']['dir_glab'], amc.dRTK['proc']['glab_cfg']), 'w')
        fd_cfg.write(glab_cfg)
        fd_cfg.close()

        logger.info('{func:s}: created glab configuration file {cfg:s}\n{content!s}'.format(cfg=amc.dRTK['proc']['glab_cfg'], content=glab_cfg, func=cFuncName))

    except IOError:
        logger.info('{func:s}: problems using template file {tmpl:s}'.format(tmpl=amc.dRTK['options']['template'], func=cFuncName))
        sys.exit(amc.E_FILE_NOT_EXIST)


def run_glabng_session(logger: logging.Logger):
    """
    run_glabng_session runs gLAB (v6.x) using provided configuration file
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # uncompress the RINEX OBS file
    runGLABNG = '{prog:s} -input:cfg {cfg:s}'.format(prog=amc.dRTK['progs']['glabng'], cfg=os.path.join(amc.dRTK['proc']['dir_glab'], amc.dRTK['proc']['glab_cfg']))
    logger.info('{func:s}: Running:\n{cmd:s}'.format(func=cFuncName, cmd=colored(runGLABNG, 'green')))

    # run the program
    exeprogram.subProcessDisplayStdOut(cmd=runGLABNG, verbose=True)

    # compress the resulting "out" file
    runGZIP = '{prog:s} -f {zip:s}'.format(prog=amc.dRTK['progs']['gzip'], zip=os.path.join(amc.dRTK['proc']['dir_glab'], amc.dRTK['proc']['glab_out']))
    logger.info('{func:s}: compressing {out:s} file by:\n{cmd:s}'.format(out=amc.dRTK['proc']['glab_out'], func=cFuncName, cmd=colored(runGZIP, 'green')))
    # run the program
    exeprogram.subProcessDisplayStdErr(cmd=runGZIP, verbose=True)

    runGZIP


def main_glab_proc(argv) -> bool:
    """
    glabplotposn plots data from gLAB (v6) OUTPUT messages

    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # store cli parameters
    amc.dRTK = {}
    cli_opt = {}
    cli_opt['igs_root'], cli_opt['year'], cli_opt['doy'], cli_opt['gnss'], cli_opt['cutoff'], cli_opt['template'], log_levels = treatCmdOpts(argv)
    amc.dRTK['options'] = cli_opt

    # check some arguments

    # create logging for better debugging
    logger, log_name = amc.createLoggers(os.path.basename(__file__), dir=os.getcwd(), logLevels=log_levels)

    ret_val = check_arguments(logger=logger)
    if ret_val != amc.E_SUCCESS:
        sys.exit(ret_val)

    # locate the program used for execution
    amc.dRTK['progs'] = {}
    amc.dRTK['progs']['glabng'] = location.locateProg('glabng', logger)
    amc.dRTK['progs']['crz2rnx'] = location.locateProg('crz2rnx', logger)
    amc.dRTK['progs']['gunzip'] = location.locateProg('gunzip', logger)
    amc.dRTK['progs']['gzip'] = location.locateProg('gzip', logger)

    # use the template file for creation of glab config file
    create_session_template(logger=logger)

    # run glabng using created cfg file
    run_glabng_session(logger=logger)

    # report to the user
    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(amc.dRTK, sort_keys=False, indent=4, default=amutils.DT_convertor)))

    # # move the log file to the glab directory
    # code_txt = ''
    # for code in amc.dRTK['proc']['codes']:
    #     code_txt += ('_' + code)
    # move(log_name, os.path.join(amc.dRTK['proc']['dir_glab'], 'glab_proc_{gnss:s}{prcodes:s}.log'.format(gnss=''.join(amc.dRTK['proc']['gnss']), prcodes=code_txt)))

    return amc.E_SUCCESS


if __name__ == "__main__":  # Only run if this file is called directly
    main_glab_proc(sys.argv)
