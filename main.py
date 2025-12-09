import time
import os
from dotenv import load_dotenv

# Modülleri içe aktar
from modules.sensors import SensorSimulator
from modules.devices import DeviceManager
from modules.agent import SHIADecisionAgent
from modules.policy_manager import PolicyManager
from dashboard import display_dashboard

# Konfigürasyon
load_dotenv() # .env dosyasını yükler

# Proje Bilgileri (Belgeden) [cite: 1]
# Group 1: İlayda Erten (Lider), Elif Yılmaz, Azra Pala, Melih Öztorun, Enes Şahin

def main():
    # 1. Başlatma (Initialization)
    sensors = SensorSimulator()
    devices = DeviceManager()
    agent = SHIADecisionAgent()
    policy = PolicyManager()
    
    logs = []

    print("SHIA System Initializing...")
    time.sleep(1)

    # 2. Ana Döngü (Main Loop)
    try:
        while True:
            # A. Veri Topla (Perceive)
            current_data = sensors.update()

            # B. Karar Ver (Reason)
            decision_json = agent.decide(current_data)

            # C. Kararı Doğrula (Policy Check)
            is_valid, msg = policy.validate_action(decision_json, current_data)

            # D. Eyleme Geç (Act)
            if is_valid:
                dev_id = decision_json.get("device_id")
                action = decision_json.get("action")
                
                if dev_id == "all":
                    # Toplu kapatma senaryosu
                    for d in devices.devices:
                        devices.update_device(d, "OFF")
                    log_msg = "All devices turned OFF via Policy."
                elif action != "IDLE":
                    _, log_msg = devices.update_device(dev_id, action)
                else:
                    log_msg = "System IDLE (No action needed)."
            else:
                log_msg = f"BLOCKED: {msg}"

            # E. Kendi Kendini Eleştir (Reflect/Feedback) [cite: 26]
            if decision_json.get("action") != "IDLE":
                review = agent.reflect(decision_json, current_data)
                log_msg += f" | REVIEW: {review}"

            # Loglama
            logs.append(f"[{current_data['time'].strftime('%H:%M')}] {log_msg}")

            # F. Görselleştir
            display_dashboard(current_data, devices.get_status(), decision_json, logs)

            # Simülasyon hızı (Her 5 saniyede bir güncelle)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nSHIA System Shutdown.")

if __name__ == "__main__":
    main()