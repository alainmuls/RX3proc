#!/usr/bin/env python

import sys
import os
import argparse
from termcolor import colored
import logging
import json
from typing import Union
import glob
import pathlib
import pandas as pd
import tempfile
from shutil import copyfile
import re
from datetime import datetime
from math import ceil

from ampyutils import am_config as amc
from ampyutils import gnss_cmd_opts as gco
from gfzrnx import gfzrnx_constants as gfzc

from ampyutils import amutils, location

__author__ = 'amuls'

# global used dictionary
global dRnx
dRnx = {}


def treatCmdOpts(argv):
    """
    Treats the command line options

    :param argv: the options
    :type argv: list of string
    """
    baseName = colored(os.path.basename(__file__), 'yellow')

    helpTxt = baseName + ' combines P3RS2 RINEX observation / navigation files'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)
    parser.add_argument('--from_dir', help='Directory of P3RS2 RINEX files (default {:s})'.format(colored('.', 'green')), required=False, type=str, default='.')
    parser.add_argument('--rnx_dir', help='Root directory of P3RS2 RINEX files (default {:s})'.format(colored(gco.P3RS2RNXDIR, 'green')), required=False, type=str, default=gco.P3RS2RNXDIR)
    parser.add_argument('--marker', help='marker name (4 chars)', required=True, type=str, action=gco.marker_action)
    parser.add_argument('--year', help='Year (4 digits)', required=True, type=int, action=gco.year_action)
    parser.add_argument('--doy', help='day-of-year [1..366]', required=True, type=int, action=gco.doy_action)

    parser.add_argument('--startepoch', help='specify start epoch hh:mm:ss (default {start:s})'.format(start=colored('00:00:00', 'green')), required=False, type=str, default='00:00:00', action=gco.epoch_action)
    parser.add_argument('--endepoch', help='specify end epoch hh:mm:ss (default {end:s})'.format(end=colored('23:59:59', 'green')), required=False, type=str, default='23:59:59', action=gco.epoch_action)

    parser.add_argument('--crux', help='CRUX template file for updating RINEX headers (default {crux:s})'.format(crux=colored(gfzc.crux_tmpl, 'green')), required=False, type=str, default=gfzc.crux_tmpl)

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv)

    # return arguments
    return args.from_dir, args.rnx_dir, args.marker, args.year, args.doy, args.startepoch, args.endepoch, args.crux, args.logging


def list_rinex_files(logger: logging.Logger) -> Union[list, list]:
    """
    list_rinex_files return a list with OBS and one with NAV files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    file_pattern = 'P3RS-2_RX_R_{year:04d}{doy:03d}*_15M_00U_MO.rnx'.format(year=dRnx['cli']['year'], doy=dRnx['cli']['doy'])
    lst_obsf = sorted(glob.glob(file_pattern))

    file_pattern = 'P3RS-2_RX_R_{year:04d}{doy:03d}*_15M_MN.rnx'.format(year=dRnx['cli']['year'], doy=dRnx['cli']['doy'])
    lst_nav = sorted(glob.glob(file_pattern))

    logger.info('{func:s}: found {count:d} RINEX observation files'.format(count=len(lst_obsf), func=cFuncName))
    logger.info('{func:s}: found {count:d} RINEX navigation files'.format(count=len(lst_nav), func=cFuncName))

    return lst_obsf, lst_nav


def check_obstypes_order(lst_obsf: list, logger: logging.Logger = None) -> bool:
    """
    check_obstypes_order checks whether the RINEX OBS has the same order for the observable types
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # create tmp file for storing the observables
    lst_obst = []
    for rnx_obs in lst_obsf:
        with open(rnx_obs, 'r') as frnx:
            lst_obst.append(sorted(amutils.lines_that_contain('SYS / # / OBS TYPES', frnx)))
            logger.debug('{func:s}: {obsf:s}: {obst!s}'.format(obsf=rnx_obs, obst=lst_obst[-1], func=cFuncName))

    # create dataframe of this lst_obst
    col_hdrs = [obst[:1] for obst in lst_obst[0]]
    df_obst = pd.DataFrame(lst_obst, columns=[col_hdrs])

    if logger is not None:
        logger.debug('{func:s}: obs types found\n{obst!s}'.format(obst=df_obst, func=cFuncName))

    obst_uniq = df_obst.nunique()

    ret_value = True
    for col in df_obst.columns:
        ret_value &= (obst_uniq[col] == 1)

    return ret_value


