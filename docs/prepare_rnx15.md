

## Combining (15 minutes) P3RS2 RINEX files into daily RINEX v3.x files
    

### __rnx15_combine.py__

`rnx15_combine.py` combines the 15 minutes RINEX files from P3RS2 Rx for a specific day to create observation and navigation files in correct RINEX v3.x format.

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ rnx15_combine.py -h
usage: rnx15_combine.py [-h] [-f FROM_DIR] [-r RNX_DIR] -m MARKER -y YEAR -d DOY \
          [-c CRUX] [-l LOGGING LOGGING]

rnx15_combine.py combines P3RS2 RINEX observation / navigation files

optional arguments:
  -h, --help            show this help message and exit
  -f FROM_DIR, --from_dir FROM_DIR
                        Directory of P3RS2 RINEX files (default .)
  -r RNX_DIR, --rnx_dir RNX_DIR
                        Root directory of P3RS2 RINEX files \
                            (default /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/)
  -m MARKER, --marker MARKER
                        marker name (4 chars)
  -y YEAR, --year YEAR  Year (4 digits)
  -d DOY, --doy DOY     day-of-year [1..366]
  -c CRUX, --crux CRUX  CRUX template file for updating RINEX headers \
                            (default ~/amPython/rnxproc/p3rs2-obs.crux)
  -l LOGGING LOGGING, --logging LOGGING LOGGING
                        specify logging level console/file (two of CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET, \
                            default INFO DEBUG)
```
    
\normalsize


#### Example run


\tiny
    
```bash
INFO: location.py - locateProg: gfzrnx is /home/amuls/bin/gfzrnx
INFO: location.py - locateProg: rnx2crz is /home/amuls/bin/rnx2crz
INFO: location.py - locateProg: gzip is /usr/bin/gzip
INFO: rnx15_combine.py - list_rinex_files: found 13 RINEX observation files
INFO: rnx15_combine.py - list_rinex_files: found 13 RINEX navigation files
INFO: rnx15_combine.py - create_crux_file: created crux file /tmp/tmpqei5s1w9
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203110910_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203110925_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111019_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111034_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111049_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111104_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111119_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111134_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111149_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111207_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111222_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111309_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203111324_15M_00U_MO.rnx: \
          ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', \
          'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: obs types found
                                                    E                                                  G
0   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
1   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
2   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
3   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
4   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
5   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
6   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
7   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
8   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
9   E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
10  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
11  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
12  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
INFO: rnx15_combine.py - combine_rnx_obs: combined 13 RINEX files into /tmp/P3RS3110.20O
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp /tmp/P3RS3110.20O -nomren23 04,BEL
INFO: rnx15_combine.py - convert_obsrnx3: adjusting RINEX header for P3RS3110.20O
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp /tmp/P3RS3110.20O -crux /tmp/tmpqei5s1w9 -f \
        -fout /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/20311/P3RS04BEL_R_20203110000_01D_00U_MO.rnx
