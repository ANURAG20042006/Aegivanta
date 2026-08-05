import api from './api';
import { PacketFeatureVector, PredictionResult } from '../types';

export const predictService = {
  predictSingle: async (features: PacketFeatureVector | Record<string, number>, modelName?: string): Promise<PredictionResult> => {
    const payload = {
      features,
      model_name: modelName,
    };
    const response = await api.post<PredictionResult>('/predict/single', payload);
    return response.data;
  },

  predictCsv: async (file: File, modelName?: string): Promise<{ total_records: number; malicious_count: number; predictions: PredictionResult[] }> => {
    const formData = new FormData();
    formData.append('file', file);
    if (modelName) {
      formData.append('model_name', modelName);
    }
    const response = await api.post('/predict/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  remediateThreat: async (targetIp: string, action: string): Promise<{ status: string; message: string }> => {
    const response = await api.post('/predict/remediate', {
      target_ip: targetIp,
      action: action,
    });
    return response.data;
  },
};
