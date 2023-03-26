from PID_eg import ExecPID
import matplotlib.pyplot as plt

system = ExecPID(5, 0.01, 0.1, sample_time = 0.01)

system.setPIDOutputLimits((-100, 100))

x, y, setpoint = system.runPID(10)

plt.plot(x, y, label='measured', linewidth = 3)
plt.plot(x, setpoint, label='target', linewidth = 0.2)
plt.xlabel('time')
plt.ylabel('value')
plt.legend()
plt.show()