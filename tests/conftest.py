import os
import tempfile
import uuid
from pathlib import Path

import pytest

# Set threading and backend environment variables to prevent OpenMP crashes and GUI initialization on Linux
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

# Ensure test environment variables are set before any backend modules load
os.environ.setdefault("AEGIVANTA_ADMIN_PASSWORD", "TestAdminPassword2026!")
os.environ.setdefault("AEGIVANTA_ANALYST_PASSWORD", "TestAnalystPassword2026!")
os.environ.setdefault("AEGIVANTA_VIEWER_PASSWORD", "TestViewerPassword2026!")
os.environ.setdefault("SENTINEL_ADMIN_PASSWORD", "TestAdminPassword2026!")
os.environ.setdefault("SENTINEL_ANALYST_PASSWORD", "TestAnalystPassword2026!")
os.environ.setdefault("SENTINEL_VIEWER_PASSWORD", "TestViewerPassword2026!")
os.environ.setdefault("SECRET_KEY", "test_secret_key_minimum_32_characters_long_for_security_testing")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("OPERATING_MODE", "DEMO")

# Use a unique SQLite database per test session so local runs do not mutate the repo-root database.
database_path = (Path(tempfile.gettempdir()) / f"sentinelai-test-{uuid.uuid4()}.db").resolve()
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{database_path.as_posix()}")

import asyncio

@pytest.fixture(autouse=True, scope="session")
def setup_test_env():
    """Session fixture ensuring environment variables are set and database tables are initialized."""
    async def _init():
        from backend.app.main import initialize_application
        await initialize_application()

    try:
        asyncio.run(_init())
    except Exception as e:
        print(f"Warning initializing database in tests: {e}")

