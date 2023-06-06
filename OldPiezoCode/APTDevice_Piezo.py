from thorlabs_apt_device import APTDevice
from thorlabs_apt_device.enums import EndPoint
from thorlabs_apt_device.enums import LEDMode
import thorlabs_apt_device.protocol as apt

import serial.tools.list_ports
import logging
import sys
import threading
import time
class APTDevice_Piezo(APTDevice):
    """
    Initialise and open serial device for the ThorLabs APT controller.

    If the ``serial_port`` parameter is ``None`` (default), then an attempt to detect an APT device
    will be performed.
    The first device found will be initialised.
    If multiple devices are present on the system, then the use of the ``serial_number`` parameter
    will specify a particular device by its serial number.
    This is a `regular expression <https://docs.python.org/3/library/re.html>`_ match, for example
    ``serial_number="83"`` would match devices with serial numbers
    starting with 83, while ``serial_number=".*83$"`` would match devices ending in 83.

    Status updates can be obtained automatically from the device by setting ``status_updates="auto"``,
    which will request the controller to send regular updates, as well as sending the required "keepalive"
    acknowledgement messages to maintain the connection to the controller.
    In this case, ensure the :data:`keepalive_message` property is set correctly for the controller.

    To instead query the device for status updates on a regular basis, set ``status_updates="polled"``,
    in which case ensure the :data:`update_message` property is set correctly for the controller.

    The default setting of ``status_updates="none"`` will mean that no status updates will be
    performed, leaving the task up to sub-classes to implement.

    :param serial_port: Serial port device the device is connected to.
    :param vid: Numerical USB vendor ID to match.
    :param pid: Numerical USB product ID to match.
    :param manufacturer: Regular expression to match to a device manufacturer string.
    :param product: Regular expression to match to a device product string.
    :param serial_number: Regular expression to match to a device serial number.
    :param location: Regular expression to match to a device physical location (eg. USB port).
    :param controller: The destination :class:`EndPoint <thorlabs_apt_device.enums.EndPoint>` for the controller.
    :param bays: Tuple of :class:`EndPoint <thorlabs_apt_device.enums.EndPoint>`\\ (s) for the populated controller bays.
    :param channels: Tuple of indices (1-based) for the controller bay's channels.
    :param status_updates: Set to ``"auto"``, ``"polled"`` or ``"none"``.
    """

    def __init__(self,serial_port=None, deviceID=None, vid=None, pid=None, manufacturer=None, product=None, serial_number=None, location=None, controller=EndPoint.HOST, bays=(EndPoint.USB,), channels=(1,2), status_updates="polling", creation=1):
        #worked = False
        # serial_port="NODEVICE"
        # if deviceID!=None and creation != 0:
        #     print("Attempting to connect")
        #     ports = list(serial.tools.list_ports.comports())
        #     for p in ports:
        #         serial_port="NODEVICE"
        #         if "APT" in p.description:
        #             try:    
        #                 serial_port = p.name
        #                 piezo=APTDevice_Piezo(serial_port=serial_port,status_updates="auto", creation=0)


        #                 if piezo.get_serial()==deviceID:
        #                     print("Connecting to Device " + deviceID + " on Port: " + serial_port)
        #                     worked = True
        #                     # piezo.close()
        #                     # time.sleep(5)
        #                     break
        #                 else:
        #                     piezo.close()
        #                     serial_port="NODEVICE"
        #             except:
        #                 print("Device on Port " + serial_port+" is not availabe!")              
        
        # if serial_port=="NODEVICE":
        #     print("NO DEVICE WITH ID " + deviceID)

        #if not worked and serial_port != "NODEVICE":
        super().__init__(serial_port=serial_port, vid=vid, pid=pid, manufacturer=manufacturer, product=product, serial_number=serial_number, location=location, controller=controller, bays=bays, channels=channels, status_updates=status_updates)
        
        
        #GET TPZ_IOSETTINGS to set max voltage for stage.
        self.keepalive_message=apt.pz_ack_pzstatusupdate
        self.update_message=apt.pz_req_pzstatusupdate
        for bay in self.bays:
            for channel in self.channels:
                self._loop.call_soon_threadsafe(self._write, apt.pz_req_tpz_iosettings(source=EndPoint.HOST, dest=bay, chan_ident=channel))
        
        self.set_ChannelState(channel=0, state=1)
        self.set_ChannelState(channel=1, state=1)
        self.set_zero(channel=0)
        self.set_zero(channel=1)
        self.set_controlMode(channel=0, mode=1)
        self.set_controlMode(channel=1, mode=1)
        self.maxTravel=self.get_maxTravel(channel=0)
        self.get_maxTravel(channel=1)
        
        self.voltage = 0
        self.maxVoltage= 75
        self.mode = 0
        self.state = False
        self.maxTravel = 200
        self.position = 0
        
        self.serial = deviceID
        self.message_event=threading.Event()

        # if deviceID != None:
        #     return piezo

    @classmethod
    def create(cls, deviceID=None, status_updates="polling"):
        #worked = False
        if deviceID!=None:
            print("Attempting to connect")
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                serial_port="NODEVICE"
                if "APT" in p.description:
                    try:    
                        serial_port = p.name
                        piezo=APTDevice_Piezo(serial_port=serial_port,status_updates="auto", creation=0)


                        if piezo.get_serial()==deviceID:
                            print("Connecting to Device " + deviceID + " on Port: " + serial_port)
                            #worked = True
                            # piezo.close()
                            # time.sleep(5)
                            break
                        else:
                            piezo.close()
                            while(piezo._port.is_open):
                                time.sleep(0.1)
                            serial_port="NODEVICE"
                    except:
                        print("Device on Port " + serial_port+" is not availabe!")   
            if serial_port=="NODEVICE":
                print("NO DEVICE WITH ID " + deviceID)
            else:
                return piezo           

    

    def get_ChannelState(self, bay=0, channel=0, timeout=10):
        """
        Get the current channel state. 

        :param now: Get the channel state immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.mod_req_chanenablestate(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        
        self.message_event.wait(timeout=timeout)
        self.message_event.clear()

        return self.state


    def set_ChannelState(self, bay=0, channel=0, state=1):
        """
        Set the channel state. 

        :param state: state of the piezo's state. (1: Enabled; 2: Disabled)
        :param now: Perform state change immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        
        self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.mod_set_chanenablestate(source=EndPoint.HOST, dest=EndPoint.USB, chan_ident=self.channels[channel], enable_state=state))
    


    def set_controlMode(self, bay=0, channel=0, mode=1):
        """
        Set the control Mode. 
        0x01 Open Loop (no feedback)
        0x02 Closed Loop (feedback employed)
        0x03 Open Loop Smooth
        0x04 Closed Loop Smooth

        :param mode: Mode of the piezo
        :param now: Set control mode immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        self._log.debug(f"Set Channel {channel} mode to {mode} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_set_positioncontrolmode(source=EndPoint.HOST, dest=EndPoint.USB, chan_ident=self.channels[channel], mode=mode))
    

    def get_controlMode(self, bay=0, channel=0, timeout=10):
        """
        Get current control mode. 

        :param now: Get current mode immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_req_positioncontrolmode(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        
        self.message_event.wait(timeout=timeout)
        self.message_event.clear()

        return self.mode


    def set_voltage(self, voltage=None, bay=0, channel=0):
        """
        Set the piezo voltage. Must be in Open Loop Mode, and must be manually set to this mode beforehand in the main or it will not work.

        :param voltage: Set current voltage as an integer in the range 
                        from 0 to 32767, correspond to 0-100% of piezo's max voltage.
        :param now: Perform voltage change immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        voltageOut=int(32767*(voltage/self.maxVoltage))
        self._log.debug(f"Sets output voltage {voltage} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_set_outputvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltageOut))

    def get_voltage(self, bay=0, channel=0, timeout=10):
        """
        Get the piezo voltage.

        :param voltage: Get current voltage as an integer in the range 
                        from 0 to 32767, correspond to 0-100% of piezo's max voltage.
        :param now: Get current voltage immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        
        self._log.debug(f"Gets voltage on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

        self.message_event.wait(timeout=timeout)
        self.message_event.clear()
        
        return self.voltage/32767*self.maxVoltage




    def get_maxTravel(self, bay=0, channel=0, timeout=10):
        """
        Get maximum travel distance.

        :param now: Get max travel distance immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        self._log.debug(f"Gets maxTravel on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_req_maxtravel(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        
        self.message_event.wait(timeout=timeout)
        self.message_event.clear()

        return self.maxTravel


    def set_position(self, position=None , bay=0, channel=0):
        """
        Set the position of the piezo.
        ONLY WORKS IN CLOSED LOOP MODE
        Units: microns

        :param position: Output position relative to zero position; sets as an integer in the range 
                         from 0 to 32767, correspond to 0-100% of piezo extension aka maxTravel.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        #max = self.get_maxTravel()
        # Hardcoded distance for piezo
        # TODO: Automate this part
        max=20
        positionOut=int(32767.0*position/max)

        self._log.debug(f"Sets position {position} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_set_outputpos(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel], position=positionOut))
    

    def set_zero(self , bay=0, channel=0):
        """
        Reads current position, and use that as reference for position 0.

        :param now: Sets 0 immediately immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        self._log.debug(f"Zero on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_set_zero(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))


    def get_position(self , bay=0, channel=0, timeout=10):
        """
        Get position of the piezo as an integer in the range from 0 to 32767, correspond 
        to 0-100% of piezo extension aka maxTravel.

        :param now: Get current position immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        self._log.debug(f"Sets position on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputpos(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

        self.message_event.wait(timeout=timeout)
        self.message_event.clear()

        return self.position/32767*self.maxTravel/10
    

    def get_maxvoltage(self , bay=0, channel=0):
        """
        Get max voltage.

        :param position: Movement destination in encoder steps.
        :param now: Perform movement immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """    

        # print("Requesting Max Voltage")
        # print(apt.pz_req_outputmaxvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        # self._log.debug(f"Gets max voltage on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        # self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputmaxvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        return 75


    def get_serial(self, bay=0, timeout=10):
        """
        Get serial number.

        :param bay: Index (0-based) of controller bay to send the command.
        """    
        self._log.debug(f"Gets serial number [bay={self.bays[bay]:#x}.")
        self._loop.call_soon_threadsafe(self._write, apt.hw_req_info(source=EndPoint.HOST, dest=self.bays[bay]))
        
        self.message_event.wait(timeout=timeout)
        self.message_event.clear()

        return str(self.serial)


    def connect_device(self, deviceID):
        """
        Connect to piezo using serial number.

        :param deviceID: device serial number.
        """    
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "APT" in p.description:
                comPort = p.name
                piezo=APTDevice_Piezo(serial_port=comPort,status_updates="auto")
                if piezo.get_serial()==deviceID:
                    return comPort
                else:
                    piezo.close()
        return None


    def set_maxvoltage(self, voltage=None , bay=0, channel=0):
        """
        Set max voltage.

        :param position: Movement destination in encoder steps.
        :param now: Perform movement immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        # max_voltage=75
        # voltageOut=int(32767*(voltage/max_voltage))
        #print("Outputing Voltage")
        self._log.debug(f"Sets output voltage {voltage} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        print(apt.pz_set_outputmaxvolts(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltage))
        self._loop.call_soon_threadsafe(self._write, apt.pz_set_outputmaxvolts(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltage))


    def _process_message(self, m):
        super()._process_message(m)
        
        # Decode bay and channel IDs and check if they match one of ours
        if m.msg in ():
            if m.source == EndPoint.USB:
                # Map USB controller endpoint to first bay
                bay_i = 0
            else:
                # Check if source matches one of our bays
                try:
                    bay_i = self.bays.index(m.source)
                except ValueError:
                    # Ignore message from unknown bay id
                    if not m.source == 0:
                        # Some devices return zero as source of move_completed etc
                        self._log.warn(f"Message {m.msg} has unrecognised source={m.source}.")
                    bay_i = 0
                    #return
            # Check if channel matches one of our channels
            try:
                channel_i = self.channels.index(m.chan_ident)
            except ValueError:
                    # Ignore message from unknown channel id
                    self._log.warn(f"Message {m.msg} has unrecognised channel={m.chan_ident}.")
                    channel_i = 0
                    #return
        if m.msg == "pz_get_outputvolts":
            self.voltage=m.voltage
            self.message_event.set()

        # Act on each message type
        elif m.msg == "pz_get_maxtravel":
            self.maxTravel = m.travel
            self.message_event.set()
            
        elif m.msg == "pz_get_outputpos":
            self.position = m.position
            self.message_event.set()

        elif m.msg=="mod_get_chanenablestate":
            self.state = m.enabled
            self.message_event.set()
            
        elif m.msg=="pz_get_positioncontrolmode":
            self.mode = m.mode
            self.message_event.set()

        elif m.msg=="hw_get_info":
            self.serial = m.serial_number
            self.message_event.set()
            
        else:
            #self._log.debug(f"Received message (unhandled): {m}")
            pass



#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# Auto connect to COM port
# ports = list(serial.tools.list_ports.comports())
# for p in ports:
#     if "APT" in p.description:
#         comPort = p.name
# #31xxxxx is the zaxis
# #0 is xy axes
piezo1=APTDevice_Piezo.create(deviceID="31808608",status_updates="none")
# time.sleep(1)
# piezo1.set_controlMode(mode=2)
# time.sleep(1)
# piezo1.set_position(position=100)
# time.sleep(1)
# print(str(piezo1.get_position()))
#time.sleep(3)
piezo2=APTDevice_Piezo.create(deviceID="0",status_updates="none")
# # piezo1.set_ChannelState(state=1)
# #piezo1.get_serial()
# piezo1.set_ChannelState(state=1, channel=1)
# for i in range(10):
#     for j in range(100):
#         if i%2==0:
#             piezo1.set_voltage(j*70/1000, channel=1)
#             #print(j*70/100)
#         else:
#             piezo1.set_voltage(70-j*70/1000, channel=1)
#             #print(70-j*70/100)
#         print(piezo1.get_voltage())
#         time.sleep(0.1)

#Will not work if sleep is too long or too short
# piezo1.set_voltage(voltage=75)
# time.sleep(1)
# print(piezo1.get_voltage())


# piezo2=APTDevice_Piezo(serial_port="COM8",status_updates="auto")
# piezo2.set_ChannelState(state=1)

# # piezo1.identify(channel=0)

# piezo1.set_controlMode(mode=4)
# piezo2.set_controlMode(mode=4)
# time.sleep(1)
# piezo1.get_controlMode()
# piezo2.get_controlMode()
# piezo1.set_zero(channel=0)
# piezo1.set_zero(channel=1)
# piezo2.set_zero(channel=0)
# piezo2.set_position(10)
# time.sleep(1)
# time.sleep(1)
# piezo1.set_voltage(30)
# time.sleep(10)
# for i in range(10):
#     if i%2==0:
#         piezo1.set_position(position=200)
#     else:
#         piezo1.set_position(position=0)
#     time.sleep(0.5)
#     piezo1.get_position()
#     time.sleep(5)

# for i in range(10):
#     for j in range(100):
#         print("---------------------")
#         if i%2==0:
#             piezo2.set_position(j*200/100, channel=0)
#             print(j*200/100)
#         else:
#             piezo2.set_position(200-j*200/100, channel=0)
#             print(200-j*200/100)
#         time.sleep(0.5)
#         piezo2.get_position()

# piezo1.get_voltage()
# piezo1.set_ChannelState(state=1)
# time.sleep(1)
# piezo1.get_ChannelState()
# time.sleep(2)
# piezo1.set_ChannelState(state=2)
# piezo1.get_ChannelState()
# piezo1.set_maxvoltage(voltage=75)
# piezo1.get_maxvoltage()

# time.sleep(2)

# for i in range(10):
#     for j in range(100):
#         if i%2==0:
#             piezo1.set_voltage(j*70/100, channel=0)
#             print(j*70/100)
#         else:
#             piezo1.set_voltage(70-j*70/100, channel=0)
#             print(70-j*70/100)
#         piezo1.get_voltage()
#         time.sleep(0.1)

# piezo1.set_voltage(voltage=75)
# time.sleep(5)
# piezo1.get_voltage()
# time.sleep(5)
# print(piezo.update_message)
# piezo.set_voltage(50)
