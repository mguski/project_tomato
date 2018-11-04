#!/usr/bin/env python
import time
import sys
import serial
import RPi.GPIO as GPIO
import datetime
#import httplib
import SIM900
import ssh_tunnel

sys.path.insert(0, './DHT11_Python')
import dht11

# parameter
measure_interval = 60*5 # seconds
sensor_gpio = 4


# init GPIO
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()

sensor = dht11.DHT11(pin=sensor_gpio)
nTries = 10
nInvalidIntervals = 0


sim = SIM900.SIM900()
sim.power_on()
sim.activate_gprs()


tunnel = ssh_tunnel.SSH_TUNNEL()

while 1:
    # x=s.readline()
    # print("Messung...")
    iTry = 1
    result = sensor.read()
    while (not result.is_valid()) and (iTry < nTries):
        iTry += 1
        print('  DHT11: Error while reading! reading again (try {}/{} )...'.format(iTry, nTries))
        time.sleep(5)
        result = sensor.read()

    if result.is_valid():
     #   data_str = '{{"Temperatur":{:2.1f},"Luftfeuchtigkeit":{:2.1f}}}'.format(result.temperature, result.humidity)
        nInvalidIntervals = 0
        sim.activate_gprs()
        return_value = sim.post_data(result.temperature, result.humidity)
#        if not return_value:
 #           print('first transmit did not work, try again...')
 #           return_value = sim.post_data(result.temperature, result.humidity)
        sim.deactivate_gprs()


    else:
        nInvalidIntervals += 1 
        print('No valid measurment this interval. {}. interval in a row.')

    #   if tunnel.is_available()
    #       os.system('sudo pon o2')
    #       time.sleep(10)
    #       tunnel.open()
    #       os.system('sudo poff o2')

    time.sleep(measure_interval)

