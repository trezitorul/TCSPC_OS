from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import ULRange
from mcculw.ul import ULError
import time
import matplotlib.pyplot as plt
import numpy as np
import re
board_num = 0
channel_out = 3
channel_in = 3
ai_range = ULRange.BIP10VOLTS
ul.a_input_mode(board_num, 1)
eng_value_list = []
x_axis = []
outVal=0
s=1
ms=0.001
hz=1
f=10*hz 
p=1/f
ns=1e-9*s
tArray=[]
try:
    device_info = DaqDeviceInfo(board_num)
    print("unique_id", device_info.product_name)
    print(re.findall(r'\d+',str(ai_range)))
    t=0
    for i in range(int(1e4)):
        tstart=time.perf_counter()
        tArray.append(t)
        voltage= 12*np.sin(((2*np.pi)/p)*t)
        voltVal=ul.from_eng_units(board_num, ai_range, voltage)
        value_out = ul.a_out(board_num, channel_out, ai_range,voltVal)
        x_axis.append(i)
        t = (time.perf_counter() - tstart) + t
        value_in = ul.a_in(board_num, channel_in, ai_range)
        eng_units_value_in = ul.to_eng_units(board_num, ai_range, value_in)
        eng_value_list.append(eng_units_value_in)
    plt.plot(tArray,eng_value_list, marker="+")
    plt.show()
except ULError as e:
    print("A UL error occurred. Code: " + str(e.errorcode)
          + " Message: " + e.message)