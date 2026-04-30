
import re
from netrunning import NetRunning as nr
from target_config import TARGET_RANGE, TARGET_USERNAME, WORDLIST_PATH

class Orchestrator:
    def __init__(self):
        pass

    def preflight(self):
        ###to do !!!! fix shell history so it reads the contents of /bin instead of reitterating the past *since existent* history i.e. fix crabwalk
        """so the idea essentially here it to check the network enviroment, the current differences since the last time this ran. It checks imports, and dependencies as well. """
        from computerspeak import ComputerSpeak as cs
        csi = cs()
        csi.speak("[*] Starting orchestration of attack modules...")
        try:
            from netrunning import NetRunning as nr
            from metasploiting import search_modules, execute_module, list_sessions, payload_generation, get_db_status
            from catchingpackets import PacketSniffer as ps
            csi.speak("[*] Successfully imported attack modules.")
        except ImportError as e:
            csi.speak(f"[-] Error importing attack modules: {e}")
            return
        try:
            from shellwalking import ShellWalker
            from fileshuttle import FileShuttle
            from enumeration import FileCrawler
            csi.speak("[*] Successfully imported data collection modules.")
        except ImportError as e:
            csi.speak(f"[-] Error importing data collection modules: {e}")
            return
        shi = ShellWalker()
        fsi = FileShuttle()
        csi.speak("[*] Starting shell history collection...")
        new_history = fsi.list_directory("/bin")  # Example path, adjust as needed
        if new_history:
            print("[*] New shell history found, would you like to review? (y/n)")
            if input().lower() == "y":
                for item in new_history:
                    # Remove embedded null bytes to prevent subprocess errors
                    sanitized_item = item.replace('\x00', '').replace('\0', '').replace(chr(0), '')
                    fsi.append_file("rawbin.txt", f"[*] Analyzing command: {sanitized_item}")
                    if re.search(r"\b(nmap|masscan|zmap|unicornscan)\b", sanitized_item):
                        fsi.append_file("rawbin.txt", f"[*] Detected potential scanning command: {sanitized_item}\n")
                    elif re.search(r"\b(msfconsole|msfrpc|metasploit)\b", sanitized_item):
                        fsi.append_file("rawbin.txt", f"[*] Detected potential exploitation command: {sanitized_item}")
                    elif re.search(r"\b(curl|wget|ftp|scp|sftp)\b", sanitized_item):
                        fsi.append_file("rawbin.txt", f"[*] Detected potential file transfer command: {sanitized_item}\n")
                    else:
                        fsi.append_file("rawbin.txt", f"[*] No specific attack pattern detected in command: {sanitized_item}\n")
        else:
            csi.speak("[*] No new shell history found.")
        csi.speak("[*] Orchestration complete. Attack modules are ready for use based on the collected shell history and analysis.")



if __name__ == "__main__":
    ori = Orchestrator()
    ori.preflight()