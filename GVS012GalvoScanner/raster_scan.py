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
intergration_t = 0.1
dx = 0.05
dy = 0.05
spanx = 2
spany = 2
n = 0
tragx, tragy, x_axis, y_axis, counts = [],[],[], [], []
nspanx=math.ceil(spanx/dx)
nspany=math.ceil(spany/dy)
x0=-1*spanx/2
y0=-1*spany/2
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
        print(x, y, c)

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