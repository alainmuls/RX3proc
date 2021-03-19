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
import numpy as np
from shutil import copyfile
from typing import Tuple
import pickle

from gfzrnx import gfzrnx_constants as gfzc
from ampyutils import gnss_cmd_opts as gco

from ampyutils import am_config as amc
from ampyutils import amutils
from tle import tle_visibility, tleobs_plot
from ltx import ltx_rnxobs_reporting


__author__ = 'amuls'


def treatCmdOpts(argv):
    """
    Treats the command line options

    :param argv: the options
    :type argv: list of string
    """
    baseName = os.path.basename(__file__)
    amc.cBaseName = colored(baseName, 'yellow')

    helpTxt = amc.cBaseName + ' analyses observation tabular file for selected GNSSs'

    # create the parser for command line arguments
    parser = argparse.ArgumentParser(description=helpTxt)

    parser.add_argument('--obstab', help='observation tabular file', type=str, required=True)

    parser.add_argument('--prns', help='list of PRNs to examine (default {:s} (if PRN is 00 than all PRNs for GNSS used)'.format(colored('E00', 'green')), type=str, required=False, default=['E00', 'G00'], action=gco.prn_list_action, nargs='+')

    parser.add_argument('--freqs', help='select frequencies to use (out of {freqs:s}, default {freq:s})'.format(freqs='|'.join(gfzc.lst_freqs), freq=colored(gfzc.lst_freqs[0], 'green')), default=gfzc.lst_freqs[0], type=str, required=False, action=gco.freqtype_action, nargs='+')
    parser.add_argument('--obstypes', help='select observation types(s) to use (out of {osbtypes:s}, default {osbtype:s})'.format(osbtypes='|'.join(gfzc.lst_obstypes), osbtype=colored(gfzc.lst_obstypes[0], 'green')), default=gfzc.lst_obstypes[0], type=str, required=False, action=gco.obstype_action, nargs='+')

    parser.add_argument('--snr_th', help='threshold for detecting variation in SNR levels (default {snrtr:s})'.format(snrtr=colored('2', 'green')), type=float, required=False, default=2, action=gco.snrth_action)

    parser.add_argument('--interval', help='measurement interval in seconds (default {interv:s}s)'.format(interv=colored('1', 'green')), required=False, default=1., type=float, action=gco.interval_action)

    parser.add_argument('--cutoff', help='cutoff angle in degrees (default {mask:s})'.format(mask=colored('0', 'green')), default=0, type=int, required=False, action=gco.cutoff_action)

    parser.add_argument('--plot', help='displays interactive plots (default False)', action='store_true', required=False, default=False)

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'.format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')), nargs=2, required=False, default=gco.lst_logging_choices[3:5], action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv[1:])

    # return arguments
    return args.obstab, args.prns, args.freqs, args.obstypes, args.snr_th, args.cutoff, args.plot, args.logging


