"""
Environment & Dependency Integrity Test Suite
===============================================
Verifies that all required backend, database, security, and ML packages
are installed and importable in the current execution environment with
compatible versions matching serialized ML artifacts.
"""
import sys
import importlib
import pytest


def test_scikit_learn_version_compatibility():
    """Verify scikit-learn version is 1.6.x (matching serialized artifacts)."""
    import sklearn
    version = getattr(sklearn, "__version__", "")
    assert version.startswith("1.6."), (
        f"Incompatible scikit-learn version: {version}. "
        f"Serialized artifacts (best_model.joblib) require scikit-learn 1.6.x."
    )


def test_database_and_security_dependencies_importable():
    """Verify backend database and authentication dependencies can be imported."""
    required_modules = [
        ("aiosqlite", "aiosqlite"),
        ("asyncpg", "asyncpg"),
        ("jose", "python-jose"),
        ("passlib", "passlib"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("pydantic", "pydantic"),
    ]
    for import_name, pkg_name in required_modules:
        try:
            mod = importlib.import_module(import_name)
            assert mod is not None, f"Module {import_name} is None"
        except ImportError as e:
            pytest.fail(f"Required dependency '{pkg_name}' ({import_name}) failed to import: {e}")


def test_ml_core_dependencies_importable():
    """Verify core machine learning dependencies can be imported."""
    required_ml = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scipy", "scipy"),
        ("joblib", "joblib"),
        ("shap", "shap"),
        ("xgboost", "xgboost"),
        ("lightgbm", "lightgbm"),
        ("catboost", "catboost"),
        ("imblearn", "imbalanced-learn"),
    ]
    for import_name, pkg_name in required_ml:
        try:
            mod = importlib.import_module(import_name)
            assert mod is not None, f"Module {import_name} is None"
        except ImportError as e:
            pytest.fail(f"Required ML dependency '{pkg_name}' ({import_name}) failed to import: {e}")


def test_python_runtime_version():
    """Verify runtime Python version is 3.11.x as specified by the project lockfile and .python-version."""
    assert sys.version_info[:2] == (3, 11), (
        f"Incompatible Python version: {sys.version}. SentinelAI requires Python 3.11.x for reproducible ML artifacts and dependencies."
    )


def test_test_database_isolation():
    """Verify test runs use an isolated database and do not target the repo-root sentinelai.db."""
    import os
    db_url = os.environ.get("DATABASE_URL", "")
    assert "sentinelai-test-" in db_url or "temp" in db_url.lower() or "test" in db_url.lower(), (
        f"Database URL '{db_url}' is not properly isolated for testing."
    )
    assert not db_url.endswith("/./sentinelai.db") and not db_url.endswith("/sentinelai.db"), (
        "Test suite must not execute against the production/development repository root database."
    )
