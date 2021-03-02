\newpage

## Converting and analysing RINEX files to observation tabular and statistics files

The following scripts convert the RINEX obtained files to a tabular observation file (`*.obstab`) and an overview of general observation statistics  file (`obsstat`). An analysis based on these files is performed and `LaTeX` sections are generated.

### __rnxobs_tabular.py__

`rnxobs_tabular.py` converts the RINEX file to the tabular and statistics files and creates a summary `LaTeX`section for the report.

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ rnxobs_tabular.py --help
usage: rnxobs_tabular.py [-h] -r RNXOBSF [-g GNSSS [GNSSS ...]] [-l LOGGING LOGGING]

rnxobs_tabular.py creates observation tabular/statistics file for selected GNSSs

optional arguments:
  -h, --help            show this help message and exit
  -r RNXOBSF, --rnxobsf RNXOBSF
                        RINEX observation file
  -g GNSSS [GNSSS ...], --gnsss GNSSS [GNSSS ...]
                        select (1 or more) GNSS(s) to use (out of E|G, default E)
  -l LOGGING LOGGING, --logging LOGGING LOGGING
                        specify logging level console/file (two of CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET, default INFO DEBUG)
```
    
\normalsize

#### Example run

\tiny
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ rnxobs_tabular.py --rnxobsf ~/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.rnx \
        -g G E
INFO: location.py - locateProg: gfzrnx is /home/amuls/bin/gfzrnx
INFO: rnxobs_analysis.py - RX3obs_header_info extracting observation header info from SEPT00BEL_R_20191340000_01D_01S_MO.rnx
INFO: amutils.py - run_subprocess: running
/home/amuls/bin/gfzrnx -finp SEPT00BEL_R_20191340000_01D_01S_MO.rnx -fout SEPT00BEL_R_20191340000_01D_01S_MO-obs.json -meta basic:json -f

. . .

ltx_gfzrnx_report.py - report_information: report creation information {'title': NoEscape(Analysis of observations

14 May 2019), 'subtitle': NoEscape(Receiver SEPT00BEL @ 2019/134), 'author': ['A. Muls'], 'company': ['Royal Military Academy'], 'classification': '  '}

. . .

INFO: rnxobs_tabular.py - create_tabular_observations creating observation tabular file SEPT00BEL_R_20191340000_01D_01S_MO_G.obstab
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp SEPT00BEL_R_20191340000_01D_01S_MO.rnx -tab_obs -fout SEPT00BEL_R_20191340000_01D_01S_MO_G.obstab -f -tab_sep , -satsys G
proc_out = 
DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-03-02 14:41:35 | W | 0000-00-00 00:00:00.000 | SEPT | O | mismatch between header MARKER NAME (SEPT) and file/station name (SEPT00BEL) / using >SEPT<
2021-03-02 14:42:09 | W | 2019-05-14 23:59:59.000 | SEPT | O | mismatch of number of satellites(20) and records got(11) 2019 05 14 23 59 59.0000000 !
2021-03-02 14:42:13 | N | 2019-05-14 23:59:59.000 | SEPT | O | 734601 records skipped via input (SEPT00BEL_R_20191340000_01D_01S_MO.rnx)
INFO: rnxobs_tabular.py - create_tabular_observations creating observation statistics file SEPT00BEL_R_20191340000_01D_01S_MO_G.obsstat
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp SEPT00BEL_R_20191340000_01D_01S_MO.rnx -stk_obs -fout SEPT00BEL_R_20191340000_01D_01S_MO_G.obsstat -f -satsys G
proc_out = 
DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-03-02 14:42:42 | W | 0000-00-00 00:00:00.000 | SEPT | O | mismatch between header MARKER NAME (SEPT) and file/station name (SEPT00BEL) / using >SEPT<
2021-03-02 14:43:16 | W | 2019-05-14 23:59:59.000 | SEPT | O | mismatch of number of satellites(20) and records got(11) 2019 05 14 23 59 59.0000000 !
2021-03-02 14:43:20 | N | 2019-05-14 23:59:59.000 | SEPT | O | 734601 records skipped via input (SEPT00BEL_R_20191340000_01D_01S_MO.rnx)
INFO: rnxobs_tabular.py - create_tabular_observations creating observation tabular file SEPT00BEL_R_20191340000_01D_01S_MO_E.obstab
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp SEPT00BEL_R_20191340000_01D_01S_MO.rnx -tab_obs -fout SEPT00BEL_R_20191340000_01D_01S_MO_E.obstab -f -tab_sep , -satsys E
proc_out = 
DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-03-02 14:43:23 | W | 0000-00-00 00:00:00.000 | SEPT | O | mismatch between header MARKER NAME (SEPT) and file/station name (SEPT00BEL) / using >SEPT<
2021-03-02 14:43:48 | W | 2019-05-14 23:59:59.000 | SEPT | O | mismatch of number of satellites(20) and records got(9) 2019 05 14 23 59 59.0000000 !
2021-03-02 14:43:51 | N | 2019-05-14 23:59:59.000 | SEPT | O | 957276 records skipped via input (SEPT00BEL_R_20191340000_01D_01S_MO.rnx)
INFO: rnxobs_tabular.py - create_tabular_observations creating observation statistics file SEPT00BEL_R_20191340000_01D_01S_MO_E.obsstat
INFO: amutils.py - run_subprocess_output: running
/home/amuls/bin/gfzrnx -finp SEPT00BEL_R_20191340000_01D_01S_MO.rnx -stk_obs -fout SEPT00BEL_R_20191340000_01D_01S_MO_E.obsstat -f -satsys E
proc_out = 
DATE/TIME           | C | EPOCH / FILE            | SITE | T | MESSAGE
--------------------+---+-------------------------+------+---+-----------------------------------------------------------...
2021-03-02 14:44:04 | W | 0000-00-00 00:00:00.000 | SEPT | O | mismatch between header MARKER NAME (SEPT) and file/station name (SEPT00BEL) / using >SEPT<
2021-03-02 14:44:29 | W | 2019-05-14 23:59:59.000 | SEPT | O | mismatch of number of satellites(20) and records got(9) 2019 05 14 23 59 59.0000000 !
2021-03-02 14:44:31 | N | 2019-05-14 23:59:59.000 | SEPT | O | 957276 records skipped via input (SEPT00BEL_R_20191340000_01D_01S_MO.rnx)
INFO: rnxobs_tabular.py - rnx_tabular: Project information =
{
    "info": {
        "obs_date": "14 May 2019",
        "marker": "SEPT00BEL",
        "yyyy": 2019,
        "doy": 134
    },
    "cli": {
        "GNSSs": [
            "G",
            "E"
        ],
        "obsf": "SEPT00BEL_R_20191340000_01D_01S_MO.rnx",
        "path": "/home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134"
    },
    "bin": {
        "gfzrnx": "/home/amuls/bin/gfzrnx"
    },
    "hdr": {
        "data": {
            "epoch": {
                "first": "2019 05 14 00 00 00.0000000",
                "last": "2019 05 14 23 59 59.0000000"
            }
        },
        "file": {
            "duration": "86400",
            "epo_first": "2019 05 14 00 00 00.0000000",
            "epo_first_name": "2019 05 14 00 00 00.0000000",
            "interval": "1.000",
            "md5": "325bd5f1cbfae170bd4dd49d8a2f8cb4",
            "name": "SEPT00BEL_R_20191340000_01D_01S_MO.rnx",
            "pgm": "sbf2rin-13.4.5",
            "pgm_date": "20210302 130957 UTC",
            "pgm_runby": "",
            "satsys": "EG",
            "site": "SEPT00BEL",
            "source": "R",
            "sysfrq": {
                "E": [
                    "1",
                    "5"
                ],
                "G": [
                    "1",
                    "2",
                    "5"
                ]
            },
            "sysobs": {
                "E": [
                    "C1C",
                    "C5Q",
                    "D1C",
                    "D5Q",
                    "L1C",
                    "L5Q",
                    "S1C",
                    "S5Q"
                ],
                "G": [
                    "C1C",
                    "C1W",
                    "C2L",
                    "C2W",
                    "C5Q",
                    "D1C",
                    "D2L",
                    "D2W",
                    "D5Q",
                    "L1C",
                    "L2L",
                    "L2W",
                    "L5Q",
                    "S1C",
                    "S1W",
                    "S2L",
                    "S2W",
                    "S5Q"
                ]
            },
            "system": "M",
            "systyp": {
                "E": [
                    "C",
                    "D",
                    "L",
                    "S"
                ],
                "G": [
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
        "path": "/home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134/ltx",
        "script": "/home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134/ltx/01_script_info"
    },
    "obstab": {
        "G": {
            "obs_G_tabf": "SEPT00BEL_R_20191340000_01D_01S_MO_G.obstab",
            "obs_G_statf": "SEPT00BEL_R_20191340000_01D_01S_MO_G.obsstat"
        },
        "E": {
            "obs_E_tabf": "SEPT00BEL_R_20191340000_01D_01S_MO_E.obstab",
            "obs_E_statf": "SEPT00BEL_R_20191340000_01D_01S_MO_E.obsstat"
        }
    }
}
dObstabs = {'G': {'obs_G_tabf': 'SEPT00BEL_R_20191340000_01D_01S_MO_G.obstab', \
                  'obs_G_statf': 'SEPT00BEL_R_20191340000_01D_01S_MO_G.obsstat'}, \
            'E': {'obs_E_tabf': 'SEPT00BEL_R_20191340000_01D_01S_MO_E.obstab', \
                  'obs_E_statf': 'SEPT00BEL_R_20191340000_01D_01S_MO_E.obsstat'}}
```
    
