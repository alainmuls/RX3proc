import os
import sys
from termcolor import colored
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from matplotlib import dates
from typing import Tuple

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
    dt_rise = []
    dt_set = []
    for j, (t_rise, t_set) in enumerate(zip(dfTle.tle_rise, dfTle.tle_set)):
        if len(t_rise) > 0:
            dt_rise.append(t_rise[0])
        if len(t_set) > 0:
            dt_set.append(t_set[-1])

    dt_min = min(dt_rise)
    dt_max = max(dt_set)

    if logger is not None:
        logger.info('{func:s}: TLE time span {start:s} -> {end:s}'.format(start=dt_min.strftime('%H:%M:%S'), end=dt_max.strftime('%H:%M:%S'), func=cFuncName))

    fig, ax = plt.subplots(figsize=(8, 6))

    gnss_id = dfTle.index.to_list()[0][0]
    y_prns = [int(prn[1:]) for prn in dfTle.index.to_list()]

    # create colormap with nrcolors discrete colors
    prn_colors, title_font = amutils.create_colormap_font(nrcolors=len(y_prns), font_size=12)

    # get the date of this observation to combine with rise and set times
    cur_date = dTime['date'].date()

    for y_prn, prn_color, (prn, tle_prn) in zip(y_prns, prn_colors, dfTle.iterrows()):
        for tle_rise, tle_set in zip(tle_prn.tle_rise, tle_prn.tle_set):
            ax.plot_date(y=[y_prn, y_prn], x=[datetime.combine(cur_date, tle_rise), datetime.combine(cur_date, tle_set)], linewidth=2, color=prn_color, linestyle='-', markersize=6, marker='|')
        for _, tle_cul in enumerate(tle_prn.tle_cul):
            if tle_cul is not np.NaN:
                ax.plot_date(y=y_prn, x=datetime.combine(cur_date, tle_cul), color=prn_color, markersize=6, marker='v')

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
    tick_labels = []
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


def obstle_plot_obscount(obsstatf: str, dfObsTle: pd.DataFrame, dTime: dict, reduce2percentage: bool = False, show_plot: bool = False, logger: logging.Logger = None):
    """
    obstle_plot_arcs plots count of observations wrt to number obtained from TLE
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    fig, ax = plt.subplots(figsize=(8, 6))

    gnss_id = dfObsTle.TYP.iloc[0][0]
    y_prns = [int(prn[1:]) for prn in dfObsTle.TYP.to_list()]

    # select the columns used for plotting
    col_names = dfObsTle.columns.tolist()
    obstypes = col_names[4:]

    # determine widths of bars to use for each PRN
    dy_obstypes, bar_width = bars_info(nr_arcs=len(obstypes), logger=logger)

    # create colormap with nrcolors discrete colors
    bar_colors, title_font = amutils.create_colormap_font(nrcolors=len(obstypes), font_size=12)

    # plot the TLE observation count
    for i, (y_prn, prn) in enumerate(zip(y_prns, dfObsTle.TYP)):
        for j, (obst, dy_obst, bar_color) in enumerate(zip(list(reversed(obstypes)), list(reversed(dy_obstypes)), list(reversed(bar_colors)))):
            prn_width = dfObsTle.iloc[i][obst]
            print('prn_width = {!s}'.format(prn_width))
            if not reduce2percentage:
                if i == 0:
                    ax.barh(y=y_prn + dy_obst, width=prn_width, height=bar_width, color=bar_color, label=obst)
                else:
                    ax.barh(y=y_prn + dy_obst, width=prn_width, height=bar_width, color=bar_color)
            else:
                if j == 0:
                    tle_width = prn_width / 100
                if tle_width != 0:
                    if i == 0:
                        ax.barh(y=y_prn + dy_obst, width=prn_width / tle_width, height=bar_width, color=bar_color, label=obst)
                    else:
                        ax.barh(y=y_prn + dy_obst, width=prn_width / tle_width, height=bar_width, color=bar_color)

    # beautify plot
    ax.xaxis.grid(b=True, which='major')
    ax.yaxis.grid(b=True, which='major')
    ax.legend(loc='best', markerscale=4)

    # ax.set_xlabel('PRN', fontdict=title_font)
    ax.set_ylabel('PRNs', fontdict=title_font)
    if not reduce2percentage:
        ax.set_xlabel('Observations Count [-]', fontdict=title_font)
    else:
        ax.set_xlabel('Observations Count [%]', fontdict=title_font)

    # plot title
    plt.title('Observations Count for GNSS {gnss:s} on {date!s} ({yy:04d}/{doy:03d})'.format(gnss=gco.dict_GNSSs[gnss_id], yy=dTime['YYYY'], doy=dTime['DOY'], date=dTime['date'].strftime('%d/%m/%Y')))

    # setticks on Y axis to represent the PRNs
    ax.yaxis.set_ticks(np.arange(1, y_prns[-1] + 1))
    tick_labels = []
    for i in np.arange(1, y_prns[-1] + 1):
        tick_prn = '{gnss:s}{prn:02d}'.format(gnss=gnss_id, prn=i)
        if tick_prn in dfObsTle.TYP.to_list():
            tick_labels.append(tick_prn)
        else:
            tick_labels.append('')

    ax.set_yticklabels(tick_labels)

    fig.tight_layout()

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    for ext in ['pdf', 'png', 'eps']:
        plt_name = os.path.join('png', '{basen:s}-ObsTLE.{ext:s}'.format(basen=obsstatf.split('.')[0], ext=ext))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)


def bars_info(nr_arcs: int, logger: logging.Logger) -> Tuple[list, int]:
    """
    bars_info determines the width of an individual bar, the spaces between the arc bars, and localtion in delta-x-coordinates of beginning of each PRN arcs
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')
    logger.info('{func:s}: determining the information for the bars'.format(func=cFuncName))

    # the bars for all arcs for 1 PRN may span over 0.8 units (from [-0.4 => 0.4]), including the spaces between the different arcs
    width_prn_arcs = 0.8
    dx_start = -0.4  # start of the bars relative to integer of PRN
    width_space = 0.02  # space between the different arcs for 1 PRN

    # substract width-spaces needed for nr_arcs
    width_arcs = width_prn_arcs - (nr_arcs - 1) * width_space

    # the width taken by 1 arc for 1 prn is
    width_arc = width_arcs / nr_arcs

    # get the delta-x to apply to the integer value that corresponds to a PRN
    dx_obs = [dx_start + i * (width_space + width_arc) for i in np.arange(nr_arcs)]

    return dx_obs, width_arc

