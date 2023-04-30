from GVS012GalvoScanner.GVS012Galvo import * 
import dash
from dash import html
from dash import dcc, DiskcacheManager, CeleryManager
from collections import deque
import math
from dash.dependencies import Input, Output, State
from dash import ctx
import dash_bootstrap_components as dbc
import math as m
import os
import time
import logging
import numpy as np
import asyncio
import threading
import matplotlib.pyplot as plt

global scan_data
scan_data = np.zeros([1,1])
n=0

galvo = GVS012Galvo(ULRange.BIP10VOLTS,"single_ended")
galvo.setX(0)
galvo.setY(0)
time.sleep(1)
vArray = []
outVal=0
s=1
ms=0.001*s
hz=1
f=1*hz 
p=1/f
ns=1e-9*s
tArray=[]
t = 0
A = 0.05 #For development purposes only!!! This needs to be set with the correct projection distances for the final setup in this case this is in cm.
X_trajectory = []
Y_trajectory = []
X_actualpos = []
Y_actualpos = []
maxV=0
minV=0
#t=None

async def run_rasterScan(x0, y0, spanx, spany, dx, dy, dt):
    global rasterScanTask
    #asyncio.to_thread(rasterScan(x0, y0, spanx, spany, dx, dy, dt))
    settings={"x0":float(x0), "y0": float(y0), "spanx":float(spanx), "spany":float(spany), "dx":float(dx), "dy": float(dy), "dt":float(dt)}
    coro=asyncio.to_thread(rasterScan, x0, y0, spanx, spany, dx, dy, dt)
    rasterScanTask = asyncio.create_task(coro)
    #await rasterScanTask

def rasterScan(x0, y0, spanx, spany, dx, dy, dt):
    global scan_data
    intergration_t = dt #Controls Integration Time
    tragx, tragy, x_axis, y_axis, scan_data = [],[],[], [], []
    nspanx=math.ceil(spanx/dx)
    nspany=math.ceil(spany/dy)
    x0=x0-1*spanx/2
    y0=y0-1*spany/2
    totalN=nspanx*nspany
    scan_data=np.zeros([nspanx, nspany])
    n=1
    t_left=0
    
    for i in range(nspanx):
        tragx.append(x0+dx*i)
    for j in range(nspany):       
        tragy.append(y0+dy*j)


    for i in range(nspanx):
        for j in range(nspany):
            galvo.setX(tragx[i])
            galvo.setY(tragy[j])
            x=galvo.getX()
            y=galvo.getY()
            c=galvo.getCounts(intergration_t)
            #c=randint(0,100)
            x_axis.append(x)
            y_axis.append(y)
            scan_data[i,j]=c
            #print(scan_data)
            t_left_temp=int((totalN-n)*1.1*intergration_t)
            if t_left_temp!=t_left:
                t_left=t_left_temp
                print(str(int(100*n/totalN))+"% Complete, expected time remaining: " + str(int(t_left))+"S")
            n+=1
    return 0
#t=threading.Thread(target=rasterScan, kwargs=settings, daemon=True)
#t.start()

#threading.Event

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # remove "Updating..." from title

