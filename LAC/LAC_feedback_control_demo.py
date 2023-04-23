from LAC import LAC
import time
import sys
import matplotlib.pyplot as plt
sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\PM16-120PowerMonitor")
from PowerMeter import *

lac = LAC()

meter1 = PowerMeter()
meter1.open(0)
meter1.setMeterWavelength(532)
meter1.setMeterPowerAutoRange(1)
meter1.setMeterPowerUnit(0)
uW=1
W=1E6*uW
delta = 0
setpoint = 1*uW
increment = 0.4
tol = 0*uW
time.sleep(1)
lac.reset()
lac.set_accuracy(value=0)
lac.set_movement_threshold(value=0)
lac.set_proportional_gain(100)
lac.set_derivative_gain(1)
#lac.set_average_rc(value=10)
integral_prior=0
error_prior=0
times=[]
powers=[]
t=0
error_prior=0
Kp=5#2 is Amazing
Ki=0
Kd=0.1
bias=0
cycleTime=0.5
dt=0.1
iteration_time=dt
pwrToMot=2/10
delta=1

'''setPos=int(0.99*1023)
lac.set_position(setPos)
time.sleep(30)
maxPower=meter1.getMeasurement() * W

setPos=int(0.02*1023)
lac.set_position(setPos)
time.sleep(30)
minPower=meter1.getMeasurement() * W
print("PowerVals")
print(maxPower)
print(minPower)
pwrToMot=(0.99-0.02)/(maxPower-minPower)
print(pwrToMot)
print("-------------------------------")'''
#pwrToMot=(0.99-0.02)/(2.95-0.04)
pwrToMot=0.01
setPos=int(0.5*1023)
lac.set_position(setPos)
time.sleep(15)

while t<=60:
    tstart= time.perf_counter()
    iteration_time=dt
    t=t+dt
    times.append(t)
    
    
    powers.append(meter1.getMeasurement() * W)
    error = (setpoint * uW-meter1.getMeasurement() * W )
    integral=integral_prior + error*iteration_time
    derivative=(error-error_prior)/iteration_time
    output = Kp*error + Ki*integral + Kd*derivative + bias
    output=pwrToMot*output
    error_prior = error
    integral_prior=integral
    print("---------")
    print(round(t, 1))
    print(powers[-1])
    print(error)
    print(output)
    print(round(output*1023))
    if abs(error) > tol:
        currPos=lac.get_feedback()
        print(currPos)
        setPos= currPos+ round(output*1023)
        print(setPos)

        if setPos<999 and setPos>20:
            print("setPos")
            setPos=int(setPos)

            lac.set_position(setPos)
        else:
            if setPos>0.99:
                setPos=0.99
            else:
                setPos=0.02
            setPos=int(setPos*1023)
            lac.set_position(setPos)
    else:
        break
    time.sleep(cycleTime)
    dt = (time.perf_counter() - tstart) 
    

    #print("------------------------")
    #print(meter1.getMeasurement() * W)
    #print(delta)
    #print(lac.get_feedback()/1023)
    #print("")
    #time.sleep(iteration_time)

plt.plot(times, powers)
plt.title("Linear Actuated Variable Attenuator (LAVA) Performance")
plt.xlabel("Time (s)")
plt.ylabel("Optical Power (uW)")
plt.show()