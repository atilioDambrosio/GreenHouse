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

from libs.comunication import WindTCPHandler
from libs.files import readJson
from libs.kafka_libs import read_last_message_tp, get_consumer, get_producer, send_msg, set_topics_partitions
from kafka import TopicPartition


class Wind:
    def __init__(self, file_cfg=None):
        self.speed = 40
        self.direction = 40
        self.state = "OFF"
        self.init_kafka(file_cfg)
        self.create_dict_functions()

    def init_kafka(self, file_cfg):
        sim_data = readJson(file_cfg)
        self.topic = sim_data["kafka"]["topic"]
        self.consumer = get_consumer([self.topic])
        self.tp_speed = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["speed"])
        self.tp_direction = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["direction"])
        producer = get_producer()
        set_topics_partitions(self.topic, self.tp_direction.partition+1)
        send_msg(producer, self.topic, self.speed, self.tp_speed.partition)
        send_msg(producer, self.topic, self.direction, self.tp_direction.partition)

    def get_speed(self, **kwargs):
        self.speed = read_last_message_tp(self.consumer, self.tp_speed)
        return self.speed

    def get_direction(self, **kwargs):
        self.direction = read_last_message_tp(self.consumer, self.tp_direction)
        return self.direction

    def set_state(self, **kwargs):
        self.state = kwargs["data"]

    def get_state(self, **kwargs):
        return self.state

    def create_dict_functions(self):
        self.dict_functions_beam = {
            "GET_SPEED": partial(self.get_speed), "GET_DIRECT": partial(self.get_direction),
            "GET_STATE": partial(self.get_state), "SET_STATE": partial(self.set_state, data=None)}



if __name__ == "__main__":
    server_data = readJson('config/wind_config.json')
    ip_address = server_data['server']['ip']
    port = server_data['server']['port']
    try:
        server = socketserver.TCPServer((ip_address, port), WindTCPHandler)
        server.wind = Wind(file_cfg='config/wind_config.json')
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
