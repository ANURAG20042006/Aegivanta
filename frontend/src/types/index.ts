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
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: string;
  flow_duration: number;
  total_fwd_packets: number;
  total_backward_packets: number;
  packet_length_mean: number;
  packet_length_std: number;
  flow_bytes_s: number;
  flow_packets_s: number;
  syn_flag_count: number;
  rst_flag_count: number;
  psh_flag_count: number;
  ack_flag_count: number;
  urg_flag_count: number;
  extra_features?: Record<string, number>;
}

export interface IncidentItem {
  id: string;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol?: string;
  attack_type: string;
  confidence_score: number;
  is_malicious: boolean;
  severity: string;
  model_name?: string;
  timestamp: string;
}

export interface IncidentListResponse {
  items: IncidentItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface PredictionResult {
  incident_id: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: string;
  attack_type: string;
  confidence_score: number;
  is_malicious: boolean;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  model_used: string;
  timestamp: string;
  attack_probabilities: Record<string, number>;
  shap_explanation?: Record<string, number>;
}

export interface BatchPredictionResponse {
  total_packets_inspected: number;
  malicious_packets_count: number;
  benign_packets_count: number;
  threat_ratio_percentage: number;
  results: PredictionResult[];
}

export interface AttackDistributionItem {
  attack_type: string;
  count: number;
  percentage: number;
}

export interface ModelPerformanceItem {
  model_name: string;
  model_type: string;
  accuracy: number;
  f1_score: number;
  precision_score: number;
  recall_score: number;
  roc_auc: number;
  is_active: boolean;
}

export interface AnalyticsSummary {
  network_status: 'SECURE' | 'WARNING' | 'CRITICAL';
  total_packets_inspected: number;
  total_threats_detected: number;
  critical_incidents_count: number;
  prediction_accuracy: number;
  active_model: string;
  attack_distribution: AttackDistributionItem[];
  model_performance: ModelPerformanceItem[];
  top_source_ips: Array<{ ip: string; count: number }>;
  recent_incidents: IncidentItem[];
}

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource: string;
  ip_address: string;
  status: string;
  timestamp: string;
  details?: Record<string, any>;
}

export interface ReportResponse {
  report_id: string;
  file_name: string;
  format: string;
  download_url: string;
  generated_at: string;
  total_records_exported: number;
}
