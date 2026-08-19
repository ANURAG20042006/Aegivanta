"""
backend/app/services/pcap_service.py
====================================
Phase 3.1 Production Real Network Telemetry Engine:
Native High-Performance Binary PCAP & PCAPNG Parser, 5-Tuple Bidirectional Flow Aggregator,
and Strict CICIDS2017 30-Feature Extractor.
"""

import io
import math
import struct
import socket
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional, BinaryIO
from collections import defaultdict
import numpy as np

from backend.app.schemas.predict import PacketFeatureVector
from ml.schema.feature_schema import validate_input_vector, DEFAULT_FEATURE_SCHEMA

logger = logging.getLogger("SentinelAI")

# PCAP Magic Numbers
PCAP_MAGIC_MICRO_BE = b"\xa1\xb2\xc3\xd4"
PCAP_MAGIC_MICRO_LE = b"\xd4\xc3\xb2\xa1"
PCAP_MAGIC_NANO_BE = b"\xa1\xb2\x3c\x4d"
PCAP_MAGIC_NANO_LE = b"\x4d\x3c\xb2\xa1"
PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"


class RawPacket:
    """Represents a decoded network packet."""
    __slots__ = (
        "timestamp_sec",
        "timestamp_usec",
        "timestamp_float",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "protocol",
        "ip_total_length",
        "ip_header_length",
        "transport_header_length",
        "payload_length",
        "syn_flag",
        "ack_flag",
        "fin_flag",
        "rst_flag",
        "psh_flag",
        "urg_flag"
    )

    def __init__(
        self,
        timestamp_sec: int,
        timestamp_usec: int,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        protocol: str,
        ip_total_length: int,
        ip_header_length: int,
        transport_header_length: int,
        payload_length: int,
        syn_flag: int = 0,
        ack_flag: int = 0,
        fin_flag: int = 0,
        rst_flag: int = 0,
        psh_flag: int = 0,
        urg_flag: int = 0
    ):
        self.timestamp_sec = timestamp_sec
        self.timestamp_usec = timestamp_usec
        self.timestamp_float = float(timestamp_sec) + float(timestamp_usec) / 1_000_000.0
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        self.ip_total_length = ip_total_length
        self.ip_header_length = ip_header_length
        self.transport_header_length = transport_header_length
        self.payload_length = payload_length
        self.syn_flag = syn_flag
        self.ack_flag = ack_flag
        self.fin_flag = fin_flag
        self.rst_flag = rst_flag
        self.psh_flag = psh_flag
        self.urg_flag = urg_flag


