import time
import busio
import board
from digitalio import DigitalInOut
import serial
import re
import sqlalchemy
import sshtunnel
import MySQLdb

# read in mysql credentials
with open('./dashboard/mysql.txt') as f:
    mysqlp = f.read()

# read in ssh credentials
with open('./dashboard/sshcreds.txt') as f:
    sshCreds = f.read()

# set up a serial connection
uart = serial.Serial('/dev/serial0', baudrate=9600,timeout=5)

# set up sshtunnel
sshtunnel.SSH_TIMEOUT = 30.0
sshtunnel.TUNNEL_TIMEOUT = 30.0

# read in from serial
while True:
    try:
        wxData = uart.read(35)
    except:
        wxData=None
    
    if wxData:
        # decode the bytearray
        data = wxData.decode()
        print(data)
        # check to see if array has necessary components
        checks=['T','H','P']
        if not (data.startswith('ZX') and data.endswith('QV')):
            print('missing data')
            time.sleep(.5)
            continue
        
        # clean up data
        data = re.sub('[ZXT:PHQV]','',data)
        print(data)
        
        try:
            with sshtunnel.SSHTunnelForwarder(
                ('ssh.pythonanywhere.com'),
                ssh_username='busbykt', ssh_password=f'{sshCreds}',
                remote_bind_address=('busbykt.mysql.pythonanywhere-services.com',3306)
            ) as tunnel:
            
                # connect to remote mysql db
                wxdb = MySQLdb.connect(
                    user='busbykt',
                    passwd=f'{mysqlp}',
                    host='127.0.0.1', port=tunnel.local_bind_port,
                    db='busbykt$wxdb'
                )
                # create a cursor 
                cur = wxdb.cursor()
                # write to database
                cur.execute(f'''
                   INSERT INTO wxData VALUES
                    (NOW(),{data},0,0)
                ''')
                # commit transaction
                wxdb.commit()
                # close
                cur.close()
        except:
            continue
        
    time.sleep(.5)
