
import time
import busio
import board
from digitalio import DigitalInOut
import serial

# set up a serial connection
uart = serial.Serial('/dev/serial0', baudrate=9600,timeout=5)

# read in from serial
while True:
    wxData = uart.read(25)
    
    if wxData:
        print(wxData.decode())

    


