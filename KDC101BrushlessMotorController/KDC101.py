import os
import time
import logging
import sys
import clr
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from ctypes import *

sys.path.append(r"C:\\Program Files\\Thorlabs\\Kinesis")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
#clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.ControlParameters.dll")
#clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.AdvancedMotor.dll")
#clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.KCubeMotor.dll")
#clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.Settings.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.DCServoCLI.dll")
clr.AddReference("System.Collections")
clr.AddReference("System.Linq")
clr.AddReference('System')

from System import Decimal
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI 
from Thorlabs.MotionControl.GenericMotorCLI import GenericMotorCLI
#from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import ControlParameters
#from Thorlabs.MotionControl.GenericMotorCLI.AdvancedMotor import AdvancedMotor
#from Thorlabs.MotionControl.GenericMotorCLI.KCubeMotor import KcubeMotor
#from Thorlabs.MotionControl.GenericMotorCLI.Settings import Settings
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo


logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

class KDC101BrushlessMotorController:
    def __init__(self,deviceID):
        self.device = self.SetupDevice(deviceID)
        self.config = self.SetupStage(deviceID)
    
    def SetupDevice(self,deviceID):
        DeviceManagerCLI.BuildDeviceList()
        device =  KCubeDCServo.CreateKCubeDCServo(str(deviceID))
        device.Connect(deviceID)
        device.StartPolling(1)
        time.sleep(0.25)
        device.EnableDevice()
        time.sleep(0.25)
        return device 
    def SetupStage(self,deviceID):
        config = self.device.LoadMotorConfiguration(str(deviceID))
        config.DeviceSettingsName = "MTS25"
        config.UpdateCurrentConfiguration()
        return config
    def SetPosition(self,position,maxvelocity):
        self.device.Home(60000)
        velparams = self.device.GetVelocityParams()
        velparams.MaxVelocity = Decimal(float(maxvelocity))
        self.device.SetVelocityParams(velparams)
        self.device.MoveTo(Decimal(float(position)), 60000)
        return
    def GetPosition(self):
        pos = Decimal.ToDouble(self.device.Position)
        return pos

deviceID = "27262347"
Motor = KDC101BrushlessMotorController(deviceID)
Motor.SetPosition(180,60)
position = Motor.GetPosition()
print(position)
