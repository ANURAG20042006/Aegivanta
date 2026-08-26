# 🛡️ SentinelAI Phase 3 — Feature Contract & Artifact Integrity Audit Report

**Audit Date**: August 12, 2026  
**Schema Contract Version**: `schema-v1.0`  
**Inference Failure Code**: `HTTP 422 Unprocessable Entity` (Schema Violation), `HTTP 503 Service Unavailable` (Artifact Error)  

---

## 1. Executive Summary & Verification

Phase 3 establishes a strict **Feature Schema Contract** and **Model Artifact Integrity Validator**:
1. Invalid input vectors missing required features or containing out-of-range/invalid dtypes are rejected immediately with `HTTP 422 Unprocessable Entity` before invoking model inference.
2. Artifact compatibility is verified prior to prediction. Missing `metadata.json`, corrupted model weights, or mismatched `feature_schema_version` / `preprocessing_version` raise controlled `HTTP 503 Service Unavailable` errors.
3. All production heuristic rules (`if port == ...`, `if packet_count > ...`) have been removed from the classification path.

---

## 2. Feature Schema Contract & Range Specification

| Feature Name | Exact Ordering | Dtype | Required | Allowed Range Bounds |
| :--- | :---: | :---: | :---: | :---: |
| **Destination Port** | Index 0 | `float64` | Yes | `[0.0, 65535.0]` |
| **Flow Duration** | Index 1 | `float64` | Yes | `[0.0, 864000000.0]` |
| **Total Fwd Packets** | Index 2 | `float64` | No | `[0.0, 10000000.0]` |
| **Total Backward Packets** | Index 3 | `float64` | No | `[0.0, 10000000.0]` |
| **Flow Bytes/s** | Index 6 | `float64` | No | `[0.0, 1e12]` |
| **Flow Packets/s** | Index 7 | `float64` | Yes | `[0.0, 1e9]` |
| **Packet Length Mean** | Index 8 | `float64` | Yes | `[0.0, 65535.0]` |
| **SYN Flag Count** | Index 10 | `float64` | Yes | `[0.0, 100.0]` |

---

## 3. Automated Test Suite Proof (`tests/pytest/test_phase3_contract_and_artifacts.py`)

- `test_valid_vector`: Validates proper vector schema pass-through.
- `test_missing_feature`: Verifies rejection when required feature is absent.
- `test_extra_feature`: Verifies support for optional custom features.
- `test_reordered_feature`: Verifies order-agnostic dictionary key mapping.
- `test_invalid_dtype`: Rejects nested dictionaries/lists.
- `test_invalid_range`: Rejects port values outside `[0, 65535]`.
- `test_schema_mismatch`: Rejects incompatible schema version in artifact.
- `test_missing_model_version`: Rejects metadata missing model version.
- `test_corrupted_artifact`: Rejects empty or corrupted metadata.
- `test_incompatible_preprocessing_version`: Rejects legacy un-isolated preprocessing.

```bash
# Execution verification
python -m pytest tests/pytest/test_phase3_contract_and_artifacts.py -v
```
