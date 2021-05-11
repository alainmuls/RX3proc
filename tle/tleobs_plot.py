import os
import sys
from termcolor import colored
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
import datetime as dt
from matplotlib import dates
from typing import Tuple
from matplotlib.ticker import MultipleLocator, MaxNLocator
from math import ceil, floor

from ampyutils import amutils
from plot import plot_utils
from gfzrnx import gfzrnx_constants as gco

__author__ = 'amuls'


def tle_plot_arcs(marker: str,
                  obsf: str,
                  lst_PRNs: list,
                  dfTabObs: pd.DataFrame,
                  dfTleVis: pd.DataFrame,
                  dTime: dict,
                  show_plot: bool = False, logger: logging.Logger = None):
    """
    tle_plot_arcs plots the arcs caclculated by TLE for the GNSS
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    # find minimum time for tle_rise and maximum time for tle_set columns
    dt_rise = []
    dt_set = []
    for j, (t_rise, t_set) in enumerate(zip(dfTleVis.tle_rise, dfTleVis.tle_set)):
        if len(t_rise) > 0:
            dt_rise.append(t_rise[0])
        if len(t_set) > 0:
            dt_set.append(t_set[-1])

    dt_min = min(dt_rise)
    dt_max = max(dt_set)

    if logger is not None:
        logger.info('{func:s}: TLE time span {start:s} -> {end:s}'.format(start=dt_min.strftime('%H:%M:%S'),
                                                                          end=dt_max.strftime('%H:%M:%S'),
                                                                          func=cFuncName))

    gnss_id = dfTleVis.index.to_list()[0][0]
    y_prns = [int(prn[1:]) + 1 for prn in dfTleVis.index.to_list()]

    fig, ax = plt.subplots(figsize=(8, 6))

    # create colormap with nrcolors discrete colors
    prn_colors, title_font = amutils.create_colormap_font(nrcolors=len(y_prns), font_size=12)

    # get the date of this observation to combine with rise and set times
    cur_date = dTime['date'].date()

    for y_prn, prn_color, (prn, tle_prn) in zip(y_prns, prn_colors, dfTleVis.iterrows()):
        for tle_rise, tle_set in zip(tle_prn.tle_rise, tle_prn.tle_set):
            ax.plot_date(y=[y_prn, y_prn],
                         x=[dt.datetime.combine(cur_date, tle_rise),
                            dt.datetime.combine(cur_date, tle_set)],
                         linewidth=2,
                         color=prn_color,
                         linestyle='-',
                         markersize=6,
                         marker='|')
        for _, tle_cul in enumerate(tle_prn.tle_cul):
            if isinstance(tle_cul, dt.datetime.time):
                ax.plot_date(y=y_prn,
                             x=dt.datetime.combine(cur_date, tle_cul),
                             color=prn_color,
                             markersize=6,
                             marker='v')

    # beautify plot
    ax.xaxis.grid(b=True, which='major')
    ax.yaxis.grid(b=True, which='major')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=6, markerscale=4)

    # ax.set_xlabel('PRN', fontdict=title_font)
    ax.set_ylabel('PRNs', fontdict=title_font)
    ax.set_xlabel('TLE arcs', fontdict=title_font)

    # plot title
    plt.title('TLE arcs: {marker:s}, {gnss:s}, {date!s} ({yy:04d}/{doy:03d})'
              .format(marker=marker,
                      gnss=gco.dict_GNSSs[gnss_id],
                      yy=dTime['YYYY'],
                      doy=dTime['DOY'],
                      date=dTime['date'].strftime('%d/%m/%Y')))

    # create the ticks for the time ax
    ax.set_xlim([dt.datetime.combine(cur_date, dt_min),
                 dt.datetime.combine(cur_date, dt_max)])
    dtFormat = plot_utils.determine_datetime_ticks(startDT=dt.datetime.combine(cur_date, dt_min),
                                                   endDT=dt.datetime.combine(cur_date, dt_max))

    if dtFormat['minutes']:
        # ax.xaxis.set_major_locator(dates.MinuteLocator(byminute=range(10, 60, 10), interval=1))
        pass
    else:
        ax.xaxis.set_major_locator(dates.HourLocator(interval=dtFormat['hourInterval']))   # every 4 hours
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))  # hours and minutes

    ax.xaxis.set_minor_locator(dates.DayLocator(interval=1))    # every day
    ax.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))

    ax.xaxis.set_tick_params(rotation=0)
    for tick in ax.xaxis.get_major_ticks():
        # tick.tick1line.set_markersize(0)
        # tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')
    # setticks on Y axis to represent the PRNs
    ax.yaxis.set_ticks(np.arange(1, y_prns[-1] + 1))
    tick_labels = []
    for i in np.arange(0, y_prns[-1]):
        tick_prn = '{gnss:s}{prn:02d}'.format(gnss=gnss_id, prn=i)
        if tick_prn in dfTleVis.index.to_list():
            tick_labels.append(tick_prn)
        else:
            tick_labels.append('')

    ax.set_yticklabels(tick_labels)

    # fig.tight_layout()

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    for ext in ['png']:
        plt_name = os.path.join('png', '{basen:s}-TLEarcs.{ext:s}'.format(basen=obsf.split('.')[0], ext=ext))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))


def obstle_plot_obscount(marker: str,
                         obsf: str,
                         dfObsTle: pd.DataFrame,
                         dTime: dict,
                         show_plot: bool = False, logger: logging.Logger = None) -> str:
    """
    obstle_plot_arcs plots count of observations wrt to number obtained from TLE
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    fig, ax = plt.subplots(figsize=(8, 6))

    gnss_id = dfObsTle.PRN.iloc[0][0]
    y_prns = [int(prn[1:]) for prn in dfObsTle.PRN.to_list()]

    # select the columns used for plotting
    col_names = dfObsTle.columns.tolist()
    obstypes = [x for x in col_names[col_names.index('PRN') + 1:]]

    # determine widths of bars to use for each PRN
    dy_obstypes, bar_width = bars_info(nr_arcs=len(obstypes), logger=logger)

    # create colormap with nrcolors discrete colors
    bar_colors, title_font = amutils.create_colormap_font(nrcolors=len(obstypes), font_size=12)

    # plot the TLE observation count
    for i, (y_prn, prn) in enumerate(zip(y_prns, dfObsTle.PRN)):
        for j, (obst, dy_obst, bar_color) in enumerate(zip(list(reversed(obstypes)),
                                                           list(reversed(dy_obstypes)),
                                                           list(reversed(bar_colors)))):
            prn_width = dfObsTle.iloc[i][obst]
            if i == 0:
                ax.barh(y=y_prn + dy_obst,
                        width=prn_width,
                        height=bar_width,
                        color=bar_color,
                        label=obst)
            else:
                ax.barh(y=y_prn + dy_obst,
                        width=prn_width,
                        height=bar_width,
                        color=bar_color)

    # beautify plot
    ax.xaxis.grid(b=True, which='major')
    ax.yaxis.grid(b=False)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=6, markerscale=4)

    # ax.set_xlabel('PRN', fontdict=title_font)
    ax.set_ylabel('PRNs', fontdict=title_font)
    ax.set_xlabel('Observations Count [-]', fontdict=title_font)

    # plot title
    plt.title('Observations vs TLE: {marker:s}, {gnss:s}, {date!s} ({yy:04d}/{doy:03d})'
              .format(marker=marker,
                      gnss=gco.dict_GNSSs[gnss_id],
                      yy=dTime['YYYY'],
                      doy=dTime['DOY'],
                      date=dTime['date'].strftime('%d/%m/%Y')))

    # setticks on Y axis to represent the PRNs
    _, xlim_right = ax.get_xlim()
    ylim_left, ylim_right = ax.get_ylim()
    for i in np.arange(int(ylim_left), int(ylim_right)):
        if i % 2 == 0:
            ax.barh(y=i, height=1, width=xlim_right, color='black', alpha=0.1)

    ax.yaxis.set_ticks(np.arange(1, y_prns[-1] + 1))
    tick_labels = []
    for i in np.arange(1, y_prns[-1] + 1):
        tick_prn = '{gnss:s}{prn:02d}'.format(gnss=gnss_id, prn=i)
        if tick_prn in dfObsTle.PRN.to_list():
            tick_labels.append(tick_prn)
        else:
            tick_labels.append('')

    ax.set_yticklabels(tick_labels)
    fig.tight_layout()

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    for ext in ['png']:
        plt_name = os.path.join('png', '{basen:s}-ObsTLE.{ext:s}'.format(basen=obsf.split('.')[0], ext=ext))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    return plt_name


