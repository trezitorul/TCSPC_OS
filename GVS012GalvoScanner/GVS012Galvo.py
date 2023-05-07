import os
import sys
from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import ULRange
from mcculw.ul import ULError
import time
import matplotlib.pyplot as plt
import numpy as np
import math
from pylab import *
class GVS012Galvo:
    def __init__(self,range,mode):
        '''
        Initialize the Stage 
        '''
        self.um=1
        self.nm=(self.um/1000)
        self.board_num = 0
        self.range = range
        self.LUT = []
        self.mode = mode
        self.setMode(mode)
        self.counterchannel = 0 #detecting either there is single photon (1) or not(0)
        self.thetaHigh=0
        self.thetaLow=1
        self.phiHigh=2
        self.phiLow=3
        self.VToA=10 #Volts per Optical Scan Angle (1/2 * 0.5 V per Mechanical Angle, Optical Scan Angle is 2X Mechanical Scan Angle)
        self.projectionDistance=10.63*self.um #1/tan(31) used for development only, corresponds to max displacement of the X axis at theta=31 degrees. Units can be chosen arbitrarily for now as um
    
    def setMode(self,mode):
        '''
        Set the DAQ card to either "differential" or "single_ended"
        '''
        if mode == "differential":
            ul.a_input_mode(self.board_num, 0)
            self.mode = mode
            return 
        elif mode == "single_ended":
            ul.a_input_mode(self.board_num, 1)
            self.mode = mode
            return 
        else:
            print("error, please use either differential or single_ended")
            return "null"
    
    def getVoltage(self,channel_in):
        '''
        Return analog input channel's voltage
        '''
        value_in = ul.a_in(self.board_num, channel_in, self.range)
        voltage = ul.to_eng_units(self.board_num, self.range, value_in)
        return voltage
    def setVoltage(self,channel_out,voltage):
        '''
        Set the analog output channel's voltage
        '''
        voltage_pk = 10
        if abs(voltage) > abs(voltage_pk):
            print("invalid voltage on" + str(channel_out)+" of " + str(voltage) + "please reenter correct voltage")
            return
        else:
            print(voltage)
            voltVal=ul.from_eng_units(self.board_num, self.range, voltage)
            value_out = ul.a_out(self.board_num, channel_out, self.range,voltVal)
            return

    def setDiffVoltage(self,channel_high, channel_low,voltage):
        '''
        Set the analog output differential voltage between 2 channel
        '''
        voltage_pk = 20
        if abs(voltage) > abs(voltage_pk):
            print("invalid voltage please reenter correct voltage")
            return
        else:
            differential_voltage = voltage * 1/2
            voltValHigh=ul.from_eng_units(self.board_num, self.range, differential_voltage)
            voltValLow=ul.from_eng_units(self.board_num, self.range, -1 * differential_voltage)
            value_high = ul.a_out(self.board_num, channel_high, self.range,voltValHigh)
            value_low = ul.a_out(self.board_num, channel_low, self.range,voltValLow)
            return 
    
    def getDiffVoltage(self,channel_high,channel_low):
        '''
        Return differential voltage between 2 channels
        '''
        mode = self.mode
        if mode == "single_ended":
            return self.getVoltage(channel_high) - self.getVoltage(channel_low)
        elif mode == "differential": 
            if channel_low == channel_high + 1 and channel_high % 2 == 0:
                return self.getVoltage(channel_high // 2)
            else:
                print("please use correct channels, refer to manual to connect to correct pin in differential mode")
                return "null"
        else:
            print("please use correct mode, single_ended or differential")
            return "null"

    def setThetaAngle(self, theta):
        '''
        Set optical angle in respect to X axis
        '''
        V_theta=self.VToA*theta
        self.setDiffVoltage(self.thetaHigh,self.thetaLow, V_theta)
        return 

    def setPhiAngle(self, phi):
        '''
        Set optical angle in respect to Y axis
        '''
        V_phi=self.VToA*phi
        self.setDiffVoltage(self.phiHigh,self.phiLow, V_phi)
        return 

    def setX(self, X):
        '''
        Set horizontal positon of laser
        '''
        theta=math.degrees(np.arctan(X/self.projectionDistance))
        self.setThetaAngle(theta)
        return
    def setY(self, Y):
        '''
        Set vertical position of laser
        '''
        phi=math.degrees(np.arctan(Y/self.projectionDistance))
        self.setPhiAngle(phi)
        return
    
    def getThetaAngle(self):
        '''
        Return optical angle in respect to X axis
        '''
        Xvolt = self.getDiffVoltage(self.thetaHigh,self.thetaLow)
        theta = Xvolt / self.VToA
        return theta
    
    def getX(self):
        '''
        Return horizontal positon of laser
        '''
        theta = self.getThetaAngle()
        X_position = math.tan(math.radians(theta)) * self.projectionDistance
        return X_position
    
    def getPhiAngle(self):
        '''
        Return optical angle in respect to Y axis
        '''
        Yvolt = self.getDiffVoltage(self.phiHigh,self.phiLow)
        phi = Yvolt / self.VToA
        return phi
    
    def getY(self):
        '''
        Return vertical position of laser
        '''
        phi = self.getPhiAngle()
        Y_position = math.tan(math.radians(phi)) * self.projectionDistance
        return Y_position
    
    def setZero(self):
        '''
        Reset Galvo config
        '''
        for i in range(4):
            self.setVoltage(i,0)
        ul.release_daq_device(self.board_num)
        return
    
    def getCounts(self,dt):
        '''
        Implementing electrical pulse countings on the Daq cards
        '''
        daq_dev_info = DaqDeviceInfo(self.board_num)
        ctr_info = daq_dev_info.get_ctr_info()
        if self.counterchannel != ctr_info.chan_info[0].channel_num:
            print("wrong channel")
            return "null"
        else:
            ul.c_clear(self.board_num, self.counterchannel)
            t=0
            while t <= dt:
                tstart= time.perf_counter()
                counts = ul.c_in_32(self.board_num, self.counterchannel)
                t = (time.perf_counter() - tstart) + t
            return counts
    
    def rasterscan(self,intergration_t,dx,dy,n,spanx,spany, setx, sety):
        data1 = 0
        counts = []
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
                self.setX(x)
                self.setY(y)
                x=self.getX()
                y=self.getY()
                c=self.getCounts(intergration_t)
            else:
                return -1000, -1000, -1000
        return x, y, c
    
if __name__ == "__main__":
    '''
    test motor with read and write operations
    '''
    galvo = GVS012Galvo(ULRange.BIP10VOLTS,"single_ended")
    vArray = []
    outVal=0
    s=1
    ms=0.001
    hz=1
    f=1*hz 
    p=1/f
    ns=1e-9*s
    tArray=[]
    channel_X_high = [0,0] #[out channel, in channel]
    channel_X_low = [1,1]
    channel_Y_high = [2,2]
    channel_Y_low = [3,3]
    t = 0
    vArrayX =[]
    vArrayY = []
    vArrayX1 =[]
    vArrayY1 = []
    cArrayX=[]
    cArrayY=[]
    cArrayX1=[]
    cArrayY1=[]
    A=5# Volts
    try:
        device_info = DaqDeviceInfo(galvo.board_num)
        print("unique_id", device_info.product_name)
        print(galvo.mode)
        galvo.setMode("differential")
        print(galvo.mode)
        for i in range(int(1e3)):
            tstart=time.perf_counter()
            tArray.append(t)
            voltageX = A * np.sin(((2*np.pi)/p)*t)
            voltageY = A * np.sin(((2*np.pi)/p)*t + np.pi/2)
            galvo.setDiffVoltage(channel_Y_high[0],channel_Y_low[0], voltageY)
            galvo.setDiffVoltage(channel_X_high[0],channel_X_low[0], voltageX)
            Voltage_outY = galvo.getDiffVoltage(channel_Y_high[1],channel_Y_low[1])
            Voltage_outX = galvo.getDiffVoltage(channel_X_high[1],channel_X_low[1])
            cArrayX.append(voltageX)
            cArrayY.append(voltageY)
            vArrayX.append(Voltage_outX)
            vArrayY.append(Voltage_outY)
            t = (time.perf_counter() - tstart) + t
        plt.plot(tArray, vArrayX, marker='+',c ='b', label="X")
        plt.plot(tArray, vArrayY, marker ='+',c ='r', label="Y")
        plt.plot(tArray, cArrayX,c ='b')
        plt.plot(tArray, cArrayY,c ='r')
        plt.legend()
        plt.show()
        galvo.setZero()
    except ULError as e:
        print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)