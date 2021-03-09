import os
import sys
from termcolor import colored
import matplotlib.pyplot as plt
import numpy as np
import logging
from typing import Tuple
import matplotlib.ticker as ticker
import pandas as pd
from matplotlib import dates
from datetime import datetime

from ampyutils import amutils
from plot import plot_utils
from gfzrnx import gfzrnx_constants as gfzc

__author__ = 'amuls'


def obstab_plot_obstimelines(dfObsTab: pd.DataFrame, lst_prns: list, dTime: dict, show_plot: bool = False, logger: logging.Logger = None) -> str:
    """
    obstab_plot_obstimelines plots the timeline of observales per PRN
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')
    # plt.style.use('seaborn-darkgrid')

    # determine how many PRNs are observed used as coordinate
    y_prns = np.arange(len())  # location of the PRNs

    # determine how many bars per PRN, that is how many observables of one type found
    obst_cli = obsts_cli[0]  # in enumerate(obsts_cli), all observables have the same timeline
    obst_bars = [obst_used for obst_used in obsts_used if obst_used[0].lower() == obst_cli.lower()]
    nr_bars = len(obst_bars)

    fig, ax = plt.subplots(figsize=(10, 7))

    dy_obs, bar_width = bars_info(nr_arcs=nr_bars, logger=logger)

    # create colormap with nrcolors discrete colors
    bar_colors, title_font = amutils.create_colormap_font(nrcolors=nr_bars, font_size=12)

    for i, prn in enumerate(dprns[gnss]):
        dfprn = dfobs[dfobs['PRN'] == prn]
        for j, obst_used in enumerate(obst_bars):

            dfprnobst = dfprn[['DATE_TIME', obst_used]].copy()

            # dfprnobst['value'] = dfprnobst[obst_used].notna() * (y_prns[i] + dy_obs[j] * bar_width)
            # df[df['A'] > 2]['B'] = new_val  # new_val not set in df
            # df.loc[df['A'] > 2, 'B'] = new_val
            dfprnobst.loc[dfprnobst[obst_used].notna(), 'value'] = y_prns[i] + dy_obs[j]
            if i == 0:
                ax.plot(dfprnobst['DATE_TIME'], dfprnobst['value'], color=bar_colors[j], linewidth=4, label=obst_used)
            else:
                ax.plot(dfprnobst['DATE_TIME'], dfprnobst['value'], color=bar_colors[j], linewidth=4)

    # beautify plot
    ax.xaxis.grid(b=True, which='major')
    ax.yaxis.grid(b=True, which='major')
    ax.legend(loc='best', markerscale=4)

    # ax.set_xlabel('PRN', fontdict=title_font)
    ax.set_ylabel('PRNs', fontdict=title_font)
    ax.set_xlabel('Time', fontdict=title_font)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    # setticks on Y axis to represent the PRNs
    ax.yaxis.set_ticks(np.arange(0, len(dprns[gnss])))
    ax.set_yticklabels(dprns[gnss])

    # plot title
    plt.title('Observation timeline for GNSS {gnss:s} on {yy:02d}/{doy:03d}'.format(gnss=gnss, yy=(yyyy % 100), doy=doy))

    # create the ticks for the time axis
    dtFormat = plot_utils.determine_datetime_ticks(startDT=dfprn['DATE_TIME'].iloc[0], endDT=dfprn['DATE_TIME'].iloc[-1])

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
    plt_name = '{basen:s}-{gnss:s}-timeline.pdf'.format(basen=obstab_name.split('.')[0], gnss=gnss)
    fig.savefig(os.path.join(dir_gfzplt, plt_name), dpi=200)
    logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    return plt_name


def obstab_plot_observable(yyyy: int, doy: int, gnss: str, dfprnobst: pd.DataFrame, dir_gfzplt: str, obstab_name: str, dt_first: datetime, dt_last: datetime, show_plot: bool = False, logger: logging.Logger = None) -> str:
    """
    obstab_plot_observable plots the selected observable type
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    amutils.logHeadTailDataFrame(df=dfprnobst, dfName='dfprnobst[{gnss:s}]'.format(gnss=gnss), logger=logger, callerName=cFuncName)

    # set up the plot
    plt.style.use('ggplot')
    # plt.style.use('seaborn-darkgrid')

    # determine index of first obst
    idx_PRN = dfprnobst.columns.get_loc('PRN') + 1
    nr_obsts = len(dfprnobst.columns[idx_PRN:])

    # used markers
    lst_markers = ['o', 'x', '+', '.', ',', 'v', '^', '<', '>', 's', 'd']

    # create 2 subplots with same axis if more than 1 obst, else only 1 subplot
    if nr_obsts == 1:
        fig, ax1 = plt.subplots(1, figsize=(10, 4))
    else:
        fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(10, 7), gridspec_kw={'height_ratios': [2, 1]})

    # create colormap with nrcolors discrete colors which is th efirst always present plot
    obst_colors, title_font = amutils.create_colormap_font(nrcolors=nr_obsts, font_size=12)
    obst_markers = lst_markers[:nr_obsts]
    for obst, obst_color, marker in zip(dfprnobst.columns[idx_PRN:], obst_colors, obst_markers):
        ax1.plot(dfprnobst['DATE_TIME'], dfprnobst[obst], color=obst_color, label=obst, alpha=0.6, linestyle='', marker=marker, markersize=2)

    # beautify plot
    ax1.xaxis.grid(b=True, which='major')
    ax1.yaxis.grid(b=True, which='major')

    ax1.set_ylabel(gfzc.dict_obstypes[dfprnobst.columns[idx_PRN][0]], fontdict=title_font)
    # ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    ax1.legend(loc='best', markerscale=4)

    # setticks on Y axis to represent the PRNs
    if dfprnobst.columns[idx_PRN][0] == 'S':
        ax1.set_yticks(np.arange(10, 61, 10))

    # this will be the bottom axis if only 1 obst available
    axis = ax1

    # add difference plot when there are more than 1 obst available
    if nr_obsts > 1:
        # add difference between observables
        diff_colors = []
        for i, color in enumerate(amutils.get_spaced_colors(nr_obsts)):
            diff_colors.append(tuple(rgb / 256. for rgb in color))

        obst_diff_markers = lst_markers[:nr_obsts]

        dfprnobstdiff = pd.DataFrame(dfprnobst['DATE_TIME'])
        for i, obst1 in enumerate(dfprnobst.columns[idx_PRN:-1]):
            for j, obst2 in enumerate(dfprnobst.columns[idx_PRN + (i + 1):]):
                obst_diff = '{obst1:s}-{obst2:s}'.format(obst1=obst1, obst2=obst2)

                dfprnobstdiff[obst_diff] = dfprnobst[obst1] - dfprnobst[obst2]

                marker = obst_diff_markers[i * len(dfprnobst.columns[idx_PRN:-1]) + j]
                ax2.plot(dfprnobstdiff['DATE_TIME'], dfprnobstdiff[obst_diff], label=obst_diff, alpha=0.6, linestyle='', marker=marker, markersize=2)

        # beutify this plot
        if dfprnobst.columns[idx_PRN][0] == 'S':
            ax2.set_ylim([-10, +10])
        if dfprnobst.columns[idx_PRN][0] == 'C':
            ax2.set_ylim([-20, +20])
        ax2.set_ylabel('Diff {obst:s}'.format(obst=gfzc.dict_obstypes[dfprnobst.columns[idx_PRN][0]]), fontdict=title_font)

        # this will be the bottom axis if more than 1 obst available
        axis = ax2

    # plot title
    plt.suptitle('{obst:s} for PRN {prn:s} on {yy:02d}/{doy:03d}'.format(obst=gfzc.dict_obstypes[dfprnobst.columns[idx_PRN][0]], prn=dfprnobst['PRN'].iloc[0], yy=(yyyy % 100), doy=doy))

    # beautify plot
    axis.set_xlabel('Time', fontdict=title_font)
    axis.yaxis.grid(b=True, which='major')
    axis.legend(loc='best', markerscale=3)

    # create the ticks for the time axis
    axis.set_xlim([dt_first, dt_last])
    dtFormat = plot_utils.determine_datetime_ticks(startDT=dt_first, endDT=dt_last)

    if dtFormat['minutes']:
        # ax.xaxis.set_major_locator(dates.MinuteLocator(byminute=range(10, 60, 10), interval=1))
        pass
    else:
        axis.xaxis.set_major_locator(dates.HourLocator(interval=dtFormat['hourInterval']))   # every 4 hours
    axis.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))  # hours and minutes

    axis.xaxis.set_minor_locator(dates.DayLocator(interval=1))    # every day
    axis.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))

    axis.xaxis.set_tick_params(rotation=0)
    for tick in axis.xaxis.get_major_ticks():
        # tick.tick1line.set_markersize(0)
        # tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    fig.tight_layout()

    # save the plot in subdir png of GNSSSystem
    plt_name = '{basen:s}-{gnss:s}-{PRN:s}-{obst:s}.pdf'.format(basen=obstab_name.split('.')[0], gnss=gnss, PRN=dfprnobst['PRN'].iloc[0], obst=gfzc.dict_obstypes[dfprnobst.columns[idx_PRN][0]])
    fig.savefig(os.path.join(dir_gfzplt, plt_name), dpi=200)
    logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    # if show_plot:
    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    return plt_name
