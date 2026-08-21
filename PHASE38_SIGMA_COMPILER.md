# PHASE 38 — SIGMA / YARA-L COMPILER SPECIFICATION

## 1. Compiler Grammar

- Parses logsource (service, product, category).
- Evaluates detection selections, filters, and boolean conditions (`selection and not filter`).
- Emits target runtime queries for the underlying streaming query engine.
