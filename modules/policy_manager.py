class PolicyManager:
    """
    SHIA için güvenlik ve enerji tasarrufu politikalarını içeren karar doğrulama sistemi.
    """

    def __init__(self):
        # Cihazların hızlı ON/OFF yapmasını engellemek için basit bir durum tutucu
        self.last_actions = {}  # {device_id: action}
        self.power_limit = 3500  # Watt, ev için örnek güç sınırı

    # ----------------------------------------------------------------------

    def validate_action(self, action_json, sensor_data, devices=None):
        """
        AI kararını güvenlik, enerji ve mantık kurallarına göre denetler.

        Parametreler:
            action_json: {"device_id": str, "action": str, ...}
            sensor_data: sensör ölçümleri
            devices: DeviceManager içindeki cihaz veri tablosu

        Returns:
            (bool, str): Onay durumu, açıklama
        """

        device_id = action_json.get("device_id")
        action = action_json.get("action")

        # Eğer IDLE ise her zaman kabul
        if action == "IDLE":
            return True, "IDLE action allowed."

        # Eğer cihaz yoksa engelle
        if devices and device_id not in devices:
            return False, f"Device '{device_id}' does not exist."

        # Cihaz detayını al
        device = devices.get(device_id) if devices else None
        temp = sensor_data["temperature"]
        light = sensor_data["light_level"]
        occupancy = sensor_data["occupancy"]

        # ===============================================================
        # 1. GÜVENLİK KURALLARI
        # ===============================================================

        # --- Ev boşken klima ve ısıtıcı açılamaz ---
        if not occupancy:
            if device_id in ["ac_main", "heater_main"] and action == "ON":
                return False, "Cannot turn ON AC/Heater when house is empty."

            if "light" in device_id and action == "ON":
                return False, "Lights cannot be turned ON when house is empty."

            if device_id == "smart_lock" and action == "UNLOCKED":
                return False, "Front door cannot be unlocked when house is empty."

        # --- Sıcaklık tabanlı güvenlik ---
        if device_id == "heater_main" and action == "ON" and temp > 28:
            return False, "Heater cannot be turned ON above 28°C (safety rule)."

        if device_id == "ac_main" and action == "ON" and temp < 18:
            return False, "AC cannot be turned ON under 18°C (avoid overcooling)."

        # --- Işık seviyesi mantığı ---
        if "light" in device_id and action == "ON" and light > 600:
            return False, "Light is already bright enough; no need to turn ON."

        # ===============================================================
        # 2. ENERJİ TASARRUF KURALLARI
        # ===============================================================

        # Aynı cihaz bir önceki adımda farklı mod aldıysa hızlı değişimi engelle
        last_action = self.last_actions.get(device_id)
        if last_action and last_action != action:
            # Çok hızlı ON/OFF yapmayı engeller
            return False, f"Rapid switching detected on {device_id} — blocked."

        # Toplam güç sınırı kontrolü
        if devices:
            total_power = 0
            for dev_id, dev in devices.items():
                if dev["state"] in ["ON", "UNLOCKED"]:
                    total_power += dev["power_usage"]

            # Yeni açılacak cihazın gücünü ekle
            if action == "ON" and device:
                total_power += device["power_usage"]

            if total_power > self.power_limit:
                return False, (
                    f"Power limit exceeded ({total_power}W). Action blocked to save energy."
                )

        # ===============================================================
        # 3. AI KARAR MANTIĞI KONTROLÜ
        # ===============================================================

        # Cihaz türüne özel yanlış komut engelleme
        if device and device["type"] == "lock":
            if action not in ["LOCKED", "UNLOCKED"]:
                return False, "Locks only accept LOCKED / UNLOCKED commands."

        if device and device["type"] != "lock":
            if action not in ["ON", "OFF"]:
                return False, f"Invalid action '{action}' for device '{device_id}'."

        # Her şey başarılıysa kaydet ve izin ver
        self.last_actions[device_id] = action
        return True, "Action approved."

