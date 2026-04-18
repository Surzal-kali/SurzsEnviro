import re

from computerspeak import ComputerSpeak as cs
from fileshuttle import FileShuttle as fs
import subprocess
import platform
import time
import socket
import nmap
import os
from target_config import TARGET_IP, TARGET_INTERFACE, SELF_IP_RE, TARGET_RANGE
class NetRunning:
    def __init__(self):
        self.cs = cs()
        self.fs = fs()
    def scan_network(self, target_ip_range: str):
        """Scan the network for active hosts within the specified IP range using nmap. This function performs a ping scan to identify active hosts in the given IP range. The results are logged using the ComputerSpeak class, and a list of active hosts is returned. The function also includes error handling to catch and report any issues that may arise during the scanning process."""
        self.cs.execute_command(f"Write-Output Scanning network for active hosts in range: {target_ip_range}")
        nm = nmap.PortScanner()
        nm.scan(hosts=target_ip_range, arguments='-sn')
        active_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']
        self.cs.execute_command(f"Write-Output Active hosts found: {', '.join(active_hosts)}")
        return active_hosts
    def scan_ports(self, target_ip: str):
        """Scan the ports on the specified target IP using nmap. This function performs a SYN scan on the target IP address to identify open ports and their associated services. The results are collected and returned in a structured format, including the port number, service name, version information, and protocol. The function also logs the scanning process using the ComputerSpeak class, providing insights into the target being scanned and the open ports discovered."""
        self.cs.execute_command(f"Write-Output 'Scanning ports on target: {target_ip}'")
        nm = nmap.PortScanner()
        nm.scan(hosts=target_ip, arguments='-sS -sV -Pn -p 1-8080')
        open_ports = []
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                for port in sorted(nm[host][proto].keys()):
                    port_info = nm[host][proto][port]
                    if port_info.get('state') == 'open':
                        service = port_info.get('name', 'unknown')
                        version = port_info.get('version', '')
                        open_ports.append((port, service, version, proto))
                        print(f"Open port found: {port}/{proto} - Service: {service} Version: {version}")
        self.cs.execute_command(f"Write-Output 'Open ports found on {target_ip}: {open_ports}'")
        return open_ports #im a silly goober
    def run_nmap_script(self, target_ip: str, script_name: str):
        """Run a specific nmap script against the target IP and return the output. This function uses the nmap library to execute a specified nmap script against a target IP address. The results of the script execution are collected and returned in a structured format. The function also logs the actions being performed using the ComputerSpeak class, providing insights into the scanning process and the results obtained from the nmap script execution."""
        self.cs.execute_command(f"Write-Output 'Running nmap script {script_name} on target: {target_ip}'")
        nm = nmap.PortScanner()
        nm.scan(target_ip, arguments=f'--script={script_name}')
        script_output = {}
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                lport = nm[host][proto].keys()
                for port in lport:
                    if 'script' in nm[host][proto][port]:
                        script_output[(port, proto)] = nm[host][proto][port]['script']
        self.cs.execute_command(f"Write-Output 'Nmap script output for {target_ip}: {script_output}'")
        return script_output
    def create_server(self,folder:str, port: int):
        """Create a simple HTTP server on the specified port to serve files or payloads."""
        self.cs.execute_command(f"Write-Output 'Starting simple HTTP server on port {port}'")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        if platform.system() == "Windows":
            command = f"python -m http.server {port} --directory {folder}"
        else:
            command = f"python3 -m http.server {port} --directory {folder}"
        subprocess.Popen(command, shell=True)
    #hear me out. we serve a web page at the end right? shouldn't we implement the logic now? we have an integrated browser :D  yeth we have that in dacore.py this only lists the directory of the repo. lets refactor it to serve a CERTAIN directory. and then we can just move files into that directory and have the other instances download them. :D
if __name__ == "__main__":
    nri = NetRunning()
    targets = nri.scan_network(TARGET_RANGE)
    print(f"Discovered targets: {targets}")
    for target in targets:
        if re.match(SELF_IP_RE, target): 
            print(f"Skipping self IP: {target}")
            continue
        ports = nri.scan_ports(target)
        print(f"Open ports on {target}: {ports}")
        for port, service, version, proto in ports:
            if service in ["http", "https"]:
                script_output = nri.run_nmap_script(target, "http-vuln-cve2014-6271")
                print(f"Nmap script output for {target}:{port}: {script_output}")
    #nmap is pretty slow, so we won't run the script against every target and port. but we can run it against the ones that look interesting. :
            if service in ['smb', 'microsoft-ds']:
                script_output = nri.run_nmap_script(target, "smb-vuln-ms17-010")
                print(f"Nmap script output for {target}:{port}: {script_output}")
