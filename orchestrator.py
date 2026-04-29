import psutil
import re
import socket

from target_config import TARGET_RANGE
def preflight():
    print("[*] Starting orchestration of attack modules...")
    try:
        from netrunning import NetRunning as nr
        from metasploiting import search_modules, execute_module, list_sessions, payload_generation, get_db_status
        from catchingpackets import PacketSniffer as ps
        from computerspeak import ComputerSpeak as cs
        print("[*] Successfully imported attack modules.")

    except ImportError as e:
        print(f"[-] Error importing attack modules: {e}")
        return
    try:
        from shellwalking import ShellWalker
        from fileshuttle import FileShuttle
        from enumeration import FileCrawler
        print("[*] Successfully imported data collection modules.")
    except ImportError as e:
        print(f"[-] Error importing data collection modules: {e}")
        return
    shi = ShellWalker()
    fsi = FileShuttle()
    fci = FileCrawler()
    past_history= fsi.file_read(file_path="shell_history.txt")
    print("[*] Starting shell history collection...")
    new_history = shi.crabwalk()
    if new_history != past_history:
        print("[*] New shell history found, would you like to review? (y/n)")   
        if input ().lower() == "y":
            print("\n".join(new_history))
        else:
            fsi.append_file("shell_history.txt", content=f"{new_history}\n")
    else:
        print("[*] No new shell history found.")
    for item in new_history:
        print(f"[*] Analyzing command: {item}")
        if re.search(r"\b(nmap|masscan|zmap|unicornscan)\b", item):
            print(f"[*] Detected potential scanning command: {item}")
            # Here you could add logic to analyze the command further, extract targets, or correlate with other data sources.
        elif re.search(r"\b(msfconsole|msfrpc|metasploit)\b", item):
            print(f"[*] Detected potential exploitation command: {item}")
            # Here you could add logic to analyze the command further, extract module names, or correlate with other data sources.
        elif re.search(r"\b(curl|wget|ftp|scp|sftp)\b", item):
            print(f"[*] Detected potential file transfer command: {item}")
            # Here you could add logic to analyze the command further, extract URLs or file paths, or correlate with other data sources.
        else:
            print(f"[*] No specific attack pattern detected in command: {item}")
    print("[*] Orchestration complete. Attack modules are ready for use based on the collected shell history and analysis.")


def network_check():
    try:
        from netrunning import NetRunning as nr
        from catchingpackets import PacketSniffer as ps
        print("[*] Successfully imported network modules.")
    except ImportError as e:
        print(f"[-] Error importing network modules: {e}")
        return
    nri= nr()
    active_hosts = nri.run_nmap_script(target_ip=TARGET_RANGE, script_name="ping")
    from fileshuttle import FileShuttle as fs
    fsi = fs()
    if fsi.file_read(file_path="active_hosts.txt") != str(active_hosts):
        fsi.append_file("active_hosts.txt", f"{active_hosts}\n")
        return active_hosts
    else:
        fsi.create_file(file_path="active_hosts.txt", content=F"{active_hosts}\n")
        fsi.append_file("active_hosts.txt", content=F"{active_hosts}\n")
        return active_hosts


def target_practice(active_hosts):
    print("[*] Starting target practice module...")
    from netrunning import NetRunning as nr
    nri= nr()
    for host in active_hosts:
        print(f"[*] Analyzing target: {host}")
        safetycheck= input(f"[*] Do you want to run reconnaissance on {host}? (y/n) ")
        if safetycheck.lower() == "y":
            print(f"[*] Running reconnaissance on {host}...")
        

        else:
            print(f"[*] Skipping reconnaissance on {host}.")            
    print("[*] Target practice complete. You can now use the collected information for further analysis or exploitation activities.")





if __name__ == "__main__":
    preflight()
    target_practice(network_check())
