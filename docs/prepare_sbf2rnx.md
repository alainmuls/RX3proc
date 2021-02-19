### Converting (six-)hourly SBF files to (compressed) RINEX v3.x files

| __Script__             | __Task__                                                             |
| :----------------:     | :-----------------------------------------------                     |
| __sbf_daily.py__       | Combine (six-)hourly SBF files to daily files                        |
| __sbf_rinex.py__       | Convert SBF daily file to RINEX v3.X observation & navigation file   |
| __prepare_sbf2rnx.py__ | Combines above scripts and offers to get compressed RINEX v3.x files |

### Combining (15 minutes) P3RS2 RINEX files into daily RINEX v3.x files

| __Script__           | __Task__                                                               |
| :----------------:   | :-----------------------------------------------                       |
| __rnx15_combine.py__ | Combines 15 minutes RINEX files frim P3RS2                             |
| __prepare_rnx15.py__ | Usage above script and add possibility for compressed RINEX v3.x files |


\newpage

# Python scripts

## Converting (six-)hourly SBF files to (compressed) RINEX v3.x files

### __sbf_daily.py__

`sbf_daily.py` creates a daily SBF file based on (six) hourly SBF files found in given directory

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ sbf_daily.py -h
usage: sbf_daily.py [-h] [-d DIR] [-o] [-l LOGGING LOGGING]

sbf_daily.py creates a daily SBF file based on (six) hourly SBF files found in given directory

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     Directory of SBF file (defaults to .)
  -o, --overwrite       overwrite daily SBF file (default False)
  -l LOGGING LOGGING, --logging LOGGING LOGGING
                        specify logging level console/file (default INFO DEBUG)
```
    
\normalsize

#### Example run

\scriptsize
    
```bash                        
[amuls:~/amPython/rnxproc] [rnxproc]$ sbf_daily.py -d ~/RxTURP/BEGPIOS/ASTX/19134/
INFO: sbf_daily.py - main: working directory is /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main: changed to directory /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main: combine SBF (six-)hourly files to daily SBF file
INFO: sbf_daily.py - main: creating daily SBF file SEPT1340.19_

[amuls:~/amPython/rnxproc] [rnxproc]$ sbf_daily.py -d ~/RxTURP/BEGPIOS/ASTX/19134/
INFO: sbf_daily.py - main: working directory is /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main: changed to directory /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - main: combine SBF (six-)hourly files to daily SBF file
INFO: sbf_daily.py - main: reusing daily SBF file SEPT1340.19_
```
    
\normalsize

### __sbf_rinex.py__

`sbf_rinex.py` converts a SBF file into RINEX v3.x observation and navigation files.

#### Usage

\scriptsize
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ rinex.py --help
usage: sbf_rinex.py [-h] -f SBFF [-r RNXDIR] [-l LOGGING LOGGING]

sbf_rinex.py convert binary raw data from SBF to RINEX Obs & Nav files

optional arguments:
  -h, --help            show this help message and exit
  -f SBFF, --sbff SBFF  Binary SBF file
  -r RNXDIR, --rnxdir RNXDIR
                        Directory for RINEX output (default .)
  -l LOGGING LOGGING, --logging LOGGING LOGGING
                        specify logging level console/file (default INFO DEBUG)
```
    
\normalsize

#### Example run


\tiny
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ sbf_rinex.py --sbff /home/amuls/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ --rnxdir /home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134
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

### __prepare_sbf2rnx.py__

This script combines the scripts `sbf_daily.py` and `sbf-rinex.py` and offers the possibility to perform compression of these files:

- RINEX observation file undergoes a Hatanaka compression using the program `rnx2crz`,
- RINEX navigation file is `gzip` compressed.

#### Usage


\scriptsize
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ prepare_sbf2rnx.py -h
usage: prepare_sbf2rnx.py [-h] [-r ROOT_DIR] -m MARKER -y YEAR -d DOY [-c] [-o] [-l LOGGING LOGGING]

prepare_sbf2rnx.py Combining and conversion of SBF files to RINEX v3.x Obs/Nav files