def check_arguments(logger: logging.Logger = None):
    """
    check arhuments and change working directory
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # check & change working dir
    dTab['dir'] = os.path.dirname(Path(dTab['cli']['obstabf']).resolve())
    dTab['obstabf'] = os.path.basename(dTab['cli']['obstabf'])

    if not amutils.changeDir(dTab['dir']):
        if logger is not None:
            logger.error('{func:s}: changing to directory {dir:s} failed'.format(dir=dTab['dir'], func=cFuncName))
        sys.exit(amc.E_DIR_NOT_EXIST)

    # check accessibilty of observation statistics file
    if not amutils.file_exists(fname=dTab['obstabf'], logger=logger):
        if logger is not None:
            logger.error('{func:s}: observation file {file:s} not accessible'.format(file=dTab['obstabf'], func=cFuncName))
        sys.exit(amc.E_FILE_NOT_EXIST)

    # create dir for storing the latex sections
    dTab['ltx']['path'] = os.path.join(dTab['dir'], 'ltx')
    if not amutils.mkdir_p(dTab['ltx']['path']):
        if logger is not None:
            logger.error('{func:s}: cannot create directory {dir:s} failed'.format(dir=dTab['ltx']['path'], func=cFuncName))
        sys.exit(amc.E_FAILURE)

    # extract YY and DOY from filename
    dTab['time']['YYYY'] = int(dTab['obstabf'][12:16])
    dTab['time']['DOY'] = int(dTab['obstabf'][16:19])
    # converting to date
    dTab['time']['date'] = datetime.strptime('{year:04d}-{doy:03d}'.format(year=dTab['time']['YYYY'], doy=dTab['time']['DOY']), "%Y-%j")

    # if 'E00' or 'G00' is selected, the list of PRNs to examine is all PRNs for that GNSS
    use_all_prns = False
    for gnss in gfzc.lst_GNSSs:
        for prn in dTab['cli']['lst_prns']:
            if prn == gfzc.dict_GNSS_PRNs[gnss][0]:
                use_all_prns = True
                dTab['lst_prns'] = gfzc.dict_GNSS_PRNs[gnss]

    if not use_all_prns:
        dTab['lst_prns'] = dTab['cli']['lst_prns']


def read_obstab(obstabf: str, lst_PRNs: list, dCli: dict, logger: logging.Logger = None) -> Tuple[list, pd.DataFrame]:
    """
    read_obstab reads the SNR for the selected frequencies into a dataframe
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # determine what the columnheaders will be
    hdr_count = -1
    hdr_columns = []
    with open(obstabf) as fin:
        for line in fin:
            # print(line.strip())
            hdr_count += 1
            if line.strip().startswith('OBS'):
                break
            else:
                if line.strip() != '#HD,G,DATE,TIME,PRN':
                    hdr_line = line.strip()

    # split up on comma into a list
    hdr_columns = hdr_line.split(',')
    # print('hdr_columns = {!s}'.format(hdr_columns))
    # print('hdr_columns[2:4] = {!s}'.format(hdr_columns[2:4]))
    # print('hdr_count = {!s}'.format(hdr_count))

    # keep the header columns selected by --freqs and --obstypes options
    obstypes = hdr_columns[2:5]
    obsfreqs = []
    for obst in dCli['obs_types']:
        for freq in dCli['freqs']:
            obsfreq = '{obst:s}{freq:s}'.format(obst=obst, freq=freq)
            obsfreqs.append([obstid for obstid in hdr_columns[2:] if obstid.startswith(obsfreq)][0])
    obstypes += obsfreqs

    logger.info('{func:s}: loading from {tab:s}: {cols:s}'.format(tab=obstabf, cols=colored(', '.join(obstypes), 'green'), func=cFuncName))

    dfTmp = pd.read_csv(obstabf, delimiter=',', skiprows=hdr_count, names=hdr_columns, header=None, parse_dates=[hdr_columns[2:4]], usecols=obstypes)

    # check whether the selected PRNs are in the dataframe, else remove this PRN from
    # print('lst_PRNs = {}'.format(lst_PRNs))
    lst_ObsPRNs = sorted(dfTmp.PRN.unique())
    # print('lst_obsPRNs = {}'.format(lst_ObsPRNs))

    lst_CommonPRNS = [prn for prn in lst_ObsPRNs if prn in lst_PRNs]
    # print('lst_CommonPRNS = {}'.format(lst_CommonPRNS))

    if len(lst_CommonPRNS) == 0:
        logger.error('{func:s}: selected list of PRNs ({lstprns:s}) not observed. program exits'.format(lstprns=colored(', '.join(lst_PRNs), 'red'), func=cFuncName))
        sys.exit(amc.E_PRN_NOT_IN_DATA)
    else:
        logger.info('{func:s}: following PRNs examined: {prns:s}'.format(prns=', '.join(lst_CommonPRNS), func=cFuncName))

    # apply mask to dataframe to select PRNs in the list
    # print('lst_PRNs = {}'.format(lst_PRNs))
    # print("dfTmp['PRN'].isin(lst_PRNs) = {}".format(dfTmp['PRN'].isin(lst_PRNs)))
    dfTmp = dfTmp[dfTmp['PRN'].isin(lst_CommonPRNS)]

    # # XXX TEST BEGIN for testing remove some lines for SV E02
    # indices = dfTmp[dfTmp['PRN'] == 'E02'].index
    # print('dropping indices = {!s}'.format(indices[5:120]))
    # dfTmp.drop(indices[5:120], inplace=True)
    # # END XXX TEST

    if logger is not None:
        amutils.logHeadTailDataFrame(df=dfTmp, dfName='dfTmp', callerName=cFuncName, logger=logger)

    return lst_CommonPRNS, obsfreqs, dfTmp


