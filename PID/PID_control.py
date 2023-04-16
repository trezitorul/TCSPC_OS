from PID import PID
import time
import random
import threading
from PowerMeter import PowerMeter
from LAC_control import LAC
from matplotlib import pyplot as plt

class ExecPID:

    def __init__(self, kP, kI, kD, setpoint = 0.5, accuracy = 0.98, sample_time = 0.01):
        self.pid = PID(Kp=kP, Ki=kI, Kd=kD, setpoint=setpoint, sample_time=sample_time)
        self.pid.setpoint = setpoint
        self.accuracy = accuracy
        self.min = 0.15 #default 
        self.max = 0.98 #default
        self.meter1 = PowerMeter()
        self.meter1.open(0)
        self.meter1.setMeterWavelength(532)
        self.meter1.setMeterPowerAutoRange(1)
        self.meter1.setMeterPowerUnit(0)
        self.lac = LAC(retractLimit = self.min, extendLimit = self.max)
        self.value = self.lac.get_feedback()
        self.powerValue = self.meter1.getMeasurement()

        self.stop_flag = threading.Event()
        t = threading.Thread(target=self.runPID)
        t.start()

    def getValue(self):
        return self.value
    
    def setPIDMovementLimits(self, limits):
        self.pid.output_limits = limits

    def setPIDOutputLimits(self, limits):
        self.min = limits[0]
        self.max = limits[1]
    
    def updateLACSetpoint(self, value):
        self.pid.setpoint = value

    def updateAccuracy(self, value):
        self.accuracy = value
    
    def update(self, PID_power, dt):
        if PID_power != 0:
            
            newValue = self.value + 1 * PID_power * dt

            if newValue > self.max:
                newValue = self.max
            elif newValue < self.min:
                newValue = self.min

            self.value = newValue

            self.lac.set_position(newValue)
        
        return self.value
    
    def runPID(self):
        start_time = time.time()
        last_time = start_time
        #last_target = self.pid.setpoint #DEMO PURPOSES ONLY

        # Keep track of values for plotting
        self.setpointArr, self.yArr, self.xArr = [], [], []

        while not self.stop_flag.is_set():
            current_time = time.time()
            dt = current_time - last_time

            self.value = self.lac.get_feedback() #self.update(PID_power, dt)
            PID_power = self.pid(self.value)

            if ((abs(self.value - self.pid.setpoint)) / self.pid.setpoint < (1 - self.accuracy)):
                PID_power = 0

            self.xArr += [current_time - start_time]
            self.yArr += [self.value]
            self.setpointArr += [self.pid.setpoint]

            #last_target += (random.random() - 0.5) / 100 #DEMO (ENTER TARGET VALUE HERE)
            #self.pid.setpoint = last_target #DEMO

            self.update(PID_power, dt)

            last_time = current_time
    
    def close(self):
        self.stop_flag.set()
        self.meter1.close()
        return self.setpointArr, self.xArr, self.yArr
        
