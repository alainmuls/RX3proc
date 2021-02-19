import sys
import os
import logging
from termcolor import colored
from datetime import datetime, timedelta
from skyfield import api as sf
import pandas as pd

from tle import tle_parser
from ampyutils import amutils

__author__ = 'amuls'


def PRNs_visibility(prn_lst: list, cur_date: datetime, interval: float, cutoff: int = 5, logger: logging.Logger = None) -> pd.DataFrame:
    """
    PRNs_visibility determines the visibilty info for list of PRNs passed
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('{func:s}: observed PRNs are {prns!s} (#{total:d})'.format(prns=prn_lst, total=len(prn_lst), func=cFuncName))

    logger.info('{func:s}; getting corresponding NORAD info'.format(func=cFuncName))

    # read the files galileo-NORAD-PRN.t and gps-ops-NORAD-PRN.t
    dfNORAD = tle_parser.read_norad2prn(logger=logger)
    amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=dfNORAD, dfName='dfNORAD')

    # get the corresponding NORAD nrs for the given PRNs
    dNORADs = tle_parser.get_norad_numbers(prns=prn_lst, dfNorad=dfNORAD, logger=logger)
    logger.info('{func:s}: corresponding NORAD nrs (#{count:d}):'.format(count=len(dNORADs), func=cFuncName))

    # load a time scale and set RMA as Topo
    # loader = sf.Loader(dir_tle, expire=True)  # loads the needed data files into the tle dir
    ts = sf.load.timescale()
    RMA = sf.Topos('50.8438 N', '4.3928 E')
    logger.info('{func:s}: Earth station RMA @ {topo!s}'.format(topo=colored(RMA, 'green'), func=cFuncName))
    # get the datetime that corresponds to yydoy
    # date_yydoy = datetime.strptime(amc.dRTK['rnx']['times']['DT'], '%Y-%m-%d %H:%M:%S')
    # yydoy = date_yydoy.strftime('%y%j')
    logger.info('{func:s}: calculating rise / set times for {date:s}'.format(date=cur_date, func=cFuncName))

    t0 = ts.utc(int(cur_date.strftime('%Y')), int(cur_date.strftime('%m')), int(cur_date.strftime('%d')))
    date_tomorrow = cur_date + timedelta(days=1)
    t1 = ts.utc(int(date_tomorrow.strftime('%Y')), int(date_tomorrow.strftime('%m')), int(date_tomorrow.strftime('%d')))

    # find corresponding TLE record for NORAD nrs
    df_tles = tle_parser.find_norad_tle_yydoy(dNorads=dNORADs, yydoy=cur_date.strftime('%y%j'), logger=logger)

    # list of rise / set times by observation / TLEs
    lst_obs_rise = []

    # find in observations and by TLEs what the riuse/set times are and number of observations
    for prn in prn_lst:
        # find rise:set times using TLEs
        dt_tle_rise, dt_tle_set, dt_tle_cul, tle_arc_count = tle_parser.tle_rise_set_times(prn=prn, df_tle=df_tles, marker=RMA, t0=t0, t1=t1, elev_min=cutoff, obs_int=1, logger=logger)

        # add to list for creating dataframe
        lst_obs_rise.append([dt_tle_rise, dt_tle_set, dt_tle_cul, tle_arc_count])

    # test to import in dataframe
    df_rise_set_tmp = pd.DataFrame(lst_obs_rise, columns=['tle_rise', 'tle_set', 'tle_cul', 'tle_arc_count'], index=prn_lst)

    return df_rise_set_tmp
