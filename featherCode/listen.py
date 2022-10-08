# Listen
import board
import busio
import digitalio
import time
import gc

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs = digitalio.DigitalInOut(board.RFM9X_CS)
reset = digitalio.DigitalInOut(board.RFM9X_RST)

import adafruit_rfm9x
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
rfm9x.tx_power = 10

uart = busio.UART(board.TX, board.RX, baudrate=9600)

while True:
    gc.collect()
    # wait to receive weather data
    packet = rfm9x.receive(timeout=5.0)
    if packet is None:
        print('No data received')
    else:
        packet_text = str(packet, 'ascii')
        print('Received reply: {0}'.format(packet_text))
        print("Received signal strength: {0} dB".format(rfm9x.last_rssi))

        # write data out
        uart.write(packet)

        # tell weather station we received data
        rfm9x.send('Data received')
        time.sleep(3)
