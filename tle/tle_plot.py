import os
import sys
from termcolor import colored
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from matplotlib import dates

from ampyutils import amutils
from plot import plot_utils
from gfzrnx import gfzrnx_constants as gco

__author__ = 'amuls'


def tle_plot_arcs(obsstatf: str, dfTle: pd.DataFrame, dTime: dict, show_plot: bool = False, logger: logging.Logger = None):
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

    gnss_id = dfTle.index.to_list()[0][0]
    y_prns = [int(prn[1:]) for prn in dfTle.index.to_list()]

    # create colormap with nrcolors discrete colors
    prn_colors, title_font = amutils.create_colormap_font(nrcolors=len(y_prns), font_size=12)

    # get the date of this observation to combine with rise and set times
    cur_date = dTime['date'].date()

    for i, (prn, tle_prn) in enumerate(dfTle.iterrows()):
        # print('prn = {!s}: y_prn = {:d} rise = {!s}  set = {!s}'.format(prn, y_prns[i], tle_prn.tle_rise, tle_prn.tle_set))

        for tle_rise, tle_set in zip(tle_prn.tle_rise, tle_prn.tle_set):
            # print('   rise = {!s} -> set = {!s}'.format(datetime.combine(cur_date, tle_rise), datetime.combine(cur_date, tle_set)))
            ax.plot_date(y=[y_prns[i], y_prns[i]], x=[datetime.combine(cur_date, tle_rise), datetime.combine(cur_date, tle_set)], linewidth=2, color=prn_colors[i], linestyle='-', markersize=6, marker='|')

        # print('tle_prn.tle_cul = {!s}'.format(tle_prn.tle_cul))
        # print('type(tle_prn.tle_cul) = {!s}'.format(type(tle_prn.tle_cul)))
        for _, tle_cul in enumerate(tle_prn.tle_cul):
            # print('tle_cul = {!s}'.format(tle_cul))
            # print('type(tle_cul) = {!s}'.format(type(tle_cul)))
            if tle_cul is not np.NaN:
                ax.plot_date(y=y_prns[i], x=datetime.combine(cur_date, tle_cul), color=prn_colors[i], markersize=6, marker='v')

    # beautify plot
    ax.xaxis.grid(b=True, which='major')
    ax.yaxis.grid(b=True, which='major')
    ax.legend(loc='best', markerscale=4)

    # ax.set_xlabel('PRN', fontdict=title_font)
    ax.set_ylabel('PRNs', fontdict=title_font)
    ax.set_xlabel('TLE arcs', fontdict=title_font)

    # plot title
    plt.title('TLE arcs for GNSS {gnss:s} on {date!s} ({yy:04d}/{doy:03d})'.format(gnss=gco.dict_GNSSs[gnss_id], yy=dTime['YYYY'], doy=dTime['DOY'], date=dTime['date'].strftime('%d/%m/%Y')))

    # setticks on Y axis to represent the PRNs
    ax.yaxis.set_ticks(np.arange(1, y_prns[-1] + 1))
    print(dfTle.index.to_list())
    tick_labels = []
    print(gnss_id)
    for i in np.arange(1, y_prns[-1] + 1):
        tick_prn = '{gnss:s}{prn:02d}'.format(gnss=gnss_id, prn=i)
        if tick_prn in dfTle.index.to_list():
            tick_labels.append(tick_prn)
        else:
            tick_labels.append('')

    ax.set_yticklabels(tick_labels)

    # create the ticks for the time ax
    ax.set_xlim([datetime.combine(cur_date, dt_min), datetime.combine(cur_date, dt_max)])
    dtFormat = plot_utils.determine_datetime_ticks(startDT=datetime.combine(cur_date, dt_min), endDT=datetime.combine(cur_date, dt_max))

    if dtFormat['minutes']:
        # ax.xaxis.set_major_locator(dates.MinuteLocator(byminute=range(10, 60, 10), interval=1))
        pass
    else:
        ax.xaxis.set_major_locator(dates.HourLocator(interval=dtFormat['hourInterval']))   # every 4 hours
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))  # hours and minutes

    ax.xaxis.set_minor_locator(dates.DayLocator(interval=1))    # every day
    ax.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))

    ax.xaxis.set_tick_params(rotation=0)
    for tick in ax.xaxis.get_major_ticks():
        # tick.tick1line.set_markersize(0)
        # tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    fig.tight_layout()

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    for ext in ['pdf', 'png', 'eps']:
        plt_name = os.path.join('png', '{basen:s}-TLEarcs.{ext:s}'.format(basen=obsstatf.split('.')[0], ext=ext))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)
