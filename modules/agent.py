from datetime import datetime


class SHIADecisionAgent:
    """
    OFFLINE SHIA Agent (LLM yok)
    - Memory (history)
    - Trend analysis
    - Rule-based decision making
    - Manual lock awareness (kullanıcı kilitlediyse dokunmaz)
    """

    def __init__(self):
        self.memory = {
            "temperature": [],
            "light_level": [],
            "occupancy": [],
        }
        self.memory_limit = 20

    def _trend(self, values):
        if len(values) < 2:
            return 0.0
        diffs = [values[i] - values[i - 1] for i in range(1, len(values))]
        return sum(diffs) / len(diffs)

    def _push(self, key, value):
        self.memory[key].append(value)
        if len(self.memory[key]) > self.memory_limit:
            self.memory[key].pop(0)

    def decide(self, sensor_data: dict) -> dict:
        temp = float(sensor_data.get("temperature", 22.0))
        light = int(sensor_data.get("light_level", 400))
        occupancy = bool(sensor_data.get("occupancy", True))
        ts = datetime.now().isoformat()

        # manual locks: {"heater_main": True/False, ...}
        manual_locks = sensor_data.get("manual_locks", {}) or {}

        # memory update
        self._push("temperature", temp)
        self._push("light_level", light)
        self._push("occupancy", occupancy)

        temp_trend = self._trend(self.memory["temperature"])
        light_trend = self._trend(self.memory["light_level"])

        device_id = "none"
        action = "IDLE"
        base_reason = "No action required."

        if not occupancy:
            device_id = "none"
            action = "IDLE"
            base_reason = "House is empty; keeping system idle to save energy."
        else:
            # Trend-aware heating/cooling/lighting
            if temp < 19 or (temp < 21 and temp_trend < -0.30):
                device_id = "heater_main"
                action = "ON"
                base_reason = "Temperature is low or decreasing rapidly; turning heater ON proactively."

            elif temp > 25 or (temp > 24 and temp_trend > 0.30):
                device_id = "ac_main"
                action = "ON"
                base_reason = "Temperature is high or rising rapidly; turning AC ON proactively."

            elif light < 120 or (light < 180 and light_trend < -15):
                device_id = "lights_living"
                action = "ON"
                base_reason = "Light level is low or decreasing; turning living room lights ON."

            else:
                device_id = "none"
                action = "IDLE"
                base_reason = "Environmental conditions are stable; no action needed."

        # ✅ Manual lock enforcement (kritik)
        if device_id != "none" and manual_locks.get(device_id, False):
            locked_reason = (
                f"User manual control is ACTIVE for '{device_id}'. "
                f"AI will not change this device until manual lock is released."
            )
            device_id = "none"
            action = "IDLE"
            base_reason = locked_reason

        reason = (
            "Environment analysis:\n"
            f"- Temperature: {temp:.1f}°C (trend {temp_trend:+.2f}°C/step)\n"
            f"- Light level: {light} (trend {light_trend:+.1f}/step)\n"
            f"- Occupancy: {'occupied' if occupancy else 'empty'}\n\n"
            "Decision reasoning:\n"
            f"- {base_reason}"
        )

        return {
            "device_id": device_id,
            "action": action,
            "reason": reason,
            "timestamp": ts,
        }

    def reflect(self, last_decision: dict, sensor_data: dict) -> str:
        action = last_decision.get("action", "IDLE")
        device_id = last_decision.get("device_id", "none")
        temp = float(sensor_data.get("temperature", 22.0))
        occupancy = bool(sensor_data.get("occupancy", True))

        if action == "IDLE" or device_id == "none":
            # manuel kilit bilgisi varsa daha açıklayıcı yaz
            manual_locks = sensor_data.get("manual_locks", {}) or {}
            locked = [d for d, v in manual_locks.items() if v]
            if locked:
                return f"AI stayed idle because manual control is active for: {', '.join(locked)}."
            return "System stayed idle; likely energy-efficient."

        if action == "ON" and not occupancy:
            return "Turning devices ON while house is empty is not energy-efficient."

        if action == "ON" and 20 <= temp <= 24:
            return "Turning device ON in a comfortable temperature range may waste energy."

        return "Decision seems reasonable given the current conditions."
