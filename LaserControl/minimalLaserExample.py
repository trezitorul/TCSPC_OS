# -*- codingO=: utf-8 -*-
"""
Created on Sat Jan 2 16:57:54 2021

@author: RGB-Lasersystems
"""

import serial
import time

# set com port the laser registered to
com_port = 'COM5'
# set serial connection setting (see manual)
ser= serial.Serial(
                        port=com_port,
                        baudrate=57600,
                        timeout=10,            #in seconds
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS
                    )

# send initialisation command
print("init")
command = 'init\r\n'.encode()
ser.write(bytes(command))
#time.sleep(5)
# send command to set output power to 1mW
print("5mw")
command = 'P=5\r\n'.encode()
ser.write(bytes(command))
#time.sleep(5)
# send enable command (for safety reasons the laser is turned on after 5 seconds. compare  "21 CFR 1040")
print("enable")
command = 'O=1\r\n'.encode()
ser.write(bytes(command))

# wait for 7 seconds (5 seconds for laser on and 2 seconds emission)
time.sleep(7)

# send command to set output power to 2mW
print("50")
command = 'P=50\r\n'.encode()
ser.write(bytes(command))

# wait for 2 seconds (2 seconds emission)
time.sleep(2)

# send disable command
command = 'O=0\r\n'.encode()
ser.write(bytes(command))

# close serial connection
ser.close()
