"""
SentinelAI — Environment Verification Script
Verifies all required runtime and test dependencies are correctly installed
with compatible versions. Exits with code 1 if any critical dependency fails.

Usage:
    python scripts/verify_environment.py
    (Run from project root: cd "major project" && python scripts/verify_environment.py)

Artifact-critical packages (wrong version = FAIL):
    scikit-learn == 1.6.1   (serialized .joblib artifacts)
    numpy        == 2.2.2
    pandas       == 2.2.3

Bounded-compatible packages (outside range = FAIL):
    scipy, joblib, xgboost, lightgbm, catboost, shap, imbalanced-learn
"""
import sys
import importlib
import platform
from pathlib import Path

# Ensure project root is in sys.path for backend/ml package resolution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Artifact-critical packages: EXACT pinned version required
# Format: (import_name, pip_name, required_exact_version)
# ---------------------------------------------------------------------------
ARTIFACT_CRITICAL = [
    ("sklearn",  "scikit-learn",   "1.6.1"),
    ("numpy",    "numpy",          "2.2.2"),
    ("pandas",   "pandas",         "2.2.3"),
]

# ---------------------------------------------------------------------------
# Bounded-compatible packages: version must be within [min_ver, max_ver_excl)
# Format: (import_name, pip_name, min_ver_tuple, max_ver_tuple or None, tested_version)
# ---------------------------------------------------------------------------
BOUNDED_PACKAGES = [
    # (import, pip_name, min_tuple, max_tuple_exclusive, tested_version)
    ("scipy",    "scipy",          (1, 15, 0), (2, 0, 0), "1.15.2"),
    ("joblib",   "joblib",         (1, 4, 0),  (2, 0, 0), "1.4.2"),
    ("xgboost",  "xgboost",        (3, 0, 0),  (4, 0, 0), "3.0.1"),
    ("lightgbm", "lightgbm",       (4, 0, 0),  (5, 0, 0), "4.7.0"),
    ("catboost", "catboost",       (1, 2, 0),  (2, 0, 0), "1.2.8"),
    ("shap",     "shap",           (0, 51, 0), (1, 0, 0), "0.51.0"),
    ("imblearn", "imbalanced-learn",(0, 14, 0),(1, 0, 0), "0.14.2"),
]

# ---------------------------------------------------------------------------
# Other required packages (existence + importability enforced, version logged)
# ---------------------------------------------------------------------------
REQUIRED_PACKAGES = [
    ("fastapi",          "fastapi",           "__version__"),
    ("uvicorn",          "uvicorn",           "__version__"),
    ("pydantic",         "pydantic",          "__version__"),
    ("pydantic_settings","pydantic-settings", "__version__"),
    ("sqlalchemy",       "sqlalchemy",        "__version__"),
    ("aiosqlite",        "aiosqlite",         "__version__"),
    ("asyncpg",          "asyncpg",           "__version__"),
    ("jose",             "python-jose",       "__version__"),
    ("passlib",          "passlib",           "__version__"),
    ("dotenv",           "python-dotenv",     "__version__"),
    ("matplotlib",       "matplotlib",        "__version__"),
    ("pytest",           "pytest",            "__version__"),
    ("httpx",            "httpx",             "__version__"),
    ("fakeredis",        "fakeredis",         "__version__"),
]

OPTIONAL_PACKAGES = [
    ("torch",      "torch",      "__version__"),
    ("redis",      "redis",      "__version__"),
    ("reportlab",  "reportlab",  "__version__"),
    ("openpyxl",   "openpyxl",   "__version__"),
]


