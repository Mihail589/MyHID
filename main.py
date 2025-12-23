import hid
from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        super().__init__(device_address, send_report_id, use_hidd)

    def _write_report(self, data: bytes):
        pass

    def _open_path(self, path):
        for device_info in self.discover():  # Для каждого найденного HID устройства
            if device_info["path"] == path:  # Если имя устройства совпало
                pid = f"0x{device_info['product_id']:04x}"
                vid = f"0x{device_info['vendor_id']:04x}"
                break
        self.device = hid.device(vid, pid)
        
    def _write_report(self, data: bytes):
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
    h = Hid(HidAttributes(0x04d8, 0xf94c))
    h.run()
    h.write(b'\xc8\x04(\x00\x0e|')
    print(h.read())
