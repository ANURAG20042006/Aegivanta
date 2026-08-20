"""
backend/app/services/worker_registry.py
=========================================
Phase 3.11: Worker Role Registry for Horizontal Scaling.
Defines typed worker roles so each deployment scales independently.
Each worker class only consumes streams relevant to its responsibility domain.
"""

import os
import logging
from enum import Enum
from typing import List

logger = logging.getLogger("SentinelAI")


class WorkerRole(str, Enum):
    """Named worker roles for horizontal scaling.
    Each role is deployed as a separate Kubernetes Deployment with independent HPA.
    """
    TELEMETRY     = "telemetry"     # Ingests raw telemetry events from XREAD consumer group
    DETECTION     = "detection"     # Runs detection pipeline (ML + rules) on raw events
    THREAT_INTEL  = "threat_intel"  # Synchronises threat feeds and IOC lifecycle
    RESPONSE      = "response"      # Executes SOAR response actions, manages approval queue
    HUNTING       = "hunting"       # Processes scheduled threat hunting jobs
    AUDIT         = "audit"         # Writes immutable audit records from the audit stream


# Stream assignments per worker role.
# Workers should only read/write streams they own.
WORKER_STREAM_ASSIGNMENTS: dict[WorkerRole, List[str]] = {
    WorkerRole.TELEMETRY:    ["sentinelai:telemetry"],
    WorkerRole.DETECTION:    ["sentinelai:detection", "sentinelai:dl_queue:detection"],
    WorkerRole.THREAT_INTEL: ["sentinelai:threat_intel", "sentinelai:dl_queue:threat_intel"],
    WorkerRole.RESPONSE:     ["sentinelai:response", "sentinelai:dl_queue:response"],
    WorkerRole.HUNTING:      ["sentinelai:hunting"],
    WorkerRole.AUDIT:        ["sentinelai:audit"],
}

# Consumer group name per stream
CONSUMER_GROUP_PREFIX = "sentinelai-cg"

# Retry policy per worker role
WORKER_RETRY_POLICY: dict[WorkerRole, dict] = {
    WorkerRole.TELEMETRY:    {"max_retries": 3,  "retry_backoff_s": 2,  "dlq_threshold": 3},
    WorkerRole.DETECTION:    {"max_retries": 5,  "retry_backoff_s": 5,  "dlq_threshold": 5},
    WorkerRole.THREAT_INTEL: {"max_retries": 3,  "retry_backoff_s": 10, "dlq_threshold": 3},
    WorkerRole.RESPONSE:     {"max_retries": 5,  "retry_backoff_s": 5,  "dlq_threshold": 3},
    WorkerRole.HUNTING:      {"max_retries": 2,  "retry_backoff_s": 30, "dlq_threshold": 2},
    WorkerRole.AUDIT:        {"max_retries": 10, "retry_backoff_s": 2,  "dlq_threshold": 10},
}

# Backpressure thresholds: if stream PEL > N, pause production
BACKPRESSURE_THRESHOLDS: dict[WorkerRole, int] = {
    WorkerRole.TELEMETRY:    1000,
    WorkerRole.DETECTION:    500,
    WorkerRole.THREAT_INTEL: 200,
    WorkerRole.RESPONSE:     100,
    WorkerRole.HUNTING:      50,
    WorkerRole.AUDIT:        1000,
}


def current_worker_role() -> WorkerRole:
    """Reads SENTINELAI_WORKER_ROLE env var to determine which role this process serves."""
    raw = os.environ.get("SENTINELAI_WORKER_ROLE", "").strip().lower()
    try:
        return WorkerRole(raw)
    except ValueError:
        logger.warning("Unknown SENTINELAI_WORKER_ROLE '%s', defaulting to DETECTION", raw)
        return WorkerRole.DETECTION


def get_consumer_group(role: WorkerRole) -> str:
    """Returns the canonical Redis consumer group name for the given worker role."""
    return f"{CONSUMER_GROUP_PREFIX}-{role.value}"
