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
}

export interface IncidentListResponse {
  total: number;
  page: number;
  size: number;
  incidents: IncidentItem[];
  items?: IncidentItem[];
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
  total_packets_inspected: number;
  total_threats_isolated: number;
  critical_threats_count: number;
  attack_distribution: AttackDistributionItem[];
  top_malicious_ips: Array<{ ip: string; count: number }>;
  model_leaderboard: ModelPerformanceItem[];
  recent_incidents: IncidentItem[];
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
