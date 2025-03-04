import os
import time
import random
import sys
import json
import pygame
from colorama import init, Fore, Style
from datetime import datetime

# Cross-platform imports for non-blocking input
import platform
if platform.system() == "Windows":
    import msvcrt
else:
    import select
    import termios
    import tty

# Initialize colorama for colored text
init(autoreset=True)

# Initialize pygame for sound effects
pygame.mixer.init()

# Load sound effects (replace with your own .wav files or comment out if unavailable)
try:
    sound_boot = pygame.mixer.Sound("boot.wav")
    sound_event = pygame.mixer.Sound("event.wav")
    sound_scan = pygame.mixer.Sound("scan.wav")
    sound_transmit = pygame.mixer.Sound("transmit.wav")
except FileNotFoundError:
    sound_boot = sound_event = sound_scan = sound_transmit = None

# File to store persistent state
STATE_FILE = "satellite_state.json"

# Load or initialize satellite state
def load_state():
    default_state = {"health": 100, "data_collected": 0, "missions_completed": 0, "solar_power": 100}
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            # Ensure all required keys exist, adding defaults if missing
            for key, value in default_state.items():
                if key not in state:
                    state[key] = value
            # If 'fuel' exists from an older save, convert it to 'solar_power'
            if "fuel" in state:
                state["solar_power"] = state.pop("fuel")
            return state
    except FileNotFoundError:
        with open(STATE_FILE, "w") as f:
            json.dump(default_state, f)
        return default_state

# Save satellite state
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# Generate dynamic frames based on health
def get_frame(health, base_frames):
    if health > 75:
        return base_frames
    elif health > 50:
        return [frame.replace("[O]", "[#]").replace("=", "-") for frame in base_frames]
    else:
        return [frame.replace("[O]", "[X]").replace("=", "*").replace("-", "~") for frame in base_frames]

# Function to colorize frames based on state
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

