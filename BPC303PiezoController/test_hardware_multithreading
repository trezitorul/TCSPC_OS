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
import sys
import clr
import matplotlib.pyplot as plt
from ctypes import *
from System import Decimal
import threading

sys.path.append(r"C:\\Program Files\\Thorlabs\\Kinesis")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.Benchtop.PiezoCLI.dll")
clr.AddReference("System.Collections")
clr.AddReference("System.Linq")

from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI 
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceNotReadyException 
import Thorlabs.MotionControl.GenericPiezoCLI.Piezo as Piezo 
from Thorlabs.MotionControl.Benchtop.PiezoCLI import BenchtopPiezo 


#DeviceManagerCLI = cdll.LoadLibrary("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
#GenericMotorCLI = cdll.LoadLibrary("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
isPlotting=False
def Setup_BPC(deviceID):
    DeviceManagerCLI.BuildDeviceList()
    device =  BenchtopPiezo.CreateBenchtopPiezo(deviceID)
    device.Connect(deviceID)
    return device 

def create_channel(device,chan_no):
    channel = device.GetChannel(chan_no)
    if not channel.IsSettingsInitialized():
        channel.WaitForSettingsInitialized(10000)  
        assert channel.IsSettingsInitialized() is True
    return channel 
def get_general_channel_inf0(channel):
    general_info =[piezoconfig,currentsettings,channel_info]
    piezoconfig = channel.GetPiezoConfiguration(channel.DeviceID)
    currentsettings = channel.PiezoDeviceSettings 
    channel_info = channel.GetDeviceInfo()
    return general_info

#try: 
deviceID = "71201654"
device = Setup_BPC(deviceID)
channel=[0, 1, 2]
channel[0] = create_channel(device,1)
channel[0].StartPolling(250)
channel[1] = create_channel(device,2)
channel[1].StartPolling(250)
channel[2] = create_channel(device,3)
channel[2].StartPolling(250)
time.sleep(5)
for chan in channel:
    chan.EnableDevice()
time.sleep(0.25)
device_info = device.GetDeviceInfo()
print("With serial:",device_info.SerialNumber,"Initialize device:",device_info.Name)
mode = Piezo.PiezoControlModeTypes.CloseLoop
for chan in channel:
    chan.SetPositionControlMode(mode)
    chan.SetPosition(Decimal(0))
    chan.SetOutputVoltage(Decimal(0))
print("INITIALIZATION COMPLETE")
#except Exception as e:
#    logging.warning(e)
#    logging.warning('Device failed to setup')

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # remove "Updating..." from title

