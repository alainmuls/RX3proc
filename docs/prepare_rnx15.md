

## Combining (15 minutes) P3RS2 RINEX files into daily RINEX v3.x files
    

### __rnx15_combine.py__

`rnx15_combine.py` combines the 15 minutes RINEX files from P3RS2 Rx for a specific day to create observation and navigation files in correct RINEX v3.x format.

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ rnx15_combine.py --help
usage: rnx15_combine.py [-h] [--from_dir FROM_DIR] [--rnx_dir RNX_DIR] --marker MARKER --year YEAR \
         --doy DOY [--startepoch STARTEPOCH] [--endepoch ENDEPOCH] [--crux CRUX] [--logging LOGGING LOGGING]

rnx15_combine.py combines P3RS2 RINEX observation / navigation files

optional arguments:
  -h, --help            show this help message and exit
  --from_dir FROM_DIR   Directory of P3RS2 RINEX files (default .)
  --rnx_dir RNX_DIR     Root directory of P3RS2 RINEX files (default /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/)
  --marker MARKER       marker name (4 chars)
  --year YEAR           Year (4 digits)
  --doy DOY             day-of-year [1..366]
  --startepoch STARTEPOCH
                        specify start epoch hh:mm:ss (default 00:00:00)
  --endepoch ENDEPOCH   specify end epoch hh:mm:ss (default 23:59:59)
  --crux CRUX           CRUX template file for updating RINEX headers (default /home/amuls/amPython/RX3proc/gfzrnx/P3RS2-obs.crux)
  --logging LOGGING LOGGING
                        specify logging level console/file (two of CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET, default INFO DEBUG)
