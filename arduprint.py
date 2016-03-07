import serial
import syslog
from datetime import datetime
from time import sleep

#port = "/dev/ttyUSB1"
port = "/dev/ttyACM0"

ser = serial.Serial(port, 115200, timeout=15)
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
ser.write("hello")

count = 11
while True:
    count+= 1
#    print count
    if count > 10:
      ser.write("1")
      count = 1;
    rawdata = ser.readline()
    buff1 = "%s" % rawdata.split(b'\0',1)[0]
    data = "%s" % buff1.strip()
    if "3478-ENDTRANSMISSION" in data:
      break
#    print len(data)
    if not data.isspace():
      if len(data) > 0:
        print time.time(), " Got:", data, "At:", datetime.now()
#    	syslog.syslog(str(data))
        ser.write("1")

    sleep(0.5)
#    print 'not blocked'

ser.close()
