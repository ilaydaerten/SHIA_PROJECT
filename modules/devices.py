from datetime import datetime


class DeviceManager:
    def __init__(self):
        """
        Cihazların gelişmiş durumu.
        """
        self.devices = {
            "heater_main": {
                "state": "OFF",
                "power_usage": 1800,  # Watt
                "type": "heater",
                "description": "Ana oda elektrikli ısıtıcı",
                "last_changed": None
            },
            "ac_main": {
                "state": "OFF",
                "power_usage": 2200,  # Watt
                "type": "ac",
                "description": "Merkezi klima sistemi",
                "last_changed": None
            },
            "lights_living": {
                "state": "OFF",
                "power_usage": 60,  # Watt
                "type": "light",
                "description": "Salon LED aydınlatma",
                "last_changed": None
            },
            "smart_lock": {
                "state": "LOCKED",
                "power_usage": 0,
                "type": "lock",
                "description": "Giriş kapısı akıllı kilit",
                "last_changed": None
            },
        }

    # ----------------------------------------------------------------------

    def update_device(self, device_id: str, action: str):
        """
        Cihazın durumunu günceller.
        'ON', 'OFF', 'LOCKED', 'UNLOCKED', 'IDLE' gibi komutlar olabilir.

        Returns:
            (bool, str): Başarılı mı?, Açıklama mesajı
        """
        if device_id not in self.devices:
            return False, f"Device '{device_id}' not found."

        device = self.devices[device_id]
        previous_state = device["state"]

        # IDLE komutu = hiçbir şey yapma
        if action == "IDLE":
            return True, f"{device_id} remains in state {previous_state} (IDLE)"

        # Kilit için özel durumlar
        if device["type"] == "lock":
            if action not in ["LOCKED", "UNLOCKED"]:
                return False, f"Invalid command for lock device: {action}"
            device["state"] = action

        # Genel cihazlar
        else:
            if action not in ["ON", "OFF"]:
                return False, f"Invalid action '{action}' for device '{device_id}'"
            device["state"] = action

        # Değişim zamanı kaydet
        device["last_changed"] = datetime.now().strftime("%H:%M:%S")

        return True, f"{device_id} changed from {previous_state} to {device['state']}"

    # ----------------------------------------------------------------------

    def get_status(self):
        """
        Dashboard'lar için cihaz sözlüğünü döndürür.
        """
        return self.devices

    # ----------------------------------------------------------------------

    def get_energy_usage(self) -> int:
        """
        Şu an aktif (ON/UNLOCKED) cihazların toplam güç tüketimini hesaplar.
        """
        total = 0
        for dev_id, dev in self.devices.items():
            if dev["state"] in ["ON", "UNLOCKED"]:
                total += dev["power_usage"]
        return total
