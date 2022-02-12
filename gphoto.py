#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 15:12:36 2022

@author: nicolas
"""


import subprocess
import os
import threading
import glob
import shutil
import time

class capture():
    
    def __init__(self,targetDir,toProcessDir,simulDir=None):
        self.targetDir=targetDir
        self.toProcessDir=toProcessDir
        #to do test id dir exists and if not create them
        self.thread=None
        self.n=0
        self.terminate=False
        if not simulDir is None:
            self.simulation=True
            self.simulDir=simulDir
        else:
            self.simulation=False
        
    def capture(self):
        if self.simulation:
            self.__simCapture()
        else:
            self.__capture()
        
    def __simCapture(self):
        simuFiles=glob.glob(self.simulDir+'/*.ARW')
        i=0
        for file in simuFiles:
            shutil.copy(file,self.targetDir+"/src%05d.arw"%i )
            time.sleep(1)
            os.link(self.targetDir+"/"+"src%05d.arw"%i, self.toProcessDir+"/"+"src%05d.arw2"%i)
            i+=1
            print("Capture %d/%d"%(i,self.n))
            if i>self.n or self.terminate:
                self.terminate=True
                self.thread=None
                return
    
    def __capture(self):
        i=0

        while (i<=self.n and not self.terminate):
            #move to target dir and capture
            #-----------------------------
            # os.chdir(self.targetDir)
            # ret=subprocess.run(["gphoto2", "--capture-image-and-download","--force-overwrite"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            
            ret = subprocess.Popen(["gphoto2", "--capture-image-and-download","--force-overwrite"], cwd=self.targetDir,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            ret.wait()
            
            if ret.returncode==0:
                #rename and properly number the capture
                [os.rename(src, src.replace("capt0000","src%05d"%i)) for src in glob.glob(self.targetDir+'/*')]
                #extension modified to prevent siril from converting file
                #to do : check arw is present (raw+jpeg or raw selected on the camera)
                os.link(self.targetDir+"/"+"src%05d.arw"%i, self.toProcessDir+"/"+"src%05d.arw2"%i)
                i+=1
                print("Capture %d/%d"%(i,self.n))
            else:
                self.terminate=True
                print("Capture failed")
                print(ret.stderr)
        self.terminate=True
        self.thread=None
        

    def startCapture(self,n):
        self.n=n
        #clean directories
        [os.remove(src) for src in glob.glob(self.targetDir+'/*.*')]
        [os.remove(src) for src in glob.glob(self.toProcessDir+'/*.*')]
        
        self.terminate=False
        self.thread=threading.Thread(target=self.capture)
        self.thread.start()

    def abortCapture(self):
        if not self.thread is None:
            self.terminate=True
            self.thread.join()
            self.thread=None
        
if __name__ == '__main__':
    cap=capture("/mnt/data/sandbox/liveStack/trash","/mnt/data/sandbox/liveStack/toProcess","/mnt/data/sandbox/liveStack/simul")
    cap.startCapture(3)
