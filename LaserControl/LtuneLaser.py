import serial
import time

class RGB_Laser:
    """
    RGB Lasersystems implementation, using the company's python integration example.

    :param com_port: com port device is connected to.
    
    """
    def __init__(self, com_port=None):
        
        self.com_port = com_port
        
        self.ser = serial.Serial(
                        port = com_port,
                        baudrate = 57600,
                        timeout = 10,            #in seconds
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS
                    )
        
        self.enabled = False
        
        # Unsure if self.ser works, everything is called with ser.write and wanted to make it accessable
        
        command = 'init\r\n'.encode() #Initialization command
        self.ser.write(bytes(command)) #Send command

    def laser_enable(self):
        command = 'O=1\r\n'.encode()
        self.ser.write(bytes(command))
        self.enabled = True

    def laser_disable(self):
        command = 'O=0\r\n'.encode()
        self.ser.write(bytes(command))
        self.enabled=False