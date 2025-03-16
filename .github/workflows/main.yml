import os
import time
import random
import sys
import json
import pygame
from colorama import init, Fore, Style
from datetime import datetime
import requests

# Cross-platform imports
import platform
if platform.system() == "Windows":
    import msvcrt
else:
    import select
    import termios
    import tty

# Initialize colorama and pygame
init(autoreset=True)
try:
    pygame.mixer.init()
except pygame.error as e:
    print(Fore.RED + f"Warning: Pygame mixer initialization failed: {e}")
    pygame = None

sound_boot = sound_event = sound_scan = sound_transmit = None
if pygame:
    try:
        sound_boot = pygame.mixer.Sound("boot.wav")
        sound_event = pygame.mixer.Sound("event.wav")
        sound_scan = pygame.mixer.Sound("scan.wav")
        sound_transmit = pygame.mixer.Sound("transmit.wav")
    except FileNotFoundError:
        print(Fore.YELLOW + "Warning: Sound files not found.")

STATE_FILE = "satellite_state.json"
NASA_API_KEY = "wImf5bgi9rhZBp3nRN1PYEmLVXSjKpQTyjaXbcog"

# Cached data
cached_epic_data = None
cached_neows_data = None
api_status = "Unknown"

def load_state():
    default_state = {"health": 100, "data_collected": 0, "missions_completed": 0, "solar_power": 100}
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            for key, value in default_state.items():
                if key not in state:
                    state[key] = value
            if "fuel" in state:
                state["solar_power"] = state.pop("fuel")
            return state
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(Fore.YELLOW + f"Warning: Could not load state file ({e}). Using default state.")
        with open(STATE_FILE, "w") as f:
            json.dump(default_state, f)
        return default_state

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except IOError as e:
        print(Fore.RED + f"Error: Failed to save state: {e}")

def fetch_epic_data(max_retries=3, delay=5):
    global cached_epic_data, api_status
    if cached_epic_data:
        return cached_epic_data
    url = f"https://api.nasa.gov/EPIC/api/natural?api_key={NASA_API_KEY}"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data:
                latest = data[0]
                cached_epic_data = {
                    "latitude": float(latest["centroid_coordinates"]["lat"]),
                    "longitude": float(latest["centroid_coordinates"]["lon"]),
                    "altitude_km": 35786,
                    "temperature_c": random.uniform(-50, 50),
                    "signal_noise_ratio": random.uniform(10, 30),
                    "timestamp": latest["date"]
                }
                print(Fore.GREEN + "Successfully fetched EPIC data.")
                log_data("EPIC data fetched successfully")
                api_status = "Online"
                return cached_epic_data
            else:
                print(Fore.YELLOW + "Warning: EPIC API returned empty data.")
                log_data("EPIC API returned empty data")
                api_status = "Partial"
                return None
        except requests.RequestException as e:
            error_msg = f"Attempt {attempt + 1}/{max_retries} - Error fetching EPIC data: {e} (Status: {response.status_code if 'response' in locals() else 'N/A'})"
            print(Fore.RED + error_msg)
            log_data(error_msg)
            api_status = "Offline"
            if attempt < max_retries - 1:
                print(Fore.YELLOW + f"Retrying in {delay} seconds...")
                time.sleep(delay)
    return None

def fetch_neows_data(max_retries=3, delay=5):
    global cached_neows_data, api_status
    if cached_neows_data:
        return cached_neows_data
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_API_KEY}"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            neos = data["near_earth_objects"][today]
            if neos:
                neo = random.choice(neos)
                cached_neows_data = {
                    "name": neo["name"],
                    "distance_km": float(neo["close_approach_data"][0]["miss_distance"]["kilometers"]),
                    "hazardous": neo["is_potentially_hazardous_asteroid"]
                }
                print(Fore.GREEN + "Successfully fetched NeoWs data.")
                log_data("NeoWs data fetched successfully")
                api_status = "Online"
                return cached_neows_data
            print(Fore.YELLOW + "Warning: No NEOs detected today.")
            log_data("No NEOs detected today")
            api_status = "Partial"
            return None
        except requests.RequestException as e:
            error_msg = f"Attempt {attempt + 1}/{max_retries} - Error fetching NeoWs data: {e} (Status: {response.status_code if 'response' in locals() else 'N/A'})"
            print(Fore.RED + error_msg)
            log_data(error_msg)
            api_status = "Offline"
            if attempt < max_retries - 1:
                print(Fore.YELLOW + f"Retrying in {delay} seconds...")
                time.sleep(delay)
    return None

