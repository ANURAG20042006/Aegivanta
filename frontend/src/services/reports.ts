import api from './api';
import { ReportResponse } from '../types';
import { authStorage } from '../utils/authStorage';

export const reportService = {
  generateReport: async (format: 'pdf' | 'excel' | 'csv'): Promise<ReportResponse> => {
    const response = await api.post<ReportResponse>('/reports/generate', {
      format,
      include_shap_charts: true,
    });
    return response.data;
  },

  downloadFile: async (downloadUrl: string): Promise<void> => {
    // Use fetch here so the auth header is explicit and binary responses are never
    // coerced by Axios into a JSON error payload.
    const token = authStorage.getAccessToken();
    const response = await fetch(downloadUrl, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const body = await response.json();
        detail = body.detail || detail;
      } catch {
        // Keep the HTTP status when the server response is not JSON.
      }
      throw new Error(detail);
    }

    const blob = await response.blob();
    const contentDisposition = response.headers.get('content-disposition') || '';
    const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
    const fallbackName = decodeURIComponent(downloadUrl.split('/').pop() || 'aegivanta-report');
    const filename = filenameMatch?.[1] || fallbackName;
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = objectUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(objectUrl);
  },
};
