import axios from 'axios';

const API_BASE = '/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  const activeTenantId = localStorage.getItem('active_tenant_id');
  return {
    headers: {
      Authorization: `Bearer ${token}`,
      ...(activeTenantId ? { 'X-Tenant-ID': activeTenantId } : {})
    }
  };
};

export interface Organization {
  id: string;
  name: string;
  slug: string;
  billing_email: string;
  plan_tier: string;
  status: string;
}

export interface Member {
  id: string;
  user_id: string;
  username?: string;
  email?: string;
  role: string;
  status: string;
}

export interface Tenant {
  id: string;
  organization_id: string;
  name: string;
  slug: string;
  environment_type: string;
  is_active: boolean;
}

export interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  rate_limit_rpm: number;
  is_active: boolean;
  last_used_at?: string;
  created_at: string;
}

export interface SubscriptionInfo {
  organization_id: string;
  plan_tier: string;
  status: string;
  seat_limit: number;
  telemetry_limit_gb_monthly: number;
  current_period_start: string;
  current_period_end: string;
  features: string[];
}

export interface SensorItem {
  id: string;
  name: string;
  hostname: string;
  ip_address: string;
  os_type: string;
  sensor_version: string;
  status: string;
  last_heartbeat: string;
  created_at: string;
}

export interface IntegrationItem {
  id: string;
  organization_id: string;
  integration_type: string;
  name: string;
  status: string;
  config_json?: Record<string, any>;
  last_sync_at?: string;
  created_at: string;
}

