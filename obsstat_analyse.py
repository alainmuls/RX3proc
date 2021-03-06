#!/usr/bin/env python

import sys
import os
import argparse
from termcolor import colored
import logging
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from shutil import copyfile
import pickle

from gfzrnx import gfzrnx_constants as gfzc
from ampyutils import gnss_cmd_opts as gco

from ampyutils import am_config as amc
from ampyutils import amutils
from tle import tle_visibility, tleobs_plot
from ltx import ltx_rnxobs_reporting
from cvsdb import cvsdb_ops

__author__ = 'amuls'


def treatCmdOpts(argv):
    """
    Treats the command line options

    :param argv: the options
    :type argv: list of string
    """
    baseName = os.path.basename(__file__)
    amc.cBaseName = colored(baseName, 'yellow')

    helpTxt = amc.cBaseName + ' analyses observation statistics file for selected GNSSs'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('--obsstat', help='observation statistics file', type=str, required=True)

    parser.add_argument('--freqs', help='select frequencies to use (out of {freqs:s}, default {freq:s})'.format(freqs='|'.join(gfzc.lst_freqs), freq=colored(gfzc.lst_freqs[0], 'green')), default=gfzc.lst_freqs[0], type=str, required=False, action=gco.freqtype_action, nargs='+')

    parser.add_argument('--cutoff', help='cutoff angle in degrees (default {mask:s})'.format(mask=colored('0', 'green')), default=0, type=int, required=False, action=gco.cutoff_action)

    parser.add_argument('--dbcvs', help='Add information to CVS database (default {cvsdb:s})'.format(cvsdb=colored(gco.CVSDB_OBSTLE, 'green')), required=False, type=str, default=gco.CVSDB_OBSTLE)

    parser.add_argument('--plot', help='displays interactive plots (default False)', action='store_true', required=False, default=False)

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv[1:])

    # return arguments
    return args.obsstat, args.freqs, args.cutoff, args.dbcvs, args.plot, args.logging


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
        sys.exit(amc.E_CREATE_DIR_ERROR)

    # check for accessibility of CVS database
    if not amutils.path_writable(os.path.dirname(dStat['cli']['cvsdb'])):
        if logger is not None:
            logger.error('{func:s}: cannot write to directory {dir:s} failed'.format(dir=colored(os.path.dirname(dStat['cli']['cvsdb']), 'red'), func=cFuncName))
        sys.exit(amc.E_PATH_NOT_WRITABLE)

    # check whether selected freq is available
    for clifreq in dStat['cli']['freqs']:
        if clifreq not in dStat['info']['freqs']:
            if logger is not None:
                logger.error('{func:s}: selected frequency {clifreq:s} is not available'.format(clifreq=colored(clifreq, 'red'), func=cFuncName))
            sys.exit(amc.E_NOAVAIL_FREQ)

    # extract YY and DOY from filename
    dStat['time']['YYYY'] = int(dStat['obsstatf'][12:16])
    dStat['time']['DOY'] = int(dStat['obsstatf'][16:19])
    # converting to date
    dStat['time']['date'] = datetime.strptime('{year:04d}-{doy:03d}'.format(year=dStat['time']['YYYY'], doy=dStat['time']['DOY']), "%Y-%j")


