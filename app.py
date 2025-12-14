import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Modules
from modules.sensors import SensorSimulator
from modules.devices import DeviceManager
from modules.agent import SHIADecisionAgent
from modules.policy_manager import PolicyManager


# ---------------- UI LABELS ---------------- #
DEVICE_LABELS = {
    "heater_main": "Main Heater",
    "ac_main": "Air Conditioner",
    "lights_living": "Living Room Lights",
    "smart_lock": "Smart Door Lock",
    "none": "No Device"
}

load_dotenv()

st.set_page_config(
    page_title="SHIA - Smart Home Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ---------------- SESSION STATE ---------------- #
if "initialized" not in st.session_state:
    st.session_state.sensors = SensorSimulator()
    st.session_state.devices = DeviceManager()
    st.session_state.agent = SHIADecisionAgent()
    st.session_state.policy = PolicyManager()
    st.session_state.logs = []
    st.session_state.last_decision = None

    # Manual locks (AI cannot control locked devices)
    st.session_state.manual_locks = {
        "heater_main": False,
        "ac_main": False,
        "lights_living": False,
        "smart_lock": False,
    }

    st.session_state.initialized = True

sensors = st.session_state.sensors
devices = st.session_state.devices
agent = st.session_state.agent
policy = st.session_state.policy

# ---------------- HEADER ---------------- #
st.title("🏠 SHIA – Smart Household Intelligent Agent")

st.divider()

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.header("🎮 Control Panel")

    run_step = st.button("▶ Run One Simulation Step", type="primary")

    st.markdown("---")
    st.subheader("🛠 Manual Device Control")

    device_list = ["heater_main", "ac_main", "lights_living", "smart_lock"]

    for dev_id in device_list:
        st.markdown(f"**{DEVICE_LABELS.get(dev_id)}**")

        locked = st.session_state.manual_locks.get(dev_id, False)
        if locked:
            st.success("Manual Control Active ✅ (AI will not control this device)")
        else:
            st.info("AI Control Enabled ✅")

        c1, c2, c3 = st.columns(3)

        if dev_id == "smart_lock":
            on_label, off_label = "UNLOCK", "LOCK"
            on_action, off_action = "UNLOCKED", "LOCKED"
        else:
            on_label, off_label = "ON", "OFF"
            on_action, off_action = "ON", "OFF"

        # Manual ON
        if c1.button(on_label, key=f"{dev_id}_manual_on"):
            success, msg = devices.update_device(dev_id, on_action)
            st.session_state.manual_locks[dev_id] = True

            st.session_state.logs.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "temperature": sensors.data["temperature"],
                "humidity": sensors.data["humidity"],
                "light_level": sensors.data["light_level"],
                "occupancy": sensors.data["occupancy"],
                "action": f"MANUAL: {DEVICE_LABELS.get(dev_id)} → {on_action}",
                "policy": "MANUAL",
                "device_msg": msg,
                "reflection": (
                    f"User manually set {DEVICE_LABELS.get(dev_id)} to {on_action}. "
                    "Manual lock activated."
                )
            })

        # Manual OFF
        if c2.button(off_label, key=f"{dev_id}_manual_off"):
            success, msg = devices.update_device(dev_id, off_action)
            st.session_state.manual_locks[dev_id] = True

            st.session_state.logs.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "temperature": sensors.data["temperature"],
                "humidity": sensors.data["humidity"],
                "light_level": sensors.data["light_level"],
                "occupancy": sensors.data["occupancy"],
                "action": f"MANUAL: {DEVICE_LABELS.get(dev_id)} → {off_action}",
                "policy": "MANUAL",
                "device_msg": msg,
                "reflection": (
                    f"User manually set {DEVICE_LABELS.get(dev_id)} to {off_action}. "
                    "Manual lock activated."
                )
            })

        # Release to AI
        if c3.button("Release to AI", key=f"{dev_id}_release"):
            st.session_state.manual_locks[dev_id] = False
            st.session_state.logs.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "temperature": sensors.data["temperature"],
                "humidity": sensors.data["humidity"],
                "light_level": sensors.data["light_level"],
                "occupancy": sensors.data["occupancy"],
                "action": f"MANUAL RELEASE: {DEVICE_LABELS.get(dev_id)}",
                "policy": "MANUAL",
                "device_msg": f"Manual control released for {DEVICE_LABELS.get(dev_id)}.",
                "reflection": f"AI control re-enabled for {DEVICE_LABELS.get(dev_id)}."
            })

        st.markdown("---")

    st.caption(
        "ℹ️ When a device is manually controlled, AI will not interfere "
        "until **Release to AI** is pressed."
    )

