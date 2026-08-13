import os
import pytest

# Ensure test environment variables are set before any backend modules load
os.environ.setdefault("SENTINEL_ADMIN_PASSWORD", "TestAdminPassword2026!")
os.environ.setdefault("SENTINEL_ANALYST_PASSWORD", "TestAnalystPassword2026!")
os.environ.setdefault("SENTINEL_VIEWER_PASSWORD", "TestViewerPassword2026!")
os.environ.setdefault("SECRET_KEY", "test_secret_key_minimum_32_characters_long_for_security_testing")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("OPERATING_MODE", "DEMO")

@pytest.fixture(autouse=True, scope="session")
def setup_test_env():
    """Session fixture ensuring environment variables are set."""
    pass
