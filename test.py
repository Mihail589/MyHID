import hid
import os

def try_direct_open():
    """Пытаемся открыть устройство разными способами"""
    
    # Способ 1: Попробовать все возможные устройства
    print("Method 1: Trying all devices...")
    all_devices = hid.enumerate()
    
    for dev in all_devices:
        try:
            print(f"\nTrying device at path: {dev['path'][:50]}...")
            device = hid.device()
            device.open_path(dev['path'])
            
            print(f"  Success! Device info:")
            print(f"    Vendor:  0x{dev['vendor_id']:04X}")
            print(f"    Product: 0x{dev['product_id']:04X}")
            
            # Получаем строки если возможно
            try:
                print(f"    Manufacturer: {device.get_manufacturer_string()}")
                print(f"    Product: {device.get_product_string()}")
            except:
                pass
                
            device.close()
            
        except Exception as e:
            print(f"  Failed: {e}")
    
    # Способ 2: Попробовать конкретные VID/PID
    print("\n\nMethod 2: Trying specific VID/PID...")
    
    # Ваши значения
    vid_pid_attempts = [
        (0x04D8, 0xF95C),     # Ваши значения
        (0x04D8, None),       # Только vendor
        (None, 0xF95C),       # Только product
        (1240, 63820),        # Десятичные значения
    ]
    
    for vid, pid in vid_pid_attempts:
        print(f"\nTrying VID={vid}, PID={pid}...")
        try:
            device = hid.device()
            if vid is not None and pid is not None:
                device.open(vid, pid)
            elif vid is not None:
                device.open(vendor_id=vid)
            elif pid is not None:
                device.open(product_id=pid)
            
            print(f"  Success!")
            device.close()
        except Exception as e:
            print(f"  Failed: {e}")

if __name__ == "__main__":
    try_direct_open()