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
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.DCServoCLI.dll")
clr.AddReference("System.Collections")
clr.AddReference("System.Linq")
clr.AddReference('System')

from System import Decimal
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI 
from Thorlabs.MotionControl.GenericMotorCLI import GenericMotorCLI
from Thorlabs.MotionControl.KCube.DCServoCLI import KCubeDCServo

"Move the kcube to 90 degree and then to 180"
deviceID = "27262347"
DeviceManagerCLI.BuildDeviceList()
device =  KCubeDCServo.CreateKCubeDCServo(str(deviceID))
device.Connect(deviceID)
device.StartPolling(1)
time.sleep(0.25)
device.EnableDevice()
time.sleep(0.25)
config = device.LoadMotorConfiguration(str(deviceID))
config.DeviceSettingsName = "MTS25"
config.UpdateCurrentConfiguration()
device.Home(60000)
velparams = device.GetVelocityParams()
maxvelocity = 100
velparams.MaxVelocity = Decimal(float(maxvelocity))
device.SetVelocityParams(velparams)
for i in [90,180]:
    device.MoveTo(Decimal(float(i)), 60000)
    current_pos = Decimal.ToDouble(device.Position)
    print("current position:",current_pos)
    time.sleep(0.25)
