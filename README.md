# Sentinel Spy Satellite System

A terminal-based simulation of a spy satellite, featuring ASCII art animations, real-time controls, and interactive events. Manage your satellite's health, solar power, and data collection while navigating challenges like debris fields and signal intercepts.

## Features
- **ASCII Art Animation**: Watch your satellite in action with dynamic frames that change based on health and actions (scanning, transmitting, repairing).
- **Real-Time Controls**: Use single-key inputs (no `Enter` required) to control speed, initiate scans, transmit data, repair the satellite, and respond to events.
- **Events and Challenges**: Encounter random events like debris fields and signal intercepts, requiring quick decisions to manage resources.
- **Solar Power Management**: Monitor and manage solar power levels, which are consumed by actions like repairs and evasion maneuvers.
- **Sound Effects (Optional)**: Add immersion with sound effects using `pygame` (requires `.wav` files).
- **Persistent State**: Satellite state (health, data, missions completed, solar power) is saved to a JSON file between sessions.

## Requirements
- **Python 3.6+**: Ensure Python is installed on your system.
- **Operating System**: Compatible with Windows, Linux, and macOS.
- **Dependencies**:
  - `colorama`: For colored terminal output.
  - `pygame`: For sound effects (optional; script works without it if sound files are unavailable).
- **Terminal/Console**: A terminal that supports ANSI escape codes for colors and ASCII art rendering (e.g., Windows Command Prompt, PowerShell, Linux Terminal, macOS Terminal).

## Installation
Follow these steps to set up and run the Sentinel Spy Satellite System.

### 1.  Download the Script

Make sure file is on desktop as satellite_animation.py

Then run in terminal cd ~/Desktop

next run python3 satellite_animation.py