\normalsize

#### Resulting directory structure

\scriptsize
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ ll -R
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

./ltx:
total 4
-rw-rw-r-- 1 amuls amuls 1464 Mar  2 14:41 01_script_info.tex
```
    
\normalsize

The `*.obstab` and `*.obsstat` files are Comma Separated Values (CVS) files.

#### Latex section created `01_script_info.tex`
 
\scriptsize

```
\subsection{Script details}%
\label{subsec:Scriptdetails}%
\subsubsection{Program information}%
\label{ssubsec:Programinformation}%
\setlength{\tabcolsep}{2pt}%
\begin{longtabu}[l]{rcl}%
Script&:&rnxobs\_tabular.py\\%
Run at&:&02/03/2021 14:41\\%
Run by&:&A. Muls\\%
&&Royal Military Academy\\%
\end{longtabu}

%
\subsubsection{Parameters}%
\label{ssubsec:Parameters}%
\setlength{\tabcolsep}{2pt}%
\begin{longtabu}[l]{rcl}%
RINEX root directory&:&/home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134\\%
RINEX observation file&:&SEPT00BEL\_R\_20191340000\_01D\_01S\_MO.rnx\\%
RINEX version&:&3.04\\%
Marker&:&SEPT00BEL\\%
Year/day{-}of{-}year&:&2019/134\\%
&&\\%
\end{longtabu}

