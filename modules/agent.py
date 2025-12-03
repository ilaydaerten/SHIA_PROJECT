import pandas as pd
import datetime
import os

class SmartAgent:
    def __init__(self, sensors, devices, policy):
        self.sensors = sensors
        self.devices = devices
        self.policy = policy
        self.log_file = "data/logs.csv"
        
        # Log dosyası yoksa başlıkları oluştur
        if not os.path.exists(self.log_file):
            df = pd.DataFrame(columns=["Timestamp", "Sensors", "Actions"])
            df.to_csv(self.log_file, index=False)

    def run_cycle(self):
        print("\n--- SHIA Agent Döngüsü Başlıyor ---")
        
        # 1. Gözlemle (Observe)
        data = self.sensors.get_data()
        print(f"Sensör Verisi: {data}")

        # 2. Karar Ver (Decide)
        recommended_actions = self.policy.evaluate(data)
        
        # 3. Uygula (Act)
        for device, action in recommended_actions.items():
            current_status = self.devices.devices.get(device)
            if current_status != action: # Sadece durum değişecekse işlem yap
                self.devices.update_device(device, action)
        
        # 4. Öğren/Kaydet (Log/Learn)
        self.log_action(data, recommended_actions)
        print("Cihaz Durumları:", self.devices.get_status())

    def log_action(self, sensors, actions):
        # Basit bir CSV loglama (İleride ML için veri seti olacak)
        new_row = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Sensors": str(sensors),
            "Actions": str(actions)
        }
        # Pandas ile CSV'ye ekleme
        df = pd.DataFrame([new_row])
        df.to_csv(self.log_file, mode='a', header=False, index=False)