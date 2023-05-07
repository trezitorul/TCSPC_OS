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
"Create a Sine Wave on channel X"
deviceID = "71201654"
DeviceManagerCLI.BuildDeviceList()
device =  BenchtopPiezo.CreateBenchtopPiezo(str(deviceID))
device.Connect(deviceID)
channel = device.GetChannel(1)
if not channel.IsSettingsInitialized():
    channel.WaitForSettingsInitialized(10000)  
    assert channel.IsSettingsInitialized() is True
channel.StartPolling(1)
time.sleep(0.2)
channel.EnableDevice()
time.sleep(0.2)
channel.SetPositionControlMode(Piezo.PiezoControlModeTypes.CloseLoop)
initial_position = Decimal(0)
channel.SetPosition(initial_position)
initial_voltage = Decimal(0)
channel.SetOutputVoltage(initial_voltage)
traj = []
pos_vec = []
samples = []
time.sleep(0.25)
for i in range(5e2):
    pos =  np.sin(i)
    channel.SetPosition(Decimal(float(pos)))
    position = Decimal.ToDouble(channel.GetPosition())
    traj.append(pos)
    pos_vec.append(position)
    samples.append(i)
    time.sleep(0.2)

plt.plot(samples,traj)
plt.plot(samples,pos)
plt.show()
