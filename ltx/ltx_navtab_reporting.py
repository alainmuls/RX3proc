import os
from pylatex import Subsection, LongTabu, Figure
from pylatex.utils import bold, NoEscape

from ampyutils import am_config as amc
from gfzrnx import gfzrnx_constants as gfzc

__author__ = 'amuls'


def navtab_rinex_information(gnss: str, dnavInfo: dict) -> Subsection:
    """
    navtab_rinex_information creates a subsection with RINEX nav information for a GNSS
    """
    n = 10  # max elements per line in longtabu

    ssec = Subsection(title='RINEX navigation analysis for {gnss:s}'.format(gnss=gfzc.dict_GNSSs[gnss]))

    # report the PRNs for which a navigation was received
    with ssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
        if len(dnavInfo['PRNs']) > n:
            subPRNs = [dnavInfo['PRNs'][i * n:(i + 1) * n] for i in range((len(dnavInfo['PRNs']) + n - 1) // n)]
            for i, subsubPRNs in enumerate(subPRNs):
                if i == 0:
                    longtabu.add_row(('PRNs with navigation data', ':', '{prn:s}'.format(prn=', '.join(subsubPRNs))))
                else:
                    longtabu.add_row(('', '', '{prn:s}'.format(prn=', '.join(subsubPRNs))))
            # longtabu.add_empty_row()

        # only calculated for GALILEO
    with ssec.create(LongTabu('rcl', pos='l', col_space='2pt')) as longtabu:
        if ('IODnav_errs' in dnavInfo.keys()) and dnavInfo['IODnav_errs'] > 0:
            longtabu.add_row(('Navigation data with IODnav = 0', ':', '{errnav:d}'.format(errnav=dnavInfo['IODnav_errs'])))

    if gnss == 'E':
        ssec.append(NoEscape('Navigation data are obtained from following {navsv:s}:'.format(navsv=bold('navigation services'))))
        ssec.append(navtab_galileo_datasource(dnavInfo=dnavInfo))

        ssec.append(NoEscape('Overview of received {sisa:s} (Signal In Space Accuracy) and {health:s}:'.format(sisa=bold('SISA'), health=bold('health status'))))
        for info in ['SISA', 'health']:
            ssec.append(navtab_gnss_info(info_name=info, dInfo=dnavInfo[info]))
    elif gnss == 'G':
        ssec.append(NoEscape('Overview of received {SVacc:s} (SV accuracy) and {health:s}:'.format(SVacc=bold('SVacc'), health=bold('health status'))))
        for info in ['SVacc', 'health']:
            ssec.append(navtab_gnss_info(info_name=info, dInfo=dnavInfo[info]))

    # add plot about upload of navigation message
    with ssec.create(Figure(position='htbp!')) as figure:
        fig_name = os.path.join(amc.dRTK['dirs']['rnxplt'], amc.dRTK['navtab']['plt']['navupload_{gnss:s}'.format(gnss=gnss)])
        figure.add_image(fig_name, width=NoEscape(r'0.95\linewidth'))
        figure.add_caption(NoEscape(r'\label{fig:navupload_' + '{gnss:s}'.format(gnss=gnss) + '} Navigation upload for ' + '{gnss:s}'.format(gnss=gfzc.dict_GNSSs[gnss])))

    return ssec


def navtab_gnss_info(info_name: str, dInfo: dict) -> LongTabu:
    """
    navtab_gnss_info reports the GALILEO specific navigation information
    """
    # report DataSrc for Galileo PRNs
    longtabu = LongTabu('c|c|r', pos='c', col_space='5pt')
    longtabu.add_row(('PRN', info_name, 'count'), mapper=[bold])
    longtabu.add_hline()
    for prn, prn_info in dInfo.items():
        for i, (prn_key, prn_value) in enumerate(prn_info.items()):
            if i == 0:
                longtabu.add_row((prn, '{value:.2f}'.format(value=prn_key), '{count:d}'.format(count=prn_value)))
            else:
                longtabu.add_row(('', '{value:.2f}'.format(value=prn_key), '{count:d}'.format(count=prn_value)))

    return longtabu


def navtab_galileo_datasource(dnavInfo: dict) -> LongTabu:
    """
    navtab_galileo_datasource reports the GALILEO specific navigation information
    """
    # report DataSrc for Galileo PRNs
    longtabu = LongTabu('c|c|r', pos='c', col_space='5pt')
    longtabu.add_row(('PRN', 'Navigation signal', 'count'), mapper=[bold])
    longtabu.add_hline()
    for prn, prnDataSrc in dnavInfo['DataSrc'].items():
        for i, (prnkey, prnValue) in enumerate(prnDataSrc.items()):
            if i == 0:
                longtabu.add_row((prn, '{srcname:s}'.format(srcname=gfzc.dict_navtype[prnkey]), '{count:d}'.format(count=prnValue)))
            else:
                longtabu.add_row(('', '{srcname:s}'.format(srcname=gfzc.dict_navtype[prnkey]), '{count:d}'.format(count=prnValue)))

    return longtabu
