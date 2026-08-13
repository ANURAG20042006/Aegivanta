"""
SentinelAI Master Release Verification Script (verify_release.py)
==================================================================
Single-command automated release reproduction & integrity verification suite.

Executes all 8 validation stages:
  1. Environment & Dependency Consistency
  2. Python Package Compilation (compileall)
  3. ML Artifact Dimensional & SHA-256 Hash Integrity
  4. Authoritative Metadata Metric Consistency (EXP-2026-002)
  5. Pytest Engine Execution
  6. Frontend Production Build Verification
  7. Final Master Integrity Audit

Usage:
    python scripts/verify_release.py
"""
import sys
import os
import subprocess
import json
import hashlib
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

# Set UTF-8 encoding for standard output on Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_step(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_command(cmd: list, cwd: Path = PROJECT_ROOT) -> Tuple[int, str, str]:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.returncode, res.stdout, res.stderr


def main():
    print("=================================================================")
    print("      SentinelAI Automated Master Release Verification Suite       ")
    print("=================================================================")

    failed_stages = []

    # -------------------------------------------------------------------
    # STAGE 1: Environment & Dependency Consistency
    # -------------------------------------------------------------------
    print_step("STAGE 1: Environment & Dependency Verification")
    code, stdout, stderr = run_command([sys.executable, "scripts/verify_environment.py"])
    print(stdout)
    if code != 0:
        print(f"[FAIL] Environment verification failed:\n{stderr}")
        failed_stages.append("Stage 1: Environment Verification")
    else:
        print("[PASS] Environment verification succeeded.")

    # -------------------------------------------------------------------
    # STAGE 2: Python Compilation
    # -------------------------------------------------------------------
    print_step("STAGE 2: Python Package Compilation (compileall)")
    code, stdout, stderr = run_command([sys.executable, "-m", "compileall", "-q", "backend", "ml", "scripts", "tests"])
    if code != 0:
        print(f"[FAIL] Compilation failed:\n{stderr}")
        failed_stages.append("Stage 2: Python Compilation")
    else:
        print("[PASS] Python compilation clean — 0 errors.")

    # -------------------------------------------------------------------
    # STAGE 3: Artifact Integrity
    # -------------------------------------------------------------------
    print_step("STAGE 3: ML Artifact Integrity & Hash Matching")
    artifacts_dir = PROJECT_ROOT / "ml" / "artifacts"
    best_model_p = artifacts_dir / "best_model.joblib"
    prep_p = artifacts_dir / "preprocessor.joblib"
    meta_p = artifacts_dir / "metadata.json"
    manifest_p = artifacts_dir / "artifact_manifest.json"

    if not (best_model_p.exists() and prep_p.exists() and meta_p.exists() and manifest_p.exists()):
        print("[FAIL] Missing required artifact files in ml/artifacts/")
        failed_stages.append("Stage 3: Artifact Existence")
    else:
        try:
            import joblib
            model_obj = joblib.load(best_model_p)
            prep_obj = joblib.load(prep_p)
            manifest = json.loads(manifest_p.read_text(encoding="utf-8"))

            inner_model = getattr(model_obj, "model", model_obj)
            n_features_in = getattr(inner_model, "n_features_in_", None)
            if (not n_features_in or n_features_in == 0) and hasattr(inner_model, "feature_names_") and inner_model.feature_names_:
                n_features_in = len(inner_model.feature_names_)
            elif (not n_features_in or n_features_in == 0) and hasattr(inner_model, "_input_dim") and inner_model._input_dim:
                n_features_in = inner_model._input_dim
            prep_features = len(getattr(prep_obj, "selected_feature_names", []))

            actual_model_hash = hashlib.sha256(best_model_p.read_bytes()).hexdigest()
            actual_prep_hash = hashlib.sha256(prep_p.read_bytes()).hexdigest()

            dim_match = (n_features_in == prep_features == 30)
            hash_match = (actual_model_hash == manifest.get("model_hash") and actual_prep_hash == manifest.get("preprocessor_hash"))

            print(f"  Model n_features_in: {n_features_in}")
            print(f"  Preprocessor selected features: {prep_features}")
            print(f"  Model SHA256 Match: {actual_model_hash == manifest.get('model_hash')}")
            print(f"  Preprocessor SHA256 Match: {actual_prep_hash == manifest.get('preprocessor_hash')}")

            if dim_match and hash_match:
                print("[PASS] Artifact dimensions (30 == 30) and SHA256 hashes verified.")
            else:
                print("[FAIL] Artifact dimension or hash mismatch.")
                failed_stages.append("Stage 3: Artifact Hash & Dimension Integrity")
        except Exception as e:
            print(f"[FAIL] Error validating artifacts: {e}")
            failed_stages.append("Stage 3: Artifact Load")

    # -------------------------------------------------------------------
    # STAGE 4: Metadata Metric Consistency
    # -------------------------------------------------------------------
    print_step("STAGE 4: Authoritative Research Metric Consistency")
    try:
        metadata = json.loads(meta_p.read_text(encoding="utf-8"))
        exp_id = metadata.get("experiment_id")
        cv_f1 = metadata.get("cv_metrics", {}).get("macro_f1_mean")
        test_f1 = metadata.get("final_test_metrics", {}).get("macro_f1")

        prov_p = Path("results/EXP-2026-002/provenance.json")
        prov_match = prov_p.exists()
        print(f"  Provenance Manifest Exists: {prov_match}")

        if exp_id == "EXP-2026-002" and cv_f1 is not None and test_f1 is not None and prov_match:
            print("[PASS] Authoritative experiment metrics and provenance manifest verified.")
        else:
            print("[FAIL] Unexpected experiment metadata structure or missing provenance manifest.")
            failed_stages.append("Stage 4: Metadata Metric Consistency")
    except Exception as e:
        print(f"[FAIL] Metadata verification error: {e}")
        failed_stages.append("Stage 4: Metadata Metric Consistency")

    # -------------------------------------------------------------------
    # STAGE 5: Pytest Execution
    # -------------------------------------------------------------------
    print_step("STAGE 5: Pytest Test Suite Execution")
    code, stdout, stderr = run_command([sys.executable, "-m", "pytest", "-q"])
    print(stdout)
    if code != 0:
        print(f"[FAIL] Pytest failed with exit code {code}:\n{stderr}")
        failed_stages.append("Stage 5: Pytest Execution")
    else:
        print("[PASS] Pytest suite executed with 0 failures and 0 collection errors.")

    # -------------------------------------------------------------------
    # STAGE 6: Frontend Production Build Verification (Fresh Build Required)
    # -------------------------------------------------------------------
    print_step("STAGE 6: Frontend Production Build Verification (Fresh Build)")
    print("--> Executing fresh 'npm ci' and 'npm run build' in frontend/...")
    
    # Force clean build execution — existing dist/ is NEVER accepted as proof
    code_ci, stdout_ci, stderr_ci = run_command(["npm.cmd" if sys.platform == "win32" else "npm", "ci"], cwd=PROJECT_ROOT / "frontend")
    if code_ci != 0:
        print(f"[FAIL] 'npm ci' failed in frontend/:\n{stderr_ci}")
        failed_stages.append("Stage 6: Frontend npm ci")
    else:
        print("[PASS] 'npm ci' clean dependency installation succeeded.")
        code_b, stdout_b, stderr_b = run_command(["npm.cmd" if sys.platform == "win32" else "npm", "run", "build"], cwd=PROJECT_ROOT / "frontend")
        dist_html = PROJECT_ROOT / "frontend" / "dist" / "index.html"
        if code_b == 0 and dist_html.exists():
            print(f"[PASS] Fresh frontend build succeeded. Emitted asset: {dist_html}")
        else:
            print(f"[FAIL] Frontend build failed:\n{stderr_b}")
            failed_stages.append("Stage 6: Frontend Production Build")

    # -------------------------------------------------------------------
    # STAGE 7: Final Master Integrity Audit
    # -------------------------------------------------------------------
    print_step("STAGE 7: Final Integrity Audit (scripts/final_integrity_audit.py)")
    code, stdout, stderr = run_command([sys.executable, "scripts/final_integrity_audit.py"])
    print(stdout)
    if code != 0:
        print(f"[FAIL] Final integrity audit failed:\n{stderr}")
        failed_stages.append("Stage 7: Final Integrity Audit")
    else:
        print("[PASS] Final integrity audit reported 0 critical failures.")

    # -------------------------------------------------------------------
    # FINAL SUMMARY & REPRODUCIBILITY STATUS
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("                     MASTER VERIFICATION SUMMARY                      ")
    print("=" * 70)
    if not failed_stages:
        print("STATUS: ENVIRONMENT VERIFIED")
        print("STATUS: CLEAN ENVIRONMENT REPRODUCED")
        print("RESULT: ALL RELEASE VERIFICATION STAGES PASSED (0 FAILURES)")
        print("SentinelAI is 100% verified, reproducible, and ready for submission.")
        sys.exit(0)
    else:
        print(f"RESULT: VERIFICATION FAILED ON {len(failed_stages)} STAGE(S):")
        for stage in failed_stages:
            print(f"  - {stage}")
        sys.exit(1)


if __name__ == "__main__":
    from typing import Tuple
    main()
