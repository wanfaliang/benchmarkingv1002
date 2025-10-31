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
  verifyGoogleToken: (idToken) => {
    return api.post('/api/auth/google/verify', { id_token: idToken });
  },
  // NEW: Email verification endpoints
  verifyEmail: (token) => api.get(`/api/auth/verify-email/${token}`),
  resendVerification: (email) => api.post('/api/auth/resend-verification', null, {
    params: { email }
  }),
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

// Dataset endpoints
export const datasetsAPI = {
  // CRUD Operations
  create: (payload) => api.post('/api/datasets', payload),
  list: (params = {}) => api.get('/api/datasets', { params }), // ?status=ready&visibility=private
  get: (id) => api.get(`/api/datasets/${id}`),
  update: (id, name) => api.patch(`/api/datasets/${id}`, { name }), // Update name/description
  updateConfig: (id, payload) => api.put(`/api/datasets/${id}`, payload), // Full config update (requires re-collection)
  delete: (id) => api.delete(`/api/datasets/${id}`),
  reset: (id) => api.post(`/api/datasets/${id}/reset`), // Reset to 'created' state

  // Data Collection
  startCollection: (id) => api.post(`/api/datasets/${id}/start-collection`),
  getProgress: (id) => api.get(`/api/datasets/${id}/progress`),
  downloadRawData: (id) => api.get(`/api/datasets/${id}/download/raw-data`, { responseType: 'blob' }),

  // Metadata
  getMetadata: (id) => api.get(`/api/datasets/${id}/metadata`),

  // Data Access - GET endpoints (16 data sources)
  getData: {
    financial: (id, params) => api.get(`/api/datasets/${id}/data/financial`, { params }),
    incomeStatement: (id, params) => api.get(`/api/datasets/${id}/data/is`, { params }),
    balanceSheet: (id, params) => api.get(`/api/datasets/${id}/data/bs`, { params }),
    cashFlow: (id, params) => api.get(`/api/datasets/${id}/data/cf`, { params }),
    ratios: (id, params) => api.get(`/api/datasets/${id}/data/ratio`, { params }),
    keyMetrics: (id, params) => api.get(`/api/datasets/${id}/data/km`, { params }),
    enterpriseValue: (id, params) => api.get(`/api/datasets/${id}/data/ev`, { params }),
    employeeHistory: (id, params) => api.get(`/api/datasets/${id}/data/eh`, { params }),
    profiles: (id, params) => api.get(`/api/datasets/${id}/data/profile`, { params }),
    pricesDaily: (id, params) => api.get(`/api/datasets/${id}/data/prices/daily`, { params }),
    pricesMonthly: (id, params) => api.get(`/api/datasets/${id}/data/prices/monthly`, { params }),
    sp500Daily: (id, params) => api.get(`/api/datasets/${id}/data/prices/sp500daily`, { params }),
    sp500Monthly: (id, params) => api.get(`/api/datasets/${id}/data/prices/sp500monthly`, { params }),
    institutional: (id, params) => api.get(`/api/datasets/${id}/data/institutional`, { params }),
    insider: (id, params) => api.get(`/api/datasets/${id}/data/insider`, { params }),
    insiderStats: (id, params) => api.get(`/api/datasets/${id}/data/insiderstat`, { params }),
    economic: (id, params) => api.get(`/api/datasets/${id}/data/economic`, { params }),
    analystEstimates: (id, params) => api.get(`/api/datasets/${id}/data/analyst`, { params }),
    analystTargets: (id, params) => api.get(`/api/datasets/${id}/data/target`, { params }),
    analystCoverage: (id, params) => api.get(`/api/datasets/${id}/data/analystcoverage`, { params }),
  },

  // Flexible Queries - POST endpoints
  query: (id, payload) => api.post(`/api/datasets/${id}/query`, payload),
  aggregate: (id, payload) => api.post(`/api/datasets/${id}/aggregate`, payload),
  pivot: (id, payload) => api.post(`/api/datasets/${id}/pivot`, payload),
  compare: (id, payload) => api.post(`/api/datasets/${id}/compare`, payload),

  // Sharing & Collaboration
  share: (id, payload) => api.post(`/api/datasets/${id}/share`, payload), // { email, permission }
  unshare: (id, userId) => api.delete(`/api/datasets/${id}/share/${userId}`),
  listShares: (id) => api.get(`/api/datasets/${id}/shares`),
  createPublicLink: (id) => api.post(`/api/datasets/${id}/share/public`),
  revokePublicLink: (id) => api.delete(`/api/datasets/${id}/share/public`),
  getPublicDataset: (shareToken) => api.get(`/api/datasets/public/${shareToken}`),

  // Export
  exportCSV: (id, payload) => api.post(`/api/datasets/${id}/export/csv`, payload, { responseType: 'blob' }),
  exportExcel: (id, payload) => api.post(`/api/datasets/${id}/export/excel`, payload, { responseType: 'blob' }),
  exportParquet: (id, payload) => api.post(`/api/datasets/${id}/export/parquet`, payload, { responseType: 'blob' }),
};

// ============================================================================
// DASHBOARDS (Custom Views)
// ============================================================================

export const dashboardsAPI = {
  create: (datasetId, payload) => api.post(`/api/datasets/${datasetId}/dashboards`, payload),
  list: (datasetId) => api.get(`/api/datasets/${datasetId}/dashboards`),
  get: (datasetId, dashboardId) => api.get(`/api/datasets/${datasetId}/dashboards/${dashboardId}`),
  update: (datasetId, dashboardId, payload) => api.put(`/api/datasets/${datasetId}/dashboards/${dashboardId}`, payload),
  delete: (datasetId, dashboardId) => api.delete(`/api/datasets/${datasetId}/dashboards/${dashboardId}`),
  setDefault: (datasetId, dashboardId) => api.post(`/api/datasets/${datasetId}/dashboards/${dashboardId}/set-default`),
};

// ============================================================================
// SAVED QUERIES
// ============================================================================

export const queriesAPI = {

  // Create new query
  // POST /api/datasets/queries
  create: (payload) => api.post('/api/datasets/queries', payload),
  
  // List queries (with optional filters)
  // GET /api/datasets/queries?data_source=financial&include_public=true
  list: (params = {}) => api.get('/api/datasets/queries/all', { params }),
  
  // Get single query by ID
  // GET /api/datasets/queries/{query_id}
  get: (queryId) => api.get(`/api/datasets/queries/${queryId}`),
  
  // Update query (name, description, config, is_public)
  // PUT /api/datasets/queries/{query_id}
  update: (queryId, payload) => api.put(`/api/datasets/queries/${queryId}`, payload),
  
  // Delete query
  // DELETE /api/datasets/queries/{query_id}
  delete: (queryId) => api.delete(`/api/datasets/queries/${queryId}`),
  
  // -------------------------------------------------------------------------
  // Execution
  // -------------------------------------------------------------------------
  
  // Execute saved query (applies saved filters and returns data)
  // POST /api/datasets/queries/{query_id}/execute
  execute: (queryId, datasetId) => api.post(`/api/datasets/queries/${queryId}/execute`, null, {
    params: { dataset_id: datasetId }
  }),
};

export const formatError = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};



export default api;
