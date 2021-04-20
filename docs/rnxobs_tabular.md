\newpage

## Converting and analysing RINEX files to observation tabular and statistics files

The following scripts convert the RINEX obtained files to a tabular observation file (`*.obstab`) and an overview of general observation statistics  file (`obsstat`). An analysis based on these files is performed and `LaTeX` sections are generated.

### __rnxobs_tabular.py__

`rnxobs_tabular.py` converts the RINEX file to the __statistics__ and  __tabular__ files and creates a summary `LaTeX` section used for reporting.

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ rnxobs_tabular.py  --help
usage: rnxobs_tabular.py [-h] --obsfile OBSFILE [--gnsss GNSSS [GNSSS ...]] [--logging LOGGING LOGGING]

rnxobs_tabular.py creates observation tabular/statistics file for selected GNSSs

optional arguments:
  -h, --help            show this help message and exit
  --obsfile OBSFILE     RINEX observation file
  --gnsss GNSSS [GNSSS ...]
                        select (1 or more) GNSS(s) to use (out of E|G, default E)
  --logging LOGGING LOGGING
                        specify logging level console/file (two of CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET, default INFO DEBUG)
```
    
\normalsize

#### Example run

\tiny
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ rnxobs_tabular.py \
        --obsfile ~/RxTURP/CHIRPSAWTOOTH/rnx/20349/TURX00BEL_R_20203491400_01H_01S_MO.rnx \
        --gnsss E
INFO: location.py - locateProg: gfzrnx is /home/amuls/bin/gfzrnx
INFO: rnxobs_analysis.py - RX3obs_header_info extracting observation header info \
            from TURX00BEL_R_20203491400_01H_01S_MO.rnx
INFO: amutils.py - run_subprocess: running
/home/amuls/bin/gfzrnx -finp TURX00BEL_R_20203491400_01H_01S_MO.rnx \
                       -fout TURX00BEL_R_20203491400_01H_01S_MO-obs.json  \
                       -meta basic:json -f
INFO: rnxobs_tabular.py - main_rnx_obstab: dGFZ[hdr] =
{
    "data": {
        "epoch": {
            "first": "2020 12 14 14 00 00.0000000",
            "last": "2020 12 14 14 59 59.0000000"
        }
    },
    "file": {
        "duration": "3600",
        "epo_first": "2020 12 14 14 00 00.0000000",
        "epo_first_name": "2020 12 14 14 00 00.0000000",
        "interval": "1.000",
        "md5": "031c398b308f4e4a15dff54ffa5ecbe1",
        "name": "TURX00BEL_R_20203491400_01H_01S_MO.rnx",
        "pgm": "sbf2rin-13.4.5",
        "pgm_date": "20210318 121941 UTC",
        "pgm_runby": "",
        "satsys": "E",
        "site": "TURX00BEL",
        "source": "R",
        "sysfrq": {
            "E": [
                "1",
                "6"
            ]
        },
        "sysobs": {
            "E": [
                "C1A",
                "C6A",
                "D1A",
                "D6A",
                "L1A",
                "L6A",
                "S1A",
                "S6A"
            ]
        },
        "sysobs_num": {
            "E": 8
        },
        "sysobs_sum": 8,
        "system": "E",
        "systyp": {
            "E": [
                "C",
                "D",
                "L",
                "S"
            ]
        },
        "type": "O",
        "version": "3.04"
    }
}
INFO: rnxobs_tabular.py - main_rnx_obstab: dGFZ =
{
    "info": {
        "obs_date": "14 December 2020",
        "marker": "TURX00BEL",
        "yyyy": 2020,
        "doy": 349
    },
    "cli": {
        "GNSSs": [
            "E"
        ],
        "obsf": "TURX00BEL_R_20203491400_01H_01S_MO.rnx",
        "path": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349"
    },
    "bin": {
        "gfzrnx": "/home/amuls/bin/gfzrnx"
    },
    "hdr": {
        "data": {
            "epoch": {
                "first": "2020 12 14 14 00 00.0000000",
                "last": "2020 12 14 14 59 59.0000000"
            }
        },
        "file": {
            "duration": "3600",
            "epo_first": "2020 12 14 14 00 00.0000000",
            "epo_first_name": "2020 12 14 14 00 00.0000000",
            "interval": "1.000",
            "md5": "031c398b308f4e4a15dff54ffa5ecbe1",
            "name": "TURX00BEL_R_20203491400_01H_01S_MO.rnx",
            "pgm": "sbf2rin-13.4.5",
            "pgm_date": "20210318 121941 UTC",
            "pgm_runby": "",
            "satsys": "E",
            "site": "TURX00BEL",
            "source": "R",
            "sysfrq": {
                "E": [
                    "1",
                    "6"
                ]
            },
            "sysobs": {
                "E": [
                    "C1A",
                    "C6A",
                    "D1A",
                    "D6A",
                    "L1A",
                    "L6A",
                    "S1A",
                    "S6A"
                ]
            },
            "sysobs_num": {
                "E": 8
            },
            "sysobs_sum": 8,
            "system": "E",
            "systyp": {
                "E": [
                    "C",
                    "D",
                    "L",
                    "S"
                ]
            },
            "type": "O",
            "version": "3.04"
        }
    },
    "ltx": {
        "path": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349/ltx"
    },
    "obstab": {},
    "obshdr": "TURX00BEL_R_20203491400_01H_01S_MO.obshdr"
}
INFO: rnxobs_tabular.py - create_tabular_observations \
                        creating observation tabular file TURX00BEL_R_20203491400_01H_01S_MO_E.obstab
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp TURX00BEL_R_20203491400_01H_01S_MO.rnx \
                       -tab_obs -fout TURX00BEL_R_20203491400_01H_01S_MO_E.obstab \
                       -f -tab_sep , -satsys E
proc_out = 
DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-04-20 16:26:57 | W | 0000-00-00 00:00:00.000 | TURX | O | mismatch between header MARKER NAME (TURX) and file/station name (TURX00BEL) / using >TURX<
INFO: rnxobs_tabular.py - create_tabular_observations creating observation statistics file TURX00BEL_R_20203491400_01H_01S_MO_E.obsstat
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp TURX00BEL_R_20203491400_01H_01S_MO.rnx -stk_obs -fout TURX00BEL_R_20203491400_01H_01S_MO_E.obsstat -f -satsys E
proc_out = 
DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-04-20 16:26:58 | W | 0000-00-00 00:00:00.000 | TURX | O | mismatch between header MARKER NAME (TURX) and file/station name (TURX00BEL) / using >TURX<
INFO: rnxobs_tabular.py - main_rnx_obstab: Project information =
{
    "info": {
        "obs_date": "14 December 2020",
        "marker": "TURX00BEL",
        "yyyy": 2020,
        "doy": 349
    },
    "cli": {
        "GNSSs": [
            "E"
        ],
        "obsf": "TURX00BEL_R_20203491400_01H_01S_MO.rnx",
        "path": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349"
    },
    "bin": {
        "gfzrnx": "/home/amuls/bin/gfzrnx"
    },
    "hdr": {
        "data": {
            "epoch": {
                "first": "2020 12 14 14 00 00.0000000",
                "last": "2020 12 14 14 59 59.0000000"
            }
        },
        "file": {
            "duration": "3600",
            "epo_first": "2020 12 14 14 00 00.0000000",
            "epo_first_name": "2020 12 14 14 00 00.0000000",
            "interval": "1.000",
            "md5": "031c398b308f4e4a15dff54ffa5ecbe1",
            "name": "TURX00BEL_R_20203491400_01H_01S_MO.rnx",
            "pgm": "sbf2rin-13.4.5",
            "pgm_date": "20210318 121941 UTC",
            "pgm_runby": "",
            "satsys": "E",
            "site": "TURX00BEL",
            "source": "R",
            "sysfrq": {
                "E": [
                    "1",
                    "6"
                ]
            },
            "sysobs": {
                "E": [
                    "C1A",
                    "C6A",
                    "D1A",
                    "D6A",
                    "L1A",
                    "L6A",
                    "S1A",
                    "S6A"
                ]
            },
            "sysobs_num": {
                "E": 8
            },
            "sysobs_sum": 8,
            "system": "E",
            "systyp": {
                "E": [
                    "C",
                    "D",
                    "L",
                    "S"
                ]
            },
            "type": "O",
            "version": "3.04"
        }
    },
    "ltx": {
        "path": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349/ltx",
        "script": "/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349/ltx/TURX00BEL_01_E_script_info"
    },
    "obstab": {
        "E": {
            "obs_E_tabf": "TURX00BEL_R_20203491400_01H_01S_MO_E.obstab",
            "obs_E_statf": "TURX00BEL_R_20203491400_01H_01S_MO_E.obsstat"
        }
    },
    "obshdr": "TURX00BEL_R_20203491400_01H_01S_MO.obshdr"
}
dObstabs = {'E': {'obs_E_tabf': 'TURX00BEL_R_20203491400_01H_01S_MO_E.obstab', 'obs_E_statf': 'TURX00BEL_R_20203491400_01H_01S_MO_E.obsstat'}}
```
    
