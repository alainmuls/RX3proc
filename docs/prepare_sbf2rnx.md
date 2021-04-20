
## Converting (six-)hourly SBF files to (compressed) RINEX v3.x files

### __sbf_daily.py__

`sbf_daily.py` creates a (daily) SBF file based on ((six) hourly) SBF files found in given directory. This script is oriented towards the continuous logging 

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ sbf_daily.py --help
usage: sbf_daily.py [-h] [--dir DIR] [--overwrite] [--logging LOGGING LOGGING]

sbf_daily.py creates a daily SBF file based on (six) hourly SBF files found in given directory

optional arguments:
  -h, --help            show this help message and exit
  --dir DIR             Directory of SBF file (defaults to .)
  --overwrite           overwrite daily SBF file (default False)
  --logging LOGGING LOGGING
                        specify logging level console/file (default INFO DEBUG)
```
    
\normalsize

#### Example run

\scriptsize
    
```bash                        
[amuls:~/amPython/RX3proc] [RX3proc]$ sbf_daily.py --dir ~/RxTURP/BEGPIOS/ASTX/19134/
INFO: sbf_daily.py - main_combine_sbf: working directory is /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main_combine_sbf: changed to directory /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main_combine_sbf: combine SBF (six-)hourly files to daily SBF file
INFO: sbf_daily.py - main_combine_sbf: reusing daily SBF file SEPT1340.19_

[amuls:~/amPython/RX3proc] [RX3proc]$ sbf_daily.py --dir ~/RxTURP/BEGPIOS/ASTX/19134/ --overwrite
INFO: sbf_daily.py - main_combine_sbf: working directory is /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main_combine_sbf: changed to directory /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main_combine_sbf: combine SBF (six-)hourly files to daily SBF file
INFO: sbf_daily.py - main_combine_sbf: creating daily SBF file SEPT1340.19_
```
    
\normalsize

### __sbf_rinex.py__

`sbf_rinex.py` converts a SBF file into RINEX v3.x observation and navigation files.  A time span can be specified.

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ sbf_rinex.py --help
usage: sbf_rinex.py [-h] --sbffile SBFFILE [--rnxdir RNXDIR] [--startepoch STARTEPOCH] \
          [--endepoch ENDEPOCH] [--logging LOGGING LOGGING]

sbf_rinex.py convert binary raw data from SBF to RINEX Obs & Nav files

optional arguments:
  -h, --help            show this help message and exit
  --sbffile SBFFILE     Binary SBF file
  --rnxdir RNXDIR       Directory for RINEX output (default .)
  --startepoch STARTEPOCH
                        specify start epoch hh:mm:ss (default 00:00:00)
  --endepoch ENDEPOCH   specify end epoch hh:mm:ss (default 23:59:59)
  --logging LOGGING LOGGING
                        specify logging level console/file (two of CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET, default INFO DEBUG)

```
    
\normalsize

#### Example run using all data in the SBF file 


\tiny
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ sbf_rinex.py --sbff /home/amuls/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_\
         --rnxdir /home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134