export const saasApi = {
  // Organizations
  listMyOrganizations: async (): Promise<Organization[]> => {
    const res = await axios.get(`${API_BASE}/organizations/me`, getAuthHeaders());
    return res.data;
  },
  createOrganization: async (data: { name: string; slug: string; billing_email: string; plan_tier?: string }): Promise<Organization> => {
    const res = await axios.post(`${API_BASE}/organizations`, data, getAuthHeaders());
    return res.data;
  },
  listMembers: async (orgId: string): Promise<Member[]> => {
    const res = await axios.get(`${API_BASE}/organizations/${orgId}/members`, getAuthHeaders());
    return res.data;
  },
  inviteMember: async (orgId: string, data: { email: string; role: string }): Promise<Member> => {
    const res = await axios.post(`${API_BASE}/organizations/${orgId}/members`, data, getAuthHeaders());
    return res.data;
  },

  // Tenants
  listTenants: async (): Promise<Tenant[]> => {
    const res = await axios.get(`${API_BASE}/tenants`, getAuthHeaders());
    return res.data;
  },
  createTenant: async (data: { name: string; slug: string; environment_type?: string }): Promise<Tenant> => {
    const res = await axios.post(`${API_BASE}/tenants`, data, getAuthHeaders());
    return res.data;
  },

  // Subscriptions & Billing
  getCurrentSubscription: async (): Promise<SubscriptionInfo> => {
    const res = await axios.get(`${API_BASE}/subscriptions/current`, getAuthHeaders());
    return res.data;
  },
  getUsage: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/subscriptions/usage`, getAuthHeaders());
    return res.data;
  },
  upgradePlan: async (new_plan_tier: string): Promise<SubscriptionInfo> => {
    const res = await axios.post(`${API_BASE}/subscriptions/upgrade`, { new_plan_tier }, getAuthHeaders());
    return res.data;
  },

  // API Keys
  listApiKeys: async (): Promise<ApiKeyItem[]> => {
    const res = await axios.get(`${API_BASE}/api-keys`, getAuthHeaders());
    return res.data;
  },
  createApiKey: async (data: { name: string; scopes: string[]; rate_limit_rpm?: number }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/api-keys`, data, getAuthHeaders());
    return res.data;
  },
  revokeApiKey: async (keyId: string): Promise<void> => {
    await axios.delete(`${API_BASE}/api-keys/${keyId}`, getAuthHeaders());
  },

  // Sensors
  listSensors: async (): Promise<SensorItem[]> => {
    const res = await axios.get(`${API_BASE}/sensors`, getAuthHeaders());
    return res.data;
  },
  enrollSensor: async (data: { name: string; hostname: string; ip_address: string; os_type?: string; sensor_type?: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/sensors/enroll`, data, getAuthHeaders());
    return res.data;
  },
  revokeSensor: async (sensorId: string): Promise<void> => {
    await axios.delete(`${API_BASE}/sensors/${sensorId}`, getAuthHeaders());
  },
  rotateSensorToken: async (sensorId: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/sensors/${sensorId}/rotate-token`, {}, getAuthHeaders());
    return res.data;
  },
  scheduleSensorUpgrade: async (sensorId: string, target_version: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/sensors/${sensorId}/upgrade`, { target_version }, getAuthHeaders());
    return res.data;
  },
  getSensorInstallCommand: async (sensorId: string, os_type?: string): Promise<any> => {
    const res = await axios.get(`${API_BASE}/sensors/${sensorId}/install-command?os_type=${os_type || 'linux'}`, getAuthHeaders());
    return res.data;
  },
  getFleetHealth: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/sensors/fleet/health`, getAuthHeaders());
    return res.data;
  },


  // Integrations
  listIntegrations: async (): Promise<IntegrationItem[]> => {
    const res = await axios.get(`${API_BASE}/integrations`, getAuthHeaders());
    return res.data;
  },
  createIntegration: async (data: { integration_type: string; name: string; config: Record<string, any> }): Promise<IntegrationItem> => {
    const res = await axios.post(`${API_BASE}/integrations`, data, getAuthHeaders());
    return res.data;
  },
  testIntegration: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/integrations/${id}/test`, {}, getAuthHeaders());
    return res.data;
  },
  deleteIntegration: async (id: string): Promise<void> => {
    await axios.delete(`${API_BASE}/integrations/${id}`, getAuthHeaders());
  },

  // Onboarding
  getOnboardingStatus: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/onboarding/status`, getAuthHeaders());
    return res.data;
  },

  // Phase 5 Enterprise Security Center APIs
  setupMFA: async (): Promise<{ secret: string; recovery_codes: string[]; otpauth_uri: string }> => {
    const res = await axios.post(`${API_BASE}/identity/mfa/setup`, {}, getAuthHeaders());
    return res.data;
  },
  verifyMFA: async (code: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/identity/mfa/verify`, { code }, getAuthHeaders());
    return res.data;
  },
  listSessions: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/identity/sessions`, getAuthHeaders());
    return res.data;
  },
  revokeSession: async (sessionId: string): Promise<void> => {
    await axios.delete(`${API_BASE}/identity/sessions/${sessionId}`, getAuthHeaders());
  },
  configureSSO: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/identity/sso/config`, data, getAuthHeaders());
    return res.data;
  },
  getSecurityPosture: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/security/posture`, getAuthHeaders());
    return res.data;
  },
  getSecurityPolicies: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/security/policies`, getAuthHeaders());
    return res.data;
  },
  updateSecurityPolicies: async (data: any): Promise<any> => {
    const res = await axios.put(`${API_BASE}/security/policies`, data, getAuthHeaders());
    return res.data;
  },
  listSecurityEvents: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/security/events`, getAuthHeaders());
    return res.data;
  },

  // AI Security Copilot & Detection Content
  queryCopilot: async (query: string, incident_id?: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/copilot/query`, { query, incident_id }, getAuthHeaders());
    return res.data;
  },
  explainIncident: async (incidentId: string): Promise<any> => {
    const res = await axios.get(`${API_BASE}/copilot/incidents/${incidentId}/explain`, getAuthHeaders());
    return res.data;
  },
  listDetectionRules: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/detection-rules`, getAuthHeaders());
    return res.data;
  },
  createDetectionRule: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/detection-rules`, data, getAuthHeaders());
    return res.data;
  },
  testDetectionRule: async (data: { rule_dsl: any; sample_events: any[] }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/detection-rules/test`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 16 Production Intelligence & Value APIs
  getDetectionQuality: async (lookback_days: number = 30): Promise<any> => {
    const res = await axios.get(`${API_BASE}/detection/quality?lookback_days=${lookback_days}`, getAuthHeaders());
    return res.data;
  },
  getDetectionQualityHistory: async (limit: number = 30): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/detection/quality/history?limit=${limit}`, getAuthHeaders());
    return res.data;
  },
  listBenchmarks: async (limit: number = 20): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/detection/benchmarks?limit=${limit}`, getAuthHeaders());
    return res.data;
  },
  getAlertPriority: async (alertId: string): Promise<any> => {
    const res = await axios.get(`${API_BASE}/alerts/${alertId}/priority`, getAuthHeaders());
    return res.data;
  },
  listAlertGroups: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/alerts/groups/active`, getAuthHeaders());
    return res.data;
  },
  getIncidentTimeline: async (incidentId: string): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/incidents/${incidentId}/timeline`, getAuthHeaders());
    return res.data;
  },
  transitionIncidentStatus: async (incidentId: string, data: { new_status: string; reason?: string; notes?: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/incidents/${incidentId}/transition`, data, getAuthHeaders());
    return res.data;
  },
  assignIncidentAnalyst: async (incidentId: string, analyst_username: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/incidents/${incidentId}/assign`, { analyst_username }, getAuthHeaders());
    return res.data;
  },
  searchInvestigations: async (payload: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/investigations/search`, payload, getAuthHeaders());
    return res.data;
  },
  getSecurityValue: async (lookback_days: number = 30): Promise<any> => {
    const res = await axios.get(`${API_BASE}/analytics/security-value?lookback_days=${lookback_days}`, getAuthHeaders());
    return res.data;
  },
  getPostureImprovements: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/security-posture/improvements`, getAuthHeaders());
    return res.data;
  },
  getTelemetryCostIntelligence: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/telemetry/cost-intelligence`, getAuthHeaders());
    return res.data;
  },
  getProductAnalytics: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/analytics/product`, getAuthHeaders());
    return res.data;
  },

  // Phase 17 Autonomous Threat Response & Continuous Validation APIs
  getAutonomousPolicy: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/autonomous-response/policy`, getAuthHeaders());
    return res.data;
  },
  updateAutonomousPolicy: async (data: any): Promise<any> => {
    const res = await axios.put(`${API_BASE}/autonomous-response/policy`, data, getAuthHeaders());
    return res.data;
  },
  simulateResponse: async (data: { incident_id: string; action_type: string; target_entity: string; parameters?: any }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/autonomous-response/simulate`, data, getAuthHeaders());
    return res.data;
  },
  executeResponse: async (data: { incident_id: string; action_type: string; target_entity: string; bypass_approval?: boolean }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/autonomous-response/execute`, data, getAuthHeaders());
    return res.data;
  },
  rollbackResponse: async (actionId: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/autonomous-response/${actionId}/rollback`, {}, getAuthHeaders());
    return res.data;
  },
  getSecurityValidation: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/security/validation`, getAuthHeaders());
    return res.data;
  },
  runSecurityValidation: async (): Promise<any> => {
    const res = await axios.post(`${API_BASE}/security/validation/run`, {}, getAuthHeaders());
    return res.data;
  },
  listSimulations: async (limit: number = 20): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/security/simulations?limit=${limit}`, getAuthHeaders());
    return res.data;
  },
  runSimulation: async (attack_technique: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/security/simulations`, { attack_technique }, getAuthHeaders());
    return res.data;
  },
  getSimulationDetails: async (id: string): Promise<any> => {
    const res = await axios.get(`${API_BASE}/security/simulations/${id}`, getAuthHeaders());
    return res.data;
  },
  getCoverageGaps: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/detection/coverage/gaps`, getAuthHeaders());
    return res.data;
  },
  getAttackPaths: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/security/attack-paths`, getAuthHeaders());
    return res.data;
  },
  getAssetRisks: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/assets/risk`, getAuthHeaders());
    return res.data;
  },
  getControlEffectiveness: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/security/control-effectiveness`, getAuthHeaders());
    return res.data;
  },

  // Phase 18 Threat Intelligence & Threat Hunting Platform APIs
  listThreatActors: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/threat-intelligence/actors`, getAuthHeaders());
    return res.data;
  },
  createThreatActor: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/threat-intelligence/actors`, data, getAuthHeaders());
    return res.data;
  },
  listThreatCampaigns: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/threat-intelligence/campaigns`, getAuthHeaders());
    return res.data;
  },
  createThreatCampaign: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/threat-intelligence/campaigns`, data, getAuthHeaders());
    return res.data;
  },
  correlateThreatIndicator: async (ioc_value: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/threat-intelligence/correlate`, { ioc_value }, getAuthHeaders());
    return res.data;
  },
  recordThreatSighting: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/threat-intelligence/sightings`, data, getAuthHeaders());
    return res.data;
  },
  syncThreatFeed: async (feedId: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/threat-intelligence/feeds/${feedId}/sync`, {}, getAuthHeaders());
    return res.data;
  },
  getHuntingTemplates: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/hunting-workbench/templates`, getAuthHeaders());
    return res.data;
  },
  executeAdvancedHunt: async (data: { target_entity: string; query_pattern: string; limit?: number }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/hunting-workbench/execute`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 19 Autonomous SOC & SOAR 2.0 APIs
  listSOARPlaybooks: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/soar/playbooks`, getAuthHeaders());
    return res.data;
  },
  createSOARPlaybook: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/soar/playbooks`, data, getAuthHeaders());
    return res.data;
  },
  executeSOARPlaybook: async (id: string, data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/soar/playbooks/${id}/execute`, data, getAuthHeaders());
    return res.data;
  },
  dryRunSOARPlaybook: async (id: string, data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/soar/playbooks/${id}/dry-run`, data, getAuthHeaders());
    return res.data;
  },
  listSOARExecutions: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/soar/executions`, getAuthHeaders());
    return res.data;
  },
  evaluateSOARDecision: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/soar/decision/evaluate`, data, getAuthHeaders());
    return res.data;
  },
  getSOARKillSwitch: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/soar/kill-switch`, getAuthHeaders());
    return res.data;
  },
  toggleSOARKillSwitch: async (data: { is_active: boolean; reason?: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/soar/kill-switch`, data, getAuthHeaders());
    return res.data;
  },
  listSOARConnectors: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/soar/connectors`, getAuthHeaders());
    return res.data;
  },
  testSOARConnectorHealth: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/soar/connectors/${id}/health-check`, {}, getAuthHeaders());
    return res.data;
  },

  // Phase 20 Advanced AI/ML Security Intelligence APIs
  listAIModels: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/ai-intel/models`, getAuthHeaders());
    return res.data;
  },
  registerAIModel: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-intel/models/register`, data, getAuthHeaders());
    return res.data;
  },
  promoteAIModel: async (id: string, data: { target_stage: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-intel/models/${id}/promote`, data, getAuthHeaders());
    return res.data;
  },
  rollbackAIModel: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-intel/models/${id}/rollback`, {}, getAuthHeaders());
    return res.data;
  },
  verifyAIModelSignature: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-intel/models/${id}/verify-signature`, {}, getAuthHeaders());
    return res.data;
  },
  getAIModelDrift: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/ai-intel/drift`, getAuthHeaders());
    return res.data;
  },
  getAIDetectionQuality: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/ai-intel/quality`, getAuthHeaders());
    return res.data;
  },
  executeMultiModelDetection: async (data: { features: Record<string, number>; entity_id?: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-intel/detect/multi-model`, data, getAuthHeaders());
    return res.data;
  },
  listAIAdversarialEvents: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/ai-intel/adversarial/events`, getAuthHeaders());
    return res.data;
  },
  reasonAICopilot: async (data: { prompt: string; incident_id?: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-intel/copilot/reason`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 21 Cloud & Container Security APIs
  getCloudInventory: async (provider?: string, asset_type?: string): Promise<any[]> => {
    const params: any = {};
    if (provider) params.provider = provider;
    if (asset_type) params.asset_type = asset_type;
    const res = await axios.get(`${API_BASE}/cloud-security/inventory`, { ...getAuthHeaders(), params });
    return res.data;
  },
  runCSPMScan: async (): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/cspm/scan`, {}, getAuthHeaders());
    return res.data;
  },
  getCSPMFindings: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/cloud-security/cspm/findings`, getAuthHeaders());
    return res.data;
  },
  scanContainerImage: async (data: { image_name: string; image_tag?: string; signature_token?: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/containers/scan`, data, getAuthHeaders());
    return res.data;
  },
  listContainerScans: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/cloud-security/containers/scans`, getAuthHeaders());
    return res.data;
  },
  auditK8sManifest: async (data: { manifest_yaml: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/k8s/audit-manifest`, data, getAuthHeaders());
    return res.data;
  },
  getCloudIAMAnalysis: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/cloud-security/iam/analysis`, getAuthHeaders());
    return res.data;
  },
  getCloudAttackPaths: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/cloud-security/attack-paths`, getAuthHeaders());
    return res.data;
  },

  // Phase 22 Endpoint XDR & Zero-Trust APIs
  getEndpointTelemetry: async (event_category?: string, hostname?: string): Promise<any[]> => {
    const params: any = {};
    if (event_category) params.event_category = event_category;
    if (hostname) params.hostname = hostname;
    const res = await axios.get(`${API_BASE}/endpoint-xdr/telemetry`, { ...getAuthHeaders(), params });
    return res.data;
  },
  getEndpointDetections: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/endpoint-xdr/detections`, getAuthHeaders());
    return res.data;
  },
  getXDRIncidents: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/endpoint-xdr/xdr/incidents`, getAuthHeaders());
    return res.data;
  },
  getZeroTrustPostures: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/endpoint-xdr/zero-trust/posture`, getAuthHeaders());
    return res.data;
  },
  evaluateZeroTrustPosture: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/endpoint-xdr/zero-trust/evaluate`, data, getAuthHeaders());
    return res.data;
  },
  executeEndpointResponse: async (data: { sensor_id: string; hostname: string; action_type: string; target_entity: string; reason: string; approval_id?: string }): Promise<any> => {
    const res = await axios.post(`${API_BASE}/endpoint-xdr/response/execute`, data, getAuthHeaders());
    return res.data;
  },
  rollbackEndpointResponse: async (actionId: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/endpoint-xdr/response/rollback/${actionId}`, {}, getAuthHeaders());
    return res.data;
  },

  // Phase 23 Integration Ecosystem APIs
  getIntegrationCatalog: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/integrations/marketplace/catalog`, getAuthHeaders());
    return res.data;
  },
  getConnectors: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/integrations/connectors`, getAuthHeaders());
    return res.data;
  },
  registerConnector: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/integrations/connectors/register`, data, getAuthHeaders());
    return res.data;
  },
  getWebhookDeliveries: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/integrations/webhooks/deliveries`, getAuthHeaders());
    return res.data;
  },
  getIntegrationHealthDashboard: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/integrations/health/dashboard`, getAuthHeaders());
    return res.data;
  },

  // Phase 24 Global Ops / FinOps / SRE APIs
  getFinOpsDashboard: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/global-ops/finops/dashboard`, getAuthHeaders());
    return res.data;
  },
  getCapacityDashboard: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/global-ops/capacity/dashboard`, getAuthHeaders());
    return res.data;
  },
  getSLODashboard: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/global-ops/sre/slo-dashboard`, getAuthHeaders());
    return res.data;
  },

  // Phase 26 Autonomous SOC Intelligence & Continuous Security Validation APIs
  getContinuousValidation: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/security/continuous-validation`, getAuthHeaders());
    return res.data;
  },
  runContinuousValidation: async (): Promise<any> => {
    const res = await axios.post(`${API_BASE}/security/continuous-validation/run`, {}, getAuthHeaders());
    return res.data;
  },
  getSecurityScorecard: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/security/scorecard`, getAuthHeaders());
    return res.data;
  },
  getSOCCases: async (status?: string, priority?: string): Promise<any[]> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (priority) params.append('priority', priority);
    const res = await axios.get(`${API_BASE}/soc/cases?${params.toString()}`, getAuthHeaders());
    return res.data;
  },
  createSOCCase: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/soc/cases`, data, getAuthHeaders());
    return res.data;
  },
  getSOCCaseDetails: async (id: string): Promise<any> => {
    const res = await axios.get(`${API_BASE}/soc/cases/${id}`, getAuthHeaders());
    return res.data;
  },
  updateSOCCaseStatus: async (id: string, newStatus: string): Promise<any> => {
    const res = await axios.put(`${API_BASE}/soc/cases/${id}/status`, { status: newStatus }, getAuthHeaders());
    return res.data;
  },
  getSavedHuntingQueries: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/hunting/v2/saved`, getAuthHeaders());
    return res.data;
  },
  executeHuntingSearch: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/hunting/v2/search`, data, getAuthHeaders());
    return res.data;
  },
  queryAIAnalyst: async (query: string, caseId?: string, incidentId?: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-analyst/v2/investigate`, { query, case_id: caseId, incident_id: incidentId }, getAuthHeaders());
    return res.data;
  },
  getCorrelationGraph: async (incidentId: string): Promise<any> => {
    const res = await axios.get(`${API_BASE}/ai-analyst/v2/correlation/${incidentId}`, getAuthHeaders());
    return res.data;
  },
  getSREHealth: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/sre/health`, getAuthHeaders());
    return res.data;
  },
  getSRESLO: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/sre/slo`, getAuthHeaders());
    return res.data;
  },
  getSREErrorBudget: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/sre/error-budget`, getAuthHeaders());
    return res.data;
  },
  getChaosScenarios: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/sre/chaos/scenarios`, getAuthHeaders());
    return res.data;
  },
  runChaosSimulation: async (scenarioKey: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/sre/chaos/run`, { scenario_key: scenarioKey }, getAuthHeaders());
    return res.data;
  },

  // Phase 27 Cloud Security & CNAPP APIs
  getCNAPPSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/cloud-security/cnapp/summary`, getAuthHeaders());
    return res.data;
  },
  getCloudAccounts: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/cloud-security/accounts`, getAuthHeaders());
    return res.data;
  },
  connectCloudAccount: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/accounts`, data, getAuthHeaders());
    return res.data;
  },
  syncCloudAccount: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/accounts/${id}/sync`, {}, getAuthHeaders());
    return res.data;
  },
  getCWPPFindings: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/cloud-security/cwpp/findings`, getAuthHeaders());
    return res.data;
  },
  simulateCWPPThreat: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/cwpp/simulate-threat`, data, getAuthHeaders());
    return res.data;
  },
  containWorkload: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/cwpp/contain/${id}`, {}, getAuthHeaders());
    return res.data;
  },
  getServerlessFindings: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/cloud-security/serverless/findings`, getAuthHeaders());
    return res.data;
  },
  auditServerlessFunction: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/serverless/audit`, data, getAuthHeaders());
    return res.data;
  },
  getK8sClusters: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/cloud-security/k8s/clusters`, getAuthHeaders());
    return res.data;
  },
  enrollK8sCluster: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/cloud-security/k8s/clusters/enroll`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 28 Enterprise Identity, PAM & Zero Trust 2.0 APIs
  getIAMSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/iam/summary`, getAuthHeaders());
    return res.data;
  },
  getPAMElevations: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/iam/pam/elevations`, getAuthHeaders());
    return res.data;
  },
  requestJITElevation: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/iam/pam/request-elevation`, data, getAuthHeaders());
    return res.data;
  },
  approveJITElevation: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/iam/pam/approve/${id}`, {}, getAuthHeaders());
    return res.data;
  },
  revokeJITElevation: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/iam/pam/revoke/${id}`, {}, getAuthHeaders());
    return res.data;
  },
  getITDRDetections: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/iam/itdr/detections`, getAuthHeaders());
    return res.data;
  },
  simulateITDREvent: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/iam/itdr/simulate-attack`, data, getAuthHeaders());
    return res.data;
  },
  evaluateZeroTrustSession: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/iam/zero-trust/evaluate-session`, data, getAuthHeaders());
    return res.data;
  },
  getRegisteredPasskeys: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/iam/passkeys`, getAuthHeaders());
    return res.data;
  },
  getIdentityScorecards: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/iam/governance/scorecards`, getAuthHeaders());
    return res.data;
  },
  reapDormantIdentities: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/iam/governance/reap-dormant`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 29 Supply Chain Security, SBOM 2.0 & SLSA Level 3 APIs
  getSupplyChainSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/supply-chain/summary`, getAuthHeaders());
    return res.data;
  },
  getSBOMComponents: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/supply-chain/sbom/components`, getAuthHeaders());
    return res.data;
  },
  generateSBOMExport: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/supply-chain/sbom/generate`, data, getAuthHeaders());
    return res.data;
  },
  getVEXStatements: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/supply-chain/vex/statements`, getAuthHeaders());
    return res.data;
  },
  publishVEXStatement: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/supply-chain/vex/publish`, data, getAuthHeaders());
    return res.data;
  },
  getSLSAAttestations: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/supply-chain/slsa/attestations`, getAuthHeaders());
    return res.data;
  },
  verifySLSAProvenance: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/supply-chain/slsa/verify`, data, getAuthHeaders());
    return res.data;
  },
  getPipelineGates: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/supply-chain/gates`, getAuthHeaders());
    return res.data;
  },
  evaluatePipelineGate: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/supply-chain/gates/evaluate`, data, getAuthHeaders());
    return res.data;
  },
  scanCodeSecrets: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/supply-chain/secrets/scan`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 30 AI/LLM Security & Shadow AI APIs
  getAISecuritySummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/llm-security/summary`, getAuthHeaders());
    return res.data;
  },
  inspectLLMPrompt: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/llm-security/guardrails/inspect`, data, getAuthHeaders());
    return res.data;
  },
  getLLMSecurityEvents: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/llm-security/events`, getAuthHeaders());
    return res.data;
  },
  getShadowAITools: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/llm-security/shadow-ai`, getAuthHeaders());
    return res.data;
  },
  toggleShadowAIBlock: async (id: string, data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/llm-security/shadow-ai/block/${id}`, data, getAuthHeaders());
    return res.data;
  },
  getVectorDBAudits: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/llm-security/vectordb/audits`, getAuthHeaders());
    return res.data;
  },
  scanVectorDBCollection: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/llm-security/vectordb/scan`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 31 Attack Surface Management (ASM) & CTEM APIs
  getASMSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/attack-surface/summary`, getAuthHeaders());
    return res.data;
  },
  getExternalAssets: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/attack-surface/assets`, getAuthHeaders());
    return res.data;
  },
  discoverExternalDomain: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/attack-surface/assets/discover`, data, getAuthHeaders());
    return res.data;
  },
  getDanglingDNS: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/attack-surface/dangling-dns`, getAuthHeaders());
    return res.data;
  },
  getDarkWebCredentials: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/attack-surface/darkweb/credentials`, getAuthHeaders());
    return res.data;
  },
  getBrandTyposquats: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/attack-surface/brand/typosquats`, getAuthHeaders());
    return res.data;
  },
  getCTEMPrioritizedExposures: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/attack-surface/ctem/prioritized-exposures`, getAuthHeaders());
    return res.data;
  },

  // Phase 32 Cyber Threat Intelligence (CTI) 2.0 APIs
  getCTISummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/threat-intel-v2/summary`, getAuthHeaders());
    return res.data;
  },
  getThreatActors: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/threat-intel-v2/actors`, getAuthHeaders());
    return res.data;
  },
  getSTIXFeeds: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/threat-intel-v2/feeds`, getAuthHeaders());
    return res.data;
  },
  pollSTIXFeed: async (id: string): Promise<any> => {
    const res = await axios.post(`${API_BASE}/threat-intel-v2/feeds/poll/${id}`, {}, getAuthHeaders());
    return res.data;
  },
  getCTIIndicators: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/threat-intel-v2/indicators`, getAuthHeaders());
    return res.data;
  },
  getCampaignHeatmaps: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/threat-intel-v2/campaigns/heatmap`, getAuthHeaders());
    return res.data;
  },
  generateThreatHuntingQueries: async (data: any): Promise<any[]> => {
    const res = await axios.post(`${API_BASE}/threat-intel-v2/hunting/generate-queries`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 33 Deception Technology & Honeypot Fleet APIs
  getDeceptionSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/deception/summary`, getAuthHeaders());
    return res.data;
  },
  getHoneypots: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/deception/honeypots`, getAuthHeaders());
    return res.data;
  },
  deployHoneypot: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/deception/honeypots/deploy`, data, getAuthHeaders());
    return res.data;
  },
  getCanaries: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/deception/canaries`, getAuthHeaders());
    return res.data;
  },
  generateCanary: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/deception/canaries/generate`, data, getAuthHeaders());
    return res.data;
  },
  triggerCanary: async (id: string, data: any = {}): Promise<any> => {
    const res = await axios.post(`${API_BASE}/deception/canaries/trigger/${id}`, data, getAuthHeaders());
    return res.data;
  },
  getDeceptionInteractions: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/deception/interactions`, getAuthHeaders());
    return res.data;
  },
  getEndpointLures: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/deception/endpoint-lures`, getAuthHeaders());
    return res.data;
  },

  // Phase 34 Risk-Based Vulnerability Management (RBVM) & EPSS 2.0 APIs
  getRBVMSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/vulnerability-mgmt/summary`, getAuthHeaders());
    return res.data;
  },
  getVulnerabilities: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/vulnerability-mgmt/vulnerabilities`, getAuthHeaders());
    return res.data;
  },
  getAssetExposures: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/vulnerability-mgmt/asset-exposures`, getAuthHeaders());
    return res.data;
  },
  getVirtualPatches: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/vulnerability-mgmt/virtual-patches`, getAuthHeaders());
    return res.data;
  },
  deployVirtualPatch: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/vulnerability-mgmt/virtual-patches/deploy`, data, getAuthHeaders());
    return res.data;
  },
  getRemediationCampaigns: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/vulnerability-mgmt/campaigns`, getAuthHeaders());
    return res.data;
  },
  getEPSSDistribution: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/vulnerability-mgmt/epss-distribution`, getAuthHeaders());
    return res.data;
  },

  // Phase 35 Data Loss Prevention (DLP) & Cryptographic Tokenization APIs
  getDLPSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/dlp-security/summary`, getAuthHeaders());
    return res.data;
  },
  getDLPPolicies: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/dlp-security/policies`, getAuthHeaders());
    return res.data;
  },
  inspectPayload: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/dlp-security/inspect`, data, getAuthHeaders());
    return res.data;
  },
  getDLPIncidents: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/dlp-security/incidents`, getAuthHeaders());
    return res.data;
  },
  getTokenVault: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/dlp-security/tokens`, getAuthHeaders());
    return res.data;
  },
  tokenizeData: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/dlp-security/tokens/tokenize`, data, getAuthHeaders());
    return res.data;
  },
  detokenizeData: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/dlp-security/tokens/detokenize`, data, getAuthHeaders());
    return res.data;
  },
  getShadowData: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/dlp-security/shadow-data`, getAuthHeaders());
    return res.data;
  },

  // Phase 36 Microsegmentation & ZTNA 2.0 APIs
  getZTNAMicrosegSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/microsegmentation/summary`, getAuthHeaders());
    return res.data;
  },
  getZTNAConnectors: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/microsegmentation/connectors`, getAuthHeaders());
    return res.data;
  },
  getMicrosegPolicies: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/microsegmentation/policies`, getAuthHeaders());
    return res.data;
  },
  createMicrosegPolicy: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/microsegmentation/policies`, data, getAuthHeaders());
    return res.data;
  },
  getZTNAClients: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/microsegmentation/sessions`, getAuthHeaders());
    return res.data;
  },
  terminateZTNASession: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/microsegmentation/sessions/terminate`, data, getAuthHeaders());
    return res.data;
  },
  getLateralAlerts: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/microsegmentation/lateral-alerts`, getAuthHeaders());
    return res.data;
  },
  getNetworkFlowGraph: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/microsegmentation/network-flow-graph`, getAuthHeaders());
    return res.data;
  },

  // Phase 37 AI SOC Autonomy & UEBA 2.0 APIs
  getAISOCSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/ai-soc-ueba/summary`, getAuthHeaders());
    return res.data;
  },
  getUEBAProfiles: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/ai-soc-ueba/profiles`, getAuthHeaders());
    return res.data;
  },
  getAISOCInvestigations: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/ai-soc-ueba/investigations`, getAuthHeaders());
    return res.data;
  },
  triggerAISOCInvestigation: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-soc-ueba/investigations/trigger`, data, getAuthHeaders());
    return res.data;
  },
  approveAISOCAction: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/ai-soc-ueba/investigations/approve-action`, data, getAuthHeaders());
    return res.data;
  },
  getInsiderThreats: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/ai-soc-ueba/insider-threats`, getAuthHeaders());
    return res.data;
  },
  getAISOCDecisionAudits: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/ai-soc-ueba/decision-audits`, getAuthHeaders());
    return res.data;
  },

  // Phase 38 Autonomous Detection Engineering & Multi-Standard Compliance APIs
  getComplianceDetectionSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/compliance-detection/summary`, getAuthHeaders());
    return res.data;
  },
  getAutonomousDetectionRules: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/compliance-detection/detection-rules`, getAuthHeaders());
    return res.data;
  },
  createAutonomousDetectionRule: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/compliance-detection/detection-rules`, data, getAuthHeaders());
    return res.data;
  },
  testDetectionRuleSandbox: async (data: any): Promise<any> => {

    const res = await axios.post(`${API_BASE}/compliance-detection/detection-rules/test-sandbox`, data, getAuthHeaders());
    return res.data;
  },
  getComplianceControls: async (framework?: string): Promise<any[]> => {
    const params = framework ? { framework } : {};
    const res = await axios.get(`${API_BASE}/compliance-detection/compliance-controls`, { ...getAuthHeaders(), params });
    return res.data;
  },
  getComplianceReports: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/compliance-detection/compliance-reports`, getAuthHeaders());
    return res.data;
  },
  generateComplianceReport: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/compliance-detection/compliance-reports/generate`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 39 Predictive Security Intelligence & Emerging Threat Forecasting APIs
  getPredictiveIntelSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/predictive-intel/summary`, getAuthHeaders());
    return res.data;
  },
  getPredictiveForecasts: async (horizon?: string): Promise<any[]> => {
    const params = horizon ? { horizon } : {};
    const res = await axios.get(`${API_BASE}/predictive-intel/forecasts`, { ...getAuthHeaders(), params });
    return res.data;
  },
  generatePredictiveForecast: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/predictive-intel/forecasts/generate`, data, getAuthHeaders());
    return res.data;
  },
  getAdversarialSimulations: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/predictive-intel/simulations`, getAuthHeaders());
    return res.data;
  },
  getThreatHorizonIndicators: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/predictive-intel/horizon-indicators`, getAuthHeaders());
    return res.data;
  },

  // Phase 40 Privacy-Preserving Threat Intelligence & Federated IOC Exchange APIs
  getFederatedThreatSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/federated-threat/summary`, getAuthHeaders());
    return res.data;
  },
  getFederatedNodes: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/federated-threat/nodes`, getAuthHeaders());
    return res.data;
  },
  getFederatedThreatIndicators: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/federated-threat/indicators`, getAuthHeaders());
    return res.data;
  },
  shareFederatedIndicator: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/federated-threat/indicators/share`, data, getAuthHeaders());
    return res.data;
  },
  executeBlindHomomorphicMatch: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/federated-threat/blind-match`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 41 Global Distributed Edge Security & Regional Ingestion Fabric APIs
  getEdgeFabricSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/edge-fabric/summary`, getAuthHeaders());
    return res.data;
  },
  getEdgePoPs: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/edge-fabric/pops`, getAuthHeaders());
    return res.data;
  },
  getEdgeInspectionPolicies: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/edge-fabric/policies`, getAuthHeaders());
    return res.data;
  },
  createEdgeInspectionPolicy: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/edge-fabric/policies`, data, getAuthHeaders());
    return res.data;
  },
  getRegionalIngestionRoutes: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/edge-fabric/routes`, getAuthHeaders());
    return res.data;
  },

  // Phase 42 Multi-Region Data Resilience, Active-Active Failover & Data Residency APIs
  getMultiRegionSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/multi-region/summary`, getAuthHeaders());
    return res.data;
  },
  getMultiRegionClusters: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/multi-region/clusters`, getAuthHeaders());
    return res.data;
  },
  triggerMultiRegionFailover: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/multi-region/failover`, data, getAuthHeaders());
    return res.data;
  },
  getFailoverEvents: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/multi-region/failover-events`, getAuthHeaders());
    return res.data;
  },
  getDataResidencyBoundaries: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/multi-region/residency`, getAuthHeaders());
    return res.data;
  },
  createDataResidencyBoundary: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/multi-region/residency`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 43 Enterprise Data Governance, Lineage, Legal Hold & DSAR Privacy APIs
  getDataGovernanceSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/governance-dsar/summary`, getAuthHeaders());
    return res.data;
  },
  getDataLineage: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/governance-dsar/lineage`, getAuthHeaders());
    return res.data;
  },
  getLegalHolds: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/governance-dsar/legal-holds`, getAuthHeaders());
    return res.data;
  },
  createLegalHold: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/governance-dsar/legal-holds`, data, getAuthHeaders());
    return res.data;
  },
  getDSARRequests: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/governance-dsar/requests`, getAuthHeaders());
    return res.data;
  },
  createDSARRequest: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/governance-dsar/requests`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 44 Security Marketplace & Ecosystem Package Manager APIs
  getMarketplaceSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/marketplace/summary`, getAuthHeaders());
    return res.data;
  },
  getMarketplacePackages: async (packageType?: string): Promise<any[]> => {
    const url = packageType ? `${API_BASE}/marketplace/packages?package_type=${packageType}` : `${API_BASE}/marketplace/packages`;
    const res = await axios.get(url, getAuthHeaders());
    return res.data;
  },
  getInstalledExtensions: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/marketplace/installed`, getAuthHeaders());
    return res.data;
  },
  installMarketplacePackage: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/marketplace/install`, data, getAuthHeaders());
    return res.data;
  },
  uninstallMarketplacePackage: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/marketplace/uninstall`, data, getAuthHeaders());
    return res.data;
  },
  publishMarketplacePackage: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/marketplace/publish`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 45 Developer Platform, Public Versioned API & Webhooks Engine APIs
  getDeveloperSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/developer/summary`, getAuthHeaders());
    return res.data;
  },
  getDeveloperApiKeys: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/developer/keys`, getAuthHeaders());
    return res.data;
  },
  createDeveloperApiKey: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/developer/keys`, data, getAuthHeaders());
    return res.data;
  },
  getWebhookSubscriptions: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/developer/webhooks`, getAuthHeaders());
    return res.data;
  },
  createWebhookSubscription: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/developer/webhooks`, data, getAuthHeaders());
    return res.data;
  },
  getDeveloperWebhookDeliveries: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/developer/deliveries`, getAuthHeaders());
    return res.data;
  },

  testDispatchWebhook: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/developer/test-dispatch`, data, getAuthHeaders());
    return res.data;
  },

  // Phase 46 Security Automation Studio APIs
  getAutomationStudioSummary: async (): Promise<any> => {
    const res = await axios.get(`${API_BASE}/automation-studio/summary`, getAuthHeaders());
    return res.data;
  },
  getAutomationPlaybooks: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/automation-studio/playbooks`, getAuthHeaders());
    return res.data;
  },
  createAutomationPlaybook: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/automation-studio/playbooks`, data, getAuthHeaders());
    return res.data;
  },
  getPlaybookExecutions: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/automation-studio/executions`, getAuthHeaders());
    return res.data;
  },
  simulatePlaybookExecution: async (data: any): Promise<any> => {
    const res = await axios.post(`${API_BASE}/automation-studio/simulate`, data, getAuthHeaders());
    return res.data;
  },
  getPlaybookTemplates: async (): Promise<any[]> => {
    const res = await axios.get(`${API_BASE}/automation-studio/templates`, getAuthHeaders());
    return res.data;
  }
};
































