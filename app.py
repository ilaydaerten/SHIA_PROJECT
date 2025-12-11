import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Modüller
from modules.sensors import SensorSimulator
from modules.devices import DeviceManager
from modules.agent import SHIADecisionAgent
from modules.policy_manager import PolicyManager

# -----------------------------------------------------------------
# STREAMLIT SAYFA AYARLARI
# -----------------------------------------------------------------
st.set_page_config(
    page_title="SHIA - Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

load_dotenv()

# -----------------------------------------------------------------
# SESSION STATE BAŞLATMA
# -----------------------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.sensors = SensorSimulator()
    st.session_state.devices = DeviceManager()
    st.session_state.agent = SHIADecisionAgent()
    st.session_state.policy = PolicyManager()
    st.session_state.logs = []
    st.session_state.last_decision = None
    st.session_state.initialized = True

sensors = st.session_state.sensors
devices = st.session_state.devices
agent = st.session_state.agent
policy = st.session_state.policy

# -----------------------------------------------------------------
# BAŞLIK
# -----------------------------------------------------------------
st.title("🏠 SHIA: Smart Household Intelligent Agent")
st.markdown("### **Group 1:** İlayda Erten (Lider) • Elif Yılmaz • Azra Pala • Melih Öztorun • Enes Şahin")
st.divider()

# -----------------------------------------------------------------
# SIDEBAR - KONTROL PANELİ
# -----------------------------------------------------------------
with st.sidebar:
    st.header("🎮 Kontrol Paneli")
    run_step = st.button("Sistemi Bir Adım İlerlet (STEP)", type="primary")

    st.markdown("---")
    st.info("Bu panel, SHIA'nın sensör verisini okuyup karar verme sürecini başlatır.")


# -----------------------------------------------------------------
# STEP ÇALIŞTIRMA
# -----------------------------------------------------------------
if run_step:
    # 1. Sensör güncelle
    sensor_data = sensors.update()

    # 2. AI Kararı
    decision = agent.decide(sensor_data)

    # 3. Policy kontrolü
    is_valid, policy_msg = policy.validate_action(decision, sensor_data, devices.get_status())

    # 4. Cihaz üzerinde uygula
    if is_valid:
        dev_id = decision["device_id"]
        action = decision["action"]

        if dev_id != "none":
            success, device_msg = devices.update_device(dev_id, action)
        else:
            device_msg = "No device action required (IDLE)."
    else:
        device_msg = f"ACTION BLOCKED: {policy_msg}"

    # 5. Reflection (AI değerlendirme)
    reflection = agent.reflect(decision, sensor_data)

    # 6. Log ekle
    log_entry = {
        "time": sensor_data["time"].strftime("%H:%M:%S"),
        "temperature": sensor_data["temperature"],
        "humidity": sensor_data["humidity"],
        "light_level": sensor_data["light_level"],
        "occupancy": sensor_data["occupancy"],
        "action": f"{decision['device_id']} → {decision['action']}",
        "policy": policy_msg,
        "device_msg": device_msg,
        "reflection": reflection
    }

    st.session_state.logs.insert(0, log_entry)
    st.session_state.last_decision = decision


# -----------------------------------------------------------------
# DASHBOARD – 1: Sensör Verileri
# -----------------------------------------------------------------
st.subheader("📡 Sensör Verileri")

sensor = sensors.data

col1, col2, col3, col4 = st.columns(4)

col1.metric("Sıcaklık (°C)", f"{sensor['temperature']}°C")
col2.metric("Nem (%)", f"{sensor['humidity']}%")
col3.metric("Işık (lm)", f"{sensor['light_level']} lm")
col4.metric("Hareket", "EV DOLU 👤" if sensor["occupancy"] else "EV BOŞ ⭕")

st.divider()

# -----------------------------------------------------------------
# DASHBOARD – 2: Cihaz Durumları
# -----------------------------------------------------------------
st.subheader("🔌 Cihaz Durumları")

device_data = []
for dev_id, dev in devices.get_status().items():
    device_data.append({
        "Cihaz": dev_id,
        "Durum": dev["state"],
        "Güç (W)": dev["power_usage"],
        "Açıklama": dev["description"],
        "Son Değişim": dev["last_changed"],
    })

df_devices = pd.DataFrame(device_data)

st.dataframe(df_devices, use_container_width=True)

total_power = devices.get_energy_usage()
st.markdown(f"### 🔋 Toplam Güç Tüketimi: **{total_power} W**")

st.divider()

# -----------------------------------------------------------------
# DASHBOARD – 3: AI Kararı & Policy Durumu
# -----------------------------------------------------------------
st.subheader("🧠 Yapay Zeka Kararı ve Güvenlik Analizi")

if st.session_state.last_decision:
    last = st.session_state.last_decision

    colA, colB = st.columns(2)

    with colA:
        st.info(f"**AI Kararı:** {last['device_id']} → {last['action']}")
        st.write(f"**Reason:** {last['reason']}")

    with colB:
        if st.session_state.logs:
            st.success(f"**Policy:** {st.session_state.logs[0]['policy']}")
            st.write(f"**Reflection:** {st.session_state.logs[0]['reflection']}")
else:
    st.warning("Henüz bir karar üretilmedi. STEP butonuna basın.")

st.divider()

# -----------------------------------------------------------------
# DASHBOARD – 4: LOG TABLOSU
# -----------------------------------------------------------------
st.subheader("📜 Sistem Logları")

if st.session_state.logs:
    df_logs = pd.DataFrame(st.session_state.logs)
    st.dataframe(df_logs, use_container_width=True)
else:
    st.info("Henüz log kaydı yok.")
