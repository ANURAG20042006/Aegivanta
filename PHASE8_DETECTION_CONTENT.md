# Aegivanta Phase 8 — Detection Content & Detection-as-Code Platform

## 1. Detection-as-Code Framework

Aegivanta Phase 8 enables versioned, declarative detection rules defined as structured AST logic with MITRE ATT&CK mapping and false-positive guidance.

### Rule DSL Schema
```json
{
  "rule_code": "AEG-R-2026-001",
  "name": "Distributed SSH Password Spraying",
  "version": "1.0.0",
  "severity": "HIGH",
  "confidence": 0.90,
  "mitre_attack_mappings": {
    "tactics": ["Credential Access", "Initial Access"],
    "techniques": ["T1110.003", "T1078"]
  },
  "rule_dsl": {
    "and": [
      {"field": "data.event_type", "op": "eq", "value": "AUTH_EVENT"},
      {"field": "data.success", "op": "eq", "value": false}
    ]
  }
}
```
