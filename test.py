import hid

def check_device_info():
    """Проверяет доступность устройства и получает информацию"""
    vid = 0x04D8
    pid = 0xF95C
    
    print(f"Looking for device {vid:04X}:{pid:04X}")
    
    # Получаем список всех HID устройств
    all_devices = hid.enumerate()
    print(f"Total HID devices: {len(all_devices)}")
    
    # Ищем наше устройство
    target_devices = hid.enumerate(vid, pid)
    
    if not target_devices:
        print("Device not found!")
        return False
    
    print(f"Found {len(target_devices)} matching device(s):")
    
    for i, dev_info in enumerate(target_devices):
        print(f"\nDevice {i+1}:")
        print(f"  Vendor ID:  {dev_info['vendor_id']:04X}")
        print(f"  Product ID: {dev_info['product_id']:04X}")
        print(f"  Path:       {dev_info['path']}")
        print(f"  Serial:     {dev_info['serial_number']}")
        print(f"  Manufacturer: {dev_info['manufacturer_string']}")
        print(f"  Product:      {dev_info['product_string']}")
        print(f"  Release:      {dev_info['release_number']}")
        print(f"  Interface:    {dev_info['interface_number']}")
        
        # Пытаемся открыть устройство
        try:
            device = hid.device()
            device.open_path(dev_info['path'])
            
            # Получаем строки
            print(f"  Manufacturer: {device.get_manufacturer_string()}")
            print(f"  Product: {device.get_product_string()}")
            print(f"  Serial: {device.get_serial_number_string()}")
            
            # Пробуем прочитать дескриптор
            report_desc = device.get_report_descriptor()
            print(f"  Report desc size: {len(report_desc) if report_desc else 0}")
            
            device.close()
            
        except Exception as e:
            print(f"  Cannot open: {e}")
    
    return True

if __name__ == "__main__":
    check_device_info()