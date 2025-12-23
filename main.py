import hid
from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        super().__init__(device_address, send_report_id, use_hidd)


    def _open_path(self, path):
        print(path)
        self.device = hid.device(path=path)
        
    def write(self, data):
        self.device.write(data)

    def read(self, size = 1):
        self.device.set_nonblocking(0)
        data = self.device.read(64, timeout_ms=1000)
        return data
def list_hid_devices():
    """Enumerates and prints information about all connected HID devices."""
    print("Enumerating HID devices...")
    for device_info in hid.enumerate():
        print("-" * 50)
        print(f"Path: {device_info['path']}")
        print(f"Vendor ID (VID): 0x{device_info['vendor_id']:04x}")
        print(f"Product ID (PID): 0x{device_info['product_id']:04x}")
        print(f"Serial Number: {device_info['serial_number']}")
        print(f"Manufacturer: {device_info['manufacturer_string']}")
        print(f"Product: {device_info['product_string']}")
    print("-" * 50)

if __name__ == "__main__":
    try:
        # Initialize the hidapi library
        list_hid_devices()
    except Exception as e:
        print(f"An error occurred: {e}")

        # Finalize the hidapi library
    h = Hid.init_by_device_name("TBS CROSSFIRE")
    h.run()
    h.write(b'\xc8\x04(\x00\x0e|')
    print(h.read())
