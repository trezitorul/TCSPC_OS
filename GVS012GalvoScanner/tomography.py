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

sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\QuTag\\quTAG_MC-Software_Python-examples-20220711 (1)\\quTAG_MC-Software_Python-examples-20220711")
sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\LAC")
sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\MFF101FlipperMirror")
sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\OldPiezoCode")
from APTDevice_Piezo import APTDevice_Piezo
from LAC import LAC
from MFF101FlipperMirror import MFF101FlipperMirror

piezo1=APTDevice_Piezo(serial_port="COM7",status_updates="auto")
piezo1.set_ChannelState(state=1)
piezo2=APTDevice_Piezo(serial_port="COM8",status_updates="auto")
piezo2.set_ChannelState(state=1)
# piezo1.identify(channel=0)

piezo1.set_controlMode(mode=4)
piezo2.set_controlMode(mode=4)
time.sleep(1)
piezo1.get_controlMode()
piezo2.get_controlMode()
piezo1.set_zero(channel=0)
piezo1.set_zero(channel=1)
piezo2.set_zero(channel=0)
time.sleep(1)

# This code shows how to get event rates and coincidences from a quTAG connected via USB.
# Additionally we are plotting the data "live" with matplotlib.

# Import the python wrapper which wraps the DLL functions.
# The wrapper should be in the same directory like this code in the folder '..\QUTAG-V1.5.0\userlib\src'.
try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path.")


# Initialize the quTAG device
qutag = QuTAG_MC.QuTAG()


# Read back device parameters: coincidence window in bins (bin width corresponds to timebase) and exposuretime in ms
# We use the exposure time for the y-axis in the plot 
na, coincWin, expTime = qutag.getDeviceParams()
print("Coincidence window",coincWin, "bins, exposure time",expTime, "ms")

cameraFlipperID = "37005411"
cameraFlipper = MFF101FlipperMirror(cameraFlipperID)
#mirror.HomeMirror()
beamBlockFlipperID="37005466"
beamBlockFlipper = MFF101FlipperMirror(beamBlockFlipperID)
def getQuTagCounts(channels, exposureTime):
    counts=0
    time.sleep(exposureTime)
    data,updates = qutag.getCoincCounters()
    
    for chan in channels:
        counts+=data[chan]
    return counts

cameraFlipper.SetMode("off")
beamBlockFlipper.SetMode("off")
print("Disengaging Camera Assembly")
time.sleep(1)
lac = LAC()
time.sleep(1)
lac.set_position(int(0.7*1023))
time.sleep(15)
piezoid = "71201654"
#piezo = BPC303PiezoController("CloseLoop",piezoid)
galvo = GVS012Galvo(ULRange.BIP10VOLTS,"single_ended")
intergration_t = 0.0005 #Controls Integration Time
qutag.setExposureTime(int(intergration_t*1000))
dx = 0.0005#Step X resolution
dy = 0.0005 #Step Y resolution 
spanx = 0.1 #Scan X Width
spany = 0.1 #Scan Y Width
n = 0
tragx, tragxv, tragy, tragyv, x_axis, vx_axis, y_axis, vy_axis, counts = [],[],[], [], [],[],[],[],[]
nspanx=math.ceil(spanx/dx)
nspany=math.ceil(spany/dy)
x0=-1*spanx/2
y0=-1*spany/2

totalN=nspanx*nspany
n=1
t_left=0
z_scans=[]
z_heights=[]
for z in range(7000, 10000, 50):
    t_left=0
    n=0
    piezo2.set_position(z/1000)
    time.sleep(5)
    print("Scanning at"+str(z))
    z_heights.append(z)
    tragx, tragxv, tragy, tragyv, x_axis, vx_axis, y_axis, vy_axis, counts = [],[],[], [], [],[],[],[],[]
    for i in range(nspanx):
        for j in range(nspany):
            galvo.setX(x0+dx*i)
            galvo.setY(y0+dy*j)
            x=galvo.getX()
            y=galvo.getY()
            vx=galvo.getDiffVoltage(0,1)
            vy=galvo.getDiffVoltage(2,3)
            c=getQuTagCounts([5,6], intergration_t)
            #c=galvo.getCounts(intergration_t)
            tragx.append(x0+dx*i)
            tragy.append(y0+dy*j)
            x_axis.append(x)
            vx_axis.append(vx)
            y_axis.append(y)
            vy_axis.append(vy)
            counts.append(c)
            t_left_temp=int((totalN-n)*1.1*intergration_t)
            if t_left_temp!=t_left:
                t_left=t_left_temp
                print(str(int(100*n/totalN))+"% Complete, expected time remaining: " + str(int(t_left))+"S")
            n+=1
    i,j=np.meshgrid(np.unique(tragx), np.unique(tragy))
    zscan=counts
    counts=np.array(zscan)
    z=counts.reshape(len(i), len(j))
    plt.close()
    plt.pcolormesh(i,j, z, vmax=50)
    plt.colorbar()
    plt.show(block=False)
    plt.pause(3)
    z_scans.append(counts)
piezo2.set_position(0)
galvo.setX(0)
galvo.setY(0)
lac.set_position(int(0.1*1023))
time.sleep(10)

beamBlockFlipper.SetMode("on")
cameraFlipper.SetMode("on")
print("Engaging Camera Assembly")
lac.set_position(int(0.3*1023))
time.sleep(1)
tragx=np.round(tragx, decimals=4)
tragy=np.round(tragy, decimals=4)
plt.scatter(tragx, tragy)
# print(x_axis)
# print(y_axis)
# print(counts)
i,j=np.meshgrid(np.unique(tragx), np.unique(tragy))
for zscan in z_scans:
    counts=np.array(zscan)
    z=counts.reshape(len(i), len(j))
    plt.pcolormesh(i,j, z, vmax=50)
    plt.colorbar()
    plt.show()
z_scans.append(tragx)
z_scans.append(tragy)
np.save("tomo_6-4-23", z_scans)