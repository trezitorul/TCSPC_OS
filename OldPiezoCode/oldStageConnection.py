#import thorlabs_apt_device as apt
from thorlabs_apt_device import APTDevice
from thorlabs_apt_device.enums import EndPoint
from thorlabs_apt_device.enums import LEDMode
import thorlabs_apt_device.protocol as apt
import thorlabs_apt_device.protocol.functions as func
import logging
import sys
#print(apt.devices.aptdevice.list_devices())
#info =apt.devices.aptdevice.list_devices()[-1]
#piezo1=apt.devices.aptdevice.APTDevice(serial_port="COM7")
#piezo2=apt.devies.aptdevice.APTDevice(serial_port="COM8")
#piezo1.identify()
#print(piezo1.channels[0])
#piezo2.identi
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

    def __init__(self, serial_port=None, vid=None, pid=None, manufacturer=None, product=None, serial_number=None, location=None, controller=EndPoint.USB, bays=(EndPoint.USB,), channels=(1,), status_updates="polling"):
        super().__init__(serial_port=serial_port, vid=vid, pid=pid, manufacturer=manufacturer, product=product, serial_number=serial_number, location=location, controller=controller, bays=bays, channels=channels, status_updates=status_updates)
        #GET TPZ_IOSETTINGS to set max voltage for stage.
        self.keepalive_message=apt.pz_ack_pzstatusupdate
        self.update_message=apt.pz_req_pzstatusupdate
        for bay in self.bays:
            for channel in self.channels:
                self._loop.call_soon_threadsafe(self._write, apt.pz_req_tpz_iosettings(source=EndPoint.HOST, dest=bay, chan_ident=channel))


    def set_voltage(self, voltage=None, now=True ,bay=0, channel=0):
        """
        Perform an absolute move.

        :param position: Movement destination in encoder steps.
        :param now: Perform movement immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
        max_voltage=75
        voltageOut=int(32767*(voltage/max_voltage))
        if now == True:
            print("Outputing Voltage")
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
        Get voltage.

        :param position: Movement destination in encoder steps.
        :param now: Perform movement immediately, or wait for subsequent trigger.
        :param bay: Index (0-based) of controller bay to send the command.
        :param channel: Index (0-based) of controller bay channel to send the command.
        """
    

        
        if now == True:
            print("Outputting Voltage")
            self._log.debug(f"Gets voltage on [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            self._loop.call_soon_threadsafe(self._write, apt.pz_req_outputvolts(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel]))
        elif now == False:
            self._log.debug(f"Preparing to set output voltage steps [bay={self.bays[bay]:#x}, channel={self.channels[channel]}].")
            # self._loop.call_soon_threadsafe(self._write, apt.mot_set_moveabsparams(source=EndPoint.USB, dest=self.bays[bay], chan_ident=self.channels[channel], absolute_position=position))
        else:
            # Don't move now, and no position specified...
            pass


            
    def _process_message(self, m):
        #print("hello")
        print(m.msg)
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
        
        # Act on each message type
        if m.msg in ("pz_get_pzstatusupdate", "mot_get_outputvolts", "mot_move_stopped", "mot_move_completed"):
            # DC motor status update message    
            #print(m._asdict())
            print(m.output_voltage)
            #self.status_[bay_i][channel_i].update(m._asdict())

        else:
            #self._log.debug(f"Received message (unhandled): {m}")
            pass

import time
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
piezo1=APTDevice_Piezo(serial_port="COM4",status_updates="auto")
#piezo2=APTDevice_Piezo(serial_port="COM8",status_updates="auto")
print("hello")
piezo1.identify(channel=None)
#time.sleep(1)
#piezo1.set_voltage(voltage=70)
#piezo2.identify(channel=None)
#time.sleep(5)
piezo1.get_voltage()
time.sleep(3)
#print(piezo.update_message)
#piezo.set_voltage(50)