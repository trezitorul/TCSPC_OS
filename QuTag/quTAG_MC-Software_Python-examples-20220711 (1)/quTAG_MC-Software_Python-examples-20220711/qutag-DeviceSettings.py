# Example for using the Coincidence Counters with python + quTAG
#
# Author: qutools GmbH
# Last edited: Sep 2019
#
# Tested with python 3.7.3 (32bit), Windows 7 (64bit)
#
# This is demo code. Use at your own risk. No warranties.
#
# It may be used and modified with no restriction; raw copies as well as 
# modified versions may be distributed without limitation.


# This code shows different device settings and their usage. For additional information see the documentation of TDCBase.


try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path / same folder.")

import numpy as np
import time


# Initialize device
qutag = QuTAG_MC.QuTAG()

# Get the timebase (the resolution) from the quTAG. It is used as time unit by many other functions.
timebase = qutag.getTimebase()
print("Device timebase:", timebase, "s")

time.sleep(1)
data,updates = qutag.getCoincCounters()
print("Updates since last call: ", updates, "| Data: ", data)



# Read back device parameters: coincidence window in bins (bin width is timebase) and exposuretime in ms
na, coincWin, expTime = qutag.getDeviceParams()
print("Coincidence window",coincWin, "bins, exposure time",expTime, "ms")



# Define the coincidence window	in bins of the timebase
qutag.setCoincidenceWindow(20000) # with the timebase 1e-12s -> coincidence window is set to 20ns

# Set the exposure or integration time in milliseconds, range = 0..65535
qutag.setExposureTime(100) # 500ms Counting

# Enable Start channel and Stop channels
# Selects the channels that contribute to the timestamp output stream.
# First bool argument enables/disables the start channel by True/False.
# Second argument enables stop channels by a bitmask. E.g: 10011 enables sStop channels 1, 2 and 5. If econd argument is missing, all channels are activated.
qutag.enableChannels(True) # Enables start channel and all stop channels
qutag.enableChannels(True, 11101001) # Disables start channel and enables only stop channels 1, 4, 6, 7, 8 - all other stop channels are disabled

time.sleep(1)

# See which channels are activated
rc = qutag.getChannelsEnabled()
print("getChannelsEnabled: ", rc)



time.sleep(1)

# Retrieve countrates and coincidence rates
data,updates = qutag.getCoincCounters()
print("data: ", data)



# Set Channel Delay Times.
# Different signal runtimes cause relative delay times of the signals at different channels. The function allows to configure a delay per channel that will be compensated including the changed sorting of events. If not set, all delays are 0. The compensation is carried out in hardware.
# Change the delay from channel 1 to 100ps, the start channel number is 0
print("Set a channel delay on channel 1: ")
qutag.setChannelDelay(1, 100)

# Let's check the channel delay on channel 1
rc = qutag.getChannelDelay(1)
print("Channel delay on channel 1: ", rc , " [ps]")



# Let's configure a channel with threshold voltage and rising or faling edge.
# Configure the channel: 2
# Type of signal conditioning
#       LVTTL signals (Trigger at 2V rising edge, termination optional.):       SCOND_LVTTL
#       NIM signals (Trigger at -0.6V falling edge, termination fixed on.):     SCOND_NIM
#       Misc signals (Conditioning on, everything optional.):                   SCOND_MISC
# Rising/falling edge: True/False (rising is default)
# Voltage threshold from -2...3V when signal conditioning is SIGNALCOND_MISC: 1.2V
# For additional information see the documentation of TDCBase.
qutag.setSignalConditioning(2,qutag.SCOND_MISC,False,1.2)
print("Signal Cond.", qutag.getSignalConditioning(2))

# Enable Markers.
# The markers 0-3 are low resolution timestamps triggered over the GPIO port. Marker 4 is a 1ms timer tick.
# If enabled, the markers are included in timestamp protocol files with channel numbers 100-104.
# By default, all markers are activated. The function allows to enable or disable the single marker channels. 
qutag.enableMarkers((1,2))

# Check for data loss.
# Timestamps of events detected by the device can get lost if their rate is too high for the USB interface or if the PC is unable to receive the data in time.
# The TDC recognizes this situation and signals it to the PC (with high priority).
# The function checks if a data loss situation is currently detected or if it has been latched since the last call.
# If you are only interested in the current situation, call the function twice; the first call will delete the latch. 
rc = qutag.getDataLost()
print("Data loss", rc)


# Enable external clock"
qutag.enableExternalClock(True)
# Get status of external clock"
clockState = qutag.getClockState()
print("Clock State: locked ", clockState[0], ", uplink ", clockState[1])


rc = qutag.startCalibration()
# wait a little to get the device started calibrating
time.sleep(.5)

calibState = qutag.getCalibrationState()
print("getCalibrationState", calibState)

while calibState:
	time.sleep(0.1)
	calibState = qutag.getCalibrationState()
	#print("getCalibrationState: ", calibState)
print("CalibrationState done:", calibState)


# Deinitialize the quTAG. This closes the USB connection. If not called, the connection might be still open by Python and still busy - unable to further connect.
qutag.deInitialize()

