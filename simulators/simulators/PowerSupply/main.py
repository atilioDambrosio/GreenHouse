""""""
import socketserver
import threading
from functools import partial

'''
#---------------------------------------------------------------------------------
# Copyright (C) 2020, CELIS TTI BU.
# The copyright to the computer program(s) herein is the property of TTI NORTE SL
#
# The program(s) may be used and/or copied only with the written permission
# of CELIS TTI BU or in accordance with the terms and conditions stipulated in the
# agreement/contract under which the program(s) have been supplied.
#
# This library provides a collection of functions for controlling the Keysight VSA 89601B that runs on a MXA platform.
# These functions are aimed to simplify the high level test procedures where this instrument is involved within SGMA.
#
#Chiller's simulator
# URL: $HeadURL: https://192.168.1.10:8443/svn/projects/trunk/escan/simulators/chiller/main.py $
# Last commit author: $Author: pmonsalvete $
# Revision: $Revision: 39 $
# Date: $Date: 2022-11-17 11:23:08 -0100 (Thu, 17 Nov 2022) $
# Module ID
# $Id: main.py 39 2022-11-17 12:23:08Z pmonsalvete $
#---------------------------------------------------------------------------------
'''

from libs.comunication import PowerSupplyTCPHandler
from libs.files import readJson


class PowerSupply:
    def __init__(self):
        self.volt = 0
        self.current = 0
        self.current_limit = 5
        self.resistor = 10
        self.state = "OFF"
        self.create_dict_functions()
        thread_main_loop = threading.Thread(target=self.loop_read_current)
        thread_main_loop.daemon = True
        thread_main_loop.start()

    def loop_read_current(self):
        while True:
            if self.state == 'ON' and self.volt/self.resistor > self.current_limit:
                self.state = 'OFF'

    def get_volt(self, **kwargs):
        return self.volt

    def get_current(self, **kwargs):
        return (self.volt/self.resistor)

    def get_current_limit(self, **kwargs):
        return self.current_limit

    def set_volt(self, **kwargs):
        self.volt = float(kwargs["data"])

    def set_current(self, **kwargs):
        self.current_limit = float(kwargs["data"])

    def set_state(self, **kwargs):
        self.state = kwargs["data"]

    def get_state(self, **kwargs):
        return self.state

    def create_dict_functions(self):
        self.dict_functions_beam = {
            "GET_VOLT": partial(self.get_volt), "GET_CURRENT": partial(self.get_current),
            "GET_CURRENT_LIMIT":partial(self.get_current_limit),
            "SET_VOLT": partial(self.set_volt, data=None),
            "SET_CURRENT": partial(self.set_current, data=None),
            "GET_STATE": partial(self.get_state), "SET_STATE": partial(self.set_state, data=None)}



if __name__ == "__main__":
    server_data = readJson('/home/celis/power_supply_sim/config/soil_moisture_config.json')
    ip_address = server_data['server']['ip']
    port = server_data['server']['port']
    try:
        server = socketserver.TCPServer((ip_address, port), PowerSupplyTCPHandler)
        server.power_supply = PowerSupply()
        server.allow_reuse_address = True
        print("Server created in IP {}\tPORT {}".format(ip_address, port))
        print("Server is waiting...")
        server.serve_forever()
        while True:
            pass
    except KeyboardInterrupt:
        server.shutdown()
        print("Server closed")
    except ConnectionResetError:
        print("Polling closed")
