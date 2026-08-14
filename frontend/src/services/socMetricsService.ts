/**
 * frontend/src/services/socMetricsService.ts
 * API Service for SOC Effectiveness Metrics and ATT&CK Coverage.
 */

import api from './api';

export interface SOCOverviewData {
  time_window_days: number;
  sample_incidents_count: number;
  sample_alerts_count: number;
  mttd_minutes: number;
  mttr_minutes: number;
  open_incidents: number;
  resolved_incidents: number;
  alert_to_incident_ratio: number;
  estimated_false_positive_rate_pct: number;
  generated_at: string;
}

export interface AttackCoverageData {
  id: string;
  observed_techniques_count: number;
  detected_techniques_count: number;
  total_matrix_techniques: number;
  coverage_percentage: number;
  tactic_breakdown: Record<string, {
    total_techniques: number;
    detected_count: number;
    coverage_pct: number;
    is_active_observation: boolean;
  }>;
  technique_details: {
    detected_techniques: string[];
    catalog: Record<string, string[]>;
  };
  created_at: string;
}

export const socMetricsService = {
  getOverview: async (lookbackDays: number = 30): Promise<SOCOverviewData> => {
    const res = await api.get(`/soc-metrics/overview?lookback_days=${lookbackDays}`);
    return res.data;
  },

  getWorkload: async (): Promise<any> => {
    const res = await api.get('/soc-metrics/workload');
    return res.data;
  },

  getAttackCoverage: async (): Promise<AttackCoverageData> => {
    const res = await api.get('/attack-coverage');
    return res.data;
  },

  recomputeCoverage: async (): Promise<any> => {
    const res = await api.post('/attack-coverage/snapshot');
    return res.data;
  }
};
