from PID_control import ExecPID
import matplotlib.pyplot as plt
import time

system = ExecPID(5, 0.01, 0.1, setpoint = 50, sample_time = 0.01)

system.setPIDMovementLimits((-100, 100)) #max possible movement in either direction
system.setPIDOutputLimits((0.15, 0.98)) #max and min possible output

time.sleep(10)

x, y, setpoint = system.close()

plt.plot(x, y, label='measured', linewidth = 3)
plt.plot(x, setpoint, label='target', linewidth = 0.2)
plt.xlabel('time')
plt.ylabel('value')
plt.legend()
plt.show()

system.close()
