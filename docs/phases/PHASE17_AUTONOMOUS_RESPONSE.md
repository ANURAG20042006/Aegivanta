# Aegivanta — Phase 17: Autonomous Response Orchestration Specification

## 1. Risk-Based Autonomy Levels
1. `LEVEL_0_OBSERVE`: Telemetry ingestion only; all automated and autonomous responses suppressed.
2. `LEVEL_1_RECOMMEND`: AI proposes remediation actions for manual analyst execution.
3. `LEVEL_2_APPROVAL_REQUIRED`: Default enterprise tier; all containment actions require human approval.
4. `LEVEL_3_LIMITED_AUTONOMOUS`: Autonomous containment of non-critical assets; critical assets gated.
5. `LEVEL_4_FULL_AUTONOMOUS`: High-velocity automated containment without mandatory human gating.

## 2. API Endpoints
- `GET /api/v1/autonomous-response/policy`
- `PUT /api/v1/autonomous-response/policy`
- `POST /api/v1/autonomous-response/simulate`
- `POST /api/v1/autonomous-response/execute`
- `POST /api/v1/autonomous-response/{id}/rollback`

## 3. Reversible Rollback Transactions
Every reversible action records original and modified system states and an executable rollback operation (`ResponseRollback`).
