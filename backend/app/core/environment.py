"""
backend/app/core/environment.py
===============================
Phase B2 Authoritative Environment Model, Data Provenance,
Fail-Closed Runtime Guards, and Security Audit Logger.
"""

import os
import enum
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("Aegivanta.SecurityEnvironment")


class AegivantaEnvironment(str, enum.Enum):
    """Authoritative environment identifiers for Aegivanta."""
    DEMO = "DEMO"
    LAB = "LAB"
    PRODUCTION = "PRODUCTION"


class SecurityEnvironmentError(RuntimeError):
    """Raised when an environment or provenance constraint is violated in PRODUCTION."""
    pass


class ProductionConfigurationError(SecurityEnvironmentError):
    """Raised when production configuration is incomplete, insecure, or pointing to mock providers."""
    pass


class DataProvenance(BaseModel):
    """Cryptographic and contextual metadata tracking the exact origin of operational data."""
    environment: AegivantaEnvironment
    source_type: str = Field(..., description="E.g. REAL_TELEMETRY, SENSOR_EDR, PCAP_TAP, BENCHMARK_FLOW, DEMO_FIXTURE")
    source_id: str = Field(..., description="Identifier of the emitting sensor, gateway, or benchmark")
    is_synthetic: bool = False
    is_mock: bool = False
    is_simulated: bool = False
    is_seeded: bool = False
    is_demo: bool = False
    is_production: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance_id: Optional[str] = None


def get_authoritative_environment() -> AegivantaEnvironment:
    """
    Resolves the authoritative system environment from environment variables.
    Fails closed if the environment is missing, ambiguous, or invalid in production contexts.
    """
    raw_env = os.environ.get("AEGIVANTA_ENVIRONMENT") or os.environ.get("OPERATING_MODE") or os.environ.get("APP_ENV")
    if not raw_env:
        # If in production deployment context without explicit env, fail closed
        if os.environ.get("ENV") == "production" or os.environ.get("NODE_ENV") == "production":
            raise ProductionConfigurationError("Mandatory AEGIVANTA_ENVIRONMENT is missing in production deployment.")
        return AegivantaEnvironment.DEMO

    env_upper = raw_env.strip().upper()
    if env_upper in ["PROD", "PRODUCTION"]:
        return AegivantaEnvironment.PRODUCTION
    elif env_upper in ["LAB", "RESEARCH", "BENCHMARK"]:
        return AegivantaEnvironment.LAB
    elif env_upper in ["DEMO", "DEV", "DEVELOPMENT", "TEST", "STAGING"]:
        return AegivantaEnvironment.DEMO
    else:
        raise SecurityEnvironmentError(f"Invalid or unrecognized AEGIVANTA_ENVIRONMENT '{raw_env}'. Must be DEMO, LAB, or PRODUCTION.")


# In-memory security violation audit trail
SECURITY_AUDIT_TRAIL: List[Dict[str, Any]] = []


def record_security_violation(
    component: str,
    source: str,
    reason: str,
    environment: AegivantaEnvironment,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Records an immutable, auditable security violation event when a guard blocks non-production data."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": environment.value,
        "component": component,
        "source": source,
        "reason": reason,
        "decision": "BLOCKED",
        "request_id": request_id or hashlib.sha256(f"{component}:{source}:{time_now()}".encode()).hexdigest()[:16]
    }
    SECURITY_AUDIT_TRAIL.append(event)
    logger.warning("SECURITY GUARD VIOLATION: [%s] Component '%s' blocked source '%s': %s", environment.value, component, source, reason)
    return event


def time_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ==============================================================================
# PRODUCTION RUNTIME GUARDS
# ==============================================================================

