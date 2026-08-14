import api from './api';
import { AlertItem, AlertListResponse, AlertStatsResponse } from '../types';

export interface AlertFilterParams {
  page?: number;
  size?: number;
  severity?: string;
  status?: string;
  asset_id?: string;
  source_ip?: string;
  attack_type?: string;
}

export const alertService = {
  async listAlerts(params?: AlertFilterParams): Promise<AlertListResponse> {
    const response = await api.get<AlertListResponse>('/alerts', { params });
    return response.data;
  },

  async getAlert(id: string): Promise<AlertItem> {
    const response = await api.get<AlertItem>(`/alerts/${id}`);
    return response.data;
  },

  async getAlertStats(): Promise<AlertStatsResponse> {
    const response = await api.get<AlertStatsResponse>('/alerts/summary/stats');
    return response.data;
  },

  async updateStatus(id: string, status: string, notes?: string): Promise<AlertItem> {
    const response = await api.patch<AlertItem>(`/alerts/${id}/status`, { status, notes });
    return response.data;
  }
};
