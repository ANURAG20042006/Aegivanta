import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor to attach JWT Bearer Token & Request Correlation ID
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('aegivanta_token') || localStorage.getItem('sentinel_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
      localStorage.removeItem('aegivanta_token');
      localStorage.removeItem('sentinel_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
