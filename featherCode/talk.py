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

# create analog in to read battery voltage
D9 = AnalogIn(board.D9)

# wind directon
A5 = AnalogIn(board.A5)

# wind direction dictionary
wDir = {
    'N':50000,
    'NNE':26000,
    'NE':29000,
    'ENE':5500,
    'E':6000,
    'ESE':4000,
    'SE':12000,
    'SSE':8000,
    'S':18000,
    'SSW':16000,
    'SW':40000,
    'WSW':38500,
    'W':60000,
    'WNW':53000,
    'NW':56300,
    'NNW':45000
}

def getWindDir():
    '''
    Reads wind vane analog input counts
    '''
    minDist=100000
    curDir = A5.value
    for direction in wDir:
        # compute the counts away from each distance
        dist = abs(curDir-wDir[direction])
        if dist < minDist:
            minDist = dist
            bestDirection = direction
   
    return bestDirection

def getWindSpeed():
    '''
    Polls anemometer for current wind speed
    '''
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
    windSpeed = round(count*1.492 / window,0)
    
    return windSpeed

def getVoltage(pin):
    return round((pin.value*2)*3.3/65536,1)

while True:

    gc.collect()
    # Wait for confirmation from listener
    packet = rfm9x.receive(timeout=3.0)

    # get wind speed
    windSpeed = getWindSpeed()
        
    # get wind direction
    windDir = getWindDir()

    # gather environmental data from sensor
    temp = round(envSensor.temperature*9/5+32,1)
    humidity = round(envSensor.humidity,0)
    pressure = round(envSensor.pressure,1)

    battV = getVoltage(D9)

    packetText = str(f"ZX{temp},{humidity},{pressure},{windSpeed},'{windDir}',{battV}QV", "ascii")
    print(packetText)
    print(f'wind speed {windSpeed}')
    print(f'wind dir {windDir}')

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
        time.sleep(7)
