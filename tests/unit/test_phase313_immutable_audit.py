"""
tests/unit/test_phase313_immutable_audit.py
============================================
Phase 3.13 Enterprise Governance Tests: Immutable Audit Trail.
Tests HMAC chaining, sanitization, event type coverage, and tamper detection.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestAuditEventTypes:

    def test_all_critical_event_types_exist(self):
        """Verify all required audit event types are defined."""
        from backend.app.services.immutable_audit_service import AuditEventType

        required_events = [
            "auth.login",
            "auth.logout",
            "auth.login_failed",
            "incident.created",
            "incident.updated",
            "incident.resolved",
            "investigation.created",
            "response.approved",
            "response.executed",
            "response.rollback",
            "governance.policy_changed",
            "governance.model_promoted",
            "governance.model_demoted",
            "data.exported",
        ]

        all_values = {e.value for e in AuditEventType}
        for event in required_events:
            assert event in all_values, f"Missing audit event type: '{event}'"

    def test_event_types_are_string_enum(self):
        """AuditEventType must be a str Enum (values usable as strings)."""
        from backend.app.services.immutable_audit_service import AuditEventType

        for event in AuditEventType:
            assert isinstance(event.value, str)
            assert "." in event.value, f"Event '{event.value}' lacks namespace prefix"


class TestAuditSanitization:

    def test_sanitize_drops_password_field(self):
        """Sensitive 'password' field must be completely dropped from audit details."""
        from backend.app.services.immutable_audit_service import _sanitize_audit_details
        result = _sanitize_audit_details({"user": "alice", "password": "secret"})
        assert "password" not in result
        assert result["user"] == "alice"

    def test_sanitize_drops_all_forbidden_fields(self):
        """All forbidden field names must be stripped."""
        from backend.app.services.immutable_audit_service import _sanitize_audit_details, _FORBIDDEN_AUDIT_FIELDS
        data = {field: "value" for field in _FORBIDDEN_AUDIT_FIELDS}
        data["safe_field"] = "keep_me"
        result = _sanitize_audit_details(data)
        for field in _FORBIDDEN_AUDIT_FIELDS:
            assert field not in result, f"Forbidden field '{field}' was not removed"
        assert result["safe_field"] == "keep_me"

    def test_sanitize_recurses_into_nested_dicts(self):
        """Sanitization must be recursive for nested credential objects."""
        from backend.app.services.immutable_audit_service import _sanitize_audit_details
        data = {
            "context": {
                "user": "bob",
                "secret": "my_secret",
                "metadata": {"api_key": "key123", "note": "important"}
            }
        }
        result = _sanitize_audit_details(data)
        assert "secret" not in result["context"]
        assert "api_key" not in result["context"]["metadata"]
        assert result["context"]["user"] == "bob"
        assert result["context"]["metadata"]["note"] == "important"

    def test_sanitize_returns_empty_for_non_dict(self):
        """Non-dict input must return empty dict safely."""
        from backend.app.services.immutable_audit_service import _sanitize_audit_details
        assert _sanitize_audit_details(None) == {}
        assert _sanitize_audit_details("string") == {}
        assert _sanitize_audit_details(123) == {}


class TestAuditHMACChaining:

    def test_compute_record_hmac_is_deterministic(self):
        """Same inputs must always produce the same HMAC."""
        from backend.app.services.immutable_audit_service import _compute_record_hmac
        h1 = _compute_record_hmac("id-1", "auth.login", "user-1", "2025-01-01T00:00:00+00:00", "{}", "GENESIS")
        h2 = _compute_record_hmac("id-1", "auth.login", "user-1", "2025-01-01T00:00:00+00:00", "{}", "GENESIS")
        assert h1 == h2

    def test_compute_record_hmac_changes_with_different_inputs(self):
        """Different inputs must produce different HMACs."""
        from backend.app.services.immutable_audit_service import _compute_record_hmac
        h1 = _compute_record_hmac("id-1", "auth.login",  "user-1", "2025-01-01T00:00:00+00:00", "{}", "GENESIS")
        h2 = _compute_record_hmac("id-1", "auth.logout", "user-1", "2025-01-01T00:00:00+00:00", "{}", "GENESIS")
        assert h1 != h2

    def test_compute_record_hmac_changes_with_different_prev_hash(self):
        """Chaining: changing prev_hash must change the output HMAC."""
        from backend.app.services.immutable_audit_service import _compute_record_hmac
        base_args = ("id-1", "auth.login", "user-1", "2025-01-01T00:00:00+00:00", "{}")
        h_genesis = _compute_record_hmac(*base_args, "GENESIS")
        h_chained = _compute_record_hmac(*base_args, "abc123previoushash")
        assert h_genesis != h_chained

    def test_compute_record_hmac_is_hexadecimal_string(self):
        """HMAC output must be a lowercase hex string (SHA-256 = 64 hex chars)."""
        from backend.app.services.immutable_audit_service import _compute_record_hmac
        h = _compute_record_hmac("id-1", "auth.login", "user-1", "2025-01-01T00:00:00+00:00", "{}", "GENESIS")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_tampered_record_produces_different_hash(self):
        """Modifying any field in a record must invalidate the HMAC."""
        from backend.app.services.immutable_audit_service import _compute_record_hmac

        original_hash = _compute_record_hmac(
            "id-1", "auth.login", "user-1", "2025-01-01T00:00:00+00:00",
            '{"action": "login"}', "GENESIS"
        )

        # Simulate tampering: actor changed
        tampered_hash = _compute_record_hmac(
            "id-1", "auth.login", "ATTACKER", "2025-01-01T00:00:00+00:00",
            '{"action": "login"}', "GENESIS"
        )

        assert original_hash != tampered_hash


class TestImmutableAuditServiceRecord:

    def _mock_db(self):
        """Creates a mock SQLAlchemy async session for unit testing."""
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()

        # Mock _get_latest_hash to return GENESIS
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute = AsyncMock(return_value=mock_result)
        return db

    @pytest.mark.asyncio
    async def test_record_returns_audit_log_instance(self):
        """record() must return an AuditLog ORM object."""
        from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType
        from backend.app.models.audit_log import AuditLog

        db = self._mock_db()
        result = await ImmutableAuditService.record(
            db=db,
            event_type=AuditEventType.LOGIN,
            actor_id="user-1",
            resource="auth",
            action="User login from 10.0.0.1",
            details={"source": "web_ui"},
        )

        assert isinstance(result, AuditLog)
        db.add.assert_called_once()
        db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_strips_password_from_details(self):
        """record() must sanitize sensitive fields before persisting."""
        from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType

        db = self._mock_db()
        result = await ImmutableAuditService.record(
            db=db,
            event_type=AuditEventType.LOGIN,
            actor_id="user-1",
            resource="auth",
            action="Login attempt",
            details={"password": "should_not_be_stored", "username": "alice"}
        )

        stored_details = result.details
        assert "password" not in stored_details
        assert stored_details.get("username") == "alice"

    @pytest.mark.asyncio
    async def test_record_includes_chain_hash_in_details(self):
        """record() must embed _chain_hash and _prev_hash in the details JSON."""
        from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType

        db = self._mock_db()
        result = await ImmutableAuditService.record(
            db=db,
            event_type=AuditEventType.INCIDENT_CREATED,
            actor_id="user-2",
            resource="incident:INC-001",
            action="Created high severity incident",
        )

        assert "_chain_hash" in result.details
        assert "_prev_hash"  in result.details
        assert len(result.details["_chain_hash"]) == 64  # SHA-256 hex

    @pytest.mark.asyncio
    async def test_record_uses_genesis_prev_hash_for_first_record(self):
        """First audit record must use 'GENESIS' as the previous hash."""
        from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType

        db = self._mock_db()
        result = await ImmutableAuditService.record(
            db=db,
            event_type=AuditEventType.LOGIN,
            actor_id="user-1",
            resource="auth",
            action="First ever login"
        )
        assert result.details["_prev_hash"] == "GENESIS"

    @pytest.mark.asyncio
    async def test_record_stores_event_type_in_action_field(self):
        """The action field must include the typed event_type for searchability."""
        from backend.app.services.immutable_audit_service import ImmutableAuditService, AuditEventType

        db = self._mock_db()
        result = await ImmutableAuditService.record(
            db=db,
            event_type=AuditEventType.RESPONSE_EXECUTED,
            actor_id="system",
            resource="response:ACT-001",
            action="Block IP 10.0.0.1"
        )
        assert "response.executed" in result.action
