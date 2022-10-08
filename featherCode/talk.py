# Talker Code
import board
import busio
import digitalio
import time
import gc
# environmental sensor
import adafruit_bme680
# radio
import adafruit_rfm9x

# environmental sensor i2c
i2c = board.I2C()
envSensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs = digitalio.DigitalInOut(board.RFM9X_CS)
reset = digitalio.DigitalInOut(board.RFM9X_RST)

rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
rfm9x.tx_power=7

while True:

    gc.collect()
    # Wait for confirmation from listener
    packet = rfm9x.receive(timeout=3.0)

    # gather environmental data from sensor
    temp = round(envSensor.temperature*9/5+32,0)
    humidity = round(envSensor.humidity,2)
    pressure = round(envSensor.pressure,2)

    packetText = str(f'T:{temp},H:{humidity},P:{pressure}', "ascii")
    print(packetText)

    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Sending Weather Data.")
        rfm9x.send(packetText)

    else:
        # Received a packet!
        # Print out the raw bytes of the packet:
        # print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        print("Confirmation received.")
        print('Confirmation signal strength: {0} dB'.format(rfm9x.last_rssi))

        # wait to send data again if listener just confirmed receipt of packet
        time.sleep(5)
