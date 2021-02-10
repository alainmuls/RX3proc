
import os
import sys
from termcolor import colored
from pylatex.utils import NoEscape
from nested_lookup import nested_lookup
from datetime import datetime
import logging
from pylatex import Document, Section

from ampyutils import am_config as amc
from ltx import ltx_report, ltx_obstab_reporting, ltx_titlepage, ltx_navtab_reporting


def report_information(logger: logging.Logger = None) -> dict:
    """
    report_information determines the info about author and so on
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    obs_date = nested_lookup(key='first', document=amc.dRTK)[0]
    obs_date = datetime.strptime(obs_date.split('.')[0], '%Y %m %d %H %M %S').strftime('%d %B %Y')
    report_info = {'title': NoEscape('Analysis of observations\n\n{date:s}'.format(date=obs_date)),
                   'subtitle': NoEscape('Receiver {marker:s} @ {year:04d}/{doy:03d}'.format(marker=amc.dRTK['cli']['marker'], year=amc.dRTK['cli']['yyyy'], doy=amc.dRTK['cli']['doy'])),
                   'author': ['A. Muls'],
                   'company': ['Royal Military Academy'],
                   'classification': '  '}

    if logger is not None:
        logger.info('{func:s}: report creation information {report!s}'.format(report=report_info, func=cFuncName))

    return report_info


def create_gfzrnx_document(logger: logging.Logger = None) -> Document:
    """
    create_gfzrnx_document creates the ltx document for gfzrnx analysis of RINEX Obs/nav analysis
    """
    # create ltx document name
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    # get tthe report information
    report_info = report_information(logger=logger)

    fancy_head = [r'{author:s}'.format(author=', '.join([author for author in report_info['author']])),
                  r'{classification:s}'.format(classification=report_info['classification']),
                  NoEscape(r'\today')]
    fancy_foot = [r'', r'{classification:s}'.format(classification=report_info['classification']), r'']

    amc.dRTK['obstab']['pdf'] = amc.dRTK['obstab']['fname'].split('.')[0] + '.pdf'
    if logger is not None:
        logger.info('{func:s}: creating PDF report {pdf:s}'.format(pdf=colored(amc.dRTK['obstab']['pdf'], 'green'), func=cFuncName))

    # start the latex document
    ltxdoc = ltx_report.create_document(fhead=fancy_head, ffoot=fancy_foot)
    ltx_titlepage.report_titlepage(doc=ltxdoc, report_info=report_info)

    return ltxdoc


def create_obstab_report(ltxdoc: Document, logger: logging.Logger = None) -> Document:
    """
    create_obstab_report creates the PDF/ltx report document
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    if logger is not None:
        logger.info('{func:s}: adding observation analyis to ltx_report'.format(func=cFuncName))

    # add analysis section for the observations
    ltxdoc.append(Section(title='Creation of RINEX files for {marker:s}'.format(marker=amc.dRTK['cli']['marker'])))
    # report the information from CLI options in a subsection
    ltxdoc.append(ltx_obstab_reporting.obstab_script_information(dCLI=amc.dRTK['cli'], script_name=os.path.basename(__file__)))

    # add subsection of created RINEX files
    rnx_obs3f = nested_lookup(key='obs3f', document=amc.dRTK)[0]
    rnx_nav3f = nested_lookup(key='nav3f', document=amc.dRTK)[0]
    dir_yydoy = nested_lookup(key='yydoy', document=amc.dRTK)[0]
    ltxdoc.append(ltx_obstab_reporting.obstab_files_created(dir_yydoy=dir_yydoy, rnx_obs3f=rnx_obs3f, rnx_nav3f=rnx_nav3f))

    # start of analysis of RINEX observation file
    ltxdoc.append(Section(title='Analysis of RINEX observation files'))

    # add information with systypes and obstypes
    GNSSs = nested_lookup(key='GNSSs', document=amc.dRTK)[0]
    print('GNSSs = {!s}'.format(GNSSs))
    sysobs = nested_lookup(key='sysobs', document=amc.dRTK)[0]
    sysfreqs = nested_lookup(key='sysfrq', document=amc.dRTK)[0]
    sysprns = nested_lookup(key='PRNs', document=amc.dRTK)[0]
    sysspan = nested_lookup(key='t_span', document=amc.dRTK)[0]
    ltxdoc.append(ltx_obstab_reporting.obstab_rinex_information(GNSSsysts=GNSSs, sysobss=sysobs, sysfreqs=sysfreqs, sysprns=sysprns, sysspan=sysspan))

    plots = nested_lookup(key='plt', document=amc.dRTK)[0]
    for gnss in amc.dRTK['cli']['GNSSs']:
        ltxdoc.append(ltx_obstab_reporting.obstab_obst_summary(gnss=gnss, cli_obsts=amc.dRTK['cli']['obstypes'], obs_plots=plots))

    return ltxdoc


def create_navtab_report(ltxdoc: Document, logger: logging.Logger = None) -> Document:
    """
    create_navtab_report creates the PDF/ltx report document
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    ltxdoc.append(Section(title='Analysis of RINEX navigation files'))
    for gnss in amc.dRTK['cli']['GNSSs']:
        ltxdoc.append(ltx_navtab_reporting.navtab_rinex_information(gnss=gnss, dnavInfo=amc.dRTK['navtab'][gnss]))

    return ltxdoc
