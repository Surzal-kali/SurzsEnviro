from computerspeak import ComputerSpeak as cs
from pymetasploit3.msfrpc import MsfRpcClient
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

def somerandomcode1():
    nri=nr()
    fci=fc()
    fsi=fs() 
    wpi=wp()
    csi=cs()
    swi=sw()
    psi=ps()
    tfi=tf()
    ori=Or()
    cci=cc()
    ori.preflight()
    csi.speak("[*] Starting random code execution...")
    nri.scan_network(TARGET_RANGE, TARGET_INTERFACE)
    time.sleep(2)
    csi.speak("[*] Network scan completed. Starting enumeration...")
    if nri.scan_network(TARGET_IP, TARGET_INTERFACE) is not None:
        csi.speak("[*] Target is online.")
    else:
        csi.speak("[*] Target is offline.")
    time.sleep(2)
    
if __name__ == "__main__":
    somerandomcode1()
    csi=cs()
    csi.speak("Welcome Home")
