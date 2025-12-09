import random
from datetime import datetime, timedelta

class SensorSimulator:
    def __init__(self):
        # Başlangıç değerleri
        self.data = {
            "temperature": 22.0,  # Derece
            "humidity": 45,       # Yüzde
            "light_level": 500,   # Lümen
            "occupancy": True,    # Evde biri var mı?
            "time": datetime.now()
        }

    def update(self):
        """Sensör verilerini rastgele değiştirerek simülasyon yapar."""
        # Saati ilerlet
        self.data["time"] += timedelta(minutes=30)
        
        # Sıcaklık dalgalanması (-1 ile +1 arasında)
        self.data["temperature"] += random.uniform(-1, 1)
        self.data["temperature"] = round(self.data["temperature"], 1)

        # Işık seviyesi (Gündüz/Gece simülasyonu basitçe)
        hour = self.data["time"].hour
        if 7 <= hour <= 18:
            self.data["light_level"] = random.randint(400, 900)
        else:
            self.data["light_level"] = random.randint(0, 100)

        # Hareket durumu (Rastgele değişebilir)
        if random.random() > 0.8: # %20 ihtimalle durum değişir
            self.data["occupancy"] = not self.data["occupancy"]

        return self.data