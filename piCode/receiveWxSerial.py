
import time
import busio
import board
from digitalio import DigitalInOut
import serial
import re

# set up a serial connection
uart = serial.Serial('/dev/serial0', baudrate=9600,timeout=5)

# read in from serial
while True:
    wxData = uart.read(30)
    
    if wxData:
        # decode the bytearray
        data = wxData.decode()
        print(data)
        # cleanup
        data = re.sub('[T:PH]','',data)
        print(data)
        with open('wxData.csv', mode='a') as f:
            f.write(data+'\n')

