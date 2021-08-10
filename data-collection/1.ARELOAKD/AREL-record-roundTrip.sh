#!/usr/bin/bash


# put this in crontab:
# https://help.ubuntu.com/community/CronHowto

# * 12 * * * /CARE-U/AREL-record-roundTrip.sh


# this script is to do one round trip recording


# turn on usb port
# ubuntu 20.10
uhubctl -n 2109 -a 1
# ubuntu 20.04
#uhubctl -n 1d6b -a 1 # https://github.com/mvp/uhubctl

# setup python environment
source /CARE-U/myvenv/bin/activate


DEVICE_8F=D6:4A:69:3E:1D:8F # ARELOAKD
DEVICE_48=F1:74:F9:F8:A9:48 # AREL-BOT2


DEVICE=$DEVICE_8F

# wait 5 seconds
sleep 5

# record for 60 seconds each
REC_TIME=70


# get time
START=$(date +'%Y-%m-%d-%H%M%S')
# make directory for time
mkdir /CARE-U/recordings/$START

DIR=/CARE-U/recordings/$START

python3 /CARE-U/depthai-python/examples/calibration_backup-AREL.py $DIR >> ${DIR}/errors.log 2>&1

LOG=$DIR/recording.log
echo START - $START >> $LOG

# go to open position
python3 /CARE-U/python-host/switchbot_py3_AREL.py -d $DEVICE -c open >> ${DIR}/errors.log 2>&1
echo opening - $(date +'%Y-%m-%d-%H%M%S') >> $LOG

# record for 60 seconds
python3 /CARE-U/depthai-python/examples/encoding_max_limit-AREL.py $DIR opening $REC_TIME >> ${DIR}/errors.log 2>&1

# go to closing position
python3 /CARE-U/python-host/switchbot_py3_AREL.py -d $DEVICE -c close 
echo closing - $(date +'%Y-%m-%d-%H%M%S') >> $LOG

# record for 60 seconds
python3 /CARE-U/depthai-python/examples/encoding_max_limit-AREL.py $DIR closing $REC_TIME >> ${DIR}/errors.log 2>&1




# turn of usb port
# ubuntu 20.10
uhubctl -n 2109 -a 0 >> ${DIR}/errors.log 2>&1
# ubuntu 20.04
#uhubctl -n 1d6b -a 0 # https://github.com/mvp/uhubctl



echo END - $(date +'%Y-%m-%d-%H%M%S') >> $LOG
