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
from shutil import copyfile
from typing import Tuple
import pickle
import numpy as np

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

    parser.add_argument('--prns', help='list of PRNs to examine (default {:s} (if PRN is 00 than all PRNs for GNSS used)'
                                       .format(colored('E00', 'green')),
                        type=str,
                        required=False,
                        default=['E00', 'G00'],
                        action=gco.prn_list_action,
                        nargs='+')

    parser.add_argument('--freqs', help='select frequencies to use (out of {freqs:s}, default {freq:s})'
                                        .format(freqs='|'.join(gfzc.lst_freqs), freq=colored(gfzc.lst_freqs[0], 'green')),
                        default=gfzc.lst_freqs[0],
                        type=str,
                        required=False,
                        action=gco.freqtype_action,
                        nargs='+')

    parser.add_argument('--obstypes', help='select observation types(s) to use (out of {osbtypes:s}, default {osbtype:s})'
                                           .format(osbtypes='|'.join(gfzc.lst_obstypes),
                        osbtype=colored(gfzc.lst_obstypes[0], 'green')),
                                           default=gfzc.lst_obstypes[0],
                        type=str,
                        required=False,
                        action=gco.obstype_action,
                        nargs='+')

    parser.add_argument('--snr_th', help='threshold for detecting variation in SNR levels (default {snrtr:s})'
                                         .format(snrtr=colored('2', 'green')),
                        type=float,
                        required=False,
                        default=2,
                        action=gco.snrth_action)

    parser.add_argument('--cutoff', help='cutoff angle in degrees (default {mask:s})'.format(mask=colored('0', 'green')),
                        default=0,
                        type=int,
                        required=False,
                        action=gco.cutoff_action)

    parser.add_argument('--jamsc', help='CSV file containing jamming scenario',
                        type=str,
                        required=False,
                        default=None)

    parser.add_argument('--plot', help='displays interactive plots (default False)',
                        action='store_true',
                        required=False,
                        default=False)

    parser.add_argument('--logging', help='specify logging level console/file (two of {choices:s}, default {choice:s})'
                                          .format(choices='|'.join(gco.lst_logging_choices), choice=colored(' '.join(gco.lst_logging_choices[3:5]), 'green')),
                        nargs=2,
                        required=False,
                        default=gco.lst_logging_choices[3:5],
                        action=gco.logging_action)

    # drop argv[0]
    args = parser.parse_args(argv[1:])

    # return arguments
    return args.obstab, args.freqs, args.prns, args.obstypes, args.snr_th, args.cutoff, args.jamsc, args.plot, args.logging


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

    # check whether selected freq is available
    for clifreq in dTab['cli']['freqs']:
        if clifreq not in dTab['info']['freqs']:
            if logger is not None:
                logger.error('{func:s}: selected frequency {clifreq:s} is not available'.format(clifreq=colored(clifreq, 'red'), func=cFuncName))
            sys.exit(amc.E_NOAVAIL_FREQ)

    # if 'E00' or 'G00' is selected, the list of PRNs to examine is all PRNs for that GNSS
    use_all_prns = False
    for gnss in gfzc.lst_GNSSs:
        for prn in dTab['cli']['lst_prns']:
            if prn == gfzc.dict_GNSS_PRNs[gnss][0]:
                use_all_prns = True
                dTab['lst_prns'] = gfzc.dict_GNSS_PRNs[gnss]

    if not use_all_prns:
        dTab['lst_prns'] = dTab['cli']['lst_prns']

    # check presence of possible jamming scenario
    if dTab['cli']['jamsc'] is not None:
        if not amutils.file_exists(fname=dTab['cli']['jamsc'], logger=logger):
            if logger is not None:
                logger.error('{func:s}: jamming scenario {file:s} not accessible'.format(file=dTab['cli']['jamsc'], func=cFuncName))
            sys.exit(amc.E_FILE_NOT_EXIST)


