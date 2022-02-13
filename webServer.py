#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 21:11:14 2022

@author: nicolas
"""

print ("starting")
import eventlet
eventlet.monkey_patch()



import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import Input, Output, State,dcc, html,callback_context
import plotly.express as px

import numpy as np

import dash_daq as daq
import random
from flask import Flask
from flask_socketio import SocketIO
from random import randint
from threading import Timer

import sockettest
import layout
from mmiControler import cmmiPocess
from cLog import cLog



print ("dependencies loaded")




class webInteract():
    def __init__(self,controler,callBacks):
        """
        Call dedicated to interaction with MMI web page
        Parameters
        ----------
        controler : controller class
        callBacks : list of functions
            [
                darkCallBack -> 1 arg = number of dark,
                CaptureCallBack -> 1 arg = number of image,
                TestCallBack -> No arg,
            ]
        some list element can be set to None if no callback wanted
        Returns
        -------
        None.

        """
        #---------------------------------------
        #configure the server to work with DASH
        #---------------------------------------
        self.server = Flask(__name__, static_url_path='')
        self.socket = SocketIO(self.server, async_mode='eventlet')
        self.app = dash.Dash(__name__, server=self.server,
                             external_stylesheets=[dbc.themes.BOOTSTRAP])

        self.app.scripts.config.serve_locally = True
        self.app.css.config.serve_locally = True
        self.app.layout =layout.layout
        
        
        #---------------------------------------
        #initialize controller
        #---------------------------------------
        self.mmiProcess=controler
        self.mmiProcess.readFile()
        
        #---------------------------------------
        #initialize callbacks
        #---------------------------------------
        self.app.callback(
            Output('trigger2','children'),
            Input('stretchSlider', 'value'))(self.adjustStretch)
            
        self.app.callback(
                    Output('liveImg', 'figure'),
                    Output('status', 'children'),
                    Input('trigger1','children'),
                    Input('trigger2','children'),
                    State('status', 'children')
                  )(self.update_graph_scatter)

        self.app.callback(
                    Output('trigger1','children'),
                    Input('autoHisto', 'value')
                )(self.autoStretch)
        
        self.app.callback(
                    Output('runDark','value'),
                    Input('runDark', 'n_clicks'),
                    State('DarkNb','value')
                )(self.startDark)
        
        self.app.callback(
                    Output('runCapture','value'),
                    Input('runCapture', 'n_clicks'),
                    State('ImgNb','value')
                )(self.startCapture)
        
        self.app.callback(
                    Output('Test','value'),
                    Input('Test', 'n_clicks'),
                )(self.startTest)

        self.callBacks=callBacks


    def runServer(self):
        """
        Run the webserver

        Returns
        -------
        None.

        """
        print("starting Server")
        self.socket.run(self.server, debug=False, port=5000, host='0.0.0.0')
        
    #----------------------------------------------------------
    #---------------- Action on Web Page--------------------------------
    #----------------------------------------------------------
    
    def printStatus(self,status):
        """
        Display Status on web page

        Parameters
        ----------
        status : string
        Returns
        -------
        None.

        """
        self.change("Status", {'value':status})

    
    def printLog(self,log):
        """
        Display log on web page

        Parameters
        ----------
        log : String

        Returns
        -------
        None.

        """
        self.change("log", {'value':log})

    def displayNewFile(self,file):
        """
        Display New file

        Parameters
        ----------
        file : TYPE String
            DESCRIPTION. Path to File to display

        Returns
        -------
        None.

        """
        mmiProcess.imageFile=file
        if self.mmiProcess.checkFileUpdate():
            self.change('trigger1', {'children': str(randint(0, 10000))})
            print("FileUpdate")
        pass

    #----------------------------------------------------------
    #---------------- CALL BACK--------------------------------
    #----------------------------------------------------------
    
    def adjustStretch(self,value):
        print("stretch Callback")
        # print(callback_context.triggered[0])
        print("value",value)
        if callback_context.triggered[0]['prop_id']=='stretchSlider.value':
            print("adjust image stretch")
            print(value)
            self.mmiProcess.adjustStretch(value)
            return ""


    def update_graph_scatter(self,trigger1,trigger2,statusIn):
        global mmiProcess
        
        #check if file has been updated
        if trigger1:
            print("update from file")
            fig= self.figureUpdate(self.mmiProcess.readFile())
            return fig,mmiProcess.serialize()
        
        #check if Status has been updated    
        if statusIn:
            status=statusIn
            if status!=mmiProcess.serialize():
                print("Update display parameters")
                fig= self.figureUpdate(self.mmiProcess.getImageData())
                return fig,self.mmiProcess.serialize()
        else:
            #figure is not initialized
            print("Initial update")
            fig= self.figureUpdate(self.mmiProcess.readFile())
            return fig,self.mmiProcess.serialize()
    
        print("No Update")
        return dash.no_update,dash.no_update


    def autoStretch(self,value):
        print("AutoStretch Callback")
        print(callback_context.triggered[0])
        print("value",value)
        if callback_context.triggered[0]['prop_id']=='autoHisto.value':
            print("toggle image stretch")
            self.mmiProcess.displayOriginal=not value
            return ""
    
    def startDark(self,n,nDark):
        print("start Dark Callback")
        print(callback_context.triggered[0])
        if callback_context.triggered[0]['prop_id']=='runDark.n_clicks':
            if not nDark is None:
                if not self.callBacks[0] is None:
                    self.callBacks[0](nDark)
                else:
                    print("no Dark callBack defined")
            else:
                print("Number of Dark not defined")
            return dash.no_update

    def startCapture(self,n,nCap):
        print("start Capture Callback")
        print(callback_context.triggered[0])
        if callback_context.triggered[0]['prop_id']=='runCapture.n_clicks':
            if not nCap is None:
                if not self.callBacks[1] is None:
                    self.callBacks[1](nCap)
                else:
                    print("no Capture callBack defined")
            else:
                print("Number of image not defined")
            return dash.no_update

    def startTest(self,n):
        print("start Test Callback")
        print(callback_context.triggered[0])
        if callback_context.triggered[0]['prop_id']=='Test.n_clicks':
            if not self.callBacks[2] is None:
                self.callBacks[2]()
            else:
                print("no Test callBack defined")

            return dash.no_update

    #----------------------------------------------------------
    #---------------- HELPERS--------------------------------
    #----------------------------------------------------------



    def change(self,id, val):
        """
        Push update to web page from python

        Parameters
        ----------
        id : String, id of item to update
        val : String, value of item to update
        Returns
        -------
        None.

        """
        self.socket.emit('call', {'id': id, 'val': val})
    
    
    def figureUpdate(self,imageData):  
        """
        Return a new figure with image updated
        Keep zoom level

        Parameters
        ----------
        imageData : numpy array, 

        Returns
        -------
        fig : plotly figure to be returned by callbacks
        """
        
        fig = px.imshow(imageData, binary_string=True, binary_backend="jpg",
                        binary_compression_level=5,)
        #preserve zoom after update
        # fig["data"][0]["name"]=status
        fig['layout']['uirevision'] = 'some-constant'
        fig.update_layout(
            height=800,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=0, b=0, l=0, r=0),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                linewidth=0
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                linewidth=0
            ),
            hovermode=False
        )
        return fig

if __name__ == "__main__":
    import cv2
    def caption(file,caption):
        img = cv2.imread(file,-1)
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,500)
        fontScale              = 1
        fontColor              = (0,0,255)
        thickness              = 1
        lineType               = 2
        
        cv2.putText(img,caption, 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)

        
        #Save image
        cv2.imwrite(caption+".jpg", img)
        

    
    
    def timerCallback1():
        global web,imageFile
        Timer(5.0, timerCallback1).start()
        id=str(randint(0, 10000))
        print(id)
        web.printLog(id)
        web.printStatus(id)
        caption(imageFile,id)
        web.displayNewFile(id+".jpg")
    
    
    def startDark(n):
        print("starting %d darks"%n)

    def startCapture(n):
        print("starting %d capture"%n)

    def startTest():
        print("starting Test")
    
    # imageFile="/mnt/data/sandbox/liveStack/cap00000/liveStack/current.tif"
    imageFile="/mnt/data/sandbox/liveStack/cap00000/liveStack/current.tif"
    logger=cLog()
    mmiProcess=cmmiPocess(imageFile)
    web=webInteract(mmiProcess,[startDark,startCapture,startTest])
    timerCallback1()
    web.runServer()


    
