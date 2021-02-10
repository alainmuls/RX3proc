import sys
import os
from termcolor import colored
import logging
import json
from typing import Union
import pandas as pd
import tempfile
from datetime import datetime

from ampyutils import am_config as amc
from ampyutils import amutils
from plot import obstab_plot


def RX3obs_header_info(gfzrnx: str, obs3f: str, logger: logging.Logger = None) -> dict:
    """
    RX3obs_header_info extracts the header information from a ::RX3:: observation file and returns it into a json structure
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # name of created json file
    jsonf = os.path.basename(obs3f).split('.')[0] + '-obs.json'

    # prepare the creation of obs hdr json structure
    # gfzrnx -finp P3RS00BEL_R_20203110910_05H_01S_MO.rnx -meta basic:json -fout jsonf
    args4GFZRNX = [gfzrnx, '-finp', obs3f, '-fout', jsonf, '-meta', 'basic:json', '-f']
    if logger is not None:
        logger.info('{func:s} extracting observation header info from {obs3f:s}'.format(obs3f=obs3f, func=cFuncName))

    err_code = amutils.run_subprocess(sub_proc=args4GFZRNX, logger=logger)
    if err_code != amc.E_SUCCESS:
        # get name of ::R3:: observation file
        if logger is not None:
            logger.error('{func:s}: {err!s} extracting header info from observation file'.format(err=err_code, func=cFuncName))
        sys.exit(err_code)

    # Opening JSON file and creating a dictionaty
    with open(jsonf) as fjson:
        dobs_hdr = json.load(fjson)

    return {key: dobs_hdr[key] for key in ['data', 'file']}


def get_observable_types(gfzdir: str, obstabf: str, gnss: str, logger: logging.Logger) -> Union[dict, int]:
    """
    get_observable_types finds the observable types for the selected GNSSs and returns as a dict per GNSS
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # read in the header lines of the obstab file and retain the headers requested
    gnss_hdrs = {}
    idx2use = {}

    # for gnss in amc.dRTK['cli']['GNSSs']:
    hdr_lines = amutils.txt_lines_with(substr='#HD {gnss:s}'.format(gnss=gnss), fname=os.path.join(gfzdir, obstabf))

    for hdr_line in hdr_lines:
        hdr = hdr_line.split()
        idx2use[gnss] = []

        # retain headers up until PRN
        idx_obstypes = hdr.index('PRN') + 1
        for idx in range(idx_obstypes):
            idx2use[gnss].append(idx)

        # retain headers according to the selected observable types
        for obstype in amc.dRTK['cli']['obstypes']:
            for idx in range(idx_obstypes, len(hdr), 1):
                if hdr[idx].startswith(obstype):
                    idx2use[gnss].append(idx)

    gnss_hdrs = [hdr[i] for i in idx2use[gnss]]

    logger.info('{func:s} gnss_hdrs are = {hdr!s}'.format(hdr=gnss_hdrs, func=cFuncName))

    return gnss_hdrs, idx_obstypes


def create_obstab(gfzrnx: str, dir_gfzrnx: str, obs3f: str, logger: logging.Logger) -> str:
    """
    create_obstab creates the observation tabular file from the RINEX obs file
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    if not amutils.mkdir_p(path=amc.dRTK['dirs']['gfzdata']):
        logger.error('{func:s}: Could!sot create directory {gfzd:s}'.format(gfzd=colored(amc.dRTK['dirs']['gfzdata'], 'red'), func=cFuncName))
        sys.exit(amc.E_DIR_NOT_EXIST)

    # create the observation tabular file
    # gfzrnx -finp POTS00DEU_R_20150070000_01D_30S_MO.rnx -tab_obs -fout POTS00DEU_2015007_G03.tab
    obs3tabf = os.path.splitext(obs3f)[0] + '.obstab'
    args4GFZRNX = [gfzrnx, '-finp', obs3f, '-tab_obs', '-fout', os.path.join(dir_gfzrnx, obs3tabf), '-f']

    if logger is not None:
        logger.info('{func:s} creating observation tabular file {obs3tabf:s}'.format(obs3tabf=obs3tabf, func=cFuncName))
    # run program
    err_code = amutils.run_subprocess(sub_proc=args4GFZRNX, logger=logger)
    if err_code != amc.E_SUCCESS:
        logger.error('{func:s}: error {err!s} creating observation tabular file {obs3tabf:s}'.format(err=err_code, obs3tabf=obs3tabf, func=cFuncName))
        sys.exit(err_code)

    return obs3tabf


def timing_overview(gnss: str, dfobs: dict, PRNs: list, obst_used: list, nrepochs: int, logger: logging.Logger = None) -> dict:
    """
    timing_overview analyses the general timing and number of observations per satsyst
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # # determine index of header PRN
    # prn_idx = dfobs.columns.get_loc('PRN')
    # obs_list = list(dfobs.columns.values)[prn_idx + 1:]
    # # get the number of unique epochs
    # epochs_observed = len(dfobs['DATE_TIME'].unique())

    # interate over the loged SVs and determine the number of observations per requested observable
    epochs_prn = {}
    for prn in PRNs:
        epochs_prn[prn] = {}
        for obst in obst_used:
            # print("dfobs[dfobs['{!s}'] == {!s}][obst].count() = {!s}".format(obst, prn, dfobs[dfobs['PRN'] == prn][obst].count()))
            epochs_prn[prn][obst] = dfobs[dfobs['PRN'] == prn][obst].count()
        if logger is not None:
            logger.debug('{func:s}: count of observables for {prn:s}: {count!s}'.format(prn=prn, count=epochs_prn[prn], func=cFuncName))
            # print('type(epochs_prn[prn]) = {!s}'.format(type(epochs_prn[prn])))

    # print('type(epochs_prn) = {!s}'.format(type(epochs_prn)))

    return epochs_prn


