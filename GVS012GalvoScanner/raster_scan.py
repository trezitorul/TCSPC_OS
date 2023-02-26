from GVS012Galvo import * 
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

galvo = GVS012Galvo(ULRange.BIP10VOLTS,"single_ended")
intergration_t = 0.001 #Controls Integration Time
dx = 0.002 #Step X resolution
dy = 0.002 #Step Y resolution 
spanx = 0.5 #Scan X Width
spany = 0.5 #Scan Y Width
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