import hid, select
from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        super().__init__(device_address, send_report_id, use_hidd)


    def _open_path(self, path):
        self.device = hid.device()
        attrs = dir(self.device)
        print(attrs)
        self.device.open_path(path)
        
        
    def write(self, data):
        self.device.write(data)

    def read(self, size = 1):
        self.device.set_nonblocking(0)
        data = self.device.read(64, timeout_ms=1000)
        return data
if __name__ == "__main__":
    print(Hid.discover())
    h = Hid.init_by_device_name("Usb Mouse")
    h.run()
    for i in range(3):
        h.write(b'\xc8\x04(\x00\x0e|')
        print(bytes(h.read()))
