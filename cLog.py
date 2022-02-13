#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 10:29:08 2022

@author: nicolas
"""
import collections

class cLog():
    def __init__(self,size=10):
        self.log=collections.deque(size*[""])
        
    
    def pushToLog(self,log):
        self.log.appendleft(log)
        
    def logToString(self):
        return "\n".join(self.log)
    
    def logToFile(self):
        pass