#!/usr/bin/env python

import RPi.GPIO as GPIO

pin = int(17)


GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.LOW)


gpio_status = 0
while 1 :
   # get keyboard input
   input = raw_input(">> ")
   # Python 3 users
   # input = input(">> ")
   if input == 'exit':
       exit()
   else:
       if gpio_status:
           GPIO.output(pin, GPIO.LOW)
           print("GPIO {} LOW".format(pin))
           gpio_status = 0
       else:
           GPIO.output(pin, GPIO.HIGH)
           print("GPIO {} HIGH".format(pin))

           gpio_status = 1


