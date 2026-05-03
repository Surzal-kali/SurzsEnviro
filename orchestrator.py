
import re
from pathlib import Path
from fileshuttle import FileShuttle

class Orchestrator:
    def __init__(self):
        pass

    @staticmethod
    def _list_bin_entries(directory: str = "/bin"):
        target = Path(directory)
        if not target.is_dir():
            return []
        return sorted(entry.name for entry in target.iterdir())

    def preflight(self):
        """so the idea essentially here it to check the network enviroment, the current differences since the last time this ran. It checks imports, and dependencies as well. """
        from computerspeak import ComputerSpeak as cs
        csi = cs()
        csi.speak("[*] Starting orchestration of attack modules...")
        try:
            from netrunning import NetRunning as nr
            from metasploiting import search_modules, execute_module, list_sessions, payload_generation, get_db_status
            from catchingpackets import PacketSniffer as ps
            print("[*] Successfully imported attack modules.")
        except ImportError as e:
            print(f"[-] Error importing attack modules: {e}")
            return
        try:
            from fileshuttle import FileShuttle
            from enumeration import FileCrawler
            print("[*] Successfully imported data collection modules.")
        except ImportError as e:
            print(f"[-] Error importing data collection modules: {e}")
            return
        fsi = FileShuttle()
        bin_entries = self._list_bin_entries("/bin")
        if bin_entries:
            print(f"[*] Found {len(bin_entries)} entries in /bin for startup analysis, would you like to review? (y/n)")
            if input().lower() == "y":
                for item in bin_entries:
                    # Remove embedded null bytes to prevent subprocess errors
                    sanitized_item = item.replace('\x00', '').replace('\0', '').replace(chr(0), '')
                    fsi.append_file("bin.txt", f"\n[*] Analyzing command: {sanitized_item}")
                    if re.search(r"\b(nmap|masscan|zmap|unicornscan)\b", sanitized_item):
                        fsi.append_file("bin.txt", f"[*] Detected potential scanning command: {sanitized_item}\n")
                    elif re.search(r"\b(msfconsole|msfrpc|metasploit)\b", sanitized_item):
                        fsi.append_file("bin.txt", f"[*] Detected potential exploitation command: {sanitized_item}\n")
                    elif re.search(r"\b(curl|wget|ftp|scp|sftp)\b", sanitized_item):
                        fsi.append_file("bin.txt", f"[*] Detected potential file transfer command: {sanitized_item}\n")
                    else:
                        continue
        else:
            print("[*] No /bin entries found for startup analysis.")
        print("[*] Orchestration complete. Attack modules are ready for use based on the collected startup analysis.")




if __name__ == "__main__":
    fsi = FileShuttle() 
    ori = Orchestrator()
    ori.preflight()
    choice = input("[*] Would you like to clean the collected startup analysis? (y/n): ")
    if choice.lower() == "y":
        fsi.delete_file("rawbin.txt")  # Clear the file
        print("[*] Startup analysis cleaned.")
    else:
        print("[*] Startup analysis retained.")
