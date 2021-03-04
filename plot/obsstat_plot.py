import os
import sys
from termcolor import colored
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
import matplotlib.ticker as ticker
from typing import Tuple

from ampyutils import amutils

__author__ = 'amuls'


def obsstat_plot_obscount(obs_statf: str, gnss: str, gfzrnx: str, show_plot: bool = False, logger: logging.Logger = None):
    """
    obsstat_plot_obscount plots the number of observables per PRN for this gnss
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # set up the plot
    plt.style.use('ggplot')

    # read the observation statistics file into dataframe
    df_obsstat = pd.read_csv(obs_statf, header=0, delim_whitespace=True)  # skiprows
    amutils.logHeadTailDataFrame(df=df_obsstat, dfName='df_obsstat', logger=logger, callerName=cFuncName)

    # get the number of SVs and the observation types for Cxx only
    lst_prns = df_obsstat.PRN.unique()

    # get the list of observables
    lst_cols = df_obsstat.columns.tolist()
    lst_obst = [x for x in lst_cols[lst_cols.index('PRN') + 1:] if x.startswith('C')]
    nr_bars = len(lst_obst)

    # set up the plot
    plt.style.use('ggplot')
    # plt.style.use('seaborn-darkgrid')

    # determine how many PRNs are observed used as y coordinate
    y_prns = np.arange(len(lst_prns))  # location of the PRNs

    fig, ax = plt.subplots(figsize=(8, 6))

    dy_obs, bar_width = bars_info(nr_arcs=nr_bars, logger=logger)

    # create colormap with nrcolors discrete colors
    bar_colors, title_font = amutils.create_colormap_font(nrcolors=nr_bars, font_size=12)

    for i, prn in enumerate(lst_prns):
        for j, obst_used in enumerate(lst_obst):
            if i == 0:
                ax.barh(y=y_prns[i] + dy_obs[j], width=df_obsstat[df_obsstat.PRN == prn][obst_used], height=bar_width, color=bar_colors[j], label=obst_used)
            else:
                ax.barh(y=y_prns[i] + dy_obs[j], width=df_obsstat[df_obsstat.PRN == prn][obst_used], height=bar_width, color=bar_colors[j])

    # beautify plot
    ax.xaxis.grid(b=True, which='major')
    ax.yaxis.grid(b=True, which='major')
    ax.legend(loc='best', markerscale=4)

    # ax.set_xlabel('PRN', fontdict=title_font)
    ax.set_ylabel('PRNs', fontdict=title_font)
    ax.set_xlabel('# observations [-]', fontdict=title_font)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

    # setticks on Y axis to represent the PRNs
    ax.yaxis.set_ticks(np.arange(0, len(lst_prns)))
    ax.set_yticklabels(lst_prns)

    # plot title
    yyyy = int(obs_statf[12:16])
    doy = int(obs_statf[17:20])
    marker = obs_statf[0:4]
    plt.title('{mark:s}: Observations count for GNSS {gnss:s} on {yy:04d}/{doy:03d}'.format(gnss=gnss, yy=yyyy, doy=doy, mark=marker))

    fig.tight_layout()

    # save the plot in subdir png of GNSSSystem
    amutils.mkdir_p('png')
    for ext in ['pdf', 'png', 'eps']:
        plt_name = os.path.join('png', '{basen:s}-{gnss:s}-obscount.{ext:s}'.format(basen=obs_statf.split('.')[0], gnss=gnss, ext=ext))
        fig.savefig(plt_name, dpi=150, bbox_inches='tight', format=ext)
        logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(plt_name, 'green')))

    if show_plot:
        plt.show(block=True)
    else:
        plt.close(fig)


def bars_info(nr_arcs: int, logger: logging.Logger = None) -> Tuple[list, int]:
    """
    bars_info determines the width of an individual bar, the spaces between the arc bars, and localtion in delta-x-coordinates of beginning of each PRN arcs
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')
    if logger is not None:
        logger.info('{func:s}: determining the information for the bars'.format(func=cFuncName))

    # the bars for all arcs for 1 PRN may span over 0.8 units (from [-0.4 => 0.4]), including the spaces between the different arcs
    width_prn_arcs = 0.8
    dx_start = -0.4  # start of the bars relative to integer of PRN
    width_space = 0.1  # space between the different arcs for 1 PRN

    # substract width-spaces needed for nr_arcs
    width_arcs = width_prn_arcs - (nr_arcs - 1) * width_space

    # the width taken by 1 arc for 1 prn is
    width_arc = width_arcs / nr_arcs

    # get the delta-x to apply to the integer value that corresponds to a PRN
    dx_obs = [dx_start + i * (width_space + width_arc) for i in np.arange(nr_arcs)]

    return dx_obs, width_arc
