import os
from termcolor import colored
import logging
import sys
import glob

from ampyutils import am_config as amc
from ampyutils import amutils

__author__ = 'amuls'


def compress_rnx_obs(rnx2crz: str, obsf: str, rnxdir: str, logger: logging.Logger = None) -> str:
    """
    compress_rnx_obs compresses the observation file using RNX2CRZ
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # cmp_obsf = '{obs:s}D.Z'.format(obs=obsf[:-1])

    # create CLI line for RNX2CRZ
    args4RNX2CRZ = [rnx2crz, '-f', '-d', os.path.join(rnxdir, obsf)]

    if logger is not None:
        logger.info('{func:s}: Compressing RINEX observation {rnx:s}'.format(rnx=colored(obsf, 'green'), func=cFuncName))

    # run the program
    ret_code = amutils.run_subprocess(sub_proc=args4RNX2CRZ, logger=logger)
    if ret_code != amc.E_SUCCESS:
        if logger is not None:
            logger.info('{func:s}: RINEX rnx2crz compression failed with error: {errcode:d}'.format(func=cFuncName, errcode=ret_code))
        sys.exit(ret_code)
    else:
        # look for last created file
        return glob.glob(os.path.join(rnxdir, '*.Z'))[0]


def gzip_compress(gzip: str, ungzipf: str, dir: str, logger: logging.Logger = None) -> str:
    """
    gzip_compress compresses the rinex navigation file using gzip
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # create CLI line for GZIP compression
    args4GZIP = [gzip, '-f', os.path.join(dir, ungzipf)]

    if logger is not None:
        logger.info('{func:s}: Compressing RINEX navigation {rnx:s}'.format(rnx=colored(ungzipf, 'green'), func=cFuncName))

    # run the program
    ret_code = amutils.run_subprocess(sub_proc=args4GZIP, logger=logger)
    if ret_code != amc.E_SUCCESS:
        if logger is not None:
            logger.info('{func:s}: gzip navigation compression failed with error: {errcode:d}'.format(func=cFuncName, errcode=ret_code))
        sys.exit(ret_code)
    else:
        # look for last created file
        return glob.glob(os.path.join(dir, '*.gz'))[0]


def uncompress_rnx_obs(crz2rnx: str, rnx_dir: str, cmp_obsf: str, obs_ext: str = 'location.py', logger: logging.Logger = None) -> str:
    """
    uncompress_rnx_obs uncompresses the hatanaka compressed observation file
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    obsf = '{cmp_obsf:s}{obsext:s}'.format(cmp_obsf=cmp_obsf[:-3], obsext=obs_ext)

    # create CLI options for crz2rnx
    args4CRZ2RNX = [crz2rnx, '-f', os.path.join(rnx_dir, cmp_obsf)]

    if logger is not None:
        logger.info('{func:s}: hatanaka decompressing  RINEX observation {rnx:s}'.format(rnx=colored(cmp_obsf, 'green'), func=cFuncName))

    # run the program
    ret_code = amutils.run_subprocess(sub_proc=args4CRZ2RNX, logger=logger)
    if ret_code != amc.E_SUCCESS:
        if logger is not None:
            logger.info('{func:s}: RINEX Hatanaka decompression failed with error: {errcode:d}'.format(func=cFuncName, errcode=ret_code))
        sys.exit(ret_code)

    return obsf


def gzip_uncompress(gzip: str, gzipf: str, dir: str, logger: logging.Logger = None) -> str:
    """
    gzip_uncompress compresses the rinex navigation file using gzip
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    navf = '{nav:s}'.format(nav=gzipf[:-3])

    # create CLI line for GZIP compression
    args4GZIP = [gzip, '-d', '-f', os.path.join(dir, gzipf)]

    if logger is not None:
        logger.info('{func:s}: Decompressing file {rnx:s}'.format(rnx=colored(gzipf, 'green'), func=cFuncName))

    # run the program
    ret_code = amutils.run_subprocess(sub_proc=args4GZIP, logger=logger)
    if ret_code != amc.E_SUCCESS:
        if logger is not None:
            logger.info('{func:s}: gzip navigation decompression failed with error: {errcode:d}'.format(func=cFuncName, errcode=ret_code))
        sys.exit(ret_code)

    return navf

