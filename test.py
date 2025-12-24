import os
import glob

def find_hid_device_linux(vid, pid):
    """
    Поиск HID-устройства в Linux через sysfs
    """
    vid_str = f"{vid:04x}".upper()
    pid_str = f"{pid:04x}".upper()
    
    pattern = f"/sys/bus/hid/devices/*{vid_str}:{pid_str}*"
    devices = glob.glob(pattern)
    
    return devices

# Использование
devices = find_hid_device_linux(0x04D8, 0xF97C)
print(f"Найдено устройств: {len(devices)}")