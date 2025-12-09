import os
from tabulate import tabulate
from colorama import Fore, Style

def display_dashboard(sensor_data, devices_status, last_action, system_log):
    """
    Sistem durumunu terminalde temiz bir tablo olarak gösterir.
    """
    os.system('cls' if os.name == 'nt' else 'clear') # Ekranı temizle
    
    print(Fore.CYAN + "=== SHIA: Smart Household Intelligent Agent (Group 1) ===" + Style.RESET_ALL)
    print(f"Time: {sensor_data['time'].strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Sensör Tablosu
    sensor_table = [[k, v] for k, v in sensor_data.items() if k != 'time']
    print(Fore.YELLOW + "--- ENVIRONMENT SENSORS ---" + Style.RESET_ALL)
    print(tabulate(sensor_table, headers=["Sensor", "Value"], tablefmt="fancy_grid"))

    # 2. Cihaz Durum Tablosu
    dev_table = [[k, v] for k, v in devices_status.items()]
    print(Fore.GREEN + "\n--- DEVICE STATUS ---" + Style.RESET_ALL)
    print(tabulate(dev_table, headers=["Device", "State"], tablefmt="fancy_grid"))

    # 3. Son Karar ve Log
    print(Fore.MAGENTA + "\n--- AGENT DECISION ---" + Style.RESET_ALL)
    print(f"Action: {last_action.get('action')} on {last_action.get('device_id')}")
    print(f"Reason: {last_action.get('reason')}")
    
    print(Fore.BLUE + "\n--- SYSTEM LOG (Last Entry) ---" + Style.RESET_ALL)
    if system_log:
        print(system_log[-1])
    print("\n" + "-"*50)