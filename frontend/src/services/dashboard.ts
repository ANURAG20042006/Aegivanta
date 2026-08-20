import api from './api';

export interface SOCOverviewMetrics {
  total_incidents: number;
  open_incidents: number;
  critical_incidents: number;
  high_incidents: number;
  mean_time_to_detect_minutes: number;
  mean_time_to_acknowledge_minutes: number;
  mean_time_to_respond_minutes: number;
  mean_time_to_resolve_minutes: number;
  active_investigations: number;
  active_soar_actions: number;
  failed_response_actions: number;
  ioc_matches: number;
  detection_rate_per_hour: number;
  false_positive_rate_pct: number;
  event_ingestion_rate_eps: number;
  mitre_coverage_pct: number;
  attack_graph_nodes: number;
  attack_graph_edges: number;
  system_status: string;
  operating_mode: string;
  generated_at: string;
}

export interface DashboardIncidentItem {
  id: string;
  incident_code: string;
  title: string;
  description?: string;
  severity: string;
  risk_score: number;
  status: string;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol: string;
  attack_type: string;
  confidence_score?: number;
  is_malicious: boolean;
  asset_id?: string;
  asset_name?: string;
  asset_criticality?: string;
  ioc_matches?: string[];
  mitre_techniques?: string[];
  alert_count: number;
  analyst?: string;
  notes?: string;
  resolution?: string;
  remediation_action?: string;
  timestamp: string;
  first_seen?: string;
  last_seen?: string;
  triaged_at?: string;
  closed_at?: string;
}

export interface DashboardIncidentsResponse {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  items: DashboardIncidentItem[];
}

export interface DetectionsSummary {
  total_detections: number;
  lookback_days: number;
  severity_breakdown: Record<string, number>;
  attack_type_distribution: Array<{ attack_type: string; count: number }>;
  recent_detections: Array<{
    id: string;
    timestamp: string;
    source_ip: string;
    destination_ip: string;
    attack_type: string;
    severity: string;
    confidence_score?: number;
    is_malicious: boolean;
    rule_id?: string;
  }>;
  false_positive_estimate_pct: number;
}

export interface ThreatIntelDashboardData {
  active_indicators_count: number;
  expired_indicators_count: number;
  archived_indicators_count: number;
  total_indicators_count: number;
  ioc_type_distribution: Record<string, number>;
  total_feeds: number;
  active_feeds: number;
  failed_feeds_count: number;
  failed_feeds: Array<{
    id: string;
    feed_name: string;
    provider_type: string;
    is_active: boolean;
    last_synced_at?: string;
    status: string;
    indicator_count?: number;
    error_message?: string;
  }>;
  feeds: Array<{
    id: string;
    feed_name: string;
    provider_type: string;
    is_active: boolean;
    last_synced_at?: string;
    status: string;
    indicator_count?: number;
    error_message?: string;
  }>;
  cache_stats: {
    is_warmed: boolean;
    cached_indicators: number;
    cached_cidr_subnets: number;
    last_warmed_at?: string;
    total_lookups: number;
    total_hits: number;
    hit_ratio: number;
  };
}

export interface SOARDashboardData {
  pending_approvals_count: number;
  pending_approvals: Array<{
    id: string;
    incident_id: string;
    requested_action: string;
    target_entity: string;
    requested_by: string;
    requested_at: string;
    status: string;
    is_dry_run: boolean;
  }>;
  executing_actions_count: number;
  executing_actions: Array<{
    id: string;
    action_type: string;
    target_entity: string;
    status: string;
    created_at: string;
    incident_id?: string;
  }>;
  successful_actions_count: number;
  failed_actions_count: number;
  rolled_back_actions_count: number;
  average_response_latency_ms: number;
  status_distribution: Record<string, number>;
  policy_decisions: Record<string, number>;
}