class NativePCAPParser:
    """
    Zero-dependency, high-speed binary parser for classic PCAP and PCAPNG capture formats.
    Decodes Ethernet, IPv4, TCP, and UDP frames with strict bounds checking.
    """

    @classmethod
    def parse_pcap_bytes(cls, pcap_data: bytes, max_packets: int = 25000) -> List[RawPacket]:
        """Parses raw PCAP binary bytes and returns a list of decoded RawPacket objects."""
        if len(pcap_data) < 24:
            raise ValueError("Invalid PCAP file: File size is smaller than the 24-byte global header.")

        stream = io.BytesIO(pcap_data)
        magic = stream.read(4)

        if magic in (PCAP_MAGIC_MICRO_LE, PCAP_MAGIC_NANO_LE):
            endian = "<"
            is_nano = (magic == PCAP_MAGIC_NANO_LE)
        elif magic in (PCAP_MAGIC_MICRO_BE, PCAP_MAGIC_NANO_BE):
            endian = ">"
            is_nano = (magic == PCAP_MAGIC_NANO_BE)
        elif magic == PCAPNG_MAGIC:
            return cls._parse_pcapng(stream, max_packets)
        else:
            raise ValueError(f"Unsupported capture format or invalid magic header: {magic.hex()}")

        # Read remainder of 24-byte PCAP Global Header
        # version_major(2), version_minor(2), thiszone(4), sigfigs(4), snaplen(4), network(4)
        _ = stream.read(20)

        packets: List[RawPacket] = []
        packet_header_struct = struct.Struct(f"{endian}IIII")  # ts_sec, ts_usec, incl_len, orig_len

        while len(packets) < max_packets:
            hdr_bytes = stream.read(16)
            if len(hdr_bytes) < 16:
                break  # EOF

            ts_sec, ts_usec, incl_len, _ = packet_header_struct.unpack(hdr_bytes)
            if is_nano:
                ts_usec = ts_usec // 1000  # Convert nanoseconds to microseconds

            if incl_len <= 0 or incl_len > 65535:
                continue

            packet_raw = stream.read(incl_len)
            if len(packet_raw) < incl_len:
                break

            decoded = cls._decode_ethernet_ipv4_packet(packet_raw, ts_sec, ts_usec)
            if decoded:
                packets.append(decoded)

        return packets

    @classmethod
    def _decode_ethernet_ipv4_packet(cls, data: bytes, ts_sec: int, ts_usec: int) -> Optional[RawPacket]:
        """Decodes standard Ethernet (DIX / 802.3) -> IPv4 -> TCP/UDP packet."""
        if len(data) < 14 + 20:  # Ethernet header (14) + min IPv4 (20)
            return None

        # 1. Parse Ethernet Header
        eth_type = struct.unpack("!H", data[12:14])[0]
        ip_offset = 14

        # Handle 802.1Q VLAN Tag (Type 0x8100)
        if eth_type == 0x8100 and len(data) >= 18:
            eth_type = struct.unpack("!H", data[16:18])[0]
            ip_offset = 18

        if eth_type != 0x0800:  # Must be IPv4
            return None

        # 2. Parse IPv4 Header
        ip_data = data[ip_offset:]
        if len(ip_data) < 20:
            return None

        ver_ihl = ip_data[0]
        version = ver_ihl >> 4
        ihl = (ver_ihl & 0x0F) * 4

        if version != 4 or ihl < 20 or len(ip_data) < ihl:
            return None

        total_length = struct.unpack("!H", ip_data[2:4])[0]
        if total_length == 0 or total_length > len(ip_data):
            total_length = len(ip_data)

        protocol_num = ip_data[9]
        src_ip = socket.inet_ntoa(ip_data[12:16])
        dst_ip = socket.inet_ntoa(ip_data[16:20])

        transport_data = ip_data[ihl:total_length]

        # 3. Parse Transport Layer (TCP / UDP)
        if protocol_num == 6 and len(transport_data) >= 20:  # TCP
            src_port, dst_port = struct.unpack("!HH", transport_data[0:4])
            tcp_offset = (transport_data[12] >> 4) * 4
            if tcp_offset < 20 or tcp_offset > len(transport_data):
                tcp_offset = 20

            flags = transport_data[13]
            fin = (flags >> 0) & 1
            syn = (flags >> 1) & 1
            rst = (flags >> 2) & 1
            psh = (flags >> 3) & 1
            ack = (flags >> 4) & 1
            urg = (flags >> 5) & 1

            payload_len = max(0, len(transport_data) - tcp_offset)

            return RawPacket(
                timestamp_sec=ts_sec,
                timestamp_usec=ts_usec,
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol="TCP",
                ip_total_length=total_length,
                ip_header_length=ihl,
                transport_header_length=tcp_offset,
                payload_length=payload_len,
                syn_flag=syn,
                ack_flag=ack,
                fin_flag=fin,
                rst_flag=rst,
                psh_flag=psh,
                urg_flag=urg
            )

        elif protocol_num == 17 and len(transport_data) >= 8:  # UDP
            src_port, dst_port, udp_len = struct.unpack("!HHH", transport_data[0:6])
            payload_len = max(0, udp_len - 8)

            return RawPacket(
                timestamp_sec=ts_sec,
                timestamp_usec=ts_usec,
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol="UDP",
                ip_total_length=total_length,
                ip_header_length=ihl,
                transport_header_length=8,
                payload_length=payload_len
            )

        return None

    @classmethod
    def _parse_pcapng(cls, stream: io.BytesIO, max_packets: int) -> List[RawPacket]:
        """Decodes standard PCAPNG blocks (Section Header Block & Enhanced Packet Block)."""
        packets: List[RawPacket] = []
        # Return empty if PCAPNG block parsing reaches EOF
        # In standard PCAPNG, Enhanced Packet Block (EPB) type is 0x00000006
        stream.seek(0)
        while len(packets) < max_packets:
            block_hdr = stream.read(8)
            if len(block_hdr) < 8:
                break
            b_type, b_len = struct.unpack("<II", block_hdr)
            if b_len < 12:
                break
            body = stream.read(b_len - 8)
            if len(body) < (b_len - 8):
                break

            if b_type == 0x00000006 and len(body) >= 20:  # Enhanced Packet Block
                # interface_id(4), ts_high(4), ts_low(4), cap_len(4), orig_len(4)
                _, ts_high, ts_low, cap_len, _ = struct.unpack("<IIIII", body[0:20])
                ts_raw = (ts_high << 32) | ts_low
                ts_sec = int(ts_raw / 1_000_000)
                ts_usec = int(ts_raw % 1_000_000)
                pkt_data = body[20:20 + cap_len]
                decoded = cls._decode_ethernet_ipv4_packet(pkt_data, ts_sec, ts_usec)
                if decoded:
                    packets.append(decoded)

        return packets