\normalsize

#### Resulting directory structure

\scriptsize
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ ll -R
.:
total 569628
drwxrwxr-x 2 amuls amuls      4096 Mar  2 14:37 ltx
-rw-rw-r-- 1 amuls amuls      1631 Mar  2 14:10 prepare_sbf2rnx.log
-rw-rw-r-- 1 amuls amuls      9873 Mar  2 14:44 rnxobs_tabular_py.log
-rw-rw-r-- 1 amuls amuls       475 Mar  2 14:10 sbf_rinex.json
-rw-rw-r-- 1 amuls amuls      2075 Mar  2 14:10 sbf_rinex_py.log
-rw-rw-r-- 1 amuls amuls      1537 Mar  2 14:44 SEPT00BEL_R_20191340000_01D_01S_MO_E.obsstat
-rw-rw-r-- 1 amuls amuls  89775895 Mar  2 14:44 SEPT00BEL_R_20191340000_01D_01S_MO_E.obstab
-rw-rw-r-- 1 amuls amuls      3969 Mar  2 14:43 SEPT00BEL_R_20191340000_01D_01S_MO_G.obsstat
-rw-rw-r-- 1 amuls amuls 179788882 Mar  2 14:42 SEPT00BEL_R_20191340000_01D_01S_MO_G.obstab
-rw-rw-r-- 1 amuls amuls      1172 Mar  2 14:41 SEPT00BEL_R_20191340000_01D_01S_MO-obs.json
-rw-rw-r-- 1 amuls amuls 312972740 Mar  2 14:10 SEPT00BEL_R_20191340000_01D_01S_MO.rnx
-rw-rw-r-- 1 amuls amuls    711736 Mar  2 14:10 SEPT00BEL_R_20191340000_01D_MN.rnx
-rw-rw-r-- 1 amuls amuls     97118 Mar  2 16:57 obsstat_analyse_py.log
-rw-rw-r-- 1 amuls amuls       834 Mar  2 16:57 obsstat_analyse.json

