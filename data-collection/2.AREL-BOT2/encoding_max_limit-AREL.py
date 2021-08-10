#!/usr/bin/env python3

import depthai as dai
import sys
import time


locName=""
saveDir=""
recTimeStr="5"

if len(sys.argv) > 1:
    saveDir = sys.argv[1]

if len(sys.argv) > 2:
    locName = sys.argv[2]

if len(sys.argv) > 3:
    recTimeStr = sys.argv[3]

recTime=int(recTimeStr)
# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.createColorCamera()
monoLeft = pipeline.createMonoCamera()
monoRight = pipeline.createMonoCamera()
ve1 = pipeline.createVideoEncoder()
ve2 = pipeline.createVideoEncoder()
ve3 = pipeline.createVideoEncoder()

ve1Out = pipeline.createXLinkOut()
ve2Out = pipeline.createXLinkOut()
ve3Out = pipeline.createXLinkOut()

ve1Out.setStreamName('ve1Out')
ve2Out.setStreamName('ve2Out')
ve3Out.setStreamName('ve3Out')

# Properties
camRgb.setBoardSocket(dai.CameraBoardSocket.RGB)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
# For now, RGB needs fixed focus to properly align with depth.
# This value was used during calibration
camRgb.initialControl.setManualFocus(130)
camRgb.setImageOrientation(dai.CameraImageOrientation.NORMAL)

monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# Setting to 26fps will trigger error
ve1.setDefaultProfilePreset(1280, 720, 15, dai.VideoEncoderProperties.Profile.H264_MAIN)
ve2.setDefaultProfilePreset(3840, 2160, 15, dai.VideoEncoderProperties.Profile.H265_MAIN)
ve3.setDefaultProfilePreset(1280, 720, 15, dai.VideoEncoderProperties.Profile.H264_MAIN)

# Linking
monoLeft.out.link(ve1.input)
camRgb.video.link(ve2.input)
monoRight.out.link(ve3.input)

ve1.bitstream.link(ve1Out.input)
ve2.bitstream.link(ve2Out.input)
ve3.bitstream.link(ve3Out.input)


# Connect to device and start pipeline
with dai.Device(pipeline) as dev:


    # Output queues will be used to get the encoded data from the output defined above
    outQ1 = dev.getOutputQueue('ve1Out', maxSize=30, blocking=True)
    outQ2 = dev.getOutputQueue('ve2Out', maxSize=30, blocking=True)
    outQ3 = dev.getOutputQueue('ve3Out', maxSize=30, blocking=True)

    # Processing loop
    with open(saveDir+'/'+locName+'-mono1.h264', 'wb') as fileMono1H264, open(saveDir+'/'+locName+'-color.h265', 'wb') as fileColorH265, open(saveDir+'/'+locName+'-mono2.h264', 'wb') as fileMono2H264:
        print("Will loop for " + recTimeStr + " seconds")
        t_end = time.time() + recTime
        while time.time() < t_end:
            try:
                # Empty each queue
                while outQ1.has():
                    outQ1.get().getData().tofile(fileMono1H264)

                while outQ2.has():
                    outQ2.get().getData().tofile(fileColorH265)

                while outQ3.has():
                    outQ3.get().getData().tofile(fileMono2H264)
            except KeyboardInterrupt:
                break

    print("To view the encoded data, convert the stream file (.h264/.h265) into a video file (.mp4), using commands below:")
    cmd = "ffmpeg -framerate 15 -i {} -c copy {}"
    print(cmd.format("mono1.h264", "mono1.mp4"))
    print(cmd.format("mono2.h264", "mono2.mp4"))
    print(cmd.format("color.h265", "color.mp4"))
