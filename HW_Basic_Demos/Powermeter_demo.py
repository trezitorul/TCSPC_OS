import sys
from matplotlib import pyplot as plt
sys.path.append("C:\\Users\\Ozymandias\\TCSPC_project\\PM16_120PowerMonitor")
from PowerMeter import PowerMeter
meter1 = PowerMeter()
meter1.open(0)
meter1.setMeterWavelength(532)
meter1.setMeterPowerAutoRange(1)
meter1.setMeterPowerUnit(0)
timeArray, measurementArray = meter1.getMeasurements(1000, 0.01)
meter1.close()
plt.plot(timeArray, measurementArray, 'o', color='black')
plt.show()