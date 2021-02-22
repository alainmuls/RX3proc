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

    sys.exit(66)
