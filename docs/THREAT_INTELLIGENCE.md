# SentinelAI Threat Intelligence Architecture

## Overview
The SentinelAI Phase 2 Threat Intelligence component provides high-performance indicator ingestion, normalization, storage, and real-time telemetry enrichment.

## IOC Types and Normalization
1. **IPv4 (`ipv4`)**: Strips whitespace and verifies standard 4-octet IPv4 syntax.
2. **IPv6 (`ipv6`)**: Normalizes IPv6 addresses into standard compressed RFC 5952 representation.
3. **Domain (`domain`)**: Strips protocols (`http://`, `https://`), paths, port numbers, and trailing dots, converting to lowercase.
4. **URL (`url`)**: Normalizes protocol schemes, lowercase hostnames, and standardizes query parameters.
5. **File Hash (`sha256`, `md5`)**: Strips whitespace and normalizes to lowercase hexadecimal characters.

## Threat Feed Providers
- **`StaticListProvider`**: Imports serialized JSON list payloads from static arrays.
- **`GenericJsonProvider`**: Fetches external JSON feeds via HTTP and maps arbitrary schema structures.
- **`GenericCsvProvider`**: Parses CSV feeds and extracts indicator fields.

## Non-Destructive Telemetry Enrichment
When raw packet flows or alerts are ingested, `ThreatIntelService.enrich_telemetry()` queries the IOC store. If an indicator matches:
- An enrichment record is attached to the security event metadata payload.
- Active hit counts and last-seen timestamps are updated.
- Raw ML feature values and model predictions remain completely untouched.
