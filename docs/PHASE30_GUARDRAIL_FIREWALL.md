# PHASE 30 — LLM GUARDRAIL FIREWALL CONFIGURATION

## 1. Guardrail Engine Architecture

- **Bidirectional Interceptor**: Analyzes inbound user prompts and outbound model responses.
- **Latency Budget**: Sub-15ms overhead per prompt inspection.
- **Verdict States**:
  - `ALLOW`: Clean prompt forwarded directly.
  - `SANITIZED`: PII masked, clean text forwarded.
  - `BLOCKED`: High injection probability, response rejected with safety advisory.
