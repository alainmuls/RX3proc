import sys
import os
from math import isnan
from pylatex import Subsection, NoEscape, Figure, LongTabu, Subsubsection, Enumerate, MultiColumn, NewPage, TextColor
from pylatex.utils import bold
from pylatex.section import Paragraph
import datetime as dt
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
        with sssec.create(LongTabu('rcl', pos='l', col_space='4pt')) as longtabu:
            longtabu.add_row(('Script', ':', script_name))
            longtabu.add_row(('Run at', ':', '{dt!s}'.format(dt=dt.datetime.now().strftime("%d/%m/%Y %H:%M"))))
            longtabu.add_row(('Run by', ':', '{author:s}'.format(author=', '.join(info_report['author']))))
            longtabu.add_row(('', '', '{company:s}'.format(company=', '.join(info_report['company']))))
            # longtabu.add_empty_row()

    with ssec.create(Subsubsection(title='Parameters', numbering=True)) as sssec:
        with sssec.create(LongTabu('rcl', pos='l', col_space='4pt')) as longtabu:
            longtabu.add_row(('RINEX root directory', ':', os.path.expanduser(dCli['path'])))
            longtabu.add_row(('RINEX observation file', ':', dCli['obsf']))
            longtabu.add_row(('RINEX version', ':', dHdr['file']['version']))
            longtabu.add_row(('Marker', ':', dInfo['marker']))
            longtabu.add_row(('Year/day-of-year', ':', '{yyyy:04d}/{doy:03d}'.format(yyyy=dInfo['yyyy'], doy=dInfo['doy'])))
            longtabu.add_empty_row()

    with ssec.create(Subsubsection(title='Observation header information', numbering=True)) as sssec:
        with sssec.create(LongTabu('rcl', pos='l', col_space='4pt')) as longtabu:
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
        with sssec.create(LongTabu('rcl', pos='l', col_space='4pt')) as longtabu:
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


