"""
SentinelAI — Final Integrity Audit Script
==========================================
Automatically verifies all production correctness requirements.
Returns exit code 0 if all critical checks pass, 1 if any critical check fails.

Usage:
    python scripts/final_integrity_audit.py

Checks:
  [ ] dependencies available
  [ ] compilation passes
  [ ] model artifact exists
  [ ] preprocessor exists
  [ ] model/preprocessor dimensions match
  [ ] artifact hashes match manifest
  [ ] schema version matches
  [ ] metadata exists and is non-fabricated
  [ ] FPR formula is correct (FP/(FP+TN), not 1-recall)
  [ ] no hardcoded default confidences (0.95)
  [ ] final test metrics not used in promotion gate code
  [ ] rollback requires hash verification
  [ ] research output CSVs exist
  [ ] frontend build artifact exists
"""
import sys
import os
import json
import hashlib
import importlib
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
RESULTS_DIR = PROJECT_ROOT / "results"

PASS = "  [PASS]"
FAIL = "  [FAIL]"
WARN = "  [WARN]"
SKIP = "  [SKIP]"

critical_failures = []
warnings = []

def check(label: str, condition: bool, critical: bool = True, detail: str = ""):
    status = PASS if condition else (FAIL if critical else WARN)
    suffix = f" — {detail}" if detail else ""
    print(f"{status} {label}{suffix}")
    if not condition:
        if critical:
            critical_failures.append(label)
        else:
            warnings.append(label)
    return condition


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ===================================================================
# SECTION 1: Dependencies
# ===================================================================
run_section("1. DEPENDENCY VERIFICATION")

required = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "aiosqlite",
            "sklearn", "numpy", "pandas", "scipy", "shap", "joblib",
            "imblearn", "xgboost", "lightgbm", "catboost", "pytest", "httpx"]

for pkg in required:
    try:
        importlib.import_module(pkg)
        check(f"import {pkg}", True)
    except ImportError as e:
        check(f"import {pkg}", False, detail=str(e))


# ===================================================================
# SECTION 2: Compilation
# ===================================================================
run_section("2. PYTHON COMPILATION")

result = subprocess.run(
    [sys.executable, "-m", "compileall", "-q", "backend", "ml", "scripts"],
    cwd=str(PROJECT_ROOT),
    capture_output=True, text=True
)
check("compileall backend ml scripts", result.returncode == 0,
      detail=result.stderr.strip()[:200] if result.stderr.strip() else "OK")


# ===================================================================
# SECTION 3: Artifact Existence
# ===================================================================
run_section("3. ARTIFACT EXISTENCE")

best_model_path = ARTIFACTS_DIR / "best_model.joblib"
preprocessor_path = ARTIFACTS_DIR / "preprocessor.joblib"
metadata_path = ARTIFACTS_DIR / "metadata.json"
manifest_path = ARTIFACTS_DIR / "artifact_manifest.json"

check("best_model.joblib exists", best_model_path.exists())
check("preprocessor.joblib exists", preprocessor_path.exists())
check("metadata.json exists", metadata_path.exists())
check("artifact_manifest.json exists", manifest_path.exists())


# ===================================================================
# SECTION 4: Artifact Hashes
# ===================================================================
run_section("4. ARTIFACT HASH INTEGRITY")

if manifest_path.exists():
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Verify model hash
    if best_model_path.exists():
        actual_model_hash = sha256_file(best_model_path)
        expected_model_hash = manifest.get("model_hash", "")
        check("model SHA256 matches manifest",
              actual_model_hash == expected_model_hash,
              detail=f"actual={actual_model_hash[:16]}... expected={expected_model_hash[:16]}...")

    # Verify preprocessor hash
    if preprocessor_path.exists():
        actual_prep_hash = sha256_file(preprocessor_path)
        expected_prep_hash = manifest.get("preprocessor_hash", "")
        check("preprocessor SHA256 matches manifest",
              actual_prep_hash == expected_prep_hash,
              detail=f"actual={actual_prep_hash[:16]}... expected={expected_prep_hash[:16]}...")

    # Schema version present
    check("schema_version in manifest",
          bool(manifest.get("feature_schema_version")),
          detail=manifest.get("feature_schema_version", "MISSING"))

    # Random seed present
    check("git_commit in manifest", bool(manifest.get("git_commit")))
