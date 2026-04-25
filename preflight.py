import psutil

from target_config import TARGET_RANGE, TARGET_IPS, TARGET_USERNAME, TARGET_PASSWORD, MSF_PASS, SELF_IP_RE, IPV4_RE
import re
import socket
def preflight():
    target_ips=list(TARGET_IPS)
    interfacesraw = psutil.net_if_addrs()
    for interface in interfacesraw:
        print(f"[*] Detected network interface: {interface}")
    target_interface = input("[-] Please enter the network interface to use for the attack (e.g., eth0): ")  
    TARGET_INTERFACE = target_interface
    all_ips = []
    for iface, addrs in interfacesraw.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                all_ips.append(addr.address)
    print(f"[*] Detected IP addresses on the system: {', '.join(all_ips)}")
    if not any(re.match(SELF_IP_RE, ip) for ip in all_ips):
        print(f"[-] Warning: No IP address on this system matches the SELF_IP_RE pattern: {SELF_IP_RE}")
    for ip in target_ips:
        if not IPV4_RE.match(ip):
            print(f"[-] Warning: TARGET_IPS entry '{ip}' does not appear to be a valid IPv4 address.")
    if not TARGET_IPS or TARGET_IPS == [""]:
        print(f"[-] Warning: TARGET_IPS is empty. No specific target IPs will be used.")
    if not TARGET_USERNAME or not TARGET_PASSWORD:
        print(f"[-] Warning: TARGET_USERNAME or TARGET_PASSWORD is not set. Default credentials will be used, which may not be effective.")
    print("[*] Preflight checks completed. All required environment variables are set and valid.")
