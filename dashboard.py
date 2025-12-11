import os
from tabulate import tabulate
from colorama import Fore, Style


def display_dashboard(
    sensor_data: dict,
    devices_status: dict,
    decision: dict,
    policy_msg: str,
    device_msg: str,
    total_power: int,
    logs: list
):
    """
    SHIA terminal dashboard (main.py için).
    Yeni cihaz modeli + policy sistemi + gelişmiş agent için güncellendi.
    """

    # Ekranı temizle
    os.system("cls" if os.name == "nt" else "clear")

    print(Fore.CYAN + "=== SHIA: Smart Household Intelligent Agent (Terminal Dashboard) ===" + Style.RESET_ALL)
    print(f"Time: {sensor_data['time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # ---------------------------------------------------------
    # 1. Sensör Tablosu
    # ---------------------------------------------------------
    sensor_table = [
        ["Temperature (°C)", sensor_data["temperature"]],
        ["Humidity (%)", sensor_data["humidity"]],
        ["Light Level (lm)", sensor_data["light_level"]],
        ["Occupancy", "YES" if sensor_data["occupancy"] else "NO"],
    ]

    print(Fore.YELLOW + "--- ENVIRONMENT SENSORS ---" + Style.RESET_ALL)
    print(tabulate(sensor_table, headers=["Sensor", "Value"], tablefmt="fancy_grid"))
    print()

    # ---------------------------------------------------------
    # 2. Cihaz Durumları
    # ---------------------------------------------------------
    device_table = []
    for dev_id, dev in devices_status.items():
        device_table.append([
            dev_id,
            dev["state"],
            dev["power_usage"],
            dev["description"],
            dev["last_changed"] or "-"
        ])

    print(Fore.GREEN + "--- DEVICE STATUS ---" + Style.RESET_ALL)
    print(tabulate(
        device_table,
        headers=["Device", "State", "Power (W)", "Description", "Last Changed"],
        tablefmt="fancy_grid"
    ))
    print()

    # ---------------------------------------------------------
    # 3. AI Kararı
    # ---------------------------------------------------------
    print(Fore.MAGENTA + "--- AI DECISION ---" + Style.RESET_ALL)
    print(f"Device   : {decision.get('device_id')}")
    print(f"Action   : {decision.get('action')}")
    print(f"Reason   : {decision.get('reason')}")
    print()

    # ---------------------------------------------------------
    # 4. Policy Sonucu
    # ---------------------------------------------------------
    print(Fore.BLUE + "--- POLICY CHECK ---" + Style.RESET_ALL)
    print(policy_msg)
    print()

    # ---------------------------------------------------------
    # 5. Uygulama Sonucu (DeviceManager geri bildirimi)
    # ---------------------------------------------------------
    print(Fore.CYAN + "--- DEVICE UPDATE RESULT ---" + Style.RESET_ALL)
    print(device_msg)
    print()

    # ---------------------------------------------------------
    # 6. Enerji Tüketimi
    # ---------------------------------------------------------
    print(Fore.YELLOW + f"Total Power Consumption: {total_power} W" + Style.RESET_ALL)
    print()

    # ---------------------------------------------------------
    # 7. Log
    # ---------------------------------------------------------
    print(Fore.WHITE + "--- LAST LOG ENTRY ---" + Style.RESET_ALL)
    if logs:
        print(logs[-1])
    else:
        print("No logs yet.")
    print("\n" + "-" * 80 + "\n")
