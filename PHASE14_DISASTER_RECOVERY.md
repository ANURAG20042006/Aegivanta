# Aegivanta — Phase 14: Disaster Recovery & Business Continuity Plan

## 1. Backup Procedures
Managed via `scripts/backup.py`:
- **PostgreSQL Database Dump**: Compressed `pg_dump` with SHA-256 integrity checksum (`.dump` + `.dump.sha256` + `.meta.json`).
- **Secret Isolation**: Backups exclude database passwords, API secret keys, and JWT signing credentials.
- **Access Permissions**: Backup files are restricted to system user permissions (mode `0600`).

## 2. Recovery Objectives & Verification
- **Target RPO**: < 1 hour (Tested & verified).
- **Target RTO**: < 30 minutes (Tested & verified).
- **Restore Testing**: Automated verification using `python scripts/backup.py verify --backup-file <path>`.
- **Integrity Guarantee**: Mismatched SHA-256 hashes immediately halt restore operations.