def analyse_obsprn(dfObsPrns: pd.DataFrame, prn_list: list, obsfreqs: list, snrth: float, interval: int, logger: logging.Logger):
    """
    analyse_obsprn analyses the observations for the gicen PRNs and detemines a loss in SNR if asked.
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    print('prn_list = {}'.format(prn_list))
    # idx_time_gaps = {}
    # idx_snr_posjumps = {}
    # idx_snr_negjumps = {}
    for prn in prn_list:
        # idx_time_gaps[prn] = {}
        # idx_snr_posjumps[prn] = {}
        # idx_snr_negjumps[prn] = {}

        for obsfreq in obsfreqs:
            print('obsfreq = {}'.format(obsfreq))
            # select only the elements for this prn
            dfObsFreqPrn = dfObsPrns[dfObsPrns.PRN == prn][['DATE_TIME', 'PRN', obsfreq]].dropna()

            # calculate the time difference between successive entries
            dfObsFreqPrn.insert(loc=dfObsFreqPrn.columns.get_loc('DATE_TIME') + 1, column='dt', value=(dfObsFreqPrn['DATE_TIME'] - dfObsFreqPrn['DATE_TIME'].shift(1)).astype('timedelta64[s]'))
            # add column which is difference between current and previous obst
            dfObsFreqPrn.insert(loc=dfObsFreqPrn.columns.get_loc(obsfreq) + 1, column='d{obsfreq:s}'.format(obsfreq=obsfreq), value=(dfObsFreqPrn[obsfreq] - dfObsFreqPrn[obsfreq].shift(1)).astype(float))

            # find the exponential moving average
            # dfObsFreqPrn['EMA05'] = dfObsFreqPrn[obsfreq].ewm(halflife='5 seconds', adjust=False, times=dfObsFreqPrn['DATE_TIME']).mean()
            # dfObsFreqPrn['WMA05'] = dfObsFreqPrn[obsfreq].rolling(5, min_periods=1).mean()

            # find the gaps for this PRN and OBST
            idx_time_gaps = dfObsFreqPrn.index[dfObsFreqPrn.dt != interval].tolist()
            # convert to positional indices
            posidx_time_gaps = [dfObsFreqPrn.index.get_loc(gap) for gap in idx_time_gaps]
            print('posidx_time_gaps = {}'.format(posidx_time_gaps))

            # for idx_gap in idx_time_gaps[1:]:
            #     pos_idx_gap = dfObsFreqPrn.index.get_loc(idx_gap)
            #     print(dfObsFreqPrn.iloc[pos_idx_gap - 2 * span:pos_idx_gap + int(span / 2)])

            # find the SNR differences that are higher than snrth (SNR threshold)
            if obsfreq[0] == 'S':
                idx_snr_posjumps = dfObsFreqPrn.index[dfObsFreqPrn['d{obsfreq:s}'.format(obsfreq=obsfreq)] > snrth].tolist()
                # convert to poisionla indices
                posidx_snr_posjumps = [dfObsFreqPrn.index.get_loc(jump) for jump in idx_snr_posjumps]
                print('posidx_snr_posjumps = {} #{}'.format(posidx_snr_posjumps, len(posidx_snr_posjumps)))

                idx_snr_negjumps = dfObsFreqPrn.index[dfObsFreqPrn['d{obsfreq:s}'.format(obsfreq=obsfreq)] < -snrth].tolist()
                # convert to poisionla indices
                posidx_snr_negjumps = [dfObsFreqPrn.index.get_loc(jump) for jump in idx_snr_negjumps]
                print('posidx_snr_negjumps = {} #{}'.format(posidx_snr_negjumps, len(posidx_snr_negjumps)))

            # else:
            #     idx_snr_posjumps[prn][obsfreq] = []
            #     idx_snr_negjumps[prn][obsfreq] = []

            # info user
            amutils.logHeadTailDataFrame(df=dfObsFreqPrn, dfName='dfObsFreqPrn', callerName=cFuncName, logger=logger)

            # plot for each PRN and obstfreq
            tleobs_plot.plot_prnfreq(obsstatf=dTab['cli']['obstabf'], dfPrnObst=dfObsFreqPrn, posidx_gaps=posidx_time_gaps, snrth=snrth, dTime=dTab['time'], show_plot=True, logger=logger)

            posidx = posidx_time_gaps[2]
            print(posidx)
            print('posidx= {}'.format(dfObsFreqPrn.iloc[posidx]))

            # posidx = posidx_time_gaps[2] - 1
            # print(posidx)
            # print('posidx= {}'.format(dfObsFreqPrn.iloc[posidx]))

            beginTime = dfObsFreqPrn.DATE_TIME.iloc[posidx - 1]
            endTime = dfObsFreqPrn.DATE_TIME.iloc[posidx]
            print('time gap = {} => {} = {}'.format(beginTime, endTime, (endTime - beginTime).total_seconds()))

    sys.exit(77)


def obstab_analyse(argv):
    """
    obstab_analyse analyses the created OBSTAB files and compares with TLE data.
    """

    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    global dTab
    dTab = {}
    dTab['cli'] = {}
    dTab['time'] = {}
    dTab['ltx'] = {}
    dTab['plots'] = {}

    dTab['cli']['obstabf'], dTab['cli']['lst_prns'], dTab['cli']['freqs'], dTab['cli']['obs_types'], dTab['cli']['snrth'], dTab['cli']['mask'], show_plot, logLevels = treatCmdOpts(argv)

    # create logging for better debugging
    logger, log_name = amc.createLoggers(baseName=os.path.basename(__file__), logLevels=logLevels)

    # verify input
    check_arguments(logger=logger)

    # read the observation header info from the Pickle file
    dTab['obshdr'] = '{obsf:s}.obshdr'.format(obsf=os.path.splitext(dTab['cli']['obstabf'])[0][:-2])
    with open(dTab['obshdr'], 'rb') as handle:
        dTab['hdr'] = pickle.load(handle)
    dTab['marker'] = dTab['hdr']['file']['site']
    dTab['time']['interval'] = float(dTab['hdr']['file']['interval'])

    logger.info('{func:s}: Imported header information from {hdrf:s}\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab['hdr'], sort_keys=False, indent=4, default=amutils.json_convertor), hdrf=colored(dTab['obshdr'], 'blue')))

    # determine start and end times of observation
    DTGobs_start = datetime.strptime(dTab['hdr']['data']['epoch']['first'].split('.')[0], '%Y %m %d %H %M %S')
    DTGobs_end = datetime.strptime(dTab['hdr']['data']['epoch']['last'].split('.')[0], '%Y %m %d %H %M %S')
    print(DTGobs_start)
    print(DTGobs_end)

    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # read obsstat into a dataframe and select the SNR for the selected frequencies
    dTab['lst_CmnPRNs'], dTab['obsfreqs'], dfObsTab = read_obstab(obstabf=dTab['obstabf'], lst_PRNs=dTab['lst_prns'], dCli=dTab['cli'], logger=logger)

    # get the observation time spans based on TLE values
    # dfTLE = tle_visibility.PRNs_visibility(prn_lst=dTab['lst_CmnPRNs'], cur_date=dTab['time']['date'], interval=dTab['time']['interval'], cutoff=dTab['cli']['mask'], logger=logger)
    dfTLE = tle_visibility.PRNs_visibility(prn_lst=dfObsTab.PRN.unique(), DTG_start=DTGobs_start, DTG_end=DTGobs_end, interval=dTab['time']['interval'], cutoff=dTab['cli']['mask'], logger=logger)

    amutils.logHeadTailDataFrame(df=dfObsTab, dfName='dfObsTab', callerName=cFuncName, logger=logger)
    amutils.logHeadTailDataFrame(df=dfTLE, dfName='dfTLE', callerName=cFuncName, logger=logger)

    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # perform analysis of the observations done
    analyse_obsprn(dfObsPrns=dfObsTab, prn_list=dTab['lst_CmnPRNs'], obsfreqs=dTab['obsfreqs'], snrth=dTab['cli']['snrth'], interval=dTab['time']['interval'], logger=logger)
    # tleobs_plot.tle_plot_arcs()
    sys.exit(55)

    # plot the observables for all or selected PRNs
    tleobs_plot.tle_plot_arcs(obsstatf=dTab['obstabf'], lst_PRNs=dTab['lst_CmnPRNs'], dfTabObs=dfObsTab, dfTle=dfTLE, dTime=dTab['time'], logger=logger, show_plot=show_plot)

    # report to the user
    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # store the json structure
    jsonName = os.path.join(dTab['dir'], '{scrname:s}.json'.format(scrname=os.path.splitext(os.path.basename(__file__))[0]))
    with open(jsonName, 'w+') as f:
        json.dump(dTab, f, ensure_ascii=False, indent=4, default=amutils.json_convertor)

    # clean up
    copyfile(log_name, os.path.join(dTab['dir'], '{scrname:s}.log'.format(scrname=os.path.basename(__file__).replace('.', '_'))))
    os.remove(log_name)


if __name__ == "__main__":  # Only run if this file is called directly
    obstab_analyse(sys.argv)
