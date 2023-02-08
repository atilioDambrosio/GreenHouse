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

from libs.comunication import SoilMoistureTCPHandler
from libs.files import readJson
from libs.kafka_libs import read_last_message_tp, get_consumer, get_producer, send_msg
from kafka import TopicPartition


class SoilMoisture:
    def __init__(self, file_cfg=None):
        self.soil_moisture = 30
        self.state = "OFF"
        self.init_kafka(file_cfg)
        self.create_dict_functions()

    def init_kafka(self, file_cfg):
        sim_data = readJson(file_cfg)
        self.topic = sim_data["kafka"]["topic"]
        self.consumer = get_consumer([self.topic])
        self.num_partition = sim_data["kafka"]["partitions"]["soil_moisture"]
        self.tp_soil_moisture = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["soil_moisture"])
        producer = get_producer()
        send_msg(producer, self.topic, self.soil_moisture, self.num_partition)

    def get_soil_moisture(self, **kwargs):
        self.soil_moisture = read_last_message_tp(self.consumer, self.tp_soil_moisture)
        return self.soil_moisture

    def set_state(self, **kwargs):
        self.state = kwargs["data"]

    def get_state(self, **kwargs):
        return self.state

    def create_dict_functions(self):
        self.dict_functions_beam = {
            "GET_MOIST": partial(self.get_soil_moisture),
            "GET_STATE": partial(self.get_state), "SET_STATE": partial(self.set_state, data=None)}



if __name__ == "__main__":
    server_data = readJson('config/soil_moisture_config.json')
    ip_address = server_data['server']['ip']
    port = server_data['server']['port']
    try:
        server = socketserver.TCPServer((ip_address, port), SoilMoistureTCPHandler)
        server.soil_moist = SoilMoisture(file_cfg='config/soil_moisture_config.json')
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