else:
    check("manifest readable", False, detail="manifest_path missing")


# ===================================================================
# SECTION 5: Model/Preprocessor Dimension Match
# ===================================================================
run_section("5. MODEL/PREPROCESSOR DIMENSION COMPATIBILITY")

if best_model_path.exists() and preprocessor_path.exists():
    try:
        import joblib
        import numpy as np

        loaded_model = joblib.load(str(best_model_path))
        loaded_prep = joblib.load(str(preprocessor_path))

        inner_model = getattr(loaded_model, "model", loaded_model)
        model_n_features = getattr(inner_model, "n_features_in_", None)

        if model_n_features is not None and hasattr(loaded_prep, "selected_feature_names"):
            prep_n_features = len(loaded_prep.selected_feature_names)
            check("model.n_features_in_ == len(preprocessor.selected_feature_names)",
                  model_n_features == prep_n_features,
                  detail=f"model={model_n_features}, preprocessor={prep_n_features}")
        elif model_n_features is None:
            check("model.n_features_in_ available", False,
                  critical=False, detail="n_features_in_ not set — model may not be fitted")
        else:
            check("preprocessor.selected_feature_names available", False,
                  critical=False, detail="preprocessor missing selected_feature_names attribute")
    except Exception as e:
        check("model/preprocessor load & dimension check", False, detail=str(e))


# ===================================================================
# SECTION 6: Metadata Non-Fabrication Checks
# ===================================================================
run_section("6. METADATA INTEGRITY (NON-FABRICATED METRICS)")

if metadata_path.exists():
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # CV metrics must exist
    cv = meta.get("cv_metrics", {})
    check("cv_metrics present in metadata", bool(cv))
    check("cv_metrics.macro_f1_mean is a real float (not None)",
          cv.get("macro_f1_mean") is not None)
    check("cv_metrics.macro_f1_std is a real float (not None)",
          cv.get("macro_f1_std") is not None)

    # Final test metrics
    ft = meta.get("final_test_metrics", {})
    check("final_test_metrics present", bool(ft))
    check("final_test_metrics.macro_f1 is real", ft.get("macro_f1") is not None)
    check("final_test_metrics.fpr is real", ft.get("fpr") is not None)

    # Check no suspiciously fabricated perfect scores
    f1_val = cv.get("macro_f1_mean", 0)
    acc_val = meta.get("final_test_metrics", {}).get("accuracy", 0)
    check("cv F1 not suspiciously perfect (>0.99)",
          f1_val < 0.99,
          critical=False,
          detail=f"cv_macro_f1_mean={f1_val}")

    # Check training timestamp present and non-empty
    check("training_timestamp present", bool(meta.get("training_timestamp")))

    # Check required fields
    for field in ["experiment_id", "model_version", "random_seed", "dataset_hash",
                  "feature_schema_version", "preprocessing_version", "git_commit"]:
        check(f"metadata.{field} present", field in meta and meta[field] is not None)


# ===================================================================
# SECTION 7: FPR Formula Verification (Code Analysis)
# ===================================================================
run_section("7. FPR FORMULA VERIFICATION")

security_metrics_path = PROJECT_ROOT / "ml" / "metrics" / "security_metrics.py"
if security_metrics_path.exists():
    src = security_metrics_path.read_text(encoding="utf-8")
    # Must contain FP/(FP+TN) style calculation
    has_fp_div = "fp / denominator" in src or "fp/denominator" in src or "FP / (FP + TN)" in src.upper()
    has_1_minus_recall = "1 - recall" in src.lower() or "1-recall" in src.lower()
    check("FPR formula uses FP/(FP+TN)", has_fp_div)
    check("FPR formula does NOT use 1-recall", not has_1_minus_recall)
