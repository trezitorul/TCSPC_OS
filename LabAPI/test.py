import dash
from dash import html
from dash import dcc
from collections import deque
import math
from dash.dependencies import Input, Output, State
from dash import ctx
import dash_bootstrap_components as dbc
import os
import time
import logging
import sys
import clr
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from ctypes import *
from System import Decimal
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
    channel.StartPolling(1)
    time.sleep(0.5)
    channel.EnableDevice()
    time.sleep(0.25)
    return channel 
def initialize_allchan(device):
    channelX = create_channel(device,1)
    set_mode(channelX,"CloseLoop")
    set_zero(channelX)
    channelY = create_channel(device,2)
    set_mode(channelY,"CloseLoop")
    set_zero(channelY)
    return [channelX,channelY]
def get_general_channel_inf0(channel):
    general_info =[piezoconfig,currentsettings,channel_info]
    piezoconfig = channel.GetPiezoConfiguration(channel.DeviceID)
    currentsettings = channel.PiezoDeviceSettings 
    channel_info = channel.GetDeviceInfo()
    return general_info
def set_zero(channel):
    initial_position = Decimal(0)
    channel.SetPosition(initial_position)
    initial_voltage = Decimal(0)
    channel.SetOutputVoltage(initial_voltage)
    time.sleep(0.5)
def set_mode(channel,mode):
    if mode == "CloseLoop":
        mode = Piezo.PiezoControlModeTypes.CloseLoop
    elif mode =="OpenLoop":
        mode = Piezo.PiezoControlModeTypes.OpenLoop   
    channel.SetPositionControlMode(mode)
   

def main():
    try: 
        deviceID = "71201654"
        device = Setup_BPC(deviceID)
        [channelX,channelY] = initialize_allchan(device)
        
        ##[pos_trajectory,pos_list,time_list]=channel_scan(channelX,0.01,5,5,2)
        ##plt.plot(time_list,pos_list,color ='r', label = "actual position")
        ##plt.plot(time_list,pos_trajectory,color ='g', label = "trajectory")
        duration = 5
        interval = 0.001
        traj_sample_size = int(duration // interval)
        t = np.linspace(0,duration,traj_sample_size)
        #fund_traj = signal.square(2 * np.pi * 0.25 * t)
        fund_traj = np.sin(2*np.pi*(0.25)*t)
        peak_location = 5
        amp = peak_location / 2
        traj = [(amp * x) + amp for x in fund_traj]
        pos_list = []
        time_list = []
        pos_refreshrate = 0.001
        temp_time = 0
        i = 0
        interval_pos = int(pos_refreshrate // interval)
        time0 = time.time()
        for i in range(len(traj)):
            if (i % interval_pos == 0) :
                channelX.SetPosition(Decimal(float(traj[i])))
            temp_pos = Decimal.ToDouble(channelX.GetPosition())
            pos_list.append(temp_pos)
            temp_time = time.time() - time0
            print([temp_pos,temp_time])
            time_list.append(temp_time)
            current_time = time.time() - time0
            target_time = i*interval
            while (current_time <= target_time):
                time.sleep(interval* 0.01)
                current_time = time.time() - time0
        
        fig, ax1 = plt.subplots()
        ax1.plot(time_list,pos_list, color='red')
        ax2 = ax1.twiny()
        ax2.plot(time_list,traj, color='green')
        fig.tight_layout()
        #plt.plot(t,traj)
        plt.show()
        device.Disconnect()
    except Exception as e:
        logging.warning(e)
        logging.warning('Device failed to setup')

if __name__ == "__main__":
    main()        