# AEGIVANTA — PHASE 20 ADVERSARIAL DEFENSE SPECIFICATION

## 1. Prompt Injection Defenses
Multi-layer regex and heuristic pattern guards detect jailbreak attempts (`DAN mode`, `system override`, `ignore previous instructions`, `bypass policy`). Malicious instructions are sanitized and logged to `AIAdversarialEvent`.

## 2. Training Data Poisoning Defense
Validates incoming feedback and telemetry against numeric sanity (NaN/Inf) and physical statistical bounds before incorporating into training pipelines.

## 3. Model Extraction Mitigation
Tracks inference burst velocity per tenant. Queries exceeding 50 EPS trigger adaptive confidence quantization and subtle jitter noise to prevent boundary reverse-engineering.
