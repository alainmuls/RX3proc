
# Overview of `rnxproc`

## General directory structure for (semi-)permanent monitoring

The repository is based on the following directory structure[^1] for the binary receiver data:

\scriptsize 

```bash
${HOME}/RxTURP
    BEGPIOS
        ASTX
            ...
            19133
            19134
            19135
            ...
        BEGP
            ...
            19133
            19134
            19135
            ...
        P3RS2
            LOG
                pvt_ls
```

\normalsize

where `YYDDD` represents 2 digits for the year and 3 digits for the day of year.

During processing, in each receiver type directory (`ASTX`, `BEGP`, ...) a `rinex` sub-directory is created with sub-directories with the same `YYDDD` as the original raw binary data sub-directories.

[^1]: I never tested this repository using another directory structure.

The P3RS2 outputs RINEX observation and navigation files each 15 minutes into a single directory `LOG/pvt_ls` and need to be treated differently. These files uses the following naming convention, loosely based on the official RINEX v3 naming convention:

+ __P3RS-2_RX_R_YYYYDOYHHMM_15M_MN.rnx__ for the RINEX navigation files,
+ __P3RS-2_RX_R_YYYYDOYHHMM_15M_00U_MO.rnx__ for the RINEX observation file

where:

+ __YYYY__ ... 4 digit year number
+ __DOY__ ... 3 digit day of year number
+ __HHMM__ ... hour and minutes of file creation

The resulting ::RX3:: formatted daily files are stored under directory `/home/amuls/RxTURP/BEGPIOS/P3RS2/rinex`. In this directory the daily created files are organised in sub-directories __YYDOY__ similar to the structure followed for the other receivers. The ::RX3:: files are stored in Hatanaka compressed form for observation files, while __gzip__ compresses the navigation files. As example:

\scriptsize

```bash
[amuls:~/RxTURP/BEGPIOS/P3RS2/rinex/20311] $ ls -l
total 1740
-rw-rw-r-- 1 amuls amuls  12534623 Jan 13 16:43 P3RS00BEL_R_20203300008_01D_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls    165168 Jan 13 16:41 P3RS00BEL_R_20203300000_01D_MN.rnx.gz
```

\normalsize

## Purpose

`rnxproc` provides several python scripts which can be run in stand alone mode or be called from other python scripts. The purpose is to create  scripts performing a specific task. Some tasks will be grouped in a more general (super-)script to perform several elementary steps in a row.

### Converting (six-)hourly SBF files to (compressed) RINEX v3.x files

| __Script__             | __Task__                                                             |
| :----------------:     | :-----------------------------------------------                     |
| __sbf_daily.py__       | Combine (six-)hourly SBF files to daily files                        |
| __sbf_rinex.py__       | Convert SBF daily file to RINEX v3.X observation & navigation file   |
| \color{blue}{prepare\_sbf2rnx.py} | \color{blue}{Combines above scripts and offers to get compressed RINEX v3.x files} |

### Combining (15 minutes) P3RS2 RINEX files into daily RINEX v3.x files

| __Script__           | __Task__                                                               |
| :----------------:   | :-----------------------------------------------                       |
| __rnx15_combine.py__ | Combines 15 minutes RINEX files frim P3RS2                             |
| \color{blue}{prepare\_rnx15.py} | \color{blue}{Uses above script and add possibility for compressed RINEX v3.x files} |

### Converting and analysing RINEX files to observation tabular and statistics files

| __Script__             | __Task__                                                       |
| :----------------:     | :-----------------------------------------------               |
| __rnxobs_tabular.py__  | creates observation tabular/statistics file for selected GNSSs |
| __obsstat_analyse.py__ | analyses observation statistics file for selected GNSSs        |
