import os
import sys
from pylatex import Subsection, LongTable, MultiColumn, NoEscape, Itemize, SubFigure, Figure, LongTabu, Subsubsection
from datetime import datetime
from pylatex.utils import bold
import numpy as np
from nested_lookup import nested_lookup
import json
import pandas as pd

from gfzrnx import gfzrnx_constants as gfzc

from ampyutils import am_config as amc
from ampyutils import amutils
from ltx import ltx_gfzrnx_report

__author__ = 'amuls'


def obstab_script_information(dCli: dict, dHdr: dict, dInfo: dict, script_name: str) -> Subsection:
    """
    obstab_script_information creates the section with information about the script obstab_analyze
    """
    info_report = ltx_gfzrnx_report.report_information(dInfo=dInfo)

    n = 10  # max elements per line in longtabu

    print('dHdr information =\n{json!s}'.format(json=json.dumps(dHdr, sort_keys=False, indent=4, default=amutils.json_convertor)))

    ssec = Subsection('Script details')
    with ssec.create(Subsubsection(title='Program information', numbering=True)) as sssec:
        with sssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
            longtabu.add_row(('Script', ':', script_name))
            longtabu.add_row(('Run at', ':', '{dt!s}'.format(dt=datetime.now().strftime("%d/%m/%Y %H:%M"))))
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

            longtabu.add_row(('First epoch', ':', datetime.strptime(epoch_first.split('.')[0], '%Y %m %d %H %M %S').strftime('%Y/%m/%d %H:%M:%S')))
            longtabu.add_row(('Last epoch', ':', datetime.strptime(epoch_last.split('.')[0], '%Y %m %d %H %M %S').strftime('%Y/%m/%d %H:%M:%S')))
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
                    longtabu.add_row(('Frequencies {syst:s}'.format(syst=gnss), ':', '{freq:s}'.format(freq=', '.join(sysfreq))))
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
                                longtabu.add_row(('Observable types {syst:s}'.format(syst=gnss), ':', '{obst:s}'.format(obst=', '.join(subsubobstypes))))
                            else:
                                longtabu.add_row(('', '', '{obst:s}'.format(obst=', '.join(subsubobstypes))))
                    else:
                        longtabu.add_row(('Observable types {syst:s}'.format(syst=gnss), ':', '{obst:s}'.format(obst=', '.join(obstypes))))
            longtabu.add_empty_row()


    # print('ssec = \n{!s}'.format(ssec))
    # print('-' * 25)
    # print('type(ssec) = {!s}'.format(type(ssec)))
    # print('-' * 25)

    return ssec