def read_obstab(obstabf: str,
                lst_PRNs: list,
                dCli: dict,
                logger: logging.Logger = None) -> Tuple[list, list, list, pd.DataFrame]:
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
    for freq in dTab['cli']['freqs']:
        for obst in dCli['obs_types']:
            obsfreq = '{obst:s}{freq:s}'.format(obst=obst, freq=freq)
            obsfreqs.append([obstid for obstid in hdr_columns[2:] if obstid.startswith(obsfreq)][0])
    obstypes += obsfreqs

    # created the possible navigation signals we have
    nav_signals = list(set([obsfreq[1:] for obsfreq in obsfreqs]))
    # print(nav_signals)

    logger.info('{func:s}: loading from {tab:s}: {cols:s}'.format(tab=obstabf, cols=colored(', '.join(obstypes), 'green'), func=cFuncName))

    dfTmp = pd.read_csv(obstabf, delimiter=',', skiprows=hdr_count, names=hdr_columns, header=None, parse_dates=[hdr_columns[2:4]], usecols=obstypes)

    # check whether the selected PRNs are in the dataframe, else remove this PRN from
    # print('lst_PRNs = {}'.format(lst_PRNs))
    lst_ObsPRNs = sorted(dfTmp.PRN.unique())
    # print('lst_obsPRNs = {}'.format(lst_ObsPRNs))
    # print("dfTmp[dfTmp['PRN'] == 'E07'] = \n{}".format(dfTmp[dfTmp['PRN'] == 'E07']))

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

    return lst_CommonPRNS, nav_signals, obsfreqs, dfTmp


