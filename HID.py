import hid, os
import select
from select import epoll, EPOLLIN, EPOLLERR, EPOLLHUP

from base_hid import *

class Hid(BaseHid):
    def __init__(self, device_address, send_report_id = 0, use_hidd = False):
        self.epoll = epoll()
        self.fd = None
        super().__init__(device_address, send_report_id, use_hidd)

    def _open_path(self, path):
        # Находим соответствующий hidraw устройству
        device_found = False
        for i in range(20):
            pathh = f"/dev/hidraw{i}"
            if os.path.exists(pathh):
                # Проверяем, соответствует ли это устройство нашему пути
                try:
                    fd = os.open(pathh, os.O_RDWR | os.O_NONBLOCK)
                    
                    # Создаем устройство hid для основной работы
                    self.device = hid.device()
                    self.device.open_path(path)
                    
                    # Регистрируем файловый дескриптор в epoll
                    self.epoll.register(fd, EPOLLIN | EPOLLERR | EPOLLHUP)
                    self.fd = fd
                    
                    print(f"Opened {path} as {pathh} with fd={fd}")
                    device_found = True
                    break
                except Exception as e:
                    print(f"Error opening {pathh}: {e}")
                    if 'fd' in locals():
                        os.close(fd)
        
        if not device_found:
            raise Exception(f"Cannot find hidraw device for {path}")

    def write(self, data):
        if hasattr(self, 'device') and self.device:
            self.device.write(data)
        else:
            raise Exception("Device not opened")

    def read(self, size=1):
        # Используем epoll для ожидания данных
        return self._wait_for_event()

    def readHID(self):
        # Чтение через hidapi
        try:
            if hasattr(self, 'device') and self.device:
                data = bytes(self.device.read(64, timeout_ms=100))
                return data if data else b''
        except Exception as e:
            print(f"Error reading from HID: {e}")
            return b''

    def readRaw(self):
        # Чтение напрямую из файлового дескриптора
        if self.fd:
            try:
                data = os.read(self.fd, 64)
                return data
            except BlockingIOError:
                return b''
            except Exception as e:
                print(f"Error reading from fd {self.fd}: {e}")
                return b''
        return b''

    def _wait_for_event(self, timeout=1000):
        """Ожидание событий с использованием epoll"""
        if not self.fd:
            return b''
        
        try:
            # Ожидаем события с таймаутом (в миллисекундах)
            events = self.epoll.poll(timeout / 1000.0 if timeout else None)
            
            for fd, event in events:
                if fd == self.fd:
                    if event & EPOLLIN:
                        # Данные доступны для чтения
                        return self.readRaw()
                    elif event & EPOLLERR:
                        print("Error on device fd")
                        return b''
                    elif event & EPOLLHUP:
                        print("Device disconnected")
                        return b''
        
        except Exception as e:
            print(f"Error in epoll.poll: {e}")
        
        return b''

    def close(self):
        """Корректное закрытие устройства"""
        if hasattr(self, 'epoll') and self.epoll and self.fd:
            self.epoll.unregister(self.fd)
        
        if self.fd:
            os.close(self.fd)
            self.fd = None
        
        if hasattr(self, 'device') and self.device:
            self.device.close()
        
        if hasattr(self, 'epoll') and self.epoll:
            self.epoll.close()