# Cross-platform function to get a single character without pressing Enter
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
            if select.select([sys.stdin], [], [], timeout)[0]:
                char = sys.stdin.read(1).lower()
                return char
            return None
        except Exception as e:
            print(f"Error in get_char_non_blocking: {e}")
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Enhanced boot-up sequence with sound
def boot_up_sequence():
    boot_messages = [
        ("Initializing Sentinel Spy Satellite Systems...", Fore.CYAN),
        ("Checking power levels... OK", Fore.GREEN),
        ("Activating solar panels... OK", Fore.GREEN),
        ("Engaging high-resolution cameras... OK", Fore.GREEN),
        ("Calibrating infrared and radar sensors... OK", Fore.GREEN),
        ("Establishing communication link... OK", Fore.GREEN),
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
    print(Fore.CYAN + "\nStarting animation sequence...")
    time.sleep(2)

# Base frames for the satellite
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

# Scanning frames: Sensors blink and add "radar waves"
scan_frames = [
    frame.replace("[O]", "[+]").replace("[ ]", "[+]") + "\n         ~ ~ ~ Scanning ~ ~ ~"
    for frame in base_frames
]

# Transmitting frames: Antennas flash
transmit_frames = [
    frame.replace("|||", "!!!").replace("[O]", "[*]").replace("[ ]", "[*]")
    for frame in base_frames
]

# Repairing frames: Add sparks and a "repair drone"
repair_frames = [
    frame.replace("[O]", "[*]").replace("[ ]", "[*]").replace("---", "-[*]-")
    for frame in base_frames
]

# Dynamic status messages and events
status_messages = [
    "Scanning sector 1... No anomalies detected",
    "Adjusting orbital trajectory... Complete",
    "Receiving data packet... 100% integrity",
    "Thermal imaging online... Operational",
    "Signal strength: 98%... Stable",
]

# Multi-stage event system
events = [
    {
        "name": "Debris Field",
        "stages": [
            ("Debris field detected ahead! (E)vade or (T)ake the hit?", Fore.YELLOW),
        ],
        "outcomes": {
            "e": ("Evasion successful! Minor solar power cost.", Fore.GREEN, -5, -10),
            "t": ("Impact sustained! Minor damage taken.", Fore.RED, -10, 0),
        }
    },
    {
        "name": "Signal Intercept",
        "stages": [
            ("Unknown signal detected! (I)ntercept or (G)nore?", Fore.CYAN),
        ],
        "outcomes": {
            "i": ("Signal intercepted! Data collected.", Fore.GREEN, 20, 0),
            "g": ("Signal ignored. No changes.", Fore.YELLOW, 0, 0),
        }
    },
]

# Generate fake telemetry data
def generate_telemetry():
    return {
        "latitude": round(random.uniform(-90, 90), 2),
        "longitude": round(random.uniform(-180, 180), 2),
        "altitude_km": round(random.uniform(500, 600), 1),
        "temperature_c": round(random.uniform(-50, 50), 1),
        "signal_noise_ratio": round(random.uniform(10, 30), 1),
    }

# Log data to a file
def log_data(message):
    with open("satellite_log.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

# Animation loop with telemetry, events, transmission, and repairs
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

    # Store the last processed character to avoid repeated inputs
    last_char = None

    try:
        while True:
            # Determine which frame set to use and adjust for health
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

                telemetry = generate_telemetry()
                print(Fore.WHITE + f"\nTelemetry: Lat: {telemetry['latitude']}°, Lon: {telemetry['longitude']}°, Alt: {telemetry['altitude_km']}km")
                print(Fore.WHITE + f"Temp: {telemetry['temperature_c']}°C, SNR: {telemetry['signal_noise_ratio']}dB")

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
                        log_data("Transmission disrupted due to interference")
                        transmitting = False
                        transmit_progress = 0
                        time.sleep(2)
                elif repairing and repair_progress < 100:
                    print(Fore.YELLOW + f"\nRepairing: {repair_progress}%")
                    repair_progress += 10
                elif event_active:
                    event_msg, event_color = current_event["stages"][event_stage]
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

                # Capture and process keypresses in real-time
                char = get_char_non_blocking(timeout=frame_speed)
                if char and char != last_char:  # Process new keypresses only
                    print(f"DEBUG: Key pressed: '{char}'")  # Debug input
                    last_char = char
                    if char == 'q':
                        break
                    elif char == 's':
                        frame_speed = max(0.1, frame_speed - 0.1)
                    elif char == 'd':
                        frame_speed = min(2.0, frame_speed + 0.1)
                    elif char == 'c' and not event_active and not transmitting and not repairing:
                        if not scanning:
                            scanning = True
                            scan_progress = 0
                            print(Fore.BLUE + "\nInitiating scan...")
                            if sound_scan:
                                sound_scan.play()
                            log_data("Initiated sector scan")
                    elif char == 't' and not event_active and not scanning and not repairing:
                        if state["data_collected"] >= 100 and not transmitting:
                            transmitting = True
                            transmit_progress = 0
                            print(Fore.MAGENTA + "\nInitiating data transmission...")
                            if sound_transmit:
                                sound_transmit.play()
                            log_data("Initiated data transmission")
                    elif char == 'r' and not event_active and not scanning and not transmitting:
                        if state["health"] < 100 and state["solar_power"] >= 10 and not repairing:
                            repairing = True
                            repair_progress = 0
                            print(Fore.YELLOW + "\nInitiating repairs...")
                            state["solar_power"] -= 10
                            log_data("Initiated repairs: Consumed 10% solar power")
                    elif event_active:
                        print(f"DEBUG: Processing event input: '{char}'")  # Debug input
                        print(f"DEBUG: Available outcomes: {current_event['outcomes'].keys()}")
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
                print(Fore.GREEN + "\nScan complete! Data collected.")
                state["data_collected"] += 50
                log_data("Scan completed: 50MB data collected")
                scanning = False
            if transmitting and transmit_progress >= 100:
                print(Fore.GREEN + "\nTransmission complete! Data sent to ground station.")
                state["missions_completed"] += 1
                state["data_collected"] = 0
                log_data(f"Transmission completed: Mission {state['missions_completed']}")
                transmitting = False
            if repairing and repair_progress >= 100:
                print(Fore.GREEN + "\nRepairs complete! Health restored.")
                state["health"] = min(100, state["health"] + 20)
                log_data("Repairs completed: Health +20%")
                repairing = False

            if state["health"] <= 0:
                print(Fore.RED + "\nCRITICAL FAILURE: Satellite health depleted!")
                log_data("Satellite failure: Health depleted")
                break
            if state["solar_power"] <= 0:
                print(Fore.RED + "\nCRITICAL FAILURE: Solar power depleted!")
                log_data("Satellite failure: Solar power depleted")
                break

        save_state(state)

    except KeyboardInterrupt:
        print(Fore.RED + "\nAnimation terminated by user.")
        save_state(state)
    except Exception as e:
        print(Fore.RED + f"\nError occurred: {e}")
        save_state(state)
    finally:
        print(Fore.CYAN + "\nShutting down animation sequence...")
        pygame.mixer.quit()

# Main program with welcome message
def main():
    state = load_state()
    print(Fore.MAGENTA + Style.BRIGHT + f"Welcome to Sentinel Spy Satellite System v5.0")
    print(Fore.YELLOW + f"Current Status - Health: {state['health']}%, Data: {state['data_collected']}MB, Solar Power: {state['solar_power']}%")
    print(Fore.YELLOW + f"Missions Completed: {state['missions_completed']}")
    print(Fore.YELLOW + "Press any key to start the boot sequence, or Ctrl+C to exit.")
    try:
        char = getchar()  # Use blocking input for the initial prompt
    except KeyboardInterrupt:
        print(Fore.RED + "\nProgram aborted.")
        sys.exit(0)

    boot_up_sequence()
    animation_loop(state)
    print(Fore.GREEN + "System shutdown complete. Goodbye.")

# Blocking getchar for main menu (since we want to wait for input here)
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
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
