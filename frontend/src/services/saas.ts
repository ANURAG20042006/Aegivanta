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
  }
};