def combine_rnx_obs(lst_obsf: list, ext: str, logger: logging.Logger) -> str:
    """
    combine_rnx_obs combines the found observation files
    """
    #  Example: ALGO00CAN_R_20121601000_01H_05Z_MO.rnx.gz //1 hour, Obs Mixed and 5Hz

    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # dRnx['obsf'] = 'P3RS00BEL_R_{year:04s}{doy:03s}{start:04s}_01D_01S_MO.rnx'.format(year=dRnx['cli']['year'], doy=dRnx['cli']['doy'], start=start_time)
    tmp_obsf = os.path.join(tempfile.gettempdir(), 'P3RS{doy:03d}0.{yy:02d}{ext:s}'.format(doy=dRnx['cli']['doy'], yy=(dRnx['cli']['year'] % 100), ext=ext))

    # regular expression used to search for erroneous formatted fields (pseudo-distance)
    regex = re.compile(r"^\D\d{4}")
    # regex = re.compile(r"^[:upper:][:digit:]{4}")

    # count_error_rnxobs = 0
    with open(tmp_obsf, 'w') as fout:
        for i, rnx_obs in enumerate(lst_obsf):

            # rewrite to temp file with the erroneous pseudo-range records removed
            with open(rnx_obs, "r") as f:
                lines = f.readlines()
            with open(os.path.join('/tmp/', rnx_obs), "w") as f:
                for line in lines:
                    if not re.search(regex, line):
                        f.write(line)

            # process_rnxobs = True

            # # check if current rnx_obs file has erroneous pseudo-range values
            # for jj, line in enumerate(open(rnx_obs)):
            #     if re.search(regex, line):
            #         print('{:d}: {:s}'.format(jj, line.strip()))
            #         # logger.info('{func:s}: erroneous data in {rnxobs:s}:{line:d}'.format(rnxobs=rnx_obs, line=jj + 1, func=cFuncName))
            #         count_error_rnxobs += 1
            #         process_rnxobs = False
            #         # break


            # if process_rnxobs:
            # include the hedaer from the first file
            if i == 0:
                eof_hdr = 0
            else:
                eof_hdr = amutils.line_num_for_phrase_in_file(phrase='END OF HEADER', filename=rnx_obs) + 1

            # for the last file, make sure we do not include data from the next day
            if i < len(lst_obsf) - 1:
                with open(os.path.join('/tmp/', rnx_obs)) as fobs:
                    lines_data = fobs.readlines()
                    # print('\nos.path.join('/tmp/', rnx_obs) = {!s}'.format(os.path.join('/tmp/', rnx_obs)))
                    # print('len lines_data = {:d}'.format(len(lines_data)))
                    # print('eof_hdr = {:d}'.format(eof_hdr))
                    # print('start lines = \n{!s}'.format(''.join(lines_data[eof_hdr:eof_hdr + 2])))
                    # print('end lines = \n{!s}'.format(''.join(lines_data[-3:])))
                    fout.write(''.join(lines_data[eof_hdr:]))
            else:
                # find line that starts at new day in the next day
                dRnx['rnx']['date'] = amutils.yeardoy2ymd(year=dRnx['cli']['year'], doy=dRnx['cli']['doy'] + 1)
                search_date = dRnx['rnx']['date'].strftime("> %Y %m %d")
                begin_next_day = amutils.line_num_for_phrase_in_file(phrase=search_date, filename=os.path.join('/tmp/', rnx_obs))

                if begin_next_day == -1:
                    # last file has no day-over effect
                    with open(os.path.join('/tmp/', rnx_obs)) as fobs:
                        lines_data = fobs.readlines()
                        # print('\nos.path.join('/tmp/', rnx_obs) = {!s}'.format(os.path.join('/tmp/', rnx_obs)))
                        # print('len lines_data = {:d}'.format(len(lines_data)))
                        # print('eof_hdr = {:d}'.format(eof_hdr))
                        # print('start lines = \n{!s}'.format(''.join(lines_data[eof_hdr:eof_hdr + 2])))
                        # print('end lines = \n{!s}'.format(''.join(lines_data[-3:])))
                        fout.write(''.join(lines_data[eof_hdr:]))
                else:
                    with open(os.path.join('/tmp/', rnx_obs)) as fobs:
                        lines_data = fobs.readlines()

                        # print('\nos.path.join('/tmp/', rnx_obs) = {!s}'.format(os.path.join('/tmp/', rnx_obs)))
                        # print('len lines_data = {:d}'.format(len(lines_data)))
                        # print('eof_hdr = {:d}'.format(eof_hdr))
                        # print('begin_next_day = {:d}'.format(begin_next_day))
                        # print('start lines = \n{!s}'.format(''.join(lines_data[eof_hdr:eof_hdr + 2])))
                        # print('end lines = \n{!s}'.format(''.join(lines_data[begin_next_day - 3:begin_next_day])))
                        fout.write(''.join(lines_data[eof_hdr:begin_next_day]))

            os.remove(os.path.join('/tmp/', rnx_obs))

    logger.info('{func:s}: combined {count:d} RINEX files into {obsf:s}'.format(count=len(lst_obsf), obsf=tmp_obsf, func=cFuncName))

    return tmp_obsf


