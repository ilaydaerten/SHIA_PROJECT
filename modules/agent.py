from datetime import datetime


class SHIADecisionAgent:
    """
    LLM KULLANMADAN çalışan, tamamen kural tabanlı SHIA ajanı.

    Görevleri:
    - Sensör verisine bakarak cihazlara karar vermek (decide)
    - Verilen kararı enerji verimliliği açısından yorumlamak (reflect)
    """

    def __init__(self):
        # İstersen ileride parametre ekleyebilirsin (konfor aralığı vb.)
        self.comfort_min = 20  # Konfor sıcaklığı alt sınırı
        self.comfort_max = 24  # Konfor sıcaklığı üst sınırı

    # ------------------------------------------------------------------ #
    #  KURAL TABANLI KARAR
    # ------------------------------------------------------------------ #

    def decide(self, sensor_data: dict) -> dict:
        """
        Sensör verisini analiz eder ve JSON benzeri bir karar objesi döner.
        HİÇBİR API veya LLM kullanılmaz.

        Dönüş formatı HER ZAMAN:
        {
            "device_id": "...",
            "action": "ON / OFF / IDLE / LOCKED / UNLOCKED",
            "reason": "string",
            "timestamp": "ISO 8601"
        }
        """

        temp = sensor_data.get("temperature", 22)
        light = sensor_data.get("light_level", 400)
        occupancy = sensor_data.get("occupancy", True)
        now = sensor_data.get("time", datetime.now())
        ts = now.isoformat()

        device_id = "none"
        action = "IDLE"
        reason = "Conditions are in a normal range; no action needed."

        # Ev boşsa: enerji tasarrufu → IDLE (kararı Policy zaten kontrol ediyor)
        if not occupancy:
            device_id = "none"
            action = "IDLE"
            reason = "House is empty; keeping system idle to save energy."

        else:
            # Sıcak → Klima aç
            if temp > 25:
                device_id = "ac_main"
                action = "ON"
                reason = f"Temperature {temp}°C is high and house occupied; turning AC ON."

            # Soğuk → Isıtıcı aç
            elif temp < 19:
                device_id = "heater_main"
                action = "ON"
                reason = f"Temperature {temp}°C is low and house occupied; turning heater ON."

            # Ortam çok karanlık → Işıkları aç
            elif light < 100:
                device_id = "lights_living"
                action = "ON"
                reason = f"Light level {light} is low and house occupied; turning living room lights ON."

            # Diğer durumlar → IDLE
            else:
                device_id = "none"
                action = "IDLE"
                reason = "Environment is comfortable and bright enough; no action needed."

        return {
            "device_id": device_id,
            "action": action,
            "reason": reason,
            "timestamp": ts,
        }

    # ------------------------------------------------------------------ #
    #  KURAL TABANLI REFLECTION (ENERJİ YORUMU)
    # ------------------------------------------------------------------ #

    def reflect(self, last_decision: dict, sensor_data: dict) -> str:
        """
        Kararı enerji verimliliği açısından yorumlar.
        LLM kullanılmaz; sadece basit kurallarla kısa bir cümle döner.
        """

        action = last_decision.get("action", "IDLE")
        device_id = last_decision.get("device_id", "none")
        temp = sensor_data.get("temperature", 22)
        light = sensor_data.get("light_level", 400)
        occupancy = sensor_data.get("occupancy", True)

        # Hiçbir şey yapılmadı
        if action == "IDLE" or device_id == "none":
            if occupancy:
                return "System stayed idle while conditions were comfortable; this is energy-efficient."
            else:
                return "House is empty and system stayed idle; this is highly energy-efficient."

        # Ev boşken cihaz açmak
        if not occupancy and action == "ON":
            return "Turning devices ON while the house is empty is not energy-efficient."

        # Konfor aralığında ısıtıcı/klima açıldıysa
        if device_id in ["ac_main", "heater_main"] and action == "ON":
            if self.comfort_min <= temp <= self.comfort_max:
                return (
                    f"Temperature is already comfortable at {temp}°C; turning {device_id} ON may waste energy."
                )
            else:
                return (
                    f"Turning {device_id} ON is reasonable at {temp}°C, but should be turned OFF once comfort range is reached."
                )

        # Işık çok yüksekken lamba açıldıysa
        if device_id.startswith("lights") and action == "ON":
            if light > 600:
                return "Turning lights ON while the environment is already bright wastes energy."
            else:
                return "Turning lights ON at this light level is acceptable."

        # Diğer tüm durumlar için genel yorum
        return "The decision seems reasonable from an energy perspective given the current conditions."