def read_obsstat(logger: logging.Logger = None) -> pd.DataFrame:
    """
    read_obsstat reads the SNR for the selected frequencies into a dataframe
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    dfTmp = pd.read_csv(dStat['obsstatf'], delim_whitespace=True)
    dfTmp.rename(columns={'TYP': 'PRN'}, inplace=True)
    if logger is not None:
        amutils.logHeadTailDataFrame(df=dfTmp, dfName='dfTmp', callerName=cFuncName, logger=logger)

    # select the SNR colmuns for the selected frequencies
    col_names = dfTmp.columns.tolist()
    cols2keep = col_names[:4]
    for freq in dStat['cli']['freqs']:
        cols2keep += [col for col in col_names[4:] if col.startswith('S{freq:s}'.format(freq=freq))]

    return dfTmp[cols2keep]


def cvsdb_update_obstle(obsstatf: str, dfObsTle: pd.DataFrame, dTime: dict, cvsdb: str, logger: logging.Logger = None):
    """cvdb: str
    cvsdb_update_obstle updates the observation vs TLE statistics
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # create the ID part for adding to CVSDB
    obshdr_data = ['{YYYY:04d}'.format(YYYY=dTime['YYYY']),
                   '{DOY:03d}'.format(DOY=dTime['DOY']),
                   '{rx:s}'.format(rx=dfObsTle.columns[1]),
                   '{gnss:s}'.format(gnss=dfObsTle.columns[2]),
                   "OBS"]
    tlehdr_data = ['{YYYY:04d}'.format(YYYY=dTime['YYYY']),
                   '{DOY:03d}'.format(DOY=dTime['DOY']),
                   '{rx:s}'.format(rx=dfObsTle.columns[1]),
                   '{gnss:s}'.format(gnss=dfObsTle.columns[2]),
                   "TLE"]
    # print('hdr_data = {!s}'.format(hdr_data))

    # iterate over all examined obstypes
    for obst in dfObsTle.columns[4:-1]:
        # hdr_data += ',{obst:s}'.format(obst=obst)

        obs_data = [np.NaN] * 37  # contains CVS fields of observation counts per PRN, field 0 is sum of all SVs, field xx is for PRNxx
        tleobs_data = [np.NaN] * 37   # percentage of observation count wrt TLE per PRN

        # note which observable is on this line
        obs_data[0] = '{:s}'.format(obst)
        tleobs_data[0] = '{:s}'.format(obst)

        for SVPRN in dfObsTle.PRN:
            prn = int(SVPRN[1:])

            # the data for the absolute values
            obs_data[prn] = dfObsTle.loc[dfObsTle.PRN == SVPRN][obst] .values[0]

            # the data for the relative to TLE values
            tleobs_data[prn] = float('{:.1f}'.format(obs_data[prn] / dfObsTle.loc[dfObsTle.PRN == SVPRN][dfObsTle.columns[-1]] .values[0] * 100))

        # print(hdr_data + obs_data)
        # print(hdr_data + tleobs_data)

        # update the cvsdb with absolute and relative values
        cvsdb_ops.cvsdb_update_line(cvsdb_name=cvsdb, line_data=obshdr_data + obs_data, id_fields=len(obshdr_data) + 1, logger=logger)
        cvsdb_ops.cvsdb_update_line(cvsdb_name=cvsdb, line_data=tlehdr_data + tleobs_data, id_fields=len(tlehdr_data) + 1, logger=logger)

    pass


