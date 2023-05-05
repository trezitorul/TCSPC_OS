# Example for using the Coincidence Counters with python + quTAG
#
# Author: qutools GmbH
# Last edited: Sep 2019
#
# Tested with python 3.7 (32bit), numpy-1.13.3 and Windows 7 (64bit)
#
# This is demo code. Use at your own risk. No warranties.
#
# It may be used and modified with no restriction; raw copies as well as 
# modified versions may be distributed without limitation.

# for plotting
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
# for numpy arrays
import numpy as np
# for sleep
import time

# This code shows how to get histograms from a quTAG connected via USB.
# Additionally we are using channel delays to shift the histogram in the plot.

# Import the python wrapper which wraps the DLL functions.
# The wrapper should be in the same directory like this code in the folder.
try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path.")

# initialize device
qutag = QuTAG_MC.QuTAG()

# Choose our start and stop channel
ch_start = 1
ch_stop = 2

bin_width = 1
bin_count = 1000


# Let's add/remove (True/False) a histogram with specified start and stop channels.
# All time differences beween a start and the first following stop event will contribute to the histogram.
# This function also enables the calculation of start stop histograms. When enabled, all incoming events contribute to the histograms.
# When disabled, all corresponding functions are unavailable. The function implicitly clears the histograms.
qutag.addHistogram(ch_start,ch_stop,True)
qutag.addHistogram(ch_stop,ch_start,True)


# Sets parameters for the internally generated start stop histograms: bin width in ps & bin count (range = 2 ... 1000000, default = 10000)
# If the function is not called, default values are in place. When the function is called, all collected histogram data are cleared. 
qutag.setHistogramParams(bin_width,bin_count)
time_array = np.linspace(-bin_width * (bin_count - 1), bin_width * bin_count, 2 * bin_count - 1)
#print("time_array: ",time_array.size)

# plotting with mathplotlib
style.use('fivethirtyeight')
fig = plt.figure()
fig.set_size_inches(10,7)
ax1 = fig.add_subplot(1,1,1)

# Integer variable for the channel delays with zero ps. We are going to shift the delay on channel ch_start in the coming loop.
offset = 1000
channelDelay = offset

# Let's get histograms of the device in a loop with increasing channel delay.
while True:
	# Shift the delay on channel 'ch_start' +20ps each loop by changing the created array
	channelDelay += 10
        
	# Set the new channel delay at channel 'ch_start'
	qutag.setChannelDelay(ch_start, channelDelay)

	if (channelDelay > 1000 + offset):
		# Reset the channel delay for plotting range
		channelDelay = offset

	time.sleep(0.1)
        	
	# Clear histogram data with True to avoid old data at another channel delay
	rc_1 = qutag.getHistogram(ch_start,ch_stop,True)
	rc_2 = qutag.getHistogram(ch_stop,ch_start,True)
        
	
	# wait a second for accumulating data
	time.sleep(0.1)
	# get the histogram of channel ch_start & ch_stop and clear the data
	rc_1 = qutag.getHistogram(ch_start,ch_stop,True)
	rc_2 = qutag.getHistogram(ch_stop,ch_start,True)
	print("Counts inside the histogram: ", rc_1[1], "| Counts too Small: ", rc_1[2], "| Counts too Large: ", rc_1[3], "| max Exposure time: ", rc_1[6]/1000, "ns")
	print("Counts inside the histogram: ", rc_2[1], "| Counts too Small: ", rc_2[2], "| Counts too Large: ", rc_2[3], "| max Exposure time: ", rc_2[6]/1000, "ns")

	rc_1[0][0] = rc_1[0][0] + rc_2[0][0]

	# Now make sure, both arrays - histograms - are put correctly together. 
	data_array = np.append(np.flip(np.delete(rc_2[0],0)),rc_1[0])

	# Plotting...
	plt.cla() # clear old plotting data
	# plot the data
	plt.plot(time_array,data_array)
	ax1.set_title('Time tagger histogram - channel delay ' + str(channelDelay) + ' ps',fontsize=30)
	plt.xlabel(r'$\Delta$ time [ps]',fontsize=28)
	plt.ylabel('Counts [ ]',fontsize=28)
	plt.pause(0.05)


# Disconnects a connected device and stops the internal event loop.
qutag.deInitialize()



