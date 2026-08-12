# SentinelAI Phase 12 Baseline Repository Audit Report

**Audit Date**: 2026-08-13  
**Audit Scope**: Pre-remediation repository state prior to Phase 12 Master Remediation  
**Environment**: Python 3.11, Node.js 20+, Windows 11  

---

## 1. Credential & Security Audit Findings

### A. Base64-Obfuscated Passwords Found in Source Code
- **`backend/app/main.py`**:
  - `os.environ.get("SENTINEL_ADMIN_PASSWORD") or base64.b64decode(b"QWRtaW5TZWN1cmUyMDI2IQ==").decode()`
  - `os.environ.get("SENTINEL_ANALYST_PASSWORD") or base64.b64decode(b"QW5hbHlzdFNlY3VyZTIwMjYh").decode()`
  - `os.environ.get("SENTINEL_VIEWER_PASSWORD") or base64.b64decode(b"Vmlld2VyU2VjdXJlMjAyNiE=").decode()`
- **`backend/app/reset_users.py`**:
  - `admin_pass = os.environ.get("SENTINEL_ADMIN_PASSWORD", base64.b64decode(b"QWRtaW5TZWN1cmUyMDI2IQ==").decode())`
  - `analyst_pass = os.environ.get("SENTINEL_ANALYST_PASSWORD", base64.b64decode(b"QW5hbHlzdFNlY3VyZTIwMjYh").decode())`
  - `viewer_pass = os.environ.get("SENTINEL_VIEWER_PASSWORD", base64.b64decode(b"Vmlld2VyU2VjdXJlMjAyNiE=").decode())`
- **`frontend/src/pages/Login.tsx`**:
  - Quick role fill buttons called `atob('QWRtaW5TZWN1cmUyMDI2IQ==')`, `atob('QW5hbHlzdFNlY3VyZTIwMjYh')`, `atob('Vmlld2VyU2VjdXJlMjAyNiE=')`.
- **Integration Tests**:
  - `tests/integration/test_app_lifespan_flow.py` and `tests/integration_test_runner.py` used `base64.b64decode` fallbacks.

### B. Findings Assessment
Base64 string decoding is not encryption. Exposing default credentials in client-side React bundles or server source files breaks security isolation. All Base64 decoders must be replaced with strict environment variable loading or ephemeral random development generation.

---

## 2. Machine Learning & Experiment Consistency Findings

### A. Experiment ID Discrepancies
- Previous iterations produced mixed experiment identifiers across `EXP-2026-001` artifacts and root `ml/artifacts/metadata.json`.
- `metadata.json` recorded `Naive Bayes` champion selected during Phase 11 multi-metric CV.
- `research_summary.json` in `results/EXP-2026-001/` contained legacy run data.

### B. Action Item for Phase 12
All stale/previous experiment outputs will be archived into `results/archive/`. A single authoritative clean regeneration (`EXP-2026-002`) will produce all artifacts in `results/EXP-2026-002/` and `ml/artifacts/`.

---

## 3. Central FPR & Metrics Module Need
While `1 - recall` was fixed in `model_selector.py` during Phase 11, the repository lacks a single centralized `ml/metrics/security_metrics.py` module. Creating this module will unify FPR, Macro FPR, Weighted FPR, Precision, Recall, and F1 calculations across all pipeline steps.
