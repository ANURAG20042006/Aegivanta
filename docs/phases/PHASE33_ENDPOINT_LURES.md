# PHASE 33 — ENDPOINT DECEPTION LURE DISTRIBUTION SPECIFICATION

## 1. Endpoint Lure Types

- **LSASS Saved Credentials**: Fake domain admin and service account credentials injected into memory to catch Mimikatz or procdump executions.
- **Browser Cookies**: Fake session cookies placed in Chromium/Firefox profiles to catch cookie stealer malware.
- **Network Share Mappings**: Canary drive mappings pointing to decoy SMB servers.
