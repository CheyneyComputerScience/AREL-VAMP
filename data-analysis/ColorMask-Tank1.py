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





def colorMask(imageFile, minGreen, maxGreen):
# 1. Read in the image

    parts = imageFile.split("/")
    filePath = parts[-1]
    tank = parts[-2]
    imageName = filePath.split(".")[0]
    imageName = "results/" + tank + "/" + imageName
    imageImage = cv.imread(imageFile)


# 2. Filter based on hsv image

    hsvImage = cv.cvtColor(imageImage, cv.COLOR_BGR2HSV)


# 3. Get bitmask based on filter
    mask = cv.inRange(hsvImage, minGreen, maxGreen)

# 4. Spatially cluster the bitmask

## setup the variables
# Get all x, y coordinates of white pixels in the mask
    x, y = np.where(mask == 255)
# these are the locations that are being labeled
    zipped = np.column_stack((x, y))
# these have been scaled to a floating point value
    scaled = StandardScaler().fit_transform(zipped)
# the scaled range scales from [0,1280] to [-2.5,2.5]
# so it's about a 256:1 conversion so
# the max distance in the scaled image space, about 12.8 pixels
    #max_distance=0.05
    max_distance=0.015
# the minimum number of points needed before the cluster is saved
    min_cluster_size = 100
# does the work
    db = DBSCAN(eps=max_distance, min_samples=min_cluster_size, n_jobs=-1).fit(scaled)


# 5. create image from all spatial clusters

# Number of clusters
    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    h, w = mask.shape
    label_img = np.zeros((h, w), np.uint8)

    label_tuples = [[] for x in range(n_clusters)]

    for z in range(0, len(db.labels_)):
        if db.labels_[z] > 0:
            label_tuples[db.labels_[z]].append((zipped[z][0],zipped[z][1]))


        if not db.labels_[z] == -1:
            # Add a cluster with a unique label color to the cluster image
            label_img[zipped[z][0], zipped[z][1]] = db.labels_[z]

    labelsName = imageName+"-"+str(n_clusters)+"-labels.png"
    cv.imwrite(labelsName,label_img)


# 6. filter based on hue and value and save bitmask and color image

# look for between 90 and 160 for value
# look for between 28 and 32 for hue
    imageLetter="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sliceName=imageName+"-slice"
    maskName= imageName+"-mask"

    b = 0
    for i in range(1,n_clusters):
        bitMask = (label_img == i).astype("uint8")
        componentMask = bitMask*255

        result = cv.bitwise_and(hsvImage,hsvImage,mask=componentMask)
        num_pix2 = np.count_nonzero(bitMask)
        h,s,v = cv.split(result)

        hueAve = np.sum(h)/num_pix2
        valAve = np.sum(v)/num_pix2
        if 28 < hueAve < 32 and 90 < valAve < 160 :
            corrected2 = cv.cvtColor(result, cv.COLOR_HSV2BGR)

            cv.imwrite(sliceName+"-"+imageLetter[b]+".png",corrected2)
            cv.imwrite(maskName+"-"+imageLetter[b]+".png",componentMask)
            b+=1



# ## For each tank and each image file

threshFile = open('results/colorRange.txt','r')
directory = 'largeStills/tank1/'

for line in threshFile.readlines():
    parts = line.split('\t')
    name = parts[0]

    lowVals = parts[1].replace('(','').replace(')','').split(',')
    upVals = parts[2].replace('(','').replace(')','').split(',')
    tankNum = int(parts[4])
    lh = int(lowVals[0])
    ls = int(lowVals[1])
    lv = int(lowVals[2])
    uh = int(upVals[0])
    us = int(upVals[1])
    uv = int(upVals[2])

    path = directory + name
    print("starting " + path)
    colorMask(path,(lh,ls,lv),(uh,us,uv))
    print("finished " + path)
