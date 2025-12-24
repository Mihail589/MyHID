import os
import fcntl
import struct
import glob

def find_and_open_hidraw(vid, pid):
    """
    Найти и открыть hidraw устройство по VID/PID
    Возвращает файловый дескриптор
    """
    # Преобразуем VID/PID в hex
    vid_hex = f"{vid:04x}"
    pid_hex = f"{pid:04x}"
    
    # Ищем в sysfs
    sysfs_pattern = f"/sys/bus/hid/devices/*{vid_hex}:{pid_hex}*/hidraw"
    
    for sysfs_path in glob.glob(sysfs_pattern):
        # Получаем имя hidraw устройства
        hidraw_devices = os.listdir(sysfs_path)
        if hidraw_devices:
            hidraw_name = hidraw_devices[0]
            dev_path = f"/dev/{hidraw_name}"
            
            try:
                # Открываем устройство
                fd = os.open(dev_path, os.O_RDWR | os.O_NONBLOCK)
                print(f"Открыто устройство: {dev_path}, fd={fd}")
                return fd
            except OSError as e:
                print(f"Ошибка открытия {dev_path}: {e}")
    
    return None

# Использование
VID = 1240
PID = 63820

fd = find_and_open_hidraw(VID, PID)
print(fd)