X = deque(maxlen=50)
Y = deque(maxlen=50)

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
            dcc.Input("0", id="set_x", type="number", style={'margin-left': '23%', }, step=0.2),

            html.Div("Yt(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input("0", id="set_y", type="number", style={'margin-left': '23%', }, step=0.2),

            html.Div("Zt(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input(id="set_z", type="number", style={'margin-left': '23%', }, step=0.2),

            # create go-to button
            html.Br(),
            html.Button('Go to', id='go_to', style={'margin-left' : '8%',  'width' : '300px', 'margin-top' : '2%',
                                                    'border' : '2px inset', 'background-color' : 'lavender',
                                                    'border-radius': '6px', 'height': '40px'}),

            # create and format x,y span inputs
            html.Div("Xspan(um)", style={'font-size': '18px', 'margin-left': '2%', 'border-top' : '2px dashed thistle',
                                         'margin-top' : '4%'}),
            dcc.Input("10", id="x_span", type="number", style={'margin-left': '23%',}, step=0.2, debounce=True),

            html.Div("Yspan(um)", style={'font-size': '18px', 'margin-left': '2%', }),
            dcc.Input("10", id="y_span", type="number", style={'margin-left': '23%',}, step=0.2, debounce=True),

            # create and format V, dx, dy inputs
            html.Div("V(nm/sec)", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("2000", id="velocity", type="number", style={'margin-left': '23%',}, step=0.2),

            html.Div("dx(nm)", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("1",id="dx", type="number", style={'margin-left': '23%',}, step=0.2),

            html.Div("dy(nm)", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("1", id="dy", type="number", style={'margin-left': '23%',}, step=0.2),

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

@app.callback(Output('hidden-div', 'children'),
              [State('set_x', 'value'),
               State('set_y', 'value'),
               Input('interval', 'n_intervals'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State('dx', 'value'),
               State('dy', 'value')])
               
def background_update(setx, sety, n, spanx, spany, dx, dy):
    num_points_row =  int(spanx) // int(dx) + 1
    y = int(sety) + int(spany) / 2 - int(dy) * (int(n) // num_points_row)

    if (n==0):
        x = int(setx) + int(spanx) * (-1) / 2

    #even row (x traverse right)
    elif ((int(n) // num_points_row) % 2 == 0):
        x = int(setx) + int(spanx) * (-1) / 2 + (int(n) % num_points_row) * int(dx)

    #odd row
    else:
        x = int(setx) + int(spanx) / 2 - ((int(n)) % num_points_row) * int(dx)

    if x>=0 and x<=15 and y >=0 and y<=15:
        if y >= (int(sety) - int(spany)/ 2):
        
            channel[0].SetPosition(Decimal(x))
            channel[1].SetPosition(Decimal(y))
            
    x1 = Decimal.ToDouble(channel[0].GetPosition())
    y1 = Decimal.ToDouble(channel[1].GetPosition())
    X.append(x1)
    Y.append(y1)
    print(X)
    print(Y)
    return 0

# setting x, y
@app.callback(Output('current_x', 'children'),
              Output('current_y', 'children'),
              [State('set_x', 'value'),
               State('set_y', 'value'),
               Input('go_to', 'n_clicks'),
               Input('interval', 'n_intervals'),
               ])
def setting_x(setx, sety, go_to, n):
    if 'go_to' == ctx.triggered_id:
        channel[0].SetPosition(Decimal(setx))
        channel[1].SetPosition(Decimal(sety))
        time.sleep(0.4)
        x = Decimal.ToDouble(channel[0].GetPosition())
        y = Decimal.ToDouble(channel[1].GetPosition())
        return x, y
    else:
        if (n>0):
            return X[-1], Y[-1]
        else: 
            return 0,0 




@app.callback(Output('graph', 'figure'),
               [Input('scan', 'n_clicks'),
                Input('go_to', 'n_clicks'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State('set_x', 'value'),
               State('set_y', 'value'),
               ])
def update_axis(click1, click2, spanx, spany, setx, sety):

    trace1 = {'x': [], 'y' : [], 'mode': 'markers', 'name': 'actual'}
    trace2 = {'x': [int(setx)], 'y': [int(sety)], 'name' : 'simulated'}
    #trace3 = {'x': [], 'y':[]}
    if "go_to" == ctx.triggered_id:
        return dict(data=[trace2],
                    layout=dict(xaxis=dict(range=[int(spanx) * (-1), int(spanx)]),
                                yaxis=dict(range=[int(spany) * (-1),  int(spany)])))
    else:
        return dict(data=[trace1, trace2],
              layout=dict(xaxis=dict(range=[(int(setx) - int(spanx) /2 - 1), int(setx) + int(spanx)/2 + 1]),
                          yaxis=dict(range=[int(sety) - int(spany) /2 - 1, int(sety) + int(spany)/2 + 1])))

@app.callback(Output('graph', 'extendData'),
              [State('set_x', 'value'),
               State('set_y', 'value'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State('dx', 'value'),
               State('dy', 'value'),
               Input('interval', 'n_intervals')],)
def extend_data(setx, sety, spanx, spany, dx, dy, n):
    num_points_row =  int(spanx) // int(dx) + 1
    y = int(sety) + int(spany) / 2 - int(dy) * (int(n) // num_points_row)

    if (n==0):
        x = int(setx) + int(spanx) * (-1) / 2

    #even row (x traverse right)
    elif ((int(n) // num_points_row) % 2 == 0):
        x = int(setx) + int(spanx) * (-1) / 2 + (int(n) % num_points_row) * int(dx)

    #odd row
    else:
        x = int(setx) + int(spanx) / 2 - ((int(n)) % num_points_row) * int(dx)
    
    if (n > 0):
        return dict(x=[[X[-1]]], y=[[Y[-1]]]), [0], 1000
    else:
        return dict(x=[[]], y=[[]]), [0], 1000


#@app.callback(Output('graph', 'extendData'),
#              Input('interval', 'n_intervals'))
#def extend_trace3(n):
#    x = Decimal.ToDouble(channel[0].GetPosition())
#    y = Decimal.ToDouble(channel[1].GetPosition())
#    return dict(x=[[x]], y=[[y]]), [2], 1000,
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

@app.callback(Output('interval', 'n_intervals'),
              Output('interval', 'interval'),
              [State('velocity', 'value'),
               State('interval', 'n_intervals'),
               State('interval', 'disabled'),
              Input('scan', 'n_clicks'),
              #Input('go_to', 'n_clicks'),
              Input('restart', 'n_clicks'),
               Input('stop', 'n_clicks')])
def restart_interval(vel, interval, disabled, scan, restart, stop):
    if 'scan' == ctx.triggered_id:
        return 0, (1 / int(vel)) * pow(10,6)
    elif 'stop' == ctx.triggered_id:
        if (disabled == True):
            return interval, (1 / int(vel)) * pow(10,6)
        else:
            return interval, 0
    elif 'restart' == ctx.triggered_id:
        return 0, (1 / int(vel)) * pow(10,6)
    else:
        return 0, 0


if __name__ == '__main__':
    app.run_server(debug=False)