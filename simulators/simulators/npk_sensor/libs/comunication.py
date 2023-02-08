""""""
import json
import socketserver
import traceback

from libs.files import readJson
import time


class NpkSensorTCPHandler(socketserver.BaseRequestHandler):
    """
    This is the handler class fort he TCP server used for communication
    """

    def handle(self):
        while True:
            self.npk = self.server.npk
            answer_recv = rec_answer(self.request).replace('"', "")
            answers = answer_recv.split(",")
            for answer in answers:
                try:
                    if "GET_" in answer:
                        answer = self.npk.dict_functions_beam[answer]()
                    elif "SET_" in answer:
                        request, value = answer.split(" ")
                        self.npk.dict_functions_beam[request](data=value)
                        answer = "23"
                    else:
                        answer = "ERROR in request"
                except Exception as e:
                    answer = "ERROR"
                    print("EEROR", e)
                send_answer(self.request, answer)



def send_answer(sock_c, answer):
    answer_bin = json.dumps(answer).encode('utf-8')
    endingChar = "\n"
    sock_c.sendall(answer_bin + endingChar.encode())


def rec_answer(socket):
    char = socket.recv(1).decode()
    word = ''
    if char != "":
        while char != "\n":
            word = word + char
            char = socket.recv(1).decode()
        print(word)
    return word
