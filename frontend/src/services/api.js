// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
// frontend/src/services/api.js - UPDATE the login function
export const authAPI = {
  register: (userData) => api.post('/api/auth/register', userData),
  login: (formData) => api.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  }),
  getCurrentUser: () => api.get('/api/auth/me'),
};

// Ticker validation
export const tickerAPI = {
  validate: (ticker) => api.post('/api/tickers/validate', { ticker }),
};

// Analysis endpoints
export const analysisAPI = {
  list: () => api.get('/api/analyses'),
  create: (data) => api.post('/api/analyses', data),
  get: (id) => api.get(`/api/analyses/${id}`),
  update: (id, data) => api.put(`/api/analyses/${id}`, data),
  updateName: (id, name) => api.patch(`/api/analyses/${id}`, { name }),
  delete: (id) => api.delete(`/api/analyses/${id}`),
  reset: (id) => api.post(`/api/analyses/${id}/reset`),
  restartAnalysis: (id) => api.post(`/api/analyses/${id}/restart-analysis`),
  
  // Phase A: Data Collection
  startCollection: (id) => api.post(`/api/analyses/${id}/start-collection`),
  
  // Phase B: Analysis Generation
  startAnalysis: (id) => api.post(`/api/analyses/${id}/start-analysis`),
  
  // Sections
  getSections: (id) => api.get(`/api/analyses/${id}/sections`),
  getSection: (id, sectionNum) => api.get(`/api/analyses/${id}/sections/${sectionNum}`),
  
  // Downloads
  downloadRawData: (id) => api.get(`/api/analyses/${id}/download/raw-data`, {
    responseType: 'blob',
  }),
};

export default api;
