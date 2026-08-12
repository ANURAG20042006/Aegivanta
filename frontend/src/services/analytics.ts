import api from './api';
import { AnalyticsSummary, ModelPerformanceItem } from '../types';

export const analyticsService = {
  getSummary: async (): Promise<AnalyticsSummary> => {
    const response = await api.get<AnalyticsSummary>('/analytics/summary');
    return response.data;
  },

  getModels: async (): Promise<ModelPerformanceItem[]> => {
    const response = await api.get<ModelPerformanceItem[]>('/train/models');
    return response.data;
  },

  triggerTraining: async () => {
    const response = await api.post('/train/trigger');
    return response.data;
  },

  getROCCurves: async (): Promise<any> => {
    const response = await api.get('/analytics/roc');
    return response.data;
  },
};