def bars_info(nr_arcs: int,
              logger: logging.Logger) -> Tuple[list, int]:
    """
    bars_info determines the width of an individual bar, the spaces between the arc bars, and localtion in delta-x-coordinates of beginning of each PRN arcs
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')
    logger.info('{func:s}: determining the information for the bars'.format(func=cFuncName))

    # the bars for all arcs for 1 PRN may span over 0.8 units (from [-0.4 => 0.4]), including the spaces between the different arcs
    width_all_arcs = 0.8
    dx_start = -0.4  # start of the bars relative to integer of PRN
    width_space = 0.02  # space between the different arcs for 1 PRN

    # substract width-spaces needed for nr_arcs
    width_arcs = width_all_arcs - (nr_arcs - 1) * width_space

    # the width taken by 1 arc for 1 prn is
    width_arc = width_arcs / nr_arcs

    # get the delta-x to apply to the integer value that corresponds to a PRN
    # print('np.arange(nr_arcs) = {}'.format(np.arange(nr_arcs)))
    dx_obs = [dx_start + i * (width_space + width_arc) for i in np.arange(nr_arcs)]
    # print('\nnr_arcs = {}'.format(nr_arcs))
    # print('width_arcs = {}'.format(width_arcs))
    # print('dx_obs = {}'.format(dx_obs))
    # print('width_arc = {}'.format(width_arc))


    return dx_obs, width_arc


def obstle_plot_relative(marker: str,
                         obsf: str,
                         dfObsTle: pd.DataFrame,
                         dTime: dict,
                         show_plot: bool = False, logger: logging.Logger = None) -> str:
    """
    obstle_plot_relativeobsf plots the percenatge of observations observed wrt the TLE determined max values.
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    fig, ax = plt.subplots(figsize=(8, 6))

    gnss_id = dfObsTle.PRN.iloc[0][0]
    x_prns = [int(prn[1:]) for prn in dfObsTle.PRN.to_list()]
    x_crds = np.arange(1, 38)

    # select the columns used for plotting
    col_names = dfObsTle.columns.tolist()
    obstypes = [x for x in col_names[col_names.index('PRN') + 1:]]

    # create colormap with nrcolors discrete colors
    colors, title_font = amutils.create_colormap_font(nrcolors=len(obstypes[:-1]), font_size=12)
    # used markers
    lst_markers = ['o', 'v', '^', '<', '>', 'x', '+', 's', 'd', '.', ',']

    # create an offset to plot the markers per PRN
    # print('obstypes[:-1] = {}'.format(obstypes[:-1]))
    # print('len(obstypes[:-1]) = {}'.format(len(obstypes[:-1])))
    dx_obs, dx_width = bars_info(nr_arcs=len(obstypes[:-1]), logger=logger)
    # print('dx_obs = {}'.format(dx_obs))
    # print('dx_width = {}'.format(dx_width))
    # print('x_prns = {}'.format(x_prns))

    # store the percantages in a dict
    for j, (obst, color, plotmarker) in enumerate(zip(list(reversed(obstypes[:-1])), list(reversed(colors)), lst_markers)):
        obs_percentages = [np.NaN] * 37

        # print('j = {}'.format(j))
        # print('dx_width = {}'.format(dx_width))

        for i, (x_prn, prn) in enumerate(zip(x_prns, dfObsTle.PRN)):
            tle_maxobs = dfObsTle.iloc[i][obstypes[-1]] / 100
            if tle_maxobs != 0:
                obs_perc = dfObsTle.iloc[i][obst] / tle_maxobs
                obs_percentages[x_prn] = obs_perc
            else:
                obs_percentages[x_prn] = np.NaN

            # print('\nj = {}'.format(j))
            # print('prn = {}'.format(prn))
            # print('x_prn = {}'.format(x_prn))
            # print('dx_width = {}'.format(dx_width))
            # print('dx_obs[j] = {}'.format(dx_obs[j]))
            # print('x_prn + dx_obs[j] = {}'.format(x_prn + dx_obs[j]))
            # print('x_prn + dx_obs[j]  + j * dx_width / len(dx_obs) = {}'.format(x_prn + dx_obs[j] + j * dx_width / len(dx_obs)))
            # print('x_prn + dx_obs[j] * j + j * dx_width / len(dx_obs) = {}'.format(x_prn + dx_obs[j] * j + j * dx_width / len(dx_obs)))
            # print('x_prn + dx_obs[j] + j * dx_width = {}'.format(x_prn + dx_obs[j] + j * dx_width))
            # print('x_prn + dx_obs[j] = {}'.format(x_prn + dx_obs[j]))

            # plot the current percentages per PRN and per OBST
            if i == 0:
                ax.bar(x=x_prn + dx_obs[j],
                       height=obs_perc,
                       width=dx_width,
                       color=color,
                       label=obst,
                       align='center')
            else:
                ax.bar(x=x_prn + dx_obs[j],
                       height=obs_perc,
                       width=dx_width,
                       color=color,
                       align='center')


    # beautify plot
    ax.xaxis.grid(b=False)
    ax.yaxis.grid(b=True, which='both')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=6, markerscale=2)

    ax.yaxis.grid(True)
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.grid(which="minor", color='black', linestyle='-.', linewidth=5)

    # ax.set_xlabel('PRN', fontdict=title_font)
    ax.set_xlabel('PRNs', fontdict=title_font)
    ax.set_ylabel('Observations relative to TLE [-]', fontdict=title_font)

    # plot title
    plt.title('Relative Observations: {marker:s}, {gnss:s}, {date!s} ({yy:04d}/{doy:03d})'
              .format(marker=marker,
                      gnss=gco.dict_GNSSs[gnss_id],
                      yy=dTime['YYYY'],
                      doy=dTime['DOY'],
                      date=dTime['date'].strftime('%d/%m/%Y')))

    # setticks on X axis to represent the PRNs
    # print('\nx_crds[-1] = {}'.format(x_crds[-1]))
    ax.xaxis.set_ticks(np.arange(0, x_crds[-1]))
    tick_labels = []
    for i in np.arange(0, x_crds[-1]):
        # create a grey bar for separating between PRNs
        if i % 2 == 0:
            ax.bar(i, 100, width=1, color='black', alpha=0.05)

        tick_prn = '{gnss:s}{prn:02d}'.format(gnss=gnss_id, prn=i)
        # print('tick_prn[{}] = {}'.format(i, tick_prn))

        if tick_prn in dfObsTle.PRN.to_list():
            tick_labels.append(tick_prn)
        else:
            tick_labels.append('')

    ax.set_xticklabels(tick_labels, rotation=90, horizontalalignment='center')
    fig.tight_layout()

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    for ext in ['png']:
        plt_name = os.path.join('png', '{basen:s}-PERC.{ext:s}'.format(basen=obsf.split('.')[0], ext=ext))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    return plt_name


