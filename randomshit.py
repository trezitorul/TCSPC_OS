from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
tArray = []
yArray = []
for t in range(100):
    tArray.append(t)
    y = signal.square(2*np.pi*2*t)
    yArray.append(y)
plt.plot(tArray, yArray)
plt.show()