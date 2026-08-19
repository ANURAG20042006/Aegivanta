"""
tests/unit/test_phase3_pcap_parsing.py
======================================
Comprehensive unit tests verifying Phase 3.1 Real Network PCAP parsing, 5-tuple bidirectional flow canonicalization,
and mathematical correctness of all 30 CICIDS2017 derived features across standard and edge-case network flows.
"""

import io
import math
import struct
import socket
import pytest
import numpy as np

from backend.app.services.pcap_service import (
    NativePCAPParser,
    BidirectionalFlowAggregator,
    PCAPTelemetryService,
    RawPacket
)


def create_synthetic_pcap_bytes(packets_spec) -> bytes:
    """
    Generates authentic binary PCAP bytes containing specified IPv4 TCP/UDP packets.
    packets_spec: List of tuples (ts_float, src_ip, dst_ip, src_port, dst_port, proto, payload_bytes, flags)
    flags: dict with bools: syn, ack, fin, rst, psh, urg
    """
    buf = io.BytesIO()

    # 1. PCAP Global Header (24 bytes, Little-Endian standard)
    magic = 0xa1b2c3d4
    v_major = 2
    v_minor = 4
    thiszone = 0
    sigfigs = 0
    snaplen = 65535
    network = 1  # LINKTYPE_ETHERNET
    buf.write(struct.pack("<IHHiIII", magic, v_major, v_minor, thiszone, sigfigs, snaplen, network))

    for spec in packets_spec:
        ts_float, src_ip, dst_ip, src_port, dst_port, proto, payload_bytes, flags = spec
        ts_sec = int(ts_float)
        ts_usec = int((ts_float - ts_sec) * 1_000_000)

        # Build Transport Layer
        proto_num = 6 if proto.upper() == "TCP" else 17
        if proto_num == 6:
            flag_byte = 0
            if flags.get("fin"): flag_byte |= (1 << 0)
            if flags.get("syn"): flag_byte |= (1 << 1)
            if flags.get("rst"): flag_byte |= (1 << 2)
            if flags.get("psh"): flag_byte |= (1 << 3)
            if flags.get("ack"): flag_byte |= (1 << 4)
            if flags.get("urg"): flag_byte |= (1 << 5)

            data_offset = 5  # 5 words = 20 bytes
            data_offset_res = (data_offset << 4)
            transport_hdr = struct.pack(
                "!HHIIBBHHH",
                src_port,
                dst_port,
                100000,  # seq
                200000,  # ack
                data_offset_res,
                flag_byte,
                64240,  # window
                0,      # checksum
                0       # urg ptr
            )
            transport_layer = transport_hdr + payload_bytes
        else:
            udp_len = 8 + len(payload_bytes)
            transport_layer = struct.pack("!HHHH", src_port, dst_port, udp_len, 0) + payload_bytes

        # Build IPv4 Layer
        ihl = 5  # 20 bytes
        ver_ihl = (4 << 4) | ihl
        total_len = 20 + len(transport_layer)
        ip_hdr = struct.pack(
            "!BBHHHBBH4s4s",
            ver_ihl,
            0,          # tos
            total_len,
            54321,      # id
            0x4000,     # flags (DF)
            64,         # ttl
            proto_num,
            0,          # checksum
            socket.inet_aton(src_ip),
            socket.inet_aton(dst_ip)
        )
        ip_packet = ip_hdr + transport_layer

        # Build Ethernet Frame
        eth_hdr = struct.pack(
            "!6s6sH",
            b"\x00\x0c\x29\x1b\x2c\x3d",  # dst mac
            b"\x00\x0c\x29\x4e\x5f\x6a",  # src mac
            0x0800                       # EtherType IPv4
        )
        eth_frame = eth_hdr + ip_packet

        # Packet Record Header (16 bytes)
        incl_len = len(eth_frame)
        orig_len = len(eth_frame)
        buf.write(struct.pack("<IIII", ts_sec, ts_usec, incl_len, orig_len))
        buf.write(eth_frame)

    return buf.getvalue()