def obstle_plot_arcs_prns(marker: str,
                          obsf: str,
                          dTime: dict,
                          navsig_name: str,
                          lst_PRNs: list,
                          dfNavSig: pd.DataFrame,
                          dfTleVis: pd.DataFrame,
                          show_plot: bool = False,
                          logger: logging.Logger = None) -> str:
    """
    obstle_plot_arcs_prns plots the arcs caclculated by TLE for the GNSS and selected PRNs
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    # get min and max times according the observation smade
    amutils.logHeadTailDataFrame(df=dfNavSig, dfName='dfNavSig', callerName=cFuncName, logger=logger)
    amutils.logHeadTailDataFrame(df=dfTleVis, dfName='dfTleVis', callerName=cFuncName, logger=logger)

    # create colormap with 36 discrete colors
    max_prn = 36
    prn_colors, title_font = amutils.create_colormap_font(nrcolors=max_prn, font_size=12)

    # subplots
    fig, ax = plt.subplots(figsize=(12.0, 8.0))
    # print('dTime = {}'.format(dTime))
    fig.suptitle('{marker:s} - {navs:s} - {date:s} ({yy:04d}/{doy:03d} - Obs vs TLE)'.format(
                 marker=marker,
                 date='{date:s}'.format(date=dTime['date'].strftime('%d/%m/%Y')),
                 navs=navsig_name,
                 yy=dTime['YYYY'],
                 doy=dTime['DOY']),
                 fontdict=title_font,
                 fontsize=18)

    # PLOT PRN ARCS FROM OBSERVED AND TLE
    for prn in lst_PRNs:
        y_prn = int(prn[1:]) - 1

        # get the lists with rise / set times as observed
        # for dt_obs_rise, dt_obs_set in zip(dfTleVis.loc[prn]['obs_rise'], dfTleVis.loc[prn]['obs_set']):
        #     ax.plot_date([dt_obs_rise, dt_obs_set], [y_prn, y_prn], linestyle='solid', color=prn_colors[y_prn], linewidth=2, marker='v', markersize=4, alpha=1)

        # get the lists with rise / set times by TLEs
        for tle_rise, tle_set, tle_cul in zip(dfTleVis.loc[prn]['tle_rise'],
                                              dfTleVis.loc[prn]['tle_set'],
                                              dfTleVis.loc[prn]['tle_cul']):
            ax.plot_date([dt.datetime.combine(dfNavSig.DATE_TIME.iloc[0], tle_rise),
                          dt.datetime.combine(dfNavSig.DATE_TIME.iloc[0], tle_set)],
                         [y_prn, y_prn],
                         linestyle='-',
                         color=prn_colors[y_prn],
                         linewidth=11,
                         marker='|',
                         markersize=16,
                         alpha=0.3)

            # add a indicator for the culmination time of PRN
            if isinstance(tle_cul, dt.time):
                ax.plot(dt.datetime.combine(dfNavSig.DATE_TIME.iloc[0], tle_cul),
                        y_prn,
                        marker='^',
                        markersize=13,
                        alpha=0.3,
                        color=prn_colors[y_prn])

        # get the data for this particular PRN out of dfNavSig
        dfPrnObs = dfNavSig[dfNavSig['PRN'] == prn]
        ax.plot(dfPrnObs['DATE_TIME'],
                [y_prn] * dfPrnObs.shape[0],
                linestyle='',
                marker='.',
                markersize=6,
                color=prn_colors[y_prn])

    # format the date time ticks
    # ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    # ax.xaxis.set_major_formatter(dates.DateFormatter('\n%d-%m-%Y'))

    # ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    # ax.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M:%S'))
    # plt.xticks()

    # create the ticks for the time ax
    ax.set_xlim([dTime['start'], dTime['end']])
    dtFormat = plot_utils.determine_datetime_ticks(startDT=dTime['start'], endDT=dTime['end'])

    if dtFormat['minutes']:
        # ax.set_major_locator(dates.MinuteLocator(byminute=range(10, 60, 10), interval=1))
        pass
    else:
        ax.xaxis.set_major_locator(dates.HourLocator(interval=dtFormat['hourInterval']))   # every 4 hours
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))  # hours and minutes

    ax.xaxis.set_minor_locator(dates.DayLocator(interval=1))    # every day
    ax.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))

    ax.xaxis.set_tick_params(rotation=0)
    for tick in ax.xaxis.get_major_ticks():
        # tick.tick1line.set_markersize(0)
        # tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    # format the y-ticks to represent the PRN number
    plt.yticks(np.arange(0, max_prn))
    prn_ticks = [''] * max_prn

    # get list of observed PRN numbers (without satsyst letter)
    prn_nrs = [int(prn[1:]) for prn in dfTleVis.index]

    # and the corresponding ticks
    for prn_nr, prn_txt in zip(prn_nrs, dfTleVis.index):
        prn_ticks[prn_nr - 1] = prn_txt
    # ax.yaxis.set_major_locator(mticker.FixedLocator(prn_ticks))

    # adjust color for y ticks
    # ax.yaxis.set_major_locator(ticker.FixedLocator(np.arange(0, max_prn)))
    for color, tick in zip(prn_colors, ax.yaxis.get_major_ticks()):
        tick.label1.set_color(color)  # set the color property
        tick.label1.set_fontweight('bold')
    # print('prn_ticks = {}'.format(prn_ticks))
    ax.set_yticks(np.arange(0, max_prn))
    ax.set_yticklabels(prn_ticks)

    # set the axis labels
    ax.set_xlabel('Time', fontdict=title_font)
    ax.set_ylabel('PRN', fontdict=title_font)

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    for ext in ['png']:
        plt_name = os.path.join('png', '{basen:s}-{navs:s}-TLE-arcs.{ext:s}'.format(basen=obsf.split('.')[0], navs=navsig_name, ext=ext))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    return plt_name


def plot_prn_navsig_obs(marker: str,
                        dTime: dict,
                        obsf: str,
                        prn: str,
                        dfPrnObst: pd.DataFrame,
                        dfTleVisPrn: pd.DataFrame,
                        df_PRNElev: pd.DataFrame,
                        dfJam: pd.DataFrame,
                        obst: str,
                        posidx_gaps: list,
                        snrth: float,
                        show_plot: bool = False,
                        logger: logging.Logger = None) -> str:
    """
    plot_prn_navsig_obs plots for a given PRN the observation OBST for a navigation signal (with the exponential moving average)
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    amutils.logHeadTailDataFrame(df=dfPrnObst, dfName='dfPrnObst', callerName=cFuncName, logger=logger)
    amutils.logHeadTailDataFrame(df=dfTleVisPrn, dfName='dfTleVisPrn', callerName=cFuncName, logger=logger)

    # sys.exit(98)

    # used markers
    lst_markers = ['o', 'x', '+', '.', ',', 'v', '^', '<', '>', 's', 'd']
    lst_colors, title_font = amutils.create_colormap_font(nrcolors=1, font_size=12)

    if obst[0] == 'S':  # more detailed plot for SNR analysis
        fig = plt.figure(figsize=(12, 7))
        gs = fig.add_gridspec(nrows=3, hspace=0.1, height_ratios=[8, 3, 1])
        axObst, axSNR, axTLE = gs.subplots(sharex=True)
        # fig, (axObst, axSNR) = plt.subplots(2, sharex=True, figsize=(8, 6), )
    else:
        fig = plt.figure(figsize=(9, 7))
        gs = fig.add_gridspec(nrows=2, hspace=0.1, height_ratios=[11, 1])
        axObst, axTLE = gs.subplots(sharex=True)

    # print('posidx_gaps = {}'.format(posidx_gaps))
    # plot on axObst the curves, on axSNR difference with previous value (only for SNR) and TLE on axTLE
    for plot_marker, color in zip(lst_markers[:1], lst_colors):
        # go over the time intervals
        for posidx_start, posidx_stop in zip(posidx_gaps[:-1], posidx_gaps[1:]):
            dfTimeSegment = dfPrnObst.iloc[posidx_start:posidx_stop]
            # print('dfTimeSegment = \n{}'.format(dfTimeSegment))

            axObst.plot(dfTimeSegment['DATE_TIME'],
                        dfTimeSegment[obst],
                        linestyle='--', dashes=(1, 2), marker=plot_marker, markersize=2, color='blue')

            if obst[0] == 'S':
                axSNR.fill_between(dfTimeSegment['DATE_TIME'], -snrth, +snrth,
                                   color='black', alpha=0.20, linestyle='-')
                axSNR.plot(dfTimeSegment['DATE_TIME'],
                           dfTimeSegment['d{obst:s}'.format(obst=obst)],
                           linestyle='--', dashes=(1, 2), marker=plot_marker, markersize=2, color='blue')

    # plot the SINR against time on second y-axis for the axPRNcnt plot
    if len(dfJam.index) > 0:
        jam_min = 5 * floor(dfJam['SINR [dB]'].min() / 5)
        jam_max = 5 * ceil(dfJam['SINR [dB]'].max() / 5)

        axJam = axObst.twinx()
        axJam.fill_between(dfJam['DATE_TIME'],
                           y1=dfJam['SINR [dB]'], y2=0,
                           step='post',
                           color='red', alpha=0.2,
                           linewidth=2, linestyle='-')
        axJam.set_ylim([jam_min, jam_max])
        axJam.set_ylabel('SINR [dB]')

    # read in the timings for the TLE of this PRN
    for tle_rise, tle_set, tle_cul in zip(dfTleVisPrn['tle_rise'], dfTleVisPrn['tle_set'], dfTleVisPrn['tle_cul']):
        axTLE.plot_date([dt.datetime.combine(dfPrnObst.DATE_TIME.iloc[0], tle_rise),
                         dt.datetime.combine(dfPrnObst.DATE_TIME.iloc[0], tle_set)],
                        [1, 1],
                        linestyle='-', linewidth=9, marker='')

        # add a tick at culmination point
        if isinstance(tle_cul, dt.time):
            axTLE.plot(dt.datetime.combine(dfPrnObst.DATE_TIME.iloc[0], tle_cul),
                       1,
                       marker='v', markersize=14)

    # print the elevation values at the according time
    # ax.text(x=x_text_annotation, y=670000, s='Holiday in US', alpha=0.7, color='#334f8d')
    for ind in df_PRNElev.index:
        axTLE.text(x=df_PRNElev.loc[ind].DATE_TIME,
                   y=1,
                   s=df_PRNElev.loc[ind].elevation,
                   horizontalalignment='center',
                   fontweight='heavy',
                   rotation='vertical')

    # create title
    fig.suptitle('{marker:s}: {obst:s} for {prn:s} @ {dt:s} ({yyyy:04d}/{doy:03d})'.format(marker=marker, obst=obst, prn=prn, dt=dTime['date'].strftime('%d/%m/%Y'), yyyy=dTime['YYYY'], doy=dTime['DOY']))

    # beautify plot
    axObst.xaxis.grid(b=True, which='both')
    axObst.yaxis.grid(b=True, which='both')
    axObst.set_ylabel('{obst:s} [dBHz]'.format(obst=obst))

    if obst.startswith('S'):  # SNR displayed
        axObst.set_ylim([15, 55])

        axSNR.xaxis.grid(b=True, which='both')
        axSNR.yaxis.grid(b=True, which='both')
        axSNR.set_ylabel('d({snr:s})'.format(snr=obst))

        # print(dfPrnObst)
        # print(dfPrnObst['d{obst:s}'.format(obst=obst)])
        # print(type(dfPrnObst['d{obst:s}'.format(obst=obst)]))
        # print(dfPrnObst['d{obst:s}'.format(obst=obst)].abs())
        # print('max = {}'.format(dfPrnObst['d{obst:s}'.format(obst=obst)].abs().max()))
        ylim = max(3 * snrth, ceil(dfPrnObst['d{obst:s}'.format(obst=obst)].abs().max()))
        axSNR.set_ylim([-ylim, +ylim])

    axTLE.xaxis.grid(b=True)
    axTLE.yaxis.grid(b=False)
    axTLE.tick_params(left=False)
    axTLE.get_yaxis().set_ticklabels([])
    axTLE.set_ylabel('TLE span')

    # create the ticks for the time ax
    axTLE.set_xlim([dTime['start'], dTime['end']])
    dtFormat = plot_utils.determine_datetime_ticks(startDT=dTime['start'], endDT=dTime['end'])

    if dtFormat['minutes']:
        # ax.xaxis.set_major_locator(dates.MinuteLocator(byminute=range(10, 60, 10), interval=1))
        pass
    else:
        axTLE.xaxis.set_major_locator(dates.HourLocator(interval=dtFormat['hourInterval']))   # every 4 hours
    axTLE.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))  # hours and minutes

    axTLE.xaxis.set_minor_locator(dates.DayLocator(interval=1))    # every day
    axTLE.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))

    axTLE.xaxis.set_tick_params(rotation=0)
    for tick in axTLE.xaxis.get_major_ticks():
        # tick.tick1line.set_markersize(0)
        # tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    # save the plot in subdir png
    amutils.mkdir_p('png')
    for ext in ['png']:
        tmp_name = '{basen:s}-{obst:s}-{prn:s}.{ext:s}'.format(basen=os.path.basename(obsf).split('.')[0], ext=ext, obst=obst, prn=prn)
        plt_name = os.path.join('png', tmp_name)
        # print('plt_name = {}'.format(plt_name))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)

    return plt_name


