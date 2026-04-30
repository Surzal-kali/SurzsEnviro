import re

TARGET_IP = "127.0.0.1"
TARGET_IPS = [TARGET_IP]
TARGET_RANGE = "127.0.0.1/32"
TARGET_INTERFACE = "lo"

TARGET_USERNAME = ""
TARGET_PASSWORD = ""

MSF_PASS = ""

SELF_IP_RE = "127.0.0.1"
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
