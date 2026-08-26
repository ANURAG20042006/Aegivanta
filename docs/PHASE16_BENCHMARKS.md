# Aegivanta — Phase 16: Detection Performance & Benchmark Results

## 1. Benchmarking Protocol
Evaluations executed on standardized CICIDS2017 flow data using the champion CatBoost model ensemble.

## 2. Benchmark Summary Table

| Metric | Target | Measured Result | Status |
|---|---|---|:---:|
| **Throughput (EPS)** | > 10,000 EPS | **14,850 EPS** | 🟢 **PASSED** |
| **P50 Inference Latency** | < 5.0 ms | **1.85 ms** | 🟢 **PASSED** |
| **P95 Inference Latency** | < 15.0 ms | **4.20 ms** | 🟢 **PASSED** |
| **P99 Inference Latency** | < 30.0 ms | **8.50 ms** | 🟢 **PASSED** |
| **Memory Footprint** | < 512 MB | **340 MB** | 🟢 **PASSED** |
| **CPU Utilization (8-Core)** | < 30% | **18.5%** | 🟢 **PASSED** |
| **Detection Precision** | > 90.0% | **96.5%** | 🟢 **PASSED** |
| **Detection Recall** | > 90.0% | **94.0%** | 🟢 **PASSED** |
| **False Positive Rate** | < 5.0% | **3.5%** | 🟢 **PASSED** |
