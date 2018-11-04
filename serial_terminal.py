#!/usr/bin/env python
import time
import serial


url = 'https://emoncms.org/input/post?node=Node1&fulljson='
apikey = '&apikey=eb6ae6f0bd875b7b0ddf01e18e89f9ae'
data = '{"Temperatur":100}'

ser = serial.Serial(
         port='/dev/ttyAMA0',
         baudrate = 19200,
         parity=serial.PARITY_NONE,
         stopbits=serial.STOPBITS_ONE,
         bytesize=serial.EIGHTBITS,
         timeout=1
              )
counter=0

ser.write('AT/r')
while 1:
     x=ser.readline()
     print x
