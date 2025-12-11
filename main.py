import time
import os
from dotenv import load_dotenv

# Modüller
from modules.sensors import SensorSimulator
from modules.devices import DeviceManager
from modules.agent import SHIADecisionAgent
from modules.policy_manager import PolicyManager
from dashboard import display_dashboard

# -------------------------------------------------------
# Sistem Konfigürasyonu
# -------------------------------------------------------
load_dotenv()

def main():

    # 1. Nesneleri başlat
    sensors = SensorSimulator()
    devices = DeviceManager()
    agent = SHIADecisionAgent()
    policy = PolicyManager()

    logs = []

    print("SHIA System Initializing...")
    time.sleep(1)

    # ---------------------------------------------------
    # ANA DÖNGÜ
    # ---------------------------------------------------
    try:
        while True:
            # ------------------------
            # A. Sensör verilerini oku
            # ------------------------
            current_data = sensors.update()

            # ------------------------
            # B. AI kararını al
            # ------------------------
            decision_json = agent.decide(current_data)

            # ------------------------
            # C. Policy kontrolü
            # ------------------------
            is_valid, policy_msg = policy.validate_action(decision_json, current_data, devices.get_status())

            # ------------------------
            # D. Cihaza uygula
            # ------------------------
            if is_valid:
                dev_id = decision_json.get("device_id")
                action = decision_json.get("action")

                if dev_id != "none":
                    success, device_msg = devices.update_device(dev_id, action)
                else:
                    device_msg = "System IDLE — No device action taken."
            else:
                device_msg = f"BLOCKED: {policy_msg}"

            # ------------------------
            # E. Reflection (AI geri bildirim)
            # ------------------------
            reflection = agent.reflect(decision_json, current_data)

            # ------------------------
            # F. Log kaydı ekle
            # ------------------------
            log_entry = (
                f"[{current_data['time'].strftime('%H:%M:%S')}] "
                f"Decision: {decision_json} | Policy: {policy_msg} | "
                f"Device: {device_msg} | Reflection: {reflection}"
            )
            logs.append(log_entry)

            # ------------------------
            # G. Dashboard Terminal UI
            # ------------------------
            display_dashboard(
                sensor_data=current_data,
                devices_status=devices.get_status(),
                decision=decision_json,
                policy_msg=policy_msg,
                device_msg=device_msg,
                total_power=devices.get_energy_usage(),
                logs=logs
            )

            # ------------------------
            # H. Bekleme süresi (simülasyon hızı)
            # ------------------------
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nSHIA System Shutdown.")


# -----------------------------------------------------
# PROGRAM BAŞLANGICI
# -----------------------------------------------------
if __name__ == "__main__":
    main()
