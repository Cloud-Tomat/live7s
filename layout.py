#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 09:05:29 2022

@author: nicolas
"""


import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html,dcc
import sockettest

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP]

#-----------------------------------------------------
#--------------------- side panel --------------------
#-----------------------------------------------------
controls = dbc.Card(
    [
        html.Div(
            [
                sockettest.sockettest(),
                dbc.Row(dbc.Label("Number of Dark")),
                dbc.Row(dbc.Input(id="DarkNb", type="number",  min=0, step=1,placeholder="number of dark")),
                dbc.Row(dbc.Button("Start Dark",id="runDark",n_clicks=0,style={"margin-top": "15px","margin-bottom": "15px"})),
            ]
        ),
        html.Div(
            [
                dbc.Row(dbc.Label("Number of Image")),
                dbc.Row(dbc.Input(id="ImgNb", type="number",  min=0, step=1,placeholder="number of image")),
                dbc.Row(dbc.Button("Start Capture",id="runCapture",style={"margin-top": "15px","margin-bottom": "15px"})),
            ]
        ),
        html.Div(
            [
                dbc.Row(dbc.Label("Status\n")),
                dbc.Row(dbc.Label("-",id="Status",style={"border":"1px lightgray solid"})),
                dbc.Row(dbc.Button("Test",id="Test",style={"margin-top": "15px","margin-bottom": "15px"})),
            ]
        
        ),
        html.Div(
            [
                dbc.Row(dbc.Label("Log\n")),
                # dbc.Row(dbc.Label("-",id="Log",style={"border":"2px black solid"})),
                dbc.Row(dcc.Textarea(id="log",readOnly=True,style={"border":"2px black solid",'whiteSpace': 'pre-wrap'})),
            ]
        
        ),
    ],
    body=True,
)


#-----------------------------------------------------
#--------------------- right view --------------------
#-----------------------------------------------------

graph=(
       html.P(id='status'),     #Storage of image status / 
       dbc.Row(dcc.Graph(id="liveImg")),
       dbc.Row((
           dbc.Col(dbc.Label("Histogram",style={"margin-top": "15px","margin-bottom": "15px"}),md=1),
           dbc.Col(daq.ToggleSwitch(label="stretch",id="autoHisto",value=False,style={'textAlign':'left',"margin-top": "15px","margin-bottom": "15px"})
                   ),)
               
           
           ),
       
       dbc.Row(dcc.Slider(id="stretchSlider", min=0, max=20000,value=10000)),)

#-----------------------------------------------------
#--------------------- Full layout --------------------
#-----------------------------------------------------

layout = dbc.Container(
    [
        html.P(id='trigger1',hidden=True),  #trick to cascade  callback 
        html.P(id='trigger2',hidden=True),  #trick to cascade  callback 
        html.P(id='stretch'),
        html.H1("Sony A7S Live Stacker"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(graph,md=8),
            ],
            align="center",
        ),
    ],
    fluid=True,
)