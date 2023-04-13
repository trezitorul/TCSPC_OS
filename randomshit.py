import time
import matplotlib.pyplot as plt
import random
import numpy as np
tPerfArray=[]
t=0
dt=0.001
varDt=random.random()

tSleepArray=[]
t=0
actualT=0
c=0.0001
cVals=[]
for i in range(4):
    if i==0:
        c=0
    if i ==1:
        c=0.0001
    c=c*10
    cVals.append(c)
    tSleepArray.append([])
    tPerfArray.append([])
    t=0
    actualT=0
    while actualT<=0.5:
        tstart=time.perf_counter()
        tPerfArray[-1].append(actualT)
        tSleepArray[-1].append(t)
        t=t+dt
        print(round(t))
        print(actualT)
        varDt=random.random()*c
        time.sleep(varDt)
        time.sleep(dt)

        actualT = (time.perf_counter() - tstart) + actualT

#plt.plot(tPerfArray)
print(tPerfArray)
for i in range(len(tPerfArray)):    
    print(i)
    plt.plot(tPerfArray[i], np.array(tSleepArray[i]))

plt.plot(tPerfArray[0], tPerfArray[0])
plt.yscale("log")
plt.title("perf_counter vs. sleep with variable delays")

for i in range(len(cVals)):
    cVals[i]="rand = [0,"+str(cVals[i])+"]"
cVals.append("reference")
plt.legend(cVals)
plt.xlabel("Actual Time")
plt.ylabel("Log of Time Measured by Sleep")
plt.show()