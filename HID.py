import os
import select
from select import epoll, EPOLLIN, EPOLLERR, EPOLLHUP
from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id=0, use_hidd=False):
        self.epoll = epoll()
        self.fd = None
        super().__init__(device_address, send_report_id, use_hidd)

    def _open_path(self, path):
        # Преобразуем путь устройства в hidraw
        self.path = path if isinstance(path, bytes) else path.encode()
        # Ищем соответствующий hidraw
        device_found = False
        for i in range(20):
            hidraw_path = f"/dev/hidraw{i}"
            if os.path.exists(hidraw_path):
                # Проверяем, соответствует ли это нашему устройству
                try:
                    # Можно проверить через sysfs
                    dev_path = f"/sys/class/hidraw/hidraw{i}/device"
                    if os.path.exists(dev_path):
                    # Собираем полный путь устройства
                        realpath = os.path.realpath(dev_path)
                        print(f"hidraw{i}: {realpath}")
                        if path.decode() in realpath:
                            fd = os.open(hidraw_path, os.O_RDWR | os.O_NONBLOCK)
                            self.fd = fd
                            self.epoll.register(fd, EPOLLIN | EPOLLERR | EPOLLHUP)
                except Exception as e:
                    print(f"Error checking {hidraw_path}: {e}")
        

    def write(self, data):
        if self.fd:
            # Для HID устройств часто требуется report id
            if isinstance(data, list):
                data = bytes(data)
            elif isinstance(data, int):
                data = bytes([data])
            
            try:
                return os.write(self.fd, data)
            except Exception as e:
                print(f"Error writing: {e}")
                return 0
        else:
            raise Exception("Device not opened")

    def read(self, size=64):
        return self._wait_for_event(size)
    
    def _wait_for_event(self, size):
        try:
            # Используем epoll с таймаутом
            events = self.epoll.poll(1.0)  # 1 секунда таймаут
            for fd, event in events:
                    if event & EPOLLIN:
                        return os.read(fd, size)
                    elif event & EPOLLERR:
                        print("EPOLLERR - проверьте права доступа к устройству")
                        return b''
                    elif event & EPOLLHUP:
                        print("EPOLLHUP - устройство отключено")
                        return b''
        except Exception as e:
            print(f"Error in epoll: {e}")
        
        return b''

    def close(self):
        if hasattr(self, 'epoll') and self.epoll and self.fd:
            try:
                self.epoll.unregister(self.fd)
            except:
                pass
        
        if self.fd:
            try:
                os.close(self.fd)
            except:
                pass
            self.fd = None
        
        if hasattr(self, 'epoll') and self.epoll:
            try:
                self.epoll.close()
            except:
                pass