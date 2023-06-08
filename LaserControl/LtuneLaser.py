import serial
import time
#import serial.tools.list_ports

class RGB_Laser:
    """
    RGB Lasersystems implementation, using the company's python integration example.

    :param com_port: com port device is connected to.
    """
    def __init__(self, com_port=None):
        
        # ports = list(serial.tools.list_ports.comports())
        # for p in ports:
        #     if "RGB" in p.description:
        #         com_port = p.name
        
        # Start serial connection
        self.ser = serial.Serial(
                        port = com_port,
                        baudrate = 57600,
                        timeout = 10,            #in seconds
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS
                    )
        
        self.com_port = com_port
        self.enabled = False
        self.power = 0
        
        # Unsure if self.ser works, everything is called with ser.write and wanted to make it accessable
        
        # Initialize laser at connection
        command = 'init\r\n'.encode()
        self.ser.write(bytes(command))

    def laser_enable(self):
        """
        Enables laser. For safety reasons, the laser takes 5 seconds to turn on.
        """
        command = 'O=1\r\n'.encode()
        self.ser.write(bytes(command))
        self.enabled = True

    def laser_disable(self):
        """
        Disables laser.
        """
        command = 'O=0\r\n'.encode()
        self.ser.write(bytes(command))
        self.enabled = False

    def end(self):
        """
        Closes serial connection.
        """
        self.ser.close()
    
    def set_outputPower(self, power):
        """
        Sets output power to inputted value in mW.

        :param: power: power to set laser to in mW.
        """
        if not self.enabled:
            raise ValueError("Laser must be enabled to set output power!")

        command = f'P={power}\r\n'.encode()
        self.ser.write(bytes(command))
        self.power = power
    
    def get_outputPower(self):
        """
        Returns output power in mW.
        """
        return self.power