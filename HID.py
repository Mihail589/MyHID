import hid
from select import epoll

from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        self.epoll = epoll()
        super().__init__(device_address, send_report_id, use_hidd)


    def _open_path(self, path):
        self.device = hid.device()
        self.device.open_path(path)


    def write(self, data):
        self.device.write(data)

    def read(self, size = 1):
        self.runner = True
        self._wait_for_event()

    def readHID(self):
        self.device.set_nonblocking(0)
        data = b''
        while data == b'':
            data = bytes(self.device.read(64, timeout_ms=1000))
        self.runner = False
        return data 

    def _wait_for_event(self):
        while self.runner:
            events = self.epoll.poll(3)
            