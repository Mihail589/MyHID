
from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        super().__init__(device_address, send_report_id, use_hidd)
        


if __name__ == "__main__":
    #try:
    #    # Initialize the hidapi library
    #    list_hid_devices()
    #except Exception as e:
    #    print(f"An error occurred: {e}")
#
    #    # Finalize the hidapi library
    h = Hid.init_by_device_name("Usb Mouse")

