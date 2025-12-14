import random
import math
from datetime import datetime, timedelta


class SensorSimulator:
    """
    SHIA için gerçekçi bir ortam sensör simülatörü.

    Üretilen alanlar:
        - temperature (°C)
        - humidity (%)
        - light_level (lümen)
        - occupancy (bool)
        - time (datetime)
    """

    def __init__(self, start_time: datetime | None = None):
        # Başlangıç zamanı: verilmezse şu an
        self.data = {
            "time": start_time or datetime.now(),
            # Başlangıç değerleri (makul ev ortamı)
            "temperature": 22.0,
            "humidity": 45,
            "light_level": 400,
            "occupancy": True,
        }

    # ------------------------- Yardımcı Fonksiyonlar -------------------------

    def _simulate_time(self):
        """Her adımda simülasyon zamanını 30 dakika ileri al."""
        self.data["time"] += timedelta(minutes=30)

    def _base_outdoor_temp(self, hour: int) -> float:
        """
        Gün içi dış ortam sıcaklık eğrisi (basit sinus eğrisi).
        Min: gece 4–5 civarı, Max: öğlen 15–16 civarı.
        """
        # Ortalama sıcaklık ve genlik
        mean = 20   # ortalama dış sıcaklık
        amplitude = 6  # gün içi oynama

        # 0–23 saatini 0–2π aralığına map et
        # Faz kaydırma ile tepeyi 15:00 civarına getiriyoruz.
        angle = 2 * math.pi * (hour - 15) / 24
        return mean - amplitude * math.cos(angle)

    def _simulate_temperature(self):
        """
        İç ortam sıcaklığını dış sıcaklığa göre yumuşak şekilde güncelle.
        Bu modelde cihaz etkisini bilmiyoruz, sadece doğal akışı simüle ediyoruz.
        """
        hour = self.data["time"].hour
        outdoor = self._base_outdoor_temp(hour)

        indoor = self.data["temperature"]

        # İç ortam dış sıcaklığa yavaşça yaklaşsın (örneğin 0.1 oranında)
        delta = (outdoor - indoor) * 0.1

        # Küçük rastgele oynama
        noise = random.uniform(-0.9, 0.9)

        new_temp = indoor + delta + noise
        self.data["temperature"] = round(new_temp, 1)

    def _simulate_humidity(self):
        """
        Nem: 30–70 arasında dolaşsın, küçük dalgalanmalarla.
        Gece biraz artsın, gündüz biraz azalsın.
        """
        hour = self.data["time"].hour
        humidity = self.data["humidity"]

        # Gece (22–7): nem biraz artma eğiliminde
        if hour >= 22 or hour <= 7:
            trend = 0.3
        else:
            trend = -0.2

        noise = random.uniform(-1, 1)

        new_hum = humidity + trend + noise
        new_hum = max(10, min(90, new_hum))  # 30–70 aralığında tut

        self.data["humidity"] = int(new_hum)

    def _simulate_light(self):
        """
        Işık seviyesi:
            - 0–6   : Gece (çok düşük)
            - 7–10  : Sabah (yükselen)
            - 11–16 : Gündüz (yüksek)
            - 17–20 : Akşamüstü (azalan)
            - 21–23 : Gece (çok düşük)
        """
        hour = self.data["time"].hour

        if 0 <= hour < 6:
            base = random.randint(0, 50)
        elif 6 <= hour < 10:
            base = random.randint(100, 500)
        elif 10 <= hour < 17:
            base = random.randint(500, 900)
        elif 17 <= hour < 21:
            base = random.randint(150, 400)
        else:  # 21–24
            base = random.randint(0, 80)

        # Küçük noise
        noise = random.randint(-20, 20)
        light = max(0, base + noise)

        self.data["light_level"] = light

    def _simulate_occupancy(self):
        """
        Evde biri var mı?
            - Gece (22–7): yüksek ihtimalle ev dolu
            - Gündüz iş/school saatleri (9–17): daha boş olma ihtimali yüksek
        Durum her adımda tamamen random değişmiyor, küçük olasılıkla flip ediliyor.
        """
        hour = self.data["time"].hour
        occ = self.data["occupancy"]

        if 22 <= hour or hour < 7:
            # Gece: genelde evde
            change_prob = 0.05    # %5 ihtimalle değişsin
        elif 9 <= hour < 17:
            # Mesai/school saati: evde olmama olasılığı fazla
            change_prob = 0.25
        else:
            # Ara saatler (sabah/akşam)
            change_prob = 0.15

        if random.random() < change_prob:
            occ = not occ

        self.data["occupancy"] = occ

    # ------------------------------ Public API ------------------------------

    def update(self) -> dict:
        """
        Sensör verilerini bir adım günceller ve sözlük halinde döner.
        Bu fonksiyon her çağrıldığında:
            - zaman ilerler
            - sıcaklık, nem, ışık, occupancy güncellenir
        """
        self._simulate_time()
        self._simulate_temperature()
        self._simulate_humidity()
        self._simulate_light()
        self._simulate_occupancy()
        return self.data
