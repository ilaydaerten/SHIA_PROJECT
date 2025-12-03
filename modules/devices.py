class DeviceManager:
    def __init__(self):
        self.devices = {
            "Heater": "OFF",
            "AirConditioner": "OFF",
            "Lights": "OFF",
            "DoorLock": "LOCKED",
            "Window": "CLOSED"
        }

    def update_device(self, device_name, action):
        if device_name in self.devices:
            self.devices[device_name] = action
            print(f"[Device Log] {device_name} -> {action}")
        else:
            print(f"Hata: {device_name} bulunamadı.")
            
    def get_status(self):
        return self.devices