./ltx:
total 4
-rw-rw-r-- 1 amuls amuls 1296 Apr 20 16:26 TURX00BEL_01_E_script_info.tex
```


\normalsize

The `*.obstab` and `*.obsstat` files are Comma Separated Values (CVS).

#### Latex section created `TURX00BEL_01_E_script_info.tex`
 
\scriptsize

```
\subsection{Script details}%
\label{subsec:Scriptdetails}%
\subsubsection{Program information}%
\label{ssubsec:Programinformation}%
\setlength{\tabcolsep}{4pt}%
\begin{longtabu}[l]{rcl}%
Script&:&rnxobs\_tabular.py\\%
Run at&:&20/04/2021 16:26\\%
Run by&:&A. Muls\\%
&&Royal Military Academy\\%
\end{longtabu}

%
\subsubsection{Parameters}%
\label{ssubsec:Parameters}%
\setlength{\tabcolsep}{4pt}%
\begin{longtabu}[l]{rcl}%
RINEX root directory&:&/home/amuls/RxTURP/CHIRPSAWTOOTH/rnx/20349\\%
RINEX observation file&:&TURX00BEL\_R\_20203491400\_01H\_01S\_MO.rnx\\%
RINEX version&:&3.04\\%
Marker&:&TURX00BEL\\%
Year/day{-}of{-}year&:&2020/349\\%
&&\\%
\end{longtabu}

%
\subsubsection{Observation header information}%
\label{ssubsec:Observationheaderinformation}%
\setlength{\tabcolsep}{4pt}%
\begin{longtabu}[l]{rcl}%
First epoch&:&2020/12/14 14:00:00\\%
Last epoch&:&2020/12/14 14:59:59\\%
Interval&:&1.0\\%
&&\\%
GNSS&:&E (Galileo) \\%
Frequencies E&:&1, 6\\%
&&\\%
Observable types&:&S (Pseudorange) \\%
&:&C (SNR) \\%
&:&D (Doppler) \\%
&:&L (Carrier) \\%
&&\\%
\end{longtabu}

%
\subsubsection{Logged observables}%
\label{ssubsec:Loggedobservables}%
\setlength{\tabcolsep}{4pt}%
\begin{longtabu}[l]{rcl}%
Observable types E&:&C1A, C6A, D1A, D6A, L1A, L6A, S1A, S6A\\%
&&\\%
\end{longtabu}
```

\normalsize