def obstle_plot_gnss_obst(marker: str,
                          obsf: str,
                          dTime: dict,
                          navsig_name: str,
                          lst_PRNs: list,
                          dfNavSig: pd.DataFrame,
                          dfNavSigPRNcnt: pd.DataFrame,
                          navsig_obst_lst: list,
                          dfJam: pd.DataFrame,
                          dfTleVis: pd.DataFrame,
                          show_plot: bool = False,
                          logger: logging.Logger = None) -> dict:
    """
    obstle_plot_gnss_obst plots for a GNSS the selected obst for all selected PRNs on 1 plot
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    # used markers
    max_prn = 36
    lst_colors, title_font = amutils.create_colormap_font(nrcolors=max_prn, font_size=12)

    # return plot names created
    lst_pltnames = {}

    # get the date of observations
    cur_date = dfNavSig.DATE_TIME.iloc[0]

    # plot per obst all PRN  for this navigation signal
    for obst in navsig_obst_lst:
        fig = plt.figure(figsize=(10, 7))
        gs = fig.add_gridspec(nrows=3, hspace=0.1, height_ratios=[9, 3, 3])
        axObst, axPRNcnt, axTLE = gs.subplots(sharex=True)

        # retain only the current obst in dataframe
        dfNavSigObst = dfNavSig[['DATE_TIME', 'PRN', obst]]
        for prn, prn_color in zip(lst_PRNs, lst_colors[:len(lst_PRNs)]):
            dfNavSigObstPRN = dfNavSigObst[(dfNavSigObst['PRN'] == prn)]
            amutils.logHeadTailDataFrame(df=dfNavSigObstPRN, dfName='dfNavSigObstPRN', callerName=cFuncName, logger=logger)

            axObst.plot(dfNavSigObstPRN['DATE_TIME'],
                        dfNavSigObstPRN[obst],
                        linestyle='--', dashes=(1, 2), marker='.', markersize=2,
                        color=prn_color, label=prn)

            # read in the timings for the TLE of this PRN
            dfTlePrn = dfTleVis.loc[prn]
            iPRN = int(prn[1:])
            for tle_rise, tle_set, tle_cul in zip(dfTlePrn['tle_rise'], dfTlePrn['tle_set'], dfTlePrn['tle_cul']):
                # print('prn = {}'.format(prn))
                # print('tle_rise = {}'.format(tle_rise))
                # print('tle_set = {}'.format(tle_set))
                # print('tle_cul = {}'.format(tle_cul))
                # print('cur_date = {}'.format(cur_date))

                axTLE.plot_date([dt.datetime.combine(cur_date, tle_rise),
                                 dt.datetime.combine(cur_date, tle_set)],
                                [iPRN, iPRN],
                                linestyle='-', linewidth=2, marker='', color=prn_color)

                # add a tick at culmination point
                if isinstance(tle_cul, dt.time):
                    axTLE.plot(dt.datetime.combine(cur_date, tle_cul),
                               iPRN,
                               marker='v', markersize=3, color=prn_color)

        # display the number of PRNs still observed
        axPRNcnt.plot(dfNavSigPRNcnt[dfNavSigPRNcnt.PRNcnt >= 4].DATE_TIME,
                      dfNavSigPRNcnt[dfNavSigPRNcnt.PRNcnt >= 4].PRNcnt,
                      color='green',
                      linestyle='', marker='.', markersize=2)
        axPRNcnt.plot(dfNavSigPRNcnt[dfNavSigPRNcnt.PRNcnt < 4].DATE_TIME,
                      dfNavSigPRNcnt[dfNavSigPRNcnt.PRNcnt < 4].PRNcnt,
                      color='red',
                      linestyle='', marker='.', markersize=2)

        # set integer ticks
        axPRNcnt.yaxis.set_major_locator(MaxNLocator(integer=True))
        # axPRNcnt.set_ylim([0, dfNavSigPRNcnt.PRNcnt.max() + 1])
        y_ticks = np.arange(0, dfNavSigPRNcnt.PRNcnt.max() + 1, int(dfNavSigPRNcnt.PRNcnt.max() / 5 + 1))
        axPRNcnt.set_yticks(y_ticks)
        axPRNcnt.set_ylabel('PRN count [-]')

        # plot the SINR against time on second y-axis for the axPRNcnt plot
        if len(dfJam.index) > 0:
            jam_min = 5 * floor(dfJam['SINR [dB]'].min() / 5)
            jam_max = 5 * ceil(dfJam['SINR [dB]'].max() / 5)

            axJam = axObst.twinx()
            axJam.fill_between(dfJam['DATE_TIME'],
                               y1=dfJam['SINR [dB]'], y2=0,
                               step='post',
                               color='red', alpha=0.2,
                               linewidth=2, linestyle='-')
            axJam.set_ylim([jam_min, jam_max])
            axJam.set_ylabel('SINR [dB]')

        # create title
        fig.suptitle('{marker:s}: {obst:s} for {navsig:s} @ {dt:s} ({yyyy:04d}/{doy:03d})'.format(marker=marker, obst=obst, navsig=navsig_name, dt=dTime['date'].strftime('%d/%m/%Y'), yyyy=dTime['YYYY'], doy=dTime['DOY']))

        # axObst.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fancybox=True, shadow=True, ncol=6, markerscale=4)
        axObst.legend(bbox_to_anchor=(1.03, 0), loc='upper left', markerscale=4, fancybox=True, shadow=True, fontsize='x-small')

        # beautify plot
        axObst.xaxis.grid(b=True, which='both')
        axObst.yaxis.grid(b=True, which='both')
        axObst.set_ylabel('{obst:s} [dBHz]'.format(obst=obst))

        if obst.startswith('S'):  # SNR displayed
            axObst.set_ylim([15, 55])

        axTLE.xaxis.grid(b=True)
        axTLE.yaxis.grid(b=False)
        axTLE.tick_params(left=False)
        axTLE.get_yaxis().set_ticklabels([])
        axTLE.set_ylabel('TLE span')

        # create the ticks for the time ax
        axTLE.set_xlim([dTime['start'], dTime['end']])
        dtFormat = plot_utils.determine_datetime_ticks(startDT=dTime['start'], endDT=dTime['end'])

        if dtFormat['minutes']:
            # ax.xaxis.set_major_locator(dates.MinuteLocator(byminute=range(10, 60, 10), interval=1))
            pass
        else:
            axTLE.xaxis.set_major_locator(dates.HourLocator(interval=dtFormat['hourInterval']))   # every 4 hours
        axTLE.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))  # hours and minutes

        axTLE.xaxis.set_minor_locator(dates.DayLocator(interval=1))    # every day
        axTLE.xaxis.set_minor_formatter(dates.DateFormatter('\n%d-%m-%Y'))

        axTLE.xaxis.set_tick_params(rotation=0)
        for tick in axTLE.xaxis.get_major_ticks():
            # tick.tick1line.set_markersize(0)
            # tick.tick2line.set_markersize(0)
            tick.label1.set_horizontalalignment('center')

        # save the plot in subdir png
        amutils.mkdir_p('png')
        for ext in ['png']:
            tmp_name = '{basen:s}-{navsig:s}-{obst:s}.{ext:s}'.format(basen=os.path.basename(obsf).split('.')[0], ext=ext, obst=obst, navsig=navsig_name)

            plt_name = os.path.join('png', tmp_name)
            # print('plt_name = {}'.format(plt_name))
            fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
            logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

            lst_pltnames[obst] = plt_name

        if show_plot:
            plt.show(block=True)
        else:
            plt.close(fig)

    return lst_pltnames
