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

// ============================================================================
// RESEARCH MODULE - Treasury Explorer
// ============================================================================

export const treasuryResearchAPI = {
  // Get summary statistics for each term
  getTerms: () => api.get('/api/research/treasury/terms'),

  // Get list of auctions with filters
  getAuctions: (params = {}) => api.get('/api/research/treasury/auctions', { params }),

  // Get detailed auction info
  getAuctionDetail: (auctionId) => api.get(`/api/research/treasury/auctions/${auctionId}`),

  // Get yield history for a term
  getYieldHistory: (securityTerm, years = 5) =>
    api.get(`/api/research/treasury/history/${encodeURIComponent(securityTerm)}`, {
      params: { years }
    }),

  // Get upcoming auctions
  getUpcoming: () => api.get('/api/research/treasury/upcoming'),

  // Compare yields across terms
  compareTerms: (terms, years = 5) =>
    api.get('/api/research/treasury/compare', {
      params: { terms, years }
    }),

  // Get snapshot of latest auctions
  getSnapshot: () => api.get('/api/research/treasury/snapshot'),
};

// ============================================================================
// RESEARCH MODULE - BLS CU (Consumer Price Index) Explorer
// ============================================================================

export const cuResearchAPI = {
  // Get available dimensions (areas and items)
  getDimensions: () => api.get('/api/research/bls/cu/dimensions'),

  // Get series list with filters
  getSeries: (params = {}) => api.get('/api/research/bls/cu/series', { params }),

  // Get time series data for a specific series
  getSeriesData: (seriesId, params = {}) =>
    api.get(`/api/research/bls/cu/series/${seriesId}/data`, { params }),

  // Get overview with headline and core CPI
  getOverview: (areaCode = '0000') =>
    api.get('/api/research/bls/cu/overview', { params: { area_code: areaCode } }),

  // Get overview timeline
  getOverviewTimeline: (areaCode = '0000', monthsBack = 12) =>
    api.get('/api/research/bls/cu/overview/timeline', {
      params: { area_code: areaCode, months_back: monthsBack }
    }),

  // Get category analysis
  getCategoryAnalysis: (areaCode = '0000') =>
    api.get('/api/research/bls/cu/categories', { params: { area_code: areaCode } }),

  // Get category timeline
  getCategoryTimeline: (areaCode = '0000', monthsBack = 12) =>
    api.get('/api/research/bls/cu/categories/timeline', {
      params: { area_code: areaCode, months_back: monthsBack }
    }),

  // Compare areas for a given item
  compareAreas: (itemCode = 'SA0') =>
    api.get('/api/research/bls/cu/areas/compare', { params: { item_code: itemCode } }),

  // Get area comparison timeline
  getAreaComparisonTimeline: (itemCode = 'SA0', monthsBack = 12) =>
    api.get('/api/research/bls/cu/areas/compare/timeline', {
      params: { item_code: itemCode, months_back: monthsBack }
    }),
};

// ============================================================================
// RESEARCH MODULE - BLS LN (Labor Force Statistics) Explorer
// ============================================================================

export const lnResearchAPI = {
  // Get available dimensions (age, sex, race, education, etc.)
  getDimensions: () => api.get('/api/research/bls/ln/dimensions'),

  // Get series list with filters
  getSeries: (params = {}) => api.get('/api/research/bls/ln/series', { params }),

  // Get time series data for a specific series
  getSeriesData: (seriesId, params = {}) =>
    api.get(`/api/research/bls/ln/series/${seriesId}/data`, { params }),

  // Get overview with headline unemployment, LFPR, and emp-pop ratio
  getOverview: () => api.get('/api/research/bls/ln/overview'),

  // Get overview timeline
  getOverviewTimeline: (monthsBack = 24) =>
    api.get('/api/research/bls/ln/overview/timeline', {
      params: { months_back: monthsBack }
    }),

  // Get demographic analysis (age, sex, race, education breakdowns)
  getDemographicAnalysis: () => api.get('/api/research/bls/ln/demographics'),

  // Get demographic timeline for a specific dimension
  getDemographicTimeline: (dimensionType, monthsBack = 24) =>
    api.get('/api/research/bls/ln/demographics/timeline', {
      params: { dimension_type: dimensionType, months_back: monthsBack }
    }),

  // Get occupation analysis
  getOccupationAnalysis: () => api.get('/api/research/bls/ln/occupations'),

  // Get occupation timeline
  getOccupationTimeline: (monthsBack = 24) =>
    api.get('/api/research/bls/ln/occupations/timeline', {
      params: { months_back: monthsBack }
    }),

  // Get industry analysis
  getIndustryAnalysis: () => api.get('/api/research/bls/ln/industries'),

  // Get industry timeline
  getIndustryTimeline: (monthsBack = 24) =>
    api.get('/api/research/bls/ln/industries/timeline', {
      params: { months_back: monthsBack }
    }),
};

// ============================================================================
// RESEARCH MODULE - BLS LA (Local Area Unemployment Statistics) Explorer
// ============================================================================

