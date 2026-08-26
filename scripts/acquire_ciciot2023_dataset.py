import os
import sys
import io
import json
import time
import hashlib
from pathlib import Path
import httpx
import pandas as pd
import numpy as np

# Set stdout UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "EXP-2026-003"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# List of representative classes and their remote URLs in bencorn/CIC-IoT-2023 or baalajimaestro/DDoS-CICIoT2023
SOURCES = [
    # 1. Benign Traffic
    ("Benign", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Benign_Final/BenignTraffic.pcap.csv"),
    # 2. DDoS variants
    ("DDoS-HTTP_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DDoS-HTTP_Flood/DDoS-HTTP_Flood.pcap.csv"),
    ("DDoS-SYN_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DDoS-SYN_Flood/DDoS-SYN_Flood.pcap.csv"),
    ("DDoS-SlowLoris", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DDoS-SlowLoris/DDoS-SlowLoris.pcap.csv"),
    ("DDoS-UDP_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DDoS-UDP_Flood/DDoS-UDP_Flood.pcap.csv"),
    ("DDoS-ICMP_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DDoS-ICMP_Flood/DDoS-ICMP_Flood.pcap.csv"),
    ("DDoS-PSHACK_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DDoS-PSHACK_Flood/DDoS-PSHACK_Flood.pcap.csv"),
    ("DDoS-RSTFINFlood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DDoS-RSTFINFlood/DDoS-RSTFINFlood.pcap.csv"),
    # 3. DoS variants
    ("DoS-HTTP_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DoS-HTTP_Flood/DoS-HTTP_Flood.pcap.csv"),
    ("DoS-SYN_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DoS-SYN_Flood/DoS-SYN_Flood.pcap.csv"),
    ("DoS-TCP_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DoS-TCP_Flood/DoS-TCP_Flood.pcap.csv"),
    ("DoS-UDP_Flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DoS-UDP_Flood/DoS-UDP_Flood.pcap.csv"),
    # 4. Mirai Botnet
    ("Mirai-greeth_flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Mirai-greeth_flood/Mirai-greeth_flood.pcap.csv"),
    ("Mirai-greip_flood", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Mirai-greip_flood/Mirai-greip_flood.pcap.csv"),
    ("Mirai-udpplain", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Mirai-udpplain/Mirai-udpplain.pcap.csv"),
    # 5. Reconnaissance
    ("Recon-PortScan", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Recon-PortScan/Recon-PortScan.pcap.csv"),
    ("Recon-OSScan", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Recon-OSScan/Recon-OSScan.pcap.csv"),
    ("Recon-HostDiscovery", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Recon-HostDiscovery/Recon-HostDiscovery.pcap.csv"),
    ("Recon-PingSweep", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Recon-PingSweep/Recon-PingSweep.pcap.csv"),
    ("VulnerabilityScan", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/VulnerabilityScan/VulnerabilityScan.pcap.csv"),
    # 6. Web Attacks
    ("SqlInjection", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/SqlInjection/SqlInjection.pcap.csv"),
    ("CommandInjection", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/CommandInjection/CommandInjection.pcap.csv"),
    ("XSS", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/XSS/XSS.pcap.csv"),
    ("BrowserHijacking", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/BrowserHijacking/BrowserHijacking.pcap.csv"),
    ("Uploading_Attack", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Uploading_Attack/Uploading_Attack.pcap.csv"),
    # 7. Brute Force / Spoofing / Malware
    ("DictionaryBruteForce", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DictionaryBruteForce/DictionaryBruteForce.pcap.csv"),
    ("DNS_Spoofing", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/DNS_Spoofing/DNS_Spoofing.pcap.csv"),
    ("MITM-ArpSpoofing", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/MITM-ArpSpoofing/MITM-ArpSpoofing.pcap.csv"),
    ("Backdoor_Malware", "https://huggingface.co/datasets/bencorn/CIC-IoT-2023/resolve/main/CSV/CSV/Backdoor_Malware/Backdoor_Malware.pcap.csv"),
]

def acquire():
    print(f"--> Starting CICIoT2023 real-world dataset acquisition from verified repository...")
    collected_dfs = []
    
    client = httpx.Client(timeout=30.0, follow_redirects=True)
    
    for label_name, url in SOURCES:
        try:
            print(f"    Fetching {label_name} from {url}...")
            # Fetch first 100KB to 200KB chunk containing real flow records
            resp = client.get(url, headers={"Range": "bytes=0-150000"})
            if resp.status_code in [200, 206]:
                # Handle possible truncated last line
                lines = resp.text.splitlines()
                if len(lines) > 2:
                    clean_text = "\n".join(lines[:-1]) # drop incomplete last line
                    df_part = pd.read_csv(io.StringIO(clean_text))
                    # Assign ground-truth label
                    df_part["label"] = label_name
                    # Take up to 500 samples per class to maintain balanced diversity
                    if len(df_part) > 300:
                        df_part = df_part.sample(n=300, random_state=42)
                    collected_dfs.append(df_part)
                    print(f"      [OK] Loaded {len(df_part)} flows for '{label_name}' (Columns: {df_part.shape[1]})")
            else:
                print(f"      [WARN] HTTP {resp.status_code} for {label_name}")
        except Exception as e:
            print(f"      [ERR] Failed for {label_name}: {e}")

    if not collected_dfs:
        raise RuntimeError("No data could be acquired!")

    full_df = pd.concat(collected_dfs, ignore_index=True)
    # Deduplicate columns if any duplicate column headers exist
    full_df = full_df.loc[:, ~full_df.columns.duplicated()]
    
    out_csv = RAW_DIR / "ciciot2023_real_benchmark.csv"
    full_df.to_csv(out_csv, index=False)
    
    csv_bytes = out_csv.read_bytes()
    sha256 = hashlib.sha256(csv_bytes).hexdigest()
    
    print("\n" + "=" * 60)
    print(f"--> Dataset Saved to        : {out_csv}")
    print(f"--> Total Rows              : {len(full_df)}")
    print(f"--> Total Columns           : {full_df.shape[1]}")
    print(f"--> Unique Attack Classes   : {full_df['label'].nunique()}")
    print(f"--> Dataset SHA-256 Digest  : {sha256}")
    print("=" * 60)
    print("\nClass Distribution:")
    print(full_df["label"].value_counts())
    
    return full_df, sha256

if __name__ == "__main__":
    acquire()