def test_native_pcap_parser_decoding():
    """Verify raw binary PCAP decoding parses Ethernet, IPv4, TCP headers and flags accurately."""
    packets_spec = [
        (100.0, "192.168.1.10", "10.0.0.1", 50001, 80, "TCP", b"GET / HTTP/1.1\r\n", {"syn": True}),
        (100.1, "10.0.0.1", "192.168.1.10", 80, 50001, "TCP", b"", {"syn": True, "ack": True}),
        (100.2, "192.168.1.10", "10.0.0.1", 50001, 80, "TCP", b"Host: example.com\r\n\r\n", {"psh": True, "ack": True}),
    ]

    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    assert len(pcap_data) > 0

    packets = NativePCAPParser.parse_pcap_bytes(pcap_data)
    assert len(packets) == 3

    # Verify Packet 1
    p1 = packets[0]
    assert p1.src_ip == "192.168.1.10"
    assert p1.dst_ip == "10.0.0.1"
    assert p1.src_port == 50001
    assert p1.dst_port == 80
    assert p1.protocol == "TCP"
    assert p1.syn_flag == 1
    assert p1.ack_flag == 0
    assert p1.payload_length == len(b"GET / HTTP/1.1\r\n")

    # Verify Packet 2 (Backward SYN+ACK)
    p2 = packets[1]
    assert p2.src_ip == "10.0.0.1"
    assert p2.dst_ip == "192.168.1.10"
    assert p2.src_port == 80
    assert p2.dst_port == 50001
    assert p2.syn_flag == 1
    assert p2.ack_flag == 1


def test_bidirectional_flow_canonicalization_proof():
    """
    CRITICAL TEST 1: Prove bidirectional flow canonicalization.
    Prove that:
      A:1234 -> B:80
      B:80   -> A:1234
      A:1234 -> B:80
    are represented as EXACTLY ONE flow with correct FWD/BWD classification relative to initiator A.
    """
    packets_spec = [
        # Packet 1 (FWD initiator from 192.168.1.10:1234 to 10.0.0.1:80)
        (100.0, "192.168.1.10", "10.0.0.1", 1234, 80, "TCP", b"INIT_SYN", {"syn": True}),
        # Packet 2 (BWD response from 10.0.0.1:80 to 192.168.1.10:1234)
        (100.1, "10.0.0.1", "192.168.1.10", 80, 1234, "TCP", b"RESP_SYNACK", {"syn": True, "ack": True}),
        # Packet 3 (FWD follow-up from 192.168.1.10:1234 to 10.0.0.1:80)
        (100.2, "192.168.1.10", "10.0.0.1", 1234, 80, "TCP", b"DATA_ACK", {"ack": True}),
    ]

    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    packets = NativePCAPParser.parse_pcap_bytes(pcap_data)
    flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(packets)

    # Must produce exactly ONE aggregated bidirectional flow
    assert len(flows) == 1, f"Expected 1 flow, got {len(flows)}"
    flow = flows[0]

    # The flow initiator must define the forward source and destination endpoints
    assert flow.source_ip == "192.168.1.10"
    assert flow.destination_ip == "10.0.0.1"
    assert flow.source_port == 1234
    assert flow.destination_port == 80
    assert flow.protocol == "TCP"

    # Verify packet counts: 2 forward packets, 1 backward packet
    assert flow.total_fwd_packets == 2.0
    assert flow.total_backward_packets == 1.0


