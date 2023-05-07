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

'''
Draw a circle on the projection plane with threadings
'''
galvo = GVS012Galvo(ULRange.BIP10VOLTS,"differential")
vArray = []
outVal=0
s=1
ms=0.001
hz=1
f=1*hz 
p=1/f
ns=1e-9*s
tArray=[]
global t
t=0
A = 1 #For development purposes only!!! This needs to be set with the correct projection distances for the final setup in this case this is in cm.
X_trajectory = [0]
Y_trajectory = [0]
X_actualpos = [0]
Y_actualpos = [0]
maxV=0
minV=0
def handle_kb_interrupt(sig, frame):
    stop_event.set()

def makeCircle():
    t=0
    try:
        for i in range(int(1e9)):
            if stop_event.is_set():
                break
            tstart=time.perf_counter()
            tArray.append(t)
            trajX = A * np.sin(((2*np.pi)/p)*t)
            trajY = A * np.sin(((2*np.pi)/p)*t + np.pi/2)
            galvo.setX(trajX)
            galvo.setY(trajY)
            posX = galvo.getX()
            posY = galvo.getY()
            X_trajectory.append(trajX)
            Y_trajectory.append(trajY)
            X_actualpos.append(posX)
            Y_actualpos.append(posY)
            t = (time.perf_counter() - tstart) + t
        galvo.setZero()
    except ULError as e:
        print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)
    return X_trajectory, Y_trajectory, X_actualpos, Y_actualpos

stop_event = threading.Event()
signal.signal(signal.SIGINT, handle_kb_interrupt)
plt.ion()
plt.show()
lastLength=0
for i in range(int(1e10)):
    if i==0:
        t1=threading.Thread(target=makeCircle, args=())
        t1.start()
    else:
        
        print(X_trajectory)
        plt.clf()
        plt.plot(X_actualpos, Y_actualpos)
        plt.plot(X_trajectory, Y_trajectory)
        lastLength=len(X_actualpos)
        plt.draw()
        plt.pause(.001) 
        time.sleep(0.5)
        #p=p+1