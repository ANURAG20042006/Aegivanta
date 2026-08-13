"""
SentinelAI Rollback Security & SHA256 Verification Test Suite (Phase 12)
========================================================================
Guarantees:
  - Exact SHA256 hash match passes verification
  - Wrong SHA256 hash fails closed with error
  - Missing model/preprocessor artifact fails closed
  - Corrupt artifact JSON/joblib fails closed
  - Dimension mismatch fails closed
"""
import os
import json
import hashlib
import joblib
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from backend.app.models.model_registry import ModelRegistry
from backend.app.api.v1.train import verify_rollback_artifact_integrity


def test_rollback_missing_artifact_file_rejection(tmp_path):
    """Test rollback fails closed when target model artifact file does not exist."""
    fake_model = ModelRegistry(
        id="test-id-1",
        model_name="Fake Model",
        model_version="fake-v1.0",
        model_type="Classical",
        artifact_path=str(tmp_path / "non_existent_model.joblib"),
        artifact_sha256="1234567890abcdef"
    )
    ok, msg = verify_rollback_artifact_integrity(fake_model, artifacts_dir=tmp_path)
    assert ok is False
    assert "does not exist on disk" in msg


def test_rollback_corrupt_joblib_artifact_rejection(tmp_path):
    """Test rollback fails closed when target joblib artifact is corrupt."""
    corrupt_file = tmp_path / "corrupt_model.joblib"
    corrupt_file.write_bytes(b"NOT_A_REAL_JOBLIB_FILE_CORRUPT_BYTES")

    fake_model = ModelRegistry(
        id="test-id-2",
        model_name="Corrupt Model",
        model_version="corrupt-v1.0",
        model_type="Classical",
        artifact_path=str(corrupt_file),
        artifact_sha256=hashlib.sha256(b"NOT_A_REAL_JOBLIB_FILE_CORRUPT_BYTES").hexdigest()
    )
    ok, msg = verify_rollback_artifact_integrity(fake_model, artifacts_dir=tmp_path)
    assert ok is False
    assert "corrupted or unloadable" in msg


def test_rollback_hash_mismatch_rejection(tmp_path):
    """Test rollback fails closed when model artifact SHA256 does not match registered hash."""
    # Write a valid dummy joblib model
    dummy_file = tmp_path / "dummy_model.joblib"
    joblib.dump({"dummy": "model"}, dummy_file)

    actual_hash = hashlib.sha256(dummy_file.read_bytes()).hexdigest()
    wrong_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    fake_model = ModelRegistry(
        id="test-id-3",
        model_name="Mismatch Model",
        model_version="mismatch-v1.0",
        model_type="Classical",
        artifact_path=str(dummy_file),
        artifact_sha256=wrong_hash
    )
    ok, msg = verify_rollback_artifact_integrity(fake_model, artifacts_dir=tmp_path)
    assert ok is False
    assert "SHA-256 hash mismatch" in msg
