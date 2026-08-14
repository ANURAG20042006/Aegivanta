import api from './api';
import { ProtectedAsset, AssetListResponse, AssetHealthSummary } from '../types';

export interface AssetFilterParams {
  page?: number;
  size?: number;
  asset_type?: string;
  environment?: string;
  criticality?: string;
  status?: string;
  search?: string;
}

export const assetService = {
  async listAssets(params?: AssetFilterParams): Promise<AssetListResponse> {
    const response = await api.get<AssetListResponse>('/assets', { params });
    return response.data;
  },

  async getAsset(id: string): Promise<ProtectedAsset> {
    const response = await api.get<ProtectedAsset>(`/assets/${id}`);
    return response.data;
  },

  async getAssetHealth(id: string): Promise<AssetHealthSummary> {
    const response = await api.get<AssetHealthSummary>(`/assets/${id}/health`);
    return response.data;
  },

  async getSummaryStats(): Promise<{
    total_assets: number;
    active_healthy: number;
    degraded: number;
    compromised: number;
    high_or_critical_risk_assets: number;
  }> {
    const response = await api.get('/assets/summary/stats');
    return response.data;
  },

  async createAsset(data: Partial<ProtectedAsset>): Promise<ProtectedAsset> {
    const response = await api.post<ProtectedAsset>('/assets', data);
    return response.data;
  },

  async updateAsset(id: string, data: Partial<ProtectedAsset>): Promise<ProtectedAsset> {
    const response = await api.put<ProtectedAsset>(`/assets/${id}`, data);
    return response.data;
  },

  async deleteAsset(id: string): Promise<void> {
    await api.delete(`/assets/${id}`);
  }
};
