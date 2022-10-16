# Talk
import board
import busio
import digitalio
import time
import gc
from analogio import AnalogIn
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
rfm9x.tx_power=15

# wind speed counter
D11 = digitalio.DigitalInOut(board.D11)
D11.switch_to_input(pull=digitalio.Pull.UP)

while True:

    gc.collect()
    # Wait for confirmation from listener
    packet = rfm9x.receive(timeout=3.0)
    
    # get wind speed
    curTime, count, lastValue = 0,0,0
    window = 2
    fixedTime = time.monotonic() # millisecond timer
    while curTime < fixedTime+window:
        # if switch closed and was previously open
        if D11.value and not lastValue:
            count+=1
            lastValue=1
            time.sleep(.01) # speed limit and "debounce"
        # if reading the same value twice (when windspeed is low)
        # do not iterate count
        elif D11.value and lastValue:
            pass
        # wait 10ms and update lastValue
        else:
            lastValue=0
            time.sleep(.01)
        curTime = time.monotonic()
        
    # compute wind speed in mph
    windSpeed = round(count*1.492 / window,1)

    # gather environmental data from sensor
    temp = round(envSensor.temperature*9/5+32,1)
    humidity = round(envSensor.humidity,1)
    pressure = round(envSensor.pressure,1)

    packetText = str(f'ZXT:{temp},H:{humidity},P:{pressure}QV', "ascii")
    print(packetText)
    print(f'wind speed {windSpeed}')

    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        print("Sending Weather Data.")
        rfm9x.send(packetText)

    else:
        # Received a packet
        print("Confirmation received.")
        print('Confirmation signal strength: {0} dB'.format(rfm9x.last_rssi))

        # wait to send data again if listener just confirmed receipt of packet
        time.sleep(5)