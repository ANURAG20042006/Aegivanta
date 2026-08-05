import api from './api';
import { PacketFeatureVector, PredictionResult, BatchPredictionResponse } from '../types';

export const predictService = {
  predictSingle: async (features: PacketFeatureVector, modelName: string = 'Random Forest'): Promise<PredictionResult> => {
    const response = await api.post<PredictionResult>('/predict/single', {
      features,
      model_name: modelName,
    });
    return response.data;
  },

  predictCSV: async (file: File, modelName: string = 'Random Forest'): Promise<BatchPredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_name', modelName);

    const response = await api.post<BatchPredictionResponse>('/predict/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
