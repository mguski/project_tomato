#!/usr/bin/env python
import time
import serial
import RPi.GPIO as GPIO
import private_data

# SIM900 power up GPIO
sim900_power_gpio = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(sim900_power_gpio, GPIO.OUT)
GPIO.output(sim900_power_gpio, GPIO.LOW)

url_main = 'https://emoncms.org/input/post?node=Node1&apikey=' + private_data.APIKEY




class SIM900:
    def __init__(self):
        # configure the serial connections (the parameters differs on the device you are connecting to)
        self.serial = serial.Serial(
                port='/dev/ttyAMA0',
                baudrate=19200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1 )
        self.serial.isOpen()
        self.send_command('ATE0')


    def send_command(self, command, nResponses=1):
        self.serial.write(command + '\r\n')
        response_list = []

        for iResponse in range(nResponses):
            # print('  wait for response {} / {}'.format(iResponse +1, nResponses))
            wait_counter = 0
            while (self.serial.inWaiting() == 0 ) & (wait_counter < 50):
               # print('.')
                time.sleep(0.1)
                wait_counter += 1

            
            out = ''
            while self.serial.inWaiting() > 0:
                out += self.serial.read(1)
                if self.serial.inWaiting <= 0:
                   time.sleep(0.1)
            total_length = len(out)
            out = out[2:-2]
            print("   command: {} >> {} (length {})".format(command, out, total_length))
            response_list.append(out)

        if nResponses == 1:
            return_var = response_list[0]
        else:
            return_var = response_list


        return return_var

    def isOn(self):
        response = self.send_command('AT')
    #    print("resp: {}, length: {}".format(response,  len(response)))
    #    for i in range(len(response)):
    #        print("  + {} {}".format(response[i], ord(response[i])))
        return 'OK' in response

    def power_down_at(self):
        self.send_command('AT+CPOWD=1')
        time.sleep(2)
        out = ''
        while self.serial.inWaiting() > 0:
            out += self.serial.read(1)
        print(out)
        

    def power_on(self):
        print('Check is GSM module is on....')
        if  self.isOn():
            print(' GSM already active')
        else:
            print(' GSM off\n  Triggering wake up....')
            GPIO.output(sim900_power_gpio, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(sim900_power_gpio, GPIO.LOW)
            time.sleep(4)
            print('  Triggered wake up.')
            
            # receive default wake up sequence
            out = ''
            while self.serial.inWaiting() > 0:
                out += self.serial.read(1)

            # check again
            if  self.isOn():
                self.send_command('ATE0')
                print(' GSM now active')
            else:
                print(' GSM still off')


    def activate_gprs(self):
        if not self.isOn():
            print('Error: SIM900 is not active! Cancel gprs connection')
            return False

        self.send_command('AT+SAPBR=3,1,"Contype","GPRS"')
        self.send_command('AT+SAPBR=3,1,"APN","internet"')
        time.sleep(15)  
        self.send_command('AT+SAPBR=1,1')
        self.send_command('AT+SAPBR=2,1')
        return True

    def deactivate_gprs(self):
        self.send_command('AT+SAPBR=0,1')

    def http(self, url):
        self.send_command('AT+HTTPINIT')
        self.send_command('AT+HTTPSSL=1')
        self.send_command('AT+HTTPPARA="CID",1')
        self.send_command('AT+HTTPPARA="URL","{:s}"'.format(url))
        response = self.send_command('AT+HTTPACTION=0', nResponses=2)

        print(response)
        resp_split = response[1].split(',')
        if (len(resp_split) > 1) and (resp_split[1] == '200'):
            print('http get worked')
        else:
            print('http get did not work: {}'.format(response[1]))
            self.send_command('AT+HTTPTER')
            return False


        response = self.send_command('AT+HTTPREAD')
        self.send_command('AT+HTTPTER')
        print('HTTPDATA:  ' + response)
        if 'OK' in response:
            ret_val = True
        else:
            ret_val = False

        return ret_val


    def post_data(self, temperature, humidity):
        url_data = '&fulljson={{%22Temperatur%22:{:2.1f},%22Luftfeuchtigkeit%22:{:2.1f}}}'.format(temperature,humidity)
        url = url_main + url_data 
        
        self.http(url)

    def sleep(self):
        print('Going to sleep mode...')
        self.send_command('AT+CSCLK=2')
        time.sleep(5)
        print('SIM900 sleeping.')


    def wake_up(self):
        print('Waking up...')
        self.send_command('AT+CSCLK=0')
        time.sleep(0.01)
        self.send_command('AT+CSCLK=0')
        print('SIM900 awake.')


    def tcp_init(self):
        self.send_command('AT+CSTT="internet"')
        self.send_command('AT+CIICR')
        self.send_command('AT+CIFSR')

    def tcp_check_port(self):
        command = 'AT+CIPSTART="TCP","{}","{}"'.format(private_data.DYNDNS_URL, private_data.REV_SSH_PORT)
        print(command)
        response = self.send_command(command, 3)
        
        if response[1] == 'CONNECT OK':
            self.send_command('AT+CIPCLOSE')
            return True
        else:
            return False




if __name__ == '__main__':
    sim = SIM900()
    sim.power_on()
    print(sim.isOn())
    
    sim.activate_gprs()
    sim.post_data(31.2)
    sim.deactivate_gprs()
    
    
    
    
    
    ser = sim.serial
    
    print('Enter your commands below.\r\nInsert "exit" to leave the application.')
    
    input=1
    while 1 :
       # get keyboard input
       input = raw_input(">> ")
       # Python 3 users
       # input = input(">> ")
       if input == 'exit':
           ser.close()
           exit()
       else:
           # send the character to the device
           # (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
           ser.write(input + '\r\n')
           out = ''
           # let's wait one second before reading output (let's give device time to answer)
           time.sleep(1)
           while ser.inWaiting() > 0:
               out += ser.read(1)
           if out != '':
               print(">>" + out)
    


