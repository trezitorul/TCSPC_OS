from pid import PID
import time
import random

class ExecPID:

    def __init__(self, kP, kI, kD, initValue = 0, setpoint = 0, sample_time = 0.01):
        self.value = initValue
        self.pid = PID(Kp=kP, Ki=kI, Kd=kD, setpoint=setpoint, sample_time=sample_time)

    def getValue(self):
        return self.value
    
    def setPIDOutputLimits(self, limits):
        self.pid.output_limits = limits
    
    def update(self, PID_power, dt):
        if PID_power > 0:
            self.value += 1 * PID_power * dt
        else:
            self.value += 1 * PID_power * dt

        return self.value
    
    def runPID(self, time_period):
        start_time = time.time()
        last_time = start_time
        last_target = 0 #DEMO PURPOSES ONLY

        # Keep track of values for plotting
        setpoint, y, x = [], [], []

        while time.time() - start_time < time_period:
            current_time = time.time()
            dt = current_time - last_time

            PID_power = self.pid(self.value)
            self.value = self.update(PID_power, dt)

            x += [current_time - start_time]
            y += [self.value]
            setpoint += [self.pid.setpoint]

            last_target += (random.random() - 0.5) / 100 #DEMO (ENTER TARGET VALUE HERE)
            self.pid.setpoint = last_target #DEMO

            last_time = current_time

        return x, y, setpoint 
        