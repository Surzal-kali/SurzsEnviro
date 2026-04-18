import pyshark
from pathlib import Path
from computerspeak import ComputerSpeak as cs
from fileshuttle import FileShuttle as fs
from target_config import TARGET_INTERFACE

_HERE = Path(__file__).resolve().parent  # SurzsEnviro/

class PacketSniffer:
    def __init__(self, interface: str = TARGET_INTERFACE):
        self.interface = interface
        self.cs = cs()
        self.fs = fs()
    
    def start_sniffing(self, packet_count: int = 300, sniff_time: int = 600, filter: str = "", output_file: str = "captured_packets.pcap"):
        """Start sniffing packets on the specified interface. This function uses the PyShark library to capture network packets on the specified interface, with optional parameters for packet count, sniffing duration, and BPF filter. The captured packets are saved to a file in PCAP format, and relevant information about each packet is printed to the console. The function includes error handling to catch and report any issues that may arise during the packet capture process, and it ensures that resources are properly released after the capture is complete."""
        save_path = str(_HERE / output_file)
        try:
            capture_kwargs = {
                "interface": self.interface,
                "output_file": save_path,
            }
            if filter:
                capture_kwargs["bpf_filter"] = filter

            capture = pyshark.LiveCapture(**capture_kwargs)
            print("Capturing packets... Press Ctrl+C to stop.")
            capture.sniff(packet_count=packet_count, timeout=sniff_time)
            for packet in capture:
                print(f"Packet Timestamp: {packet.sniff_time}")
                print(f"Packet Length: {packet.length} bytes")
                cs.execute_command(f"Write-Output {packet} >> {save_path}")
                if 'ip' in packet:
                    print(f"Source IP: {packet.ip.src}")
                print("-" * 40)
        except Exception as e:
            print(f"Error: {e}")
            print(f"Failed to capture packets on interface {self.interface}: {e}")
        finally:
            capture.close()
            print(f"Captured packets saved to {save_path}")
        return save_path

    def analyze_capture(self, capture_path: str):
        """Analyze the captured packets and extract relevant information. This function reads the captured packets from the specified file, extracts details such as timestamp, packet length, and source IP address (if available), and prints this information to the console. It also includes error handling to catch and report any issues that may arise during the analysis process."""
        capture = pyshark.FileCapture(input_file=capture_path)
        try:
            for packet in capture:
                print(f"Packet Timestamp: {packet.sniff_time}", file=open("packet_analysis.txt", "a"))
                print(f"Packet Length: {packet.length} bytes", file=open("packet_analysis.txt", "a"))
                print(f"Packet Summary: {packet.summary()}", file=open("packet_analysis.txt", "a"))
                if 'ip' in packet:
                    print(f"Source IP: {packet.ip.src}", file=open("packet_analysis.txt", "a"))
                print("-" * 40, file=open("packet_analysis.txt", "a"))
        except Exception as e:
            print(f"Error analyzing capture: {e}")
        finally:
            capture.close()




