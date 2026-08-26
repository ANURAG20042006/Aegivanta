# SentinelAI — Phase 3.7 Architecture Specification

## Autonomous Incident Response + SOAR + Safe Remediation Engine

### 1. Architectural Pipeline

Phase 3.7 introduces a production-grade autonomous incident response and safe remediation engine into SentinelAI.

```
Detection
   ↓
Correlation
   ↓
Risk (0–100 Explainable Scoring)
   ↓
Incident Formation & Deduplication
   ↓
Response Decision Engine (ResponseDecisionService)
   ↓
Response Policy Evaluator (ResponsePolicyEngine)
   ↓
Approval Workflow / Authorization Gate
   ↓
Modular Safe Action Executor (ResponseActionRegistry)
   ↓
Safe Infrastructure Adapters (Network, Host, Account)
   ↓
Active Verification (verify)
   ↓
Automatic Rollback if failure occurs (ResponseRollbackService)
   ↓
Incident & Timeline Update (IncidentTimelineEvent)
   ↓
Immutable Audit Trail (ResponseAuditLog)
```

---

### 2. Core Subsystems

#### 2.1 Centralized Response Policy Engine (`backend/app/services/response_policy_service.py`)
- Configurable policies with risk score thresholds, severity tiers, allowed actions, cooldown windows, max actions per incident, and target restrictions.
- Strict tiering:
  - `LOW`: `NO_AUTOMATION` (prohibits automated execution)
  - `MEDIUM`: `ALERT_ONLY` (notifications, ticket generation)
  - `HIGH`: `REQUIRE_APPROVAL` (quarantine/block actions requiring analyst/admin sign-off)
  - `CRITICAL`: `ALLOW_AUTOMATED_RESPONSE` (pre-authorized emergency containment)

#### 2.2 Response Decision Engine (`backend/app/services/response_decision_service.py`)
- Evaluates multi-dimensional threat context: lateral movement, blast radius score, crown jewel index, IOC matches, credential abuse indicators.
- Recommends tailored containment actions (`ISOLATE_HOST`, `BLOCK_IP`, `QUARANTINE_ASSET`, `REVOKE_SESSION`, `DISABLE_ACCOUNT`) with explainable rationale.

#### 2.3 Modular Response Action Framework (`backend/app/services/response_actions/`)
- Unified abstract base `ResponseAction` requiring `validate()`, `preview()`, `execute()`, `verify()`, and `rollback()`.
- Safe adapters:
  - `NetworkEnforcementAdapter`: Manages perimeter IP drop rules without wildcard exposures.
  - `HostIsolationAdapter`: Manages host network quarantine while preserving SOC connectivity.
  - `AssetQuarantineAdapter`: Segregates crown jewel assets into restricted security zones.
  - `AccountResponseAdapter`: Revokes active sessions and locks compromised accounts without permanent data deletion.
- Fail-Closed Architecture: If an infrastructure adapter is unconfigured or unreachable, the action returns `BLOCKED` with an explicit reason (no fake success).

#### 2.4 Idempotency & Cooldown Engine
- Deduplicates incoming response actions using `X-Idempotency-Key` and `IdempotencyRecord`.
- Enforces per-incident and per-target cooldown windows (default 180s–300s) to prevent remediation feedback loops.

#### 2.5 Response Rollback Service (`backend/app/services/response_actions/rollback.py`)
- Restores affected infrastructure to its exact prior state for reversible actions, logging audit events and timeline records.

#### 2.6 Redis Response Actions Stream & Worker (`backend/app/response_worker.py`)
- Consumes from `sentinel:response-actions` stream under consumer group `sentinel:response:group`.
- Implements XACK and XAUTOCLAIM for reliable message processing with zero action loss.
