import re
import os

def env(variable_name: str, default: str = "") -> str:
    print("[*] Setting up environment variables and configurations...")
    # Here you can add logic to read from a config file, environment variables, or user input to set these values.
    value = os.getenv(variable_name, default)
    if not value:
        value = input(f"[*] Please enter a value for {variable_name} (default: '{default}'): ") or default
    print(f"[*] {variable_name} set to: {value}")
    return value
MSF_PASS = env("MSF_PASS", "Surzal123")
TARGET_USERNAME= env("TARGET_USERNAME", "")
TARGET_RANGE = env("TARGET_RANGE", "10.0.0.104/24")
TARGET_IP = env("TARGET_IP", "")
TARGET_INTERFACE = env("TARGET_INTERFACE", "wlan0")
TARGET_PASSWORD = env("TARGET_PASSWORD", "")
WORDLIST_PATH = env("WORDLIST_PATH", "./wordlist.txt")
SELF_IP_RE = "127.0.0.1"
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