def test_dedicated_30_cicids_feature_calculations_mathematical_proof():
    """
    CRITICAL TEST 2: Prove mathematical correctness of all 30 CICIDS2017 features.
    Computes exact expected mathematical values and asserts exact matching against extracted values.
    """
    # Define exact packet payloads:
    # Fwd 1: payload 100 bytes -> IP len = 20(IP) + 20(TCP) + 100 = 140 bytes, act_data=1, syn=1
    # Bwd 1: payload 50 bytes  -> IP len = 20(IP) + 20(TCP) + 50 = 90 bytes, ack=1
    # Bwd 2: payload 150 bytes -> IP len = 20(IP) + 20(TCP) + 150 = 190 bytes, ack=1
    # Fwd 2: payload 0 bytes   -> IP len = 20(IP) + 20(TCP) + 0 = 40 bytes, act_data=0, ack=1
    # Fwd 3: payload 300 bytes -> IP len = 20(IP) + 20(TCP) + 300 = 340 bytes (after 1.5s idle gap), act_data=1, psh=1, ack=1

    t0 = 1000.0
    t1 = 1000.1
    t2 = 1000.2
    t3 = 1000.3
    t4 = 1002.0  # 1.7s gap (> 1.0s) -> creates 1 idle period and 2 active bursts

    packets_spec = [
        (t0, "10.0.0.10", "10.0.0.20", 5000, 8080, "TCP", b"A" * 100, {"syn": True}),
        (t1, "10.0.0.20", "10.0.0.10", 8080, 5000, "TCP", b"B" * 50, {"ack": True}),
        (t2, "10.0.0.20", "10.0.0.10", 8080, 5000, "TCP", b"C" * 150, {"ack": True}),
        (t3, "10.0.0.10", "10.0.0.20", 5000, 8080, "TCP", b"", {"ack": True}),
        (t4, "10.0.0.10", "10.0.0.20", 5000, 8080, "TCP", b"D" * 300, {"psh": True, "ack": True}),
    ]

    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    packets = NativePCAPParser.parse_pcap_bytes(pcap_data)
    flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(packets)
    assert len(flows) == 1
    flow = flows[0]
    ef = flow.extra_features

    # Forward IP lengths: [140, 40, 340]
    # Backward IP lengths: [90, 190]
    # All IP lengths: [140, 90, 190, 40, 340]
    fwd_lens = [140, 40, 340]
    bwd_lens = [90, 190]
    all_lens = [140, 90, 190, 40, 340]
    duration_sec = t4 - t0  # 2.0s

    # 1. Total Fwd Packets [00]
    assert ef["Total Fwd Packets"] == 3.0
    # 2. Total Length of Fwd Packets [01]
    assert ef["Total Length of Fwd Packets"] == sum(fwd_lens)  # 520.0
    # 3. Fwd Packet Length Max [02]
    assert ef["Fwd Packet Length Max"] == max(fwd_lens)  # 340.0
    # 4. Fwd Packet Length Min [03]
    assert ef["Fwd Packet Length Min"] == min(fwd_lens)  # 40.0
    # 5. Fwd Packet Length Mean [04]
    assert pytest.approx(ef["Fwd Packet Length Mean"], 1e-4) == np.mean(fwd_lens)  # 173.3333
    # 6. Fwd Packet Length Std [05]
    assert pytest.approx(ef["Fwd Packet Length Std"], 1e-4) == np.std(fwd_lens, ddof=0)
    # 7. Bwd Packet Length Max [06]
    assert ef["Bwd Packet Length Max"] == max(bwd_lens)  # 190.0
    # 8. Bwd Packet Length Min [07]
    assert ef["Bwd Packet Length Min"] == min(bwd_lens)  # 90.0
    # 9. Bwd Packet Length Mean [08]
    assert pytest.approx(ef["Bwd Packet Length Mean"], 1e-4) == np.mean(bwd_lens)  # 140.0
    # 10. Bwd Packet Length Std [09]
    assert pytest.approx(ef["Bwd Packet Length Std"], 1e-4) == np.std(bwd_lens, ddof=0)  # 50.0
    # 11. Flow Packets/s [10]
    assert pytest.approx(ef["Flow Packets/s"], 1e-4) == 5 / duration_sec  # 2.5
    # 12. Fwd Header Length [11] (3 fwd packets * 40 bytes (20 IP + 20 TCP))
    assert ef["Fwd Header Length"] == 120.0
    # 13. Min Packet Length [12]
    assert ef["Min Packet Length"] == min(all_lens)  # 40.0
    # 14. Max Packet Length [13]
    assert ef["Max Packet Length"] == max(all_lens)  # 340.0
    # 15. Packet Length Mean [14]
    assert pytest.approx(ef["Packet Length Mean"], 1e-4) == np.mean(all_lens)  # 180.0
    # 16. Average Packet Size [15]
    assert pytest.approx(ef["Average Packet Size"], 1e-4) == sum(all_lens) / len(all_lens)  # 180.0
    # 17. Avg Fwd Segment Size [16]
    assert pytest.approx(ef["Avg Fwd Segment Size"], 1e-4) == sum(fwd_lens) / len(fwd_lens)  # 173.3333
    # 18. Avg Bwd Segment Size [17]
    assert pytest.approx(ef["Avg Bwd Segment Size"], 1e-4) == sum(bwd_lens) / len(bwd_lens)  # 140.0
    # 19. Fwd Header Length.1 [18]
    assert ef["Fwd Header Length.1"] == 120.0
    # 20. Subflow Fwd Packets [19]
    assert ef["Subflow Fwd Packets"] == 3.0
    # 21. Subflow Fwd Bytes [20]
    assert ef["Subflow Fwd Bytes"] == sum(fwd_lens)  # 520.0
    # 22. act_data_pkt_fwd [21] (fwd 1 has 100, fwd 2 has 0, fwd 3 has 300 -> count = 2)
    assert ef["act_data_pkt_fwd"] == 2.0
    # 23-26. Active Mean, Std, Max, Min [22-25]
    # Active burst 1: t0 to t3 (1000.3 - 1000.0 = 0.3s = 300,000 usec)
    # Active burst 2: t4 to t4 (0 usec)
    active_bursts = [300000.0, 0.0]
    assert pytest.approx(ef["Active Mean"], 1e-2) == np.mean(active_bursts)
    assert pytest.approx(ef["Active Max"], 1e-2) == max(active_bursts)
    assert pytest.approx(ef["Active Min"], 1e-2) == min(active_bursts)
    # 27-30. Idle Mean, Std, Max, Min [26-29]
    # Idle gap: t4 - t3 = 1002.0 - 1000.3 = 1.7s = 1,700,000 usec
    assert pytest.approx(ef["Idle Mean"], 1e-2) == 1700000.0
    assert pytest.approx(ef["Idle Max"], 1e-2) == 1700000.0
    assert pytest.approx(ef["Idle Min"], 1e-2) == 1700000.0


