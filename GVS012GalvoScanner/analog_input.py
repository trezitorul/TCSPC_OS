from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import ULRange
from mcculw.ul import ULError
import time
import matplotlib.pyplot as plt

board_num = 0
channel = 0
ai_range = ULRange.BIP10VOLTS
ul.a_input_mode(board_num, 1)
#ul.a_chan_input_mode(board_num, channel, )
eng_value_list = []
x_axis = []
try:
    print("ai_range:",ai_range)
    device_info = DaqDeviceInfo(board_num)
    print("unique_id", device_info.product_name)
    for i in range(10000):
        #time.sleep(0.2)
        value_in = ul.a_in(board_num, 0, ai_range)
        eng_units_value_in = ul.to_eng_units(board_num, ai_range, value_in)
        eng_value_list.append(eng_units_value_in)
        x_axis.append(i)
        print("Raw Value out: " + str(value_in))
        print("Engineering Value in: " + '{:.3f}'.format(eng_units_value_in))
    plt.plot(x_axis,eng_value_list)
    plt.show()
except ULError as e:
    print("A UL error occurred. Code: " + str(e.errorcode)
          + " Message: " + e.message)