%
\subsubsection{Observation header information}%
\label{ssubsec:Observationheaderinformation}%
\setlength{\tabcolsep}{2pt}%
\begin{longtabu}[l]{rcl}%
First epoch&:&2019/05/14 00:00:00\\%
Last epoch&:&2019/05/14 23:59:59\\%
Interval&:&1.0\\%
&&\\%
GNSS&:&G (GPS NavSTAR) \\%
&:&E (Galileo) \\%
Frequencies E&:&1, 5\\%
Frequencies G&:&1, 2, 5\\%
&&\\%
Observable types&:&C (Pseudorange) \\%
&:&S (SNR) \\%
&:&D (Doppler) \\%
&:&L (Carrier) \\%
&&\\%
\end{longtabu}

%
\subsubsection{Logged observables}%
\label{ssubsec:Loggedobservables}%
\setlength{\tabcolsep}{2pt}%
\begin{longtabu}[l]{rcl}%
Observable types E&:&C1C, C5Q, D1C, D5Q, L1C, L5Q, S1C, S5Q\\%
Observable types G&:&C1C, C1W, C2L, C2W, C5Q, D1C, D2L, D2W, D5Q, L1C\\%
&&L2L, L2W, L5Q, S1C, S1W, S2L, S2W, S5Q\\%
&&\\%
\end{longtabu}
```

\normalsize
