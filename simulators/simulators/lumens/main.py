""""""
import socketserver
import threading
from functools import partial

from libs.comunication import LumemsTCPHandler
from libs.files import readJson
from libs.kafka_libs import read_last_message_tp, get_consumer, get_producer, send_msg
from kafka import TopicPartition


class Lumens:
    def __init__(self, file_cfg=None):
        self.lumens = 30
        self.state = "OFF"
        self.init_kafka(file_cfg)
        self.create_dict_functions()

    def init_kafka(self, file_cfg):
        sim_data = readJson(file_cfg)
        self.topic = sim_data["kafka"]["topic"]
        self.consumer = get_consumer([self.topic])
        self.num_partition = sim_data["kafka"]["partitions"]["lumens"]
        self.tp_lumens = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["lumens"])
        producer = get_producer()
        send_msg(producer, self.topic, self.lumens, self.num_partition)

    def get_lumens(self, **kwargs):
        self.lumens = read_last_message_tp(self.consumer, self.tp_lumens)
        return self.lumens

    def set_state(self, **kwargs):
        self.state = kwargs["data"]

    def get_state(self, **kwargs):
        return self.state

    def create_dict_functions(self):
        self.dict_functions_beam = {
            "GET_LUMS": partial(self.get_lumens),
            "GET_STATE": partial(self.get_state), "SET_STATE": partial(self.set_state, data=None)}



if __name__ == "__main__":
    server_data = readJson('config/lumens_config.json')
    ip_address = server_data['server']['ip']
    port = server_data['server']['port']
    try:
        server = socketserver.TCPServer((ip_address, port), LumemsTCPHandler)
        server.lumens = Lumens(file_cfg='config/lumens_config.json')
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
