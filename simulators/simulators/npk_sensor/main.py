""""""
import socketserver
import threading
from functools import partial


from libs.comunication import NpkSensorTCPHandler
from libs.files import readJson
from libs.kafka_libs import read_last_message_tp, get_consumer, get_producer, send_msg, set_topics_partitions
from kafka import TopicPartition


class NpkSensor:
    def __init__(self, file_cfg=None):
        self.nitrogen = 40
        self.phosphorus = 30
        self.potassium = 30
        self.state = "OFF"
        self.init_kafka(file_cfg)
        self.create_dict_functions()

    def init_kafka(self, file_cfg):
        sim_data = readJson(file_cfg)
        self.topic = sim_data["kafka"]["topic"]
        self.consumer = get_consumer([self.topic])
        self.num_partition = sim_data["kafka"]["partitions"]["nitrogen"]
        self.tp_nitrogen = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["nitrogen"])
        self.tp_phosphorus = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["phosphorus"])
        self.tp_potassium = TopicPartition(self.topic, sim_data["kafka"]["partitions"]["potassium"])
        set_topics_partitions(self.topic, self.tp_potassium.partition+1)
        producer = get_producer()
        send_msg(producer, self.topic, self.nitrogen, self.tp_nitrogen.partition)
        send_msg(producer, self.topic, self.phosphorus, self.tp_phosphorus.partition)
        send_msg(producer, self.topic, self.potassium, self.tp_potassium.partition)

    def get_nitrogen(self, **kwargs):
        self.nitrogen = read_last_message_tp(self.consumer, self.tp_nitrogen)
        return self.nitrogen

    def get_phosphorus(self, **kwargs):
        self.phosphorus = read_last_message_tp(self.consumer, self.tp_phosphorus)
        return self.phosphorus

    def get_potassium(self, **kwargs):
        self.potassium = read_last_message_tp(self.consumer, self.tp_potassium)
        return self.potassium

    def set_state(self, **kwargs):
        self.state = kwargs["data"]

    def get_state(self, **kwargs):
        return self.state

    def create_dict_functions(self):
        self.dict_functions_beam = {
            "GET_NITRO": partial(self.get_nitrogen), "GET_PHOSP": partial(self.get_phosphorus),
            "GET_POTAS": partial(self.get_potassium),
            "GET_STATE": partial(self.get_state), "SET_STATE": partial(self.set_state, data=None)}



if __name__ == "__main__":
    server_data = readJson('config/npksensors_config.json')
    ip_address = server_data['server']['ip']
    port = server_data['server']['port']
    try:
        server = socketserver.TCPServer((ip_address, port), NpkSensorTCPHandler)
        server.npk = NpkSensor(file_cfg='config/npksensors_config.json')
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
