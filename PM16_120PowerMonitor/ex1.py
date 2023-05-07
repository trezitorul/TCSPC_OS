from PowerMeter import PowerMeter
from matplotlib import pyplot as plt

meter1 = PowerMeter()
meter1.open(0)
meter1.setMeterWavelength(532)
meter1.setMeterPowerAutoRange(1)
meter1.setMeterPowerUnit(0)
timeArray, measurementArray = meter1.getMeasurements(1000, 0.01)
meter1.close()

plt.plot(timeArray, measurementArray, 'o', color='black')
plt.show()

