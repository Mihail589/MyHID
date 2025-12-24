import os
import select

def get_any_hidraw_fd():
    """Просто получаем fd любого hidraw устройства"""
    for i in range(20):
        path = f"/dev/hidraw{i}"
        if os.path.exists(path):
            try:
                # ПРОСТО ОТКРЫВАЕМ И ВОЗВРАЩАЕМ FD
                fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
                print(f"Opened {path} with fd={fd}")
                return fd, path
            except OSError as e:
                print(f"Failed to open {path}: {e}")
                # Пробуем только для чтения
                try:
                    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                    print(f"Opened {path} read-only with fd={fd}")
                    return fd, path
                except:
                    continue
    return None, None

# Самый простой пример использования
fd, path = get_any_hidraw_fd()

if fd is not None:
    print(f"\n✅ Got real fd: {fd} for device {path}")
    
    # Теперь можно использовать с epoll
    epoll = select.epoll()
    epoll.register(fd, select.EPOLLIN)
    
    print("Waiting for data (press Ctrl+C to stop)...")
    
    try:
        while True:
            events = epoll.poll(timeout=1000)
            if events:
                for event_fd, event in events:
                    if event & select.EPOLLIN:
                        try:
                            data = os.read(fd, 64)
                            if data:
                                print(f"Data from fd {fd}: {data.hex()}")
                        except BlockingIOError:
                            pass
            else:
                print("No events...")
                
    except KeyboardInterrupt:
        print("\nStopped")
    
    finally:
        epoll.unregister(fd)
        epoll.close()
        os.close(fd)
else:
    print("❌ Could not open any hidraw device")
    print("\nTry:")
    print("1. sudo python script.py")
    print("2. sudo chmod 666 /dev/hidraw*")
    print("3. ls -la /dev/hidraw* to check permissions")