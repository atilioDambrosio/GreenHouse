import threading
import time
from PyQt5 import uic
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit
from PyQt5.QtCore import pyqtSignal
import sys
from libs.comunication import TempMoistureTCPHandler
from libs.files import readJson
import socketserver
from main import TempMoisture

class MainWindow(QMainWindow):
    trigger_update_volts = pyqtSignal(float)
    trigger_update_current = pyqtSignal(float)
    trigger_update_output_current = pyqtSignal(float)

    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi("./Files/untitled.ui",self)
        self.disable_buttons()
        self.check_state_OFF = False
        self.check_state_ON = True
        self.display = False
        self.dial_volts.valueChanged.connect(lambda: self.dialer_volts())
        self.dial_current.valueChanged.connect(lambda: self.dialer_current())
        self.dial_volts.sliderReleased.connect(self.set_volt)
        self.dial_current.sliderReleased.connect(self.set_current)
        self.dial_volts.sliderPressed.connect(self.update_main_loop)
        self.dial_current.sliderPressed.connect(self.update_main_loop)
        self.trigger_update_volts.connect(self.update_volts)
        self.trigger_update_current.connect(self.update_current)
        self.trigger_update_output_current.connect(self.update_output_current)
        self.button_state.clicked.connect(self.update_state)
        self.power_supply = TempMoisture()
        self.start_server()
        thread_main_loop = threading.Thread(target=self.loop_read)
        thread_main_loop.daemon = True
        thread_main_loop.start()
        # self.loop_read()

    def update_state(self):
        if self.button_state.isChecked():
            self.power_supply.set_state(data="ON")
            self.power_supply.set_current(data=5)
            self.display = True
            self.enable_buttons()
        else:
            self.state_off()

    def state_off(self):
        self.power_supply.set_state(data="OFF")
        self.power_supply.set_volt(data=0)
        self.power_supply.set_current(data=0)
        self.disable_buttons()
        self.trigger_update_current.emit(0)
        self.trigger_update_volts.emit(0)
        self.trigger_update_output_current.emit(0)
        self.dial_current.setValue(0)
        self.dial_volts.setValue(0)
        self.display = False

    def disable_buttons(self):
        self.lcd_volts.setEnabled(False)
        self.lcd_output_amps.setEnabled(False)
        self.lcd_current.setEnabled(False)
        self.dial_volts.setEnabled(False)
        self.dial_current.setEnabled(False)

    def enable_buttons(self):
        self.lcd_volts.setEnabled(True)
        self.lcd_output_amps.setEnabled(True)
        self.lcd_current.setEnabled(True)
        self.dial_volts.setEnabled(True)
        self.dial_current.setEnabled(True)

    def start_server(self):
        server_data = readJson(
            'config/lumens_config.json')
        ip_address = server_data['server']['ip']
        port = server_data['server']['port']
        self.server = socketserver.TCPServer((ip_address, port), TempMoistureTCPHandler)
        self.server.power_supply = self.power_supply
        self.server.allow_reuse_address = True
        print("Server created in IP {}\tPORT {}".format(ip_address, port))
        print("Server is waiting...")
        server_tcp = threading.Thread(target=self.server.serve_forever)
        server_tcp.daemon = True
        server_tcp.start()

    def update_main_loop(self):
        self.display = False

    def loop_read(self):
        while True:
            if self.display:
                self.trigger_update_current.emit(float(self.power_supply.get_current_limit()))
                self.trigger_update_output_current.emit(float(self.power_supply.get_current()))
                self.trigger_update_volts.emit(float(self.power_supply.get_volt()))
            self.loop_state()
            time.sleep(1)

    def loop_state(self):
        if self.power_supply.get_state() == 'ON' and self.check_state_ON:
            self.button_state.setChecked(True)
            self.check_state_ON = False
            self.check_state_OFF = True
            self.update_state()
        elif self.power_supply.get_state() == 'OFF' and self.check_state_OFF:
            self.button_state.setChecked(False)
            self.check_state_OFF = False
            self.check_state_ON = True
            self.update_state()


    def dialer_volts(self):
        value = self.dial_volts.value()
        self.trigger_update_volts.emit(value/100)

    def set_volt(self):
        self.power_supply.set_volt(data=self.dial_volts.value()/100)
        self.display = True

    def set_current(self):
        self.power_supply.set_current(data=self.dial_current.value()/100)
        self.display = True

    def dialer_current(self):
        value = self.dial_current.value()
        self.trigger_update_current.emit(value/100)

    def update_current(self, value):
        self.lcd_current.display('{:.02f}'.format(value))

    def update_volts(self, value):
        self.lcd_volts.display('{:.02f}'.format(value))

    def update_output_current(self, value):
        self.lcd_output_amps.display('{:.02f}'.format(value))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())