INFO: sbf_rinex.py - sbf2rnx3: arguments processed: dRnx = {'dirs': {'sbf': '/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134', 'rnx': PosixPath('/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134')}, 'sbff': 'SEPT1340.19_'}
INFO: sbf_rinex.py - checkValidityArgs: check existence of sbfDir /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_rinex.py - checkValidityArgs: check existence of binary file /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ to convert
INFO: sbf_rinex.py - checkValidityArgs: check existence of rnxdir /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134 and create if needed
INFO: location.py - locateProg: sbf2rin is /opt/Septentrio/RxTools/bin/sbf2rin
INFO: sbf_rinex.py - sbf2rnx3: convert binary file to rinex
INFO: sbf_rinex.py - sbf2rinex: RINEX conversion from SBF binary
INFO: sbf_rinex.py - sbf2rinex: creating RINEX observation file
INFO: amutils.py - run_subprocess_output: running
/opt/Septentrio/RxTools/bin/sbf2rin -f /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ -x RSCJI -s -D -v -R3 -l -O BEL
Creating RINEX file: done                                                                      |  0%
INFO: sbf_rinex.py - sbf2rinex: creating RINEX navigation file
INFO: amutils.py - run_subprocess_output: running
/opt/Septentrio/RxTools/bin/sbf2rin -f /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ -x RSCJI -s -D -v -n P -R3 -l -O BEL
Creating RINEX file: done                                                                      |  0%
INFO: sbf_rinex.py - sbf2rnx3: dRnx =
{
    "dirs": {
        "sbf": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134",
        "rnx": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134"
    },
    "sbff": "SEPT1340.19_",
    "bin": {
        "SBF2RIN": "/opt/Septentrio/RxTools/bin/sbf2rin"
    },
    "obs3f": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.rnx",
    "nav3f": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx"
}
```
    
\normalsize

#### Example run using selected data in the SBF file 

\tiny
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ sbf_rinex.py --sbff /home/amuls/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ \
        --rnxdir /home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134 --startepoc="07:15:45" --endepoc='10:05:30'
INFO: sbf_rinex.py - main_sbf2rnx3: arguments processed: dRnx = {'dirs': {'sbf': '/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134', 'rnx': PosixPath('/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134')}, 'sbff': 'SEPT1340.19_', 'time': {'startepoch': '07:15:45', 'endepoch': '10:05:30'}}
INFO: sbf_rinex.py - checkValidityArgs: check existence of sbfDir /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_rinex.py - checkValidityArgs: check existence of binary file /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ to convert
INFO: sbf_rinex.py - checkValidityArgs: check existence of rnxdir /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134 and create if needed
INFO: location.py - locateProg: sbf2rin is /opt/Septentrio/RxTools/bin/sbf2rin
INFO: sbf_rinex.py - main_sbf2rnx3: convert binary file to rinex
INFO: sbf_rinex.py - sbf2rinex: RINEX conversion from SBF binary
INFO: sbf_rinex.py - sbf2rinex: creating RINEX observation file
INFO: amutils.py - run_subprocess_output: running
/opt/Septentrio/RxTools/bin/sbf2rin -f /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ -x RSCJI -s -D -v -R3 -l -O BEL -b 07:15:45 -e 10:05:30
Creating RINEX file: done                                                                      |  0%
INFO: sbf_rinex.py - sbf2rinex: creating RINEX navigation file
INFO: amutils.py - run_subprocess_output: running
/opt/Septentrio/RxTools/bin/sbf2rin -f /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ -x RSCJI -s -D -v -n P -R3 -l -O BEL
Creating RINEX file: done                                                                      |  0%
INFO: sbf_rinex.py - sbf2rinex: sorted list (by modification time) of rnx files:
/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.rnx
/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340715_02H_01S_MO.rnx
/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx
INFO: sbf_rinex.py - main_sbf2rnx3: dRnx =
{
    "dirs": {
        "sbf": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/19134",
        "rnx": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134"
    },
    "sbff": "SEPT1340.19_",
    "time": {
        "startepoch": "07:15:45",
        "endepoch": "10:05:30"
    },
    "bin": {
        "SBF2RIN": "/opt/Septentrio/RxTools/bin/sbf2rin"
    },
    "obs3f": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340715_02H_01S_MO.rnx",
    "nav3f": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx"
}
```

\normalsize

### __prepare_sbf2rnx.py__

This script combines the scripts `sbf_daily.py` and `sbf_rinex.py` and offers the possibility to perform compression of these files:

- RINEX observation file undergoes a Hatanaka compression using the program `rnx2crz`,
- RINEX navigation file is `gzip` compressed.

#### Usage


