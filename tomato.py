#!/usr/bin/env python
import time
import os
import sys
import serial
import RPi.GPIO as GPIO
import datetime
import SIM900
import ssh_tunnel
import Adafruit_DHT

# parameter
measure_interval = 60*5 # seconds

sensor = Adafruit_DHT.DHT22
sensor_gpio = 4
sensor_nTries = 20


# init GPIO
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#GPIO.cleanup()

nInvalidIntervals = 0

def read_sensor():
    isValid = False
    iTry = 0

    while (iTry < sensor_nTries and not isValid):
        if iTry:
            time.sleep(2)
        humidity,temperature = Adafruit_DHT.read_retry(sensor, sensor_gpio)
        isValid = humidity is not None and temperature is not None
        iTry += 1

    print('Measurement: valid={}, {} C {} %rH, try {}'.format(isValid, temperature, humidity, iTry))
    output = {'isValid': isValid, 'temperature':temperature, 'humidity':humidity}

    return output

read_sensor()

def init_sim():
    sim = SIM900.SIM900()
    sim.power_on()
    sim.activate_gprs()
    sim.tcp_init()
    return sim

sim = init_sim()

tunnel = ssh_tunnel.SSH_TUNNEL()

while 1:
    result = read_sensor()

    if result['isValid']:
        nInvalidIntervals = 0
        sim.activate_gprs()
        return_value = sim.post_data(result['temperature'], result['humidity'])
        sim.deactivate_gprs()


    else:
        nInvalidIntervals += 1 
        print('No valid measurment this interval. {}. interval in a row.')


    if sim.tcp_check_port():
        print('Opening PPP connection and reverse SSH tunnel')
        os.system('sudo pon o2')
        sim.serial.close()
        time.sleep(15)
        tunnel.open()
        os.system('sudo poff o2')
        print('tunnel and PPP closing...')
        time.sleep(15)
        sim = init_sim()
    else:
        print('Waiting for {} minutes...'.format(measure_interval/60))
        time.sleep(measure_interval)

