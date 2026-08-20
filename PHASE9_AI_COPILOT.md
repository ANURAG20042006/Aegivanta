# Aegivanta Phase 9 — Enterprise AI Security Copilot

## 1. Copilot Reasoning & Architecture

The Aegivanta AI Security Copilot provides explainable attack reasoning, MITRE ATT&CK mapping, and automated evidence synthesis.

### Critical Safety Guardrails:
1. **Zero Unattended Command Execution**: All remediation recommendations produced by Copilot are marked `requires_approval: true` and must pass through human authorization and SOAR policy checks.
2. **Context Sanitization**: Automatically scrubs API keys, JWT tokens, sensor credentials, and passwords prior to reasoning.
3. **Strict Multi-Tenant Isolation**: Analysts can only query and analyze incidents and telemetry belonging to their active tenant workspace.