def read_obstab(gfzdir: str, obstabf: str, gnss: str, hdr: str, logger: logging.Logger) -> Union[pd.DataFrame, list, list]:
    """
    read_obstab reads the OBS tabular file into a dataframe
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # retain lines that start with "OBS GNSS"
    # create temporay file with only data for selected GNSS
    tmp_obstabf = os.path.join(tempfile.gettempdir(), obstabf)

    # read in the lines according to the selected GNSS
    with open(os.path.join(gfzdir, obstabf), 'r') as finp:
        hdr_line = amutils.lines_that_start_with('#HD {gnss:s}'.format(gnss=gnss), finp)
        finp.seek(0, 0)
        gnss_lines = amutils.lines_that_start_with('OBS {gnss:s}'.format(gnss=gnss), finp)
    # xrite these lines to a temporary file for loading into a dataframe
    with open(tmp_obstabf, 'w') as fout:
        fout.writelines(hdr_line)
        fout.writelines(gnss_lines)

    # dfobs = pd.DataFrame(columns=hdr)
    dfobs = pd.read_csv(tmp_obstabf, sep='\\s+', usecols=hdr, parse_dates=[['DATE', 'TIME']], na_values=['9999999999.999'])
    amutils.logHeadTailDataFrame(df=dfobs, dfName='dfobs[{gnss:s}]'.format(gnss=gnss), logger=logger, callerName=cFuncName)

    # get list of observed SVs
    lst_svs = sorted(dfobs['PRN'].unique())
    logger.info('{func:s} lst_svs = {svs!s}'.format(svs=lst_svs, func=cFuncName))

    return dfobs, lst_svs, [dfobs['DATE_TIME'].iloc[0], dfobs['DATE_TIME'].iloc[-1]]


def rnx_observation(show_plot: bool = False, logger: logging.Logger = None) -> dict:
    """
    rnx_observation makes an analysis of the rinex observation file
    """

    # analyse the GNSS observation tabular data
    dfobs = {}  # keep track of the dataframes extracted
    dTimeSpan = {}  # keep track of the observed epochs
    dPRNs = {}  # keep track of the observed PRNs
    dhdr_GNSS = {}  # keep track of the observables used for analysis
    dPRNepochs = {}  # count of observations per GNSS and per PRN
    idx_obst = {}  # index of first column with observables
    amc.dRTK['obstab']['obs_used'] = {}  # keeps observables per GNSS

    # read in dataframe the selected observables per GNSS
    for gnss in amc.dRTK['cli']['GNSSs']:
        dhdr_GNSS[gnss], idx_obst[gnss] = get_observable_types(gfzdir=amc.dRTK['dirs']['gfzdata'], obstabf=amc.dRTK['obstab']['fname'], gnss=gnss, logger=logger)

        # retain the observales used for each GNSS
        amc.dRTK['obstab']['obs_used'][gnss] = dhdr_GNSS[gnss][idx_obst[gnss]:]

        # get list of selected observations for this GNSS, the observed PRNs and the number of each observation type per PRN
        dfobs[gnss], dPRNs[gnss], dTimeSpan[gnss] = read_obstab(gfzdir=amc.dRTK['dirs']['gfzdata'], obstabf=amc.dRTK['obstab']['fname'], gnss=gnss, hdr=dhdr_GNSS[gnss], logger=logger)

        # analyse the obstab data for this GNSS
        dPRNepochs[gnss] = timing_overview(gnss=gnss, dfobs=dfobs[gnss], PRNs=dPRNs[gnss], obst_used=amc.dRTK['obstab']['obs_used'][gnss], nrepochs=dTimeSpan[gnss], logger=logger)

        # plot the number of observales per PRN and all observables for this satsyst
        # determine max number of observations
        # max_obs = int((epoch_last - epoch_first) / interval)
        amc.dRTK['obstab']['plt']['obs_count_{gnss:s}'.format(gnss=gnss)] = obstab_plot.obstab_plot_obscount(yyyy=amc.dRTK['cli']['yyyy'], doy=amc.dRTK['cli']['doy'], gnss=gnss, dprns=dPRNs, obsts_cli=amc.dRTK['cli']['obstypes'], obsts_used=amc.dRTK['obstab']['obs_used'][gnss], obs_epochs=dPRNepochs[gnss], dir_gfzplt=amc.dRTK['dirs']['rnxplt'], obstab_name=amc.dRTK['obstab']['fname'], show_plot=show_plot, logger=logger)

        amc.dRTK['obstab']['plt']['timeline_{gnss:s}'.format(gnss=gnss)] = obstab_plot.obstab_plot_obstimelines(yyyy=amc.dRTK['cli']['yyyy'], doy=amc.dRTK['cli']['doy'], gnss=gnss, dfobs=dfobs[gnss], dprns=dPRNs, obsts_cli=amc.dRTK['cli']['obstypes'], obsts_used=amc.dRTK['obstab']['obs_used'][gnss], obs_epochs=dPRNepochs[gnss], dir_gfzplt=amc.dRTK['dirs']['rnxplt'], obstab_name=amc.dRTK['obstab']['fname'], show_plot=show_plot, logger=logger)

        # adjust the headers for the dfobs because the columns DATE and TIME have been merged to DATE_TIME
        dhdr_GNSS[gnss][2] = 'DATE_TIME'
        dhdr_GNSS[gnss].pop(3)
        idx_obst[gnss] -= 1

        epoch_first = datetime.strptime(amc.dRTK['rnx']['obshdr']['data']['epoch']['first'].split('.')[0], '%Y %m %d %H %M %S')
        epoch_last = datetime.strptime(amc.dRTK['rnx']['obshdr']['data']['epoch']['last'].split('.')[0], '%Y %m %d %H %M %S')

        # create plots for the selected observation types for each PRN
        for obst_cli in amc.dRTK['cli']['obstypes']:
            lst_obst_cli = [idx for idx in dhdr_GNSS[gnss][idx_obst[gnss]:] if idx[0].lower() == obst_cli.lower()]
            lst_hdrs_obst = dhdr_GNSS[gnss][:idx_obst[gnss]] + lst_obst_cli  # headers to be read for each PRNs

            # store figures for this obst in
            amc.dRTK['obstab']['plt']['{gnss:s}_{obst:s}'.format(gnss=gnss, obst=obst_cli)] = {}

            for prn in dPRNs[gnss]:

                # select subset od dfobs that corresponds to the selected obst_cli and prn
                dfPRNobst = dfobs[gnss][lst_hdrs_obst].loc[dfobs[gnss]['PRN'] == prn]

                # create the plot
                amc.dRTK['obstab']['plt']['{gnss:s}_{obst:s}'.format(gnss=gnss, obst=obst_cli)][prn] = obstab_plot.obstab_plot_observable(yyyy=amc.dRTK['cli']['yyyy'], doy=amc.dRTK['cli']['doy'], gnss=gnss, dfprnobst=dfPRNobst, dir_gfzplt=amc.dRTK['dirs']['rnxplt'], obstab_name=amc.dRTK['obstab']['fname'], dt_first=epoch_first, dt_last=epoch_last, show_plot=show_plot, logger=logger)

    amc.dRTK['obstab']['t_span'] = dTimeSpan
    amc.dRTK['obstab']['PRNs'] = dPRNs
    # amc.dRTK['obstab']['prn_epochs'] = dPRNepochs

    return dPRNepochs
