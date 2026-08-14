# SentinelAI Continuous Asset Monitoring & SSRF Hardening

## Overview
SentinelAI Continuous Asset Monitoring provides scheduled and on-demand health probes for protected web services, APIs, databases, and network endpoints.

## SSRF Hardening Architecture
To prevent Server-Side Request Forgery (SSRF) vulnerabilities, all target endpoints undergo rigorous pre-flight validation:

1. **Protocol Restriction**: Only `http://` and `https://` schemes are permitted. Schemes such as `file://`, `gopher://`, `ftp://`, or `dict://` are rejected immediately.
2. **DNS Pre-Resolution**: Hostnames are resolved to IP addresses via `socket.getaddrinfo` prior to initiating network connections.
3. **Subnet & IP Blocklists**:
   - `127.0.0.0/8` (IPv4 Loopback)
   - `10.0.0.0/8` (RFC 1918 Class A Private)
   - `172.16.0.0/12` (RFC 1918 Class B Private)
   - `192.168.0.0/16` (RFC 1918 Class C Private)
   - `169.254.0.0/16` (Link-Local & Cloud Instance Metadata)
   - `::1/128` (IPv6 Loopback)
   - `fc00::/7` (IPv6 Unique Local Address)
   - `fe80::/10` (IPv6 Link-Local)
   - Cloud metadata hostnames (e.g. `metadata.google.internal`, `169.254.169.254`)

## State Machine & Debouncing
- **`HEALTHY`**: Endpoint returned expected status code (e.g. 200) within configured timeout.
- **`DEGRADED`**: 1 or 2 consecutive failures.
- **`DOWN`**: $\ge 3$ consecutive failures. Escalates to Phase 1 Alert and Incident Correlation Engine as a `DoS_Service_Outage` event.
