# Aegivanta — Phase 16: Safe AI Analyst Assistant Specification

## 1. Safety Guardrails & Principles
- **No Unrestricted Execution**: AI recommendations cannot trigger arbitrary shell commands or unilateral destructive containment actions.
- **Human-Gated SOAR**: All containment proposals require human analyst approval (`requires_human_approval: true`).
- **Secret & Credential Scrubbing**: Context inputs and outputs are recursively sanitized with regex redaction (`[REDACTED_JWT]`, `[REDACTED_SENSOR_TOKEN]`, `[REDACTED_API_KEY]`).
- **Strict Tenant Isolation**: Inquiries cannot access incident, asset, or telemetry context outside the caller's authorized workspace.

## 2. Recommendation Schema
Every AI recommendation provides:
- `confidence`: Calibrated 0.0 to 1.0 confidence.
- `evidence`: Specific correlated alerts, IP entities, and telemetry indicators.
- `reasoning_summary`: Human-readable summary of the attack progression.
- `recommended_action`: Structured action descriptor (e.g. `ISOLATE_HOST`, `BLOCK_IP`).
- `requires_human_approval`: Explicit boolean gating flag.