\scriptsize
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ prepare_sbf2rnx.py --help
usage: prepare_sbf2rnx.py [-h] [--root_dir ROOT_DIR] --marker MARKER --year YEAR --doy DOY \
         [--startepoch STARTEPOCH] [--endepoch ENDEPOCH] [--rnxdir RNXDIR] [--compress] [--overwrite] \
         [--logging LOGGING LOGGING]

prepare_sbf2rnx.py Combining and conversion of SBF files to RINEX v3.x Obs/Nav files

optional arguments:
  -h, --help            show this help message and exit
  --root_dir ROOT_DIR   Root directory of SBF data collection (default /home/amuls/RxTURP/BEGPIOS/)
  --marker MARKER       marker name (4 chars)
  --year YEAR           Year (4 digits)
  --doy DOY             day-of-year [1..366]
  --startepoch STARTEPOCH
                        specify start epoch hh:mm:ss (default 00:00:00)
  --endepoch ENDEPOCH   specify end epoch hh:mm:ss (default 23:59:59)
  --rnxdir RNXDIR       Directory for RINEX output (default YYDOY subdir)
  --compress            compress obtained RINEX files
  --overwrite           overwrite daily SBF file (default False)
  --logging LOGGING LOGGING
                        specify logging level console/file (default INFO DEBUG)
```
    
\normalsize


#### Example run


\tiny
    
```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ prepare_sbf2rnx.py --root_dir /media/amuls/porsche/RxTURP/CMT/ \
          --marker TURP --year 2021 --doy 89 --compress --rnxdir /media/amuls/porsche/RxTURP/CMT/rnx/
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


\scriptsize
    

```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ ls -lht ~/RxTURP/BEGPIOS/ASTX/rinex/19134
total 29M
-rw-rw-r-- 1 amuls amuls 3.1K Feb  4 15:16 prepare_sbf2rnx.log
-rw-rw-r-- 1 amuls amuls  28M Feb  4 15:16 SEPT00BEL_R_20191340000_01D_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls  439 Feb  4 15:16 sbf_rinex.json
-rw-rw-r-- 1 amuls amuls 117K Feb  4 15:16 SEPT00BEL_R_20191340000_01D_MN.rnx.gz
```

```bash
[amuls:~/amPython/RX3proc] [RX3proc]$ ls -lht /media/amuls/porsche/RxTURP/CMT/rnx/
total 111M
-rw-rw-r-- 1 amuls amuls 3.2K Apr  2 16:11 prepare_sbf2rnx.log
-rw-rw-r-- 1 amuls amuls 4.1M Apr  2 16:11 TURX00BEL_R_20210890000_13H_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls  506 Apr  2 16:11 sbf_rinex.json
-rw-rw-r-- 1 amuls amuls 2.5K Apr  2 16:11 sbf_rinex_py.log
-rw-rw-r-- 1 amuls amuls  79K Apr  2 16:11 TURX00BEL_R_20210890000_13H_MN.rnx.gz
-rw-rw-r-- 1 amuls amuls 355K Apr  2 11:46 TURX00BEL_R_20210881014_13H_MN.rnx
-rw-rw-r-- 1 amuls amuls  53M Apr  2 11:46 TURX00BEL_R_20210881014_13H_01S_MO.rnx
-rw-rw-r-- 1 amuls amuls 4.2M Mar 31 17:04 TURX00BEL_R_20210881014_13H_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls  79K Mar 31 17:04 TURX00BEL_R_20210881014_13H_MN.rnx.gz
-rw-rw-r-- 1 amuls amuls  12M Mar 31 16:36 ASTX02BEL_R_20210890600_09H_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls  21M Mar 31 16:36 ASTX02BEL_R_20210890000_14H_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls  17M Mar 31 16:35 ASTX02BEL_R_20210881200_12H_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls 103K Mar 31 16:33 ASTX02BEL_R_20210890000_15H_MP.rnx.gz
-rw-rw-r-- 1 amuls amuls  87K Mar 31 16:33 ASTX02BEL_R_20210881200_12H_MP.rnx.gz

```
    
\normalsize


\newpage
