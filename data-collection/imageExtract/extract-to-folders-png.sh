#!/usr/local/bin/bash

#X=BOT1
#Y=2021-07-04-103132
for X in */ ; do
    subdircount=$(find ${X} -maxdepth 1 -type d | wc -l)

    if [[ "$subdircount" -eq 1 ]]
    then
        echo "no subdirs"
    else
        
        for Y in ${X}*/ ; do
            #echo  ${Y}recording.log
            if [[ -f ${Y}recording.log ]] ; then
               while read -a row; do
                   c=0
                   for value in "${row[@]}"; do
                       declare -n column=column_$(( c++ ))
                       column+=( "$value" )
                   done
               done <${Y}recording.log
               last=$((${#column_0[@]} - 2))
               for ((i = 1 ; i <= ${last}; i++)); do
                   col1=${column_0[i]}
                   col3=${column_2[i]}
                   if [[ "$col1" != "START" && "$col1" != "END" ]] ; then
                       mkdir -p movies/${col1}
                       if [[ -f ${Y}${col1}-color.h265 && ! -f movies/${col1}/${col1}-${col3}-color.mp4 ]] ; then
                           ffmpeg -framerate 25 -i ${Y}${col1}-color.h265 -c copy movies/${col1}/${col1}-${col3}-color.mp4
                       fi
                       if [[ -f ${Y}${col1}-mono1.h264 && ! -f movies/${col1}/${col1}-${col3}-mono1.mp4 ]] ; then
                           ffmpeg -framerate 25 -i ${Y}${col1}-mono1.h264 -c copy movies/${col1}/${col1}-${col3}-mono1.mp4
                       fi
                       if [[ -f ${Y}${col1}-mono2.h264 && ! -f movies/${col1}/${col1}-${col3}-mono2.mp4 ]] ; then
                           ffmpeg -framerate 25 -i ${Y}${col1}-mono2.h264 -c copy movies/${col1}/${col1}-${col3}-mono2.mp4
                       fi
                       if [[ "$col1" != "opening" && "$col1" != "closing"  && "$col1" != "open" ]] ; then
                           mkdir -p largeStills/${col1}
                           if [[ -f movies/${col1}/${col1}-${col3}-color.mp4 && ! -f largeStills/${col1}/${col1}-${col3}-color.png ]] ; then
                               ffmpeg -ss 4.5 -i movies/${col1}/${col1}-${col3}-color.mp4 -r 1 -t 1 largeStills/${col1}/${col1}-${col3}-color.png
                           fi
                           if [[ -f movies/${col1}/${col1}-${col3}-mono1.mp4 && ! -f largeStills/${col1}/${col1}-${col3}-mono1.png ]] ; then
                               ffmpeg -ss 4.5 -i movies/${col1}/${col1}-${col3}-mono1.mp4 -r 1 -t 1 largeStills/${col1}/${col1}-${col3}-mono1.png
                           fi
                           if [[ -f movies/${col1}/${col1}-${col3}-mono2.mp4 && ! -f largeStills/${col1}/${col1}-${col3}-mono2.png ]] ; then
                               ffmpeg -ss 4.5 -i movies/${col1}/${col1}-${col3}-mono2.mp4 -r 1 -t 1 largeStills/${col1}/${col1}-${col3}-mono2.png
                           fi
                       fi
                   fi
               done
               column_0=()
               column_1=()
               column_2=()
            fi
        done
    fi
done


#for i in {1..9}; do
#  mytime=`echo "(${stime[$i]} + ${etime[$i]}) / 2.0" | bc -l`
  #echo $mytime
#  ffmpeg -framerate 25 -i tank${i}-color.h265 -c copy tank${i}-color.mp4
#  ffmpeg -ss 2.5 -i tank${i}-color.mp4 -r 1 -t 1 tank${i}-color.png
#done
