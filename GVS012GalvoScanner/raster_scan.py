from GVS012Galvo import * 
#from BPC303PiezoController import BPC303PiezoController
from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import ULRange
from mcculw.ul import ULError
import time
import matplotlib.pyplot as plt
import numpy as np
import math
import threading
import signal
import matplotlib.pyplot as plt
import sys

sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\LAC")
sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\MFF101FlipperMirror")
from LAC import LAC
from MFF101FlipperMirror import MFF101FlipperMirror
deviceID = "37005411"
mirror = MFF101FlipperMirror(deviceID)
#mirror.HomeMirror()


#mirror.SetMode("off")
print("Disengaging Camera Assembly")
time.sleep(1)
lac = LAC()
time.sleep(1)
lac.set_position(int(0.7*1023))
time.sleep(10)
piezoid = "71201654"
#piezo = BPC303PiezoController("CloseLoop",piezoid)
galvo = GVS012Galvo(ULRange.BIP10VOLTS,"single_ended")
intergration_t = 0.001 #Controls Integration Time
dx = 0.001 #Step X resolution
dy = 0.001 #Step Y resolution 
spanx = 0.1 #Scan X Width
spany = 0.1 #Scan Y Width
n = 0
tragx, tragy, x_axis, y_axis, counts = [],[],[], [], []
nspanx=math.ceil(spanx/dx)
nspany=math.ceil(spany/dy)
x0=-1*spanx/2
y0=-1*spany/2

totalN=nspanx*nspany
n=1
t_left=0
for i in range(nspanx):
    for j in range(nspany):
        galvo.setX(x0+dx*i)
        galvo.setY(y0+dy*j)
        x=galvo.getX()
        y=galvo.getY()
        c=galvo.getCounts(intergration_t)
        tragx.append(x0+dx*i)
        tragy.append(y0+dy*j)
        x_axis.append(x)
        y_axis.append(y)
        counts.append(c)
        t_left_temp=int((totalN-n)*1.1*intergration_t)
        if t_left_temp!=t_left:
            t_left=t_left_temp
            print(str(int(100*n/totalN))+"% Complete, expected time remaining: " + str(int(t_left))+"S")
        n+=1
galvo.setX(0)
galvo.setY(0)
lac.set_position(int(0.5*1023))
time.sleep(10)
mirror.SetMode("on")
print("Engaging Camera Assembly")
#lac.set_position(int(0.5*1023))
time.sleep(1)
tragx=np.round(tragx, decimals=4)
tragy=np.round(tragy, decimals=4)
plt.scatter(tragx, tragy)
# print(x_axis)
# print(y_axis)
# print(counts)
i,j=np.meshgrid(np.unique(tragx), np.unique(tragy))
counts=np.array(counts)
z=counts.reshape(len(i), len(j))
plt.pcolormesh(i,j, z)
plt.colorbar()
plt.show()