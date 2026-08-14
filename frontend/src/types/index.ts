export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'analyst' | 'viewer';
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  user_id: string;
  username: string;
  role: 'admin' | 'analyst' | 'viewer';
}

export interface PacketFeatureVector {
  source_ip?: string;
  destination_ip?: string;
  source_port?: number;
  destination_port?: number;
  protocol?: string;
  flow_duration?: number;
  total_fwd_packets?: number;
  total_backward_packets?: number;
  packet_length_mean?: number;
  packet_length_std?: number;
  flow_bytes_s?: number;
  flow_packets_s?: number;
  syn_flag_count?: number;
  rst_flag_count?: number;
  psh_flag_count?: number;
  ack_flag_count?: number;
  urg_flag_count?: number;
  extra_features?: Record<string, number>;
}

export interface PredictionResult {
  incident_id?: string;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol: string;
  attack_type: string;
  confidence_score: number | null;
  is_malicious: boolean;
  severity: string;
  model_used?: string;
  timestamp: string | number;
  attack_probabilities?: Record<string, number>;
  shap_explanation?: Record<string, number>;
}

export interface PredictionRequest {
  features: Record<string, number>;
  model_name?: string;
}

export type PredictionResponse = PredictionResult;

export interface BatchPredictionResponse {
  total_packets_inspected: number;
  malicious_packets_count: number;
  benign_packets_count: number;
  threat_ratio_percentage: number;
  results: PredictionResult[];
}

export interface IncidentItem {
  id: string;
  incident_code?: string;
  alert_id?: string;
  asset_id?: string;
  title?: string;
  description?: string;
  status?: string;
  risk_score?: number;
  alert_count?: number;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol: string;
  attack_type: string;
  confidence_score: number | null;
  is_malicious: boolean;
  severity: string;
  model_name?: string;
  timestamp: string;
  first_seen?: string;
  last_seen?: string;
  notes?: string;
  resolution?: string;
}

export interface IncidentListResponse {
  total: number;
  page?: number;
  size?: number;
  limit?: number;
  offset?: number;
  incidents?: IncidentItem[];
  items?: IncidentItem[];
}

export interface ProtectedAsset {
  id: string;
  name: string;
  hostname: string;
  url?: string;
  ip_address?: string;
  asset_type: 'website' | 'api' | 'server' | 'database' | 'endpoint' | 'network' | 'other';
  environment: 'production' | 'staging' | 'development';
  criticality: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'degraded' | 'compromised' | 'maintenance' | 'inactive';
  description?: string;
  risk_score: number;
  tags?: Record<string, any>;
  last_seen: string;
  created_at: string;
  updated_at: string;
}

export interface AssetListResponse {
  total: number;
  page: number;
  size: number;
  items: ProtectedAsset[];
}

export interface AssetHealthSummary {
  asset_id: string;
  name: string;
  status: string;
  criticality: string;
  risk_score: number;
  risk_tier: string;
  active_incidents_count: number;
  total_alerts_count: number;
  last_seen: string;
}

export interface AlertItem {
  id: string;
  alert_id: string;
  asset_id?: string;
  incident_id?: string;
  title: string;
  description?: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  confidence: number | null;
  risk_score: number;
  source: string;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol: string;
  attack_type: string;
  status: 'new' | 'acknowledged' | 'investigating' | 'resolved' | 'dismissed';
  explanation?: Record<string, number>;
  timestamp: string;
  created_at?: string;
}

export interface AlertListResponse {
  total: number;
  page: number;
  size: number;
  items: AlertItem[];
}

export interface AlertStatsResponse {
  total_active_alerts: number;
  critical_alerts_count: number;
  high_alerts_count: number;
  new_alerts_count: number;
  alerts_last_hour: number;
  severity_breakdown: Record<string, number>;
}

export interface TimelineEvent {
  id: string;
  incident_id: string;
  timestamp: string;
  event_type: 'DETECTION' | 'ALERT_CORRELATED' | 'TRIAGE' | 'STATUS_CHANGE' | 'ANALYST_ACTION' | 'REMEDIATION' | 'RESOLUTION';
  title: string;
  description?: string;
  actor: string;
  metadata_payload?: Record<string, any>;
}

export interface IncidentDetail extends IncidentItem {
  asset?: ProtectedAsset;
  alerts: AlertItem[];
  timeline: TimelineEvent[];
}

export interface ModelPerformanceItem {
  id?: string;
  model_name: string;
  model_type: string;
  accuracy: number | null;
  f1_score: number | null;
  precision_score: number | null;
  recall_score: number | null;
  roc_auc: number | null;
  is_active: boolean;
  trained_at?: string;
}

export interface AnalyticsSummary {
  network_status?: string;
  total_packets_inspected: number;
  total_threats_detected?: number;
  total_threats_isolated?: number;
  critical_incidents_count?: number;
  critical_threats_count?: number;
  prediction_accuracy?: number;
  active_model?: string;
  attack_distribution: AttackDistributionItem[];
  top_source_ips?: Array<{ ip: string; count: number }>;
  top_malicious_ips?: Array<{ ip: string; count: number }>;
  model_performance?: ModelPerformanceItem[];
  model_leaderboard?: ModelPerformanceItem[];
  recent_incidents?: IncidentItem[];
}

export interface AttackDistributionItem {
  attack_type: string;
  count: number;
  percentage?: number;
}

export interface ReportResponse {
  download_url: string;
  format: string;
  generated_at: string;
}
