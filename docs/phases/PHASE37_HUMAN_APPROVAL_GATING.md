# PHASE 37 — HUMAN-IN-THE-LOOP APPROVAL GATING SPECIFICATION

## 1. Impact Gating Matrix

| Action Tier | Automated Execution | Human Approval Required |
|-------------|---------------------|-------------------------|
| `NON_DESTRUCTIVE` (Log enrichment, reputation query) | YES | NO |
| `CONTAINMENT` (Endpoint quarantine, token revoke) | NO | YES |
| `HIGH_RISK` (Service termination, DB account lock) | NO | YES (Dual-authorization) |