```
    
\normalsize


#### Example run


\tiny
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ rnx15_combine.py --from_dir ~/RxTURP/CHIRPSAWTOOTH/P3RS2/ORIGS/ \
            --rnx_dir ~/RxTURP/CHIRPSAWTOOTH/rnx/  --year 2020 --doy 349 --marker P3RS \
            --startepoch='14:06:45' --endepoch='14:55:30'
INFO: location.py - locateProg: gfzrnx is /home/amuls/bin/gfzrnx
INFO: location.py - locateProg: rnx2crz is /home/amuls/bin/rnx2crz
INFO: location.py - locateProg: gzip is /usr/bin/gzip
INFO: rnx15_combine.py - list_rinex_files: found 5 RINEX observation files
INFO: rnx15_combine.py - list_rinex_files: found 5 RINEX navigation files
INFO: rnx15_combine.py - create_crux_file: created crux file /tmp/tmpdzx548q3
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203491354_15M_00U_MO.rnx: ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', 'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203491409_15M_00U_MO.rnx: ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', 'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203491424_15M_00U_MO.rnx: ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', 'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203491439_15M_00U_MO.rnx: ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', 'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: P3RS-2_RX_R_20203491454_15M_00U_MO.rnx: ['E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A D6A S6A      SYS / # / OBS TYPES\n', 'G    4 C1C L1C D1C S1C                                      SYS / # / OBS TYPES\n']
DEBUG: rnx15_combine.py - check_obstypes_order: obs types found
                                                   E                                                  G
0  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
1  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
2  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
3  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
4  E   12 C1B L1B D1B S1B C1A L1A D1A S1A C6A L6A...  G    4 C1C L1C D1C S1C                        ...
INFO: rnx15_combine.py - combine_rnx_obs: combined 5 RINEX files into /tmp/P3RS3490.20O
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp /tmp/P3RS3490.20O -nomren23 04,BEL
INFO: rnx15_combine.py - convert_obsrnx3: adjusting RINEX header for P3RS3490.20O
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp /tmp/P3RS3490.20O -crux /tmp/tmpdzx548q3 -f -fout /home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349/P3RS04BEL_R_20203490000_01D_00U_MO.rnx -epo_beg 2020349_140645 -d 2940
INFO:    process output = DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | the data are filtered by epoch interval 2020 12 14 14 06 45.0000000 - 2020 12 14 14 55 45.0000000
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | CRUX: (STRING) repair line >rnx_writer-1.0.0    P3RS-2 Receiver     20201214 135422 UTC PGM / RUN BY /DATE<
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | no MARKER NAME in header / taken from file name
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | mismatch between header MARKER NAME () and file/station name (P3RS) / using >P3RS<
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | CRUX: skip >G                                                           SYS / PHASE SHIFT<
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | CRUX: skip >  0                                                         GLONASS SLOT / FRQ #<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >ANT # / TYPE< idx. 0 -> >BEANT<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >ANT # / TYPE< idx. 1 -> >NAVXPERIENCE<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >APPROX POSITION XYZ< idx. 0 -> >4023741.3045<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >APPROX POSITION XYZ< idx. 1 -> >309110.4584<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >APPROX POSITION XYZ< idx. 2 -> >4922723.1945<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >COMMENT< idx. 0 -> >HEADER CHANGED BY RMA-CISS<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >MARKER NAME< idx. 0 -> >P3RS04BEL<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >MARKER NUMBER< idx. 0 -> >0004<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >MARKER TYPE< idx. 0 -> >P3RS04BEL<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >OBSERVER / AGENCY< idx. 0 -> >CISS<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >OBSERVER / AGENCY< idx. 1 -> >RMA-BEL<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >REC # / TYPE / VERS< idx. 0 -> >BEP3RS2<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >REC # / TYPE / VERS< idx. 1 -> >P3RS2<
2021-04-02 16:17:47 | N | 0000-00-00 00:00:00.000 | P3RS | O | update of head label >REC # / TYPE / VERS< idx. 2 -> >001<
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: missing
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: E -> L1A not found
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: E -> L1B not found
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: E -> L6A not found
2021-04-02 16:17:47 | W | 0000-00-00 00:00:00.000 | P3RS | O | header SYS / PHASE SHIFT: G -> L1C not found
2021-04-02 16:17:47 | W | 2020-12-14 14:22:00.980 | P3RS | O | mismatch of number of satellites(6) and records got(5) 2020-12-14 14:22:00.9800855 !
2021-04-02 16:17:47 | W | 2020-12-14 14:22:04.980 | P3RS | O | mismatch of number of satellites(6) and records got(5) 2020-12-14 14:22:04.9800855 !
2021-04-02 16:17:47 | W | 2020-12-14 14:22:05.980 | P3RS | O | mismatch of number of satellites(5) and records got(4) 2020-12-14 14:22:05.9800855 !
...
...
2021-04-02 16:17:48 | W | 2020-12-14 14:47:00.980 | P3RS | O | mismatch of number of satellites(6) and records got(5) 2020-12-14 14:47:00.9800855 !
INFO: rnx15_combine.py - combine_rnx_obs: combined 5 RINEX files into /tmp/P3RS3490.20M
INFO: rnx15_combine.py - convert_navrnx3: adjusting RINEX header for P3RS3490.20M
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp /tmp/P3RS3490.20M -crux /tmp/tmpdzx548q3 -f -sei in -chk -fout ::RX3::04,BEL
INFO:    process output = DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-04-02 16:17:48 | N | 0000-00-00 00:00:00.000 | P3RS | M | the data are filtered by epoch interval 2020 12 14 00 00 00.0000000 - 2020 12 15 00 00 00.0000000
2021-04-02 16:17:48 | W | 0000-00-00 00:00:00.000 | P3RS | N | CRUX: (STRING) repair line >rnx_writer-1.0.0    P3RS-2 Receiver     20201214 134005 UTC PGM / RUN BY /DATE<
2021-04-02 16:17:48 | W | 2020-12-14 13:20:00.000 | P3RS | N | wrong nav. value >1.375831935030e-233<
2021-04-02 16:17:48 | W | 2020-12-14 13:20:00.000 | P3RS | N | skip of NAV record for PRN E05 (2020-12-14 13:20:00.0000000_  -3.2136233718e-04) !
2021-04-02 16:17:48 | W | 2020-12-14 13:20:00.000 | P3RS | N | wrong nav. value >1.375831935030e-233<
2021-04-02 16:17:48 | W | 2020-12-14 13:20:00.000 | P3RS | N | skip of NAV record for PRN E05 (2020-12-14 13:20:00.0000000_  -3.2136233718e-04) !
...
...
2021-04-02 16:17:52 | W | 2020-12-14 14:10:00.000 | P3RS | N | wrong nav. value >1.375831935030e-233<
2021-04-02 16:17:52 | W | 2020-12-14 14:10:00.000 | P3RS | N | skip of NAV record for PRN E07 (2020-12-14 14:10:00.0000000_  -4.7450343101e-04) !
INFO: rnx15_combine.py - main_combine_rnx15: Project information =
{
    "cli": {
        "from_dir": "/home/amuls/RxTURP/CHIRPSAWTOOTH/P3RS2/ORIGS/",
        "rnx_dir": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/",
        "marker": "P3RS",
        "year": 2020,
        "doy": 349,
        "start_ep": "14:06:45",
        "end_ep": "14:55:30",
        "crux": "/home/amuls/amPython/RX3proc/gfzrnx/P3RS2-obs.crux"
    },
    "dirs": {
        "rinex": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/",
        "yydoy": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349"
    },
    "bin": {
        "gfzrnx": "/home/amuls/bin/gfzrnx",
        "rnx2crz": "/home/amuls/bin/rnx2crz",
        "gzip": "/usr/bin/gzip"
    },
    "rnx": {
        "date": "2020-12-15",
        "obs3f": "P3RS04BEL_R_20203490000_01D_00U_MO.rnx",
        "nav3f": "SEPT00BEL_R_20203491041_03H_MN.rnx"
    },
    "p3rs2": {
        "obs": [
            "P3RS-2_RX_R_20203491354_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203491409_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203491424_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203491439_15M_00U_MO.rnx",
            "P3RS-2_RX_R_20203491454_15M_00U_MO.rnx"
        ],
        "nav": [
            "P3RS-2_RX_R_20203491340_15M_MN.rnx",
            "P3RS-2_RX_R_20203491355_15M_MN.rnx",
            "P3RS-2_RX_R_20203491410_15M_MN.rnx",
            "P3RS-2_RX_R_20203491425_15M_MN.rnx",
            "P3RS-2_RX_R_20203491440_15M_MN.rnx"
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
[amuls:~/amPython/RX3proc] [RX3proc]$ prepare_rnx15.py --help
usage: prepare_rnx15.py [-h] [--root_dir ROOT_DIR] [--rnx_dir RNX_DIR] --marker MARKER --year YEAR --doy DOY [--startepoch STARTEPOCH] [--endepoch ENDEPOCH] [--obs_crux OBS_CRUX] [--compress] [--logging LOGGING LOGGING]

prepare_rnx15.py Combining partial (15 minutes) RINEX v3.x Obs/Nav files

optional arguments:
  -h, --help            show this help message and exit
  --root_dir ROOT_DIR   Directory of 15 min P3RS2 data collection (default /home/amuls/RxTURP/BEGPIOS/P3RS2/LOG/pvt_ls/)
  --rnx_dir RNX_DIR     Root directory of P3RS2 RINEX files (default /home/amuls/RxTURP/BEGPIOS/P3RS2/rinex/)
  --marker MARKER       marker name (4 chars)
  --year YEAR           Year (4 digits)
  --doy DOY             day-of-year [1..366]
  --startepoch STARTEPOCH
                        specify start epoch hh:mm:ss (default 00:00:00)
  --endepoch ENDEPOCH   specify end epoch hh:mm:ss (default 23:59:59)
  --obs_crux OBS_CRUX   CRUX template file for updating RINEX headers (default /home/amuls/amPython/RX3proc/gfzrnx/P3RS2-obs.crux)
  --compress            compress obtained RINEX files
  --logging LOGGING LOGGING
                        specify logging level console/file (default INFO DEBUG)
```

