from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport
from time import sleep
from sys import stdout
import time
from mcculw import ul
from mcculw.enums import ULRange
from mcculw.device_info import DaqDeviceInfo
import numpy as np
#try:
#    from console_examples_util import config_first_detected_device
#except ImportError:
#    from .console_examples_util import config_first_detected_device


def getCounts(boardnum,ctr_num,dt):
    daq_dev_info = DaqDeviceInfo(boardnum)
    ctr_info = daq_dev_info.get_ctr_info()
    if ctr_num != ctr_info.chan_info[0].channel_num:
        print("wrong channel")
        ctr_num = ctr_info.chan_info[0].channel_num 
    else:
        ul.c_clear(boardnum, ctr_num)
        countsArray = []
        while t <= dt:
            tstart= time.perf_counter()
            raw_counts = ul.c_in_32(boardnum, ctr_num)
            counts = str(raw_counts).rjust(12)
            countsArray.append(counts)
            print("counts:",counts, "at time:",t)
            time.sleep(0.1)
            t = (time.perf_counter() - tstart) + t
    stdout.flush
    return countsArray

def run_example():
    # By default, the example detects and displays all available devices and
    # selects the first device listed. Use the dev_id_list variable to filter
    # detected devices by device ID (see UL documentation for device IDs).
    # If use_device_detection is set to False, the board_num variable needs to
    # match the desired board number configured with Instacal.
    use_device_detection = True
    dev_id_list = []
    board_num = 0

    try:
        #if use_device_detection:
        #    config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_counters:
            raise Exception('Error: The DAQ device does not support counters')

        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ctr_info = daq_dev_info.get_ctr_info()

        # Use the first counter channel on the board (some boards start channel
        # numbering at 1 instead of 0, the CtrInfo class is used here to find
        # the first one).
        counter_num = ctr_info.chan_info[0].channel_num

        ul.c_clear(board_num, counter_num) #clear existing counts
        print('Please enter CTRL + C to terminate the process\n')
        t=0.0000001
        try:
            
            while True:
                
                #try:
                print("hi")
                tstart=time.perf_counter()
                #generating sine wave
                tArray =[]
                hz=1
                f=10*hz 
                p=1/f
                ai_range = ULRange.BIP10VOLTS

                #for t in range(int(1e4)):
                    
                    #tArray.append(t)
                    #voltage= 12*np.sin(((2*np.pi)/p)*t)
                    #voltVal=ul.from_eng_units(board_num, ai_range, voltage)
                    #value_out = ul.a_out(board_num, 0, ai_range,voltVal)
                    #tArray.append(t)
                    
                # Read and display the data.
                
                counter_value = ul.c_in_32(board_num, counter_num) #read counts
                print("counter Val" +str(counter_value))
                print("time " +str(t))
                print("cps "+str(counter_value/t))
                #stdout.flush()
                sleep(0.1)
                t = (time.perf_counter() - tstart) + t
               # except (ValueError, NameError, SyntaxError):
               #     print(Exception)
                #    break
        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
