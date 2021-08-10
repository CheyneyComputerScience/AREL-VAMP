#!/usr/bin/env python
# coding: utf-8

# # ColorMask Batch
#
# This program is meant to get up to 2 image masks for the
# plants that are in one tank.
#
# Steps:
#
# For every file in every tank
# 1. read in the color image
# 2. filter based on hsv image
# 3. get bitmask based on filter
# 4. spatially cluster the bitmask
# 5. create image from spatial clusters
# 5. filter based on hue and value averages
# 6. save filtered bitmask and color images

# import needed files

# In[ ]:


import cv2 as cv
import numpy as np
# probably not needed for batch processing.
from matplotlib import pyplot as plt
# for spatial clustering
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

import os





def readImage(imageFile):
# 1. Read in the image

    parts = imageFile.split("/")
    filePath = parts[-1]
    tank = parts[-2]
    imageName = filePath.split(".")[0]
    imageName = "results/" + tank + "/" + imageName
    imageImage = cv.imread(imageFile)
    return imageImage

def colorMask(imageImage,minGreen, maxGreen,num):

# 2. Filter based on hsv image
    cpImage = imageImage.copy()
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.putText(cpImage,str(num),(3000,300), font, 10,(255,255,0),6,cv.LINE_AA)
    hsvImage = cv.cvtColor(imageImage, cv.COLOR_BGR2HSV)


# 3. Get bitmask based on filter
    mask = cv.inRange(hsvImage, minGreen, maxGreen)
    colorMask = cv.cvtColor(mask,cv.COLOR_GRAY2BGR)
    #numMask = np.asarray(mask)
    result = cv.bitwise_and(imageImage,imageImage,mask=mask)


# 4. show mask and image side by side
    topIm = np.concatenate((result,colorMask),axis=1)
    bottomIm = np.concatenate((imageImage,cpImage), axis=1)
    showMe = np.concatenate((topIm,bottomIm), axis=0)

    cv.imshow(title_window, showMe)

lh = 24
ls = 80
lv = 40
uh = 70
us = 255
uv = 255
tankNum = 0
currentImage = None

def on_trackbar_tn(val):
    global tankNum
    tankNum = val

def on_trackbar_lh(val):
    global lh
    lh = val

def on_trackbar_uh(val):
    global uh
    uh = val

def on_trackbar_ls(val):
    global ls
    ls = val

def on_trackbar_us(val):
    global us
    us = val


def on_trackbar_lv(val):
    global lv
    lv = val

def on_trackbar_uv(val):
    global uv
    uv = val

def nextClicked():
    global next
    next = True

next = False
title_window = "Color Mask"
cv.namedWindow(title_window)
trackbar_name = "lower hue"
cv.createTrackbar(trackbar_name, title_window , lh, 90, on_trackbar_lh)
trackbar_name = "tank number"
cv.createTrackbar(trackbar_name, title_window , tankNum, 18, on_trackbar_tn)
trackbar_name = "lower saturation"
cv.createTrackbar(trackbar_name, title_window , ls, 255, on_trackbar_ls)
trackbar_name = "upper saturation"
cv.createTrackbar(trackbar_name, title_window , us, 255, on_trackbar_us)
trackbar_name = "lower value"
cv.createTrackbar(trackbar_name, title_window , lv, 255, on_trackbar_lv)
trackbar_name = "upper value"
cv.createTrackbar(trackbar_name, title_window , uv, 255, on_trackbar_uv)
trackbar_name = "upper hue"
cv.createTrackbar(trackbar_name, title_window , uh, 90, on_trackbar_uh)

# ## For each tank and each image file

directory = 'largeStills'





rgbPaths = []
rgbNames = []
tankNums = []
for entry in os.scandir(directory):
    if entry.name == "tank4":
        for entry2 in os.scandir(entry.path):
            if "color" in entry2.name:
                rgbPaths.append(entry2.path)
                rgbNames.append(entry2.name)
                tankNums.append(int(entry.name[4:]))

rgbTuple = zip(rgbPaths,rgbNames,tankNums)

rgbTuple_sorted = sorted(rgbTuple)

lastLine = None
outfile = open("results/colorRange-tank4.txt",'a+')
outfile.seek(0)
lines = outfile.readlines()
if len(lines) > 0:
    lastLine = lines[-1]

for path,name,num in rgbTuple_sorted:
    if lastLine is not None:
        if lastLine.startswith(name):
            parts = lastLine.split('\t')
            lowVals = parts[1].replace('(','').replace(')','').split(',')
            upVals = parts[2].replace('(','').replace(')','').split(',')
            tankNum = int(parts[4])
            lh = int(lowVals[0])
            cv.setTrackbarPos("lower hue",title_window,lh)
            ls = int(lowVals[1])
            cv.setTrackbarPos("lower saturation",title_window,ls)
            lv = int(lowVals[2])
            cv.setTrackbarPos("lower value",title_window,lv)
            uh = int(upVals[0])
            cv.setTrackbarPos("upper hue",title_window,uh)
            us = int(upVals[1])
            cv.setTrackbarPos("upper saturation",title_window,us)
            uv = int(upVals[2])
            cv.setTrackbarPos("upper value",title_window,uv)


            lastLine = None
    else:
        print(path)
        currentImage = readImage(path)
        cv.setTrackbarPos("tank number",title_window,num)
        on_trackbar_tn(num)
        print(num,tankNum)
        while not next:
            colorMask(currentImage,(lh,ls,lv),(uh,us,uv),tankNum)
            x = cv.waitKey(1000)
            if x == ord('n') or x == ord("N"):
                outfile.flush()
                nextClicked()
            if x == ord('q'):
                outfile.close()
                exit()

        next = False
        outfile.write(name)
        outfile.write('\t')
        outfile.write('(' + str(lh) + ',' + str(ls) + ',' + str(lv) + ')')
        outfile.write('\t')
        outfile.write('(' + str(uh) + ',' + str(us) + ',' + str(uv) + ')')
        outfile.write('\t')
        outfile.write(str(num))
        outfile.write('\t')
        outfile.write(str(tankNum))
        outfile.write('\n')