class BidirectionalFlowAggregator:
    """
    Groups raw network packets into bidirectional 5-tuple flows and derives all 30 CICIDS2017 features.
    No fabricated, random, or arbitrary feature values.
    """

    FLOW_TIMEOUT_SECONDS = 120.0  # Inactive flow expiration window

    @classmethod
    def aggregate_packets_into_flows(cls, packets: List[RawPacket]) -> List[PacketFeatureVector]:
        """
        Aggregates packet stream into distinct 5-tuple flows and extracts CICIDS2017 feature vectors.
        """
        if not packets:
            return []

        # Sort packets chronologically
        sorted_pkts = sorted(packets, key=lambda p: p.timestamp_float)

        # Map 5-tuple key -> Flow session data
        # Canonical flow key is the 5-tuple of the first observed packet in the flow
        flow_sessions: Dict[Tuple, Dict[str, Any]] = {}

        for pkt in sorted_pkts:
            fwd_key = (pkt.src_ip, pkt.dst_ip, pkt.src_port, pkt.dst_port, pkt.protocol)
            bwd_key = (pkt.dst_ip, pkt.src_ip, pkt.dst_port, pkt.src_port, pkt.protocol)

            if fwd_key in flow_sessions:
                session = flow_sessions[fwd_key]
                session["fwd_packets"].append(pkt)
                session["all_packets"].append(pkt)
            elif bwd_key in flow_sessions:
                session = flow_sessions[bwd_key]
                session["bwd_packets"].append(pkt)
                session["all_packets"].append(pkt)
            else:
                # Initialize new bidirectional flow session
                flow_sessions[fwd_key] = {
                    "key": fwd_key,
                    "first_packet": pkt,
                    "fwd_packets": [pkt],
                    "bwd_packets": [],
                    "all_packets": [pkt]
                }

        # Derive 30-feature vector for each completed flow
        flow_vectors: List[PacketFeatureVector] = []
        for fwd_key, session in flow_sessions.items():
            vector = cls._extract_flow_feature_vector(session)
            if vector:
                flow_vectors.append(vector)

        return flow_vectors

    @classmethod
    def _extract_flow_feature_vector(cls, session: Dict[str, Any]) -> PacketFeatureVector:
        """Derives exact CICIDS2017 30-feature attributes from a completed flow session."""
        fwd_pkts: List[RawPacket] = session["fwd_packets"]
        bwd_pkts: List[RawPacket] = session["bwd_packets"]
        all_pkts: List[RawPacket] = session["all_packets"]
        first_pkt: RawPacket = session["first_packet"]

        # Timestamps & Flow Duration (in microseconds)
        t_start = all_pkts[0].timestamp_float
        t_end = all_pkts[-1].timestamp_float
        duration_sec = max(1e-6, t_end - t_start)
        flow_duration_usec = float(duration_sec * 1_000_000.0)

        # 1. Forward Packet Length Statistics
        fwd_lengths = [p.ip_total_length for p in fwd_pkts]
        n_fwd = len(fwd_lengths)
        tot_fwd_pkts = float(n_fwd)
        tot_len_fwd = float(sum(fwd_lengths))
        fwd_max = float(max(fwd_lengths)) if fwd_lengths else 0.0
        fwd_min = float(min(fwd_lengths)) if fwd_lengths else 0.0
        fwd_mean = float(np.mean(fwd_lengths)) if fwd_lengths else 0.0
        fwd_std = float(np.std(fwd_lengths, ddof=0)) if len(fwd_lengths) > 1 else 0.0

        # 2. Backward Packet Length Statistics
        bwd_lengths = [p.ip_total_length for p in bwd_pkts]
        n_bwd = len(bwd_lengths)
        tot_bwd_pkts = float(n_bwd)
        tot_len_bwd = float(sum(bwd_lengths))
        bwd_max = float(max(bwd_lengths)) if bwd_lengths else 0.0
        bwd_min = float(min(bwd_lengths)) if bwd_lengths else 0.0
        bwd_mean = float(np.mean(bwd_lengths)) if bwd_lengths else 0.0
        bwd_std = float(np.std(bwd_lengths, ddof=0)) if len(bwd_lengths) > 1 else 0.0

        # 3. All Packet Length Statistics
        all_lengths = [p.ip_total_length for p in all_pkts]
        n_all = len(all_lengths)
        all_min = float(min(all_lengths))
        all_max = float(max(all_lengths))
        all_mean = float(np.mean(all_lengths))
        all_std = float(np.std(all_lengths, ddof=0)) if len(all_lengths) > 1 else 0.0
        avg_pkt_size = float(sum(all_lengths) / n_all) if n_all > 0 else 0.0

        # 4. Rates
        flow_pkts_s = float(n_all / duration_sec)
        flow_bytes_s = float(sum(all_lengths) / duration_sec)

        # 5. Header Lengths & Segment Sizes
        fwd_hdr_len = float(sum(p.ip_header_length + p.transport_header_length for p in fwd_pkts))
        avg_fwd_seg = float(tot_len_fwd / n_fwd) if n_fwd > 0 else 0.0
        avg_bwd_seg = float(tot_len_bwd / n_bwd) if n_bwd > 0 else 0.0

        # 6. Actual Data Packets Forward (Payload > 0)
        act_data_fwd = float(sum(1 for p in fwd_pkts if p.payload_length > 0))

        # 7. TCP Flags
        syn_count = float(sum(p.syn_flag for p in all_pkts))
        ack_count = float(sum(p.ack_flag for p in all_pkts))
        rst_count = float(sum(p.rst_flag for p in all_pkts))
        psh_count = float(sum(p.psh_flag for p in all_pkts))
        urg_count = float(sum(p.urg_flag for p in all_pkts))

        # 8. Active & Idle Periods (threshold = 1.0 second)
        active_periods: List[float] = []
        idle_periods: List[float] = []

        if len(all_pkts) > 1:
            current_active_start = all_pkts[0].timestamp_float
            last_pkt_time = all_pkts[0].timestamp_float

            for p in all_pkts[1:]:
                iat = p.timestamp_float - last_pkt_time
                if iat > 1.0:
                    # An idle gap occurred
                    act_dur = max(0.0, (last_pkt_time - current_active_start) * 1_000_000.0)
                    active_periods.append(act_dur)
                    idle_periods.append(float(iat * 1_000_000.0))
                    current_active_start = p.timestamp_float
                last_pkt_time = p.timestamp_float

            # Append final active period
            final_act = max(0.0, (all_pkts[-1].timestamp_float - current_active_start) * 1_000_000.0)
            active_periods.append(final_act)

        active_mean = float(np.mean(active_periods)) if active_periods else flow_duration_usec
        active_std = float(np.std(active_periods, ddof=0)) if len(active_periods) > 1 else 0.0
        active_max = float(max(active_periods)) if active_periods else flow_duration_usec
        active_min = float(min(active_periods)) if active_periods else flow_duration_usec

        idle_mean = float(np.mean(idle_periods)) if idle_periods else 0.0
        idle_std = float(np.std(idle_periods, ddof=0)) if len(idle_periods) > 1 else 0.0
        idle_max = float(max(idle_periods)) if idle_periods else 0.0
        idle_min = float(min(idle_periods)) if idle_periods else 0.0

        # Construct full 30-feature dictionary mapped into extra_features
        extra_features_dict = {
            "Total Fwd Packets": tot_fwd_pkts,
            "Total Length of Fwd Packets": tot_len_fwd,
            "Fwd Packet Length Max": fwd_max,
            "Fwd Packet Length Min": fwd_min,
            "Fwd Packet Length Mean": fwd_mean,
            "Fwd Packet Length Std": fwd_std,
            "Bwd Packet Length Max": bwd_max,
            "Bwd Packet Length Min": bwd_min,
            "Bwd Packet Length Mean": bwd_mean,
            "Bwd Packet Length Std": bwd_std,
            "Flow Packets/s": flow_pkts_s,
            "Fwd Header Length": fwd_hdr_len,
            "Min Packet Length": all_min,
            "Max Packet Length": all_max,
            "Packet Length Mean": all_mean,
            "Average Packet Size": avg_pkt_size,
            "Avg Fwd Segment Size": avg_fwd_seg,
            "Avg Bwd Segment Size": avg_bwd_seg,
            "Fwd Header Length.1": fwd_hdr_len,
            "Subflow Fwd Packets": tot_fwd_pkts,
            "Subflow Fwd Bytes": tot_len_fwd,
            "act_data_pkt_fwd": act_data_fwd,
            "Active Mean": active_mean,
            "Active Std": active_std,
            "Active Max": active_max,
            "Active Min": active_min,
            "Idle Mean": idle_mean,
            "Idle Std": idle_std,
            "Idle Max": idle_max,
            "Idle Min": idle_min,
            "Destination Port": float(first_pkt.dst_port),
            "Flow Duration": flow_duration_usec,
            "Total Backward Packets": tot_bwd_pkts
        }

        return PacketFeatureVector(
            source_ip=first_pkt.src_ip,
            destination_ip=first_pkt.dst_ip,
            source_port=first_pkt.src_port,
            destination_port=first_pkt.dst_port,
            protocol=first_pkt.protocol,
            flow_duration=flow_duration_usec,
            total_fwd_packets=tot_fwd_pkts,
            total_backward_packets=tot_bwd_pkts,
            packet_length_mean=all_mean,
            packet_length_std=all_std,
            flow_bytes_s=flow_bytes_s,
            flow_packets_s=flow_pkts_s,
            syn_flag_count=syn_count,
            rst_flag_count=rst_count,
            psh_flag_count=psh_count,
            ack_flag_count=ack_count,
            urg_flag_count=urg_count,
            extra_features=extra_features_dict
        )


