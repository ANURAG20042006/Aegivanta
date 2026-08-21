# PHASE 30 — OWASP TOP 10 FOR LLMS MAPPING & COVERAGE

## 1. OWASP Top 10 for LLMs Coverage Matrix

| OWASP ID | Vulnerability Title | Aegivanta Mitigation Control |
|----------|---------------------|------------------------------|
| **LLM01** | Prompt Injection | Bidirectional Guardrail Firewall with heuristic pattern scoring. |
| **LLM02** | Sensitive Information Disclosure | In-flight PII & secret redactor (SSN, credit cards, API keys). |
| **LLM03** | Supply Chain Vulnerabilities | Signed model weight hashes and verified provenance. |
| **LLM04** | Data and Model Poisoning | Vector DB anomaly scoring and fine-tune dataset auditing. |
| **LLM05** | Improper Output Handling | Output sanitization stripping `<script>` and malicious markdown. |
| **LLM06** | Excessive Agency | Strict capability scoping and mandatory SOC approval gates. |
| **LLM07** | System Prompt Leakage | Interception of prompt exfiltration patterns. |
| **LLM08** | Vector & Embedding Weaknesses | Tenant-isolated vector collection governance and audits. |
| **LLM09** | Misinformation / Hallucination | Grounding score verification and source citation enforcement. |
| **LLM10** | Unbounded Consumption (DoS) | Per-prompt token limits (max 4096 tokens) and rate limiting. |
