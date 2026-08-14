import api from './api';
import { IncidentListResponse, IncidentDetail } from '../types';

export interface IncidentFilters {
  limit?: number;
  offset?: number;
  severity?: string;
  is_malicious?: boolean;
  attack_type?: string;
  status?: string;
  asset_id?: string;
}

export const incidentsService = {
  list: async (filters: IncidentFilters = {}): Promise<IncidentListResponse> => {
    const response = await api.get<IncidentListResponse>('/incidents', { params: filters });
    return response.data;
  },

  get: async (id: string): Promise<IncidentDetail> => {
    const response = await api.get<IncidentDetail>(`/incidents/${id}`);
    return response.data;
  },

  updateStatus: async (id: string, status: string, notes?: string): Promise<any> => {
    const response = await api.patch(`/incidents/${id}/status`, { status, notes });
    return response.data;
  },

  addTimelineEvent: async (id: string, payload: { event_type: string; title: string; description?: string }): Promise<any> => {
    const response = await api.post(`/incidents/${id}/timeline`, payload);
    return response.data;
  },

  remediate: async (id: string, action: string = 'BLOCK_IP', reason?: string): Promise<any> => {
    const response = await api.post(`/incidents/${id}/remediate`, { action, reason });
    return response.data;
  }
};