class PCAPTelemetryService:
    """
    High-level PCAP Upload & Real-Time Flow Extraction Service.
    Enforces maximum upload sizes (50MB), magic header validation, and integration with PredictService.
    """

    MAX_PCAP_BYTES = 50 * 1024 * 1024  # 50 MB upload limit
    MAX_EXTRACTED_PACKETS = 50000

    # Prometheus-compatible counters
    pcap_files_processed = 0
    pcap_packets_parsed = 0
    pcap_flows_extracted = 0
    pcap_parse_errors = 0

    @classmethod
    def process_pcap_bytes(cls, pcap_data: bytes) -> List[PacketFeatureVector]:
        """
        Validates, decodes, and aggregates a raw PCAP byte stream into valid CICIDS2017 feature vectors.
        """
        if len(pcap_data) > cls.MAX_PCAP_BYTES:
            cls.pcap_parse_errors += 1
            raise ValueError(f"PCAP upload exceeds maximum allowed limit of {cls.MAX_PCAP_BYTES // (1024*1024)} MB.")

        try:
            packets = NativePCAPParser.parse_pcap_bytes(pcap_data, max_packets=cls.MAX_EXTRACTED_PACKETS)
            flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(packets)

            cls.pcap_files_processed += 1
            cls.pcap_packets_parsed += len(packets)
            cls.pcap_flows_extracted += len(flows)

            return flows
        except Exception as exc:
            cls.pcap_parse_errors += 1
            logger.error("PCAP telemetry processing failed: %s", exc)
            raise


# Singleton
pcap_service = PCAPTelemetryService()
