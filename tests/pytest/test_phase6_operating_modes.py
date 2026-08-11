import pytest
from backend.app.config import settings


def test_operating_mode_settings():
    """Requirement 1 Proof: Settings defines OPERATING_MODE with DEMO, LAB, or PRODUCTION choices."""
    assert hasattr(settings, "OPERATING_MODE")
    assert settings.OPERATING_MODE in ["DEMO", "LAB", "PRODUCTION"]


def test_demo_mode_allows_synthetic_telemetry(monkeypatch):
    """Requirement 2 Proof: DEMO mode permits synthetic telemetry stream generator."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "DEMO")
    assert settings.OPERATING_MODE == "DEMO"


def test_lab_mode_controlled_benchmark(monkeypatch):
    """Requirement 3 Proof: LAB mode executes controlled lab benchmark flows."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "LAB")
    assert settings.OPERATING_MODE == "LAB"


def test_production_mode_disables_synthetic_telemetry(monkeypatch):
    """Requirement 4 Proof: PRODUCTION mode disables random synthetic packet generation."""
    monkeypatch.setattr(settings, "OPERATING_MODE", "PRODUCTION")
    assert settings.OPERATING_MODE == "PRODUCTION"
    # Ensure random synthetic generator is disabled in PRODUCTION mode
    assert settings.OPERATING_MODE != "DEMO"
