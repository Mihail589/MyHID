from HID import *
from commands.ping import ping
if __name__ == "__main__":
    print(Hid.discover())
    h = Hid.init_by_device_name("TBS CROSSFIRE")
    h.run()
    for i in range(3):
        h.write(ping.pingTBS())
        print(bytes(h.read()))