export const laResearchAPI = {
  // Get available dimensions (areas and measures)
  getDimensions: () => api.get('/api/research/bls/la/dimensions'),

  // Get series list with filters
  getSeries: (params = {}) => api.get('/api/research/bls/la/series', { params }),

  // Get time series data for a specific series
  getSeriesData: (seriesId, params = {}) =>
    api.get(`/api/research/bls/la/series/${seriesId}/data`, { params }),

  // Get overview with aggregated national unemployment
  getOverview: () => api.get('/api/research/bls/la/overview'),

  // Get overview timeline
  getOverviewTimeline: (monthsBack = 24) =>
    api.get('/api/research/bls/la/overview/timeline', {
      params: { months_back: monthsBack }
    }),

  // Get state analysis (all states, latest snapshot)
  getStates: () => api.get('/api/research/bls/la/states'),

  // Get state timeline
  getStatesTimeline: (monthsBack = 24, stateCodes = null) =>
    api.get('/api/research/bls/la/states/timeline', {
      params: {
        months_back: monthsBack,
        ...(stateCodes && { state_codes: stateCodes })
      }
    }),

  // Get metro analysis (metropolitan areas, latest snapshot)
  getMetros: (limit = 100) =>
    api.get('/api/research/bls/la/metros', { params: { limit } }),

  // Get metro timeline
  getMetrosTimeline: (monthsBack = 24, metroCodes = null, limit = 10) =>
    api.get('/api/research/bls/la/metros/timeline', {
      params: {
        months_back: monthsBack,
        limit,
        ...(metroCodes && { metro_codes: metroCodes })
      }
    }),
};

// ============================================================================
// RESEARCH MODULE - BLS CE (Current Employment Statistics) Explorer
// ============================================================================

export const ceResearchAPI = {
  // Get available dimensions (industries, supersectors, data types)
  getDimensions: () => api.get('/api/research/bls/ce/dimensions'),

  // Get series list with filters
  getSeries: (params = {}) => api.get('/api/research/bls/ce/series', { params }),

  // Get time series data for a specific series
  getSeriesData: (seriesId, params = {}) =>
    api.get(`/api/research/bls/ce/series/${seriesId}/data`, { params }),

  // Overview - headline employment stats
  getOverview: () => api.get('/api/research/bls/ce/overview'),

  // Overview timeline
  getOverviewTimeline: (monthsBack = 24) =>
    api.get('/api/research/bls/ce/overview/timeline', {
      params: { months_back: monthsBack }
    }),

  // Supersector analysis
  getSupersectors: () => api.get('/api/research/bls/ce/supersectors'),

  // Supersector timeline
  getSupersectorsTimeline: (params = {}) =>
    api.get('/api/research/bls/ce/supersectors/timeline', { params }),

  // Industry analysis
  getIndustries: (params = {}) =>
    api.get('/api/research/bls/ce/industries', { params }),

  // Industry timeline
  getIndustriesTimeline: (industryCodes, monthsBack = 24) =>
    api.get('/api/research/bls/ce/industries/timeline', {
      params: { industry_codes: industryCodes, months_back: monthsBack }
    }),

  // Data type analysis for a specific industry
  getDataTypes: (industryCode) =>
    api.get(`/api/research/bls/ce/datatypes/${industryCode}`),

  // Data type timeline for a specific industry
  getDataTypesTimeline: (industryCode, params = {}) =>
    api.get(`/api/research/bls/ce/datatypes/${industryCode}/timeline`, { params }),

  // Earnings analysis
  getEarnings: (params = {}) =>
    api.get('/api/research/bls/ce/earnings', { params }),

  // Earnings timeline for a specific industry
  getEarningsTimeline: (industryCode, monthsBack = 24) =>
    api.get(`/api/research/bls/ce/earnings/${industryCode}/timeline`, {
      params: { months_back: monthsBack }
    }),
};

// ============================================================================
// RESEARCH MODULE - BLS PC (Producer Price Index - Industry) Explorer
// ============================================================================

export const pcResearchAPI = {
  // Get available dimensions (industries and sectors)
  getDimensions: () => api.get('/api/research/bls/pc/dimensions'),

  // Get series list with filters
  getSeries: (params = {}) => api.get('/api/research/bls/pc/series', { params }),

  // Get time series data for a specific series
  getSeriesData: (seriesId, params = {}) =>
    api.get(`/api/research/bls/pc/series/${seriesId}/data`, { params }),

  // Overview - headline PPI stats (All Commodities, Finished Goods, etc.)
  getOverview: () => api.get('/api/research/bls/pc/overview'),

  // Overview timeline
  getOverviewTimeline: (monthsBack = 24) =>
    api.get('/api/research/bls/pc/overview/timeline', {
      params: { months_back: monthsBack }
    }),

  // Sector analysis (NAICS 2-digit sectors)
  getSectors: () => api.get('/api/research/bls/pc/sectors'),

  // Sector timeline
  getSectorsTimeline: (monthsBack = 24, sectorCodes = null) =>
    api.get('/api/research/bls/pc/sectors/timeline', {
      params: {
        months_back: monthsBack,
        ...(sectorCodes && { sector_codes: sectorCodes })
      }
    }),

  // Industry analysis (within a sector)
  getIndustries: (sectorCode = null, limit = 50) =>
    api.get('/api/research/bls/pc/industries', {
      params: { sector_code: sectorCode, limit }
    }),

  // Industry timeline
  getIndustriesTimeline: (industryCodes, monthsBack = 24) =>
    api.get('/api/research/bls/pc/industries/timeline', {
      params: { industry_codes: industryCodes, months_back: monthsBack }
    }),

  // Product analysis (within an industry)
  getProducts: (industryCode, limit = 50) =>
    api.get(`/api/research/bls/pc/products/${industryCode}`, {
      params: { limit }
    }),

  // Product timeline
  getProductsTimeline: (industryCode, productCodes = null, monthsBack = 24) =>
    api.get(`/api/research/bls/pc/products/${industryCode}/timeline`, {
      params: {
        months_back: monthsBack,
        ...(productCodes && { product_codes: productCodes })
      }
    }),

  // Top movers (gainers and losers)
  getTopMovers: (period = 'mom', limit = 10) =>
    api.get('/api/research/bls/pc/top-movers', {
      params: { period, limit }
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
