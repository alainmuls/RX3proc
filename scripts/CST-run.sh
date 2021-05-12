#!/bin/bash

# example run for the CST processing

# 1. convert to RINEX v3.x files for all receivers used

sbf_rinex.py --sbffile /home/amuls/RxTURP/RFI-20349/TURP/BEGP3490.20_ --startepoch 14:00:00 --endepoch 14:30:00 --rnxdir ~/RxTURP/RFI-20349/CST/rnx/20349/

sbf_rinex.py --sbffile /home/amuls/RxTURP/RFI-20349/ASTXSB/H50_14DEC14AsTRX_SB.sbf --startepoch 14:00:00 --endepoch 14:30:00 --rnxdir ~/RxTURP/RFI-20349/CST/rnx/20349/

rnx15_combine.py --from_dir ~/RxTURP/RFI-20349/P3RS2/ --marker P3RS --year 2020 --doy 349 --startepoch 14:00:00 --endepoch 14:30:00 --rnx_dir ~/RxTURP/RFI-20349/CST/rnx/


# 2. create the observation statistics (*.obsstat) and tabular (*.obstab) files
rnxobs_tabular.py --obsfile ~/RxTURP/RFI-20349/CST/rnx/20349/TURX00BEL_R_20203491400_30M_01S_MO.rnx --gnsss E

rnxobs_tabular.py --obsfile ~/RxTURP/RFI-20349/CST/rnx/20349/SEPT00BEL_R_20203491400_30M_01S_MO.rnx --gnsss E G

rnxobs_tabular.py --obsfile ~/RxTURP/RFI-20349/CST/rnx/20349/P3RS04BEL_R_20203490000_01D_00U_MO.rnx --gnsss E G

# 3. Analyses of OBSSTAT files
obsstat_analyse.py --obsstat ~/RxTURP/RFI-20349/CST/rnx/20349/TURX00BEL_R_20203491400_30M_01S_MO_E.obsstat --freqs 1 6  --dbcvs ~/RxTURP/RFI-20349/CST/rnx/CST-db.cvs --plot

obsstat_analyse.py --obsstat ~/RxTURP/RFI-20349/CST/rnx/20349/P3RS04BEL_R_20203490000_01D_00U_MO_E.obsstat --freqs 1 6  --dbcvs ~/RxTURP/RFI-20349/CST/rnx/CST-db.cvs --plot
obsstat_analyse.py --obsstat ~/RxTURP/RFI-20349/CST/rnx/20349/P3RS04BEL_R_20203490000_01D_00U_MO_G.obsstat --freqs 1   --dbcvs ~/RxTURP/RFI-20349/CST/rnx/CST-db.cvs --plot

obsstat_analyse.py --obsstat ~/RxTURP/RFI-20349/CST/rnx/20349/SEPT00BEL_R_20203491400_30M_01S_MO_E.obsstat --freqs 1  --dbcvs ~/RxTURP/RFI-20349/CST/CST-db.cvs --plot
obsstat_analyse.py --obsstat ~/RxTURP/RFI-20349/CST/rnx/20349/SEPT00BEL_R_20203491400_30M_01S_MO_G.obsstat --freqs 1  --dbcvs ~/RxTURP/RFI-20349/CST/CST-db.cvs --plot

# 4. Analyses of OBSTAB files
obstab_analyse.py  --freqs 1 --cutoff 0 --snr_th 2.5 --obstypes S  --jamsc ~/RxTURP/RFI-20349/CST/CST-jamming.csv --obstab ~/RxTURP/RFI-20349/CST/rnx/20349/SEPT00BEL_R_20203491400_30M_01S_MO_E.obstab --prns E00 --plot --elev_step 1
obstab_analyse.py  --freqs 1 --cutoff 0 --snr_th 2.5 --obstypes S  --jamsc ~/RxTURP/RFI-20349/CST/CST-jamming.csv --obstab ~/RxTURP/RFI-20349/CST/rnx/20349/SEPT00BEL_R_20203491400_30M_01S_MO_G.obstab --prns G00 --plot --elev_step 1

