import os
import sys
from math import isnan
from pylatex import Subsection, NoEscape, Figure, LongTabu, Subsubsection
import datetime as dt
from pylatex.utils import bold
from nested_lookup import nested_lookup
import pandas as pd

from gfzrnx import gfzrnx_constants as gfzc

from ltx import ltx_gfzrnx_report

__author__ = 'amuls'


def rnxobs_script_information(dCli: dict,
                              dHdr: dict,
                              dInfo: dict,
                              script_name: str) -> Subsection:
    """
    rnxobs_script_information creates the section with information about the script obstab_analyze
    """
    info_report = ltx_gfzrnx_report.report_information(dInfo=dInfo)

    n = 10  # max elements per line in longtabu

    ssec = Subsection('Script details')
    with ssec.create(Subsubsection(title='Program information', numbering=True)) as sssec:
        with sssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
            longtabu.add_row(('Script', ':', script_name))
            longtabu.add_row(('Run at', ':', '{dt!s}'.format(dt=dt.datetime.now().strftime("%d/%m/%Y %H:%M"))))
            longtabu.add_row(('Run by', ':', '{author:s}'.format(author=', '.join(info_report['author']))))
            longtabu.add_row(('', '', '{company:s}'.format(company=', '.join(info_report['company']))))
            # longtabu.add_empty_row()

    with ssec.create(Subsubsection(title='Parameters', numbering=True)) as sssec:
        with sssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
            longtabu.add_row(('RINEX root directory', ':', os.path.expanduser(dCli['path'])))
            longtabu.add_row(('RINEX observation file', ':', dCli['obsf']))
            longtabu.add_row(('RINEX version', ':', dHdr['file']['version']))
            longtabu.add_row(('Marker', ':', dInfo['marker']))
            longtabu.add_row(('Year/day-of-year', ':', '{yyyy:04d}/{doy:03d}'.format(yyyy=dInfo['yyyy'], doy=dInfo['doy'])))
            longtabu.add_empty_row()

    with ssec.create(Subsubsection(title='Observation header information', numbering=True)) as sssec:
        with sssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
            # add start / end DTG and interval
            epoch_first = nested_lookup(key='first', document=dHdr)[0]
            epoch_last = nested_lookup(key='last', document=dHdr)[0]
            interval = float(nested_lookup(key='interval', document=dHdr)[0])

            longtabu.add_row(('First epoch', ':', dt.datetime.strptime(epoch_first.split('.')[0], '%Y %m %d %H %M %S').strftime('%Y/%m/%d %H:%M:%S')))
            longtabu.add_row(('Last epoch', ':', dt.datetime.strptime(epoch_last.split('.')[0], '%Y %m %d %H %M %S').strftime('%Y/%m/%d %H:%M:%S')))
            longtabu.add_row(('Interval', ':', '{intv:.1f}'.format(intv=interval)))
            longtabu.add_empty_row()

            for i, gnss in enumerate(dCli['GNSSs']):
                if i == 0:
                    longtabu.add_row(('GNSS', ':', '{gnss:s} ({name:s}) '.format(gnss=gnss, name=gfzc.dict_GNSSs[gnss])))
                else:
                    longtabu.add_row(('', ':', '{gnss:s} ({name:s}) '.format(gnss=gnss, name=gfzc.dict_GNSSs[gnss])))

            # add the frequencies
            for gnss, sysfreq in dHdr['file']['sysfrq'].items():
                if gnss in dCli['GNSSs']:
                    longtabu.add_row(('Frequencies {syst:s}'.format(syst=gnss), ':', '{freq:s}'.format(freq=' '.join(sysfreq))))
            longtabu.add_empty_row()

            # add observable types available
            for i, obst in enumerate(gfzc.lst_obstypes):
                if i == 0:
                    longtabu.add_row(('Observable types', ':', '{obst:s} ({name:s}) '.format(obst=obst, name=gfzc.dict_obstypes[obst])))
                else:
                    longtabu.add_row(('', ':', '{obst:s} ({name:s}) '.format(obst=obst, name=gfzc.dict_obstypes[obst])))
            longtabu.add_empty_row()

    with ssec.create(Subsubsection(title='Logged observables', numbering=True)) as sssec:
        # add info about observable types logged
        with sssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
            for gnss, obstypes in dHdr['file']['sysobs'].items():
                if gnss in dCli['GNSSs']:
                    if len(obstypes) > n:
                        subobstypes = [obstypes[i * n:(i + 1) * n] for i in range((len(obstypes) + n - 1) // n)]
                        for i, subsubobstypes in enumerate(subobstypes):
                            if i == 0:
                                longtabu.add_row(('Observable types {syst:s}'.format(syst=gnss), ':', '{obst:s}'.format(obst=' '.join(subsubobstypes))))
                            else:
                                longtabu.add_row(('', '', '{obst:s}'.format(obst=' '.join(subsubobstypes))))
                    else:
                        longtabu.add_row(('Observable types {syst:s}'.format(syst=gnss), ':', '{obst:s}'.format(obst=' '.join(obstypes))))
            longtabu.add_empty_row()

    return ssec


def obsstat_analyse(obsstatf: str,
                    dfObsTle: pd.DataFrame,
                    plots: dict) -> Subsection:
    """
    obsstat_analyse summarises the observations compared to TLE information obtained from file obsstatf
    """
    ssec = Subsection('Observation statistics')

    # select the columns used for plotting
    col_names = dfObsTle.columns.tolist()
    GNSS = col_names[col_names.index('PRN') - 1]
    obstypes = [x for x in col_names[col_names.index('PRN') + 1:]]

    # we only look at the SNR values since the same value for C/L/D, thus remove starting S
    obst_txt = ['Observation type: +{:s}'.format(x[1:]) for x in obstypes[:-1]]
    obst_txt.append(obstypes[-1])

    ssec.append('The following observations for {gnss:s} were logged: {obst:s}'.format(gnss=gfzc.dict_GNSSs[GNSS], obst=' '.join(obst_txt)))

    with ssec.create(Subsubsection(title='Observables count per navigation signal', numbering=True)) as sssec:
        # add timing and observation count info
        sssec.append('The percentages for each navigation signal are calculated by using the possible number of observations obtained from TLEs for each individual satellite.')

        # determine align formats for langtabu
        fmt_tabu = 'l|' + 'r' * (len(obstypes) - 1) + '|r'

        with sssec.create(LongTabu(fmt_tabu, pos='l', col_space='2pt')) as longtabu:
            longtabu.add_row(['PRN'] + obst_txt, mapper=[bold])  # header row
            longtabu.add_hline()
            longtabu.end_table_header()
            longtabu.add_row(['PRN'] + obst_txt, mapper=[bold])  # header row
            longtabu.add_hline()

            # for name, values in dfObsTle.iteritems():

            for index, row in dfObsTle.iterrows():
                longtabu.add_row([row.PRN] + [int(x) for x in row[obstypes].tolist()])

                # add percentage in the following row if TLE_count differs 0
                tle_obs = row[obstypes[-1]] / 100
                if tle_obs > 0:
                    longtabu.add_row([''] + ['{:.1f}% '.format(float(x / tle_obs)) for x in row[obstypes[:-1]].tolist()] + [''])
                else:
                    longtabu.add_row([''] + ['---'] * len(obstypes[:-1]) + [''])  # add emty row

            longtabu.add_hline()

        # add figures representing the observations
        ssec.append(NoEscape(r'Figure \vref{fig:obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} represents the absolute count of observables for each navigation signal set out against the maximum possible observations obtained from the Two Line Elements (TLE). The relative observation count is represented in ' + r'Figure \vref{fig:rel_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} and ' + r'Figure \vref{fig:prec_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '}.'))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['obs_count'],
                           width=NoEscape(r'0.8\textwidth'),
                           placement=NoEscape(r'\centering'))
            # plot.add_caption('Observation count per navigation signal')
            plot.add_caption(NoEscape(r'\label{fig:obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Observables overview for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['obs_perc'],
                           width=NoEscape(r'0.8\textwidth'),
                           placement=NoEscape(r'\centering'))
            plot.add_caption(NoEscape(r'\label{fig:rel_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Relative observation count per navigation signal for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['relative'],
                           width=NoEscape(r'0.8\textwidth'),
                           placement=NoEscape(r'\centering'))
            plot.add_caption(NoEscape(r'\label{fig:prec_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Relative observation count per navigation signal for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

    return ssec


def obstab_tleobs_ssec(obstabf: str,
                       lst_PRNs: list,
                       lst_NavSignals: list,
                       lst_ObsFreqs) -> Subsection:
    """
    obstab_tleobs_ssec creates a subsection used for adding info about analysis of the observations
    """
    n = 10  # max elements per line in longtabu

    ssec = Subsection('Detailed analysis of observation types')
    ssec.append('Observation tabular file: {tabf:s}'.format(tabf=obstabf))

    with ssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
        if len(lst_PRNs) > n:
            sublst_PRNs = [lst_PRNs[i * n:(i + 1) *n] for i in range((len(lst_PRNs) + n - 1) // n)]
            for i, subsublst_PRNs in enumerate(sublst_PRNs):
                if i == 0:
                    longtabu.add_row(('Examined satellites', ':', '{prns:s}'.format(prns=' '.join(subsublst_PRNs))))
                else:
                    longtabu.add_row(('', '', '{prns:s}'.format(prns=' '.join(subsublst_PRNs))))
        else:
            longtabu.add_row(('Examined satellites', ':', '{prns:s}'.format(prns=' '.join(lst_PRNs))))

        longtabu.add_empty_row()

        if len(lst_NavSignals) > n:
            sublst_NavSignals = [lst_NavSignals[i * n:(i + 1) * n] for i in range((len(lst_NavSignals) + n - 1) // n)]
            for i, subsublst_NavSignals in enumerate(sublst_NavSignals):
                if i == 0:
                    longtabu.add_row(('Examined navigation signals', ':', '{obst:s}'.format(obst=' '.join(subsublst_NavSignals))))
                else:
                    longtabu.add_row(('', '', '{obst:s}'.format(obst=' '.join(subsublst_NavSignals))))
        else:
            longtabu.add_row(('Examined navigation signals', ':', '{obst:s}'.format(obst=' '.join(lst_NavSignals))))

        longtabu.add_empty_row()

        if len(lst_ObsFreqs) > n:
            sublst_ObsFreqs = [lst_ObsFreqs[i * n:(i + 1) * n] for i in range((len(lst_ObsFreqs) + n - 1) // n)]
            for i, subsublst_ObsFreqs in enumerate(sublst_ObsFreqs):
                if i == 0:
                    longtabu.add_row(('Examined observables', ':', '{obst:s}'.format(obst=' '.join(subsublst_ObsFreqs))))
                else:
                    longtabu.add_row(('', '', '{obst:s}'.format(obst=' '.join(subsublst_ObsFreqs))))
        else:
            longtabu.add_row(('Examined observables', ':', '{obst:s}'.format(obst=' '.join(lst_ObsFreqs))))
    ssec.append(' ')

    return ssec


def tle_conversion(tle_value):
    """
    converts to HMS string if needed
    """
    if isinstance(tle_value, dt.time):
        return tle_value.strftime('%H:%M:%S')
    else:
        if isnan(tle_value):
            return ''
        else:
            return str(tle_value)


def obstab_tleobs_overview(dfTle: pd.DataFrame,
                           gnss: str,
                           navsigs: list,
                           navsig_plts: dict) -> Subsubsection:
    """
    obstab_tleobs_overview adds the info about the TLE rise/set/cul times and the general overview plot
    """
    sssec = Subsubsection('Comparison between navigation signal and TLE time spans')

    with sssec.create(LongTabu('l|l|l|l|l', pos='l', col_space='2pt')) as longtabu:
        longtabu.add_row(['PRN'] + dfTle.columns.tolist(), mapper=[bold])  # header row
        longtabu.add_hline()
        longtabu.end_table_header()
        longtabu.add_row(['PRN'] + dfTle.columns.tolist(), mapper=[bold])  # header row
        longtabu.add_hline()

        for prn, row in dfTle.iterrows():
            tabu_row = [prn]
            for col in dfTle.columns.tolist():
                tle_toadd = [tle_conversion(tle_val) for tle_val in row[col]]
                tabu_row.append(', '.join(tle_toadd))

            longtabu.add_row(tabu_row)

        longtabu.add_hline()

    # go over the available navigation signals
    print('navsigs = {}'.format(navsigs))
    for navsig in navsigs:
        print('navsig = {}'.format(navsig))
        print('navsig_plts = {}'.format(navsig_plts))

        # add figures representing the observations per navigation signal
        sssec.append(NoEscape(r'Figure \vref{fig:tle_navsig_' + '{gnss:s}'.format(gnss=gnss) + '{navs:s}'.format(navs=navsig) + '}} represents the observed time span for navigation signal {gnss:s}{navs:s} set out against the maximum time span calculated from the  Two Line Elements (TLE).'.format(gnss=gnss, navs=navsig)))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(navsig_plts[navsig],
                           width=NoEscape(r'0.8\textwidth'),
                           placement=NoEscape(r'\centering'))

            # print(r'\label{fig:tle_navsig_' + r'{gnss:s}'.format(gnss=gnss) + r'{navs:s}'.format(navs=navsig) + r'}} Navigation signal {gnss:s}{navs:s} versus TLE time span'.format(gnss=gnss, navs=navsig))

            plot.add_caption(NoEscape(r'\label{fig:tle_navsig_' + '{navs:s}'.format(navs=navsig) + '{gnss:s}'.format(gnss=gnss) + '}} Navigation signal {gnss:s}{navs:s} versus TLE time span'.format(gnss=gnss, navs=navsig)))

    return sssec
