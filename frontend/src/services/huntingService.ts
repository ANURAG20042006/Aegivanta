/**
 * frontend/src/services/huntingService.ts
 * API Service for Threat Hunting searches and saved templates.
 */

import api from './api';

export interface HuntingFilter {
  source_ip?: string;
  destination_ip?: string;
  attack_type?: string;
  severity?: string;
  asset_id?: string;
  ioc_type?: string;
  keyword?: string;
}

export interface HuntingQueryPayload {
  entity: string; // 'alerts' | 'incidents' | 'iocs'
  time_range: string; // '1h' | '24h' | '7d' | '30d' | 'custom'
  start_time?: string;
  filters: HuntingFilter;
  limit?: number;
  offset?: number;
  query_id?: string;
}

export interface HuntingResultItem {
  id: string;
  entity: string;
  title?: string;
  incident_code?: string;
  source_ip?: string;
  destination_ip?: string;
  attack_type?: string;
  severity?: string;
  confidence?: number;
  risk_score?: number;
  status?: string;
  timestamp?: string;
  created_at?: string;
  value?: string;
  threat_type?: string;
  explanation?: any;
}

export interface HuntingResponse {
  execution_id: string;
  entity: string;
  result_count: number;
  query_duration_ms: number;
  timestamp: string;
  results: HuntingResultItem[];
}

export interface SavedQuery {
  id: string;
  name: string;
  description?: string;
  query_definition: any;
  created_by: string;
  created_at: string;
}

export const huntingService = {
  executeQuery: async (payload: HuntingQueryPayload): Promise<HuntingResponse> => {
    const res = await api.post('/hunting/query', payload);
    return res.data;
  },

  getSavedQueries: async (): Promise<SavedQuery[]> => {
    const res = await api.get('/hunting/saved');
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  saveQuery: async (name: string, description: string | undefined, query_definition: any): Promise<SavedQuery> => {
    const res = await api.post('/hunting/saved', { name, description, query_definition });
    return res.data;
  }
};
