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
import decimal
#from decimal import Decimal
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

class BPC303Piezo:
    def __init__(self,mode,deviceID):
        self.mode = mode
        self.device = self.SetupDevice(deviceID)
        [self.channelX,self.channelY,self.channelZ] = self.InitializeAllchan()
    
    def SetupDevice(self,deviceID):
        DeviceManagerCLI.BuildDeviceList()
        device =  BenchtopPiezo.CreateBenchtopPiezo(str(deviceID))
        device.Connect(deviceID)
        return device 

    def CreateChannel(self,chan_no):
        channel = self.device.GetChannel(chan_no)
        if not channel.IsSettingsInitialized():
            channel.WaitForSettingsInitialized(10000)  
            assert channel.IsSettingsInitialized() is True
        channel.StartPolling(1)
        time.sleep(0.2)
        channel.EnableDevice()
        time.sleep(0.2)
        return channel 
    
    def SetZero(self,channel):
        initial_position = Decimal(0)
        channel.SetPosition(initial_position)
        initial_voltage = Decimal(0)
        channel.SetOutputVoltage(initial_voltage)
        time.sleep(0.25)
    
    def SetMode(self,channel,mode):
        if mode == "CloseLoop":
            mode = Piezo.PiezoControlModeTypes.CloseLoop
        elif mode =="OpenLoop":
            mode = Piezo.PiezoControlModeTypes.OpenLoop   
        channel.SetPositionControlMode(mode)
    
    def InitializeAllchan(self):
        channelX = self.CreateChannel(1)
        self.SetMode(channelX,self.mode)
        self.SetZero(channelX)
        channelZ = self.CreateChannel(2)
        self.SetMode(channelZ,self.mode)
        self.SetZero(channelZ)
        channelY = self.CreateChannel(3)
        self.SetMode(channelY,self.mode)
        self.SetZero(channelY)
        return [channelX,channelY,channelZ]

    def SetX(self,position):
        self.channelX.SetPosition(Decimal(float(position)))
    
    def SetY(self,position):
        self.channelY.SetPosition(Decimal(float(position)))

    def SetZ(self,position):
        self.channelZ.SetPosition(Decimal(float(position)))

    def GetX(self):
        position = Decimal.ToDouble(self.channelX.GetPosition())
        return position

    def GetY(self):
        position = Decimal.ToDouble(self.channelY.GetPosition())
        return position

    def GetZ(self):
        position = Decimal.ToDouble(self.channelZ.GetPosition())
        return position
    

print("something")
deviceID = "71201654"
Piezo = BPC303Piezo("CloseLoop",deviceID)
Zfocus = 3.88
loops = 1
Piezo.SetZ(Zfocus)
time.sleep(1)
while loops <= 100:
    Piezo.SetX(15)
    time.sleep(5)
    Piezo.SetY(15)
    time.sleep(5)
    Piezo.SetX(0)
    time.sleep(5)
    Piezo.SetY(0)
    time.sleep(5)
    loops = loops + 1