def create_crux_file(crux_tmpl: str, marker: str, logger: logging.Logger = None):
    """
    create_crux_file creates the crux file used to correct the RINEX headers
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    with open(crux_tmpl, 'r') as finp:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_cruxf:
            for line in finp:
                newline = line.replace('$(marker)', '"{marker:s}04BEL"'.format(marker=marker))
                tmp_cruxf.write(newline)

    if logger is not None:
        logger.info('{func:s}: created crux file {crux!s}'.format(crux=colored(tmp_cruxf.name, 'blue'), func=cFuncName))

    return tmp_cruxf.name


def convert_obsrnx3(gfzrnx: str, rnxf_tmp: str, cruxf: str, rnxdir: str, yyyy: int, doy: int, start_ep: str, end_ep: str, logger: logging.Logger = None) -> str:
    """
    convert_obsrnx3 updates the observation header file and converts to ::RX3::
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # determine name for obs file
    obsf = os.path.basename(rnxf_tmp)

    # get the correct RINEX v3 naming convention
    args4gfzrnx = [gfzrnx, '-finp', rnxf_tmp, '-nomren23', '04,BEL']  #  '-try_append', '900', '-splice_direct'

    # convert start / end epochs to datatime
    dt_start_ep = datetime.strptime('{yyyy:04d}/{doy:03d} {epoch:s}'.format(yyyy=yyyy, doy=doy, epoch=start_ep),
                                    '%Y/%j %H:%M:%S')
    dt_end_ep = datetime.strptime('{yyyy:04d}/{doy:03d} {epoch:s}'.format(yyyy=yyyy, doy=doy, epoch=end_ep),
                                  '%Y/%j %H:%M:%S')
    dt_minutes = ceil((dt_end_ep - dt_start_ep).total_seconds() / 60)
    # print(dt_start_ep)
    # print(type(dt_start_ep))
    # print(dt_end_ep)
    # print(type(dt_end_ep))
    # print(dt_minutes)
    # print(type(dt_minutes))

    err_code, rnx3f = amutils.run_subprocess_output(sub_proc=args4gfzrnx, logger=logger)
    if err_code != amc.E_SUCCESS:
        if logger is not None:
            logger.error('{func:s}: error {err!s} creating ::RX3:: filename'.format(err=err_code, func=cFuncName))
        sys.exit(err_code)

    # gfzrnx -finp P3RS3010.20O -fout P3RS3010.rnx -crux ~/amPython/RX3proc/test.crux  -hded
    args4gfzrnx = [gfzrnx, '-finp', rnxf_tmp, '-crux', cruxf, '-f', '-fout', os.path.join(rnxdir, rnx3f)]

    # adjust final file for the start / end times
    args4gfzrnx += ['-epo_beg', '{yyyy:04d}{doy:03d}_{start_ep:s}'.format(yyyy=yyyy, doy=doy,
                                                                          start_ep=''.join(start_ep.split(':')))]
    args4gfzrnx += ['-d', dt_minutes * 60]
    print(args4gfzrnx)
    if logger is not None:
        logger.info('{func:s}: adjusting RINEX header for {name:s}'.format(name=colored(obsf, 'green'), func=cFuncName))

    # perform the RINEX creation
    err_code, proc_out = amutils.run_subprocess_output(sub_proc=args4gfzrnx, logger=logger)
    if err_code != amc.E_SUCCESS:
        if logger is not None:
            logger.error('{func:s}: error {err!s} converting {obsf:s} to RINEX observation ::RX3::'.format(err=err_code, obsf=rnxf_tmp, func=cFuncName))
        sys.exit(err_code)
    else:
        if (len(proc_out.strip()) > 0) and (logger is not None):
            logger.info('   process output = {!s}'.format(proc_out))

    return rnx3f