app.layout=dbc.Container([
    dbc.Row([
        dbc.Col([
            # format and display current x value
            html.Div("X(um)", style={'margin-top':'5%', 'font-size' : '18px',
                                     'margin-left' : '2%'}),
            html.Div(0, id='current_x', style={'margin-left': '23%', 'border': '1px solid gray',
                                            'width' : '350px', 'height' : '26px',
                                            'background-color': 'floralwhite', 'margin-top': '-5%'}),

            # format and display current y value
            html.Div("Y(um)", style={'font-size' : '18px', 'margin-left' : '2%'}),
            html.Div(0, id='current_y', style={'margin-left': '23%', 'border': '1px solid gray',
                                            'width': '350px', 'height': '26px',
                                            'background-color': 'floralwhite', 'margin-top': '-5%'}),

            # format and display current y value
            html.Div("Z(um)", style={'font-size' : '18px', 'margin-left' : '2%'}),
            html.Div("z value displayed here", style={'margin-left': '23%', 'border': '1px solid gray',
                                                      'width': '350px', 'height': '26px',
                                                      'background-color': 'floralwhite', 'margin-top': '-5%'}),

            # format user input for x,y,z value
            html.Div("Xt(um)", style={'font-size': '18px', 'margin-left': '2%', 'border-top' : '2px dashed thistle',
                                      'margin-top' : '5%'}),
            dcc.Input("0", id="set_x", type="number", style={'margin-left': '23%', }, step=0.001),

            html.Div("Yt(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input("0", id="set_y", type="number", style={'margin-left': '23%', }, step=0.001),

            html.Div("Zt(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input(id="set_z", type="number", style={'margin-left': '23%', }, step=0.001),

            # create go-to button
            html.Br(),
            html.Button('Go to', id='go_to', style={'margin-left' : '8%',  'width' : '300px', 'margin-top' : '2%',
                                                    'border' : '2px inset', 'background-color' : 'lavender',
                                                    'border-radius': '6px', 'height': '40px'}),

            # create and format x,y span inputs
            html.Div("Xspan", style={'font-size': '18px', 'margin-left': '2%', 'border-top' : '2px dashed thistle',
                                         'margin-top' : '4%'}),
            dcc.Input("1", id="x_span", type="number", style={'margin-left': '23%',}, step=0.01, debounce=True),

            html.Div("Yspan", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input("1", id="y_span", type="number", style={'margin-left': '23%',}, step=0.01, debounce=True),

            # create and format V, dx, dy inputs
            html.Div("dt", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("0.001", id="dt", type="number", style={'margin-left': '23%',}, step=0.0001),

            html.Div("dx", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("0.1",id="dx", type="number", style={'margin-left': '23%',}, step=0.001),

            html.Div("dy", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("0.1", id="dy", type="number", style={'margin-left': '23%',}, step=0.001),

            # create scan button
            html.Br(),
            html.Button('Scan', id='scan', style={'margin-left' : '8%',  'width' : '300px', 'margin-top' : '2%',
                                                    'border' : '2px inset', 'background-color' : 'lavender',
                                                    'border-radius': '6px', 'height': '40px'}),
            html.Button('Stop/Resume', id='stop', style={'margin-left' : '8%',  'width' : '300px', 'margin-top' : '2%',
                                                    'border' : '2px inset', 'background-color' : 'pink',
                                                    'border-radius': '6px', 'height': '40px'}),
            html.Div(id='hidden-div', style={'display':'none'})

        ],  align='start', width=3),
        dbc.Col([
            html.Button('Restart', id='restart', style={'margin-left' : '8%',  'width' : '100px', 'margin-top' : '150px',
                                                    'border' : '2px inset', 'background-color' : 'lavender',
                                                    'border-radius': '6px', 'height': '40px', })
        ], width=1),
        dbc.Col([
            dcc.Graph(id='graph',  style={'height': '100vh', 'width' : '100vh', 'margin-left' : '10%'},  clickData=None,
                      hoverData=None),
            dcc.Interval(id="interval", disabled=True)

        ], width=8)
    ], justify='start')
], fluid=True, style={'background-color': 'ghostwhite'})


'''
   Output is the current x and y values shown in the yellow top left part of the gui. 
   This callback updates the current numeric value of the actual position whenever the go-to button is pressed,
            and when the scanning is running
    During scanning, x, y are only updated when n (# of intervals passed) > 0. otherwise they are set at 0,0 
    '''
@app.callback(Output('current_x', 'children'), 
              Output('current_y', 'children'),
              [State('set_x', 'value'),
               State('set_y', 'value'),
               Input('go_to', 'n_clicks'),
               Input('interval', 'n_intervals'),
               ])
def setting_x(setx, sety, go_to, n):
    x = galvo.getX()
    y = galvo.getY()
    if 'go_to' == ctx.triggered_id:
        print("Going to" + str(setx) + ", " + str(sety))
        galvo.setX(float(setx))
        galvo.setY(float(sety))
    return x, y

'''create a graph layout (add traces, define xy range, line color,...) whenever scan and go-to button is pressed.
   Also graph a simulated set-x, set-y value whenever go-to is pressed'''

@app.callback(Output('graph', 'figure'),
                [Input('scan', 'n_clicks'),
               Input('interval', 'n_intervals'),
               ])
def update_axis(scan,n):

    print("Updating Axis")
    trace4 = {'z': scan_data, 'type' : 'heatmap'}

    return dict(data=[trace4])


'''callback to turn on/off the interval counter
    output is disabled=True for disabling the counter
    '''
@app.callback(Output('interval', 'disabled'),
              [Input('go_to', 'n_clicks'),
              Input('scan', 'n_clicks'),
              Input('stop', 'n_clicks'),
              Input('restart', 'n_clicks'),
              State('interval', 'disabled')])

def disable_interval(goto, scan, stop, restart, disabled ):
    if 'scan' == ctx.triggered_id:
        return False
    elif 'stop' == ctx.triggered_id:
        if (disabled == True):
            return False
        else:
            return True
    elif 'go_to' == ctx.triggered_id:
        return True
    else:
        return True

'''callback to update # of interval passed and the speed of the interval counter
    output is #interval passed, counter speed
    The flow of the program should be normal when you pressed Go-to -> Scan -> Stop -> Go-to ...
    I still leave the restart button here in case the program starts lagging when u don't go according to the flow'''
@app.callback(Output('interval', 'n_intervals'),
              Output('interval', 'interval'),
              [State('dt', 'value'),
               State('interval', 'n_intervals'),
               State('interval', 'disabled'),
              Input('scan', 'n_clicks'),
              #Input('go_to', 'n_clicks'),
              Input('restart', 'n_clicks'),
               Input('stop', 'n_clicks'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State("set_x", 'value'),
               State("set_y", 'value'), 
               State('dx', 'value'),
               State('dy', 'value')])
def restart_interval(dt, interval, disabled, scan, restart, stop, spanx, spany, x0, y0, dx, dy):
    global rasterScanTask
    plotInterval=1000
    dt=float(dt)
    dx=float(dx)
    dy=float(dy)
    spanx=float(spanx)
    spany=float(spany)
    x0=float(x0)
    y0=float(y0)
    if 'scan' == ctx.triggered_id:
        settings={"x0":float(x0), "y0": float(y0), "spanx":float(spanx), "spany":float(spany), "dx":float(dx), "dy": float(dy), "dt":float(dt)}
        #print(threading.active_count())
        t=threading.Thread(target=rasterScan, kwargs=settings, daemon=True)
        t.start()
        #rasterScanTask=asyncio.to_thread(run_rasterScan, kwargs=settings)
        #asyncio.run(run_rasterScan(x0, y0, spanx, spany, dx, dy, dt))
        return 0, plotInterval #10^6 is because base unit is um and interval is ms
    elif 'stop' == ctx.triggered_id:
        try:
            print("Stop Requested")
            #rasterScanTask.cancel()
        except:
            print("Stop Stopped Already")
        if (disabled == True):
            return interval, plotInterval
        else:
            return interval, 0
    elif 'restart' == ctx.triggered_id:
        return 0, dt
    else:
        return 0, 0
    
'''   #if 'scan' == ctx.triggered_id:
   #     try:
  #          rasterScanTask.cancel()
    #    except:
  #          print("RUNNING")
        #if asyncio.all_tasks() is not []:
            #rasterScanTask.cancel()
        #asyncio.run(run_rasterScan(x0, y0, spanx, spany, dx, dy, dt))
        print("RASTER SCAN RUN REQUESTED")
        print(rasterScanTask)
    #    return 0, plotInterval #10^6 is because base unit is um and interval is ms
    elif 'stop' == ctx.triggered_id:
        try:
            print("Stop Requested")
            #rasterScanTask.cancel()
        except:
            print("Stop Stopped Already")
        if (disabled == True):
            return interval, plotInterval
        else:
            return interval, 0
    elif 'restart' == ctx.triggered_id:
        print("restart requested")
        try:
            $rasterScanTask.cancel()
        except:
            print("Restart Stooped Already")
        return 0, dt
    else:
        return 0, 0'''


if __name__ == '__main__':
    app.run_server(debug=True)