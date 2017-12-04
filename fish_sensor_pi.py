import os
import glob
from time import sleep
import MySQLdb

import webiopi
from webiopi.devices.analog.mcp3x0x import MCP3002
mcp = MCP3002()

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def read_cds():
    ch0 = mcp.analogRead(0)
    return ch0

def mysql_update():
    connector = MySQLdb.connect(
        host="localhost",
        db="nhs60208db",
        user="nhs60208",
        passwd="b19940716",
        charset="utf8"
    )
    cursor = connector.cursor()
    sql = "update param_tbl set param_temp=" + str(read_temp()) + ", param_lum=" + str(read_cds()) +" where param_id=1"
    print(sql)
    cursor.execute(sql)
    #cursor.execute("UPDATE param_tbl SET param_temp=%s param_lum=%s WHERE param_id=%s" ,(templine,"1"))
    connector.commit()
    cursor.close()
    connector.close()

try:
    while True:
        print(read_temp())
        print(read_cds())
        mysql_update()
        sleep(0.5)
        webiopi.sleep(0.5)

except KeyboardInterrupt:
    pass