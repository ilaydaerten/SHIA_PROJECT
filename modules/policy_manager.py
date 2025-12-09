class PolicyManager:
    def __init__(self):
        pass

    def validate_action(self, action_json, sensor_data):
        """
        AI kararını güvenlik kurallarına göre denetler.
        Döner: (Onaylandı mı?, Mesaj)
        """
        device = action_json.get("device_id")
        action = action_json.get("action")
        
        # KURAL 1: Ev boşsa ısıtıcı/klima açık kalamaz (Enerji Tasarrufu)
        if sensor_data["occupancy"] == False and action in ["ON", "AC_ON", "HEATER_ON"]:
            if device in ["heater_main", "ac_main"]:
                return False, "POLICY ALERT: Cannot turn ON climate devices when house is empty."

        # KURAL 2: Çelişkili komutlar (Sıcaklık yüksekken ısıtıcı açma)
        if device == "heater_main" and action == "ON" and sensor_data["temperature"] > 28:
             return False, "POLICY ALERT: Unsafe to turn on heater when temp is > 28°C."

        return True, "Action Approved"