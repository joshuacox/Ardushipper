#!/usr/bin/env python
import serial
import syslog
from time import sleep

#port = "/dev/ttyUSB1"
port = "/dev/ttyACM0"

ser = serial.Serial(port, 115200, timeout=15)
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)

count = 0

while True:
    rawdata = ser.readline()
    buff1 = "%s" % rawdata.split(b'\0',1)[0]
    data = "%s" % buff1.strip()
    if "3478-ENDTRANSMISSION" in data:
      count+= 1
    if count > 1:
      break
    if count > 0:
        if not data.isspace():
            if len(data) > 0:
                print 'Got:', data
                syslog.syslog(str(data))
        sleep(0.5)
ser.close()
