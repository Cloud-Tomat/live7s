#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 21:47:26 2022

@author: nicolas
"""
from pysiril.siril import Siril
from pysiril.wrapper import Wrapper
from pysiril.addons import Addons
import glob
import os
import time
import threading


class convertAndStack():
    def __init__(self,workingDir):
        self.app=Siril()                                 # Starts pySiril
        self.cmd=Wrapper(self.app)                            # Starts the command wrapper
        self.app.Open()
        self.cmd.set16bits()
        self.cmd.setext('fit')
        self.workingDir=workingDir
        self.terminate=False
        self.thread=None
        self.interSeqNum=0
        self.interSeqSize=10
        self.cmd.cd(workingDir)
   
    def convertHelper(self,baseName):
        srcDir=self.workingDir
        dstDir=self.workingDir
        self.cmd.cd(srcDir)

            
        #prepare the file to be converted
        #--------------------------------
        #freeze the file list (any file added after this step will be discarded till next run)
        srcFiles=glob.glob(srcDir+'/*.arw2')
        if len(srcFiles)==0:
            print("nothing to do")
            return False #nothing to do
        srcFiles.sort()
        startNum=int(srcFiles[0][-10:-5])

        #rename for Siril to detect them, any new arw2 file added will not be processed till next run
        [os.rename(src, src.replace(".arw2",".arw")) for src in srcFiles]

        
        #Convert to FITS
        #---------------
        self.cmd.convertraw(baseName, out=dstDir,debayer=False,fitseq=False,start=startNum)
        
        #Delete arw source
        #-----------------
        [os.remove(src) for src in glob.glob(srcDir+'/*.arw')]
        
        self.interStack(baseName)
        return True

    def conversionProcess(self,baseName):
        resCpt=0
        while not self.terminate or resCpt<4:
            time.sleep(1)
            res=self.convertHelper(baseName)
            if not res:
                resCpt+=1
            else:
                resCpt=0
    
    
    def StartConversionProcess(self,baseName):        
        self.terminate=False
        self.interSeqNum=0
        self.thread=threading.Thread(target=self.conversionProcess,args=[baseName])
        self.thread.start()

    def stopConversionProcess(self):
        if not self.thread is None:
            self.terminate=True
            self.thread.join()
            self.thread=None

    def interStack(self,baseName):
        fits=glob.glob(baseName+'*.fit')
        if len(fits)>=self.interSeqSize:
            #get the last  n file and isolate them in a dir for Siril to process them
            fits.sort()
            fits=fits[:self.interSeqSize]
            targetDir=self.workingDir+"/%d"%self.interSeqNum
            #Move the files to the dir and set siril process dir to process them
            os.mkdir(targetDir)
            [os.rename(src,targetDir+"/"+src) for src in fits]
            res=self.cmd.cd(targetDir)
            #debayer and apply dark
            res=self.cmd.preprocess(baseName, cfa=True, equalize_cfa=True, debayer=True )
            #register
            res=self.cmd.register("pp_"+baseName)
            #stack
            res=self.cmd.stack('r_pp_'+baseName, type='rej', sigma_low=3, sigma_high=3, norm='addscale', output_norm=True)
            #if file exists we assume succeed
            stacked='r_pp_'+baseName+"_stacked.fit"
            if os.path.isfile(stacked):
                os.rename(stacked,self.workingDir+"/../liveStack/preStack_%05d.fit"%self.interSeqNum)

            self.interSeqNum+=1
            return True
        
        return False
    
    def quickStack(self):
        baseName="preStack"
        res=self.cmd.cd(self.workingDir+"/../liveStack")
        fits=glob.glob('*.fit')
        print(fits)
        if len(fits)==0:
            return
        
        if len(fits)==1:
            res=self.cmd.load(fits[0])
        else:
            res=self.cmd.register(baseName)
            res=self.cmd.stack('r_'+baseName, type='rej', sigma_low=3, sigma_high=3, norm='addscale', output_norm=True)
            stacked="r_"+baseName+"_stacked.fit"
            if os.path.isfile(stacked): 
                os.rename(stacked,"stack01.fit")
                stacked="stack01.fit"
                self.cmd.load(stacked)
                print("stack success")
            else:
                self.cmd.load(fits[-1])
                print("stack failed")
            
            self.cmd.savetif("current")
            [os.remove(f) for f in glob.glob("r_*")]
            [os.remove(f) for f in glob.glob("*.seq")]



    def close(self):
        self.app.Close()
        del self.app



if __name__ == '__main__':
    ch=convertAndStack("/mnt/data/sandbox/liveStack/cap00000/process")
    # ch.convert("conv","/mnt/data/sandbox/liveStack/toProcess","/mnt/data/sandbox/liveStack/converted")
    # ch.interStack("conv2")
    ch.quickStack()
    ch.close()


