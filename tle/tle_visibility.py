import sys
import os
import logging
from termcolor import colored
from datetime import datetime
from skyfield.api import EarthSatellite
from skyfield import api as sf
import pandas as pd
import numpy as np

from tle import tle_parser
from ampyutils import amutils

__author__ = 'amuls'


def PRNs_visibility(prn_lst: list,
                    DTG_start: datetime,
                    DTG_end: datetime,
                    interval: float,
                    cutoff: int = 5,
                    logger: logging.Logger = None) -> pd.DataFrame:
    """
    PRNs_visibility determines the visibilty info for list of PRNs passed
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    if logger is not None:
        logger.info('{func:s}: observed PRNs are {prns!s} (#{total:d})'.format(prns=prn_lst,
                                                                               total=len(prn_lst),
                                                                               func=cFuncName))
        logger.info('{func:s}; getting corresponding NORAD info'.format(func=cFuncName))

    # read the files galileo-NORAD-PRN.t and gps-ops-NORAD-PRN.t
    dfNORAD = tle_parser.read_norad2prn(logger=logger)
    amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=dfNORAD, dfName='dfNORAD')

    # get the corresponding NORAD nrs for the given PRNs
    dNORADs = tle_parser.get_norad_numbers(prns=prn_lst, dfNorad=dfNORAD, logger=logger)
    if logger is not None:
        logger.info('{func:s}: corresponding NORAD nrs (#{count:d}):'.format(count=len(dNORADs), func=cFuncName))

    # load a time scale and set RMA as Topo
    # loader = sf.Loader(dir_tle, expire=True)  # loads the needed data files into the tle dir
    ts = sf.load.timescale()
    RMA = sf.Topos('50.8438 N', '4.3928 E')
    if logger is not None:
        logger.info('{func:s}: Earth station RMA @ {topo!s}'.format(topo=colored(RMA, 'green'), func=cFuncName))
        # get the datetime that corresponds to yydoy
        # date_yydoy = datetime.strptime(amc.dRTK['rnx']['times']['DT'], '%Y-%m-%d %H:%M:%S')
        # yydoy = date_yydoy.strftime('%y%j')
        logger.info('{func:s}: calculating rise / set times for {DTGstart:s} => {DTGend:s}'
                    .format(DTGstart=DTG_start.strftime('%Y/%m/%d %H:%M:%S'),
                            DTGend=DTG_end.strftime('%Y/%m/%d %H:%M:%S'),
                            func=cFuncName))

    # print(DTG_start.strftime('%Y/%m/%d %H:%M:%S'))
    # print(DTG_end.strftime('%Y/%m/%d %H:%M:%S'))
    tobs_0 = ts.utc(year=int(DTG_start.strftime('%Y')),
                    month=int(DTG_start.strftime('%m')),
                    day=int(DTG_start.strftime('%d')),
                    hour=int(DTG_start.strftime('%H')),
                    minute=int(DTG_start.strftime('%M')),
                    second=int(DTG_start.strftime('%S')))
    # date_tomorrow = cur_date + timedelta(days=1)
    # t1 = ts.utc(int(date_tomorrow.strftime('%Y')), int(date_tomorrow.strftime('%m')), int(date_tomorrow.strftime('%d')))
    tobs_1 = ts.utc(year=int(DTG_end.strftime('%Y')),
                    month=int(DTG_end.strftime('%m')),
                    day=int(DTG_end.strftime('%d')),
                    hour=int(DTG_end.strftime('%H')),
                    minute=int(DTG_end.strftime('%M')),
                    second=int(DTG_end.strftime('%S')))

    # print('tobs_0 = {}'.format(tobs_0))
    # print('tobs_1 = {}'.format(tobs_1))

    # find corresponding TLE record for NORAD nrs
    df_tles = tle_parser.find_norad_tle_yydoy(dNorads=dNORADs, yydoy=DTG_start.strftime('%y%j'), logger=logger)

    # list of rise / set times by observation / TLEs
    lst_obs_rise = []

    # find in observations and by TLEs what the riuse/set times are and number of observations
    for prn in prn_lst:
        # print('-' * 25)
        # print(prn)
        # find rise:set times using TLEs
        dt_tle_rise, dt_tle_set, dt_tle_cul, tle_arc_count = \
            tle_parser.tle_rise_set_times(prn=prn,
                                          df_tle=df_tles,
                                          marker=RMA,
                                          t0_obs=tobs_0,
                                          t1_obs=tobs_1,
                                          elev_min=cutoff,
                                          obs_int=1,
                                          logger=logger)

        # add to list for creating dataframe
        lst_obs_rise.append([dt_tle_rise, dt_tle_set, dt_tle_cul, tle_arc_count])

    # test to import in dataframe
    df_rise_set_tmp = pd.DataFrame(lst_obs_rise,
                                   columns=['tle_rise', 'tle_set', 'tle_cul', 'tle_arc_count'],
                                   index=prn_lst)

    # sys.exit(56)

    return df_tles, df_rise_set_tmp


def prn_elevation(prn: str,
                  df_tle_prn: pd.DataFrame,
                  elev_step: int,
                  DTG_start: datetime,
                  DTG_end: datetime,
                  logger: logging.Logger = None) -> pd.DataFrame:
    """
    prn_elevation calculates for a PRN the times that that PRN reaches a certain elevation angle
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # print('df_tle_prn = \n{}'.format(df_tle_prn))

    # load a time scale and set RMA as Topo
    # loader = sf.Loader(dir_tle, expire=True)  # loads the needed data files into the tle dir
    ts = sf.load.timescale()
    RMA = sf.Topos('50.8438 N', '4.3928 E')
    if logger is not None:
        logger.info('{func:s}: Earth station RMA @ {topo!s}'.format(topo=colored(RMA, 'green'), func=cFuncName))
        # get the datetime that corresponds to yydoy

    t0 = ts.utc(year=int(DTG_start.strftime('%Y')),
                month=int(DTG_start.strftime('%m')),
                day=int(DTG_start.strftime('%d')),
                hour=int(DTG_start.strftime('%H')),
                minute=int(DTG_start.strftime('%M')),
                second=int(DTG_start.strftime('%S')))
    # date_tomorrow = cur_date + timedelta(days=1)
    # t1 = ts.utc(int(date_tomorrow.strftime('%Y')), int(date_tomorrow.strftime('%m')), int(date_tomorrow.strftime('%d')))
    t1 = ts.utc(year=int(DTG_end.strftime('%Y')),
                month=int(DTG_end.strftime('%m')),
                day=int(DTG_end.strftime('%d')),
                hour=int(DTG_end.strftime('%H')),
                minute=int(DTG_end.strftime('%M')),
                second=int(DTG_end.strftime('%S')))

    elev_t0 = ts.utc(year=int(DTG_start.strftime('%Y')),
                     month=int(DTG_start.strftime('%m')),
                     day=int(DTG_start.strftime('%d')),
                     hour=0,
                     minute=0,
                     second=0)
    # date_tomorrow = cur_date + timedelta(days=1)
    # t1 = ts.utc(int(date_tomorrow.strftime('%Y')), int(date_tomorrow.strftime('%m')), int(date_tomorrow.strftime('%d')))
    elev_t1 = ts.utc(year=int(DTG_end.strftime('%Y')),
                     month=int(DTG_end.strftime('%m')),
                     day=int(DTG_end.strftime('%d')),
                     hour=23,
                     minute=59,
                     second=59)

    # print('elev_t0 = {}'.format(elev_t0))
    # print('elev_t1 = {}'.format(elev_t1))

    # create a EarthSatellites from the TLE lines for this PRN
    gnss_sv = EarthSatellite(df_tle_prn.iloc[0]['TLE1'], df_tle_prn.iloc[0]['TLE2'])
    # print('gnss_sv = {}'.format(gnss_sv))

    # keep list of events for elevation
    data_elev = []

    for elev in range(0, 90, elev_step):
        ti, elev_events = gnss_sv.find_events(RMA, elev_t0, elev_t1, altitude_degrees=elev)
        # print('{}: {} {} {}'.format(elev, elev_events, elev_events.size, type(elev_events)))
        if elev_events.size > 0 and (0 in elev_events or 2 in elev_events):
            # print('HERE {} @ {} elev_events {}: \n{}'.format(prn, elev, elev_events, ti.utc_datetime()))

            # find the times for rising above elev angle
            idx_rises = np.where(elev_events == 0)
            # print('idx_rises = {}'.format(idx_rises))
            for idx_rise in idx_rises[0]:
                # print('idx_rise = {}'.format(idx_rise))
                # t_rise = ti[idx_rise].utc_datetime()
                t_rise = ti[idx_rise].utc_datetime().time().replace(microsecond=0)
                # print('t_rise = {}'.format(t_rise))

                # if in observation interval, add to df_PRNelev
                if t0.utc_datetime().time() <= t_rise <= t1.utc_datetime().time():
                    # print('t_rise of PRN {} above {} degrees at {}'.format(prn, elev, t_rise))
                    data_elev.append([datetime.combine(DTG_start.date(), t_rise), elev])

            # find the times for rising above elev angle
            idx_sets = np.where(elev_events == 2)
            # print('idx_sets = {}'.format(idx_sets))
            for idx_set in idx_sets[0]:
                # print('idx_set = {}'.format(idx_set))
                # t_set = ti[idx_set].utc_datetime()
                t_set = ti[idx_set].utc_datetime().time().replace(microsecond=0)
                # print('t_set = {}'.format(t_set))

                if t0.utc_datetime().time() <= t_set <= t1.utc_datetime().time():
                    # print('t_set of PRN {} below {} degrees at {}'.format(prn, elev, t_set))
                    data_elev.append([datetime.combine(DTG_start.date(), t_set), elev])

        # svrise, svset, svcul, tle_count = tle_parser.tle_rise_set_times(prn=prn,
        #                                                                 df_tle=df_tles,
        #                                                                 marker=RMA,
        #                                                                 t0=t0,
        #                                                                 t1=t1,
        #                                                                 elev_min=elev,
        #                                                                 obs_int=1,
        #                                                                 logger=logger)
        # print('this {} @ {}: {} {} {}'.format(prn, elev, svrise, svcul, svset))

    # create dataframe containing the DATE_TIME at which time a elevation angle is reached
    df_PRNelev = pd.DataFrame(data_elev, columns=['DATE_TIME', 'elevation'])

    return df_PRNelev