def generate_telemetry():
    epic_data = fetch_epic_data()
    if epic_data:
        return epic_data
    else:
        print(Fore.YELLOW + "Using fallback telemetry due to API failure.")
        log_data("Using fallback telemetry due to API failure")
        return {
            "latitude": round(random.uniform(-90, 90), 2),
            "longitude": round(random.uniform(-180, 180), 2),
            "altitude_km": round(random.uniform(500, 600), 1),
            "temperature_c": round(random.uniform(-50, 50), 1),
            "signal_noise_ratio": round(random.uniform(10, 30), 1),
            "timestamp": datetime.now().isoformat()
        }

def log_data(message):
    try:
        with open("satellite_log.txt", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except IOError as e:
        print(Fore.RED + f"Error: Failed to write to log file: {e}")

def get_frame(health, base_frames):
    if health > 75:
        return base_frames
    elif health > 50:
        return [frame.replace("[O]", "[#]").replace("=", "-") for frame in base_frames]
    else:
        return [frame.replace("[O]", "[X]").replace("=", "*").replace("-", "~") for frame in base_frames]

def colorize_frame(frame, state):
    lines = frame.split("\n")
    colored_lines = []
    if state == "scanning":
        for line in lines:
            if "[+]" in line:
                line = line.replace("[+]", Fore.GREEN + "[+]" + Style.RESET_ALL)
            colored_lines.append(line)
    elif state == "transmitting":
        for line in lines:
            if "!!!" in line:
                line = line.replace("!!!", Fore.MAGENTA + "!!!" + Style.RESET_ALL)
            colored_lines.append(line)
    elif state == "repairing":
        for line in lines:
            if "[*]" in line:
                line = line.replace("[*]", Fore.YELLOW + "[*]" + Style.RESET_ALL)
            colored_lines.append(line)
    else:
        colored_lines = lines
    return "\n".join(colored_lines)

def get_char_non_blocking(timeout=0.1):
    if platform.system() == "Windows":
        start_time = time.time()
        while time.time() - start_time < timeout:
            if msvcrt.kbhit():
                char = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                return char
        return None
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                char = sys.stdin.read(1).lower()
                return char
            return None
        except Exception as e:
            print(Fore.RED + f"Error in get_char_non_blocking: {e}")
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def boot_up_sequence():
    boot_messages = [
        ("Initializing Sentinel Spy Satellite Systems...", Fore.CYAN),
        ("Checking power levels... OK", Fore.GREEN),
        ("Activating solar panels... OK", Fore.GREEN),
        ("Engaging high-resolution cameras... OK", Fore.GREEN),
        ("Calibrating infrared and radar sensors... OK", Fore.GREEN),
        ("Establishing communication link with NASA API... OK", Fore.GREEN),
        ("Running diagnostic checks... OK", Fore.GREEN),
        ("All systems operational. Satellite is online.", Fore.YELLOW + Style.BRIGHT),
    ]
    print(Fore.MAGENTA + Style.BRIGHT + "Initializing Sentinel Spy Satellite...")
    for message, color in boot_messages:
        print(color + message)
        if sound_boot:
            sound_boot.play()
        time.sleep(random.uniform(0.5, 1.5))
    time.sleep(1)
    print(Fore.CYAN + "\nStarting animation sequence with NASA data integration...")
    time.sleep(2)

base_frames = [
    r"""
                     _______
                  .-'       `-.
                 /             \
                |               |
                |   [O]   [O]   |
                |_______________|
               /   .---------.   \
              |   /           \   |
             /   |  [=======]  |   \
            |    |   |     |   |    |
           /     '---'-----'---'     \
          |         .--. .--.         |
          |        (    '    )        |
          |         '--' '--'         |
         /|___________________________|\
       .'  |                         |  `.
      /    |                         |    \
     |     |                         |     |
     |     |                         |     |
      \    |_________________________|    /
       \                                 /
        '.___    _____________    ___.'
             |  |             |  |
          ---|--|-------------|--|---
              |||             |||
              |||             |||
              |||             |||
            .-'  '.         .'  '-.
           (______|_________|______)
    """,
    r"""
                     _______
                  .-'       `-.
                 /             \
                |               |
                |   [ ]   [ ]   |
                |_______________|
               /   .---------.   \
              |   /           \   |
             /   |  [-------]  |   \
            |    |   |     |   |    |
           /     '---'-----'---'     \
          |         .--. .--.         |
          |        (    '    )        |
          |         '--' '--'         |
         /|___________________________|\
       .'  |                         |  `.
      /    |                         |    \
     |     |                         |     |
     |     |                         |     |
      \    |_________________________|    /
       \                                 /
        '.___    _____________    ___.'
             |  |             |  |
          ---|--|-------------|--|---
              |||             |||
              |||             |||
              |||             |||
            .-'  '.         .'  '-.
           (______|_________|______)
    """
]
scan_frames = [frame.replace("[O]", "[+]").replace("[ ]", "[+]") + "\n         ~ ~ ~ Scanning ~ ~ ~" for frame in base_frames]
transmit_frames = [frame.replace("|||", "!!!").replace("[O]", "[*]").replace("[ ]", "[*]") for frame in base_frames]
repair_frames = [frame.replace("[O]", "[*]").replace("[ ]", "[*]").replace("---", "-[*]-") for frame in base_frames]

status_messages = [
    "Scanning Earth surface with EPIC camera...",
    "Adjusting orbital trajectory... Complete",
    "Receiving NASA data packet... 100% integrity",
    "Thermal imaging online... Operational",
    "Signal strength to NASA servers: 98%... Stable",
]
events = [
    {"name": "Debris Field", "stages": [("Debris field detected ahead! (E)vade or (T)ake the hit?", Fore.YELLOW)],
     "outcomes": {"e": ("Evasion successful! Minor solar power cost.", Fore.GREEN, -5, -10), "t": ("Impact sustained! Minor damage taken.", Fore.RED, -10, 0)}},
    {"name": "Asteroid Proximity Alert (NASA)", "stages": [("Near-Earth Object detected! (I)ntercept or (G)nore?", Fore.CYAN)],
     "outcomes": {"i": ("Asteroid data intercepted! Data collected.", Fore.GREEN, 20, 0), "g": ("Asteroid ignored. No changes.", Fore.YELLOW, 0, 0)}},
]

def animation_loop(state):
    frame_speed = 0.5
    status_index = 0
    elapsed_time = 0
    cycles = 0
    scanning = False
    scan_progress = 0
    event_active = False
    current_event = None
    event_stage = 0
    transmitting = False
    transmit_progress = 0
    repairing = False
    repair_progress = 0
    last_char = None
    solar_charge_rate = 1
    last_api_call = 0

    try:
        while True:
            if scanning and scan_progress < 100:
                frames = get_frame(state["health"], scan_frames)
                current_state = "scanning"
            elif transmitting and transmit_progress < 100:
                frames = get_frame(state["health"], transmit_frames)
                current_state = "transmitting"
            elif repairing and repair_progress < 100:
                frames = get_frame(state["health"], repair_frames)
                current_state = "repairing"
            else:
                frames = get_frame(state["health"], base_frames)
                current_state = "default"

            for frame in frames:
                os.system('cls' if os.name == 'nt' else 'clear')
                colored_frame = colorize_frame(frame, current_state)
                print(Fore.CYAN + Style.BRIGHT + colored_frame)

                current_time = time.time()
                if current_time - last_api_call >= 15:
                    telemetry = generate_telemetry()
                    last_api_call = current_time
                else:
                    telemetry = generate_telemetry()  # Cached or fallback

                print(Fore.WHITE + f"\nTelemetry: Lat: {telemetry['latitude']}°, Lon: {telemetry['longitude']}°, Alt: {telemetry['altitude_km']}km")
                print(Fore.WHITE + f"Temp: {telemetry['temperature_c']}°C, SNR: {telemetry['signal_noise_ratio']}dB")
                print(Fore.WHITE + f"Last Update: {telemetry['timestamp']}")
                print(Fore.YELLOW + f"NASA API Status: {api_status}")

                print(Fore.GREEN + f"Satellite Health: {state['health']}% | Data: {state['data_collected']}MB | Solar Power: {state['solar_power']}%")
                print(Fore.GREEN + f"Missions Completed: {state['missions_completed']}")

                if scanning and scan_progress < 100:
                    print(Fore.BLUE + f"\nScan Progress: {scan_progress}%")
                    scan_progress += 10
                elif transmitting and transmit_progress < 100:
                    print(Fore.MAGENTA + f"\nTransmitting Data: {transmit_progress}%")
                    transmit_progress += 10
                    if random.random() < 0.05:
                        print(Fore.RED + "\nInterference detected! Transmission disrupted.")
                        log_data("Transmission disrupted")
                        transmitting = False
                        transmit_progress = 0
                        time.sleep(2)
                elif repairing and repair_progress < 100:
                    print(Fore.YELLOW + f"\nRepairing: {repair_progress}%")
                    repair_progress += 10
                elif event_active and current_event:
                    event_msg, event_color = current_event["stages"][event_stage]
                    if current_event["name"] == "Asteroid Proximity Alert (NASA)":
                        neo_data = fetch_neows_data()
                        if neo_data:
                            event_msg = f"NEO {neo_data['name']} detected {neo_data['distance_km']:.0f}km away! Hazardous: {neo_data['hazardous']}. (I)ntercept or (G)nore?"
                    print(event_color + f"\nEVENT: {event_msg}")
                else:
                    print(Fore.YELLOW + "\nStatus: " + status_messages[status_index])

                print(Fore.GREEN + f"Elapsed Time: {elapsed_time:.1f}s | Cycles: {cycles}")
                print(Fore.MAGENTA + "\nControls: (S)peed, (D)ecrease, (C) to scan, (T)ransmit, (R)epair, (Q)uit")

                time.sleep(frame_speed)
                elapsed_time += frame_speed
                status_index = (status_index + 1) % len(status_messages)

                if not event_active and not scanning and not transmitting and not repairing and random.random() < 0.03:
                    event_active = True
                    current_event = random.choice(events)
                    event_stage = 0
                    if sound_event:
                        sound_event.play()
                    log_data(f"EVENT: {current_event['stages'][event_stage][0]}")

                if cycles % 10 == 0:
                    log_data(f"Telemetry - Lat: {telemetry['latitude']}, Lon: {telemetry['longitude']}, Health: {state['health']}")

                char = get_char_non_blocking(timeout=frame_speed)
                if char and char != last_char:
                    last_char = char
                    if char == 'q':
                        break
                    elif char == 's':
                        frame_speed = max(0.1, frame_speed - 0.1)
                    elif char == 'd':
                        frame_speed = min(2.0, frame_speed + 0.1)
                    elif char == 'c' and not event_active and not transmitting and not repairing:
                        if not scanning and state["solar_power"] >= 5:
                            scanning = True
                            scan_progress = 0
                            state["solar_power"] -= 5
                            print(Fore.BLUE + "\nInitiating scan...")
                            if sound_scan:
                                sound_scan.play()
                            log_data("Initiated scan")
                        elif state["solar_power"] < 5:
                            print(Fore.RED + "\nInsufficient solar power")
                    elif char == 't' and not event_active and not scanning and not repairing:
                        if state["data_collected"] >= 100 and not transmitting and state["solar_power"] >= 10:
                            transmitting = True
                            transmit_progress = 0
                            state["solar_power"] -= 10
                            print(Fore.MAGENTA + "\nInitiating transmission...")
                            if sound_transmit:
                                sound_transmit.play()
                            log_data("Initiated transmission")
                        elif state["data_collected"] < 100:
                            print(Fore.RED + "\nInsufficient data")
                        elif state["solar_power"] < 10:
                            print(Fore.RED + "\nInsufficient solar power")
                    elif char == 'r' and not event_active and not scanning and not transmitting:
                        if state["health"] < 100 and state["solar_power"] >= 10 and not repairing:
                            repairing = True
                            repair_progress = 0
                            state["solar_power"] -= 10
                            print(Fore.YELLOW + "\nInitiating repairs...")
                            log_data("Initiated repairs")
                        elif state["health"] >= 100:
                            print(Fore.RED + "\nHealth at maximum")
                        elif state["solar_power"] < 10:
                            print(Fore.RED + "\nInsufficient solar power")
                    elif event_active and current_event:
                        if char in current_event["outcomes"]:
                            outcome_msg, outcome_color, outcome_effect, solar_power_effect = current_event["outcomes"][char]
                            print(outcome_color + f"\nOUTCOME: {outcome_msg}")
                            if outcome_effect < 0:
                                state["health"] = max(0, state["health"] + outcome_effect)
                            else:
                                state["data_collected"] += outcome_effect
                            state["solar_power"] = max(0, state["solar_power"] + solar_power_effect)
                            log_data(f"Event Outcome: {outcome_msg}")
                            event_active = False
                            time.sleep(2)
                        else:
                            outcome_msg, outcome_color, outcome_effect, solar_power_effect = current_event["outcomes"].get("g", ("No action taken.", Fore.YELLOW, 0, 0))
                            print(outcome_color + f"\nOUTCOME: {outcome_msg}")
                            state["data_collected"] += outcome_effect
                            state["solar_power"] = max(0, state["solar_power"] + solar_power_effect)
                            log_data(f"Event Outcome: {outcome_msg}")
                            event_active = False
                            time.sleep(2)

            if 'char' in locals() and char == 'q':
                break

            cycles += 1
            if scanning and scan_progress >= 100:
                print(Fore.GREEN + "\nScan complete!")
                state["data_collected"] += 50
                log_data("Scan completed")
                scanning = False
            if transmitting and transmit_progress >= 100:
                print(Fore.GREEN + "\nTransmission complete!")
                state["missions_completed"] += 1
                state["data_collected"] = 0
                log_data(f"Transmission completed: Mission {state['missions_completed']}")
                transmitting = False
            if repairing and repair_progress >= 100:
                print(Fore.GREEN + "\nRepairs complete!")
                state["health"] = min(100, state["health"] + 20)
                log_data("Repairs completed")
                repairing = False

            state["solar_power"] = min(100, state["solar_power"] + solar_charge_rate)
            if cycles % 10 == 0 and state["solar_power"] < 100:
                log_data(f"Solar charging: {state['solar_power']}%")

            if state["health"] <= 0 or state["solar_power"] <= 0:
                print(Fore.YELLOW + "\nWARNING: Critical levels! Regenerating...")
                state["health"] = 50
                state["solar_power"] = 50
                log_data("Emergency regeneration")
                if sound_event:
                    sound_event.play()
                time.sleep(2)

            save_state(state)

    except KeyboardInterrupt:
        print(Fore.RED + "\nTerminated by user.")
        save_state(state)
    except Exception as e:
        print(Fore.RED + f"\nCritical Error: {e}")
        save_state(state)
    finally:
        print(Fore.CYAN + "\nShutting down...")
        if pygame:
            pygame.mixer.quit()

def main():
    state = load_state()
    print(Fore.MAGENTA + Style.BRIGHT + "Welcome to Sentinel Spy Satellite System v5.0 (NASA Integrated)")
    print(Fore.YELLOW + f"Current Status - Health: {state['health']}%, Data: {state['data_collected']}MB, Solar Power: {state['solar_power']}%")
    print(Fore.YELLOW + f"Missions Completed: {state['missions_completed']}")
    print(Fore.YELLOW + "Press any key to start, or Ctrl+C to exit.")
    try:
        char = getchar()
    except KeyboardInterrupt:
        print(Fore.RED + "\nProgram aborted.")
        sys.exit(0)
    boot_up_sequence()
    animation_loop(state)
    print(Fore.GREEN + "Shutdown complete.")

def getchar():
    if platform.system() == "Windows":
        return msvcrt.getch().decode('utf-8', errors='ignore')
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
            return char
        except Exception as e:
            print(Fore.RED + f"Error in getchar: {e}")
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
