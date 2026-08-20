/**
 * frontend/src/services/adaptiveMl.ts
 * ===================================
 * Phase 3.10 Adaptive ML Detection Intelligence & Model Governance API Client.
 */

import api from './api';

export interface AdaptiveDetectionScoreBreakdown {
  ml_score: number;
  rule_score: number;
  behavior_score: number;
  ioc_score: number;
  graph_score: number;
}

export interface AdaptiveDetectionResult {
  detection_id: string;
  timestamp: string;
  is_malicious: boolean;
  attack_type: string;
  severity: string;
  risk_score: number;
  final_confidence: number;
  latency_ms: number;
  scores: AdaptiveDetectionScoreBreakdown;
  weights_applied: {
    ml: number;
    rules: number;
    behavior: number;
    ioc: number;
    graph: number;
  };
  safety_guardrails: {
    requires_human_approval: boolean;
    is_opaque_ml_only: boolean;
    deterministic_rule_matched: boolean;
    ioc_matched: boolean;
    policy_mode: string;
  };
  telemetry_breakdown: {
    ml_ensemble: {
      ml_score: number;
      ensemble_prediction: string;
      ensemble_confidence: number;
      model_agreement_pct: number;
      individual_models: Record<string, { predicted_class: string; confidence: number; is_malicious: boolean }>;
      strategy: string;
    };
    deterministic_rules: {
      rule_score: number;
      matched_count: number;
      matches: Array<{ rule_id: string; rule_name: string; severity: string; attack_type: string; mitre_technique?: string }>;
      authoritative_rule?: string;
    };
    behavioral_baseline: {
      behavior_score: number;
      is_anomalous: boolean;
      anomalous_metrics: string[];
      max_z_score: number;
      explanation: string;
    };
    threat_intel: {
      ioc_score: number;
      has_ioc_match: boolean;
      matched_count: number;
      matched_iocs: Array<{ value: string; type: string; feed: string; severity: string; threat_type: string }>;
    };
    attack_graph: {
      graph_score: number;
      is_lateral_movement: boolean;
      hop_count: number;
      is_crown_jewel: boolean;
      factors: string[];
    };
  };
}

export interface DriftStatusSummary {
  reference_version: string;
  baseline_hash: string | null;
  accumulated_samples: number;
  min_window_size: number;
  ready_for_evaluation: boolean;
  window_counter: number;
  thresholds: {
    psi_threshold: number;
    ks_alpha: number;
  };
}

export interface DriftEvaluationResult {
  window_id: string;
  timestamp: string;
  sample_count: number;
  status: string; // NORMAL, WARNING, DRIFT_DETECTED
  alert_status: string; // NO_DRIFT, WARNING, CRITICAL
  drift_types: string[];
  retraining_recommended: boolean;
  statistics: {
    max_feature_psi: number;
    affected_features_count: number;
    affected_features: string[];
    psi_scores: Record<string, number>;
    prediction_distribution_change?: Record<string, number>;
    performance_metrics?: Record<string, number>;
  };
}

export interface FeedbackStats {
  total_feedback_count: number;
  verdict_distribution: {
    TRUE_POSITIVE: number;
    FALSE_POSITIVE: number;
    BENIGN: number;
    UNKNOWN: number;
  };
  analyst_precision: number;
  analyst_measured_fpr: number;
  true_positive_rate: number;
  false_positive_rate: number;
  pending_retraining_samples: number;
}

export interface ModelRegistryItem {
  id: string;
  model_name: string;
  model_version: string;
  model_type: string;
  status: string;
  is_active: boolean;
  accuracy: number | null;
  f1_score: number | null;
  precision_score: number | null;
  recall_score: number | null;
  roc_auc: number | null;
  latency_ms: number | null;
  training_dataset: string;
  approval_status: string; // PENDING_REVIEW, APPROVED, REJECTED
  approved_by: string | null;
  approved_at: string | null;
  approval_notes: string | null;
  trained_at: string | null;
  promoted_at: string | null;
}

export const adaptiveMlService = {
  async detectAdaptiveFlow(features: Record<string, any>, context?: Record<string, any>): Promise<AdaptiveDetectionResult> {
    const response = await api.post('/ml/adaptive-detect', { features, context });
    return response.data;
  },

  async getDriftStatus(): Promise<DriftStatusSummary> {
    const response = await api.get('/ml/drift-status');
    return response.data;
  },

  async evaluateDrift(): Promise<DriftEvaluationResult> {
    const response = await api.post('/ml/evaluate-drift');
    return response.data;
  },

  async submitFeedback(payload: {
    predicted_attack_type: string;
    actual_verdict: string;
    predicted_confidence?: number;
    incident_id?: string;
    notes?: string;
    feature_snapshot?: Record<string, any>;
  }): Promise<any> {
    const response = await api.post('/ml/feedback', payload);
    return response.data;
  },

  async getFeedbackStats(): Promise<FeedbackStats> {
    const response = await api.get('/ml/feedback/stats');
    return response.data;
  },

  async listModelRegistry(status?: string): Promise<ModelRegistryItem[]> {
    const response = await api.get('/ml/registry', { params: status ? { status } : {} });
    return response.data;
  },

  async approveModel(modelId: string, notes?: string): Promise<any> {
    const response = await api.post(`/ml/registry/${modelId}/approve`, { notes });
    return response.data;
  },

  async rejectModel(modelId: string, reason: string): Promise<any> {
    const response = await api.post(`/ml/registry/${modelId}/reject`, { reason });
    return response.data;
  },

  async activateModel(modelId: string): Promise<any> {
    const response = await api.post(`/ml/registry/${modelId}/activate`);
    return response.data;
  },

  async rollbackModel(modelId: string, rollback_reason: string): Promise<any> {
    const response = await api.post(`/ml/registry/${modelId}/rollback`, { rollback_reason });
    return response.data;
  },
};
