/**
 * frontend/src/services/predictiveService.ts
 * API Service for Predictive Security Analytics and Risk Forecasts.
 */

import api from './api';

export interface RiskForecastData {
  id: string;
  asset_id: string;
  forecast_type: string;
  forecast_horizon: string;
  predicted_score: number;
  confidence: number;
  baseline_score: number;
  model_family: string;
  model_version: string;
  explanation: any;
  created_at: string;
}

export interface VolumeForecastData {
  id: string;
  forecast_window: string;
  predicted_alert_count: number;
  confidence: number;
  model_family: string;
  model_version: string;
  historical_reference_count: number;
  created_at: string;
}

export const predictiveService = {
  getAssetForecast: async (assetId: string, forecastType: string = '24H'): Promise<RiskForecastData> => {
    const res = await api.get(`/predictive/assets/${assetId}?forecast_type=${forecastType}`);
    return res.data;
  },

  getVolumeForecast: async (): Promise<VolumeForecastData> => {
    const res = await api.get('/predictive/volume');
    return res.data;
  }
};
