# PHASE 36 — L4/L7 MICROSEGMENTATION SPECIFICATION

## 1. Segmentation Principles

- Workloads are classified into logical security segments (e.g. `PAYMENT_GATEWAY_VPC`, `CORE_DATABASE_CLUSTER`).
- Default Deny policy applied across all inter-segment communication.
- eBPF kernel hooks filter packets at ingress and egress interfaces.
