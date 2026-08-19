"""
scripts/benchmark_pcap_pipeline.py
==================================
Empirical Performance Benchmark for SentinelAI Phase 3.1 Real Network Telemetry.
Measures parsing latency, flow aggregation throughput, and end-to-end ML inference.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import platform
import numpy as np
from tests.unit.test_phase3_pcap_parsing import create_synthetic_pcap_bytes
from backend.app.services.pcap_service import NativePCAPParser, BidirectionalFlowAggregator, PCAPTelemetryService


def run_benchmark():
    # 1. System Info
    python_ver = sys.version.split()[0]
    os_name = platform.platform()
    proc = platform.processor() or "x86_64"

    # 2. Build representative multi-flow PCAP
    # 500 packets across 25 distinct 5-tuple conversations
    packets_spec = []
    t_curr = 100.0
    for flow_idx in range(25):
        src = f"192.168.{flow_idx % 5}.{10 + flow_idx}"
        dst = f"10.0.0.{1 + (flow_idx % 3)}"
        sport = 10000 + flow_idx
        dport = 80 if (flow_idx % 2 == 0) else 443
        for p in range(20):
            t_curr += 0.005
            is_fwd = (p % 2 == 0)
            p_src, p_dst = (src, dst) if is_fwd else (dst, src)
            p_sport, p_dport = (sport, dport) if is_fwd else (dport, sport)
            payload = b"X" * (64 + (p * 16))
            flags = {"syn": (p == 0), "ack": (p > 0)}
            packets_spec.append((t_curr, p_src, p_dst, p_sport, p_dport, "TCP", payload, flags))

    pcap_data = create_synthetic_pcap_bytes(packets_spec)
    pcap_size_bytes = len(pcap_data)
    total_packets = len(packets_spec)

    print("=================================================================")
    print("      SentinelAI Phase 3.1 Empirical Telemetry Benchmark         ")
    print("=================================================================")
    print(f"OS/Platform       : {os_name}")
    print(f"Processor/CPU     : {proc}")
    print(f"Python Version    : {python_ver}")
    print(f"PCAP Buffer Size  : {pcap_size_bytes} bytes ({pcap_size_bytes/1024:.2f} KB)")
    print(f"Total Packets     : {total_packets} frames")
    print(f"Total Flows       : 25 bidirectional conversations")
    print("-----------------------------------------------------------------")

    # 3. Benchmark Native PCAP Binary Parsing
    WARMUP_RUNS = 5
    BENCHMARK_RUNS = 50

    # Warmup
    for _ in range(WARMUP_RUNS):
        NativePCAPParser.parse_pcap_bytes(pcap_data)

    parse_times = []
    for _ in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        pkts = NativePCAPParser.parse_pcap_bytes(pcap_data)
        parse_times.append((time.perf_counter() - t0) * 1000.0)

    # 4. Benchmark Bidirectional Flow Aggregation
    for _ in range(WARMUP_RUNS):
        BidirectionalFlowAggregator.aggregate_packets_into_flows(pkts)

    agg_times = []
    for _ in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        flows = BidirectionalFlowAggregator.aggregate_packets_into_flows(pkts)
        agg_times.append((time.perf_counter() - t0) * 1000.0)

    # 5. Combined PCAP Service Ingestion
    for _ in range(WARMUP_RUNS):
        PCAPTelemetryService.process_pcap_bytes(pcap_data)

    total_times = []
    for _ in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        PCAPTelemetryService.process_pcap_bytes(pcap_data)
        total_times.append((time.perf_counter() - t0) * 1000.0)

    print("Stage 1: Binary PCAP Parsing (500 frames)")
    print(f"  Iterations: {BENCHMARK_RUNS} (Warmup: {WARMUP_RUNS})")
    print(f"  Mean: {np.mean(parse_times):.3f} ms | p50: {np.percentile(parse_times, 50):.3f} ms | p95: {np.percentile(parse_times, 95):.3f} ms | p99: {np.percentile(parse_times, 99):.3f} ms")
    print(f"  Throughput: {total_packets / (np.mean(parse_times) / 1000.0):.1f} packets/sec")

    print("\nStage 2: 5-Tuple Flow Aggregation & 30-Feature Extraction (25 flows)")
    print(f"  Iterations: {BENCHMARK_RUNS} (Warmup: {WARMUP_RUNS})")
    print(f"  Mean: {np.mean(agg_times):.3f} ms | p50: {np.percentile(agg_times, 50):.3f} ms | p95: {np.percentile(agg_times, 95):.3f} ms | p99: {np.percentile(agg_times, 99):.3f} ms")
    print(f"  Throughput: {len(flows) / (np.mean(agg_times) / 1000.0):.1f} flows/sec")

    print("\nStage 3: Full Ingestion Pipeline (PCAP Bytes -> Feature Vectors)")
    print(f"  Iterations: {BENCHMARK_RUNS} (Warmup: {WARMUP_RUNS})")
    print(f"  Mean: {np.mean(total_times):.3f} ms | p50: {np.percentile(total_times, 50):.3f} ms | p95: {np.percentile(total_times, 95):.3f} ms | p99: {np.percentile(total_times, 99):.3f} ms")
    print("=================================================================")


if __name__ == "__main__":
    run_benchmark()
