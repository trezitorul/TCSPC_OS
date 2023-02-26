import os
import time
import logging
import sys
import clr
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from ctypes import *
#rom System import Decimal
import decimal
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
        self.deviceID = deviceID
        self.device = self.SetupDevice()
        [self.channelX,self.channelY,self.channelZ] = self.InitializeAllchan()
    
    def SetupDevice(self):
        DeviceManagerCLI.BuildDeviceList()
        device =  BenchtopPiezo.CreateBenchtopPiezo(self.deviceID)
        device.Connect(self.deviceID)
        return device 

    def CreateChannel(self,chan_no):
        channel = self.device.GetChannel(chan_no)
        if not channel.IsSettingsInitialized():
            channel.WaitForSettingsInitialized(10000)  
            assert channel.IsSettingsInitialized() is True
        channel.StartPolling(1)
        time.sleep(0.5)
        channel.EnableDevice()
        time.sleep(0.25)
        return channel 
    
    def SetZero(self,channel):
        initial_position = decimal.Decimal(0)
        channel.SetPosition(initial_position)
        initial_voltage = decimal.Decimal(0)
        channel.SetOutputVoltage(initial_voltage)
        time.sleep(0.5)
    
    def SetMode(self,channel,mode):
        if mode == "CloseLoop":
            mode = Piezo.PiezoControlModeTypes.CloseLoop
        elif mode =="OpenLoop":
            mode = Piezo.PiezoControlModeTypes.OpenLoop   
        channel.SetPositionControlMode(mode)
    
    def InitializeAllchan(self):
        channelX = self.device.CreateChannel(1)
        self.SetMode(channelX,self.mode)
        self.SetZero(channelX)
        channelY = self.device.CreateChannel(2)
        self.SetMode(channelY,self.mode)
        self.SetZero(channelY)
        channelZ = self.device.CreateChannel(3)
        self.SetMode(channelZ,self.mode)
        self.SetZero(channelZ)

        return [channelX,channelY,channelY]

    def SetX(self,position):
        self.channelX.SetPosition(decimal.Decimal(float(position)))
    
    def SetY(self,position):
        self.channelY.SetPosition(decimal.Decimal(float(position)))

    def SetZ(self,position):
        self.channelZ.SetPosition(decimal.Decimal(float(position)))

    def getX(self):
        position = decimal.ToDouble(self.channelX.GetPosition())
        return position

    def getY(self):
        position = decimal.ToDouble(self.channelY.GetPosition())
        return position

    def getZ(self):
        position = decimal.ToDouble(self.channelZ.GetPosition())
        return position
    
if "name" == "__main__":
    deviceID = "71201654"
    Piezo = BPC303Piezo("CloseLoop",deviceID)
    Piezo.SetX(1)
    print(Piezo.GetX())
