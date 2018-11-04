#!/usr/bin/env python
import socket
import private_data as pd
import os

class SSH_TUNNEL:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def is_available(self):
        result = self.sock.connect_ex((pd.DYNDNS_URL, pd.REV_SSH_PORT))

        if result == 0:
            print "Port is open"
            self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            print "Port is not open"
        
        return result == 0

    def open(self):
        command = 'ssh -p {} -N -R {}:localhost:22 {}@{}'.format(pd.REV_SSH_PORT, pd.REV_SSH_FORWARD_PORT, pd.REV_SSH_USER, pd.DYNDNS_URL)
        print(command)
        os.system(command)

