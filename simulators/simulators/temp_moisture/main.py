""""""
import socketserver
import threading
from functools import partial


from libs.comunication import TempMoistureTCPHandler
from libs.files import readJson
from libs.kafka_libs import read_last_message_tp, get_consumer, get_producer, send_msg, set_topics_partitions
from kafka import TopicPartition


class TempMoisture:
    def __init__(self, file_cfg=None):
        self.moisture = 40
        self.temp = 30
        self.state = "OFF"
        self.init_kafka(file_cfg)
        self.create_dict_functions()

    def init_kafka(self, file_cfg):
        sim_data = readJson(file_cfg)
        self.topic = sim_data["kafka"]["topic"]
        self.consumer = get_consumer([self.topic])
        self.tp_temp = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["temperature"])
        self.tp_moisture = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["moisture"])
        set_topics_partitions(self.topic, self.tp_moisture.partition+1)
        producer = get_producer()
        send_msg(producer, self.topic, self.temp, self.tp_temp.partition)
        send_msg(producer, self.topic, self.moisture, self.tp_moisture.partition)

    def get_moisture(self, **kwargs):
        self.moisture = read_last_message_tp(self.consumer, self.tp_moisture)
        return self.moisture

    def get_temp(self, **kwargs):
        self.temp = read_last_message_tp(self.consumer, self.tp_temp)
        return self.temp

    def set_state(self, **kwargs):
        self.state = kwargs["data"]

    def get_state(self, **kwargs):
        return self.state

    def create_dict_functions(self):
        self.dict_functions_beam = {
            "GET_MOIST": partial(self.get_moisture), "GET_TEMP": partial(self.get_temp),
            "GET_STATE": partial(self.get_state), "SET_STATE": partial(self.set_state, data=None)}



if __name__ == "__main__":
    server_data = readJson('config/temp_moisture_config.json')
    ip_address = server_data['server']['ip']
    port = server_data['server']['port']
    try:
        server = socketserver.TCPServer((ip_address, port), TempMoistureTCPHandler)
        server.temp_moist = TempMoisture(file_cfg='config/temp_moisture_config.json')
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
