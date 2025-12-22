import hid
from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        super().__init__(device_address, send_report_id, use_hidd)
        

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
   # h = Hid.init_by_device_name("Usb Mouse")

