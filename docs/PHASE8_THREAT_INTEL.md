# Aegivanta — Phase 8: Threat Intelligence Platform & IOC Lifecycle

## 1. IOC Multi-Source Ingestion & Normalization
The Threat Intelligence engine normalizes incoming indicators across 7 primary indicator types:
- `IP`: IPv4 / IPv6 addresses
- `DOMAIN`: FQDNs
- `URL`: Full HTTP/HTTPS URLs
- `HASH`: MD5, SHA-1, SHA-256 file hashes
- `EMAIL`: Malicious sender addresses
- `ASN`: Autonomous System Numbers
- `MALWARE_FAMILY`: Associated malware family taxonomy

## 2. In-Memory Fast Lookup Cache
- `GLOBAL_IOC_CACHE`: Sub-millisecond in-memory cache synchronized with PostgreSQL threat intel table.
- **Expiration & Confidence Decay**: Automatic decay of confidence scores for indicators exceeding TTL (default 30 days).
- **MITRE ATT&CK Mapping**: IOCs are linked directly to threat actors, campaign identifiers, and MITRE ATT&CK tactic/technique codes.