def read_RFIscenario(jamscf: str,
                     cur_date: datetime,
                     logger: logging.Logger = None) -> pd.DataFrame:
    """
    read_RFIscenario reads the jamming scenario into a dataframe
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    df_jam = pd.read_csv(jamscf, delimiter=',', parse_dates=[['DATE', 'TIME']])
    jam_cols = df_jam.columns.tolist()

    # add column for SINR (Signal to Interferer and Noise ratio expressed in dB)
    df_jam['SINR [dB]'] = df_jam[jam_cols[1]] - df_jam[jam_cols[2]]

    if logger is not None:
        amutils.logHeadTailDataFrame(df=df_jam, dfName='df_jam', callerName=cFuncName, logger=logger)

    return df_jam


def analyse_obsprn(marker: str,
                   obstabf: str,
                   navsig_name: str,
                   dTime: dict,
                   dfPrnNavSig: pd.DataFrame,
                   dfPrnTle: pd.DataFrame,
                   dfJamSc: pd.DataFrame,
                   prn: str,
                   navsig_obst_lst: dict,
                   snrth: float,
                   interval: int,
                   show_plot: bool = False,
                   logger: logging.Logger = None) -> Tuple[list, list, dict]:
    """
    analyse_obsprn analyses the observations for the given PRN and determines a loss in SNR if asked.
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    plots = {}
    posidx_time_gaps = []
    posidx_snr_posjumps = {}
    posidx_snr_negjumps = {}

    # get a list of time jumps for this navigation signal
    # calculate the time difference between successive entries
    dfPrnNavSig.insert(loc=dfPrnNavSig.columns.get_loc('DATE_TIME') + 1,
                       column='dt',
                       value=(dfPrnNavSig['DATE_TIME'] - dfPrnNavSig['DATE_TIME'].shift(1)).astype('timedelta64[s]'))
    amutils.logHeadTailDataFrame(df=dfPrnNavSig, dfName='dfPrnNavSig', callerName=cFuncName, logger=logger)

    # check whether data is available for this PRN, if no data available, just return with empty stuff
    if dfPrnNavSig.shape[0] == 0:
        time_gaps = None
        time_reacqs = None
        # posidx_snr_posjumps = None
        # posidx_snr_negjumps = None
        plots = None

        return posidx_time_gaps, posidx_snr_posjumps, posidx_snr_negjumps, plots

    idx_time_gaps = dfPrnNavSig.index[dfPrnNavSig.dt != interval].tolist()
    # convert to positional indices
    posidx_time_gaps = [dfPrnNavSig.index.get_loc(gap) for gap in idx_time_gaps]
    # insert the first and last positional indices to get start and end time
    if posidx_time_gaps[0] != 0:
        posidx_time_gaps.insert(0, 0)
    if posidx_time_gaps[-1] != dfPrnNavSig.shape[0] - 1:
        posidx_time_gaps.append(dfPrnNavSig.shape[0] - 1)

    # print('{}: posidx_time_gaps = \n{}'.format(prn, posidx_time_gaps))
    # print('{}: posidx_time_gaps - 1 = \n{}'.format(prn, [x - 1 for x in posidx_time_gaps[1:-1]]))

    time_reacqs = dfPrnNavSig.iloc[posidx_time_gaps]['DATE_TIME']
    time_gaps = dfPrnNavSig.iloc[[x - 1 for x in posidx_time_gaps[1:-1]]]['DATE_TIME']
    # print('{}: time_reacqs = \n{}'.format(prn, time_reacqs))
    # print('{}: time_gaps = \n{}'.format(prn, time_gaps))

    # examine the requested observations for this navigation signal
    # print('{}: navsig_obst_lst = {}'.format(prn, navsig_obst_lst))
    for navsig_obs in navsig_obst_lst:
        # print('{}: navsig_obs = {}'.format(prn, navsig_obs))
        # select only the elements for this prn
        dfPrnNSObs = dfPrnNavSig[['DATE_TIME', 'dt', 'PRN', navsig_obs]].dropna()

        # add column which is difference between current and previous obst
        dfPrnNSObs.insert(loc=dfPrnNSObs.columns.get_loc(navsig_obs) + 1,
                          column='d{nso:s}'.format(nso=navsig_obs),
                          value=(dfPrnNSObs[navsig_obs] - dfPrnNSObs[navsig_obs].shift(1)).astype(float))

        # print('dfPrnNSObs = {}'.format(dfPrnNSObs))

        # find the exponential moving average
        # dfPrnNSObs['EMA05'] = dfPrnNSObs[navsig_obs].ewm(halflife='5 seconds', adjust=False, times=dfPrnNSObs['DATE_TIME']).mean()
        # dfPrnNSObs['WMA05'] = dfPrnNSObs[navsig_obs].rolling(5, min_periods=1).mean()

        # for idx_gap in idx_time_gaps[1:]:
        #     pos_idx_gap = dfPrnNSObs.index.get_loc(idx_gap)
        #     # print(dfPrnNSObs.iloc[pos_idx_gap - 2 * span:pos_idx_gap + int(span / 2)])

        # find the SNR differences that are higher than snrth (SNR threshold)
        if navsig_obs[0] == 'S':
            idx_snr_posjumps = dfPrnNSObs.index[dfPrnNSObs['d{nso:s}'.format(nso=navsig_obs)] > snrth].tolist()
            # convert to poisionla indices
            posidx_snr_posjumps[navsig_obs] = [dfPrnNSObs.index.get_loc(jump) for jump in idx_snr_posjumps]
            # print('posidx_snr_posjumps[navsig_obs] = {} #{}'.format(posidx_snr_posjumps[navsig_obs], len(posidx_snr_posjumps[navsig_obs])))

            idx_snr_negjumps = dfPrnNSObs.index[dfPrnNSObs['d{nso:s}'.format(nso=navsig_obs)] < -snrth].tolist()
            # convert to poisionla indices
            posidx_snr_negjumps[navsig_obs] = [dfPrnNSObs.index.get_loc(jump) for jump in idx_snr_negjumps]
            # print('posidx_snr_negjumps[navsig_obs] = {} #{}'.format(posidx_snr_negjumps[navsig_obs], len(posidx_snr_negjumps[navsig_obs])))
        else:
            posidx_snr_posjumps[navsig_obs] = None
            posidx_snr_negjumps[navsig_obs] = None

        # info to user
        if logger is not None:
            amutils.logHeadTailDataFrame(df=dfPrnNSObs, dfName='dfPrnNSObs', callerName=cFuncName, logger=logger)

        # plot for each PRN and obstfreq
        plots[navsig_obs] = tleobs_plot.plot_prn_navsig_obs(marker=marker,
                                                            dTime=dTime,
                                                            obsf=obstabf,
                                                            prn=prn,
                                                            dfPrnObst=dfPrnNSObs,
                                                            dfTlePrn=dfPrnTle,
                                                            dfJam=dfJamSc,
                                                            obst=navsig_obs,
                                                            posidx_gaps=posidx_time_gaps,
                                                            snrth=snrth,
                                                            show_plot=show_plot,
                                                            logger=logger)

    # print('plots = {}'.format(plots))
    # print('posidx_time_gaps = {}'.format(posidx_time_gaps))
    # print('posidx_snr_posjumps[navsig_obs] = {}'.format(posidx_snr_posjumps[navsig_obs]))
    # print('posidx_snr_negjumps[navsig_obs] = {}'.format(posidx_snr_negjumps[navsig_obs]))

    # return posidx_time_gaps, posidx_snr_posjumps[navsig_obs], posidx_snr_negjumps[navsig_obs], plots
    # print('time_gaps = \n{}'.format(time_gaps))
    # print('time_reacqs = \n{}'.format(time_reacqs))

    return time_gaps.tolist(), time_reacqs.tolist()[1:-1], plots