\normalsize

#### Example run


\tiny
    
```bash
prepare_sbf2rnx.py --root_dir /media/amuls/porsche/RxTURP/CMT/ --marker TURP --year 2021 --doy 89 --compress --rnxdir /media/amuls/porsche/RxTURP/CMT/rnx/
INFO: === prepare_sbf2rnx.py - combine_sbffiles: passing control to sbf_daily.py (options: --dir /media/amuls/porsche/RxTURP/CMT/TURP/21089) ===
INFO: sbf_daily.py - main_combine_sbf: working directory is /media/amuls/porsche/RxTURP/CMT/TURP/21089
INFO: sbf_daily.py - main_combine_sbf: changed to directory /media/amuls/porsche/RxTURP/CMT/TURP/21089
INFO: sbf_daily.py - main_combine_sbf: combine SBF (six-)hourly files to daily SBF file
INFO: sbf_daily.py - main_combine_sbf: reusing daily SBF file TURX0890.21_
INFO: >>>>>> prepare_sbf2rnx.py - main_prepare_rnx_data: obtained daily SBF file = TURX0890.21_
INFO: === prepare_sbf2rnx.py - sbf_rnx3: passing control to sbf_rinex.py  (options: --sbff /media/amuls/porsche/RxTURP/CMT/TURP/21089/TURX0890.21_ --rnxdir /media/amuls/porsche/RxTURP/CMT/rnx/) ===
INFO: sbf_rinex.py - main_sbf2rnx3: arguments processed: dRnx = {'dirs': {'sbf': '/media/amuls/porsche/RxTURP/CMT/TURP/21089', 'rnx': PosixPath('/media/amuls/porsche/RxTURP/CMT/rnx')}, 'sbff': 'TURX0890.21_', 'time': {'startepoch': '00:00:00', 'endepoch': '23:59:59'}}
INFO: sbf_rinex.py - checkValidityArgs: check existence of sbfDir /media/amuls/porsche/RxTURP/CMT/TURP/21089
INFO: sbf_rinex.py - checkValidityArgs: check existence of binary file /media/amuls/porsche/RxTURP/CMT/TURP/21089/TURX0890.21_ to convert
INFO: sbf_rinex.py - checkValidityArgs: check existence of rnxdir /media/amuls/porsche/RxTURP/CMT/rnx and create if needed
INFO: location.py - locateProg: sbf2rin is /opt/Septentrio/RxTools/bin/sbf2rin
INFO: sbf_rinex.py - main_sbf2rnx3: convert binary file to rinex
INFO: sbf_rinex.py - sbf2rinex: RINEX conversion from SBF binary
INFO: sbf_rinex.py - sbf2rinex: creating RINEX observation file
INFO: amutils.py - run_subprocess_output: running
/opt/Septentrio/RxTools/bin/sbf2rin -f /media/amuls/porsche/RxTURP/CMT/TURP/21089/TURX0890.21_ -x RSCJI -s -D -v -R3 -l -O BEL
Creating RINEX file: done                                                                      |  0%
INFO: sbf_rinex.py - sbf2rinex: creating RINEX navigation file
INFO: amutils.py - run_subprocess_output: running
/opt/Septentrio/RxTools/bin/sbf2rin -f /media/amuls/porsche/RxTURP/CMT/TURP/21089/TURX0890.21_ -x RSCJI -s -D -v -n P -R3 -l -O BEL
Creating RINEX file: done                                                                      |  0%
INFO: sbf_rinex.py - sbf2rinex: sorted list (by modification time) of rnx files:
/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210881014_13H_01S_MO.rnx
/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210881014_13H_MN.rnx
/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_01S_MO.rnx
/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx
INFO: sbf_rinex.py - main_sbf2rnx3: dRnx =
{
    "dirs": {
        "sbf": "/media/amuls/porsche/RxTURP/CMT/TURP/21089",
        "rnx": "/media/amuls/porsche/RxTURP/CMT/rnx"
    },
    "sbff": "TURX0890.21_",
    "time": {
        "startepoch": "00:00:00",
        "endepoch": "23:59:59"
    },
    "bin": {
        "SBF2RIN": "/opt/Septentrio/RxTools/bin/sbf2rin"
    },
    "obs3f": "/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_01S_MO.rnx",
    "nav3f": "/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx"
}
INFO: >>>>>> prepare_sbf2rnx.py - main_prepare_rnx_data: obtained RINEX observation file = /media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_01S_MO.rnx
INFO: >>>>>> prepare_sbf2rnx.py - main_prepare_rnx_data: obtained RINEX navigation files = /media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx
INFO: location.py - locateProg: rnx2crz is /home/amuls/bin/rnx2crz
INFO: location.py - locateProg: gzip is /usr/bin/gzip
INFO: compress_utils.py - compress_rnx_obs: Compressing RINEX observation /media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_01S_MO.rnx
INFO: amutils.py - run_subprocess: running
/home/amuls/bin/rnx2crz -f -d /media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_01S_MO.rnx
INFO: >>>>>> prepare_sbf2rnx.py - main_prepare_rnx_data: compressed RINEX observation file = /media/amuls/porsche/RxTURP/CMT/rnx/ASTX02BEL_R_20210890600_09H_01S_MO.crx.Z
INFO: compress_utils.py - gzip_compress: Compressing RINEX navigation /media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx
INFO: amutils.py - run_subprocess: running
/usr/bin/gzip -f /media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx
INFO: >>>>>> prepare_sbf2rnx.py - main_prepare_rnx_data: compressed RINEX navigation file = /media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx.gz
INFO: prepare_sbf2rnx.py - main_prepare_rnx_data: SBF preparation information =
{
    "dirs": {
        "root": "/media/amuls/porsche/RxTURP/CMT/",
        "sbf": "/media/amuls/porsche/RxTURP/CMT/TURP/21089",
        "rnxdir": "/media/amuls/porsche/RxTURP/CMT/rnx/"
    },
    "cli": {
        "marker": "TURP",
        "yyyy": 2021,
        "doy": 89,
        "startepoch": "00:00:00",
        "endepoch": "23:59:59",
        "compress": true,
        "overwrite": false
    },
    "rnx": {
        "obs3f": "/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_01S_MO.rnx",
        "nav3f": "/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx",
        "obs3fc": "/media/amuls/porsche/RxTURP/CMT/rnx/ASTX02BEL_R_20210890600_09H_01S_MO.crx.Z",
        "nav3fc": "/media/amuls/porsche/RxTURP/CMT/rnx/TURX00BEL_R_20210890000_13H_MN.rnx.gz"
    },
    "sbffile": "TURX0890.21_",
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
[amuls:~/amPython/RX3proc] [RX3proc]$ ls -l 20311/
total 1392
-rw-rw-r-- 1 amuls amuls 1218353 Feb  9 14:38 P3RS04BEL_R_20203110000_01D_00U_MO.crx.Z
-rw-rw-r-- 1 amuls amuls   20838 Feb  9 14:38 P3RS04BEL_R_20203110000_01D_MN.rnx.gz
-rw-rw-r-- 1 amuls amuls    2598 Feb  9 14:38 prepare_rnx15.log
-rw-rw-r-- 1 amuls amuls  173172 Feb  9 14:38 rnx15_combine.log
```

\normalsize

