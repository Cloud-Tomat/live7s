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
        """
        Controler of web MMI

        Parameters
        ----------
        imageFile : String, path to initial iamge

        Returns
        -------
        None.

        """
        #original image array
        self.imageData=None
        
        #stretched image array
        self.displayImageData=None
        
        #image path+filename
        self.imageFile=imageFile
        
        #image last modification date
        self.lastModified=None
        
        #set original or stretched image
        self.displayOriginal=True
        
        #flag to know if initial image is loaded
        self.isInit=False
        
        #log stretch factor
        self.a=10000

  
    def checkFileUpdate(self):
        """
        Check if image file has been updated

        Returns
        -------
        bool.

        """
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
        """
        logarithm stretching of image
        Log paramameter is a class property

        Returns
        -------
        normImage : stretched image array

        """
    
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
        """
        Read image from file and stretch it 

        Returns
        -------
            Type : image array
            either original image or stretched image depending on 
            dislayOriginal Boolean class property

        """
        
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
        """
        return image array according to display parameter
        if image is not loaded, function load it from file

        Returns
        -------
            Type : image array
            either original image or stretched image depending on 
            dislayOriginal Boolean class property

        """
        if not self.isInit:
            self.readFile()
            self.isInit=True

        if self.displayOriginal:
            print("Original")
            return self.imageData

        else:
            print("stretched")
            return self.displayImageData

        TYPE
            DESCRIPTION.
    def adjustStretch(self,a):
        """
        Set stretch factor and update accordingly stretched image

        Parameters
        ----------
        a : float
            range ]0;10000]
            Returns
        -------
        None.

        """
        self.a=a
        self.displayImageData=self.logStretch()

    def serialize(self):
        """
        Store class property in a string
        used to check sync of MMI with controller
        Returns
        -------
        string
            class parameters

        """
        ser={
            "displayOriginal":self.displayOriginal,
            "a":self.a
            }
        return str(ser)