def ltx_obsstat_analyse(obsstatf: str,
                        dfObsTle: pd.DataFrame,
                        plots: dict,
                        script_name: str) -> Subsection:
    """
    ltx_obsstat_analyse summarises the observations compared to TLE information obtained from file obsstatf
    """
    ssec = Subsection('Observation statistics')

    # select the columns used for plotting
    col_names = dfObsTle.columns.tolist()
    GNSS = col_names[col_names.index('PRN') - 1]
    obstypes = [x for x in col_names[col_names.index('PRN') + 1:]]
    print('obstypes = {}'.format(obstypes))
    # we only look at the SNR values since the same value for C/L/D, thus remove starting S
    navsigs = ['{gnss:s}{navsig:s}'.format(gnss=GNSS, navsig=x[1:]) for x in obstypes[:-1]]
    ssec.append('Logged navigation signals for {gnss:s}: {obst:s}'.format(gnss=gfzc.dict_GNSSs[GNSS],
                                                                          obst=' '.join(navsigs)))
    # add TLE_count to navsigs
    # navsigs.append(obstypes[-1])

    with ssec.create(Subsubsection(title='Observables count per navigation signal', numbering=True)) as sssec:
        # add timing and observation count info
        sssec.append('The following table represents the number of observations made for each examined navigation signal. The percentages per navigation signal are calculated by dividing by the  number of observations obtained from Two Line Elements (TLE) at the recorded interval. The last column represents the number of observations possible during the observed time interval.')

        # determine align formats for langtabu
        fmt_tabu = 'l|' + 'rr|' * len(navsigs) + 'r'

        # with sssec.create(Table(position='H')) as table:
        with sssec.create(LongTabu(fmt_tabu, pos='l', col_space='4pt')) as longtabu:
            print(['PRN'] + navsigs + [obstypes[-1]])

            col_row = ['PRN']
            for navsig in navsigs:
                # col_row += [MultiColumn(size=2, align='|c|', data=navsig)]
                col_row += [navsig, '']
            col_row += [obstypes[-1]]
            print(col_row)

            longtabu.add_row(col_row, mapper=[bold])  # header row , mapper=[bold]
            longtabu.add_hline()
            longtabu.end_table_header()

            for index, row in dfObsTle.iterrows():

                # add percentage in the following row if TLE_count differs 0
                # tle_obs = row[obstypes[-1]] / 100
                # if tle_obs > 0:
                #     obstle_perc = ['{:.1f}%'.format(float(x / tle_obs)) for x in row[obstypes[:-1]].tolist()]
                #     # longtabu.add_row([''] + ['{:.1f}% '.format(float(x / tle_obs)) for x in row[obstypes[:-1]].tolist()] + [''])
                # else:
                #     obstle_perc = ['---'] * len(obstypes[:-1])
                #     # longtabu.add_row([''] + ['---'] * len(obstypes[:-1]) + [''])  # add emty row

                print('index = {}'.format(index))
                print('row = {}'.format(row))

                prn_row = [row.PRN]
                tle_obs = row[obstypes[-1]] / 100
                for obstype in obstypes[:-1]:
                    print("type(row[obstype]) = {}".format(type(row[obstype])))
                    prn_row += ['{}'.format(row[obstype])]

                    if tle_obs > 0:
                        print("row[obstype]/tle = {:.1f}%".format(row[obstype] / tle_obs))
                        prn_row += ['{:.1f}%'.format(row[obstype] / tle_obs)]
                    else:
                        prn_row += ['---']

                prn_row += ['{}'.format(row[obstypes[-1]])]
                print('prn_row = {}'.format(prn_row))

                # print([row.PRN, '{}'.format(row[obstypes[:-1]].tolist()), '{}'.format(obstle_perc), '{}'.format(obstypes[-1])])
                longtabu.add_row(prn_row)

        # add figures representing the observations
        ssec.append(NoEscape(r'Figure \ref{fig:obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} represents the absolute count of observables for each navigation signal set out against the maximum possible observations obtained from the TLEs. The relative observation count is represented in ' + r'Figure \ref{fig:rel_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} and ' + r'Figure \ref{fig:prec_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '}.'))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['obs_count'],
                           width=NoEscape(r'0.95\textwidth'),
                           placement=NoEscape(r'\centering'))
            # plot.add_caption('Observation count per navigation signal')
            plot.add_caption(NoEscape(r'\label{fig:obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Observables overview for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['obs_perc'],
                           width=NoEscape(r'0.95\textwidth'),
                           placement=NoEscape(r'\centering'))
            plot.add_caption(NoEscape(r'\label{fig:rel_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Relative observation count per navigation signal for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['relative'],
                           width=NoEscape(r'0.95\textwidth'),
                           placement=NoEscape(r'\centering'))
            plot.add_caption(NoEscape(r'\label{fig:prec_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Relative observation count per navigation signal for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

    return ssec


def obstab_tleobs_ssec(obstabf: str,
                       lst_PRNs: list,
                       lst_NavSignals: list,
                       lst_ObsFreqs: list,
                       dfTle: pd.DataFrame) -> Subsection:
    """
    obstab_tleobs_ssec creates a subsection used for adding info about analysis of the observations
    """
    n = 10  # max elements per line in longtabu

    ssec = Subsection('Detailed analysis of observation types')
    ssec.append('Observation tabular file: {tabf:s}'.format(tabf=obstabf))

    with ssec.create(LongTabu('rcl', pos='l', col_space='4pt')) as longtabu:
        if len(lst_PRNs) > n:
            sublst_PRNs = [lst_PRNs[i * n:(i + 1) *n] for i in range((len(lst_PRNs) + n - 1) // n)]
            for i, subsublst_PRNs in enumerate(sublst_PRNs):
                if i == 0:
                    longtabu.add_row(('Examined satellites', ':', '{prns:s}'.format(prns=' '.join(subsublst_PRNs))))
                else:
                    longtabu.add_row(('', '', '{prns:s}'.format(prns=' '.join(subsublst_PRNs))))
        else:
            longtabu.add_row(('Examined satellites', ':', '{prns:s}'.format(prns=' '.join(lst_PRNs))))

        # longtabu.add_empty_row()

        if len(lst_NavSignals) > n:
            sublst_NavSignals = [lst_NavSignals[i * n:(i + 1) * n] for i in range((len(lst_NavSignals) + n - 1) // n)]
            for i, subsublst_NavSignals in enumerate(sublst_NavSignals):
                if i == 0:
                    longtabu.add_row(('Examined navigation signals', ':', '{obst:s}'.format(obst=' '.join(subsublst_NavSignals))))
                else:
                    longtabu.add_row(('', '', '{obst:s}'.format(obst=' '.join(subsublst_NavSignals))))
        else:
            longtabu.add_row(('Examined navigation signals', ':', '{obst:s}'.format(obst=' '.join(lst_NavSignals))))

        # longtabu.add_empty_row()

        if len(lst_ObsFreqs) > n:
            sublst_ObsFreqs = [lst_ObsFreqs[i * n:(i + 1) * n] for i in range((len(lst_ObsFreqs) + n - 1) // n)]
            for i, subsublst_ObsFreqs in enumerate(sublst_ObsFreqs):
                if i == 0:
                    longtabu.add_row(('Examined observables', ':', '{obst:s}'.format(obst=' '.join(subsublst_ObsFreqs))))
                else:
                    longtabu.add_row(('', '', '{obst:s}'.format(obst=' '.join(subsublst_ObsFreqs))))
        else:
            longtabu.add_row(('Examined observables', ':', '{obst:s}'.format(obst=' '.join(lst_ObsFreqs))))

    # add the TLE rise / set / cul info
    with ssec.create(Subsubsection(r'TLE time spans')) as sssec:
        sssec.append(NoEscape(r'The table below represents the calculated rise and set times within the observation time span for a PRN based on the TLEs. When a culmination is within this interval, it is represented in the table.'))

        with sssec.create(LongTabu('l|l|l|l|l', pos='l', col_space='4pt')) as longtabu:
            longtabu.add_row(['PRN'] + dfTle.columns.tolist(), mapper=[bold])  # header row
            longtabu.add_hline()
            longtabu.end_table_header()
            # longtabu.add_row(['PRN'] + dfTle.columns.tolist(), mapper=[bold])  # header row
            # longtabu.add_hline()
            # longtabu.end_header()

            for prn, row in dfTle.iterrows():
                tabu_row = [prn]
                for col in dfTle.columns.tolist():
                    tle_toadd = [tle_conversion(tle_val) for tle_val in row[col]]
                    tabu_row.append(', '.join(tle_toadd))

                longtabu.add_row(tabu_row)

            longtabu.add_hline()

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


def obstab_tleobs_overview(gnss: str,
                           navsigs: list,
                           navsig_plts: dict,
                           navsig_obst_lst: dict,
                           dPNT: dict) -> Subsubsection:
    """
    obstab_tleobs_overview adds the info about the TLE rise/set/cul times and the general overview plot
    """
    sssec = Subsubsection(r'Navigation signals analysis')

    # go over the available navigation signals
    print('navsigs = {}'.format(navsigs))
    for navsig in navsigs:
        print('navsig = {}'.format(navsig))
        print('navsig_plts = {}'.format(navsig_plts))

        sssec.append(NewPage())

        with sssec.create(Paragraph(r'Analysis of navigation signal {gnss:s}{navs:s}'.format(gnss=gnss, navs=navsig))) as paragraph:

            with paragraph.create(Enumerate()) as enum:

                # add figures representing the observations per navigation signal
                enum.add_item(NoEscape(r'Figure \ref{fig:tle_navsig_' + '{navs:s}'.format(navs=navsig) + '{gnss:s}'.format(gnss=gnss) + '}} represents the observed time span for navigation signal {gnss:s}{navs:s} set out against the maximum time span calculated from the  Two Line Elements (TLE). If present, the culmination point for a satellite is represented by a triangle.'.format(gnss=gnss, navs=navsig)))

                with enum.create(Figure(position='htbp')) as plot:
                    plot.add_image(navsig_plts[navsig]['tle-obs'],
                                   width=NoEscape(r'0.95\textwidth'),
                                   placement=NoEscape(r'\centering'))

                    # print(r'\label{fig:tle_navsig_' + r'{gnss:s}'.format(gnss=gnss) + r'{navs:s}'.format(navs=navsig) + r'}} Navigation signal {gnss:s}{navs:s} versus TLE time span'.format(gnss=gnss, navs=navsig))

                    plot.add_caption(NoEscape(r'\label{fig:tle_navsig_' + '{navs:s}'.format(navs=navsig) + '{gnss:s}'.format(gnss=gnss) + '}} Navigation signal {gnss:s}{navs:s} versus TLE time span'.format(gnss=gnss, navs=navsig)))

                print('navsig_obst_lst[{}] = {}'.format(navsig, navsig_obst_lst[navsig]))

                for navsig_obst in navsig_obst_lst[navsig]:
                    print('navsig_obst = {}'.format(navsig_obst))
                    enum.add_item(NoEscape(r'Figure \ref{fig:tle_navsig_' + '{gnss:s}'.format(gnss=gnss) + '{navsobst:s}'.format(navsobst=navsig_obst) + '}} displays the evolution of observation type {obst:s}'.format(obst=navsig_obst)))
                    with enum.create(Figure(position='htbp')) as plot:
                        plot.add_image(navsig_plts[navsig]['obst'][navsig_obst],
                                       width=NoEscape(r'0.95\textwidth'),
                                       placement=NoEscape(r'\centering'))

                        # print(r'\label{fig:tle_navsig_' + r'{gnss:s}'.format(gnss=gnss) + r'{navs:s}'.format(navs=navsig) + r'}} Navigation signal {gnss:s}{navs:s} versus TLE time span'.format(gnss=gnss, navs=navsig))

                        plot.add_caption(NoEscape(r'\label{fig:tle_navsig_' + '{gnss:s}'.format(gnss=gnss) + '{navsobst:s}'.format(navsobst=navsig_obst) + '}} Navigation signal {navsobst:s} evolution'.format(navsobst=navsig_obst)))

                # add evolution of the PRNcnt over time (more or less than 4) and report time jumps
                if len(dPNT[navsig]['loss']) > 0:
                    enum.append('The table below summarises the PRN count statistics which determines the loss and reacquisition of PNT.')

                    with enum.create(LongTabu('r|r|r', pos='l', col_space='4pt')) as longtabu:
                        longtabu.add_row((MultiColumn(3, align='c', data=TextColor('blue','Navigation signal {navs:s}'.format(navs=navsig))),))
                        longtabu.add_row(['Loss of PNT', 'PNT Reacquisition', 'Duration [s]'], mapper=[bold])  # header row
                        longtabu.add_hline()
                        longtabu.end_table_header()
                        # longtabu.add_row(['PRN'] + dfTle.columns.tolist(), mapper=[bold])  # header row
                        # longtabu.add_hline()
                        # longtabu.end_header()

                        print('len loss / reacq = {} {}'.format(len(dPNT[navsig]['loss']), len(dPNT[navsig]['reacq'])))
                        for loss, reacq, gap in zip(dPNT[navsig]['loss'], dPNT[navsig]['reacq'], dPNT[navsig]['gap']):
                            print('{} -> {}: {}'.format(loss.strftime('%H:%M:%S'), reacq.strftime('%H:%M:%S'), gap))
                            longtabu.add_row([loss.strftime('%H:%M:%S'), reacq.strftime('%H:%M:%S'), gap])

    return sssec
