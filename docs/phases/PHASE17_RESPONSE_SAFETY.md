# Aegivanta — Phase 17: Autonomous Response Safety & Blast-Radius Guards

## 1. Safety Guardrails
1. **Tenant Policy Enforcement**: Every action must be present in the tenant's allowlist.
2. **Autonomy Level Bound**: Dangerous actions cannot exceed the tenant's maximum autonomy level.
3. **Blast-Radius Guard**: Automatically gates actions that affect critical assets or exceed maximum blast radius limits.
4. **Idempotency & Replay Protection**: Deterministic execution signatures prevent duplicate dispatches.
5. **Reversible Rollback Transactions**: State snapshots guarantee clean rollbacks.
