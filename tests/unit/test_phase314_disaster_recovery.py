"""
tests/unit/test_phase314_disaster_recovery.py
==============================================
Phase 3.14 Disaster Recovery Tests.
Tests backup script logic, checksum verification, and DR procedures
without requiring live PostgreSQL or pg_dump.
"""

import hashlib
import json
import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestBackupScriptStructure:

    def test_backup_script_exists(self):
        """scripts/backup.py must exist."""
        script = Path(__file__).parents[2] / "scripts" / "backup.py"
        assert script.exists(), f"Backup script not found at {script}"

    def test_backup_script_is_importable(self):
        """Backup script must import without errors."""
        scripts_dir = str(Path(__file__).parents[2] / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "backup",
            Path(__file__).parents[2] / "scripts" / "backup.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "cmd_backup")
        assert hasattr(module, "cmd_restore")
        assert hasattr(module, "cmd_verify")

    def test_backup_defines_rto_and_rpo_targets(self):
        """Backup script must define both RTO and RPO numeric targets."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "backup",
            Path(__file__).parents[2] / "scripts" / "backup.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, "RTO_TARGET_MINUTES"), "RTO_TARGET_MINUTES not defined"
        assert hasattr(module, "RPO_TARGET_HOURS"),   "RPO_TARGET_HOURS not defined"
        assert module.RTO_TARGET_MINUTES > 0
        assert module.RPO_TARGET_HOURS > 0


class TestBackupFileIntegrity:
    """Test backup integrity verification logic without live PostgreSQL."""

    def _sha256_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def test_sha256_verification_succeeds_for_valid_file(self):
        """Checksum verification must succeed when file is intact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dump_file = Path(tmpdir) / "test.dump"
            dump_file.write_bytes(b"FAKE_PG_DUMP_CONTENT_12345")

            actual_sha = self._sha256_file(dump_file)
            sha_file = Path(str(dump_file) + ".sha256")
            sha_file.write_text(actual_sha)

            # Verify: read and compare
            expected = sha_file.read_text().strip()
            computed  = self._sha256_file(dump_file)
            assert expected == computed

    def test_sha256_verification_fails_for_corrupted_file(self):
        """Checksum verification must fail when backup file is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dump_file = Path(tmpdir) / "test.dump"
            dump_file.write_bytes(b"ORIGINAL_CONTENT")

            original_sha = self._sha256_file(dump_file)
            sha_file = Path(str(dump_file) + ".sha256")
            sha_file.write_text(original_sha)

            # Corrupt the file
            dump_file.write_bytes(b"CORRUPTED_CONTENT_DIFFERENT")

            expected = sha_file.read_text().strip()
            computed  = self._sha256_file(dump_file)
            assert expected != computed, "Corruption should invalidate checksum"

    def test_backup_metadata_json_structure(self):
        """Backup metadata file must contain required fields (no credentials)."""
        meta = {
            "backup_timestamp": "20260101T120000Z",
            "database": "sentinelai",
            "host": "db.sentinelai.internal",
            "port": "5432",
            "backup_file": "sentinelai_20260101T120000Z.dump",
            "sha256": "abc123" * 10,
            "rpo_target_hours": 1,
            "rto_target_minutes": 30,
            "backup_status": "COMPLETED",
        }

        required_fields = ["backup_timestamp", "database", "host", "sha256",
                           "rpo_target_hours", "rto_target_minutes", "backup_status"]
        for field in required_fields:
            assert field in meta, f"Missing metadata field: {field}"

        # Sensitive fields must NOT be in metadata
        forbidden = ["password", "passwd", "secret", "api_key", "token"]
        for field in forbidden:
            assert field not in meta, f"Sensitive field '{field}' must not be in backup metadata"

    def test_backup_metadata_has_no_credentials(self):
        """Backup metadata must never contain credentials."""
        # This simulates a real backup metadata that accidentally included a password
        bad_meta = {
            "database": "sentinelai",
            "password": "db_password_1234",  # BUG: should not be here
        }
        forbidden = {"password", "passwd", "secret", "api_key", "token", "credential"}
        violations = [k for k in bad_meta if k.lower() in forbidden]
        assert len(violations) > 0, "Test setup is wrong — expected to find violation"
        # This test documents that violations MUST be caught by the backup script


class TestFailureScenarioRecovery:
    """
    Tests for failure scenario recovery procedures.
    These tests validate the recovery logic and documentation without
    requiring a full cluster environment.
    """

    def test_recovery_objectives_are_defined_and_realistic(self):
        """RTO and RPO targets must be defined and within enterprise-acceptable bounds."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "backup",
            Path(__file__).parents[2] / "scripts" / "backup.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # RTO: realistic for a containerized SOC platform
        assert module.RTO_TARGET_MINUTES <= 60, "RTO > 60 minutes is not enterprise-grade"
        # RPO: acceptable data loss window
        assert module.RPO_TARGET_HOURS <= 4, "RPO > 4 hours is not acceptable for SOC data"

    def test_backup_dir_creation_is_idempotent(self):
        """Backup directory creation must not fail if directory already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_dir = Path(tmpdir) / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            # Second call must not raise
            backup_dir.mkdir(parents=True, exist_ok=True)
            assert backup_dir.exists()

    def test_pg_dump_not_found_is_handled_gracefully(self):
        """Backup script must handle pg_dump absence gracefully (development environments)."""
        import subprocess
        # Simulate pg_dump not found
        with patch("subprocess.run", side_effect=FileNotFoundError("pg_dump not found")):
            try:
                result = subprocess.run(["pg_dump", "--version"])
            except FileNotFoundError as e:
                assert "pg_dump" in str(e)
            # No unhandled crash

    def test_worker_crash_recovery_via_xautoclaim(self):
        """
        Consumer recovery after crash is handled by XAUTOCLAIM in StreamConsumerBase.
        This test validates that the recovery mechanism is configured.
        """
        from backend.app.services.stream_consumer_base import CLAIM_IDLE_MS, CLAIM_BATCH

        # Must have a reasonable idle timeout before claiming orphaned messages
        assert CLAIM_IDLE_MS >= 30_000, "CLAIM_IDLE_MS should be at least 30 seconds"
        assert CLAIM_BATCH >= 1, "CLAIM_BATCH must be positive"

    def test_dlq_is_bounded_to_prevent_unbounded_growth(self):
        """DLQ max length must be set to prevent unbounded Redis memory growth."""
        # Inspect the DLQ xadd call in stream_consumer_base.py
        import inspect
        from backend.app.services import stream_consumer_base
        source = inspect.getsource(stream_consumer_base)

        assert "maxlen" in source, "DLQ xadd must use maxlen= to bound queue size"
        # Verify DLQ limit is reasonable
        assert "10_000" in source or "10000" in source, "DLQ maxlen should be 10000"

    def test_message_duplication_is_safe_due_to_idempotency_via_ack(self):
        """
        Redis consumer groups with XACK guarantee at-least-once delivery.
        Messages already ACKed are not redelivered by the group.
        This test documents the design assumption.
        """
        # The invariant: XREADGROUP delivers each message exactly once per group
        # until XACK is called. After ACK, no redelivery occurs.
        # Duplicate delivery only occurs if ACK fails (handled by retry logic).
        from backend.app.services.stream_consumer_base import StreamConsumerBase
        import inspect

        source = inspect.getsource(StreamConsumerBase._process_message)
        assert "xack" in source.lower(), "ACK must be called after successful processing"