def tle_cvs(dfTleVis: pd.DataFrame, cvs_name: str, logger: logging.Logger = None):
    """
    tle_cvs converts the list of datetime.time to list of strings and stores these in a CVS file
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # convert the dfTle index to a column of PRNs
    dfTleVis.reset_index(inplace=True)
    dfTleVis = dfTleVis.rename(columns={'index': 'PRN'})

    # create an empty dataframe with the same columns
    dfCvs = pd.DataFrame(columns=dfTleVis.columns.tolist())

    # get the PRN and tle_arc_count numbers into dfCvs
    dfCvs[['PRN', 'tle_arc_count']] = dfTleVis[['PRN', 'tle_arc_count']]

    if logger is not None:
        amutils.logHeadTailDataFrame(df=dfCvs, dfName='dfCvs', callerName=cFuncName, logger=logger)


def main_rnx_obsstat(argv):
    """
    main_rnx_obsstat analyses the created OBSSTAT files and compares with TLE data
    """

    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    global dStat
    dStat = {}
    dStat['cli'] = {}
    dStat['time'] = {}
    dStat['ltx'] = {}
    dStat['plots'] = {}
    dStat['info'] = {}

    dStat['cli']['obsstatf'], dStat['cli']['freqs'], dStat['cli']['mask'], dStat['cli']['cvsdb'], show_plot, logLevels = treatCmdOpts(argv)

    # detect used GNSS from the obsstatf filename
    dStat['info']['gnss'] = os.path.splitext(os.path.basename(dStat['cli']['obsstatf']))[0][-1]
    dStat['info']['gnss_name'] = gfzc.dict_GNSSs[dStat['info']['gnss']]
    # print('{} => {}'.format(dStat['gnss'], dStat['gnss_name']))

    # create logging for better debugging
    logger, log_name = amc.createLoggers(baseName=os.path.basename(__file__), logLevels=logLevels)

    # read the observation header info from the Pickle file
    dStat['obshdr'] = '{obsf:s}.obshdr'.format(obsf=os.path.splitext(dStat['cli']['obsstatf'])[0][:-2])
    try:
        with open(dStat['obshdr'], 'rb') as handle:
            dStat['hdr'] = pickle.load(handle)
        dStat['marker'] = dStat['hdr']['file']['site']
        # get interval,  start and end times of observation
        dStat['time']['interval'] = float(dStat['hdr']['file']['interval'])
        dStat['time']['first'] = datetime.strptime(dStat['hdr']['data']['epoch']['first'].split('.')[0], '%Y %m %d %H %M %S')
        dStat['time']['last'] = datetime.strptime(dStat['hdr']['data']['epoch']['last'].split('.')[0], '%Y %m %d %H %M %S')
        # get frequencies in the observation file
        dStat['info']['freqs'] = dStat['hdr']['file']['sysfrq'][dStat['info']['gnss']]
    except IOError as e:
        logger.error('{func:s}: error {err!s} reading header file {hdrf:s}'.format(hdrf=colored(dStat['obshdr'], 'red'), err=e, func=cFuncName))
        sys.exit(amc.E_FILE_NOT_EXIST)

    # verify input
    check_arguments(logger=logger)

    # sys.file_exists(9)

    logger.info('{func:s}: Imported header information from {hdrf:s}\n{json!s}'.format(func=cFuncName, json=json.dumps(dStat['hdr'], sort_keys=False, indent=4, default=amutils.json_convertor), hdrf=colored(dStat['obshdr'], 'blue')))

    # dStat['time']['first'] = datetime.strptime(dStat['hdr']['data']['epoch']['first'].split('.')[0], '%Y %m %d %H %M %S')
    # dStat['time']['last'] = datetime.strptime(dStat['hdr']['data']['epoch']['last'].split('.')[0], '%Y %m %d %H %M %S')
    # print(dStat['time']['first'])
    # print(type(dStat['time']['first']))

    # read obsstat into a dataframe and select the SNR for the selected frequencies
    dfObsStat = read_obsstat(logger=logger)
    amutils.logHeadTailDataFrame(df=dfObsStat, dfName='dfObsStat', callerName=cFuncName, logger=logger)

    # get the observation time spans based on TLE values
    dfTLE, dfTLEVis = tle_visibility.PRNs_visibility(prn_lst=dfObsStat.PRN.unique(),
                                                     DTG_start=dStat['time']['first'],
                                                     DTG_end=dStat['time']['last'],
                                                     interval=dStat['time']['interval'],
                                                     cutoff=dStat['cli']['mask'],
                                                     logger=logger)
    amutils.logHeadTailDataFrame(df=dfTLE, dfName='dfTLE', callerName=cFuncName, logger=logger)
    amutils.logHeadTailDataFrame(df=dfTLEVis, dfName='dfTLEVis', callerName=cFuncName, logger=logger)

    # combine the observation count and TLE count per PRN
    dfTLEtmp = pd.DataFrame(columns=['PRN', 'TLE_count'])  # , dtype={'PRN':'object','TLE_count':'int'})
    dfTLEtmp.PRN = dfTLEVis.index  # convert the TLE index (which are the PRNs) to a column
    amutils.logHeadTailDataFrame(df=dfTLEtmp, dfName='dfTLEtmp', callerName=cFuncName, logger=logger)

    # add colmun which contains the total number of observations over all arcs
    for i, (prn, tle_prn) in enumerate(dfTLEVis.iterrows()):
        dfTLEtmp.iloc[i].TLE_count = sum(tle_prn.tle_arc_count)

    print('dfTLEtmp = {}'.format(dfTLEtmp))
    # combine TLE and actual observations (only SNR column used since values for all other obst are the same)
    dfObsTLE = pd.merge(dfObsStat, dfTLEtmp, on='PRN')
    amutils.logHeadTailDataFrame(df=dfObsTLE,
                                 dfName='dfObsTLE',
                                 callerName=cFuncName,
                                 logger=logger)
    # store the observation / TLE info  in CVS file
    obsstat_name = '{basen:s}.obstle'.format(basen=os.path.basename(dStat['obsstatf']).split('.')[0])
    dfObsTLE.to_csv(obsstat_name, index=False)

    # store the information in cvsdb
    cvsdb_ops.cvsdb_open(cvsdb_name=dStat['cli']['cvsdb'], logger=logger)
    cvsdb_update_obstle(obsstatf=dStat['obsstatf'], dfObsTle=dfObsTLE, dTime=dStat['time'], cvsdb=dStat['cli']['cvsdb'], logger=logger)
    cvsdb_ops.cvsdb_sort(cvsdb_name=dStat['cli']['cvsdb'], logger=logger)

    # plot the Observation and TLE observation count
    dStat['plots']['obs_count'] = tleobs_plot.obstle_plot_obscount(marker=dStat['marker'],
                                                                   obsf=dStat['obsstatf'],
                                                                   dfObsTle=dfObsTLE,
                                                                   dTime=dStat['time'],
                                                                   show_plot=show_plot,
                                                                   logger=logger)
    dStat['plots']['relative'] = tleobs_plot.obstle_plot_relative(marker=dStat['marker'],
                                                                  obsf=dStat['obsstatf'],
                                                                  dfObsTle=dfObsTLE,
                                                                  dTime=dStat['time'],
                                                                  show_plot=show_plot,
                                                                  logger=logger)

    # create a section for latex reporting
    sec_obsstat = ltx_rnxobs_reporting.ltx_obsstat_analyse(dInfo=dStat['info'],
                                                           obsstatf=dStat['obsstatf'],
                                                           dfObsTle=dfObsTLE,
                                                           plots=dStat['plots'],
                                                           script_name=os.path.basename(__file__))
    dStat['ltx']['obsstat'] = os.path.join(dStat['ltx']['path'],
                                           '{marker:s}_02_{gnss:s}_obs_stat'.format(marker=dStat['obsstatf'][:9],
                                                                                    gnss=dStat['info']['gnss']))
    sec_obsstat.generate_tex(dStat['ltx']['obsstat'])

    # store the observation info from TLE in CVS file
    tle_name = '{basen:s}.tle'.format(basen=os.path.basename(dStat['obsstatf']).split('.')[0])
    tle_cvs(dfTleVis=dfTLEVis, cvs_name=tle_name, logger=logger)
    # dfTLE.to_csv(tle_name, index=True, date_format='%H:%M:%S')

    # dGFZ['ltx']['script'] = os.path.join(dGFZ['ltx']['path'], 'script_info')
    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dStat, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # report to the user

    # store the json structure
    jsonName = os.path.join(dStat['dir'], '{scrname:s}.json'.format(scrname=os.path.splitext(os.path.basename(__file__))[0]))
    with open(jsonName, 'w+') as f:
        json.dump(dStat, f, ensure_ascii=False, indent=4, default=amutils.json_convertor)

    # clean up
    copyfile(log_name, os.path.join(dStat['dir'], '{scrname:s}.log'.format(scrname=os.path.basename(__file__).replace('.', '_'))))
    os.remove(log_name)


if __name__ == "__main__":  # Only run if this file is called directly
    main_rnx_obsstat(sys.argv)
