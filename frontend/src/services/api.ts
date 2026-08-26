import axios from 'axios';
import { authStorage } from '../utils/authStorage';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor to attach JWT Bearer Token, X-Tenant-ID & Request Correlation ID
api.interceptors.request.use(
  (config) => {
    const token = authStorage.getAccessToken();
    const activeTenantId = authStorage.getActiveTenantId();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    if (activeTenantId && !config.headers['X-Tenant-ID']) {
      config.headers['X-Tenant-ID'] = activeTenantId;
    }
    // Generate correlation X-Request-ID for client requests
    if (!config.headers['X-Request-ID']) {
      config.headers['X-Request-ID'] = `client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor for handling 401 Unauthorized globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      authStorage.clearAccessToken();
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);


export default api;
