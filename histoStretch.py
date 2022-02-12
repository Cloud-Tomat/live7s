#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 19:36:23 2022

@author: nicolas
"""
import cv2
import matplotlib.pyplot as plt
from astropy.visualization import (MinMaxInterval, SqrtStretch,AsinhStretch,LogStretch,ImageNormalize)
import numpy as np
from skimage.color import rgb2hsv,hsv2rgb
from skimage import exposure
import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'


def methode1(imageData):

    hsv_img = rgb2hsv(imageData)
    v=hsv_img[:,:,2]

    # Create interval object
    interval = MinMaxInterval()
    vmin, vmax = interval.get_limits(v)
    # Create an ImageNormalize object using a SqrtStretch object
    
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch(a=10000))
    v=norm(v).astype("float64")
    
    hsv_img[:,:,2]=v
    
    normImage=hsv2rgb(hsv_img)

    return normImage

def methode2(imageData):
    
    imageData = exposure.equalize_adapthist(imageData, clip_limit=0.3)
    imageData=cv2.normalize(imageData,imageData)
    return imageData

def methode3(imageData):


    v=imageData
    # Create interval object
    interval = MinMaxInterval()
    print(v.dtype)
    vmin, vmax = interval.get_limits(v)
    # Create an ImageNormalize object using a SqrtStretch object
    
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch(a=10000))
    normImage=norm(v)

    return normImage

print("start processing")
print("open Image")
imageFile="/mnt/data/sandbox/liveStack/cap00000/liveStack/current.tif"
imageData = cv2.imread(imageFile,-1)

print("process")
normImage=methode3(imageData)
print("show")

fig = px.imshow(normImage)
fig.show()

# cv2.imshow("normalized",normImage)
# cv2.waitKey(0)

# plt.imshow(imageData)
# plt.show()
# plt.imshow(normImage)
# plt.show()