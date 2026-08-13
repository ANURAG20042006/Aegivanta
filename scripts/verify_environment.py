"""
SentinelAI — Environment Verification Script
Verifies all required runtime and test dependencies are correctly installed
with compatible versions. Exits with code 1 if any critical dependency fails.

Usage:
    python scripts/verify_environment.py
    (Run from project root: cd "major project" && python scripts/verify_environment.py)
"""
import sys
import importlib
import platform
from pathlib import Path

# Ensure project root is in sys.path for backend/ml package resolution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REQUIRED_PACKAGES = [
    # (import_name, pip_name, min_version_attr)
    ("fastapi", "fastapi", "__version__"),
    ("uvicorn", "uvicorn", "__version__"),
    ("pydantic", "pydantic", "__version__"),
    ("pydantic_settings", "pydantic-settings", "__version__"),
    ("sqlalchemy", "sqlalchemy", "__version__"),
    ("aiosqlite", "aiosqlite", "__version__"),
    ("asyncpg", "asyncpg", "__version__"),
    ("jose", "python-jose", "__version__"),
    ("passlib", "passlib", "__version__"),
    ("dotenv", "python-dotenv", "__version__"),
    ("numpy", "numpy", "__version__"),
    ("pandas", "pandas", "__version__"),
    ("scipy", "scipy", "__version__"),
    ("sklearn", "scikit-learn", "__version__"),
    ("xgboost", "xgboost", "__version__"),
    ("lightgbm", "lightgbm", "__version__"),
    ("catboost", "catboost", "__version__"),
    ("imblearn", "imbalanced-learn", "__version__"),
    ("shap", "shap", "__version__"),
    ("joblib", "joblib", "__version__"),
    ("matplotlib", "matplotlib", "__version__"),
    ("pytest", "pytest", "__version__"),
    ("httpx", "httpx", "__version__"),
]

OPTIONAL_PACKAGES = [
    ("torch", "torch", "__version__"),
    ("redis", "redis", "__version__"),
    ("reportlab", "reportlab", "__version__"),
    ("openpyxl", "openpyxl", "__version__"),
]

def check_package(import_name: str, pip_name: str, version_attr: str, required: bool = True):
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, version_attr, "unknown")
        if pip_name == "scikit-learn" and version != "unknown":
            # Strict scikit-learn 1.6.x constraint check — non-1.6.x fails verification
            parts = [int(p) for p in version.split(".")[:2] if p.isdigit()]
            if len(parts) >= 2 and (parts[0] != 1 or parts[1] != 6):
                print(f"  [FAIL] scikit-learn ({import_name}) == {version}")
                print(f"         Installed: {version}")
                print(f"         Required:  1.6.1 (>=1.6.0, <1.7.0)")
                print(f"         Reason:    Serialized ML artifacts (best_model.joblib) were generated with sklearn 1.6.1.")
                print(f"         Fix:       pip install scikit-learn==1.6.1 (or pip install -r requirements.txt inside .venv)")
                return False
        print(f"  [OK]  {pip_name} ({import_name}) == {version}")
        return True
    except ImportError as e:
        status = "FAIL" if required else "SKIP"
        print(f"  [{status}] {pip_name} ({import_name}) — NOT FOUND: {e}")
        if required:
            print(f"         Fix: pip install {pip_name} (or pip install -r requirements.txt inside .venv)")
        return not required

def main():
    print("=" * 60)
    print("SentinelAI Environment Verification")
    print(f"Python:   {platform.python_version()} ({sys.executable})")
    print(f"Platform: {platform.platform()}")
    print("=" * 60)

    print("\n[REQUIRED PACKAGES]")
    all_pass = True
    for args in REQUIRED_PACKAGES:
        ok = check_package(*args, required=True)
        if not ok:
            all_pass = False

    print("\n[OPTIONAL PACKAGES]")
    for args in OPTIONAL_PACKAGES:
        check_package(*args, required=False)

    # Verify critical imports that are used in application startup
    print("\n[CRITICAL APPLICATION IMPORTS]")
    critical = [
        ("backend.app.config", "settings"),
        ("ml.metrics.security_metrics", "calculate_macro_fpr"),
        ("ml.schema.feature_schema", "DEFAULT_FEATURE_SCHEMA"),
        ("ml.dataset.generator", "CICIDS2017DataGenerator"),
    ]
    for module_name, attr_name in critical:
        try:
            mod = importlib.import_module(module_name)
            getattr(mod, attr_name)
            print(f"  [OK]  {module_name}.{attr_name}")
        except Exception as e:
            print(f"  [FAIL] {module_name}.{attr_name} — {e}")
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("RESULT: ALL REQUIRED DEPENDENCIES VERIFIED OK")
        sys.exit(0)
    else:
        print("RESULT: ONE OR MORE REQUIRED DEPENDENCIES MISSING — see above")
        sys.exit(1)

if __name__ == "__main__":
    main()
