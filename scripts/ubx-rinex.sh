#! /bin/bash

ROOTDIR=/home/amuls/RxTURP/BEGPIOS/F9P/


ubx_rinex.py --ubxfile ${ROOTDIR}/F9PZeebrugge.ubx --rnxdir ${ROOTDIR}/rnx/ --marker F9P0 --year 2021 --doy 89 --observer amuls RMA-CISS --gnss E G --markerno=5 --markertype STATIC --receiver 5 F9PD 0.1 --antenna 5 uBLOX --startepoch 01:30:00 --endepoch 05:00:00 --year 2021 --doy 89
