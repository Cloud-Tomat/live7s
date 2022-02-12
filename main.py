#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 11:58:37 2022

@author: nicolas
"""

import stack
import gphoto
import time
import shutil
from pathlib import Path
import glob


def createWorkingDir(base):    
    existingDir=glob.glob('/mnt/data/sandbox/liveStack/cap*/', recursive = True)
    existingDir.sort()
    if len(existingDir)==0:
        dirNum=0
    else:
        if len(existingDir[-1])<6:
            dirNum=0
        else:
            try:
                dirNum=int(existingDir[-1][-6:-1])+1
            except:
                dirNum=0

    base=base+"/cap%05d"%dirNum
    capture=base+"/capture"
    process=base+"/process"
    liveStack=base+"/liveStack"
    
    
    Path(base).mkdir(parents=True, exist_ok=True) 
    Path(capture).mkdir(parents=True, exist_ok=True)
    Path(process).mkdir(parents=True, exist_ok=True)
    Path(liveStack).mkdir(parents=True, exist_ok=True)
    return(capture,process,liveStack)


if __name__ == '__main__':
    
    #create Dir structure for the project
    (capture,process,liveStack)=createWorkingDir("/mnt/data/sandbox/liveStack")

    cap=gphoto.capture(capture,process,"/mnt/data/sandbox/liveStack/simul")
    # cap=gphoto.capture(capture,process)

    cap.startCapture(50)

    ch=stack.convertAndStack(process)
    ch.StartConversionProcess("conv2")
    
    while not cap.terminate:
        time.sleep(1)
        # ch.convertHelper("conv2")
        # print("converting")

    ch.stopConversionProcess()

    ch.close()
            