def pnt_available(dfPrnEvol: pd.DataFrame,
                  interval: int,
                  logger: logging.Logger = None) -> dict:
    """
    pnt_available deterimes the data_times corresponding to loss / reacquisition of PNT
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # # TEST CHECK IF START WITH NO PNT
    # dfPrnEvol = dfPrnEvol.iloc[11:]
    # dfPrnEvol.reset_index(inplace=True)
    # # END TEST CHECK IF START WITH NO PNT

    dPNT = {}
    dPNT['loss'] = []
    dPNT['reacq'] = []
    dPNT['PNTgap'] = []

    # print(dfPrnEvol)
    # print(dfPrnEvol.shape)

    # check at first period whether we have PNT or not available
    if dfPrnEvol.iloc[0]['PRNcnt'] >= 4:
        start_PNT = True
    else:
        start_PNT = False

    # indices used to find loss / reacquistion of PNT
    idx_PNTloss = idx_PNTreacq = 0

    while True:
        try:
            if start_PNT:  # have PNT at start
                # find index of first occurence that less than 4 satellites are tracked
                idx_PNTloss = dfPrnEvol.iloc[idx_PNTreacq:].loc[dfPrnEvol.PRNcnt < 4, 'PRNcnt'].index[0]
                # find when we have reacquired PNT
                idx_PNTreacq = dfPrnEvol.iloc[idx_PNTloss:].loc[dfPrnEvol.PRNcnt >= 4, 'PRNcnt'].index[0]

                # get corresponding timings and PNT time gap
                dPNT['loss'].append(dfPrnEvol.iloc[idx_PNTloss - 1]['DATE_TIME'])
                dPNT['reacq'].append(dfPrnEvol.iloc[idx_PNTreacq]['DATE_TIME'])

            else:  # did not have PNT at start
                # lost PNT at start
                dPNT['loss'].append(dfPrnEvol.iloc[0]['DATE_TIME'])

                # find when we have reacquired PNT
                idx_PNTreacq = dfPrnEvol.iloc[idx_PNTloss:].loc[dfPrnEvol.PRNcnt >= 4, 'PRNcnt'].index[0]
                dPNT['reacq'].append(dfPrnEvol.iloc[idx_PNTreacq]['DATE_TIME'])

                # we now have a new start where we have PNT
                start_PNT = True

            dPNT['PNTgap'].append((dPNT['reacq'][-1] - dPNT['loss'][-1]).total_seconds())
            if logger is not None:
                logger.info('{func:s}: PNT loss @ {loss:s} => {reacq:s} for {gap:.1f} s'.format(loss=dPNT['loss'][-1].strftime('%H:%M:%S'),
                    reacq=dPNT['reacq'][-1].strftime('%H:%M:%S'),
                    gap=dPNT['PNTgap'][-1],
                    func=cFuncName))

        except IndexError:
            break

    return dPNT


def loss_lock_combine(navsig: str,
                      dPNT: dict,
                      lst_prns: list,
                      dPRNs: dict,
                      logger: logging.Logger) -> pd.DataFrame:
    """
    loss_lock_combine combines loss and reacq over PNT and per navsig and PRN
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # create the dataframe holding the venets
    df_event = pd.DataFrame(columns=['DATE_TIME', 'event', 'type', 'duration'])

    # add to dataframe the events on PNT loss/reacquisition
    for dt_loss, t_gap in zip(dPNT['loss'], dPNT['PNTgap']):
        new_row = {'DATE_TIME': dt_loss, 'event': 'Loss', 'type': 'PNT', 'duration': t_gap}
        df_event = df_event.append(new_row, ignore_index=True)
    for dt_reacq in dPNT['reacq']:
        new_row = {'DATE_TIME': dt_reacq, 'event': 'Reacquisition', 'type': 'PNT', 'duration': np.nan}
        df_event = df_event.append(new_row, ignore_index=True)

    for prn in lst_prns:
        for dt_loss, t_gap in zip(dPRNs[prn]['loss'], dPRNs[prn]['gap']):
            new_row = {'DATE_TIME': dt_loss, 'event': 'Loss', 'type': '{prn:s}'.format(prn=prn), 'duration': t_gap}
            df_event = df_event.append(new_row, ignore_index=True)
        for dt_reacq in dPRNs[prn]['reacq']:
            new_row = {'DATE_TIME': dt_reacq, 'event': 'Reacquisition', 'type': '{prn:s}'.format(prn=prn), 'duration': np.nan}
            df_event = df_event.append(new_row, ignore_index=True)

    df_event.sort_values(by='DATE_TIME').reset_index(inplace=True)

    amutils.logHeadTailDataFrame(df=df_event, dfName='df_event', callerName=cFuncName, logger=logger)

    return df_event


