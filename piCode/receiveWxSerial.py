
import time
import busio
import board
from digitalio import DigitalInOut
import serial
import re
import sqlite3

# set up a serial connection
uart = serial.Serial('/dev/serial0', baudrate=9600,timeout=5)

# set up the local database
con = sqlite3.connect('wx.db')
# create a cursor
cur = con.cursor()
# check if table already exists
if cur.execute('SELECT name FROM sqlite_master WHERE name="wxData"').fetchone() is None:
    print('creating table')
    # create table if it does not exist
    cur.execute('CREATE TABLE wxData(DateTime,Temperature,Humidity,Pressure,WindSpeed,WindDir)')
con.close()

# read in from serial
while True:
    try:
        wxData = uart.read(30)
    except:
        wxData=None
    
    if wxData:
        # decode the bytearray
        data = wxData.decode()
        print(data)
        # check to see if array has necessary components
        checks=['T','H','P']
        if sum([chars in data for chars in checks]) < 3:
            print('missing data')
            time.sleep(.5)
            continue
        
        # clean up data
        data = re.sub('[T:PH]','',data)
        print(data)
        
        # connect to db
        con = sqlite3.connect('wx.db')
        # create a cursor
        cur = con.cursor()        
        # write data to database
        cur.execute(f'''
            INSERT INTO wxData VALUES
                (datetime('now'),{data},'missing','missing')
        ''')
        # commit transaction
        con.commit()
        # close connection
        con.close()
        
        with open('wxData.csv', mode='a') as f:
            f.write(data+'\n')
    
    time.sleep(.5)