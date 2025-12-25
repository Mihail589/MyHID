import os

def find_hidraw_for_device(device_path):
    """
    device_path: например b'3-1:1.0' или '3-1:1.0'
    """
    if isinstance(device_path, bytes):
        device_path = device_path.decode('utf-8')
    
    # Убираем :1.0 если есть (интерфейс)
    bus_path = device_path.split(':')[0]  # '3-1'
    
    for i in range(20):
        hidraw_path = f"/dev/hidraw{i}"
        if os.path.exists(hidraw_path):
            try:
                # Проверяем через sysfs
                uevent_path = f"/sys/class/hidraw/hidraw{i}/device/uevent"
                if os.path.exists(uevent_path):
                    with open(uevent_path, 'r') as f:
                        uevent = f.read()
                    
                    # Ищем информацию о bus
                    for line in uevent.split('\n'):
                        if 'HID_UNIQ' in line or 'MODALIAS' in line:
                            # Пример строки: MODALIAS=hid:b0003g0001v000004D8p00000A5C
                            # Или ищем bus путь
                            if bus_path in uevent:
                                print(f"Found match: {hidraw_path} for {device_path}")
                                print(f"Uevent content:\n{uevent}")
                                return hidraw_path
                
                # Альтернативный путь проверки
                dev_path = f"/sys/class/hidraw/hidraw{i}/device"
                if os.path.exists(dev_path):
                    # Собираем полный путь устройства
                    realpath = os.path.realpath(dev_path)
                    print(f"hidraw{i}: {realpath}")
                    if device_path in realpath:
                        print(f"Direct match found: {hidraw_path}")
                        return hidraw_path
                        
            except Exception as e:
                print(f"Error checking {hidraw_path}: {e}")
                continue
    
    return None

find_hidraw_for_device(b'3-1:1.0')