def main_obstab_analyse(argv):
    """
    main_obstab_analyse analyses the created OBSTAB files and compares with TLE data.
    """

    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    global dTab
    dTab = {}
    dTab['cli'] = {}
    dTab['time'] = {}
    dTab['ltx'] = {}
    dTab['plots'] = {}
    dTab['lock'] = {}
    dTab['info'] = {}
    dTab['PNT'] = {}

    dTab['cli']['obstabf'], dTab['cli']['freqs'], dTab['cli']['lst_prns'], dTab['cli']['obs_types'], dTab['cli']['snrth'], dTab['cli']['mask'], dTab['cli']['jamsc'], show_plot, logLevels = treatCmdOpts(argv)

    # detect used GNSS from the obstabf filename
    dTab['info']['gnss'] = os.path.splitext(os.path.basename(dTab['cli']['obstabf']))[0][-1]
    dTab['info']['gnss_name'] = gfzc.dict_GNSSs[dTab['info']['gnss']]

    # create logging for better debugging
    logger, log_name = amc.createLoggers(baseName=os.path.basename(__file__), logLevels=logLevels)
    # read the observation header info from the Pickle file
    dTab['obshdr'] = '{obsf:s}.obshdr'.format(obsf=os.path.splitext(dTab['cli']['obstabf'])[0][:-2])
    try:
        with open(dTab['obshdr'], 'rb') as handle:
            dTab['hdr'] = pickle.load(handle)
        dTab['marker'] = dTab['hdr']['file']['site']
        dTab['time']['interval'] = float(dTab['hdr']['file']['interval'])
        dTab['info']['freqs'] = dTab['hdr']['file']['sysfrq'][dTab['info']['gnss']]
    except IOError as e:
        logger.error('{func:s}: error {err!s} reading header file {hdrf:s}'.format(hdrf=colored(dTab['obshdr'], 'red'), err=e, func=cFuncName))
        sys.exit(amc.E_FILE_NOT_EXIST)

    logger.info('{func:s}: Imported header information from {hdrf:s}\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab['hdr'], sort_keys=False, indent=4, default=amutils.json_convertor), hdrf=colored(dTab['obshdr'], 'blue')))

    # verify input
    check_arguments(logger=logger)

    # determine start and end times of observation
    dTab['time']['start'] = datetime.strptime(dTab['hdr']['data']['epoch']['first'].split('.')[0], '%Y %m %d %H %M %S')
    dTab['time']['end'] = datetime.strptime(dTab['hdr']['data']['epoch']['last'].split('.')[0], '%Y %m %d %H %M %S')

    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # read obstab into a dataframe and select the SNR for the selected frequencies
    dTab['lst_CmnPRNs'], dTab['nav_signals'], dTab['obsfreqs'], dfObsTab = read_obstab(obstabf=dTab['obstabf'],
                                                                                       lst_PRNs=dTab['lst_prns'],
                                                                                       dCli=dTab['cli'],
                                                                                       logger=logger)

    # get the observation time spans based on TLE values
    dfTLE = tle_visibility.PRNs_visibility(prn_lst=dfObsTab.PRN.unique(),
                                           DTG_start=dTab['time']['start'],
                                           DTG_end=dTab['time']['end'],
                                           interval=dTab['time']['interval'],
                                           cutoff=dTab['cli']['mask'],
                                           logger=logger)

    amutils.logHeadTailDataFrame(df=dfObsTab, dfName='dfObsTab', callerName=cFuncName, logger=logger)
    amutils.logHeadTailDataFrame(df=dfTLE, dfName='dfTLE', callerName=cFuncName, logger=logger)

    # read the jamming scenario into a dataframe
    if dTab['cli']['jamsc'] is not None:
        df_JamSc = read_RFIscenario(jamscf=dTab['cli']['jamsc'],
                                    cur_date = dTab['time']['date'],
                                    logger=logger)
    else:
        df_JamSc = pd.DataFrame(columns=['DATE_TIME', 'Signal [dBm]', 'Jammer [dBm]', 'SINR [dB]'])

    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab, sort_keys=False, indent=4, default=amutils.json_convertor)))

    # list with observable types per navigation signal
    lst_navsig_obst = {}
    # dict containing the oss / reacquisition events
    ddf_events = {}

    for navsig in dTab['nav_signals']:
        # dict for keeping the obtained info
        dTab['plots'][navsig] = {}
        dTab['lock'][navsig] = {}

        navsig_name = '{gnss:s}{navs:s}'.format(gnss=dTab['info']['gnss'], navs=navsig)
        logger.info('{func:s}: working on navigation signal {navs:s}'.format(navs=colored(navsig, 'green'), func=cFuncName))

        # keep the observables for this navigatoion signal
        col_navsig = [column for column in dfObsTab.columns.tolist()[:2]]
        col_navsig += [column for column in dfObsTab.columns.tolist()[2:] if column.endswith(navsig)]
        # print('col_navsig = {}'.format(col_navsig))
        dfNavSig = dfObsTab[col_navsig].dropna()

        amutils.logHeadTailDataFrame(df=dfNavSig, dfName='dfNavSig', callerName=cFuncName, logger=logger)

        # create dataframe for this navsig with count of PRN at each date_time
        dfNavSigPRNCount = dfNavSig.pivot_table(index=['DATE_TIME'], aggfunc='size').to_frame()
        dfNavSigPRNCount.reset_index(inplace=True)
        dfNavSigPRNCount.rename(columns={0: 'PRNcnt'}, inplace=True)
        # add difference in PRNcnt and difference in DATE_TIME
        dfNavSigPRNCount["dPRNcnt"] = dfNavSigPRNCount["PRNcnt"].diff(1)
        dfNavSigPRNCount["dt"] = dfNavSigPRNCount["DATE_TIME"].diff(dTab['time']['interval']).dt.total_seconds()
        amutils.logHeadTailDataFrame(df=dfNavSigPRNCount, dfName='dfNavSigPRNCount', callerName=cFuncName, logger=logger)

        # create a dataframe containing the times where there is a change in PRNcnt or a gap is detected
        idx_list = dfNavSigPRNCount.index[(dfNavSigPRNCount['dPRNcnt'] != 0) | (dfNavSigPRNCount['dt'] > dTab['time']['interval'])].tolist()
        idx_prev_list = [x - 1 for x in idx_list if x > 0]
        idx_merged = idx_list + idx_prev_list
        idx_merged.sort()
        # print('idx_list = {}'.format(idx_list))
        # print('idx_prev_list = {}'.format(idx_prev_list))
        # print('idx_merged = {}'.format(idx_merged))
        dfPRNEvol = dfNavSigPRNCount.iloc[idx_merged]
        dfPRNEvol.reset_index(drop=True, inplace=True)
        # print('dfPRNEvol = \n{}'.format(dfPRNEvol))
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            # print(dfPRNEvol)

        # create lists with DateTimes of loss / reacquisition of PNT
        dTab['PNT'][navsig] = pnt_available(dfPrnEvol=dfPRNEvol,
                                            interval=dTab['time']['interval'],
                                            logger=logger)
        # print("dTab['PNT'][navsig] = {}".format(dTab['PNT'][navsig]))

        amutils.logHeadTailDataFrame(df=dfPRNEvol, dfName='dfPRNEvol', callerName=cFuncName, logger=logger)

        # create plot with all selected PRNs vs the TLE part per navigation signal
        dTab['plots'][navsig]['tle-obs'] = tleobs_plot.obstle_plot_arcs_prns(marker=dTab['marker'],
                                                                             obsf=dTab['obstabf'],
                                                                             dTime=dTab['time'],
                                                                             navsig_name=navsig_name,
                                                                             lst_PRNs=dTab['lst_CmnPRNs'],
                                                                             dfNavSig=dfNavSig,
                                                                             dfTle=dfTLE,
                                                                             logger=logger,
                                                                             show_plot=show_plot)

        # perform analysis of the observations done per PRN and per navigation signal
        lst_navsig_obst[navsig] = [navsig_obs for navsig_obs in dTab['obsfreqs'] if navsig_obs.endswith(navsig)]

        # create plot with all selected PRNs for the selected obstypes
        dTab['plots'][navsig]['obst'] = tleobs_plot.obstle_plot_gnss_obst(marker=dTab['marker'],
                                                                          obsf=dTab['obstabf'],
                                                                          dTime=dTab['time'],
                                                                          navsig_name=navsig_name,
                                                                          lst_PRNs=dTab['lst_CmnPRNs'],
                                                                          dfNavSig=dfNavSig,
                                                                          dfNavSigPRNcnt=dfNavSigPRNCount,
                                                                          navsig_obst_lst=lst_navsig_obst[navsig],
                                                                          dfJam=df_JamSc,
                                                                          dfTle=dfTLE,
                                                                          logger=logger,
                                                                          show_plot=show_plot)

        for prn in dTab['lst_CmnPRNs']:

            # print('\nPRN = {} {}'.format(prn, navsig_name))
            # select the TLE row for this PRN
            dfTLEPrn = dfTLE.loc[prn]

            # select the TLE row for this PRN
            dfNavSigPRN = dfNavSig[dfNavSig['PRN'] == prn].dropna()
            # print('dfNavSigPRN = \n{}'.format(dfNavSigPRN))

            # posidx_time_gaps, posidx_snr_posjumps[navsig_obs], posidx_snr_negjumps[navsig_obs], plots
            prn_loss, prn_reacq, prn_plots = analyse_obsprn(marker=dTab['marker'],
                                                            obstabf=dTab['obstabf'],
                                                            navsig_name=navsig_name,
                                                            dTime=dTab['time'],
                                                            prn=prn,
                                                            dfPrnTle=dfTLEPrn,
                                                            dfPrnNavSig=dfNavSigPRN,
                                                            dfJamSc=df_JamSc,
                                                            navsig_obst_lst=lst_navsig_obst[navsig],
                                                            snrth=dTab['cli']['snrth'],
                                                            interval=dTab['time']['interval'],
                                                            show_plot=show_plot,
                                                            logger=logger)

            dTab['plots'][navsig][prn] = prn_plots

            dTab['lock'][navsig][prn] = {}
            dTab['lock'][navsig][prn]['loss'] = prn_loss
            dTab['lock'][navsig][prn]['reacq'] = prn_reacq
            dTab['lock'][navsig][prn]['gap'] = [(dt_reacq - dt_loss).total_seconds() for dt_loss, dt_reacq in zip(prn_loss, prn_reacq)]

            # print("xxx dTab[lock][{}][{}] = {}".format(navsig, prn, dTab['lock'][navsig][prn]))
        # combine the loss / reacquisition events in a dataframe
        ddf_events[navsig] = loss_lock_combine(navsig=navsig,
                                               dPNT=dTab['PNT'][navsig],
                                               lst_prns=dTab['lst_CmnPRNs'],
                                               dPRNs=dTab['lock'][navsig],
                                               logger=logger)
        amutils.logHeadTailDataFrame(df=ddf_events[navsig], dfName='ddf_events[navsig]', callerName=cFuncName, logger=logger)

    # report to the user
    dTab['ltx']['obstab'] = '{marker:s}_03_{gnss:s}_obs_tab'.format(marker=dTab['obstabf'][:9], gnss=dTab['info']['gnss'])

    sec_obstab = ltx_rnxobs_reporting.obstab_tleobs_ssec(dInfo=dTab['info'],
                                                         obstabf=dTab['obstabf'],
                                                         lst_PRNs=dTab['lst_CmnPRNs'],
                                                         lst_NavSignals=dTab['nav_signals'],
                                                         lst_ObsFreqs=dTab['obsfreqs'],
                                                         dfTle=dfTLE)
    ssec_tleobs = ltx_rnxobs_reporting.obstab_tleobs_overview(dInfo=dTab['info'],
                                                              navsigs=dTab['nav_signals'],
                                                              navsig_plts=dTab['plots'],
                                                              navsig_obst_lst=lst_navsig_obst,
                                                              lst_PRNs=dTab['lst_CmnPRNs'],
                                                              dEvents_df=ddf_events)
    sec_obstab.append(ssec_tleobs)
    sec_obstab.generate_tex(os.path.join(dTab['ltx']['path'], dTab['ltx']['obstab']))

    # store the json structure
    logger.info('{func:s}: Project information =\n{json!s}'.format(func=cFuncName, json=json.dumps(dTab, sort_keys=False, indent=4, default=amutils.json_convertor)))
    jsonName = os.path.join(dTab['dir'], '{scrname:s}.json'.format(scrname=os.path.splitext(os.path.basename(__file__))[0]))
    with open(jsonName, 'w+') as f:
        json.dump(dTab, f, ensure_ascii=False, indent=4, default=amutils.json_convertor)

    # clean up
    copyfile(log_name, os.path.join(dTab['dir'], '{scrname:s}.log'.format(scrname=os.path.basename(__file__).replace('.', '_'))))
    os.remove(log_name)


if __name__ == "__main__":  # Only run if this file is called directly
    main_obstab_analyse(sys.argv)
