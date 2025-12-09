import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Modüllerimizi çağırıyoruz
from modules.sensors import SensorSimulator
from modules.devices import DeviceManager
from modules.agent import SHIADecisionAgent
from modules.policy_manager import PolicyManager

# Sayfa Ayarları
st.set_page_config(
    page_title="SHIA - Group 1 Dashboard",
    page_icon="🏠",
    layout="wide"
)

# .env yükle
load_dotenv()

# --- BAŞLIK VE KENAR ÇUBUĞU ---
st.title("🏠 SHIA: Smart Household Intelligent Agent")
st.markdown("**Group 1:** İlayda Erten (Lider), Elif Yılmaz, Azra Pala, Melih Öztorun, Enes Şahin")

# --- SESSION STATE (Durum Koruma) ---
# Streamlit her tıklandığında kodu baştan çalıştırır. 
# Değişkenlerin sıfırlanmaması için session_state kullanıyoruz.

if 'initialized' not in st.session_state:
    st.session_state['sensors'] = SensorSimulator()
    st.session_state['devices'] = DeviceManager()
    st.session_state['agent'] = SHIADecisionAgent()
    st.session_state['policy'] = PolicyManager()
    st.session_state['history'] = [] # Log kayıtları
    st.session_state['initialized'] = True

# Nesneleri değişkenlere ata (kısa yazım için)
sensors = st.session_state['sensors']
devices = st.session_state['devices']
agent = st.session_state['agent']
policy = st.session_state['policy']

# --- KENAR ÇUBUĞU (KONTROLLER) ---
with st.sidebar:
    st.header("🎮 Kontrol Paneli")
    if st.button("Sistemi Bir Adım İlerlet (Step)", type="primary"):
        run_step = True
    else:
        run_step = False
        
    st.divider()
    st.info("Bu panel, SHIA projesinin simülasyon ve karar mekanizmasını görselleştirir.")

# --- ANA MANTIK (STEP FUNCTION) ---
if run_step:
    with st.spinner('Yapay Zeka Karar Veriyor...'):
        # 1. Veri Oku
        data = sensors.update()
        
        # 2. Karar Ver (AI)
        decision = agent.decide(data)
        
        # 3. Güvenlik Kontrolü (Policy)
        is_valid, msg = policy.validate_action(decision, data)
        
        # 4. Uygula
        log_entry = {}
        if is_valid:
            dev_id = decision.get("device_id")
            action = decision.get("action")
            
            if dev_id == "all":
                for d in devices.devices:
                    devices.update_device(d, "OFF")
                res = "All OFF"
            elif action != "IDLE":
                _, res = devices.update_device(dev_id, action)
            else:
                res = "IDLE"
        else:
            res = f"BLOCKED: {msg}"
            
        # 5. Review (AI Geri Bildirim)
        review = ""
        if decision.get("action") != "IDLE":
            review = agent.reflect(decision, data)
            
        # Log Kaydı
        log_entry = {
            "Time": data['time'].strftime("%H:%M"),
            "Temp": f"{data['temperature']}°C",
            "Occupancy": "Yes" if data['occupancy'] else "No",
            "Action": f"{decision.get('action')} -> {decision.get('device_id')}",
            "Review": review if review else "-"
        }
        st.session_state['history'].insert(0, log_entry) # En başa ekle

# --- GÖRSELLEŞTİRME (DASHBOARD) ---

# 1. Bölüm: Sensör Metrikleri
st.subheader("📡 Ortam Sensörleri")
col1, col2, col3, col4 = st.columns(4)

curr_data = sensors.data # Mevcut veri

with col1:
    st.metric(label="Sıcaklık", value=f"{curr_data['temperature']} °C", delta="0.5 °C")
with col2:
    st.metric(label="Nem", value=f"% {curr_data['humidity']}")
with col3:
    is_dark = curr_data['light_level'] < 100
    st.metric(label="Işık Seviyesi", value=f"{curr_data['light_level']} lm", delta_color="inverse" if is_dark else "normal")
with col4:
    occ_status = "EV DOLU 👤" if curr_data['occupancy'] else "EV BOŞ ⭕"
    st.metric(label="Hareket", value=occ_status)

st.divider()

# 2. Bölüm: Cihaz Durumları ve AI Kararı
col_devices, col_ai = st.columns([1, 2])



with col_devices:
    st.subheader("🔌 Cihaz Durumları")
    # Cihazları DataFrame olarak göster
    dev_status = devices.get_status()
    df_dev = pd.DataFrame(list(dev_status.items()), columns=["Cihaz", "Durum"])
    
    # Renkli gösterme fonksiyonu
    def color_status(val):
        color = 'green' if val == 'ON' or val == 'LOCKED' else 'red'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_dev.style.applymap(color_status, subset=['Durum']), use_container_width=True)

with col_ai:
    st.subheader("🧠 SHIA Yapay Zeka Karar Modülü")
    if len(st.session_state['history']) > 0:
        last_log = st.session_state['history'][0]
        st.info(f"Son İşlem: **{last_log['Action']}**")
        if last_log['Review'] != "-":
            st.success(f"Performans Analizi (Reflection): {last_log['Review']}")
    else:
        st.warning("Henüz simülasyon başlatılmadı. Yandaki butona basın.")

# 3. Bölüm: Geçmiş Kayıtlar (Loglar)
st.subheader("📜 Sistem Geçmişi (Logs)")
if st.session_state['history']:
    st.dataframe(pd.DataFrame(st.session_state['history']), use_container_width=True)