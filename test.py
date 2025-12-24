import os
import select, time

def open_all_hidraw_devices():
    """Открывает все hidraw устройства и возвращает список fd"""
    fds = []
    
    print("Scanning /dev/hidraw* devices...")
    
    for i in range(20):
        dev_path = f"/dev/hidraw{i}"
        
        if not os.path.exists(dev_path):
            continue
            
        try:
            # Открываем устройство
            fd = os.open(dev_path, os.O_RDONLY | os.O_NONBLOCK)
            print(f"Opened {dev_path} with fd={fd}")
            fds.append((fd, dev_path))
            
        except OSError as e:
            print(f"Failed to open {dev_path}: {e}")
    
    return fds

def test_hidraw_fds():
    """Тестируем все открытые hidraw устройства"""
    fds = open_all_hidraw_devices()
    
    if not fds:
        print("No hidraw devices found")
        return
    
    print(f"\nFound {len(fds)} hidraw device(s)")
    
    # Создаем epoll
    epoll = select.epoll()
    
    # Регистрируем все fd в epoll
    for fd, path in fds:
        epoll.register(fd, select.EPOLLIN)
        print(f"Registered fd={fd} ({path}) with epoll")
    
    print("\nReading from devices for 10 seconds...")
    
    try:
        end_time = time.time() + 10
        
        while time.time() < end_time:
            # Ждем события
            events = epoll.poll(timeout=100)  # 100ms
            
            for fd, event in events:
                # Находим путь устройства по fd
                path = None
                for f, p in fds:
                    if f == fd:
                        path = p
                        break
                
                print(f"\nEvent on fd={fd} ({path}): event={event}")
                
                if event & select.EPOLLIN:
                    try:
                        # Пробуем прочитать
                        data = os.read(fd, 64)
                        print(f"  Read {len(data)} bytes: {data.hex()}")
                        
                        # Если данные есть, это может быть наше устройство!
                        if data:
                            print(f"  +++ POSSIBLE TARGET DEVICE! +++")
                            print(f"  Device path: {path}")
                            print(f"  Data sample: {data[:16].hex()}...")
                            
                    except BlockingIOError:
                        print("  No data available")
                    except OSError as e:
                        print(f"  Read error: {e}")
                
                elif event & select.EPOLLHUP:
                    print("  Device disconnected")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    finally:
        # Очистка
        print("\nCleaning up...")
        for fd, path in fds:
            epoll.unregister(fd)
            os.close(fd)
            print(f"Closed fd={fd} ({path})")
        
        epoll.close()

if __name__ == "__main__":
    test_hidraw_fds()