class TelemetryGuard:
    """Guards telemetry ingestion boundaries against synthetic/demo leakage in PRODUCTION."""

    @staticmethod
    def validate_telemetry_provenance(
        provenance: Optional[DataProvenance],
        target_env: AegivantaEnvironment,
        raw_headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Validates telemetry payload and headers.
        In PRODUCTION: fails closed if data is synthetic, mock, demo, or missing valid production provenance.
        """
        if target_env == AegivantaEnvironment.PRODUCTION:
            if provenance is None:
                record_security_violation(
                    component="TELEMETRY_INGESTION",
                    source="UNKNOWN_UNAUTHENTICATED",
                    reason="Missing mandatory telemetry data provenance metadata in PRODUCTION.",
                    environment=target_env
                )
                raise SecurityEnvironmentError("Production telemetry requires explicit DataProvenance metadata. Unauthenticated telemetry blocked.")

            if provenance.is_synthetic or provenance.is_mock or provenance.is_demo or provenance.is_simulated or provenance.is_seeded:
                record_security_violation(
                    component="TELEMETRY_INGESTION",
                    source=provenance.source_id or provenance.source_type,
                    reason=f"Prohibited non-production telemetry flag (synthetic={provenance.is_synthetic}, mock={provenance.is_mock}, demo={provenance.is_demo}).",
                    environment=target_env
                )
                raise SecurityEnvironmentError("Production telemetry guard rejected synthetic, mock, or demo telemetry payload.")

            if provenance.environment != AegivantaEnvironment.PRODUCTION:
                record_security_violation(
                    component="TELEMETRY_INGESTION",
                    source=provenance.source_id,
                    reason=f"Environment mismatch: telemetry tagged as '{provenance.environment.value}', expected PRODUCTION.",
                    environment=target_env
                )
                raise SecurityEnvironmentError(f"Telemetry from '{provenance.environment.value}' cannot be ingested into PRODUCTION.")

        return True


class BillingGuard:
    """Guards billing subsystems against mock provider usage in PRODUCTION."""

    @staticmethod
    def validate_billing_provider(provider_type: str, target_env: AegivantaEnvironment) -> bool:
        if target_env == AegivantaEnvironment.PRODUCTION:
            if provider_type.upper() in ["MOCK", "DEMO", "MOCKBILLINGPROVIDER", "FAKE"]:
                record_security_violation(
                    component="BILLING_SERVICE",
                    source=provider_type,
                    reason="Mock billing provider prohibited in PRODUCTION environment.",
                    environment=target_env
                )
                raise ProductionConfigurationError("Production billing cannot use MockBillingProvider. Real provider credentials (e.g. Stripe) must be configured.")
        return True


class ThreatIntelGuard:
    """Guards CTI feeds against fabricated/demo threat indicators in PRODUCTION."""

    @staticmethod
    def validate_indicator_provenance(indicator: Dict[str, Any], target_env: AegivantaEnvironment) -> bool:
        if target_env == AegivantaEnvironment.PRODUCTION:
            if indicator.get("is_synthetic") or indicator.get("is_mock") or indicator.get("is_demo") or indicator.get("is_simulated"):
                record_security_violation(
                    component="THREAT_INTELLIGENCE",
                    source=str(indicator.get("source", "UNKNOWN")),
                    reason="Synthetic or demo threat intelligence indicator blocked from production IOC repository.",
                    environment=target_env
                )
                raise SecurityEnvironmentError("Production CTI rejected synthetic or simulated threat indicator.")
            if not indicator.get("source") or not indicator.get("retrieval_timestamp"):
                record_security_violation(
                    component="THREAT_INTELLIGENCE",
                    source="UNVERIFIED",
                    reason="Missing CTI provider source or retrieval timestamp.",
                    environment=target_env
                )
                raise SecurityEnvironmentError("Production CTI requires verified provider source and retrieval timestamp.")
        return True


class MLArtifactGuard:
    """Guards ML inference against experimental, demo, or unhashed model artifacts in PRODUCTION."""

    @staticmethod
    def verify_production_model_artifact(
        model_name: str,
        artifact_path: str,
        expected_hash: str,
        target_env: AegivantaEnvironment
    ) -> bool:
        if target_env == AegivantaEnvironment.PRODUCTION:
            if not os.path.exists(artifact_path):
                record_security_violation(
                    component="ML_INFERENCE_ENGINE",
                    source=model_name,
                    reason=f"Production model artifact '{artifact_path}' does not exist.",
                    environment=target_env
                )
                raise ProductionConfigurationError(f"Production model artifact for '{model_name}' is missing.")

            actual_hash = hashlib.sha256(open(artifact_path, "rb").read()).hexdigest()
            if actual_hash != expected_hash:
                record_security_violation(
                    component="ML_INFERENCE_ENGINE",
                    source=model_name,
                    reason=f"Cryptographic hash mismatch. Expected '{expected_hash}', got '{actual_hash}'.",
                    environment=target_env
                )
                raise SecurityEnvironmentError(f"Production ML artifact '{model_name}' integrity check failed (hash mismatch).")
        return True


class DatabaseGuard:
    """Guards database connections against SQLite dev/demo fallbacks in PRODUCTION."""

    @staticmethod
    def validate_database_url(db_url: str, target_env: AegivantaEnvironment) -> bool:
        if target_env == AegivantaEnvironment.PRODUCTION:
            if "sqlite" in db_url.lower() or ":memory:" in db_url.lower() or "sentinelai.db" in db_url.lower():
                record_security_violation(
                    component="DATABASE_CONNECTION",
                    source=db_url,
                    reason="SQLite / in-memory database configuration prohibited in PRODUCTION.",
                    environment=target_env
                )
                raise ProductionConfigurationError("Production requires PostgreSQL database. SQLite / in-memory fallback is prohibited.")
        return True
