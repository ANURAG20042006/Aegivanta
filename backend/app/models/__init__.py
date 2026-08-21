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
from backend.app.models.attack_surface import (
    ExternalAsset, DanglingDNSRisk, DarkWebCredentialLeak, BrandImpersonationAlert
)
from backend.app.models.threat_intel_v2 import (
    ThreatActorProfile, STIXFeedSource, CTIIndicatorRecord, CampaignHeatmapItem
)
from backend.app.models.deception import (
    HoneypotNode, CanaryToken, DeceptionInteractionEvent, EndpointLureDeployment
)
from backend.app.models.vulnerability_mgmt import (
    VulnerabilityRecord, AssetVulnerabilityMapping, VirtualPatchRule, RemediationCampaign
)
from backend.app.models.dlp_security import (
    DLPInspectionPolicy, DLPIncidentEvent, TokenizedDataVault, ShadowDataStore
)
from backend.app.models.microsegmentation import (
    ZTNAConnectorNode, MicrosegmentationPolicy, ZTNAAccessSession, LateralMovementBlockedAlert
)
from backend.app.models.ai_soc_ueba import (
    UEBAUserProfile, AISOCInvestigation, InsiderThreatIndicator, AISOCDecisionAudit
)
from backend.app.models.compliance_detection_eng import (
    AutonomousDetectionRule, ComplianceFrameworkControl, ComplianceAuditReport, DetectionSandboxExecution
)
from backend.app.models.predictive_intel import (
    PredictiveThreatForecast, AdversarialVectorSimulation, ThreatHorizonIndicator
)
from backend.app.models.federated_threat_sharing import (
    FederatedIOCExchangeNode, FederatedThreatIndicator, HomomorphicMatchQuery
)
from backend.app.models.edge_security_fabric import (
    GlobalEdgePoPNode, EdgeInspectionPolicy, RegionalIngestionRoute
)
from backend.app.models.multi_region_resilience import (
    RegionReplicationCluster, DataResidencyBoundary, FailoverExecutionEvent
)
from backend.app.models.data_governance_dsar import (
    DataLineageRecord, LegalHoldOrder, DSARPrivacyRequest
)
from backend.app.models.security_marketplace import (
    MarketplacePackage, InstalledExtension, PackageReviewRating
)
from backend.app.models.developer_webhooks import (
    DeveloperApiKey, WebhookSubscription, WebhookDeliveryLog
)
from backend.app.models.security_automation_studio import (
    AutomationPlaybook, PlaybookExecutionRun, PlaybookTemplate
)
from backend.app.models.executive_security_intelligence import (
    CISOBoardReport, CyberROIRecord, ExecutiveKPISnapshot
)
from backend.app.models.ai_ml_model_platform import (
    MLModelRegistryV2, MLModelDriftRecord, AdversarialAttackEvent
)
from backend.app.models.autonomous_control_plane import (
    AutonomousDefenseMission, DefenseWarRoomSession, WarRoomActionDecision
)
from backend.app.models.global_enterprise_certification import (
    EnterpriseCertificationBadge, ProductionReadinessGate, AutonomousDefenseAttestation
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
    "VectorDBAuditRecord",
    "ExternalAsset",
    "DanglingDNSRisk",
    "DarkWebCredentialLeak",
    "BrandImpersonationAlert",
    "ThreatActorProfile",
    "STIXFeedSource",
    "CTIIndicatorRecord",
    "CampaignHeatmapItem",
    "HoneypotNode",
    "CanaryToken",
    "DeceptionInteractionEvent",
    "EndpointLureDeployment",
    "VulnerabilityRecord",
    "AssetVulnerabilityMapping",
    "VirtualPatchRule",
    "RemediationCampaign",
    "DLPInspectionPolicy",
    "DLPIncidentEvent",
    "TokenizedDataVault",
    "ShadowDataStore",
    "ZTNAConnectorNode",
    "MicrosegmentationPolicy",
    "ZTNAAccessSession",
    "LateralMovementBlockedAlert",
    "UEBAUserProfile",
    "AISOCInvestigation",
    "InsiderThreatIndicator",
    "AISOCDecisionAudit",
    "AutonomousDetectionRule",
    "ComplianceFrameworkControl",
    "ComplianceAuditReport",
    "DetectionSandboxExecution",
    "PredictiveThreatForecast",
    "AdversarialVectorSimulation",
    "ThreatHorizonIndicator",
    "FederatedIOCExchangeNode",
    "FederatedThreatIndicator",
    "HomomorphicMatchQuery",
    "GlobalEdgePoPNode",
    "EdgeInspectionPolicy",
    "RegionalIngestionRoute",
    "RegionReplicationCluster",
    "DataResidencyBoundary",
    "FailoverExecutionEvent",
    "DataLineageRecord",
    "LegalHoldOrder",
    "DSARPrivacyRequest",
    "MarketplacePackage",
    "InstalledExtension",
    "PackageReviewRating",
    "DeveloperApiKey",
    "WebhookSubscription",
    "WebhookDeliveryLog",
    "AutomationPlaybook",
    "PlaybookExecutionRun",
    "PlaybookTemplate"
]

