def _parse_ver(ver_str: str):
    """Parse a version string into a tuple of ints for comparison."""
    parts = []
    for p in ver_str.split(".")[:3]:
        digits = "".join(c for c in p if c.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def check_artifact_critical(import_name: str, pip_name: str, required_ver: str) -> bool:
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "unknown")
        if version == required_ver:
            print(f"  [OK]  {pip_name} ({import_name}) == {version}  [artifact-pinned]")
            return True
        else:
            print(f"  [FAIL] {pip_name} ({import_name}) == {version}")
            print(f"         Required (artifact-critical): {required_ver}")
            print(f"         Artifacts (best_model.joblib, preprocessor.joblib) were")
            print(f"         serialized with {pip_name}=={required_ver}.")
            print(f"         Fix: pip install {pip_name}=={required_ver}")
            return False
    except ImportError as e:
        print(f"  [FAIL] {pip_name} ({import_name}) — NOT FOUND: {e}")
        print(f"         Fix: pip install -r requirements.txt")
        return False


def check_bounded(import_name: str, pip_name: str,
                  min_v: tuple, max_v, tested_ver: str) -> bool:
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", "unknown")
        if version == "unknown":
            print(f"  [OK]  {pip_name} ({import_name}) == unknown  [tested: {tested_ver}]")
            return True
        parsed = _parse_ver(version)
        ok = parsed >= min_v and (max_v is None or parsed < max_v)
        if ok:
            print(f"  [OK]  {pip_name} ({import_name}) == {version}  [tested: {tested_ver}]")
        else:
            min_str = ".".join(str(x) for x in min_v)
            max_str = ".".join(str(x) for x in max_v) if max_v else "∞"
            print(f"  [FAIL] {pip_name} ({import_name}) == {version}")
            print(f"         Supported range: >={min_str}, <{max_str}")
            print(f"         Fix: pip install -r requirements.txt")
        return ok
    except ImportError as e:
        print(f"  [FAIL] {pip_name} ({import_name}) — NOT FOUND: {e}")
        print(f"         Fix: pip install -r requirements.txt")
        return False


def check_package(import_name: str, pip_name: str, version_attr: str,
                  required: bool = True) -> bool:
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, version_attr, "unknown")
        print(f"  [OK]  {pip_name} ({import_name}) == {version}")
        return True
    except ImportError as e:
        status = "FAIL" if required else "SKIP"
        print(f"  [{status}] {pip_name} ({import_name}) — NOT FOUND: {e}")
        if required:
            print(f"         Fix: pip install {pip_name} (or pip install -r requirements.txt)")
        return not required


def main():
    print("=" * 60)
    print("SentinelAI Environment Verification")
    print(f"Python:   {platform.python_version()} ({sys.executable})")
    print(f"Platform: {platform.platform()}")
    print("=" * 60)

    all_pass = True

    # -----------------------------------------------------------------------
    print("\n[ARTIFACT-CRITICAL PACKAGES]  (exact version required)")
    print("  Wrong version = FAIL — ML artifacts were serialized with these exact versions.")
    # -----------------------------------------------------------------------
    for import_name, pip_name, req_ver in ARTIFACT_CRITICAL:
        ok = check_artifact_critical(import_name, pip_name, req_ver)
        if not ok:
            all_pass = False

    # -----------------------------------------------------------------------
    print("\n[BOUNDED-COMPATIBLE PACKAGES]  (range-checked)")
    print("  Outside supported range = FAIL.")
    # -----------------------------------------------------------------------
    for import_name, pip_name, min_v, max_v, tested in BOUNDED_PACKAGES:
        ok = check_bounded(import_name, pip_name, min_v, max_v, tested)
        if not ok:
            all_pass = False

    # -----------------------------------------------------------------------
    print("\n[REQUIRED PACKAGES]  (existence enforced)")
    # -----------------------------------------------------------------------
    for args in REQUIRED_PACKAGES:
        ok = check_package(*args, required=True)
        if not ok:
            all_pass = False

    # -----------------------------------------------------------------------
    print("\n[OPTIONAL PACKAGES]")
    # -----------------------------------------------------------------------
    for args in OPTIONAL_PACKAGES:
        check_package(*args, required=False)

    # -----------------------------------------------------------------------
    print("\n[CRITICAL APPLICATION IMPORTS]")
    # -----------------------------------------------------------------------
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
