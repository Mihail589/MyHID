import os
import select
import fcntl
import struct

def get_hidraw_fd(vid, pid):
    """
    Находит hidraw устройство по VID/PID и возвращает его fd
    """
    for i in range(10):  # Проверяем hidraw0..hidraw9
        dev_path = f"/dev/hidraw{i}"
        if os.path.exists(dev_path):
            try:
                # Открываем устройство
                fd = os.open(dev_path, os.O_RDWR | os.O_NONBLOCK)
                
                # Получаем информацию об устройстве
                buf = bytearray(512)
                res = fcntl.ioctl(fd, 0x80085501, buf)  # HIDIOCGRAWINFO
                
                if res >= 0:
                    bustype, vendor, product = struct.unpack('HHH', buf[:6])
                    if vendor == vid and product == pid:
                        return fd
                
                # Не подходит - закрываем
                os.close(fd)
            except (OSError, IOError):
                continue
    
    return None

# Пример использования
vid = 0x04D8  # Пример: Logitech
pid = 0xF95C  # Пример: Unifying Receiver

fd = get_hidraw_fd(vid, pid)
print(f"HID device fd: {fd}")