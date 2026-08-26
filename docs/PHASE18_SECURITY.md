# AEGIVANTA — PHASE 18 SECURITY & HARDENING CONTROLS

## 1. SSRF Protection on Threat Feeds
All external threat feed ingestion URLs undergo strict validation blocking:
- Loopback addresses (`127.0.0.0/8`, `::1/128`)
- RFC 1918 Private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)
- Cloud instance metadata endpoints (`169.254.169.254`, `metadata.google.internal`)
- Link-local and Unique Local IPv6 ranges (`fe80::/10`, `fc00::/7`)

## 2. Multi-Tenant Scoping
All threat actors, campaigns, malware classifications, and indicator sightings are indexed by `tenant_id` and isolated at the database query layer.