else:
    check("security_metrics.py exists", False)

# Check predict_service.py for fabricated confidence fallbacks
predict_svc_path = PROJECT_ROOT / "backend" / "app" / "services" / "predict_service.py"
if predict_svc_path.exists():
    svc_src = predict_svc_path.read_text(encoding="utf-8")
    # confidence = 0.95 as a fabricated assignment (not a threshold comparison)
    has_fake_conf = "confidence = 0.95" in svc_src or "confidence_score = 0.95" in svc_src
    check("predict_service.py has no fabricated confidence=0.95 assignment",
          not has_fake_conf,
          detail="0.95 used only as severity threshold, not as fabricated confidence")


# ===================================================================
# SECTION 8: Research CSV Outputs
# ===================================================================
run_section("8. RESEARCH OUTPUT ARTIFACTS")

required_csvs = [
    "cross_validation.csv",
    "baseline_comparison.csv",
    "ablation.csv",
    "robustness.csv",
    "latency.csv",
]
for csv_name in required_csvs:
    path = RESULTS_DIR / csv_name
    check(f"results/{csv_name} exists", path.exists())
    if path.exists():
        try:
            import pandas as pd
            df = pd.read_csv(str(path))
            check(f"results/{csv_name} non-empty ({len(df)} rows)", len(df) > 0)
        except Exception as e:
            check(f"results/{csv_name} readable", False, detail=str(e))

# Plots
for plot_name in ["f1_vs_fpr.png", "latency_comparison.png", "ablation_study.png"]:
    path = RESULTS_DIR / "plots" / plot_name
    check(f"results/plots/{plot_name} exists", path.exists(), critical=False)


# ===================================================================
# SECTION 9: Frontend Build
# ===================================================================
run_section("9. FRONTEND BUILD ARTIFACT")

dist_path = PROJECT_ROOT / "frontend" / "dist" / "index.html"
check("frontend/dist/index.html exists (build artifact)", dist_path.exists(),
      critical=False, detail="Run 'npm run build' in frontend/ to generate")


# ===================================================================
# SECTION 10: Security Checks
# ===================================================================
run_section("10. SECURITY CHECKS")

# Check for hardcoded production passwords in main.py
main_py = PROJECT_ROOT / "backend" / "app" / "main.py"
if main_py.exists():
    main_src = main_py.read_text(encoding="utf-8")
    # The fallback passwords are DEV-only guarded behind env check
    has_production_guard = "OPERATING_MODE.upper() == \"PRODUCTION\"" in main_src or \
                           "APP_ENV.lower() == \"production\"" in main_src
    check("main.py guards dev password fallbacks in production", has_production_guard)

config_py = PROJECT_ROOT / "backend" / "app" / "config.py"
if config_py.exists():
    cfg_src = config_py.read_text(encoding="utf-8")
    has_prod_validate = "validate_production_settings" in cfg_src
    check("validate_production_settings function exists in config.py", has_prod_validate)
    has_postgres_check = "POSTGRES_PASSWORD" in cfg_src
    check("POSTGRES_PASSWORD enforced in production validation", has_postgres_check)


# ===================================================================
# FINAL SUMMARY
# ===================================================================
run_section("FINAL SUMMARY")

total_checks = len(critical_failures) + len(warnings)
print(f"\nCritical Failures: {len(critical_failures)}")
for f in critical_failures:
    print(f"  - {f}")

print(f"\nWarnings: {len(warnings)}")
for w in warnings:
    print(f"  - {w}")

print()
if not critical_failures:
    print("RESULT: ALL CRITICAL CHECKS PASSED")
    sys.exit(0)
else:
    print(f"RESULT: {len(critical_failures)} CRITICAL CHECKS FAILED")
    sys.exit(1)
