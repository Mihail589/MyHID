import hid, os
from select import epoll, EPOLLIN

from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        self.epoll = epoll()
        super().__init__(device_address, send_report_id, use_hidd)


    def _open_path(self, path):
        fd = os.open("/dev/hidraw0", os.O_RDWR | os.O_NONBLOCK)
        print(f"Opened {path} with fd={fd}")
        self.device = hid.device()
        self.device.open_path(path)
        
        self.epoll.registred(fd)
        self.fd = fd


    def write(self, data):
        self.device.write(data)

    def read(self, size = 1):
        self.runner = True
        return self._wait_for_event()

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
            for fd, event in events:
                event_count += 1
                
                print(f"\n{'='*50}")
                print(f"Event #{event_count} on fd={fd}")
                
                # Декодируем события
                event_flags = []
                if event & EPOLLIN:
                    if fd == self.fd:
                        return self.readHID()