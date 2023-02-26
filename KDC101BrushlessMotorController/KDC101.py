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
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.ControlParameters")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.AdvancedMotor")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.KCubeMotor")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.Settings")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.DCServoCLI")
clr.AddReference("System.Collections")
clr.AddReference("System.Linq")
clr.AddReference('System')

from System import Decimal
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI 
from Thorlabs.MotionControl.GenericMotorCLI import GenericMotorCLI
from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import ControlParameters
from Thorlabs.MotionControl.GenericMotorCLI.AdvancedMotor import AdvancedMotor
from Thorlabs.MotionControl.GenericMotorCLI.KCubeMotor import KcubeMotor
from Thorlabs.MotionControl.GenericMotorCLI.Settings import Settings
from Thorlabs.MotionControl.KCube.DCServoCLI import DCServoCLI


logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def Setup_Device(deviceID):
    DeviceManagerCLI.BuildDeviceList()
    device =  BenchtopPiezo.CreateBenchtopPiezo(deviceID)
    device.Connect(deviceID)
    return device

if __name__ == "__main__":
    print("...")  