def obstab_analyse(obsstatf: str, dfObsTle: pd.DataFrame, plots: dict, script_name: str) -> Subsection:
    """
    obstab_analyse summarises the observations compared to TLE information obtained from file obsstatf
    """
    ssec = Subsection('Observation statistics')

    # select the columns used for plotting
    col_names = dfObsTle.columns.tolist()
    GNSS = col_names[col_names.index('TYP') - 1]
    obstypes = [x for x in col_names[col_names.index('TYP') + 1:]]
    print('GNSS = {!s}'.format(GNSS))
    print('obstypes = {!s}'.format(obstypes))
    print(', '.join(obstypes))

    # we only look at the SNR values since the same value for C/L/D, thus remove starting S
    obst_txt = ['+{:s}'.format(x[1:]) for x in obstypes[:-1]]
    obst_txt.append(obstypes[-1])

    ssec.append('The following observations for {gnss:s} were logged: {obst:s}'.format(gnss=gfzc.dict_GNSSs[GNSS], obst=', '.join(obst_txt)))

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

            # for name, values in dfObsTle.iteritems():
            #     print('{name!s}: {value!s}'.format(name=name, value=values))

            for index, row in dfObsTle.iterrows():
                longtabu.add_row([row.TYP] + [int(x) for x in row[obstypes].tolist()])

                # add percentage in the following row if TLE_count differs 0
                tle_obs = row[obstypes[-1]] / 100
                print('tle_obs = {:f}'.format(tle_obs))
                if tle_obs > 0:
                    longtabu.add_row([''] + ['{:.1f}% '.format(float(x / tle_obs)) for x in row[obstypes[:-1]].tolist()] + [''])
                else:
                    longtabu.add_row([''] + ['---'] * len(obstypes[:-1]) + [''])  # add emty row

            longtabu.add_hline()

        # add figures representing the observations
        ssec.append(NoEscape(r'Figure \vref{fig:obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} represents the absolute count of observables for each navigation signal set out against the maximum possible observations obtained from the Two Line Elements (TLE). The relative observation count is represented in ' + r'Figure \vref{fig:rel_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '}.'))
        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['obs_count'], width=NoEscape(r'0.8\textwidth'), placement=NoEscape(r'\centering'))
            # plot.add_caption('Observation count per navigation signal')
            plot.add_caption(NoEscape(r'\label{fig:obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Observables overview for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

        with sssec.create(Figure(position='htbp')) as plot:
            plot.add_image(plots['obs_perc'], width=NoEscape(r'0.8\textwidth'), placement=NoEscape(r'\centering'))
            plot.add_caption(NoEscape(r'\label{fig:rel_obst_gnss_' + '{gnss:s}'.format(gnss=GNSS) + '} Relative observation count per navigation signal for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[GNSS])))

    return ssec


# OLD STUFF ????

def obstab_files_created(dir_yydoy: str, rnx_obs3f: str, rnx_nav3f: str) -> Subsection:
    """
    obstab_files_created lists the created rinex files
    """
    ssec = Subsection('RINEX data files')
    with ssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
        longtabu.add_row(('RINEX directory', ':', dir_yydoy))
        longtabu.add_row(('Observation file', ':', rnx_obs3f))
        longtabu.add_row(('Navigation file', ':', rnx_nav3f))
        longtabu.add_empty_row()

    return ssec


def obstab_rinex_information(GNSSsysts: list, sysobss: dict, sysfreqs: list, sysprns: list, sysspan: list) -> Subsection:
    """
    obstab_rinex_information creates the subsection with RINEX obs information
    """
    n = 10  # max elements per line in longtabu

    epoch_first = nested_lookup(key='first', document=amc.dRTK)[0]
    epoch_last = nested_lookup(key='last', document=amc.dRTK)[0]
    interval = float(nested_lookup(key='interval', document=amc.dRTK)[0])

    ssec = Subsection(title='RINEX observation information')
    with ssec.create(Subsubsection(title='Timing', numbering=True)) as sssec:
        # add timing info
        with sssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
            longtabu.add_row(('First epoch', ':', datetime.strptime(epoch_first.split('.')[0], '%Y %m %d %H %M %S').strftime('%Y/%m/%d %H:%M:%S')))
            longtabu.add_row(('Last epoch', ':', datetime.strptime(epoch_last.split('.')[0], '%Y %m %d %H %M %S').strftime('%Y/%m/%d %H:%M:%S')))
            longtabu.add_row(('Interval', ':', '{intv:.1f}'.format(intv=interval)))

    with ssec.create(Subsubsection(title='Logged observables', numbering=True)) as sssec:
        # add info about observable types logged
        with sssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
            for gnss, obstypes in sysobss.items():
                if gnss in GNSSsysts:
                    if len(obstypes) > n:
                        subobstypes = [obstypes[i * n:(i + 1) * n] for i in range((len(obstypes) + n - 1) // n)]
                        for i, subsubobstypes in enumerate(subobstypes):
                            if i == 0:
                                longtabu.add_row(('Observable types {syst:s}'.format(syst=gnss), ':', '{obst:s}'.format(obst=', '.join(subsubobstypes))))
                            else:
                                longtabu.add_row(('', '', '{obst:s}'.format(obst=', '.join(subsubobstypes))))
                    else:
                        longtabu.add_row(('Observable types {syst:s}'.format(syst=gnss), ':', '{obst:s}'.format(obst=', '.join(obstypes))))
            longtabu.add_empty_row()

            # add the frequencies
            for gnss, sysfreq in sysfreqs.items():
                if gnss in GNSSsysts:
                    longtabu.add_row(('Frequencies {syst:s}'.format(syst=gnss), ':', '{freq:s}'.format(freq=', '.join(sysfreq))))
            longtabu.add_empty_row()

            # add info about PRNs logged
            for gnss, sysprn in sysprns.items():
                if len(sysprn) > n:
                    subsysprn = [sysprn[i * n:(i + 1) * n] for i in range((len(sysprn) + n - 1) // n)]
                    for i, subsubsysprn in enumerate(subsysprn):
                        if i == 0:
                            longtabu.add_row(('Observed PRNs {syst:s}'.format(syst=gnss), ':', '{prn:s}'.format(prn=', '.join(subsubsysprn))))
                        else:
                            longtabu.add_row(('', '', '{prn:s}'.format(prn=', '.join(subsubsysprn))))
                else:
                    longtabu.add_row(('Observed PRNs {syst:s}'.format(syst=gnss), ':', '{prn:s}'.format(prn=', '.join(sysprn))))
            longtabu.add_empty_row()

            # add first and last epoch that a PRN of GNSS has been observed
            for gnss, span in sysspan.items():
                longtabu.add_row('Time of first observation {gnss:s}'.format(gnss=gnss), ':', span[0].to_pydatetime().strftime('%Y/%m/%d %H:%M:%S'))
                longtabu.add_row('Time of last observation {gnss:s}'.format(gnss=gnss), ':', span[1].to_pydatetime().strftime('%Y/%m/%d %H:%M:%S'))
                time_span = (span[1] - span[0]) / np.timedelta64(1, 'h')
                longtabu.add_row('observation span {gnss:s}'.format(gnss=gnss), ':', '{span:.2f} hrs'.format(span=time_span))

    return ssec


def obstab_obst_summary(gnss: str, cli_obsts: list, obs_plots: dict) -> Subsection:
    """
    obstab_obst_summary creates the subsection with RINEX observables count and timeline
    """
    # Get the number of observable types for this system
    gnss_obsts = [obst_used for obst_used in amc.dRTK['obstab']['obs_used'][gnss] if obst_used[0].lower() == amc.dRTK['cli']['obstypes'][0].lower()]

    # change the first character by the selected obstypes
    replace_str = '['
    for i, obst in enumerate(amc.dRTK['cli']['obstypes']):
        if i > 0:
            replace_str += '|{obst:s}'.format(obst=obst)
        else:
            replace_str += '{obst:s}'.format(obst=obst)
    replace_str += ']'

    gnss_obsts_str = [replace_str + gnss_obst[1:] for gnss_obst in gnss_obsts]

    nr_obst = len(gnss_obsts)

    fmt = 'r | ' + ('r r |' * (nr_obst - 1)) + (' r r')

    ssec = Subsection(title='GNSS System {gnss:s}'.format(gnss=gfzc.dict_GNSSs[gnss]))

    with ssec.create(Subsubsection(title='Observables count per navigation signal', numbering=True)) as sssec:
        # add timing and observation count info
        sssec.append('The percentages for each navigation service are calculated by using the maximum number of observations over all navigation signals for each individual satellite.')

        with ssec.create(LongTable(fmt, col_space='4pt')) as longtabu:
            hdr_row = [bold('PRN')]
            for j, gnss_obst_str in enumerate(gnss_obsts_str):
                if j < len(gnss_obsts_str) - 1:
                    hdr_row.append(MultiColumn(2, align='c|', data=NoEscape(bold(gnss_obst_str))))
                else:
                    hdr_row.append(MultiColumn(2, align='c', data=NoEscape(bold(gnss_obst_str))))

            longtabu.add_hline()
            longtabu.add_row(hdr_row)  # , mapper=[bold]
            longtabu.add_hline()
            longtabu.end_table_header()
            longtabu.add_hline()
            longtabu.add_row((MultiColumn(nr_obst * 2 + 1, align='r', data="Cont' on Next Page"),))
            longtabu.add_hline()
            longtabu.end_table_footer()
            longtabu.add_hline()
            longtabu.end_table_last_footer()

            for prn in amc.dRTK['obstab']['PRNs'][gnss]:
                row = ['{prn:s}'.format(prn=prn)]

                # determine the max of observations between all observable navigation signals
                obsts_max = []
                for obst in gnss_obsts:
                    obsts_max.append(amc.dRTK['obstab']['dPRNepochs'][gnss][prn][obst])

                obst_max = max(obsts_max) / 100
                for obst in gnss_obsts:
                    row.append('{count:d}'.format(count=amc.dRTK['obstab']['dPRNepochs'][gnss][prn][obst]))
                    percentage = amc.dRTK['obstab']['dPRNepochs'][gnss][prn][obst] / obst_max
                    if '{perc:.1f}'.format(perc=percentage) == '100.0':
                        row.append('---')
                    else:
                        row.append('{perc:.1f}%'.format(perc=percentage))
                longtabu.add_row((row))

        # fig_count = 'kitten'
        ssec.append(NoEscape(r'Figure \vref{fig:obst_gnss_' + '{gnss:s}'.format(gnss=gnss) + '} represents:'))
        with ssec.create(Itemize()) as itemize:
            itemize.add_item('on the left the count of observations made per navigation signal for each satellite,')
            itemize.add_item('on the right the timeline of these observations per navigation signal for each satellite.')

        with ssec.create(Figure(position='H')) as figure:
            with ssec.create(SubFigure(position='t', width=NoEscape(r'0.5\linewidth'))) as left_fig:
                lfig_name = os.path.join(amc.dRTK['dirs']['rnxplt'], obs_plots['obs_count_{gnss:s}'.format(gnss=gnss)])
                left_fig.add_image(lfig_name, width=NoEscape(r'\linewidth'))
                left_fig.add_caption('Observables count')
            with ssec.create(SubFigure(position='t', width=NoEscape(r'0.5\linewidth'))) as right_fig:
                rfig_name = os.path.join(amc.dRTK['dirs']['rnxplt'], obs_plots['timeline_{gnss:s}'.format(gnss=gnss)])
                right_fig.add_image(rfig_name, width=NoEscape(r'\linewidth'))
                right_fig.add_caption('Observables timelines')
            figure.add_caption(NoEscape(r'\label{fig:obst_gnss_' + '{gnss:s}'.format(gnss=gnss) + '} Observables overview for GNSS ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[gnss])))

        # ssec.append(NoEscape(r'\clearpage'))

        for obst in cli_obsts:
            with ssec.create(Subsubsection(title='Analysis of observation {obst:s}'.format(obst=gfzc.dict_obstypes[obst]), numbering=True)) as sssec:
                # add anaylis plots of requested observations
                sssec.append('The following plots show the {obst:s} values for each navigation service per observed satellite. If multiple navigation signals are available for this GNSS the bottom graph of each plot represents the difference between these navigation services.'.format(obst=gfzc.dict_obstypes[obst]))

                # create the adequate dict key for this GNSS and obst
                obst_key = '{gnss:s}_{obst:s}'.format(gnss=gnss, obst=obst)

                # create a longtabu with 3 columns to display the plots per PRN
                nr_plots_per_row = 2
                width_per_col = .99 / nr_plots_per_row
                fmt = NoEscape((r'p{' + r'{width:.3f}'.format(width=width_per_col) + r'\linewidth{}}') * nr_plots_per_row)
                with ssec.create(LongTabu(fmt, pos='c', col_space='4pt')) as longtabu:
                    for i, (prn, plt) in enumerate(obs_plots[obst_key].items()):
                        if (i % nr_plots_per_row) == 0:
                            row = [''] * nr_plots_per_row
                        row[i % nr_plots_per_row] = NoEscape(r'\makecell[c]{\includegraphics[width=\linewidth{}]{' + os.path.join(amc.dRTK['dirs']['rnxplt'], '{:s}'.format(plt)) + '}}')
                        if ((i % nr_plots_per_row) == (nr_plots_per_row - 1)) or (i == len(obs_plots[obst_key].keys()) - 1):
                            longtabu.add_row(row)
                    longtabu.add_empty_row()

    return ssec