optional arguments:
  -h, --help            show this help message and exit
  -r ROOT_DIR, --root_dir ROOT_DIR
                        Root directory of SBF data collection (default /home/amuls/RxTURP/BEGPIOS/)
  -m MARKER, --marker MARKER
                        marker name (4 chars)
  -y YEAR, --year YEAR  Year (4 digits)
  -d DOY, --doy DOY     day-of-year [1..366]
  -c, --compress        compress obtained RINEX files
  -o, --overwrite       overwrite daily SBF file (default False)
  -l LOGGING LOGGING, --logging LOGGING LOGGING
                        specify logging level console/file (default INFO DEBUG)

```
    
\normalsize


#### Example run


\tiny
    
```bash
[amuls:~/amPython/rnxproc] [rnxproc]$ prepare_sbf2rnx.py  -m ASTX -y 2019 -d 134  -c
INFO: === prepare_sbf2rnx.py - combine_sbffiles: passing control to sbf_daily.py (options: --dir /home/amuls/RxTURP/BEGPIOS/ASTX/19134) ===
INFO: sbf_daily.py - combine_sbf: working directory is /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - combine_sbf: changed to directory /home/amuls/RxTURP/BEGPIOS/ASTX/19134
INFO: sbf_daily.py - combine_sbf: combine SBF (six-)hourly files to daily SBF file
INFO: sbf_daily.py - combine_sbf: reusing daily SBF file SEPT1340.19_
INFO: >>>>>> prepare_sbf2rnx.py - prepare_rnx_data: obtained daily SBF file = SEPT1340.19_
INFO: === prepare_sbf2rnx.py - sbf_rnx3: passing control to sbf_rinex.py  (options: --sbff /home/amuls/RxTURP/BEGPIOS/ASTX/19134/SEPT1340.19_ --rnxdir /home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134) ===
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
INFO: >>>>>> prepare_sbf2rnx.py - prepare_rnx_data: obtained RINEX observation file = /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.rnx
INFO: >>>>>> prepare_sbf2rnx.py - prepare_rnx_data: obtained RINEX navigation files = /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx
INFO: location.py - locateProg: rnx2crz is /home/amuls/bin/rnx2crz
INFO: location.py - locateProg: gzip is /usr/bin/gzip
INFO: compress_utils.py - compress_rnx_obs: Compressing RINEX observation /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.rnx
INFO: amutils.py - run_subprocess: running
/home/amuls/bin/rnx2crz -f -d /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.rnx
INFO: >>>>>> prepare_sbf2rnx.py - prepare_rnx_data: compressed RINEX observation file = /home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.crx.Z
INFO: compress_utils.py - gzip_compress: Compressing RINEX navigation /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx
INFO: amutils.py - run_subprocess: running
/usr/bin/gzip -f /media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx
INFO: >>>>>> prepare_sbf2rnx.py - prepare_rnx_data: compressed RINEX navigation file = /home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx.gz
INFO: prepare_sbf2rnx.py - prepare_rnx_data: SBF preparation information =
{
    "dirs": {
        "root": "/home/amuls/RxTURP/BEGPIOS/",
        "sbf": "/home/amuls/RxTURP/BEGPIOS/ASTX/19134",
        "yydoy": "/home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134"
    },
    "cli": {
        "marker": "ASTX",
        "yyyy": 2019,
        "doy": 134,
        "compress": true,
        "overwrite": false
    },
    "rnx": {
        "obs3f": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.rnx",
        "nav3f": "/media/amuls/porsche/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx",
        "obs3fc": "/home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_01S_MO.crx.Z",
        "nav3fc": "/home/amuls/RxTURP/BEGPIOS/ASTX/rinex/19134/SEPT00BEL_R_20191340000_01D_MN.rnx.gz"
    },
    "sbffile": "SEPT1340.19_",
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
[amuls:~/amPython/rnxproc] [rnxproc]$ ls -lht ~/RxTURP/BEGPIOS/ASTX/rinex/19134
total 29M
-rw-rw-r-- 1 amuls amuls 3.1K Feb  4 15:16 prepare_sbf2rnx.log
-rw-rw-r-- 1 amuls amuls  28M Feb  4 15:16 SEPT00BEL_R_20191340000_01D_01S_MO.crx.Z
-rw-rw-r-- 1 amuls amuls  439 Feb  4 15:16 sbf_rinex.json
-rw-rw-r-- 1 amuls amuls 117K Feb  4 15:16 SEPT00BEL_R_20191340000_01D_MN.rnx.gz
```
    
\normalsize


\newpage
