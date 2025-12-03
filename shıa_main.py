import time
from modules.sensors import SensorManager
from modules.devices import DeviceManager
from modules.policy_manager import PolicyManager
from modules.agent import SmartAgent

def main():
    # Modülleri başlat
    sensors = SensorManager()
    devices = DeviceManager()
    policy = PolicyManager()
    
    # Ajanı yarat
    shia_agent = SmartAgent(sensors, devices, policy)

    print("SHIA Sistemi Başlatıldı... (Çıkış için Ctrl+C)")
    
    try:
        while True:
            # Her 5 saniyede bir simülasyon döngüsü çalıştır
            shia_agent.run_cycle()
            time.sleep(5) 
    except KeyboardInterrupt:
        print("\nSistem kapatılıyor.")

if __name__ == "__main__":
    main()