export interface InvestigationsDashboardData {
  total_investigations: number;
  open_investigations: number;
  status_breakdown: Record<string, number>;
  priority_breakdown: Record<string, number>;
  analyst_workload: Record<string, number>;
  recent_cases: Array<{
    id: string;
    case_number: string;
    title: string;
    status: string;
    priority: string;
    lead_analyst: string;
    created_at: string;
    incident_id?: string;
  }>;
}

export interface MitreDashboardData {
  total_catalog_techniques: number;
  covered_techniques_count: number;
  coverage_percentage: number;
  covered_techniques: Array<{
    technique_id: string;
    name: string;
    tactic: string;
    mapped_rules_count: number;
    mapped_rules: string[];
    incident_observation_count: number;
  }>;
  uncovered_techniques_count: number;
  uncovered_techniques: Array<{
    technique_id: string;
    name: string;
    tactic: string;
  }>;
  highest_frequency_detected: Array<{
    technique_id: string;
    name: string;
    tactic: string;
    mapped_rules_count: number;
    incident_observation_count: number;
  }>;
}

export interface SystemHealthData {
  overall_status: string;
  uptime_seconds: number;
  operating_mode: string;
  environment: string;
  version: string;
  components: {
    api: { status: string; uptime_seconds: number; version: string };
    postgresql: { status: string; latency_ms: number; connected: boolean };
    redis: { status: string; connected: boolean };
    ml_inference: { status: string; model_loaded: boolean; preprocessor_loaded: boolean };
    workers: { detection_worker: string; response_worker: string; threat_feed_worker: string };
    websockets: { status: string; active_connections: number };
    ingress: { status: string };
    kubernetes: { status: string; pss_profile: string };
  };
  generated_at: string;
}

export interface SOCEventItem {
  event_id: string;
  sequence: number;
  type: string;
  severity: string;
  title: string;
  description: string;
  timestamp: string;
  epoch_ms: number;
  metadata?: Record<string, any>;
}

export const dashboardService = {
  getOverview: async (lookbackDays: number = 30): Promise<SOCOverviewMetrics> => {
    const res = await api.get<SOCOverviewMetrics>('/dashboard/overview', { params: { lookback_days: lookbackDays } });
    return res.data;
  },

  getIncidents: async (params: {
    page?: number;
    limit?: number;
    severity?: string;
    status?: string;
    attack_type?: string;
    search?: string;
    sort_by?: string;
    sort_order?: string;
    lookback_hours?: number;
  }): Promise<DashboardIncidentsResponse> => {
    const res = await api.get<DashboardIncidentsResponse>('/dashboard/incidents', { params });
    return res.data;
  },

  getDetections: async (lookbackDays: number = 30): Promise<DetectionsSummary> => {
    const res = await api.get<DetectionsSummary>('/dashboard/detections', { params: { lookback_days: lookbackDays } });
    return res.data;
  },

  getThreatIntel: async (): Promise<ThreatIntelDashboardData> => {
    const res = await api.get<ThreatIntelDashboardData>('/dashboard/threat-intel');
    return res.data;
  },

  getResponse: async (): Promise<SOARDashboardData> => {
    const res = await api.get<SOARDashboardData>('/dashboard/response');
    return res.data;
  },

  getInvestigations: async (): Promise<InvestigationsDashboardData> => {
    const res = await api.get<InvestigationsDashboardData>('/dashboard/investigations');
    return res.data;
  },

  getMitre: async (): Promise<MitreDashboardData> => {
    const res = await api.get<MitreDashboardData>('/dashboard/mitre');
    return res.data;
  },

  getSystemHealth: async (): Promise<SystemHealthData> => {
    const res = await api.get<SystemHealthData>('/dashboard/system-health');
    return res.data;
  },

  getEvents: async (params?: {
    limit?: number;
    type?: string;
    severity?: string;
    since?: string;
  }): Promise<SOCEventItem[]> => {
    const res = await api.get<SOCEventItem[]>('/dashboard/events', { params });
    return res.data;
  }
};
