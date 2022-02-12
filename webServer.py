#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 21:11:14 2022

@author: nicolas
"""
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


imageFile="/mnt/data/sandbox/liveStack/cap00000/liveStack/current.tif"




server = Flask(__name__, static_url_path='')
socket = SocketIO(server, async_mode='eventlet')
app = dash.Dash(__name__, server=server,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
app.layout =layout.layout

def change(id, val):
	socket.emit('call', {'id': id, 'val': val})

def timerCallback():
    global mmiProcess
    Timer(1.0, timerCallback).start()
    mmiProcess.pushToLog(str(randint(0, 10000)))
    change("log",{'value': mmiProcess.logToString()})
    print(mmiProcess.logToString())
    if mmiProcess.checkFileUpdate():
        change('fakeOutput1', {'children': str(randint(0, 10000))})
        print("FileUpdate")

def figureUpdate(imageData):    #,status):
    
    fig = px.imshow(imageData, binary_string=True, binary_backend="jpg",binary_compression_level=5,)
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


@app.callback(
                Output('fakeOutput2','children'),
                Input('stretchSlider', 'value'))
def adjustStretch(value):
    global mmiProcess
    print("stretch Callback")
    # print(callback_context.triggered[0])
    print("value",value)
    if callback_context.triggered[0]['prop_id']=='stretchSlider.value':
        print("adjust image stretch")
        print(value)
        mmiProcess.adjustStretch(value)
        return ""
    
                
                
@app.callback(
                Output('fakeOutput1','children'),
                Input('autoHisto', 'value')
            )
def autoStretch(value):
    global mmiProcess
    print("AutoStretch Callback")
    print(callback_context.triggered[0])
    print("value",value)
    if callback_context.triggered[0]['prop_id']=='autoHisto.value':
        print("toggle image stretch")
        mmiProcess.displayOriginal=not value
        return ""
    
 
  

@app.callback(
                Output('liveImg', 'figure'),
                Output('status', 'children'),
                Input('fakeOutput1','children'),
                Input('fakeOutput2','children'),
                State('status', 'children')
              )
def update_graph_scatter(trigger1,trigger2,statusIn):
    global mmiProcess
    
    #check if file has been updated
    if trigger1:
        print("update from file")
        fig= figureUpdate(mmiProcess.readFile())
        return fig,mmiProcess.serialize()
    
    #check if Status has been updated    
    if statusIn:
        # status=str(figIn["data"][0]["name"])
        status=statusIn
        if status!=mmiProcess.serialize():
            print("Update display parameters")
            fig= figureUpdate(mmiProcess.getImageData())
            return fig,mmiProcess.serialize()
    else:
        #figure is not initialized
        print("Initial update")
        fig= figureUpdate(mmiProcess.readFile())
        return fig,mmiProcess.serialize()

    print("No Update")
    return dash.no_update,dash.no_update

    


if __name__ == "__main__":
    mmiProcess=cmmiPocess(imageFile)
    timerCallback()

    # app.run_server(host= '0.0.0.0')
    socket.run(server, debug=False, port=5000, host='0.0.0.0')