INFO:    process output = DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | CRUX: (STRING) repair line >rnx_writer-1.0.0    P3RS-2 Receiver     20201106 091001 UTC PGM / RUN BY /DATE<
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | no MARKER NAME in header / taken from file name
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | mismatch between header MARKER NAME () and file/station name (P3RS) / using >P3RS<
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | CRUX: skip >G                                                           SYS / PHASE SHIFT<
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | CRUX: skip >  0                                                         GLONASS SLOT / FRQ #<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >ANT # / TYPE< idx. 0 -> >BEANT<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >ANT # / TYPE< idx. 1 -> >NAVXPERIENCE<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >APPROX POSITION XYZ< idx. 0 -> >4023741.3045<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >APPROX POSITION XYZ< idx. 1 -> >309110.4584<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >APPROX POSITION XYZ< idx. 2 -> >4922723.1945<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >COMMENT< idx. 0 -> >HEADER CHANGED BY RMA-CISS<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >MARKER NAME< idx. 0 -> >P3RS04BEL<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >MARKER NUMBER< idx. 0 -> >0004<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >MARKER TYPE< idx. 0 -> >P3RS04BEL<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >OBSERVER / AGENCY< idx. 0 -> >CISS<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >OBSERVER / AGENCY< idx. 1 -> >RMA-BEL<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >REC # / TYPE / VERS< idx. 0 -> >BEP3RS2<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >REC # / TYPE / VERS< idx. 1 -> >P3RS2<
2021-02-09 14:28:25 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >REC # / TYPE / VERS< idx. 2 -> >001<
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: missing
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: E -> L1A not found
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: E -> L1B not found
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: E -> L6A not found
2021-02-09 14:28:25 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: G -> L1C not found
INFO: rnx15_combine.py - combine_rnx_obs: combined 13 RINEX files into /tmp/P3RS3110.20M
INFO: rnx15_combine.py - convert_navrnx3: adjusting RINEX header for P3RS3110.20M
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp /tmp/P3RS3110.20M -crux /tmp/tmpqei5s1w9 -f -sei in -chk -fout ::RX3::04,BEL
INFO:    process output = DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-02-09 14:28:30 | W | 0000-00-00 00:00:00.000 | P3RS | N | CRUX: (STRING) repair line >rnx_writer-1.0.0    P3RS-2 Receiver     20201106 091004 UTC PGM / RUN BY /DATE<
2021-02-09 14:28:30 | W | 0000-00-00 00:00:00.000 | P3RS | N | SKIP of EPOCH: not valid >2020 11 40 14 50 00.0000000<
2021-02-09 14:28:30 | W | 2020-11-06 09:00:00.000 | P3RS | N | wrong nav. value >4.756587184875e-234<
2021-02-09 14:28:30 | W | 2020-11-06 09:00:00.000 | P3RS | N | SKIP of EPOCH: not valid >2020 11 60 80 50 00.0000000<
2021-02-09 14:28:30 | W | 2020-11-06 08:50:00.000 | P3RS | N | wrong nav. value >1.375831935030e-233<
2021-02-09 14:28:30 | W | 2020-11-06 09:00:00.000 | P3RS | N | wrong nav. value >1.375831935030e-233<
2021-02-09 14:28:30 | W | 2020-11-06 08:50:00.000 | P3RS | N | wrong nav. value >1.375831935030e-233<
...
2021-02-09 14:28:35 | W | 2020-11-06 11:30:00.000 | P3RS | N | wrong nav. value >8.176072524854e-233<
2021-02-09 14:28:35 | W | 2020-11-06 11:30:00.000 | P3RS | N | SKIP of 202 records via input (EPOCH CHECK)
INFO: rnx15_combine.py - combine_rnx15: Project information =
{
    "cli": {
        "from_dir": "/home/amuls/RxTURP/BEGPIOS/P3RS2/LOG/pvt_ls/",
        "rnx_dir": "/home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/",
        "marker": "P3RS",
        "year": 2020,
        "doy": 311,
        "crux": "/home/amuls/amPython/rnxproc/p3rs2-obs.crux"
    },
    "dirs": {
        "rinex": "/home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/",
        "yydoy": "/home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/20311"
    },
    "bin": {
        "gfzrnx": "/home/amuls/bin/gfzrnx",
        "rnx2crz": "/home/amuls/bin/rnx2crz",
        "gzip": "/usr/bin/gzip"
    },
    "rnx": {
        "date": "2020-11-07",
        "obs3f": "P3RS04BEL_R_20203110000_01D_00U_MO.rnx",
        "nav3f": "P3RS04BEL_R_20203110000_01D_MN.rnx"
    },
    "p3rs2": {
        "obs": [
            "P3RS-2_RX_R_20203110910_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203110925_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111019_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111034_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111049_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111104_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111119_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111134_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111149_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111207_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111222_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111309_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203111324_15M_00U_MO.rnx"
        ],
        "nav": [
            "P3RS-2_RX_R_20203110910_15M_MN.rnx",
            "P3RS-2_RX_R_20203110925_15M_MN.rnx",
            "P3RS-2_RX_R_20203111019_15M_MN.rnx",
            "P3RS-2_RX_R_20203111034_15M_MN.rnx",
            "P3RS-2_RX_R_20203111049_15M_MN.rnx",
            "P3RS-2_RX_R_20203111104_15M_MN.rnx",
            "P3RS-2_RX_R_20203111119_15M_MN.rnx",
            "P3RS-2_RX_R_20203111134_15M_MN.rnx",
            "P3RS-2_RX_R_20203111149_15M_MN.rnx",
            "P3RS-2_RX_R_20203111207_15M_MN.rnx",
            "P3RS-2_RX_R_20203111222_15M_MN.rnx",
            "P3RS-2_RX_R_20203111309_15M_MN.rnx",
            "P3RS-2_RX_R_20203111324_15M_MN.rnx"
        ]
    }
}

