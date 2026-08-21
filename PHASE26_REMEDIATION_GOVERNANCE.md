# Aegivanta — Automated Remediation Governance Architecture (Phase 26.11)

## Multi-Tiered Action Risk Matrix

All automated and manual response actions are classified into 4 strict governance tiers:

| Risk Tier | Action Name | Reversible | Auto-Executable | Required Approvals |
|---|---|:---:|:---:|---|
| **`LOW`** | `ADD_TAG` | Yes | Yes (Policy permitted) | None |
| **`LOW`** | `INCREASE_MONITORING` | Yes | Yes (Policy permitted) | None |
| **`MEDIUM`** | `REVOKE_SESSION` | No | Configurable | Security Analyst |
| **`MEDIUM`** | `DISABLE_API_KEY` | Yes | Configurable | Security Analyst |
| **`MEDIUM`** | `BLOCK_IP` | Yes | Configurable | Security Analyst |
| **`HIGH`** | `ISOLATE_ENDPOINT` | Yes | No (Default Human Approval) | Incident Commander / Admin |
| **`HIGH`** | `TERMINATE_PROCESS` | No | No (Default Human Approval) | Incident Commander / Admin |
| **`CRITICAL`** | `WIPE_DEVICE` | No | No (Mandatory Human Approval) | System Admin / Owner |
| **`CRITICAL`** | `DROP_DATABASE` | No | No (Mandatory Human Approval) | System Admin / Owner |

## Security & Compliance Rules
- Every action execution generates an immutable, tamper-evident audit trail record.
- Reversible actions maintain state snapshots to support one-click rollbacks.
- Unregistered actions default to `CRITICAL` risk requiring explicit Administrator review.