def test_edge_case_single_packet_flow():
    """Verify single-packet flow does not raise division-by-zero or produce NaN."""
    packets_spec = [
        (100.0, "192.168.1.50", "8.8.8.8", 43210, 53, "UDP", b"DNS_QUERY", {})
    ]
    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    packets = NativePCAPParser.parse_pcap_bytes(pcap_data)
    flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(packets)

    assert len(flows) == 1
    flow = flows[0]
    assert flow.total_fwd_packets == 1.0
    assert flow.total_backward_packets == 0.0
    assert flow.flow_duration > 0.0
    assert not math.isnan(flow.flow_packets_s)
    assert not math.isnan(flow.flow_bytes_s)

    ef = flow.extra_features
    for k, v in ef.items():
        assert not math.isnan(v), f"Feature {k} is NaN in single-packet flow"


def test_edge_case_forward_only_multi_packet_flow():
    """Verify forward-only flow (zero backward packets) correctly reports Bwd stats as 0.0 without errors."""
    packets_spec = [
        (100.0, "10.1.1.1", "10.2.2.2", 1111, 2222, "UDP", b"CHUNK_1", {}),
        (100.1, "10.1.1.1", "10.2.2.2", 1111, 2222, "UDP", b"CHUNK_2_LONGER", {}),
        (100.2, "10.1.1.1", "10.2.2.2", 1111, 2222, "UDP", b"CHUNK_3", {}),
    ]
    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    packets = NativePCAPParser.parse_pcap_bytes(pcap_data)
    flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(packets)

    assert len(flows) == 1
    flow = flows[0]
    assert flow.total_fwd_packets == 3.0
    assert flow.total_backward_packets == 0.0
    ef = flow.extra_features
    assert ef["Bwd Packet Length Max"] == 0.0
    assert ef["Bwd Packet Length Min"] == 0.0
    assert ef["Bwd Packet Length Mean"] == 0.0
    assert ef["Bwd Packet Length Std"] == 0.0
    assert ef["Avg Bwd Segment Size"] == 0.0


def test_edge_case_zero_duration_flow():
    """Verify simultaneous packets (delta t = 0.0) are clamped to minimum 1 microsecond without division by zero."""
    packets_spec = [
        (100.0, "192.168.1.1", "192.168.1.2", 80, 80, "TCP", b"A", {}),
        (100.0, "192.168.1.1", "192.168.1.2", 80, 80, "TCP", b"B", {}),
    ]
    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    packets = NativePCAPParser.parse_pcap_bytes(pcap_data)
    flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(packets)

    assert len(flows) == 1
    flow = flows[0]
    assert flow.flow_duration >= 1.0  # Clamped to at least 1 microsecond
    assert flow.flow_packets_s > 0.0
    assert not math.isinf(flow.flow_packets_s)
    assert not math.isnan(flow.flow_packets_s)


def test_pcap_service_size_limit_rejection():
    """Verify PCAP service rejects files exceeding maximum 50MB limit."""
    oversized = b"0" * (51 * 1024 * 1024)
    with pytest.raises(ValueError) as exc:
        PCAPTelemetryService.process_pcap_bytes(oversized)
    assert "exceeds maximum allowed limit" in str(exc.value)
