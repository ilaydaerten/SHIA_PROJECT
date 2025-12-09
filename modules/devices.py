class DeviceManager:
    def __init__(self):
        # Cihazların başlangıç durumları
        self.devices = {
            "heater_main": "OFF",
            "ac_main": "OFF",
            "lights_living": "OFF",
            "smart_lock": "LOCKED"
        }

    def update_device(self, device_id, action):
        """Cihaz durumunu günceller."""
        if device_id in self.devices:
            self.devices[device_id] = action
            return True, f"{device_id} is now {action}"
        return False, f"Device {device_id} not found."

    def get_status(self):
        return self.devices