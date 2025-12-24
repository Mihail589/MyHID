import os
import select
import fcntl
import array
import time

def get_hidraw_fd_direct(vid=0x04D8, pid=0xF95C):
    """
    Прямое открытие hidraw устройства - возвращает настоящий fd!
    """
    for i in range(20):  # Проверяем hidraw0..hidraw19
        dev_path = f"/dev/hidraw{i}"
        print(dev_path)
        if not os.path.exists(dev_path):
            continue
        
        # ОТКРЫВАЕМ УСТРОЙСТВО И ПОЛУЧАЕМ НАСТОЯЩИЙ FD!
        fd = os.open(dev_path, os.O_RDWR | os.O_NONBLOCK)
        
        # Проверяем VID/PID
        buf = array.array('H', [0, 0, 0])
        try:
            # HIDIOCGRAWINFO = 0x80085501
            fcntl.ioctl(fd, 0x80085501, buf, True)
            
            bustype, vendor, product = buf
            
            if vendor == vid and product == pid:
                print(f"✓ Found device: {dev_path}")
                print(f"  FD: {fd}")
                print(f"  VID: 0x{vendor:04X}, PID: 0x{product:04X}")
                return fd
            else:
                # Не наше устройство - закрываем
                os.close(fd)
                
        except IOError as e:
            print(f"  ioctl failed: {e}")
            os.close(fd)
                
    print("✗ Device not found")
    return None

# Пример: использование fd с epoll
def use_hidraw_with_epoll():
    print("Getting direct hidraw fd...")
    
    # ПОЛУЧАЕМ НАСТОЯЩИЙ FD!
    hid_fd = get_hidraw_fd_direct()
    
    if hid_fd is None:
        print("Device not found via hidraw")
        return
    
    print(f"\nSuccess! Real FD: {hid_fd}")
    
use_hidraw_with_epoll()