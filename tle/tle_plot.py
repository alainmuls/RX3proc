import os
import sys
from termcolor import colored
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
import matplotlib.ticker as ticker
from typing import Tuple
from datetime import datetime, time

from ampyutils import amutils

__author__ = 'amuls'


def tle_plot_arcs(dfTle: pd.DataFrame, dTime: dict, show_plot: bool = False, logger: logging.Logger = None):
    """
    tle_plot_arcs plots the arcs caclculated by TLE for the GNSS
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    # find minimum time for tle_rise and maximum time for tle_set columns
    dt_min = min(dfTle.tle_rise.apply(lambda x: x[0]))
    dt_max = max(dfTle.tle_set.apply(lambda x: x[-1]))
    if logger is not None:
        logger.info('{func:s}: TLE time span {start:s} -> {end:s}'.format(start=dt_min.strftime('%H:%M:%S'), end=dt_max.strftime('%H:%M:%S'), func=cFuncName))

    fig, ax = plt.subplots(figsize=(8, 6))

    y_prns = [int(prn[1:]) for prn in dfTle.index.to_list()]
    print(y_prns)

    # create colormap with nrcolors discrete colors
    prn_colors, title_font = amutils.create_colormap_font(nrcolors=len(y_prns), font_size=12)

    # get the date of this observation to combine with rise and set times
    cur_date = dTime['date'].date()

    for i, (prn, tle_prn) in enumerate(dfTle.iterrows()):
        print('prn = {!s}: y_prn = {:d} rise = {!s}  set = {!s}'.format(prn, y_prns[i], tle_prn.tle_rise, tle_prn.tle_set))

        for tle_rise, tle_set in zip(tle_prn.tle_rise, tle_prn.tle_set):
            print('   rise = {!s} -> set = {!s}'.format(datetime.combine(cur_date, tle_rise), datetime.combine(cur_date, tle_set)))
            ax.plot_date(y=[y_prns[i], y_prns[i]], x=[datetime.combine(cur_date, tle_rise), datetime.combine(cur_date, tle_set)], linewidth=2, color=prn_colors[i], linestyle='-', markersize=6, marker='|')

        print('tle_prn.tle_cul = {!s}'.format(tle_prn.tle_cul))
        print('type(tle_prn.tle_cul) = {!s}'.format(type(tle_prn.tle_cul)))
        for _, tle_cul in enumerate(tle_prn.tle_cul):
            print('tle_cul = {!s}'.format(tle_cul))
            print('type(tle_cul) = {!s}'.format(type(tle_cul)))
            if tle_cul is not np.NaN:
                ax.plot_date(y=y_prns[i], x=datetime.combine(cur_date, tle_cul), color=prn_colors[i], markersize=6, marker='v')


    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    sys.exit(66)
