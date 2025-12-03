import random

class SensorManager:
    def get_data(self):
        # Simüle edilmiş veriler döndürür
        return {
            "temperature": round(random.uniform(15.0, 35.0), 1), # 15-35 derece arası
            "humidity": round(random.uniform(30.0, 70.0), 1),    # %30-70 nem
            "light_level": random.choice(["Low", "Medium", "High"]),
            "motion_detected": random.choice([True, False]),     # Hareket var/yok
            "time_of_day": random.choice(["Day", "Night"])
        }