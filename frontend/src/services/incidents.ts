import api from './api';
import { IncidentListResponse } from '../types';

export interface IncidentFilters {
  limit?: number;
  offset?: number;
  severity?: string;
  is_malicious?: boolean;
  attack_type?: string;
}

export const incidentsService = {
  list: async (filters: IncidentFilters = {}): Promise<IncidentListResponse> => {
    const response = await api.get<IncidentListResponse>('/incidents', { params: filters });
    return response.data;
  },
};
