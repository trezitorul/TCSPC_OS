# Testing Lifetime function with python + quTAG
#
# Author: qutools GmbH
# Last edited: Oct 2020
#
# Tested with python 3.7.3 (32bit), numpy-1.13.3 and Windows 10 (64bit)
#
# This is demo code. Use at your own risk. No warranties.
#
# It may be used and modified with no restriction; raw copies as well as 
# modified versions may be distributed without limitation.

import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np # for a array to set a channel delay 

import QuTAG_MC

# initialize device
qutag = QuTAG_MC.QuTAG()

# define channels
ch_start = 1
ch_stop = 2

# define lifetime histogram
binwidth = 1
bincount = 10000


# Set the new channel delay at channel 'ch_start'
channelDelay = 1 # ps
qutag.setChannelDelay(ch_start, channelDelay)
qutag.setChannelDelay(ch_stop, channelDelay)


# enable lifetime
print("Enable lifetime: ", qutag.enableLFT(True))

# liftetime start input
qutag.setLFTStartInput(ch_start) 

# set the parameters for the lifetime histigram
qutag.setLFTParams(binwidth, bincount)

# add the histogram with the desired stop channel and the before defined start input
qutag.addLFTHistogram(ch_stop,True)


# create function
lftfunction = qutag.createLFTFunction()


params = qutag.getLFTParams()
print("params: ", params)

# get the lifetime histogram
histo  = qutag.getLFTHistogram(ch_stop,True,lftfunction)
# Lifetime function lftfunction == histo[0]
print("Number of time diffs that were bigger than the biggest histogram bin: ", histo[1])
print("Number of start events contributing to the histogram: ", histo[2])
print("Number of stop events contributing to the histogram: ", histo[3])
print("Exposure time - the time difference between the first and last event that contribute to the histogram: ", histo[4])

# let's have a look at the histogram by the analyse function. It disassembles a function description object to its components. The object itself stays valid. May be useful for non-C/C++ programmers, e.g. here in Python.
# for more information, see: https://qutools.com/files/quTAG/documentation/tdclifetm_8h.html#a3e032338d4f6ccf6fba683258e18d601
analyse = qutag.analyseLFTFunction(lftfunction)
print("Analyse - array size of values: ", analyse[0])
print("Analyse - number of valid items in values: ", analyse[1])
print("Analyse - size of a t step in TDC time units: ", analyse[2])
print("Analyse - array of function values: ", analyse[3])

qutag.deInitialize()


# Plotting with mathplotlib
style.use('fivethirtyeight')
fig = plt.figure()
fig.set_size_inches(10,7)
ax1 = fig.add_subplot(1,1,1)
plt.cla() # clear old plotting data
# plot the datapoints
plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
plt.plot(analyse[3])
ax1.set_title('quTAG Lifetime')		
plt.pause(0.05)
