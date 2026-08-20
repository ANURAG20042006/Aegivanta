# SentinelAI — Phase 3.7 SOAR Remediation & Actions Catalog

## 1. Supported Response Actions

| Action Type | Target Type | Reversible | Verification Strategy | Rollback Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **`BLOCK_IP`** | `IP` (IPv4 / IPv6) | ✅ Yes | Checks active perimeter firewall drop rule table. | Removes firewall drop rule if not present prior to execution. |
| **`ISOLATE_HOST`** | `HOST` (Hostname/ID) | ✅ Yes | Queries endpoint containment table for active network quarantine. | Releases host network quarantine, restoring normal VLAN. |
| **`QUARANTINE_ASSET`** | `ASSET` (Asset ID) | ✅ Yes | Verifies asset is placed into `RESTRICTED_DMZ` security zone. | Restores asset to original network security zone. |
| **`REVOKE_SESSION`** | `USER` (Username) | ✅ Yes | Verifies user sessions are invalidated in auth cache. | Clears session revocation blacklist. |
| **`DISABLE_ACCOUNT`** | `USER` (Username) | ✅ Yes | Verifies account is locked/disabled in identity adapter. | Re-enables account access. |

---

## 2. Action Finite State Machine

```
   [REQUESTED] 
        |
        v
   [VALIDATING] ----(Failure / Deny)----> [BLOCKED] / [FAILED]
        |
        v
   [PENDING_APPROVAL] ----(Rejected)----> [REJECTED]
        |
        +----(Approved)----+
                           v
                     [APPROVED]
                           |
                           v
                     [EXECUTING] ---------(Execution Fail)--------+
                           |                                      |
                           v                                      v
                     [VERIFYING]                               [FAILED]
                           |                                      |
         +-(Verified)-+    +-(Unverified)-+                       |
         v            |                   v                       v
    [SUCCEEDED]       |          [ROLLBACK_REQUIRED] <------------+
         |            |                   |
         | (Rollback) |                   v
         +------------+-----------> [ROLLING_BACK]
                                          |
                                          v
                                    [ROLLED_BACK]
```

---

## 3. Idempotency & Cooldown Guarantees

- **Idempotency**: Clients submit requests with `X-Idempotency-Key: <unique-uuid>`. Replays return the cached action result without re-executing against infrastructure.
- **Cooldown**: Consecutive actions on the same target IP, host, or user within the policy cooldown duration (60s–300s) are rejected with HTTP 400.
