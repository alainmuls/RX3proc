from os import path

# constants used whth gfzrnx

# identification of GNSSs
lst_GNSSs = ['E', 'G']
lst_GNSSs_names = ['Galileo', 'GPS NavSTAR']
dict_GNSSs = dict(zip(lst_GNSSs, lst_GNSSs_names))

# identification of PRNs for each GNSS
max_PRN = [36, 32]
dict_GNSS_MAXPRN = dict(zip(lst_GNSSs, max_PRN))
GNSS_PRNs = ['', '']
for i, (gnss, max_prn) in enumerate(dict_GNSS_MAXPRN.items()):
    lst_gnss_prns = ['{gnss:s}{prn:02d}'.format(gnss=gnss, prn=prn) for prn in list(range(0, max_prn + 1))]
    GNSS_PRNs[i] = lst_gnss_prns

# contains valid PRN numbers per GNSS
dict_GNSS_PRNs = dict(zip(lst_GNSSs, GNSS_PRNs))

# identification of observation types
lst_obstypes = ['S', 'C', 'D', 'L']
lst_obstypes_names = ['Pseudorange', 'SNR', 'Doppler', 'Carrier']
dict_obstypes = dict(zip(lst_obstypes, lst_obstypes_names))

lst_freqs = ['1', '2', '5', '6']

lst_MARKER_TYPES = ['STATIC', 'MOVING']

# crux templates
crux_tmpl = path.expanduser('~/amPython/rnx3proc/gfzrnx/P3RS2-obs.crux')

# identification of the navigation entries read by georinex

# Index(['SVclockBias', 'SVclockDrift', 'SVclockDriftRate', 'IODnav', 'Crs',
#        'DeltaN', 'M0', 'Cuc', 'Eccentricity', 'Cus', 'sqrtA', 'Toe', 'Cic',
#        'Omega0', 'Cis', 'Io', 'Crc', 'omega', 'OmegaDot', 'IDOT', 'DataSrc',
#        'GALWeek', 'SISA', 'health', 'BGDe5a', 'BGDe5b', 'TransTime', 'IODE',
#        'CodesL2', 'GPSWeek', 'L2Pflag', 'SVacc', 'TGD', 'IODC'],
#       dtype='object')
navcols_iden = ['sv', 'time']
navcols_common = ['SVclockBias', 'SVclockDrift', 'SVclockDriftRate', 'Crs', 'DeltaN', 'M0', 'Cuc', 'Eccentricity', 'Cus', 'sqrtA', 'Toe', 'Cic', 'Omega0', 'Cis', 'Io', 'Crc', 'omega', 'OmegaDot', 'IDOT']
navcols_E1 = ['IODnav', 'DataSrc', 'SISA', 'health', 'TransTime']
navcols_E2 = ['GALWeek', 'BGDe5a', 'BGDe5b']
navcols_G1 = ['IODE', 'SVacc', 'IODC', 'health', 'TransTime']
navcols_G2 = ['CodesL2', 'GPSWeek', 'L2Pflag', 'TGD']

# interpretation of the DataSrc entry for Galileo (float -> int!!)
dict_navtype = {0b0001: 'I/NAV E1-B',
                0b0010: 'F/NAV E5a-I',
                0b0100: 'I/NAV E5b-I',
                0b0101: 'I/NAV merged'}
