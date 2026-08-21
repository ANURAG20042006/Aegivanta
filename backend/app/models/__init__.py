"""SentinelAI SQLAlchemy ORM Models Package."""
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.models.incident import Incident
from backend.app.models.model_registry import ModelRegistry
from backend.app.models.protected_asset import ProtectedAsset
from backend.app.models.alert import Alert
from backend.app.models.incident_timeline import IncidentTimelineEvent
from backend.app.models.security_event import SecurityEvent
from backend.app.models.monitoring import MonitoringCheck, MonitoringHistory
from backend.app.models.threat_intel import ThreatIndicator, ThreatFeed
from backend.app.models.behavioral import BehavioralBaseline, AnomalyEvent
from backend.app.models.investigation import Investigation, InvestigationEvidence, InvestigationCase, InvestigationNote, InvestigationTimeline
from backend.app.models.playbook import PlaybookExecution
from backend.app.models.hunting import HuntingQuery, HuntingExecution
from backend.app.models.predictive import RiskForecast, AlertVolumeForecast
from backend.app.models.threat_graph import ThreatGraphNode, ThreatGraphEdge
from backend.app.models.response_approval import ResponseApproval
from backend.app.models.attack_coverage import AttackCoverageSnapshot
from backend.app.models.job import BackgroundJob
from backend.app.models.response import ResponsePolicy, ResponseActionRecord, IdempotencyRecord, ResponseAuditLog
from backend.app.models.feedback import DetectionFeedback, VALID_FEEDBACK_VERDICTS

from backend.app.models.tenant import Organization, Tenant, TenantMembership, TenantRole, TenantSettings
from backend.app.models.subscription import Subscription, FeatureEntitlement, PlanTier
from backend.app.models.api_key import ApiKey, ApiKeyScope
from backend.app.models.usage import UsageRecord, UsageQuota
from backend.app.models.integration import CustomerIntegration
from backend.app.models.sensor import Sensor
from backend.app.models.identity import (
    IdentityProvider, UserSession, MFAEnrollment,
    PAMSessionElevation, IdentityThreatDetection, PasskeyCredential, IdentityScorecard
)

from backend.app.models.detection_rule import DetectionRule
from backend.app.models.detection_quality import DetectionQualitySnapshot, DetectionEvaluation, DetectionBenchmark
from backend.app.models.alert_intelligence import AlertFingerprint, AlertGroup, AlertPriorityScore
from backend.app.models.security_insights import SecurityScoreHistory, SecurityImprovementRecommendation
from backend.app.models.autonomous_response import AutonomousResponsePolicy, ResponsePolicyRule, ResponseBlastRadius, ResponseRollback
from backend.app.models.security_validation import SecurityValidationRun, SecurityValidationCheck
from backend.app.models.security_simulation import SecuritySimulation, SecuritySimulationEvent
from backend.app.models.security_intelligence import DetectionCoverageGap, AssetRiskScore, SecurityControlEffectiveness
from backend.app.models.threat_intel_platform import ThreatActor, ThreatCampaign, MalwareFamily, IndicatorSighting
from backend.app.models.soar_v2 import DeclarativePlaybook, SOARExecutionSession, SOARConnector, SOARKillSwitch
from backend.app.models.ai_security_intelligence import AIModelGovernance, AIModelDriftRecord, AIAdversarialEvent, AICopilotSession
from backend.app.models.cloud_security import (
    CloudAccount, CloudAsset, CSPMFinding, ContainerVulnerabilityScan,
    CloudWorkloadFinding, ServerlessFunctionRisk, KubernetesCluster,
    CloudAttackPath, CloudIAMIdentityRisk
)
from backend.app.models.endpoint_xdr import EndpointTelemetryEvent, EndpointDetection, XDRCorrelationIncident, ZeroTrustDevicePosture, EndpointResponseAction

from backend.app.models.soc_case import SOCCase, SOCCaseTask, SOCCaseComment, SOCCaseAudit
from backend.app.models.evidence_custody import ForensicEvidenceItem, EvidenceCustodyEvent
from backend.app.models.threat_hunting_v2 import SavedHuntingQuery, HuntingInvestigationSession
from backend.app.models.supply_chain import (
    SBOMCatalogItem, VEXStatement, SLSAPipelineAttestation, PipelineSecurityGate
)
from backend.app.models.llm_security import (
    LLMGuardrailPolicy, LLMSecurityEvent, ShadowAIDiscoveryRecord, VectorDBAuditRecord
)












__all__ = [
    "User",
    "AuditLog",
    "Incident",
    "ModelRegistry",
    "ProtectedAsset",
    "Alert",
    "IncidentTimelineEvent",
    "SecurityEvent",
    "MonitoringCheck",
    "MonitoringHistory",
    "ThreatIndicator",
    "ThreatFeed",
    "BehavioralBaseline",
    "AnomalyEvent",
    "Investigation",
    "InvestigationEvidence",
    "PlaybookExecution",
    "HuntingQuery",
    "HuntingExecution",
    "RiskForecast",
    "AlertVolumeForecast",
    "ThreatGraphNode",
    "ThreatGraphEdge",
    "ResponseApproval",
    "AttackCoverageSnapshot",
    "BackgroundJob",
    "ResponsePolicy",
    "ResponseActionRecord",
    "IdempotencyRecord",
    "ResponseAuditLog",
    "DetectionFeedback",
    "Organization",
    "Tenant",
    "TenantMembership",
    "TenantRole",
    "TenantSettings",
    "Subscription",
    "FeatureEntitlement",
    "PlanTier",
    "ApiKey",
    "ApiKeyScope",
    "UsageRecord",
    "UsageQuota",
    "CustomerIntegration",
    "Sensor",
    "BillingWebhookEvent",
    "Invoice",
    "IdentityProvider",
    "UserSession",
    "MFAEnrollment",
    "PAMSessionElevation",
    "IdentityThreatDetection",
    "PasskeyCredential",
    "IdentityScorecard",
    "SCIMConfiguration",

    "SCIMProvisioningEvent",
    "SecurityPolicy",
    "CustomerSecurityEvent",
    "DeclarativePlaybook",
    "SOARExecutionSession",
    "SOARConnector",
    "SOARKillSwitch",
    "AIModelGovernance",
    "AIModelDriftRecord",
    "AIAdversarialEvent",
    "AICopilotSession",
    "CloudAccount",
    "CloudAsset",
    "CSPMFinding",
    "ContainerVulnerabilityScan",
    "CloudWorkloadFinding",
    "ServerlessFunctionRisk",
    "KubernetesCluster",
    "CloudAttackPath",
    "CloudIAMIdentityRisk",

    "EndpointTelemetryEvent",
    "EndpointDetection",
    "XDRCorrelationIncident",
    "ZeroTrustDevicePosture",
    "EndpointResponseAction",
    "IntegrationConnector",
    "EventBusContract",
    "WebhookDelivery",
    "SOCCase",
    "SOCCaseTask",
    "SOCCaseComment",
    "SOCCaseAudit",
    "ForensicEvidenceItem",
    "EvidenceCustodyEvent",
    "SavedHuntingQuery",
    "HuntingInvestigationSession",
    "SBOMCatalogItem",
    "VEXStatement",
    "SLSAPipelineAttestation",
    "PipelineSecurityGate",
    "LLMGuardrailPolicy",
    "LLMSecurityEvent",
    "ShadowAIDiscoveryRecord",
    "VectorDBAuditRecord"
]









