import csv

# for plotting
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

import numpy as np



# Example for using the Coincidence Counters with python + quTAG
#
# Author: qutools GmbH
# Last edited: Oct 2019
#
# Tested with python 3.7.3 (32bit), numpy-1.13.3 and Windows 7 (64bit)
#
# This is demo code. Use at your own risk. No warranties.
#
# It may be used and modified with no restriction; raw copies as well as 
# modified versions may be distributed without limitation.

# for sleep
import time

# This code shows how to get timestamps from a quTAG connected via USB and write them into a text file.

# Import the python wrapper which wraps the DLL functions.
# The wrapper should be in the same directory like this code in the folder '..\QUTAG-V1.x.x\userlib\src'.
try:
        import QuTAG_MC
except:
        print("Time Tagger wrapper QuTAG.py is not in the search path.")




filename = r'quTAG_timestamps_1x10MHz2.txt'



# Initialize the quTAG device
qutag = QuTAG_MC.QuTAG()


# The next function starts or stops writing the timestamp values to a file continuously.
# The timestamps written are already corrected by the detector delays, see example 'qutag-GetHistogramLoop-channelDelay-example.py'.
# Timestamps come in base units of 1 ps. The channel numbers start with 0 in binary formats, with 1 in ASCII.
# A channel number of (100 + Marker Number) is associated with marker input events.
# The 104 is a millisecond tick.
# The following file formats are available:
#    ASCII: FILEFORMAT_ASCII - Timestamp values (int base units) and channel numbers as decimal values in two comma separated columns. Channel numbers range from 1 to 8 in this format.
#    binary: FILEFORMAT_BINARY - A binary header of 40 bytes, records of 10 bytes, 8 bytes for the timestamp, 2 for the channel number, stored in little endian (Intel) byte order.
#    compressed: FILEFORMAT_COMPRESSED - A binary header of 40 bytes, records of 40 bits (5 bytes), 37 bits for the timestamp, 3 for the channel number, stored in little endian (Intel) byte order. No marker events and timer ticks are stored.
#    raw: FILEFORMAT_RAW - Like binary, but without header. Provided for backward compatiblity.


# start writing Timestamps from the quTAG
qutag.writeTimestamps(filename,qutag.FILEFORMAT_ASCII)

# Give some time to accumulate data
time.sleep(0.5) # 1 second sleep time

# stop writing Timestamps
qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)


print("Let's have a look into the file " + filename)



# Disconnects a connected device and stops the internal event loop.
qutag.deInitialize()



ch1 = []
ch2 = []

print("loop")

with open(filename, 'r') as f:
    #reader = csv.reader(f,  delimiter=';')
    reader = csv.reader(f)
    for row in reader:
        #print("1: ", row[0])
        #print("2: ", row[1])

        if (int(row[1]) == 1):
            # max of data we should accept
            ch1.append(row[0])


        if (int(row[1]) == 2):
            # max of data we should accept
            ch2.append(row[0])

print("loop done")

delta_ch1 = []
delta_ch2 = []

for x in range(2, len(ch1)-1):
    delta_ch1.append(int(ch1[x+1])-int(ch1[x]))
    #delta_ch2.append(int(ch2[x+1])-int(ch2[x]))




# Plotting with mathplotlib
style.use('fivethirtyeight')
fig = plt.figure()
fig.set_size_inches(10,7)
ax1 = fig.add_subplot(1,1,1)
#plt.cla() # clear old plotting data
# plot the datapoints
plt.plot(delta_ch1)
#plt.plot(delta_ch2)
ax1.set_title('quTAG Histogram')		
plt.pause(0.05)


