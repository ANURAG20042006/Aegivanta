"""
backend/app/observability/metrics.py
=====================================
Phase 3.12 Observability: Prometheus metrics registry for SentinelAI.
Exposes counters, histograms, and gauges for every critical operation.

ALL metric names follow the prometheus naming convention:
  sentinelai_<component>_<measurement>_<unit>

Never log secrets, JWTs, API keys, or passwords.
"""

import time
import logging
from functools import wraps
from typing import Callable, Optional

logger = logging.getLogger("SentinelAI")

# ---------------------------------------------------------------------------
# Optional prometheus_client import — degrades gracefully if not installed
# ---------------------------------------------------------------------------
try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Summary,
        Info,
        CollectorRegistry,
        REGISTRY,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not installed; metrics will be no-ops")

# ---------------------------------------------------------------------------
# Buckets
# ---------------------------------------------------------------------------
_LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
_ML_LATENCY_BUCKETS = (0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
_DB_LATENCY_BUCKETS = (0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 5.0)


def _make(metric_type, name, description, labelnames=None, buckets=None):
    """Create a prometheus metric, returning a null stub if unavailable."""
    if not PROMETHEUS_AVAILABLE:
        return _NullMetric()
    labelnames = labelnames or []
    try:
        if metric_type == "counter":
            return Counter(name, description, labelnames)
        if metric_type == "histogram":
            kw = {"buckets": buckets} if buckets else {}
            return Histogram(name, description, labelnames, **kw)
        if metric_type == "gauge":
            return Gauge(name, description, labelnames)
        if metric_type == "info":
            return Info(name, description)
    except Exception as e:
        # Already registered (e.g., in test environments that reload modules)
        logger.debug("Metric '%s' already registered: %s", name, e)
        return _NullMetric()
    return _NullMetric()


class _NullMetric:
    """No-op metric stub used when prometheus_client is not available."""
    def labels(self, **kwargs): return self
    def inc(self, amount=1): pass
    def dec(self, amount=1): pass
    def set(self, value): pass
    def observe(self, value): pass
    def info(self, value): pass
    def time(self): return _NullContextManager()


class _NullContextManager:
    def __enter__(self): return self
    def __exit__(self, *args): pass


# ===========================================================================
# API Metrics
# ===========================================================================
api_requests_total = _make(
    "counter",
    "sentinelai_api_requests_total",
    "Total HTTP requests by method, endpoint, and status code",
    ["method", "endpoint", "status_code"]
)

api_request_duration_seconds = _make(
    "histogram",
    "sentinelai_api_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    _LATENCY_BUCKETS
)

api_errors_total = _make(
    "counter",
    "sentinelai_api_errors_total",
    "Total API errors by endpoint and error type",
    ["endpoint", "error_type"]
)

# ===========================================================================
# Detection Metrics
# ===========================================================================
detections_total = _make(
    "counter",
    "sentinelai_detections_total",
    "Total detection events processed, labelled by outcome and attack_type",
    ["outcome", "attack_type", "source"]
)

detection_duration_seconds = _make(
    "histogram",
    "sentinelai_detection_duration_seconds",
    "Detection pipeline latency (rule eval + ML ensemble + scoring)",
    ["pipeline_stage"],
    _LATENCY_BUCKETS
)

detection_risk_score = _make(
    "histogram",
    "sentinelai_detection_risk_score",
    "Distribution of composite risk scores for detected events",
    [],
    [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

rule_matches_total = _make(
    "counter",
    "sentinelai_rule_matches_total",
    "Total deterministic rule matches by rule_id and severity",
    ["rule_id", "severity"]
)

# ===========================================================================
# ML Inference Metrics
# ===========================================================================
ml_inference_total = _make(
    "counter",
    "sentinelai_ml_inference_total",
    "Total ML model inference calls by model_name and outcome",
    ["model_name", "outcome"]
)

ml_inference_duration_seconds = _make(
    "histogram",
    "sentinelai_ml_inference_duration_seconds",
    "ML model inference latency",
    ["model_name"],
    _ML_LATENCY_BUCKETS
)

ml_model_agreement_pct = _make(
    "histogram",
    "sentinelai_ml_model_agreement_pct",
    "Distribution of model agreement percentage across ensemble",
    [],
    [0, 25, 50, 60, 70, 80, 90, 100]
)

model_drift_detected_total = _make(
    "counter",
    "sentinelai_model_drift_detected_total",
    "Total drift detection events by model and drift type",
    ["model_name", "drift_type"]
)

# ===========================================================================
# Incident Metrics
# ===========================================================================
incidents_created_total = _make(
    "counter",
    "sentinelai_incidents_created_total",
    "Total incidents created by severity",
    ["severity"]
)

incidents_resolved_total = _make(
    "counter",
    "sentinelai_incidents_resolved_total",
    "Total incidents resolved, by resolution type",
    ["resolution_type"]
)

incidents_open_gauge = _make(
    "gauge",
    "sentinelai_incidents_open",
    "Currently open incident count by severity",
    ["severity"]
)

incident_mttr_seconds = _make(
    "histogram",
    "sentinelai_incident_mttr_seconds",
    "Mean time to resolve incidents in seconds",
    ["severity"],
    [60, 300, 600, 1800, 3600, 7200, 86400]
)

# ===========================================================================
# IOC / Threat Intel Metrics
# ===========================================================================
ioc_matches_total = _make(
    "counter",
    "sentinelai_ioc_matches_total",
    "Total IOC cache matches by indicator type",
    ["indicator_type"]
)

ioc_cache_size = _make(
    "gauge",
    "sentinelai_ioc_cache_size",
    "Current number of entries in the fast IOC cache"
)

threat_feed_sync_total = _make(
    "counter",
    "sentinelai_threat_feed_sync_total",
    "Total threat feed sync operations by feed and status",
    ["feed_name", "status"]
)

# ===========================================================================
# Response / SOAR Metrics
# ===========================================================================
response_actions_total = _make(
    "counter",
    "sentinelai_response_actions_total",
    "Total automated response actions executed by action_type and outcome",
    ["action_type", "outcome"]
)

response_rollbacks_total = _make(
    "counter",
    "sentinelai_response_rollbacks_total",
    "Total rollback operations triggered",
    ["reason"]
)

response_approvals_pending = _make(
    "gauge",
    "sentinelai_response_approvals_pending",
    "Number of response actions awaiting human approval"
)

# ===========================================================================
# Redis / Queue Metrics
# ===========================================================================
redis_queue_depth = _make(
    "gauge",
    "sentinelai_redis_queue_depth",
    "Current Redis stream length (approximate) by stream_key",
    ["stream_key"]
)

redis_consumer_lag = _make(
    "gauge",
    "sentinelai_redis_consumer_lag",
    "Pending Entries List (PEL) size per consumer group",
    ["stream_key", "consumer_group"]
)

redis_dlq_size = _make(
    "gauge",
    "sentinelai_redis_dlq_size",
    "Current dead-letter queue depth by worker role",
    ["worker_role"]
)

worker_processing_duration_seconds = _make(
    "histogram",
    "sentinelai_worker_processing_duration_seconds",
    "Worker event processing latency by worker role",
    ["worker_role"],
    _LATENCY_BUCKETS
)

# ===========================================================================
# Database Metrics
# ===========================================================================
db_query_duration_seconds = _make(
    "histogram",
    "sentinelai_db_query_duration_seconds",
    "Database query latency by operation and table",
    ["operation", "table"],
    _DB_LATENCY_BUCKETS
)

db_connections_active = _make(
    "gauge",
    "sentinelai_db_connections_active",
    "Active database connections in the pool"
)

db_errors_total = _make(
    "counter",
    "sentinelai_db_errors_total",
    "Total database errors by operation",
    ["operation"]
)

# ===========================================================================
# Audit Metrics
# ===========================================================================
audit_events_total = _make(
    "counter",
    "sentinelai_audit_events_total",
    "Total audit events recorded by event_type",
    ["event_type"]
)

# ===========================================================================
# Phase 16: Detection Quality, Alert Intelligence & Copilot Metrics
# ===========================================================================
aegivanta_alerts_correlated_total = _make(
    "counter",
    "aegivanta_alerts_correlated_total",
    "Total security alerts correlated into incident groups",
    ["attack_type"]
)

aegivanta_alerts_deduplicated_total = _make(
    "counter",
    "aegivanta_alerts_deduplicated_total",
    "Total redundant alerts suppressed via intelligent fingerprinting",
    ["attack_type"]
)

aegivanta_incident_mttd_seconds = _make(
    "gauge",
    "aegivanta_incident_mttd_seconds",
    "Mean Time to Detect security incidents in seconds",
    []
)

aegivanta_incident_mtta_seconds = _make(
    "gauge",
    "aegivanta_incident_mtta_seconds",
    "Mean Time to Acknowledge security incidents in seconds",
    []
)

aegivanta_incident_mttr_seconds = _make(
    "gauge",
    "aegivanta_incident_mttr_seconds",
    "Mean Time to Respond and contain security incidents in seconds",
    []
)

aegivanta_detection_precision = _make(
    "gauge",
    "aegivanta_detection_precision",
    "Current detection precision ratio (0.0 to 1.0)",
    []
)

aegivanta_detection_recall = _make(
    "gauge",
    "aegivanta_detection_recall",
    "Current detection recall ratio (0.0 to 1.0)",
    []
)

aegivanta_detection_f1 = _make(
    "gauge",
    "aegivanta_detection_f1",
    "Current detection F1 score (0.0 to 1.0)",
    []
)

aegivanta_ai_requests_total = _make(
    "counter",
    "aegivanta_ai_requests_total",
    "Total AI Security Copilot inquiries processed",
    ["status"]
)

aegivanta_ai_latency_seconds = _make(
    "histogram",
    "aegivanta_ai_latency_seconds",
    "AI Security Copilot response generation latency",
    [],
    _LATENCY_BUCKETS
)

aegivanta_search_latency_seconds = _make(
    "histogram",
    "aegivanta_search_latency_seconds",
    "Threat investigation search query latency",
    [],
    _LATENCY_BUCKETS
)

aegivanta_telemetry_bytes_total = _make(
    "counter",
    "aegivanta_telemetry_bytes_total",
    "Total volume of telemetry bytes ingested",
    ["schema_type"]
)

# ===========================================================================
# Phase 17: Autonomous Response & Continuous Security Validation Metrics
# ===========================================================================
aegivanta_autonomous_actions_total = _make(
    "counter",
    "aegivanta_autonomous_actions_total",
    "Total autonomous remediation actions executed",
    ["action_type"]
)

aegivanta_autonomous_actions_denied_total = _make(
    "counter",
    "aegivanta_autonomous_actions_denied_total",
    "Total autonomous response actions rejected by policy",
    ["action_type"]
)

aegivanta_autonomous_actions_approved_total = _make(
    "counter",
    "aegivanta_autonomous_actions_approved_total",
    "Total autonomous actions approved by security administrators",
    ["action_type"]
)

aegivanta_autonomous_action_latency_seconds = _make(
    "histogram",
    "aegivanta_autonomous_action_latency_seconds",
    "Latency of autonomous response evaluation and dispatch",
    [],
    _LATENCY_BUCKETS
)

aegivanta_security_validation_total = _make(
    "counter",
    "aegivanta_security_validation_total",
    "Total continuous security defense verification runs",
    ["status"]
)

aegivanta_security_validation_failures_total = _make(
    "counter",
    "aegivanta_security_validation_failures_total",
    "Total security control check failures",
    ["category"]
)

aegivanta_detection_coverage_gaps = _make(
    "gauge",
    "aegivanta_detection_coverage_gaps",
    "Total active ATT&CK detection coverage gaps",
    []
)

aegivanta_asset_risk_score = _make(
    "histogram",
    "aegivanta_asset_risk_score",
    "Distribution of protected asset risk scores (0-100)",
    [],
    [0, 20, 40, 60, 80, 100]
)

aegivanta_response_rollbacks_total = _make(
    "counter",
    "aegivanta_response_rollbacks_total",
    "Total executed response action rollbacks",
    ["action_type"]
)

# ===========================================================================
# Phase 18: Advanced Threat Intelligence & Threat Hunting Metrics
# ===========================================================================
aegivanta_threat_indicators_total = _make(
    "gauge",
    "aegivanta_threat_indicators_total",
    "Total active indicators of compromise (IOCs) across intelligence platform",
    ["ioc_type"]
)

aegivanta_threat_feed_sync_duration_seconds = _make(
    "histogram",
    "aegivanta_threat_feed_sync_duration_seconds",
    "Duration of threat intelligence feed sync execution",
    [],
    _LATENCY_BUCKETS
)

aegivanta_threat_hunt_queries_total = _make(
    "counter",
    "aegivanta_threat_hunt_queries_total",
    "Total executed analyst threat hunting workbench queries",
    ["target_entity"]
)

aegivanta_threat_correlations_total = _make(
    "counter",
    "aegivanta_threat_correlations_total",
    "Total indicator cross-correlations performed",
    ["risk_tier"]
)

aegivanta_threat_actor_profiles_total = _make(
    "gauge",
    "aegivanta_threat_actor_profiles_total",
    "Total active threat actor profiles in platform",
    []
)

# ===========================================================================
# Phase 19: Autonomous SOC & SOAR 2.0 Metrics
# ===========================================================================
aegivanta_soar_playbooks_total = _make(
    "gauge",
    "aegivanta_soar_playbooks_total",
    "Total declarative SOAR playbooks in platform",
    ["category"]
)

aegivanta_soar_executions_total = _make(
    "counter",
    "aegivanta_soar_executions_total",
    "Total executed SOAR containment sessions",
    ["status"]
)

aegivanta_soar_approvals_pending = _make(
    "gauge",
    "aegivanta_soar_approvals_pending",
    "Total SOAR containment actions pending human approval",
    []
)

aegivanta_soar_action_duration_seconds = _make(
    "histogram",
    "aegivanta_soar_action_duration_seconds",
    "Execution duration of individual SOAR containment actions",
    ["action_type"],
    _LATENCY_BUCKETS
)

aegivanta_soar_kill_switch_active = _make(
    "gauge",
    "aegivanta_soar_kill_switch_active",
    "Current status of SOAR Emergency Containment Kill Switch (1=Active, 0=Inactive)",
    []
)

# ===========================================================================
# Phase 20: Advanced AI/ML Security Intelligence Metrics
# ===========================================================================
aegivanta_ai_models_registered_total = _make(
    "gauge",
    "aegivanta_ai_models_registered_total",
    "Total registered ML models in platform registry",
    ["stage"]
)

aegivanta_ai_inference_drift_psi = _make(
    "gauge",
    "aegivanta_ai_inference_drift_psi",
    "Current Population Stability Index (PSI) drift score for inference",
    ["model_version"]
)

aegivanta_ai_adversarial_attacks_blocked_total = _make(
    "counter",
    "aegivanta_ai_adversarial_attacks_blocked_total",
    "Total adversarial threats mitigated (poisoning, prompt injection, extraction)",
    ["threat_type"]
)

aegivanta_ai_copilot_queries_total = _make(
    "counter",
    "aegivanta_ai_copilot_queries_total",
    "Total AI Copilot 2.0 reasoning queries processed",
    ["status"]
)

aegivanta_ai_model_signature_verifications_total = _make(
    "counter",
    "aegivanta_ai_model_signature_verifications_total",
    "Total cryptographic HMAC-SHA256 signature verifications performed on models",
    ["result"]
)

# ===========================================================================
# Phase 21: Cloud & Container Security Metrics
# ===========================================================================
aegivanta_cloud_assets_total = _make(
    "gauge",
    "aegivanta_cloud_assets_total",
    "Total multi-cloud and container assets inventoried",
    []
)

aegivanta_cspm_findings_total = _make(
    "gauge",
    "aegivanta_cspm_findings_total",
    "Total active Cloud Security Posture Management misconfiguration findings",
    []
)

aegivanta_container_images_scanned_total = _make(
    "counter",
    "aegivanta_container_images_scanned_total",
    "Total container images scanned for CVE vulnerabilities and SBOM",
    []
)

aegivanta_k8s_workload_violations_total = _make(
    "counter",
    "aegivanta_k8s_workload_violations_total",
    "Total Kubernetes workload and manifest security violations detected",
    []
)

aegivanta_cloud_iam_privilege_escalation_paths_total = _make(
    "gauge",
    "aegivanta_cloud_iam_privilege_escalation_paths_total",
    "Total cloud IAM privilege escalation vectors identified",
    []
)

# ===========================================================================
# Phase 22: Endpoint XDR & Zero-Trust Security Metrics
# ===========================================================================
aegivanta_endpoint_telemetry_events_total = _make(
    "counter",
    "aegivanta_endpoint_telemetry_events_total",
    "Total normalized endpoint telemetry events ingested",
    []
)

aegivanta_edr_detections_total = _make(
    "gauge",
    "aegivanta_edr_detections_total",
    "Total active EDR endpoint behavioral detections",
    []
)

aegivanta_xdr_correlated_incidents_total = _make(
    "gauge",
    "aegivanta_xdr_correlated_incidents_total",
    "Total cross-domain correlated XDR incidents",
    []
)

aegivanta_zero_trust_device_trust_score = _make(
    "gauge",
    "aegivanta_zero_trust_device_trust_score",
    "Average Zero Trust device trust score across fleet",
    []
)

aegivanta_endpoint_response_actions_total = _make(
    "counter",
    "aegivanta_endpoint_response_actions_total",
    "Total governed endpoint response & containment actions executed",
    []
)

# ===========================================================================
# Phase 23: Enterprise Integration Ecosystem Metrics
# ===========================================================================
aegivanta_integration_connectors_total = _make(
    "gauge",
    "aegivanta_integration_connectors_total",
    "Total registered integration connectors",
    []
)

aegivanta_webhook_dead_letter_events_total = _make(
    "gauge",
    "aegivanta_webhook_dead_letter_events_total",
    "Total webhook events in dead-letter queue",
    []
)

# ===========================================================================
# Decorators / Helpers
# ===========================================================================









def record_api_request(method: str, endpoint: str, status_code: int, duration_s: float) -> None:
    """Records a single API request outcome into Prometheus."""
    api_requests_total.labels(
        method=method, endpoint=endpoint, status_code=str(status_code)
    ).inc()
    api_request_duration_seconds.labels(
        method=method, endpoint=endpoint
    ).observe(duration_s)
    if status_code >= 500:
        api_errors_total.labels(endpoint=endpoint, error_type="server_error").inc()
    elif status_code >= 400:
        api_errors_total.labels(endpoint=endpoint, error_type="client_error").inc()


def record_detection(outcome: str, attack_type: str, source: str = "pipeline",
                     risk_score: Optional[float] = None, duration_s: Optional[float] = None) -> None:
    """Records a detection event into Prometheus."""
    detections_total.labels(outcome=outcome, attack_type=attack_type, source=source).inc()
    if risk_score is not None:
        detection_risk_score.observe(risk_score)
    if duration_s is not None:
        detection_duration_seconds.labels(pipeline_stage="total").observe(duration_s)


def record_ml_inference(model_name: str, outcome: str, duration_s: float,
                        agreement_pct: Optional[float] = None) -> None:
    """Records an ML inference call into Prometheus."""
    ml_inference_total.labels(model_name=model_name, outcome=outcome).inc()
    ml_inference_duration_seconds.labels(model_name=model_name).observe(duration_s)
    if agreement_pct is not None:
        ml_model_agreement_pct.observe(agreement_pct)


def record_incident(action: str, severity: str, mttr_s: Optional[float] = None) -> None:
    """Records an incident lifecycle event."""
    if action == "create":
        incidents_created_total.labels(severity=severity).inc()
    elif action == "resolve":
        incidents_resolved_total.labels(resolution_type=severity).inc()
        if mttr_s is not None:
            incident_mttr_seconds.labels(severity=severity).observe(mttr_s)


def record_response_action(action_type: str, outcome: str) -> None:
    """Records a SOAR response action execution."""
    response_actions_total.labels(action_type=action_type, outcome=outcome).inc()


def get_metrics_response() -> tuple[bytes, str]:
    """Returns (metrics_bytes, content_type) for a Prometheus /metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        return b"# Prometheus client not available\n", "text/plain"
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
