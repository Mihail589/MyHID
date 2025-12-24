import HID

h = HID.Hid.init_by_device_name("TBS CROSSFIRE")
h.run()
report_desc = h.device.get_report_descriptor()
print(f"  Report desc size: {len(report_desc) if report_desc else 0}")