import hid, select, glob, os

from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        super().__init__(device_address, send_report_id, use_hidd)


    def _open_path(self, path):
        self.device = hid.device()
        self.device.open_path(path)
        vid, pid = 0, 0
        for i in self.discover():
            if i["path"] == path:
                vid = i["vendor_id"]
                pid = i["product_id"]
        
        if vid == 0:
            print(vid)
            return
        
        # Ищем hidraw
        vid_hex = f"{vid:04x}".lower()
        pid_hex = f"{pid:04x}".lower()
        print(glob.glob('/dev/hidraw*'))
        for hidraw in glob.glob('/dev/hidraw*'):
                name = os.path.basename(hidraw)
                uevent = f'/sys/class/hidraw/{name}/device/uevent'
                print(name)
                if os.path.exists(uevent):
                    with open(uevent, 'r') as f:
                        if f"0003:{vid_hex}:{pid_hex}" in f.read().lower():
                            self.select_fd = os.open(hidraw, os.O_RDONLY | os.O_NONBLOCK)
                            print(uevent)
                            break

    def write(self, data):
        self.device.write(data)

    def read(self, size = 1):
        self.device.set_nonblocking(0)
        data = self.device.read(64, timeout_ms=2000)

        return data