def convert_navrnx3(gfzrnx: str, rnxf_tmp: str, cruxf: str, rnxdir: str, logger: logging.Logger = None) -> str:
    """
    convert_navrnx3 updates the navigation file and converts to ::RX3::
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # chenge to rnxdir
    amutils.changeDir(rnxdir)

    # determine the basename of the navigation file
    navf = os.path.basename(rnxf_tmp)

    # convert to ::RX3:: navigation file with limit of nav records to current observation period
    # gfzrnx -finp /tmp/P3RS3110.20M -fout ::RX3::FRA -f -sei in -hded -crux /tmp/tmpqomc28ny"
    args4gfzrnx = [gfzrnx, '-finp', rnxf_tmp, '-crux', cruxf, '-f', '-sei', 'in', '-chk', '-fout', '::RX3::04,BEL']

    if logger is not None:
        logger.info('{func:s}: adjusting RINEX header for {name:s}'.format(name=colored(navf, 'green'), func=cFuncName))

    # perform the RINEX creation
    err_code, proc_out = amutils.run_subprocess_output(sub_proc=args4gfzrnx, logger=logger)
    if err_code != amc.E_SUCCESS:
        if logger is not None:
            logger.error('{func:s}: error {err!s} converting {navf:s} to RINEX navigation ::RX3::'.format(err=err_code, navf=rnxf_tmp, func=cFuncName))
        sys.exit(err_code)
    else:
        if (len(proc_out.strip()) > 0) and (logger is not None):
            logger.info('   process output = {!s}'.format(proc_out))

    # get last created file in rnxdir
    navf = os.path.basename(glob.glob(os.path.join('.', '*.rnx'))[0])

    return navf


def main_combine_rnx15(argv):
    """
    main_combine_rnx15 combines the P3RS2 RINEX files of 15 minutes and creates correct ::RX3:: files
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # treat command line options
    # store cli parameters
    cli_opt = {}
    cli_opt['from_dir'], cli_opt['rnx_dir'], cli_opt['marker'], cli_opt['year'], cli_opt['doy'], cli_opt['start_ep'], cli_opt['end_ep'], cruxf, logLevels = treatCmdOpts(argv)
    cli_opt['crux'] = os.path.expanduser(cruxf)
    dRnx['cli'] = cli_opt

    # default location for P3RS2 RINEX files
    dRnx['dirs'] = {}
    dRnx['dirs']['rinex'] = os.path.expanduser(cli_opt['rnx_dir'])

    # create logging for better debugging
    logger, log_name = amc.createLoggers(baseName=os.path.basename(__file__), logLevels=logLevels)

    # external program
    dRnx['bin'] = {}
    dRnx['bin']['gfzrnx'] = location.locateProg(progName='gfzrnx', logger=logger)
    dRnx['bin']['rnx2crz'] = location.locateProg(progName='rnx2crz', logger=logger)
    dRnx['bin']['gzip'] = location.locateProg(progName='gzip', logger=logger)

    # change to rinex directory
    path = pathlib.Path(dRnx['cli']['from_dir'])
    if not path.is_dir():
        logger.info('{func:s}: P3RS2 RINEX directory {rnxd:s} does not exist'.format(rnxd=colored(dRnx['cli']['from_dir'], 'red'), func=cFuncName))
        return amc.E_DIR_NOT_EXIST
    else:  # change to directory
        os.chdir(path)

    # get list of OBS/NAV files for yyyy/doy
    dRnx['rnx'] = {}
    dRnx['p3rs2'] = {}
    dRnx['p3rs2']['obs'], dRnx['p3rs2']['nav'] = list_rinex_files(logger=logger)

    if (len(dRnx['p3rs2']['obs']) > 0) and (len(dRnx['p3rs2']['nav']) > 0):
        # create RINEX dir for combined files
        yydoy = '{yy:02d}{doy:03d}'.format(yy=(dRnx['cli']['year'] % 100), doy=dRnx['cli']['doy'])
        dRnx['dirs']['yydoy'] = os.path.join(dRnx['dirs']['rinex'], yydoy)
        amutils.mkdir_p(dRnx['dirs']['yydoy'])
    else:
        logger.error('{func:s}: no files found for {doy:03d}/{yy:02d}'.format(doy=dRnx['cli']['doy'], yy=dRnx['cli']['year'] % 100, func=cFuncName))
        sys.exit(amc.E_NORINEXOBS)

    tmp_obsf = tmp_navf = ''

    # create the crux information file to use for correcting headers
    crux_file = create_crux_file(crux_tmpl=dRnx['cli']['crux'], marker=dRnx['cli']['marker'], logger=logger)

    # combine the RINEX quaterly observation files
    if len(dRnx['p3rs2']['obs']) > 0:
        # check order of observation types in rinex file
        if not check_obstypes_order(lst_obsf=dRnx['p3rs2']['obs'], logger=logger):
            logger.error('{func:s}: observation types not in same order, please correct. Program quits.'.format(func=cFuncName))
            sys.exit(amc.E_FAILURE)

        # create the merged OBS file
        tmp_obsf = combine_rnx_obs(lst_obsf=dRnx['p3rs2']['obs'], ext='O', logger=logger)

        # correct the faulty headers & rename to ::RX3:: format
        dRnx['rnx']['obs3f'] = convert_obsrnx3(gfzrnx=dRnx['bin']['gfzrnx'],
                                               rnxf_tmp=tmp_obsf,
                                               cruxf=crux_file,
                                               yyyy=dRnx['cli']['year'],
                                               doy=dRnx['cli']['doy'],
                                               start_ep=dRnx['cli']['start_ep'],
                                               end_ep=dRnx['cli']['end_ep'],
                                               rnxdir=dRnx['dirs']['yydoy'],
                                               logger=logger)
    else:
        logger.info('{func:s}: no RINEX observation files found - program exits'.format(func=cFuncName))
        sys.exit(amc.E_NORINEXOBS)

    # combine the RINEX quaterly navigation files
    if len(dRnx['p3rs2']['nav']) > 0:
        # create the merged NAV file
        tmp_navf = combine_rnx_obs(lst_obsf=dRnx['p3rs2']['nav'], ext='M', logger=logger)

        # correct the faulty headers & rename to ::RX3:: format
        dRnx['rnx']['nav3f'] = convert_navrnx3(gfzrnx=dRnx['bin']['gfzrnx'], rnxf_tmp=tmp_navf, cruxf=crux_file, rnxdir=dRnx['dirs']['yydoy'], logger=logger)

        # dRnx['rnx']['nav'] = os.path.basename(navf_cmp)
    else:
        logger.info('{func:s}: no RINEX navigation files found - program exits'.format(func=cFuncName))
        sys.exit(amc.E_NORINEXNAV)

    # report to the user
    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dRnx, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # remove temporary files
    try:
        if tmp_obsf:
            os.remove(tmp_obsf)
        if tmp_navf:
            os.remove(tmp_navf)
        if crux_file:
            os.remove(crux_file)
    except OSError:
        pass

    # copy temp log file to the YYDOY directory
    copyfile(log_name, os.path.join(dRnx['dirs']['yydoy'], '{scrname:s}.log'.format(scrname=os.path.splitext(os.path.basename(__file__))[0])))
    os.remove(log_name)

    return dRnx['dirs']['yydoy'], dRnx['rnx']['obs3f'], dRnx['rnx']['nav3f']


if __name__ == "__main__":  # Only run if this file is called directly
    rnxdir, obs3f, nav3f = main_combine_rnx15(sys.argv[1:])

    print('Created {obsf:s} and {navf:s}'.format(obsf=obs3f, navf=nav3f ))
