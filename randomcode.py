from computerspeak import ComputerSpeak as cs
from pymetasploit3.msfrpc import MsfRpcClient
from metasploiting import search_modules, execute_module, list_sessions, get_db_status, payload_generation
from netrunning import NetRunning as nr
from whatprocess import WhatProcess as wp
from fileshuttle import FileShuttle as fs
from enumeration import FileCrawler as fc
from shellwalking import ShellWalker as sw
from catchingpackets import PacketSniffer as ps
from target_config import MSF_PASS, TARGET_IP, TARGET_INTERFACE, TARGET_USERNAME, TARGET_PASSWORD, TARGET_RANGE, SELF_IP_RE, IPV4_RE, WORDLIST_PATH
from conquer import Tenfold as tf
from orchestrator import Orchestrator as Or
from dacore import CoreClass as cc
import re
import time
from publicface import publicface as Pf

def somerandomcode1():
    pfi = Pf()
    cci = cc()
    psi = ps()
    swi = sw()
    fci = fc()
    wpi = wp()
    nri = nr()
    csi = cs()
    tfi = tf()
    ori = Or()
    print("[*] Welcome Home")
    print("[*] Starting the conquest of the target network...")
    earth=pfi.get_request(f"http://{TARGET_IP}/", headers={'Host': 'earth.local'})
    print(f"[*] Response from target: {earth}")  # Print the first 100 characters of the response for verification
    print("[*] Conquest complete. Check the logs and reports for details.")
    nri.run_nmap_script(TARGET_IP, "http-enum")
if __name__ == "__main__":  
    somerandomcode1()
    fsi = fs()
    cleanup = input("[*] Do you want to clean up old files from previous runs? (y/n): ")
    if cleanup.lower() == "y":
        fsi.delete_file("bin.txt")
        fsi.delete_file("rawbin.txt")
        print("[*] Old files cleaned up.")