```

\normalsize


### __prepare_rnx15.py__

`prepare_rnx15.py` calls script `rnx15_combine.py` and offers possibility to compress the obtained RINEX v3.x observation and navigation files.

#### Usage


\tiny
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ prepare_rnx15.py -h
usage: prepare_rnx15.py [-h] [-f FROM_DIR] [-r RNX_DIR] -m MARKER -y YEAR -d DOY [-c] [-l LOGGING LOGGING]

prepare_rnx15.py Combining partial (15 minutes) RINEX v3.x Obs/Nav files

optional arguments:
  -h, --help            show this help message and exit
  -f FROM_DIR, --from_dir FROM_DIR
                        Directory of 15 min P3RS2 data collection (default /home/amuls/RxTURP/BEGPIOS/P3RS2/LOG/pvt_ls/)
  -r RNX_DIR, --rnx_dir RNX_DIR
                        Root directory of P3RS2 RINEX files (default /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/)
  -m MARKER, --marker MARKER
                        marker name (4 chars)
  -y YEAR, --year YEAR  Year (4 digits)
  -d DOY, --doy DOY     day-of-year [1..366]
  -c, --compress        compress obtained RINEX files
  -l LOGGING LOGGING, --logging LOGGING LOGGING
                        specify logging level console/file (default INFO DEBUG)
```

\normalsize

#### Example run


\tiny
    
```bash
OUTPUT FROM RNX15_COMBINE.PY COMES HERE

INFO: >>>>>> prepare_rnx15.py - prepare_P3RS2_data: RINEX directory = /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/20311
INFO: >>>>>> prepare_rnx15.py - prepare_P3RS2_data: obtained RINEX observation file = P3RS04BEL_R_20203110000_01D_00U_MO.rnx
INFO: >>>>>> prepare_rnx15.py - prepare_P3RS2_data: obtained RINEX navigation files = P3RS04BEL_R_20203110000_01D_MN.rnx
INFO: location.py - locateProg: rnx2crz is /home/amuls/bin/rnx2crz
INFO: location.py - locateProg: gzip is /usr/bin/gzip
INFO: compress_utils.py - compress_rnx_obs: Compressing RINEX observation P3RS04BEL_R_20203110000_01D_00U_MO.rnx
INFO: amutils.py - run_subprocess: running
/home/amuls/bin/rnx2crz -f -d /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/20311/P3RS04BEL_R_20203110000_01D_00U_MO.rnx
INFO: >>>>>> prepare_rnx15.py - prepare_P3RS2_data: compressed RINEX observation file = P3RS04BEL_R_20203110000_01D_00U_MO.crx.Z
INFO: compress_utils.py - gzip_compress: Compressing RINEX navigation P3RS04BEL_R_20203110000_01D_MN.rnx
INFO: amutils.py - run_subprocess: running
/usr/bin/gzip -f /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/20311/P3RS04BEL_R_20203110000_01D_MN.rnx
INFO: >>>>>> prepare_rnx15.py - prepare_P3RS2_data: compressed RINEX navigation file = P3RS04BEL_R_20203110000_01D_MN.rnx.gz
INFO: prepare_rnx15.py - prepare_P3RS2_data: SBF preparation information =
{
    "dirs": {
        "pvt": "/home/amuls/RxTURP/BEGPIOS/P3RS2/LOG/pvt_ls/",
        "rnx_root": "/home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/",
        "yydoy": "/home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/20311"
    },
    "cli": {
        "marker": "P3RS",
        "yyyy": 2020,
        "doy": 311,
        "compress": true
    },
    "rnx": {
        "obs3f": "P3RS04BEL_R_20203110000_01D_00U_MO.rnx",
        "nav3f": "P3RS04BEL_R_20203110000_01D_MN.rnx",
        "obs3fc": "P3RS04BEL_R_20203110000_01D_00U_MO.crx.Z",
        "nav3fc": "P3RS04BEL_R_20203110000_01D_MN.rnx.gz"
    },
    "bin": {
        "rnx2crz": "/home/amuls/bin/rnx2crz",
        "gzip": "/usr/bin/gzip"
    }
}
```

\normalsize

#### Resulting directory structure

Output shown when compress option has been chosen.

\tiny
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ ls -l 20311/
total 1392
-rw-rw-r-- 1 amuls amuls 1218353 Feb  9 14:38 P3RS04BEL_R_20203110000_01D_00U_MO.crx.Z
-rw-rw-r-- 1 amuls amuls   20838 Feb  9 14:38 P3RS04BEL_R_20203110000_01D_MN.rnx.gz
-rw-rw-r-- 1 amuls amuls    2598 Feb  9 14:38 prepare_rnx15.log
-rw-rw-r-- 1 amuls amuls  173172 Feb  9 14:38 rnx15_combine.log
```

\normalsize

