class PolicyManager:
    def evaluate(self, sensor_data):
        actions = {}
        
        # Kural 1: Sıcaklık Kontrolü
        temp = sensor_data["temperature"]
        if temp > 25.0:
            actions["AirConditioner"] = "ON"
            actions["Heater"] = "OFF"
        elif temp < 20.0:
            actions["AirConditioner"] = "OFF"
            actions["Heater"] = "ON"
        else:
            actions["AirConditioner"] = "OFF"
            actions["Heater"] = "OFF"

        # Kural 2: Işık ve Hareket Kontrolü
        if sensor_data["motion_detected"] and sensor_data["light_level"] == "Low":
            actions["Lights"] = "ON"
        else:
            actions["Lights"] = "OFF"

        # Kural 3: Güvenlik (Gece ve hareket yoksa kapıları kilitle)
        if sensor_data["time_of_day"] == "Night":
            actions["DoorLock"] = "LOCKED"
            actions["Window"] = "CLOSED"
        
        return actions