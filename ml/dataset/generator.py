import numpy as np
import pandas as pd
from typing import Tuple
from ml.dataset.cicids2017_schema import CICIDS2017_FEATURES, ATTACK_CLASSES


class CICIDS2017DataGenerator:
    """
    Generates synthetic high-fidelity benchmark datasets matching CICIDS2017 feature schemas
    with distinct class-conditional domain signatures for ML baseline evaluation.
    """

    @staticmethod
    def generate_synthetic_dataset(num_samples: int = 5000, random_seed: int = 42) -> pd.DataFrame:
        """
        Generates a synthetic DataFrame with class-conditional network flow characteristics
        across 17 attack types + BENIGN.
        """
        np.random.seed(random_seed)

        # 1. Balanced Class Distribution (BENIGN ~35%, 17 attack classes ~3.8% each)
        n_attacks = len(ATTACK_CLASSES) - 1
        attack_p = 0.65 / n_attacks
        p_dist = [0.35] + [attack_p] * n_attacks
        p_dist = np.array(p_dist) / np.sum(p_dist)

        labels = np.random.choice(ATTACK_CLASSES, size=num_samples, p=p_dist)

        # Initialize feature matrix
        feature_data = {feat: np.zeros(num_samples, dtype=np.float64) for feat in CICIDS2017_FEATURES}

        # 2. Class-Conditional Feature Synthesis with Distinct Domain Signals
        for i, label in enumerate(labels):
            noise = np.random.normal(1.0, 0.03)

            # Default baseline
            dest_port = 80
            duration = 15000.0
            fwd_pkts = 5.0
            bwd_pkts = 5.0
            fwd_len_mean = 250.0
            bwd_len_mean = 350.0
            flow_bytes_s = 5000.0
            flow_pkts_s = 100.0
            syn_flag = 0
            ack_flag = 1
            fin_flag = 0
            rst_flag = 0
            psh_flag = 0
            urg_flag = 0
            idle_mean = 500.0
            active_mean = 100.0

            # Class-specific telemetry signatures
            lbl = label.strip()

            if lbl == "BENIGN":
                dest_port = np.random.choice([80, 443, 53, 8080])
                duration = np.random.uniform(5000, 30000)
                fwd_pkts = np.random.uniform(3, 12)
                bwd_pkts = np.random.uniform(3, 12)
                fwd_len_mean = np.random.uniform(100, 450)
                bwd_len_mean = np.random.uniform(150, 600)
                flow_pkts_s = np.random.uniform(20, 250)
                flow_bytes_s = np.random.uniform(1000, 20000)
                syn_flag = 0
                ack_flag = 1

            elif lbl == "DDoS":
                dest_port = np.random.choice([80, 443])
                duration = np.random.uniform(10000, 100000)
                fwd_pkts = np.random.uniform(300, 1500)
                bwd_pkts = np.random.uniform(0, 10)
                flow_pkts_s = np.random.uniform(15000, 60000)
                flow_bytes_s = np.random.uniform(500000, 3000000)
                syn_flag = 1
                ack_flag = 0

            elif lbl == "DoS Hulk":
                dest_port = 80
                duration = np.random.uniform(20000, 150000)
                fwd_pkts = np.random.uniform(200, 1000)
                bwd_pkts = np.random.uniform(5, 30)
                flow_pkts_s = np.random.uniform(8000, 35000)
                psh_flag = 1
                syn_flag = 1

            elif lbl == "DoS Slowloris":
                dest_port = 80
                duration = np.random.uniform(200000, 1000000)
                fwd_pkts = np.random.uniform(5, 20)
                bwd_pkts = np.random.uniform(2, 10)
                flow_pkts_s = np.random.uniform(0.5, 5.0)
                idle_mean = np.random.uniform(50000, 200000)

            elif lbl == "DoS GoldenEye":
                dest_port = 80
                duration = np.random.uniform(30000, 200000)
                fwd_pkts = np.random.uniform(150, 700)
                bwd_pkts = np.random.uniform(10, 50)
                flow_pkts_s = np.random.uniform(6000, 25000)
                psh_flag = 1

            elif lbl in ["Port Scan", "PortScan"]:
                dest_port = np.random.randint(1, 65535)
                duration = np.random.uniform(10, 300)
                fwd_pkts = 1.0
                bwd_pkts = 0.0
                fwd_len_mean = 40.0
                bwd_len_mean = 0.0
                flow_pkts_s = np.random.uniform(3000, 12000)
                syn_flag = 1
                ack_flag = 0

            elif lbl == "Botnet":
                dest_port = np.random.choice([6667, 8080])
                duration = np.random.uniform(300000, 1500000)
                idle_mean = np.random.uniform(200000, 800000)
                active_mean = np.random.uniform(5000, 25000)
                fwd_pkts = np.random.uniform(10, 40)

            elif lbl == "SQL Injection":
                dest_port = np.random.choice([80, 8080])
                duration = np.random.uniform(10000, 50000)
                fwd_len_mean = np.random.uniform(1200, 3500)
                bwd_len_mean = np.random.uniform(800, 2500)
                psh_flag = 1
                ack_flag = 1

            elif lbl == "XSS":
                dest_port = np.random.choice([80, 8080])
                duration = np.random.uniform(8000, 40000)
                fwd_len_mean = np.random.uniform(800, 2200)
                bwd_len_mean = np.random.uniform(1500, 5000)
                psh_flag = 1
                ack_flag = 1

            elif lbl == "FTP-Patator":
                dest_port = 21
                duration = np.random.uniform(30000, 120000)
                fwd_pkts = np.random.uniform(15, 45)
                bwd_pkts = np.random.uniform(10, 35)
                fwd_len_mean = np.random.uniform(80, 200)
                flow_pkts_s = np.random.uniform(100, 500)

            elif lbl == "SSH-Patator":
                dest_port = 22
                duration = np.random.uniform(40000, 160000)
                fwd_pkts = np.random.uniform(20, 60)
                bwd_pkts = np.random.uniform(15, 50)
                fwd_len_mean = np.random.uniform(100, 300)
                flow_pkts_s = np.random.uniform(150, 600)

            elif lbl == "MITM":
                dest_port = np.random.choice([80, 443])
                duration = np.random.uniform(50000, 300000)
                bwd_pkts = np.random.uniform(30, 150)
                fwd_pkts = np.random.uniform(5, 25)

            elif lbl == "ARP Spoofing":
                dest_port = 0
                duration = np.random.uniform(1000, 10000)
                flow_pkts_s = np.random.uniform(800, 3000)
                fwd_pkts = np.random.uniform(30, 150)

            elif lbl == "DNS Spoofing":
                dest_port = 53
                duration = np.random.uniform(500, 5000)
                fwd_pkts = np.random.uniform(1, 3)
                bwd_len_mean = np.random.uniform(600, 2200)

            elif lbl == "Ransomware":
                dest_port = np.random.choice([445, 139])
                duration = np.random.uniform(50000, 400000)
                flow_bytes_s = np.random.uniform(200000, 1500000)
                bwd_len_mean = np.random.uniform(1000, 4000)

            elif lbl == "Malware":
                dest_port = np.random.choice([80, 443, 8080])
                duration = np.random.uniform(20000, 100000)
                active_mean = np.random.uniform(8000, 40000)
                psh_flag = 1

            elif lbl == "Data Exfiltration":
                dest_port = np.random.choice([443, 8443])
                duration = np.random.uniform(100000, 800000)
                flow_bytes_s = np.random.uniform(800000, 5000000)
                bwd_len_mean = np.random.uniform(2000, 8000)
                fwd_len_mean = np.random.uniform(50, 200)

            elif lbl == "Zero-Day Anomaly":
                dest_port = 9999
                duration = np.random.uniform(100, 800)
                flow_pkts_s = np.random.uniform(12000, 45000)

            # Assign features with slight non-degenerate noise
            feature_data["Destination Port"][i] = float(dest_port)
            feature_data["Flow Duration"][i] = max(1.0, float(duration) * noise)
            feature_data["Total Fwd Packets"][i] = max(1.0, float(fwd_pkts) * noise)
            feature_data["Total Backward Packets"][i] = max(0.0, float(bwd_pkts) * noise)
            feature_data["Total Length of Fwd Packets"][i] = max(0.0, fwd_pkts * fwd_len_mean * noise)
            feature_data["Total Length of Bwd Packets"][i] = max(0.0, bwd_pkts * bwd_len_mean * noise)
            feature_data["Fwd Packet Length Max"][i] = float(fwd_len_mean) * 1.5 * noise
            feature_data["Fwd Packet Length Min"][i] = max(0.0, float(fwd_len_mean) * 0.5 * noise)
            feature_data["Fwd Packet Length Mean"][i] = float(fwd_len_mean) * noise
            feature_data["Fwd Packet Length Std"][i] = float(fwd_len_mean) * 0.2 * noise
            feature_data["Bwd Packet Length Max"][i] = float(bwd_len_mean) * 1.5 * noise
            feature_data["Bwd Packet Length Min"][i] = max(0.0, float(bwd_len_mean) * 0.5 * noise)
            feature_data["Bwd Packet Length Mean"][i] = float(bwd_len_mean) * noise
            feature_data["Bwd Packet Length Std"][i] = float(bwd_len_mean) * 0.2 * noise
            feature_data["Flow Bytes/s"][i] = max(0.0, float(flow_bytes_s) * noise)
            feature_data["Flow Packets/s"][i] = max(0.0, float(flow_pkts_s) * noise)
            feature_data["Flow IAT Mean"][i] = max(1.0, (duration / max(1.0, fwd_pkts + bwd_pkts)) * noise)
            feature_data["Flow IAT Std"][i] = max(0.0, (duration / max(1.0, fwd_pkts + bwd_pkts)) * 0.3 * noise)
            feature_data["Flow IAT Max"][i] = max(1.0, duration * 0.8 * noise)
            feature_data["Flow IAT Min"][i] = max(0.0, duration * 0.05 * noise)
            feature_data["Fwd IAT Total"][i] = max(0.0, duration * 0.9 * noise)
            feature_data["Fwd IAT Mean"][i] = max(1.0, (duration / max(1.0, fwd_pkts)) * noise)
            feature_data["Fwd IAT Std"][i] = max(0.0, (duration / max(1.0, fwd_pkts)) * 0.3 * noise)
            feature_data["Fwd IAT Max"][i] = max(1.0, duration * 0.7 * noise)
            feature_data["Fwd IAT Min"][i] = max(0.0, duration * 0.05 * noise)
            feature_data["Bwd IAT Total"][i] = max(0.0, duration * 0.8 * noise)
            feature_data["Bwd IAT Mean"][i] = max(1.0, (duration / max(1.0, bwd_pkts)) * noise)
            feature_data["Bwd IAT Std"][i] = max(0.0, (duration / max(1.0, bwd_pkts)) * 0.3 * noise)
            feature_data["Bwd IAT Max"][i] = max(1.0, duration * 0.6 * noise)
            feature_data["Bwd IAT Min"][i] = max(0.0, duration * 0.05 * noise)
            feature_data["Fwd PSH Flags"][i] = float(psh_flag)
            feature_data["Bwd PSH Flags"][i] = float(np.random.choice([0, 1], p=[0.95, 0.05]))
            feature_data["Fwd URG Flags"][i] = float(urg_flag)
            feature_data["Bwd URG Flags"][i] = float(np.random.choice([0, 1], p=[0.9, 0.1]))
            feature_data["Fwd Header Length"][i] = fwd_pkts * 20.0
            feature_data["Bwd Header Length"][i] = bwd_pkts * 20.0
            feature_data["Fwd Packets/s"][i] = max(0.0, (fwd_pkts / (duration / 1e6 + 1e-5)) * noise)
            feature_data["Bwd Packets/s"][i] = max(0.0, (bwd_pkts / (duration / 1e6 + 1e-5)) * noise)
            feature_data["Min Packet Length"][i] = min(fwd_len_mean, bwd_len_mean) * 0.5
            feature_data["Max Packet Length"][i] = max(fwd_len_mean, bwd_len_mean) * 1.5
            feature_data["Packet Length Mean"][i] = (fwd_len_mean + bwd_len_mean) / 2.0 * noise
            feature_data["Packet Length Std"][i] = abs(fwd_len_mean - bwd_len_mean) / 2.0 * noise
            feature_data["Packet Length Variance"][i] = (feature_data["Packet Length Std"][i]) ** 2
            feature_data["FIN Flag Count"][i] = float(fin_flag)
            feature_data["SYN Flag Count"][i] = float(syn_flag)
            feature_data["RST Flag Count"][i] = float(rst_flag)
            feature_data["PSH Flag Count"][i] = float(psh_flag)
            feature_data["ACK Flag Count"][i] = float(ack_flag)
            feature_data["URG Flag Count"][i] = float(urg_flag)
            feature_data["CWE Flag Count"][i] = float(np.random.choice([0, 1], p=[0.9, 0.1]))
            feature_data["ECE Flag Count"][i] = float(np.random.choice([0, 1], p=[0.9, 0.1]))
            feature_data["Down/Up Ratio"][i] = (bwd_pkts / max(1.0, fwd_pkts)) + float(np.random.normal(0, 0.05))
            feature_data["Average Packet Size"][i] = (fwd_len_mean + bwd_len_mean) / 2.0 * noise
            feature_data["Avg Fwd Segment Size"][i] = fwd_len_mean * noise
            feature_data["Avg Bwd Segment Size"][i] = bwd_len_mean * noise
            feature_data["Fwd Header Length.1"][i] = fwd_pkts * 20.0 + float(np.random.uniform(0, 4.0))
            feature_data["Fwd Avg Bytes/Bulk"][i] = float(np.random.exponential(scale=10.0))
            feature_data["Fwd Avg Packets/Bulk"][i] = float(np.random.exponential(scale=2.0))
            feature_data["Fwd Avg Bulk Rate"][i] = float(np.random.exponential(scale=100.0))
            feature_data["Bwd Avg Bytes/Bulk"][i] = float(np.random.exponential(scale=10.0))
            feature_data["Bwd Avg Packets/Bulk"][i] = float(np.random.exponential(scale=2.0))
            feature_data["Bwd Avg Bulk Rate"][i] = float(np.random.exponential(scale=100.0))
            feature_data["Subflow Fwd Packets"][i] = fwd_pkts
            feature_data["Subflow Fwd Bytes"][i] = fwd_pkts * fwd_len_mean
            feature_data["Subflow Bwd Packets"][i] = bwd_pkts
            feature_data["Subflow Bwd Bytes"][i] = bwd_pkts * bwd_len_mean
            feature_data["Init_Win_bytes_forward"][i] = float(np.random.choice([8192, 65535, 29200]))
            feature_data["Init_Win_bytes_backward"][i] = float(np.random.choice([8192, 65535, 28960]))
            feature_data["act_data_pkt_fwd"][i] = max(1.0, fwd_pkts - 1.0)
            feature_data["min_seg_size_forward"][i] = float(np.random.choice([20.0, 32.0, 40.0]))
            feature_data["Active Mean"][i] = active_mean * noise
            feature_data["Active Std"][i] = active_mean * 0.1 * noise
            feature_data["Active Max"][i] = active_mean * 1.2 * noise
            feature_data["Active Min"][i] = active_mean * 0.8 * noise
            feature_data["Idle Mean"][i] = idle_mean * noise
            feature_data["Idle Std"][i] = idle_mean * 0.1 * noise
            feature_data["Idle Max"][i] = idle_mean * 1.2 * noise
            feature_data["Idle Min"][i] = idle_mean * 0.8 * noise

        # Inject periodic NaN and Inf for data cleaning pipeline verification
        mask_nan = np.random.choice([True, False], size=num_samples, p=[0.005, 0.995])
        mask_inf = np.random.choice([True, False], size=num_samples, p=[0.005, 0.995])
        feature_data["Flow Bytes/s"][mask_nan] = np.nan
        feature_data["Flow Packets/s"][mask_inf] = np.inf

        # Set target label
        feature_data["Label"] = labels

        # Add IP and Metadata columns
        feature_data["Source IP"] = [f"192.168.1.{np.random.randint(2, 254)}" for _ in range(num_samples)]
        feature_data["Destination IP"] = ["10.0.0.1" for _ in range(num_samples)]
        feature_data["Protocol"] = np.random.choice(["TCP", "UDP"], size=num_samples, p=[0.8, 0.2])

        df = pd.DataFrame(feature_data)
        return df


if __name__ == "__main__":
    generator = CICIDS2017DataGenerator()
    df = generator.generate_synthetic_dataset(num_samples=1000)
    print(f"Generated synthetic dataset shape: {df.shape}")
    print(df["Label"].value_counts())
