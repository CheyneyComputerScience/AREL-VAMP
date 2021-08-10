#!/usr/bin/bash


# put this in crontab:
# https://help.ubuntu.com/community/CronHowto

# 30 * * * * /CARE-U/AREL-record.sh


# this script is to do one iteration of recording each tank
# it will also take a trip back

DEVICE_8F=D6:4A:69:3E:1D:8F # ARELOAKD
DEVICE_48=F1:74:F9:F8:A9:48 # AREL-BOT2


DEVICE=$DEVICE_48


# goto to closed state (bot 1)
#python3 /CARE-U/python-host/switchbot_py3_AREL.py -d $DEVICE -c close

# goto to open state (bot 2)
python3 /CARE-U/python-host/switchbot_py3_AREL.py -d $DEVICE -c open


#wait 90 seconds
sleep 90

# turn on usb port
# ubuntu 20.10
uhubctl -n 2109 -a 1
# ubuntu 20.04
#uhubctl -n 1d6b -a 1 # https://github.com/mvp/uhubctl

# setup python environment
source /CARE-U/myvenv/bin/activate



# get time
START=$(date +'%Y-%m-%d-%H%M%S')
# make directory for time
mkdir /CARE-U/recordings/$START

DIR=/CARE-U/recordings/$START

python3 /CARE-U/depthai-python/examples/calibration_backup-AREL.py $DIR >> ${DIR}/errors.log 2>&1

LOG=$DIR/recording.log
echo START - $START >> $LOG

# locations of tanks
tanks1=(tank1 tank2 tank3 tank4 tank5 tank6 tank7 tank8 tank9)
tanks2=(tank10 tank11 tank12 tank13 tank14 tank15 tank16 tank17 tank18)
loc=("${tanks2[@]}")  # use tanks2

# record for 5 seconds each
REC_TIME=5

# for each tank 1 to 9 or 10 to 18
for i in ${!loc[@]}; do
    # goto tank n
    python3 /CARE-U/python-host/switchbot_py3_AREL.py -d $DEVICE -c ${loc[$i]} >> ${DIR}/errors.log 2>&1
    # wait ten seconds
    sleep 10
    echo ${loc[$i]} - $(date +'%Y-%m-%d-%H%M%S') >> $LOG

    # record for 5 seconds
    python3 /CARE-U/depthai-python/examples/encoding_max_limit-AREL.py $DIR ${loc[$i]} $REC_TIME >> ${DIR}/errors.log 2>&1

done

# turn of usb port
# ubuntu 20.10
uhubctl -n 2109 -a 0
# ubuntu 20.04
#uhubctl -n 1d6b -a 0 # https://github.com/mvp/uhubctl


# goto to closed state (bot 1)
#python3 /CARE-U/python-host/switchbot_py3_AREL.py -d $DEVICE -c close

# goto to open state (bot 2)
python3 /CARE-U/python-host/switchbot_py3_AREL.py -d $DEVICE -c open >> ${DIR}/errors.log 2>&1


echo END - $(date +'%Y-%m-%d-%H%M%S') >> $LOG
