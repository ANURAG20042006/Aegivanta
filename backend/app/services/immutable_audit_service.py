"""
backend/app/services/immutable_audit_service.py
================================================
Phase 3.13 Enterprise Governance: Tamper-Evident Immutable Audit Trail.

Design Principles:
  - Append-only: no UPDATE or DELETE operations on audit_logs
  - Tamper-evident: each record includes SHA-256 HMAC of its content chained
    with the previous record's hash (similar to a Merkle chain)
  - Actor-attributed: every record names the acting user/system
  - Timestamped: wall-clock UTC ISO 8601
  - Sensitive data never appears in audit records (no passwords, JWTs, secrets)

The chain is validated by recomputing each record's hash and verifying it
matches the stored value. Any modification to a past record breaks the chain.

SECURITY: The HMAC key is read from settings.SECRET_KEY (never logged).
"""

import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.models.audit_log import AuditLog

logger = logging.getLogger("SentinelAI")


# ---------------------------------------------------------------------------
# Audit event types
# ---------------------------------------------------------------------------
class AuditEventType(str, Enum):
    # Authentication
    LOGIN                 = "auth.login"
    LOGOUT                = "auth.logout"
    LOGIN_FAILED          = "auth.login_failed"
    # Incident lifecycle
    INCIDENT_CREATED      = "incident.created"
    INCIDENT_UPDATED      = "incident.updated"
    INCIDENT_RESOLVED     = "incident.resolved"
    # Investigation
    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_UPDATED = "investigation.updated"
    # Response / SOAR
    RESPONSE_APPROVED     = "response.approved"
    RESPONSE_EXECUTED     = "response.executed"
    RESPONSE_REJECTED     = "response.rejected"
    ROLLBACK_TRIGGERED    = "response.rollback"
    # Governance
    POLICY_CHANGED        = "governance.policy_changed"
    MODEL_PROMOTED        = "governance.model_promoted"
    MODEL_DEMOTED         = "governance.model_demoted"
    CONFIG_CHANGED        = "governance.config_changed"
    # Data management
    DATA_EXPORTED         = "data.exported"
    DATA_DELETED          = "data.deleted"
    RETENTION_APPLIED     = "data.retention_applied"
    # User management
    USER_CREATED          = "user.created"
    USER_ROLE_CHANGED     = "user.role_changed"
    USER_DELETED          = "user.deleted"


# ---------------------------------------------------------------------------
# Fields that must never appear in audit records
# ---------------------------------------------------------------------------
_FORBIDDEN_AUDIT_FIELDS = frozenset({
    "password", "passwd", "secret", "api_key", "token", "jwt",
    "authorization", "credential", "private_key", "access_token",
    "refresh_token", "client_secret"
})


