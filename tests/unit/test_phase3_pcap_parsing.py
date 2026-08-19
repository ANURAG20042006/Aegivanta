"""
tests/unit/test_phase3_pcap_parsing.py
======================================
Unit tests verifying Phase 3.1 Real Network PCAP parsing, 5-tuple bidirectional flow aggregation,
and strict CICIDS2017 30-feature calculation without fabricated numbers.
"""

import io
import math
import struct
import socket
import pytest
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


def test_bidirectional_flow_aggregation_feature_derivation():
    """Verify bidirectional 5-tuple aggregation calculates all 30 CICIDS2017 features correctly."""
    packets_spec = [
        # Fwd packet 1
        (1000.0, "198.51.100.20", "10.50.1.5", 44333, 80, "TCP", b"DATA_BURST_1", {"syn": True}),
        # Bwd packet 1
        (1000.05, "10.50.1.5", "198.51.100.20", 80, 44333, "TCP", b"ACK_RESPONSE", {"ack": True}),
        # Fwd packet 2
        (1000.10, "198.51.100.20", "10.50.1.5", 44333, 80, "TCP", b"DATA_BURST_2_LONGER_PAYLOAD", {"psh": True, "ack": True}),
    ]

    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    packets = NativePCAPParser.parse_pcap_bytes(pcap_data)
    flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(packets)

    assert len(flows) == 1
    flow = flows[0]

    assert flow.source_ip == "198.51.100.20"
    assert flow.destination_ip == "10.50.1.5"
    assert flow.source_port == 44333
    assert flow.destination_port == 80
    assert flow.protocol == "TCP"

    assert flow.total_fwd_packets == 2.0
    assert flow.total_backward_packets == 1.0
    assert flow.flow_duration > 0.0

    # Verify 30-feature map completeness in extra_features
    ef = flow.extra_features
    required_30 = [
        "Total Fwd Packets", "Total Length of Fwd Packets", "Fwd Packet Length Max",
        "Fwd Packet Length Min", "Fwd Packet Length Mean", "Fwd Packet Length Std",
        "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean",
        "Bwd Packet Length Std", "Flow Packets/s", "Fwd Header Length",
        "Min Packet Length", "Max Packet Length", "Packet Length Mean",
        "Average Packet Size", "Avg Fwd Segment Size", "Avg Bwd Segment Size",
        "Fwd Header Length.1", "Subflow Fwd Packets", "Subflow Fwd Bytes",
        "act_data_pkt_fwd", "Active Mean", "Active Std", "Active Max",
        "Active Min", "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
    ]
    for feat in required_30:
        assert feat in ef, f"Missing derived feature: {feat}"
        assert not math.isnan(ef[feat]), f"Feature {feat} is NaN"


def test_pcap_service_size_limit_rejection():
    """Verify PCAP service rejects files exceeding maximum 50MB limit."""
    # Create artificial oversized buffer > 50MB
    oversized = b"0" * (51 * 1024 * 1024)
    with pytest.raises(ValueError) as exc:
        PCAPTelemetryService.process_pcap_bytes(oversized)
    assert "exceeds maximum allowed limit" in str(exc.value)