# ---------------- AI STEP ---------------- #
if run_step:
    sensor_data = sensors.update()
    sensor_data["manual_locks"] = dict(st.session_state.manual_locks)

    decision = agent.decide(sensor_data)
    is_valid, policy_msg = policy.validate_action(
        decision, sensor_data, devices.get_status()
    )

    if is_valid:
        dev_id = decision["device_id"]
        action = decision["action"]
        if dev_id != "none":
            success, device_msg = devices.update_device(dev_id, action)
        else:
            device_msg = "No device action required (IDLE)."
    else:
        device_msg = f"ACTION BLOCKED: {policy_msg}"

    reflection = agent.reflect(decision, sensor_data)

    st.session_state.logs.insert(0, {
        "time": sensor_data["time"].strftime("%H:%M:%S"),
        "temperature": sensor_data["temperature"],
        "humidity": sensor_data["humidity"],
        "light_level": sensor_data["light_level"],
        "occupancy": sensor_data["occupancy"],
        "action": (
            f"{DEVICE_LABELS.get(decision['device_id'])} → "
            f"{decision['action']}"
        ),
        "policy": policy_msg,
        "device_msg": device_msg,
        "reflection": reflection
    })

    st.session_state.last_decision = decision

# ---------------- DASHBOARD ---------------- #
st.subheader("📡 Sensor Data")
sensor = sensors.data

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature (°C)", f"{sensor['temperature']} °C")
c2.metric("Humidity (%)", f"{sensor['humidity']} %")
c3.metric("Light Level (lm)", f"{sensor['light_level']} lm")
c4.metric(
    "Occupancy",
    "OCCUPIED 👤" if sensor["occupancy"] else "EMPTY ⭕"
)



st.divider()

st.subheader("🔌 Device Status (Manual Lock Aware)")
device_rows = []
for dev_id, dev in devices.get_status().items():
    device_rows.append({
        "Device": DEVICE_LABELS.get(dev_id, dev_id),
        "State": dev["state"],
        "Power (W)": dev["power_usage"],
        "Description": dev["description"],
        "Last Changed": dev["last_changed"],
        "Manual Lock": (
            "ACTIVE" if st.session_state.manual_locks.get(dev_id, False) else "—"
        )
    })

st.dataframe(pd.DataFrame(device_rows), use_container_width=True)

total_power = devices.get_energy_usage()
st.markdown(f"### 🔋 Total Power Consumption: **{total_power} W**")

st.divider()

st.subheader("🧠 AI Decision & Policy Evaluation")
if st.session_state.last_decision:
    last = st.session_state.last_decision
    left, right = st.columns(2)

    with left:
        st.info(
            f"**AI Decision:** "
            f"{DEVICE_LABELS.get(last['device_id'])} → {last['action']}"
        )
        st.write(f"**Reason:** {last['reason']}")

    with right:
        if st.session_state.logs:
            st.success(f"**Policy Result:** {st.session_state.logs[0]['policy']}")
            st.write(f"**Reflection:** {st.session_state.logs[0]['reflection']}")
else:
    st.warning("No decision has been made yet. Click **Run One Simulation Step**.")

st.divider()

st.subheader("📜 System Logs")
if st.session_state.logs:
    st.dataframe(pd.DataFrame(st.session_state.logs), use_container_width=True)
else:
    st.info("No logs available yet.")
