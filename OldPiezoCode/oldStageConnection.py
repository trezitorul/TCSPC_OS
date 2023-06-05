#import thorlabs_apt_device as apt
from thorlabs_apt_device import APTDevice
from thorlabs_apt_device.enums import EndPoint
from thorlabs_apt_device.enums import LEDMode
import thorlabs_apt_device.protocol as apt

import serial.tools.list_ports
import logging
import sys
import asyncio
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

    def __init__(self, serial_port=None, vid=None, pid=None, manufacturer=None, product=None, serial_number=None, location=None, controller=EndPoint.HOST, bays=(EndPoint.USB,), channels=(1,2), status_updates="polling"):
        super().__init__(serial_port=serial_port, vid=vid, pid=pid, manufacturer=manufacturer, product=product, serial_number=serial_number, location=location, controller=controller, bays=bays, channels=channels, status_updates=status_updates)
        #GET TPZ_IOSETTINGS to set max voltage for stage.
        self.keepalive_message=apt.pz_ack_pzstatusupdate
        self.update_message=apt.pz_req_pzstatusupdate
        for bay in self.bays:
            for channel in self.channels:
                self._loop.call_soon_threadsafe(self._write, apt.pz_req_tpz_iosettings(source=EndPoint.HOST, dest=bay, chan_ident=channel))
        self.voltage = 0
        self.mode = 0
        self.state = False
        self.maxTravel = 0
        self.position = 0
    

    def get_ChannelState(self, now=True, bay=0, channel=0):
        """
        Get the current channel state. 

        :param now: Get the channel state immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        if now == True:
            #print("Outputing Voltage")
            self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            #print(apt.pz_set_outputvolts(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltageOut))
            self._loop.call_soon_threadsafe(self._write, apt.mod_req_chanenablestate(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        else:
            # Don't move now, and no position specified...
            pass
        
        return self.state


    def set_ChannelState(self, now=True, bay=0, channel=0, state=1):
        """
        Set the channel state. 

        :param state: state of the piezo's state. (1: Enabled; 2: Disabled)
        :param now: Perform state change immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        if now == True:
            self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.mod_set_chanenablestate(source=EndPoint.HOST, dest=EndPoint.USB, chan_ident=self.channels[channel], enable_state=state))
        elif now == False and (state is not None):
            self._log.debug(f"Preparing to set state to {state} steps [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.mot_set_moveabsparams(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], absolute_position=position))
        else:
            # Don't move now, and no position specified...
            pass


    def set_controlMode(self, now=True, bay=0, channel=0, mode=1):
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

        print("Set Mode to " + str(mode))
        if now == True:
            self._log.debug(f"Get Channel {channel} mode on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_set_positioncontrolmode(source=EndPoint.HOST, dest=EndPoint.USB, chan_ident=self.channels[channel], mode=mode))
        else:
            # Don't move now, and no position specified...
            pass
    

    def get_controlMode(self, now=True, bay=0, channel=0):
        """
        Get current control mode. 

        :param now: Get current mode immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """

        if now == True:
            self._log.debug(f"Get Channel {channel} state on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_req_positioncontrolmode(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        else:
            pass
        
        return self.mode


    def set_voltage(self, voltage=None, now=True ,bay=0, channel=0):
        """
        Set the piezo voltage.

        :param voltage: Set current voltage as an integer in the range 
                         from 0 to 32767, correspond to 0-100% of piezo's max voltage.
        :param now: Perform voltage change immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        max_voltage=75
        voltageOut=int(32767*(voltage/max_voltage))
        if now == True:
            self._log.debug(f"Sets output voltage {voltage} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_set_outputvolts(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltageOut))
        elif now == False and (voltage is not None):
            self._log.debug(f"Preparing to set output voltage to {voltage} steps [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.mot_set_moveabsparams(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], absolute_position=position))
        else:
            # Don't move now, and no position specified...
            pass


    def get_voltage(self, now=True ,bay=0, channel=0):
        """
        Get the piezo voltage.

        :param voltage: Get current voltage as an integer in the range 
                         from 0 to 32767, correspond to 0-100% of piezo's max voltage.
        :param now: Get current voltage immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        
        if now == True:
            self._log.debug(f"Gets voltage on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
            time.sleep(0.1)

        elif now == False:
            self._log.debug(f"Preparing to set output voltage steps [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
        else:
            # Don't move now, and no voltage specified...
            pass

        return self.voltage


    def get_maxTravel(self, now=True ,bay=0, channel=0):
        """
        Get maximum travel distance.

        :param now: Get max travel distance immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        
        if now == True:
            self._log.debug(f"Gets maxTravel on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_req_maxtravel(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
            time.sleep(0.1)

        else:
            # Don't move now, and no position specified...
            pass

        return self.maxTravel


    def set_position(self, position=None, now=True ,bay=0, channel=0):
        """
        Set the position of the piezo.
        ONLY WORKS IN CLOSED LOOP MODE

        :param position: Output position relative to zero position; sets as an integer in the range 
                         from 0 to 32767, correspond to 0-100% of piezo extension aka maxTravel.
        :param now: Set piezo position immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        #max = self.get_maxTravel()
        # Hardcoded distance for piezo
        # TODO: Automate this part
        max=20
        positionOut=int(32767.0*position/max)

        if now == True:
            self._log.debug(f"Sets position {position} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_set_outputpos(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel], position=positionOut))
        else:
            # Don't move now, and no position specified...
            pass
    

    def set_zero(self, now=True ,bay=0, channel=0):
        """
        Reads current position, and use that as reference for position 0.

        :param now: Sets 0 immediately immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        if now == True:
            self._log.debug(f"Zero on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_set_zero(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        else:
            # Don't move now, and no position specified...
            pass


    def get_position(self, now=True ,bay=0, channel=0):
        """
        Get position of the piezo as an integer in the range from 0 to 32767, correspond 
        to 0-100% of piezo extension aka maxTravel.

        :param now: Get current position immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        if now == True:
            self._log.debug(f"Sets position on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputpos(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
        else:
            # Don't move now, and no position specified...
            pass

        return self.position
    

    def get_maxvoltage(self, now=True ,bay=0, channel=0):
        """
        Get max voltage.

        :param position: Movement destination in encoder steps.
        :param now: Perform movement immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """    

        
        if now == True:
            print("Requesting Max Voltage")
            print(apt.pz_req_outputmaxvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))
            self._log.debug(f"Gets max voltage on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputmaxvolts(source=EndPoint.HOST, dest=self.bays[bay], chan_ident=self.channels[channel]))

        elif now == False:
            self._log.debug(f"Preparing to set output voltage steps [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            # self._loop.call_soon_threadsafe(self._write, apt.mot_set_moveabsparams(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], absolute_position=position))
        else:
            # Don't move now, and no position specified...
            pass

    def set_maxvoltage(self, voltage=None, now=True ,bay=0, channel=0):
        """
        Set max voltage.

        :param position: Movement destination in encoder steps.
        :param now: Perform movement immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        # max_voltage=75
        # voltageOut=int(32767*(voltage/max_voltage))
        if now == True:
            #print("Outputing Voltage")
            self._log.debug(f"Sets output voltage {voltage} on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            print(apt.pz_set_outputmaxvolts(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltage))
            self._loop.call_soon_threadsafe(self._write, apt.pz_set_outputmaxvolts(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], voltage=voltage))
            time.sleep(0.5)
        elif now == False and (voltage is not None):
            self._log.debug(f"Preparing to set output voltage to {voltage} steps [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.mot_set_moveabsparams(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], absolute_position=position))
        else:
            # Don't move now, and no position specified...
            pass
            
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

        # Act on each message type
        elif m.msg == "pz_get_maxtravel":
            self.maxTravel = m.travel
            
        elif m.msg == "pz_get_outputpos":
            self.position = m.position

        elif m.msg=="mod_get_chanenablestate":
            self.state = m.enabled
            
        elif m.msg=="pz_get_positioncontrolmode":
            self.mode = m.mode
            
        else:
            #self._log.debug(f"Received message (unhandled): {m}")
            pass



#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# COM5 for Ozymandias
# Auto connect to COM port
ports = list(serial.tools.list_ports.comports())
for p in ports:
    if "APT" in p.description:
        comPort = p.name

# piezo1=APTDevice_Piezo(serial_port="COM7",status_updates="auto")
# piezo1.set_ChannelState(state=1)

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
