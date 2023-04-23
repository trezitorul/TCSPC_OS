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

import matplotlib.pyplot as plt

global data_matrix
data_matrix = np.zeros([1,1])
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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # remove "Updating..." from title
'''List to store values for graphing.
   maxlen is not the number of points that are retained in the graph. That is determined in the extendData callback'''
X_sim = deque(maxlen=50) #simulated x
Y_sim = deque(maxlen=50) #simulated y
X = deque(maxlen=50) #actual x
Y = deque(maxlen=50) #actual y 
count_data = []
''' formatting app
    dbc.Row and dbc.Col: use row and column for easy formatting. 
    here I used 1 row and 2 main columns: 1 column for interactive buttons and inputs to the left,
                                          1 column for the graph to the right'''
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
            dcc.Input("1",id="dx", type="number", style={'margin-left': '23%',}, step=0.01),

            html.Div("dy(nm)", style={'font-size': '18px', 'margin-left': '2%', 'margin-top' : '2%'}),
            dcc.Input("1", id="dy", type="number", style={'margin-left': '23%',}, step=0.01),

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

'''callback to store simulated and actual x and y values used for graphing, and move and read the position of the hardware
   callback is called for every update in the intervals.
   the output of this function, which is the children of 'hidden-div', is not used in the rest of the code (you can ignore the enable)
   '''
@app.callback(Output('hidden-div', 'children'),
              [State('set_x', 'value'),
               State('set_y', 'value'),
               State('interval', 'interval'),
               Input('interval', 'n_intervals'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State('dx', 'value'),
               State('dy', 'value')])    
def background_update(setx, sety, integrationTime ,n, spanx, spany, dx, dy):
    enable = False
    if (float(dx) < 1):
        num_points_row =  int(int(spanx) // float(dx)) + 2
    else:
        num_points_row = int(spanx) // float(dx) + 1

    y = int(sety) + int(spany) / 2 - float(dy) * (int(n) // num_points_row)

    if (n==0):
        x = int(setx) + int(spanx) * (-1) / 2

    #even row (x traverse right)
    elif ((int(n) // num_points_row) % 2 == 0):
        x = int(setx) + int(spanx) * (-1) / 2 + (int(n) % num_points_row) * float(dx)
    
    #odd row
    else:
        x = int(setx) + int(spanx) / 2 - ((int(n)) % num_points_row) * float(dx)
    
    if x>=-5 and x<=5 and y >=-5 and y<=5:
        if y >= (int(sety) - int(spany)/ 2):
            enable = True
            X_sim.append(x)
            Y_sim.append(y)
            galvo.setX(x)
            galvo.setY(y)

            
    x1 = galvo.getX()
    y1 = galvo.getY()
    X.append(x1)
    Y.append(y1)
    print(x)
    print(y)

    count = galvo.getCounts(integrationTime/1000)
    #count=randint(0,1000)
    count_data.append(count)
 

    return enable

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
    if 'go_to' == ctx.triggered_id:
        #galvo.setX(setx)
        #galvo.setY(sety)
        galvo.setX(0)
        galvo.setY(0)
        time.sleep(0.4)
        x = galvo.getX()
        y = galvo.getY()
        return x, y
    else:
        if (n>0):
            return X[-1], Y[-1]
        else: 
            return 0,0 


'''create a graph layout (add traces, define xy range, line color,...) whenever scan and go-to button is pressed.
   Also graph a simulated set-x, set-y value whenever go-to is pressed'''

@app.callback(Output('graph', 'figure'),
                [Input('scan', 'n_clicks'),
            #     Input('go_to', 'n_clicks'),
            Input('interval', 'n_intervals'),
               State('x_span', 'value'),
               State('y_span', 'value'),
               State('set_x', 'value'),
               State('set_y', 'value'),
               State('dx', 'value'),
               State('dy', 'value'),
               ])
def update_axis(scan, n,spanx, spany, setx, sety,dx,dy):

    if n==0:
        xspan = int(int(spanx) // float(dx)) + 2
        yspan = int(int(spanx) // float(dx)) + 2
        global data_matrix
        data_matrix = np.zeros((math.ceil(yspan), math.ceil(xspan)))
    # trace1 = {'x': [], 'y' : [], 'mode': 'markers', 'name': 'actual', "marker" : {"color" : "rgb(235,37,37)"}}
    # trace2 = {'x': [int(setx)], 'y': [int(sety)], 'name' : 'center'}
    # trace3 = {'x': [], 'y':[], 'mode' : 'line',  "line" : {"width" : "1", "color" : "rgb(192,192,192)"},
    #             'name' : 'simulated'}
    # if "go_to" == ctx.triggered_id:
    #     return if "go_to" == ctx.triggered_id:
    #                 layout=dict(xaxis=dict(range=[int(spanx) * (-1), int(spanx)]),
    #                             yaxis=dict(range=[int(spany) * (-1),  int(spany)])))
    # else:
    #     return dict(data=[trace3, trace2, trace1],
    #           layout=dict(xaxis=dict(range=[(int(setx) - int(spanx) /2 - 1), int(setx) + int(spanx)/2 + 1]),
    #                       yaxis=dict(range=[int(sety) - int(spany) /2 - 1, int(sety) + int(spany)/2 + 1])))
    
    trace4 = {'z': data_matrix, 'type' : 'heatmap'}
    if "go_to" == ctx.triggered_id:
        return dict(data=[trace4])
    if (n > 0): 
        i = int(n%data_matrix.shape[0])
        j = int(n/data_matrix.shape[1])
        print("---------------------------")
        print(data_matrix.shape)
        print(i)
        print(j)
        print(count_data[-1])
        data_matrix[j][i] = count_data[-1]
    return dict(data=[trace4])
'''callback to extend more data points in the graph. 
    output in the form of [value to be added to the trace, which trace, # points to retain on the graph]
    value to be added to the trace is taken from the stored lists
    The actual reading is only plotted when (# of interval passed) > 0  '''
# @app.callback(Output('graph', 'extendData'),
#               [State('set_x', 'value'),
#                State('set_y', 'value'),
#                State('x_span', 'value'),
#                State('y_span', 'value'),
#                State('dx', 'value'),
#                State('dy', 'value'),
#                Input('interval', 'n_intervals')],)
# def extend_data(setx, sety, spanx, spany, dx, dy, n):
    
    
    # if (n > 0):
    #     return dict(x=[ [X_sim[-1]], [X[-1]]], y=[[Y_sim[-1]], [Y[-1]]]), [0,2], 1000
    # else:
    #     return dict(x=[[X_sim[-1]]], y=[[Y_sim[-1]]]), [0], 1000
    #     return 
    


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
              [State('velocity', 'value'),
               State('interval', 'n_intervals'),
               State('interval', 'disabled'),
              Input('scan', 'n_clicks'),
              #Input('go_to', 'n_clicks'),
              Input('restart', 'n_clicks'),
               Input('stop', 'n_clicks'),
               State('x_span', 'value'),
               State('y_span', 'value'),
            State('dx', 'value'),
               State('dy', 'value')])
def restart_interval(vel, interval, disabled, scan, restart, stop, spanx, spany, dx, dy):
    if 'scan' == ctx.triggered_id:
        xspan = int(int(spanx) // float(dx)) + 2
        yspan = int(int(spanx) // float(dx)) + 2
        global data_matrix
        data_matrix = np.zeros((math.ceil(yspan), math.ceil(xspan)))
        return 0, (1 / int(vel)) * pow(10,6) #10^6 is because base unit is um and interval is ms
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