# PHASE 33 — DISTRIBUTED HONEYPOT FLEET SPECIFICATION

## 1. Supported Decoy Profiles

1. **SSH Cowrie**: Emulates Ubuntu OpenSSH server, records login credentials, remote attacker shell sessions, and downloaded scripts.
2. **Web Admin Portal**: Emulates Jenkins, GitLab, WordPress, or phpMyAdmin login portals capturing brute force and credential stuffing.
3. **Windows SMB File Share**: Emulates corporate network share hosting canary documents.
4. **Active Directory Kerberoast SPN**: Emulates SQL Server service principal accounts (`MSSQLSvc/sql-prod.corp.local:1433`) detecting Kerberoasting ticket requests.
5. **Database Decoy**: Emulates PostgreSQL/MySQL capturing automated SQL injection attempts.