def _sanitize_audit_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively strips sensitive fields from audit record details."""
    if not isinstance(details, dict):
        return {}
    sanitized = {}
    for k, v in details.items():
        if str(k).lower().replace("-", "_") in _FORBIDDEN_AUDIT_FIELDS:
            continue  # Drop the field entirely
        if isinstance(v, dict):
            sanitized[k] = _sanitize_audit_details(v)
        else:
            sanitized[k] = v
    return sanitized


# ---------------------------------------------------------------------------
# Tamper-evident chain
# ---------------------------------------------------------------------------
def _compute_record_hmac(record_id: str, event_type: str, actor_id: str,
                          timestamp_iso: str, details_json: str,
                          previous_hash: str) -> str:
    """
    Computes HMAC-SHA256 of all immutable fields plus the previous chain hash.
    Chaining previous_hash ensures that any historical edit breaks all subsequent hashes.
    """
    payload = "|".join([
        record_id,
        event_type,
        actor_id,
        timestamp_iso,
        details_json,
        previous_hash
    ])
    key = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Immutable Audit Service
# ---------------------------------------------------------------------------
class ImmutableAuditService:
    """
    Writes tamper-evident, append-only audit records.
    Uses HMAC-SHA256 chaining to detect any retrospective modification.
    """

    SYSTEM_ACTOR = "system"

    @classmethod
    async def record(
        cls,
        db: AsyncSession,
        event_type: AuditEventType,
        actor_id: str,
        resource: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "127.0.0.1",
        status: str = "SUCCESS",
    ) -> AuditLog:
        """
        Creates an immutable, chained audit record.

        Args:
            db:          Active async database session.
            event_type:  Typed AuditEventType enum value.
            actor_id:    User ID or 'system' for automated actions.
            resource:    What was acted upon (e.g., 'incident:INC-001').
            action:      Human-readable description of the action.
            details:     Optional structured context. Sensitive fields are stripped.
            ip_address:  Source IP (127.0.0.1 for internal/system actions).
            status:      'SUCCESS' or 'FAILURE'.

        Returns:
            AuditLog ORM instance (already flushed, not yet committed).
        """
        record_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        timestamp_iso = timestamp.isoformat()

        # Sanitize details — never write secrets to audit log
        clean_details = _sanitize_audit_details(details or {})
        # Add standard metadata
        clean_details["event_type"] = event_type.value
        clean_details["resource"]   = resource
        clean_details["action"]     = action

        details_json = json.dumps(clean_details, sort_keys=True, default=str)

        # Retrieve hash of most recent audit record for chain integrity
        previous_hash = await cls._get_latest_hash(db)

        # Compute tamper-evident HMAC
        chain_hash = _compute_record_hmac(
            record_id=record_id,
            event_type=event_type.value,
            actor_id=actor_id,
            timestamp_iso=timestamp_iso,
            details_json=details_json,
            previous_hash=previous_hash
        )

        audit_entry = AuditLog(
            id=record_id,
            user_id=actor_id if actor_id != cls.SYSTEM_ACTOR else None,
            action=f"{event_type.value}:{action}",
            resource=resource,
            ip_address=ip_address,
            status=status,
            timestamp=timestamp,
            details={
                **clean_details,
                "_chain_hash": chain_hash,
                "_prev_hash":  previous_hash,
            }
        )

        db.add(audit_entry)
        await db.flush()

        logger.info(
            "Audit record created",
            extra={
                "event_type": event_type.value,
                "actor_id":   actor_id,
                "resource":   resource,
                "status":     status,
                "record_id":  record_id,
            }
        )
        return audit_entry

    @classmethod
    async def _get_latest_hash(cls, db: AsyncSession) -> str:
        """Returns the chain hash of the most recent audit record, or 'GENESIS' if none exist."""
        try:
            result = await db.execute(
                select(AuditLog.details)
                .order_by(AuditLog.timestamp.desc())
                .limit(1)
            )
            row = result.scalar_one_or_none()
            if row and isinstance(row, dict):
                return row.get("_chain_hash", "GENESIS")
        except Exception as e:
            logger.warning("Could not fetch latest audit hash: %s", e)
        return "GENESIS"

    @classmethod
    async def verify_chain_integrity(
        cls,
        db: AsyncSession,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Verifies the audit chain integrity for the most recent `limit` records.
        Returns a summary with any broken links.
        """
        result = await db.execute(
            select(AuditLog)
            .order_by(AuditLog.timestamp.asc())
            .limit(limit)
        )
        records = result.scalars().all()

        verified = 0
        broken_links: List[str] = []
        previous_hash = "GENESIS"

        for record in records:
            details = record.details or {}
            stored_hash = details.get("_chain_hash", "")
            stored_prev  = details.get("_prev_hash",  "GENESIS")

            if stored_prev != previous_hash:
                broken_links.append(f"Record {record.id}: prev_hash mismatch")
                # Still continue — report all broken links
                previous_hash = stored_hash or previous_hash
                continue

            # Reconstruct the HMAC for this record
            actor_id = record.user_id or cls.SYSTEM_ACTOR
            details_for_hash = {k: v for k, v in details.items() if not k.startswith("_")}
            details_json = json.dumps(details_for_hash, sort_keys=True, default=str)

            expected_hash = _compute_record_hmac(
                record_id=record.id,
                event_type=details.get("event_type", record.action),
                actor_id=actor_id,
                timestamp_iso=record.timestamp.isoformat(),
                details_json=details_json,
                previous_hash=stored_prev
            )

            if expected_hash != stored_hash:
                broken_links.append(f"Record {record.id}: hash mismatch (tampered?)")
            else:
                verified += 1

            previous_hash = stored_hash

        return {
            "verified_count": verified,
            "total_records": len(records),
            "chain_intact": len(broken_links) == 0,
            "broken_links": broken_links
        }

    @classmethod
    async def query_audit_log(
        cls,
        db: AsyncSession,
        event_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        resource: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[AuditLog], int]:
        """Query audit records with optional filters. Returns (records, total_count)."""
        filters = []
        if event_type:
            filters.append(AuditLog.action.contains(event_type))
        if actor_id:
            filters.append(AuditLog.user_id == actor_id)
        if resource:
            filters.append(AuditLog.resource.contains(resource))

        where_clause = and_(*filters) if filters else True

        count_result = await db.execute(
            select(func.count(AuditLog.id)).where(where_clause)
        )
        total = count_result.scalar_one()

        records_result = await db.execute(
            select(AuditLog)
            .where(where_clause)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        records = records_result.scalars().all()
        return list(records), total
