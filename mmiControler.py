#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 09:17:53 2022

@author: nicolas
"""


import cv2
import os
from astropy.visualization import (MinMaxInterval, SqrtStretch,AsinhStretch,LogStretch,ImageNormalize)




class cmmiPocess:
    MAX=65535
    def __init__(self,imageFile):
        self.imageData=None
        self.displayImageData=None
        
        self.imageFile=imageFile
        self.lastModified=None
        self.low=0
        self.high=100
        self.displayOriginal=True
        self.isInit=False
        self.a=10000


    def startDark(self,num):
        if not self.startDarkCb is None:
            self.startDarkCb(num)
  
    def checkFileUpdate(self):
        fileDate=os.path.getmtime(self.imageFile)
        if not self.isInit:
            self.readFile()
            self.lastModified=fileDate
            self.isInit=True
            return True
        
        if fileDate==self.lastModified:
            return False
        else:
            self.lastModified=fileDate
            return True

    def logStretch(self):
    
        if self.imageData is None:
            return None
        
        # Create interval object
        interval = MinMaxInterval()
        vmin, vmax = interval.get_limits(self.imageData)
        
        # Create an ImageNormalize object using a logStrertch object
        norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=LogStretch(self.a))
        normImage=norm(self.imageData)
    
        return normImage

    def readFile(self):
        
        self.imageData = cv2.imread(self.imageFile,-1)
        scale_percent = 50 # percent of original size
        width = int(self.imageData.shape[1] * scale_percent / 100)
        height = int(self.imageData.shape[0] * scale_percent / 100)
        dim = (width, height)
          
        # resize image
        self.imageData = cv2.resize(self.imageData, dim, interpolation = cv2.INTER_AREA)
 
        
        # self.imageData=cv2.resize(self.imageData, ())
        self.displayImageData=self.logStretch()
        if self.displayOriginal:
            return self.imageData
        else:
            return self.displayImageData
        
    
    def getImageData(self):
        if not self.isInit:
            self.readFile()
            self.isInit=True

        if self.displayOriginal:
            print("Original")
            return self.imageData

        else:
            print("stretched")
            return self.displayImageData


    def adjustStretch(self,a):
        self.a=a
        self.displayImageData=self.logStretch()

    def serialize(self):
        ser={
            "displayOriginal":self.displayOriginal,
            "a":self.a
            }
        return str(ser)
