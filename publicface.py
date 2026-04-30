import socket
import time
from computerspeak import ComputerSpeak as cs
from metasploiting import search_modules, execute_module, list_sessions, get_db_status, payload_generation
from pymetasploit3.msfrpc import MsfRpcClient as Msf
from netrunning import NetRunning as nr
from whatprocess import WhatProcess as wp
from fileshuttle import FileShuttle as fs
from enumeration import FileCrawler as fc
from shellwalking import ShellWalker as sw
from catchingpackets import PacketSniffer as ps
from target_config import MSF_PASS, TARGET_IP, TARGET_INTERFACE, TARGET_USERNAME, TARGET_PASSWORD, TARGET_RANGE, SELF_IP_RE, IPV4_RE, WORDLIST_PATH
from conquer import Tenfold as tf
from orchestrator import Orchestrator as Or
import requests 

class publicface:
    def __init__(self):
        self.nri=nr()
        self.fci=fc()
        self.fsi=fs() 
        self.wpi=wp()
        self.csi=cs()
        self.swi=sw()
        self.psi=ps()
        self.tfi=tf()
        self.ori=Or()
        msfi=Msf(password=MSF_PASS, port=55552, ssl=False)
        self.ori.preflight()

    @staticmethod
    def hostname_to_ip(hostname):
        try:
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except socket.gaierror:
            return None

    @staticmethod
    def ip_to_hostname(ip_address):
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except socket.herror:
            return None
        
if __name__ == "__main__":
    pf=publicface()
    ori=Or()
    ori.preflight()
    pf.csi.speak("Hello, this is a test message from the public face of SurzsEnviro!")