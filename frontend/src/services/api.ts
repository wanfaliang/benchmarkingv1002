// frontend/src/services/api.ts
import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import type {
  AuthResponse,
  User,
  Analysis,
  AnalysisSection,
  Dataset,
  DatasetProgress,
  DatasetMetadata,
  Dashboard,
  SavedQuery,
  CreateAnalysisPayload,
  TickerValidationResponse,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add JWT token to requests
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
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

// ============================================================================
// Type definitions for API parameters
// ============================================================================

interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

interface DatasetCompanyPayload {
  ticker: string;
  name: string;
  currency?: string;
  exchange?: string;
}

interface DatasetCreatePayload {
  name: string;
  description?: string;
  tickers?: string[];
  companies?: DatasetCompanyPayload[];
  years_back?: number;
  include_analyst?: boolean;
  include_institutional?: boolean;
  visibility?: 'private' | 'public';
}

interface DatasetQueryParams {
  status?: string;
  visibility?: string;
}

interface SharePayload {
  email: string;
  permission: 'view' | 'edit';
}

interface ExportPayload {
  data_sources?: string[];
  tickers?: string[];
  date_range?: { start: string; end: string };
}

interface QueryPayload {
  data_source: string;
  filters?: Record<string, unknown>;
  columns?: string[];
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  limit?: number;
}

interface DashboardPayload {
  name: string;
  config: Record<string, unknown>;
}

interface SavedQueryPayload {
  name: string;
  description?: string;
  data_source: string;
  config: Record<string, unknown>;
  is_public?: boolean;
}

// ============================================================================
// Auth endpoints
// ============================================================================

export const authAPI = {
  register: (userData: RegisterData): Promise<AxiosResponse<User>> =>
    api.post('/api/auth/register', userData),

  login: (formData: URLSearchParams): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }),

  getCurrentUser: (): Promise<AxiosResponse<User>> =>
    api.get('/api/auth/me'),

  verifyGoogleToken: (idToken: string): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/api/auth/google/verify', { id_token: idToken }),

  verifyEmail: (token: string): Promise<AxiosResponse<{ message: string }>> =>
    api.get(`/api/auth/verify-email/${token}`),

  resendVerification: (email: string): Promise<AxiosResponse<{ message: string }>> =>
    api.post('/api/auth/resend-verification', null, {
      params: { email },
    }),
};

// ============================================================================
// Ticker validation
// ============================================================================

export const tickerAPI = {
  validate: (ticker: string): Promise<AxiosResponse<TickerValidationResponse>> =>
    api.post('/api/tickers/validate', { ticker }),
};

// ============================================================================
// Analysis endpoints
// ============================================================================

export const analysisAPI = {
  list: (): Promise<AxiosResponse<Analysis[]>> =>
    api.get('/api/analyses'),

  create: (data: CreateAnalysisPayload): Promise<AxiosResponse<Analysis>> =>
    api.post('/api/analyses', data),

  get: (id: number | string): Promise<AxiosResponse<Analysis>> =>
    api.get(`/api/analyses/${id}`),

  update: (id: number | string, data: Partial<Analysis>): Promise<AxiosResponse<Analysis>> =>
    api.put(`/api/analyses/${id}`, data),

  updateName: (id: number | string, name: string): Promise<AxiosResponse<Analysis>> =>
    api.patch(`/api/analyses/${id}`, { name }),

  delete: (id: number | string): Promise<AxiosResponse<void>> =>
    api.delete(`/api/analyses/${id}`),

  reset: (id: number | string): Promise<AxiosResponse<Analysis>> =>
    api.post(`/api/analyses/${id}/reset`),

  restartAnalysis: (id: number | string): Promise<AxiosResponse<Analysis>> =>
    api.post(`/api/analyses/${id}/restart-analysis`),

  // Phase A: Data Collection
  startCollection: (id: number | string): Promise<AxiosResponse<Analysis>> =>
    api.post(`/api/analyses/${id}/start-collection`),

  // Phase B: Analysis Generation
  startAnalysis: (id: number | string): Promise<AxiosResponse<Analysis>> =>
    api.post(`/api/analyses/${id}/start-analysis`),

  // Sections
  getSections: (id: number | string): Promise<AxiosResponse<{ sections: AnalysisSection[] }>> =>
    api.get(`/api/analyses/${id}/sections`),

  getSection: (id: number | string, sectionNum: number | string): Promise<AxiosResponse<string>> =>
    api.get(`/api/analyses/${id}/sections/${sectionNum}`),

  // Downloads
  downloadRawData: (id: number | string): Promise<AxiosResponse<Blob>> =>
    api.get(`/api/analyses/${id}/download/raw-data`, {
      responseType: 'blob',
    }),
};

// ============================================================================
// Dataset endpoints
// ============================================================================

export const datasetsAPI = {
  // CRUD Operations
  create: (payload: DatasetCreatePayload): Promise<AxiosResponse<Dataset>> =>
    api.post('/api/datasets', payload),

  list: (params: DatasetQueryParams = {}): Promise<AxiosResponse<Dataset[]>> =>
    api.get('/api/datasets', { params }),

  get: (id: string): Promise<AxiosResponse<Dataset>> =>
    api.get(`/api/datasets/${id}`),

  update: (id: string, name: string): Promise<AxiosResponse<Dataset>> =>
    api.patch(`/api/datasets/${id}`, { name }),

  updateConfig: (id: string, payload: DatasetCreatePayload): Promise<AxiosResponse<Dataset>> =>
    api.put(`/api/datasets/${id}`, payload),

  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete(`/api/datasets/${id}`),

  reset: (id: string): Promise<AxiosResponse<Dataset>> =>
    api.post(`/api/datasets/${id}/reset`),

  // Data Collection
  startCollection: (id: string): Promise<AxiosResponse<Dataset>> =>
    api.post(`/api/datasets/${id}/start-collection`),

  getProgress: (id: string): Promise<AxiosResponse<DatasetProgress>> =>
    api.get(`/api/datasets/${id}/progress`),

  downloadRawData: (id: string): Promise<AxiosResponse<Blob>> =>
    api.get(`/api/datasets/${id}/download/raw-data`, { responseType: 'blob' }),

  // Metadata
  getMetadata: (id: string): Promise<AxiosResponse<DatasetMetadata>> =>
    api.get(`/api/datasets/${id}/metadata`),

  // Data Access - GET endpoints (16 data sources)
  getData: {
    financial: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/financial`, { params }),
    incomeStatement: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/is`, { params }),
    balanceSheet: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/bs`, { params }),
    cashFlow: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/cf`, { params }),
    ratios: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/ratio`, { params }),
    keyMetrics: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/km`, { params }),
    enterpriseValue: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/ev`, { params }),
    employeeHistory: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/eh`, { params }),
    profiles: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/profile`, { params }),
    pricesDaily: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/prices/daily`, { params }),
    pricesMonthly: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/prices/monthly`, { params }),
    sp500Daily: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/prices/sp500daily`, { params }),
    sp500Monthly: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/prices/sp500monthly`, { params }),
    institutional: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/institutional`, { params }),
    insider: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/insider`, { params }),
    insiderStats: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/insiderstat`, { params }),
    economic: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/economic`, { params }),
    analystEstimates: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/analyst`, { params }),
    analystTargets: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/target`, { params }),
    analystCoverage: <T = unknown>(id: string, params?: Record<string, unknown>): Promise<AxiosResponse<T>> =>
      api.get(`/api/datasets/${id}/data/analystcoverage`, { params }),
  },

  // Flexible Queries - POST endpoints
  query: <T = unknown>(id: string, payload: QueryPayload): Promise<AxiosResponse<T>> =>
    api.post(`/api/datasets/${id}/query`, payload),

  aggregate: <T = unknown>(id: string, payload: Record<string, unknown>): Promise<AxiosResponse<T>> =>
    api.post(`/api/datasets/${id}/aggregate`, payload),

  pivot: <T = unknown>(id: string, payload: Record<string, unknown>): Promise<AxiosResponse<T>> =>
    api.post(`/api/datasets/${id}/pivot`, payload),

  compare: <T = unknown>(id: string, payload: Record<string, unknown>): Promise<AxiosResponse<T>> =>
    api.post(`/api/datasets/${id}/compare`, payload),

  // Sharing & Collaboration
  share: (id: string, payload: SharePayload): Promise<AxiosResponse<{ message: string }>> =>
    api.post(`/api/datasets/${id}/share`, payload),

  unshare: (id: string, userId: string): Promise<AxiosResponse<void>> =>
    api.delete(`/api/datasets/${id}/share/${userId}`),

  listShares: (id: string): Promise<AxiosResponse<Array<{ user_id: string; email: string; permission: string }>>> =>
    api.get(`/api/datasets/${id}/shares`),

  createPublicLink: (id: string): Promise<AxiosResponse<{ share_token: string }>> =>
    api.post(`/api/datasets/${id}/share/public`),

  revokePublicLink: (id: string): Promise<AxiosResponse<void>> =>
    api.delete(`/api/datasets/${id}/share/public`),

  getPublicDataset: (shareToken: string): Promise<AxiosResponse<Dataset>> =>
    api.get(`/api/datasets/public/${shareToken}`),

  // Export
  exportCSV: (id: string, payload: ExportPayload): Promise<AxiosResponse<Blob>> =>
    api.post(`/api/datasets/${id}/export/csv`, payload, { responseType: 'blob' }),

  exportExcel: (id: string, payload: ExportPayload): Promise<AxiosResponse<Blob>> =>
    api.post(`/api/datasets/${id}/export/excel`, payload, { responseType: 'blob' }),

  exportParquet: (id: string, payload: ExportPayload): Promise<AxiosResponse<Blob>> =>
    api.post(`/api/datasets/${id}/export/parquet`, payload, { responseType: 'blob' }),
};

// ============================================================================
// Dashboards (Custom Views)
// ============================================================================

export const dashboardsAPI = {
  create: (datasetId: number, payload: DashboardPayload): Promise<AxiosResponse<Dashboard>> =>
    api.post(`/api/datasets/${datasetId}/dashboards`, payload),

  list: (datasetId: number): Promise<AxiosResponse<Dashboard[]>> =>
    api.get(`/api/datasets/${datasetId}/dashboards`),

  get: (datasetId: number, dashboardId: number): Promise<AxiosResponse<Dashboard>> =>
    api.get(`/api/datasets/${datasetId}/dashboards/${dashboardId}`),

  update: (datasetId: number, dashboardId: number, payload: DashboardPayload): Promise<AxiosResponse<Dashboard>> =>
    api.put(`/api/datasets/${datasetId}/dashboards/${dashboardId}`, payload),

  delete: (datasetId: number, dashboardId: number): Promise<AxiosResponse<void>> =>
    api.delete(`/api/datasets/${datasetId}/dashboards/${dashboardId}`),

  setDefault: (datasetId: number, dashboardId: number): Promise<AxiosResponse<Dashboard>> =>
    api.post(`/api/datasets/${datasetId}/dashboards/${dashboardId}/set-default`),
};

// ============================================================================
// Saved Queries
// ============================================================================

export const queriesAPI = {
  create: (payload: SavedQueryPayload): Promise<AxiosResponse<SavedQuery>> =>
    api.post('/api/datasets/queries', payload),

  list: (params: { data_source?: string; include_public?: boolean } = {}): Promise<AxiosResponse<SavedQuery[]>> =>
    api.get('/api/datasets/queries/all', { params }),

  get: (queryId: number): Promise<AxiosResponse<SavedQuery>> =>
    api.get(`/api/datasets/queries/${queryId}`),

  update: (queryId: number, payload: Partial<SavedQueryPayload>): Promise<AxiosResponse<SavedQuery>> =>
    api.put(`/api/datasets/queries/${queryId}`, payload),

  delete: (queryId: number): Promise<AxiosResponse<void>> =>
    api.delete(`/api/datasets/queries/${queryId}`),

  execute: <T = unknown>(queryId: number, datasetId: string): Promise<AxiosResponse<T>> =>
    api.post(`/api/datasets/queries/${queryId}/execute`, null, {
      params: { dataset_id: datasetId },
    }),
};

// ============================================================================
// Research Module - Treasury Explorer
// ============================================================================

export const treasuryResearchAPI = {
  getTerms: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/treasury/terms'),

  getAuctions: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/treasury/auctions', { params }),

  getAuctionDetail: <T = unknown>(auctionId: number): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/treasury/auctions/${auctionId}`),

  getYieldHistory: <T = unknown>(securityTerm: string, years: number = 5): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/treasury/history/${encodeURIComponent(securityTerm)}`, {
      params: { years },
    }),

  getUpcoming: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/treasury/upcoming'),

  compareTerms: <T = unknown>(terms: string[], years: number = 5): Promise<AxiosResponse<T>> =>
    api.get('/api/research/treasury/compare', {
      params: { terms: terms.join(','), years },
    }),

  getSnapshot: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/treasury/snapshot'),
};

// ============================================================================
// Research Module - FRED Explorer (Treasury Yield Curve)
// ============================================================================

export const fredResearchAPI = {
  getYieldCurve: <T = unknown>(asOfDate?: string): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/yield-curve', { params: asOfDate ? { as_of_date: asOfDate } : {} }),

  getYieldHistory: <T = unknown>(tenor: string = '10Y', days: number = 365): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/yield-curve/history', { params: { tenor, days } }),

  getSpreadHistory: <T = unknown>(spread: string = '2s10s', days: number = 365): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/yield-curve/spread-history', { params: { spread, days } }),
};

// ============================================================================
// Research Module - FRED Claims Explorer (ICSA, CCSA)
// ============================================================================

export const claimsResearchAPI = {
  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/claims/overview'),

  getTimeline: <T = unknown>(weeksBack: number = 104): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/claims/overview/timeline', { params: { weeks_back: weeksBack } }),

  getSeries: <T = unknown>(seriesId: string, weeksBack: number = 104): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred/claims/series/${seriesId}`, { params: { weeks_back: weeksBack } }),

  compare: <T = unknown>(weeksBack: number = 52): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/claims/compare', { params: { weeks_back: weeksBack } }),

  // State-level claims data
  getStatesOverview: <T = unknown>(weeksBack: number = 52): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/claims/states/overview', { params: { weeks_back: weeksBack } }),

  getStateDetails: <T = unknown>(stateCode: string, weeksBack: number = 104): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred/claims/states/${stateCode}`, { params: { weeks_back: weeksBack } }),

  getStateRankings: <T = unknown>(metric: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred/claims/states/rankings/${metric}`),
};

// ============================================================================
// Research Module - FRED Fed Funds Rate Explorer
// ============================================================================

export const fedfundsResearchAPI = {
  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/overview'),

  getTimeline: <T = unknown>(yearsBack: number = 5): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/timeline', { params: { years_back: yearsBack } }),

  getChanges: <T = unknown>(yearsBack: number = 20): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/changes', { params: { years_back: yearsBack } }),

  getSeries: <T = unknown>(seriesId: string, daysBack: number = 365): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred/fedfunds/series/${seriesId}`, { params: { days_back: daysBack } }),

  compareEffective: <T = unknown>(daysBack: number = 365): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/compare-effective', { params: { days_back: daysBack } }),

  getHistoricalTable: <T = unknown>(yearsBack: number = 5, frequency: string = 'monthly'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/historical-table', { params: { years_back: yearsBack, frequency } }),

  getSiblingsSeries: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/sibling-series'),

  getAbout: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/about'),

  // OPTIMIZED: Combined endpoint - fetches timeline, comparison, and changes in ONE request
  getChartData: <T = unknown>(yearsBack: number = 5): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/fedfunds/chart-data', { params: { years_back: yearsBack } }),
};

// ============================================================================
// Research Module - FRED Consumer Sentiment Explorer
// ============================================================================

export const sentimentResearchAPI = {
  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/sentiment/overview'),

  getTimeline: <T = unknown>(monthsBack: number = 60): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/sentiment/timeline', { params: { months_back: monthsBack } }),

  comparePeriods: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/sentiment/compare-periods'),

  getSeries: <T = unknown>(seriesId: string, monthsBack: number = 60): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred/sentiment/series/${seriesId}`, { params: { months_back: monthsBack } }),

  getCorrelation: <T = unknown>(monthsBack: number = 120): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/sentiment/correlation', { params: { months_back: monthsBack } }),
};

// ============================================================================
// Research Module - FRED Leading Index & Recession Explorer
// ============================================================================

export const leadingResearchAPI = {
  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/leading/overview'),

  getTimeline: <T = unknown>(monthsBack: number = 120): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/leading/timeline', { params: { months_back: monthsBack } }),

  getRecessions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/leading/recessions'),

  getSignals: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/leading/signals'),

  getSeries: <T = unknown>(seriesId: string, monthsBack: number = 120): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred/leading/series/${seriesId}`, { params: { months_back: monthsBack } }),
};

// ============================================================================
// Research Module - FRED Housing Market Explorer
// ============================================================================

export const housingResearchAPI = {
  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/housing/overview'),

  getTimeline: <T = unknown>(monthsBack: number = 60): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/housing/timeline', { params: { months_back: monthsBack } }),

  getMortgageRates: <T = unknown>(monthsBack: number = 60): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/housing/mortgage-rates', { params: { months_back: monthsBack } }),

  getRegional: <T = unknown>(monthsBack: number = 60): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/housing/regional', { params: { months_back: monthsBack } }),

  compareStartsPermits: <T = unknown>(monthsBack: number = 120): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred/housing/compare-starts-permits', { params: { months_back: monthsBack } }),

  getSeries: <T = unknown>(seriesId: string, monthsBack: number = 60): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred/housing/series/${seriesId}`, { params: { months_back: monthsBack } }),
};

// ============================================================================
// Research Module - FRED Calendar (Release Schedule)
// ============================================================================

export const fredCalendarAPI = {
  getStats: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred-calendar/stats'),

  getUpcoming: <T = unknown>(days: number = 7): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred-calendar/upcoming', { params: { days } }),

  getMonth: <T = unknown>(year: number, month: number): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred-calendar/month/${year}/${month}`),

  getRange: <T = unknown>(start: string, end: string): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred-calendar/range', { params: { start, end } }),

  getToday: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred-calendar/today'),

  getWeek: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred-calendar/week'),

  getAllReleases: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/fred-calendar/releases'),

  getReleaseDates: <T = unknown>(releaseId: number, limit: number = 50): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred-calendar/release/${releaseId}/dates`, { params: { limit } }),

  getReleaseSeries: <T = unknown>(releaseId: number, params: { offset?: number; limit?: number; search?: string } = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred-calendar/release/${releaseId}/series`, { params }),

  getSeriesDetail: <T = unknown>(seriesId: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred-calendar/series/${seriesId}`),

  getSeriesObservations: <T = unknown>(seriesId: string, params: { start_date?: string; end_date?: string; limit?: number } = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/fred-calendar/series/${seriesId}/observations`, { params }),
};

// ============================================================================
// Research Module - Market Indices (S&P 500, Nasdaq, DJIA, Russell 2000)
// ============================================================================

export const marketResearchAPI = {
  getIndices: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/market/indices'),

  getIndexHistory: <T = unknown>(symbol: string, days: number = 30): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/market/indices/${symbol}/history`, { params: { days } }),
};

// ============================================================================
// Research Module - Economic Calendar
// ============================================================================

export const economicCalendarAPI = {
  getUpcoming: <T = unknown>(params: { days?: number; country?: string; impact?: string; limit?: number } = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/calendar/upcoming', { params }),

  getRecent: <T = unknown>(params: { days?: number; country?: string; impact?: string; limit?: number } = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/calendar/recent', { params }),

  getThisWeek: <T = unknown>(country?: string): Promise<AxiosResponse<T>> =>
    api.get('/api/research/calendar/week', { params: country ? { country } : {} }),
};

// ============================================================================
// Research Module - BLS CU (Consumer Price Index) Explorer
// ============================================================================

export const cuResearchAPI = {
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/dimensions'),

  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/series', { params }),

  getSeriesData: <T = unknown>(seriesId: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/cu/series/${seriesId}/data`, { params }),

  getOverview: <T = unknown>(areaCode: string = '0000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/overview', { params: { area_code: areaCode } }),

  getOverviewTimeline: <T = unknown>(areaCode: string = '0000', monthsBack: number = 12): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/overview/timeline', {
      params: { area_code: areaCode, months_back: monthsBack },
    }),

  getCategoryAnalysis: <T = unknown>(areaCode: string = '0000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/categories', { params: { area_code: areaCode } }),

  getCategoryTimeline: <T = unknown>(areaCode: string = '0000', monthsBack: number = 12): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/categories/timeline', {
      params: { area_code: areaCode, months_back: monthsBack },
    }),

  compareAreas: <T = unknown>(itemCode: string = 'SA0'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/areas/compare', { params: { item_code: itemCode } }),

  getAreaComparisonTimeline: <T = unknown>(itemCode: string = 'SA0', monthsBack: number = 12): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cu/areas/compare/timeline', {
      params: { item_code: itemCode, months_back: monthsBack },
    }),
};

// ============================================================================
// Research Module - BLS LN (Labor Force Statistics) Explorer
// ============================================================================

export const lnResearchAPI = {
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/dimensions'),

  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/series', { params }),

  getSeriesData: <T = unknown>(seriesId: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ln/series/${seriesId}/data`, { params }),

  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/overview'),

  getOverviewTimeline: <T = unknown>(monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/overview/timeline', {
      params: { months_back: monthsBack },
    }),

  getDemographicAnalysis: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/demographics'),

  getDemographicTimeline: <T = unknown>(dimensionType: string, monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/demographics/timeline', {
      params: { dimension_type: dimensionType, months_back: monthsBack },
    }),

  getOccupationAnalysis: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/occupations'),

  getOccupationTimeline: <T = unknown>(monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/occupations/timeline', {
      params: { months_back: monthsBack },
    }),

  getIndustryAnalysis: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/industries'),

  getIndustryTimeline: <T = unknown>(monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ln/industries/timeline', {
      params: { months_back: monthsBack },
    }),
};

// ============================================================================
// Research Module - BLS LA (Local Area Unemployment Statistics) Explorer
// ============================================================================

export const laResearchAPI = {
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/dimensions'),

  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/series', { params }),

  getSeriesData: <T = unknown>(seriesId: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/la/series/${seriesId}/data`, { params }),

  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/overview'),

  getOverviewTimeline: <T = unknown>(monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/overview/timeline', {
      params: { months_back: monthsBack },
    }),

  getStates: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/states'),

  getStatesTimeline: <T = unknown>(monthsBack: number = 24, stateCodes: string[] | null = null): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/states/timeline', {
      params: {
        months_back: monthsBack,
        ...(stateCodes && { state_codes: stateCodes.join(',') }),
      },
    }),

  getMetros: <T = unknown>(limit: number = 100): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/metros', { params: { limit } }),

  getMetrosTimeline: <T = unknown>(
    monthsBack: number = 24,
    metroCodes: string[] | null = null,
    limit: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/la/metros/timeline', {
      params: {
        months_back: monthsBack,
        limit,
        ...(metroCodes && { metro_codes: metroCodes.join(',') }),
      },
    }),
};

// ============================================================================
// Research Module - BLS CE (Current Employment Statistics) Explorer
// ============================================================================

export const ceResearchAPI = {
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/dimensions'),

  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/series', { params }),

  getSeriesData: <T = unknown>(seriesId: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ce/series/${seriesId}/data`, { params }),

  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/overview'),

  getOverviewTimeline: <T = unknown>(monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/overview/timeline', {
      params: { months_back: monthsBack },
    }),

  getSupersectors: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/supersectors'),

  getSupersectorsTimeline: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/supersectors/timeline', { params }),

  getIndustries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/industries', { params }),

  getIndustriesTimeline: <T = unknown>(industryCodes: string[], monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/industries/timeline', {
      params: { industry_codes: industryCodes.join(','), months_back: monthsBack },
    }),

  getDataTypes: <T = unknown>(industryCode: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ce/datatypes/${industryCode}`),

  getDataTypesTimeline: <T = unknown>(industryCode: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ce/datatypes/${industryCode}/timeline`, { params }),

  getEarnings: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ce/earnings', { params }),

  getEarningsTimeline: <T = unknown>(industryCode: string, monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ce/earnings/${industryCode}/timeline`, {
      params: { months_back: monthsBack },
    }),
};

// ============================================================================
// Research Module - BLS PC (Producer Price Index - Industry) Explorer
// ============================================================================

export const pcResearchAPI = {
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/dimensions'),

  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/series', { params }),

  getSeriesData: <T = unknown>(seriesId: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pc/series/${seriesId}/data`, { params }),

  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/overview'),

  getOverviewTimeline: <T = unknown>(monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/overview/timeline', {
      params: { months_back: monthsBack },
    }),

  getSectors: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/sectors'),

  getSectorsTimeline: <T = unknown>(monthsBack: number = 24, sectorCodes: string[] | null = null): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/sectors/timeline', {
      params: {
        months_back: monthsBack,
        ...(sectorCodes && { sector_codes: sectorCodes.join(',') }),
      },
    }),

  getIndustries: <T = unknown>(sectorCode: string | null = null, limit: number = 50): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/industries', {
      params: { sector_code: sectorCode, limit },
    }),

  getIndustriesTimeline: <T = unknown>(industryCodes: string[], monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/industries/timeline', {
      params: { industry_codes: industryCodes.join(','), months_back: monthsBack },
    }),

  getProducts: <T = unknown>(industryCode: string, limit: number = 50): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pc/products/${industryCode}`, {
      params: { limit },
    }),

  getProductsTimeline: <T = unknown>(
    industryCode: string,
    productCodes: string[] | null = null,
    monthsBack: number = 24
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pc/products/${industryCode}/timeline`, {
      params: {
        months_back: monthsBack,
        ...(productCodes && { product_codes: productCodes.join(',') }),
      },
    }),

  getTopMovers: <T = unknown>(period: string = 'mom', limit: number = 10): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pc/top-movers', {
      params: { period, limit },
    }),
};

// ============================================================================
// BLS WP Survey API (Producer Price Index - Commodities/Final Demand)
// Contains HEADLINE PPI numbers (Final Demand)
// ============================================================================

export const wpResearchAPI = {
  // Get available dimensions (groups, items, base years, etc.)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(seriesId: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/wp/series/${seriesId}/data`, { params }),

  // Final Demand Overview - HEADLINE PPI numbers
  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/overview'),

  // Overview timeline for charts
  getOverviewTimeline: <T = unknown>(monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/overview/timeline', {
      params: { months_back: monthsBack },
    }),

  // Intermediate Demand by production stages
  getIntermediateDemand: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/intermediate-demand'),

  // Group analysis (commodity groups or FD-ID groups)
  getGroupsAnalysis: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/groups/analysis', { params }),

  // Group timeline for comparison charts
  getGroupsTimeline: <T = unknown>(groupCodes: string[], monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/groups/timeline', {
      params: { group_codes: groupCodes.join(','), months_back: monthsBack },
    }),

  // Get items for a specific group
  getItems: <T = unknown>(groupCode: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/wp/groups/${groupCode}/items`),

  // Item analysis for a specific group
  getItemsAnalysis: <T = unknown>(groupCode: string, limit: number = 20): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/wp/groups/${groupCode}/analysis`, {
      params: { limit },
    }),

  // Top movers (biggest price changes)
  getTopMovers: <T = unknown>(period: string = 'mom', limit: number = 10, commodityOnly: boolean = true): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/wp/top-movers', {
      params: { period, limit, commodity_only: commodityOnly },
    }),
};

// ============================================================================
// BLS AP (Average Price) Research API
// ============================================================================

export const apResearchAPI = {
  // Get available dimensions (areas, items, categories)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ap/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ap/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(seriesId: string, months: number = 60): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ap/series/${seriesId}/data`, { params: { months } }),

  // Overview with featured prices and category summaries
  getOverview: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ap/overview'),

  // Compare prices across areas for an item
  compareAreas: <T = unknown>(itemCode: string): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ap/areas/compare', { params: { item_code: itemCode } }),

  // Get items analysis for a category
  getItemsAnalysis: <T = unknown>(category: string, limit: number = 50): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ap/items/analysis', { params: { category, limit } }),

  // Top movers (biggest price changes)
  getTopMovers: <T = unknown>(period: string = 'mom', category?: string, limit: number = 10): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ap/top-movers', {
      params: { period, category, limit },
    }),

  // Get price timeline for an item
  getItemTimeline: <T = unknown>(itemCode: string, areaCode: string = '0000', months: number = 60): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ap/items/${itemCode}/timeline`, {
      params: { area_code: areaCode, months },
    }),
};

// ============================================================================
// BLS CW (CPI for Urban Wage Earners) Research API
// ============================================================================

export const cwResearchAPI = {
  // Get available dimensions (areas, items)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(seriesId: string, months: number = 60): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/cw/series/${seriesId}/data`, { params: { months } }),

  // Overview with key inflation metrics
  getOverview: <T = unknown>(areaCode: string = '0000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/overview', { params: { area_code: areaCode } }),

  // Overview timeline (headline + core CPI)
  getOverviewTimeline: <T = unknown>(areaCode: string = '0000', monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/overview/timeline', {
      params: { area_code: areaCode, months_back: monthsBack },
    }),

  // Category analysis (8 major expenditure categories)
  getCategories: <T = unknown>(areaCode: string = '0000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/categories', { params: { area_code: areaCode } }),

  // Category timeline for charts
  getCategoryTimeline: <T = unknown>(areaCode: string = '0000', monthsBack: number = 24): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/categories/timeline', {
      params: { area_code: areaCode, months_back: monthsBack },
    }),

  // Compare areas for an item
  compareAreas: <T = unknown>(itemCode: string = 'SA0'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/areas/compare', { params: { item_code: itemCode } }),

  // Top movers (biggest CPI changes)
  getTopMovers: <T = unknown>(period: string = 'yoy', areaCode: string = '0000', limit: number = 10): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/cw/top-movers', {
      params: { period, area_code: areaCode, limit },
    }),
};

// ============================================================================
// BLS SM (State & Metro Employment) Research API
// ============================================================================

export const smResearchAPI = {
  // Get available dimensions (states, areas, supersectors, data types)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(seriesId: string, params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/sm/series/${seriesId}/data`, { params }),

  // Overview by supersector for a state/area
  getOverview: <T = unknown>(stateCode: string, areaCode: string = '00000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/overview', {
      params: { state_code: stateCode, area_code: areaCode },
    }),

  // Overview timeline for charts
  getOverviewTimeline: <T = unknown>(
    stateCode: string,
    areaCode: string = '00000',
    monthsBack: number = 24
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/overview/timeline', {
      params: { state_code: stateCode, area_code: areaCode, months_back: monthsBack },
    }),

  // State-level analysis (Total Nonfarm for all states)
  getStates: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/states'),

  // States timeline for comparison charts
  getStatesTimeline: <T = unknown>(monthsBack: number = 24, stateCodes: string | null = null): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/states/timeline', {
      params: {
        months_back: monthsBack,
        ...(stateCodes && { state_codes: stateCodes }),
      },
    }),

  // Metro-level analysis
  getMetros: <T = unknown>(stateCode: string | null = null, limit: number = 100): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/metros', {
      params: { state_code: stateCode, limit },
    }),

  // Metros timeline for comparison charts
  getMetrosTimeline: <T = unknown>(
    monthsBack: number = 24,
    areaCodes: string | null = null,
    limit: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/metros/timeline', {
      params: {
        months_back: monthsBack,
        limit,
        ...(areaCodes && { area_codes: areaCodes }),
      },
    }),

  // Supersector analysis for a state/area
  getSupersectors: <T = unknown>(stateCode: string, areaCode: string = '00000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/supersectors', {
      params: { state_code: stateCode, area_code: areaCode },
    }),

  // Supersectors timeline
  getSupersectorsTimeline: <T = unknown>(
    stateCode: string,
    areaCode: string,
    supersectorCodes: string,
    monthsBack: number = 24
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/supersectors/timeline', {
      params: { state_code: stateCode, area_code: areaCode, supersector_codes: supersectorCodes, months_back: monthsBack },
    }),

  // Industry analysis for a state/area
  getIndustries: <T = unknown>(
    stateCode: string,
    areaCode: string = '00000',
    supersectorCode: string | null = null,
    limit: number = 50
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/industries', {
      params: { state_code: stateCode, area_code: areaCode, supersector_code: supersectorCode, limit },
    }),

  // Industries timeline
  getIndustriesTimeline: <T = unknown>(
    stateCode: string,
    areaCode: string,
    industryCodes: string,
    monthsBack: number = 24
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/industries/timeline', {
      params: { state_code: stateCode, area_code: areaCode, industry_codes: industryCodes, months_back: monthsBack },
    }),

  // Top movers (biggest employment changes)
  getTopMovers: <T = unknown>(period: string = 'yoy', limit: number = 10): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/sm/top-movers', {
      params: { period, limit },
    }),
};

// ============================================================================
// BLS JT (JOLTS - Job Openings and Labor Turnover) Research API
// ============================================================================

export const jtResearchAPI = {
  // Get available dimensions (industries, states, data elements, size classes, rate/level)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(seriesId: string, months: number = 60): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/jt/series/${seriesId}/data`, { params: { months } }),

  // Overview with all JOLTS metrics (rates + levels)
  getOverview: <T = unknown>(industryCode: string = '000000', stateCode: string = '00'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/overview', {
      params: { industry_code: industryCode, state_code: stateCode },
    }),

  // Overview timeline for charts
  getOverviewTimeline: <T = unknown>(
    industryCode: string = '000000',
    stateCode: string = '00',
    months: number = 60
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/overview/timeline', {
      params: { industry_code: industryCode, state_code: stateCode, months },
    }),

  // Industry analysis (JOLTS metrics for all industries)
  getIndustries: <T = unknown>(stateCode: string = '00'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/industries', {
      params: { state_code: stateCode },
    }),

  // Industry timeline for comparison charts
  getIndustriesTimeline: <T = unknown>(
    dataelementCode: string = 'JO',
    ratelevelCode: string = 'R',
    stateCode: string = '00',
    months: number = 60,
    industryCodes: string | null = null
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/industries/timeline', {
      params: {
        dataelement_code: dataelementCode,
        ratelevel_code: ratelevelCode,
        state_code: stateCode,
        months,
        ...(industryCodes && { industry_codes: industryCodes }),
      },
    }),

  // Regional analysis (JOLTS metrics by state/region)
  getRegions: <T = unknown>(industryCode: string = '000000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/regions', {
      params: { industry_code: industryCode },
    }),

  // Region timeline for comparison charts
  getRegionsTimeline: <T = unknown>(
    dataelementCode: string = 'JO',
    ratelevelCode: string = 'R',
    industryCode: string = '000000',
    months: number = 60,
    stateCodes: string | null = null
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/regions/timeline', {
      params: {
        dataelement_code: dataelementCode,
        ratelevel_code: ratelevelCode,
        industry_code: industryCode,
        months,
        ...(stateCodes && { state_codes: stateCodes }),
      },
    }),

  // Size class analysis (JOLTS by establishment size)
  getSizeClasses: <T = unknown>(industryCode: string = '000000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/sizeclasses', {
      params: { industry_code: industryCode },
    }),

  // Size class timeline for comparison charts
  getSizeClassesTimeline: <T = unknown>(
    dataelementCode: string = 'JO',
    ratelevelCode: string = 'R',
    months: number = 60,
    sizeclassCodes: string | null = null
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/sizeclasses/timeline', {
      params: {
        dataelement_code: dataelementCode,
        ratelevel_code: ratelevelCode,
        months,
        ...(sizeclassCodes && { sizeclass_codes: sizeclassCodes }),
      },
    }),

  // Top movers (industries with largest JOLTS changes)
  getTopMovers: <T = unknown>(
    dataelementCode: string = 'JO',
    period: string = 'yoy',
    limit: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/jt/top-movers', {
      params: { dataelement_code: dataelementCode, period, limit },
    }),
};

// ============================================================================
// BLS OE (Occupational Employment and Wage Statistics) Research API
// ============================================================================

export const oeResearchAPI = {
  // Get available dimensions (area types, states, occupations, sectors, data types)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(seriesId: string, years: number = 10): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/oe/series/${seriesId}/data`, { params: { years } }),

  // Overview by major occupation groups
  getOverview: <T = unknown>(areaCode: string = '0000000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/overview', { params: { area_code: areaCode } }),

  // Overview timeline for charts
  getOverviewTimeline: <T = unknown>(
    areaCode: string = '0000000',
    datatype: string = 'employment',
    years: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/overview/timeline', {
      params: { area_code: areaCode, datatype, years },
    }),

  // Occupation analysis for an area/industry
  getOccupations: <T = unknown>(
    areaCode: string = '0000000',
    industryCode: string = '000000',
    majorGroup: string | null = null,
    limit: number = 100
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/occupations', {
      params: {
        area_code: areaCode,
        industry_code: industryCode,
        limit,
        ...(majorGroup && { major_group: majorGroup }),
      },
    }),

  // Occupation timeline for comparison charts
  getOccupationsTimeline: <T = unknown>(
    areaCode: string = '0000000',
    industryCode: string = '000000',
    datatype: string = 'employment',
    occupationCodes: string | null = null,
    years: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/occupations/timeline', {
      params: {
        area_code: areaCode,
        industry_code: industryCode,
        datatype,
        years,
        ...(occupationCodes && { occupation_codes: occupationCodes }),
      },
    }),

  // State comparison for an occupation
  getStates: <T = unknown>(occupationCode: string = '000000'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/states', { params: { occupation_code: occupationCode } }),

  // State timeline for comparison charts
  getStatesTimeline: <T = unknown>(
    occupationCode: string = '000000',
    datatype: string = 'annual_mean',
    stateCodes: string | null = null,
    years: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/states/timeline', {
      params: {
        occupation_code: occupationCode,
        datatype,
        years,
        ...(stateCodes && { state_codes: stateCodes }),
      },
    }),

  // Industry analysis for an occupation (national only)
  getIndustries: <T = unknown>(
    occupationCode: string = '000000',
    sectorCode: string | null = null,
    limit: number = 50
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/industries', {
      params: {
        occupation_code: occupationCode,
        limit,
        ...(sectorCode && { sector_code: sectorCode }),
      },
    }),

  // Industry timeline for comparison charts
  getIndustriesTimeline: <T = unknown>(
    occupationCode: string = '000000',
    datatype: string = 'annual_mean',
    industryCodes: string | null = null,
    years: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/industries/timeline', {
      params: {
        occupation_code: occupationCode,
        datatype,
        years,
        ...(industryCodes && { industry_codes: industryCodes }),
      },
    }),

  // Top rankings (highest paying, most employed, etc.)
  getTopRankings: <T = unknown>(
    areaCode: string = '0000000',
    rankingType: string = 'highest_paying',
    limit: number = 20
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/top-rankings', {
      params: { area_code: areaCode, ranking_type: rankingType, limit },
    }),

  // Top movers (year-over-year changes)
  getTopMovers: <T = unknown>(
    areaCode: string = '0000000',
    metric: string = 'annual_mean',
    limit: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/top-movers', {
      params: { area_code: areaCode, metric, limit },
    }),

  // Wage distribution for an occupation
  getWageDistribution: <T = unknown>(
    occupationCode: string,
    areaCode: string = '0000000'
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/wage-distribution', {
      params: { occupation_code: occupationCode, area_code: areaCode },
    }),

  // Complete occupation profile
  getOccupationProfile: <T = unknown>(
    occupationCode: string,
    areaCode: string = '0000000',
    industryCode: string = '000000'
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/oe/occupation-profile', {
      params: { occupation_code: occupationCode, area_code: areaCode, industry_code: industryCode },
    }),
};

// ============================================================================
// EC (Employment Cost Index) Research API - Legacy survey (1980-2005)
// ============================================================================

export const ecResearchAPI = {
  // Get available dimensions (compensations, groups, ownerships, periodicities)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(seriesId: string, startYear?: number, endYear?: number): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ec/series/${seriesId}/data`, {
      params: { ...(startYear && { start_year: startYear }), ...(endYear && { end_year: endYear }) },
    }),

  // Overview with headline ECI metrics
  getOverview: <T = unknown>(ownershipCode: string = '2'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/overview', { params: { ownership_code: ownershipCode } }),

  // Timeline for compensation indices
  getTimeline: <T = unknown>(
    ownershipCode: string = '2',
    periodicityCode: string = 'I',
    years: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/timeline', {
      params: { ownership_code: ownershipCode, periodicity_code: periodicityCode, years },
    }),

  // Worker group analysis
  getGroups: <T = unknown>(ownershipCode: string = '2', compCode: string = '1'): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/groups', {
      params: { ownership_code: ownershipCode, comp_code: compCode },
    }),

  // Worker group timeline
  getGroupsTimeline: <T = unknown>(
    ownershipCode: string = '2',
    compCode: string = '1',
    periodicityCode: string = 'I',
    groupCodes: string | null = null,
    years: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/groups/timeline', {
      params: {
        ownership_code: ownershipCode,
        comp_code: compCode,
        periodicity_code: periodicityCode,
        years,
        ...(groupCodes && { group_codes: groupCodes }),
      },
    }),

  // Ownership comparison
  getOwnershipComparison: <T = unknown>(
    compCode: string = '1',
    groupCode: string = '000'
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/ownership-comparison', {
      params: { comp_code: compCode, group_code: groupCode },
    }),

  // Ownership timeline
  getOwnershipTimeline: <T = unknown>(
    compCode: string = '1',
    periodicityCode: string = 'I',
    years: number = 10
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ec/ownership-comparison/timeline', {
      params: { comp_code: compCode, periodicity_code: periodicityCode, years },
    }),
};

// ============================================================================
// PR (Major Sector Productivity and Costs) Research API
// ============================================================================

export const prResearchAPI = {
  // Get available dimensions (sectors, classes, measures, durations)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(
    seriesId: string,
    years: number = 0,
    periodType: string = 'quarterly'
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pr/series/${seriesId}/data`, {
      params: { years, period_type: periodType },
    }),

  // Overview - all sectors with key metrics
  getOverview: <T = unknown>(
    classCode: string = '6',
    periodType: string = 'quarterly'
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/overview', {
      params: { class_code: classCode, period_type: periodType },
    }),

  // Overview timeline
  getOverviewTimeline: <T = unknown>(
    measure: string = 'labor_productivity',
    duration: string = 'index',
    classCode: string = '6',
    periodType: string = 'quarterly',
    years: number = 0
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/overview/timeline', {
      params: {
        measure,
        duration,
        class_code: classCode,
        period_type: periodType,
        years,
      },
    }),

  // Sector analysis
  getSectorAnalysis: <T = unknown>(
    sectorCode: string,
    classCode: string = '6',
    periodType: string = 'quarterly'
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pr/sectors/${sectorCode}`, {
      params: { class_code: classCode, period_type: periodType },
    }),

  // Sector timeline
  getSectorTimeline: <T = unknown>(
    sectorCode: string,
    duration: string = 'index',
    classCode: string = '6',
    periodType: string = 'quarterly',
    measureCodes: string | null = null,
    years: number = 0
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pr/sectors/${sectorCode}/timeline`, {
      params: {
        duration,
        class_code: classCode,
        period_type: periodType,
        years,
        ...(measureCodes && { measure_codes: measureCodes }),
      },
    }),

  // Measure comparison across sectors
  getMeasureComparison: <T = unknown>(
    measureCode: string,
    durationCode: string = '3',
    classCode: string = '6',
    periodType: string = 'quarterly'
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pr/measures/${measureCode}`, {
      params: { duration_code: durationCode, class_code: classCode, period_type: periodType },
    }),

  // Measure comparison timeline
  getMeasureComparisonTimeline: <T = unknown>(
    measureCode: string,
    durationCode: string = '3',
    classCode: string = '6',
    periodType: string = 'quarterly',
    sectorCodes: string | null = null,
    years: number = 0
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/pr/measures/${measureCode}/timeline`, {
      params: {
        duration_code: durationCode,
        class_code: classCode,
        period_type: periodType,
        years,
        ...(sectorCodes && { sector_codes: sectorCodes }),
      },
    }),

  // Class comparison (employees vs all workers)
  getClassComparison: <T = unknown>(
    sectorCode: string = '8500',
    measureCode: string = '01',
    periodType: string = 'quarterly'
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/classes/compare', {
      params: { sector_code: sectorCode, measure_code: measureCode, period_type: periodType },
    }),

  // Class comparison timeline
  getClassTimeline: <T = unknown>(
    sectorCode: string = '8500',
    measureCode: string = '01',
    durationCode: string = '3',
    periodType: string = 'quarterly',
    years: number = 0
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/classes/timeline', {
      params: {
        sector_code: sectorCode,
        measure_code: measureCode,
        duration_code: durationCode,
        period_type: periodType,
        years,
      },
    }),

  // Productivity vs costs analysis
  getProductivityVsCosts: <T = unknown>(
    classCode: string = '6',
    periodType: string = 'quarterly'
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/productivity-vs-costs', {
      params: { class_code: classCode, period_type: periodType },
    }),

  // Productivity vs costs timeline
  getProductivityVsCostsTimeline: <T = unknown>(
    sectorCode: string = '8500',
    duration: string = 'index',
    classCode: string = '6',
    periodType: string = 'quarterly',
    years: number = 0
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/productivity-vs-costs/timeline', {
      params: { sector_code: sectorCode, duration, class_code: classCode, period_type: periodType, years },
    }),

  // Manufacturing subsector comparison
  getManufacturing: <T = unknown>(
    classCode: string = '6',
    periodType: string = 'quarterly'
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/manufacturing', {
      params: { class_code: classCode, period_type: periodType },
    }),

  // Manufacturing timeline
  getManufacturingTimeline: <T = unknown>(
    measure: string = 'productivity',
    duration: string = 'index',
    classCode: string = '6',
    periodType: string = 'quarterly',
    years: number = 0
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/pr/manufacturing/timeline', {
      params: { measure, duration, class_code: classCode, period_type: periodType, years },
    }),
};

// ============================================================================
// TU (American Time Use Survey) Research API
// ============================================================================

export const tuResearchAPI = {
  // Get available dimensions
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/dimensions'),

  // Series Explorer - Method 1: Search
  searchSeries: <T = unknown>(
    search: string,
    stattypeCode?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/series/search', {
      params: {
        search,
        ...(stattypeCode && { stattype_code: stattypeCode }),
        limit,
        offset,
      },
    }),

  // Series Explorer - Method 2: Browse with filters
  browseSeries: <T = unknown>(params: {
    actcode_code?: string;
    stattype_code?: string;
    sex_code?: string;
    age_code?: string;
    race_code?: string;
    educ_code?: string;
    lfstat_code?: string;
    region_code?: string;
    limit?: number;
    offset?: number;
  }): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/series/browse', { params }),

  // Series Explorer - Method 3: Drill-down
  drilldownSeries: <T = unknown>(params: {
    actcode_code?: string;
    stattype_code?: string;
    sex_code?: string;
    age_code?: string;
  }): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/series/drilldown', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(
    seriesId: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/tu/series/${seriesId}/data`, {
      params: {
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Overview - major activities summary
  getOverview: <T = unknown>(year?: number): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/overview', {
      params: year ? { year } : {},
    }),

  // Overview timeline
  getOverviewTimeline: <T = unknown>(
    startYear?: number,
    endYear?: number,
    activities?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/overview/timeline', {
      params: {
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
        ...(activities && { activities }),
      },
    }),

  // Activity analysis
  getActivityAnalysis: <T = unknown>(
    actcodeCode: string,
    year?: number,
    includeSubactivities: boolean = true
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/tu/activity/${actcodeCode}`, {
      params: {
        ...(year && { year }),
        include_subactivities: includeSubactivities,
      },
    }),

  // Activity timeline
  getActivityTimeline: <T = unknown>(
    actcodeCode: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/tu/activity/${actcodeCode}/timeline`, {
      params: {
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Demographics - Sex comparison
  getSexComparison: <T = unknown>(
    actcodeCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/sex', {
      params: {
        actcode_code: actcodeCode,
        ...(year && { year }),
      },
    }),

  // Demographics - Sex timeline
  getSexTimeline: <T = unknown>(
    actcodeCode: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/sex/timeline', {
      params: {
        actcode_code: actcodeCode,
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Demographics - Sex comparison bulk (for multiple activities)
  getSexComparisonBulk: <T = unknown>(
    actcodeCodes: string[],
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/sex/bulk', {
      params: {
        actcode_codes: actcodeCodes.join(','),
        ...(year && { year }),
      },
    }),

  // Demographics - Age comparison
  getAgeComparison: <T = unknown>(
    actcodeCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/age', {
      params: {
        actcode_code: actcodeCode,
        ...(year && { year }),
      },
    }),

  // Demographics - Age timeline
  getAgeTimeline: <T = unknown>(
    actcodeCode: string,
    ageCodes: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/age/timeline', {
      params: {
        actcode_code: actcodeCode,
        age_codes: ageCodes,
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Demographics - Age comparison bulk (for multiple activities)
  getAgeComparisonBulk: <T = unknown>(
    actcodeCodes: string[],
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/age/bulk', {
      params: {
        actcode_codes: actcodeCodes.join(','),
        ...(year && { year }),
      },
    }),

  // Demographics - Labor force comparison
  getLaborForceComparison: <T = unknown>(
    actcodeCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/labor-force', {
      params: {
        actcode_code: actcodeCode,
        ...(year && { year }),
      },
    }),

  // Demographics - Labor force comparison bulk (for multiple activities)
  getLaborForceComparisonBulk: <T = unknown>(
    actcodeCodes: string[],
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/labor-force/bulk', {
      params: {
        actcode_codes: actcodeCodes.join(','),
        ...(year && { year }),
      },
    }),

  // Demographics - Labor force timeline
  getLaborForceTimeline: <T = unknown>(
    actcodeCode: string,
    lfstatCodes: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/labor-force/timeline', {
      params: {
        actcode_code: actcodeCode,
        lfstat_codes: lfstatCodes,
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Demographics - Education comparison
  getEducationComparison: <T = unknown>(
    actcodeCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/education', {
      params: {
        actcode_code: actcodeCode,
        ...(year && { year }),
      },
    }),

  // Demographics - Education timeline
  getEducationTimeline: <T = unknown>(
    actcodeCode: string,
    educCodes: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/education/timeline', {
      params: {
        actcode_code: actcodeCode,
        educ_codes: educCodes,
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Demographics - Race comparison
  getRaceComparison: <T = unknown>(
    actcodeCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/race', {
      params: {
        actcode_code: actcodeCode,
        ...(year && { year }),
      },
    }),

  // Demographics - Race timeline
  getRaceTimeline: <T = unknown>(
    actcodeCode: string,
    raceCodes: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/race/timeline', {
      params: {
        actcode_code: actcodeCode,
        race_codes: raceCodes,
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Demographics - Day type comparison
  getDayTypeComparison: <T = unknown>(
    actcodeCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/day-type', {
      params: {
        actcode_code: actcodeCode,
        ...(year && { year }),
      },
    }),

  // Demographics - Day type timeline
  getDayTypeTimeline: <T = unknown>(
    actcodeCode: string,
    pertypeCodes: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/demographics/day-type/timeline', {
      params: {
        actcode_code: actcodeCode,
        pertype_codes: pertypeCodes,
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Top activities
  getTopActivities: <T = unknown>(
    rankingType: string = 'most_time',
    limit: number = 10,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/top-activities', {
      params: {
        ranking_type: rankingType,
        limit,
        ...(year && { year }),
      },
    }),

  // Year-over-year changes
  getYoYChanges: <T = unknown>(
    stattype: string = 'avg_hours',
    limit: number = 5,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/yoy-changes', {
      params: {
        stattype,
        limit,
        ...(year && { year }),
      },
    }),

  // Region analysis
  getRegionComparison: <T = unknown>(
    actcodeCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/regions', {
      params: {
        actcode_code: actcodeCode,
        ...(year && { year }),
      },
    }),

  // Region timeline
  getRegionTimeline: <T = unknown>(
    actcodeCode: string,
    regionCodes: string,
    stattype: string = 'avg_hours',
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/tu/regions/timeline', {
      params: {
        actcode_code: actcodeCode,
        region_codes: regionCodes,
        stattype,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),
};

// ============================================================================
// IP (Industry Productivity) Research API
// ============================================================================

export const ipResearchAPI = {
  // Get available dimensions (sectors, industries, measures, durations, types, areas)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ip/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ip/series', { params }),

  // Get time series data for a specific series
  getSeriesData: <T = unknown>(
    seriesId: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ip/series/${seriesId}/data`, {
      params: {
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Overview - key metrics by sector
  getOverview: <T = unknown>(year?: number): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ip/overview', {
      params: year ? { year } : {},
    }),

  // Overview timeline
  getOverviewTimeline: <T = unknown>(
    measureCode: string = 'L00',
    durationCode: string = '0',
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ip/overview/timeline', {
      params: {
        measure_code: measureCode,
        duration_code: durationCode,
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Sector analysis - industries within a sector
  getSectorAnalysis: <T = unknown>(
    sectorCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ip/sectors/${sectorCode}`, {
      params: year ? { year } : {},
    }),

  // Sector timeline
  getSectorTimeline: <T = unknown>(
    sectorCode: string,
    measureCode: string = 'L00',
    durationCode: string = '0',
    industryCodes: string | null = null,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ip/sectors/${sectorCode}/timeline`, {
      params: {
        measure_code: measureCode,
        duration_code: durationCode,
        ...(industryCodes && { industry_codes: industryCodes }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Industry analysis - all measures for a specific industry
  getIndustryAnalysis: <T = unknown>(
    industryCode: string,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ip/industries/${industryCode}`, {
      params: year ? { year } : {},
    }),

  // Industry timeline
  getIndustryTimeline: <T = unknown>(
    industryCode: string,
    durationCode: string = '0',
    measureCodes: string | null = null,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ip/industries/${industryCode}/timeline`, {
      params: {
        duration_code: durationCode,
        ...(measureCodes && { measure_codes: measureCodes }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Measure comparison - compare a measure across industries
  getMeasureComparison: <T = unknown>(
    measureCode: string,
    durationCode: string = '0',
    sectorCode: string | null = null,
    year?: number,
    limit: number = 50
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ip/measures/${measureCode}`, {
      params: {
        duration_code: durationCode,
        limit,
        ...(sectorCode && { sector_code: sectorCode }),
        ...(year && { year }),
      },
    }),

  // Measure comparison timeline
  getMeasureComparisonTimeline: <T = unknown>(
    measureCode: string,
    durationCode: string = '0',
    industryCodes: string | null = null,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ip/measures/${measureCode}/timeline`, {
      params: {
        duration_code: durationCode,
        ...(industryCodes && { industry_codes: industryCodes }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Top rankings (highest/lowest industries by measure)
  getTopRankings: <T = unknown>(
    measureCode: string = 'L00',
    rankingType: string = 'highest',
    year?: number,
    limit: number = 20
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ip/top-rankings', {
      params: {
        measure_code: measureCode,
        ranking_type: rankingType,
        limit,
        ...(year && { year }),
      },
    }),

  // Productivity vs costs analysis
  getProductivityVsCosts: <T = unknown>(
    sectorCode: string | null = null,
    year?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ip/productivity-vs-costs', {
      params: {
        ...(sectorCode && { sector_code: sectorCode }),
        ...(year && { year }),
      },
    }),

  // Productivity vs costs timeline
  getProductivityVsCostsTimeline: <T = unknown>(
    industryCode: string,
    durationCode: string = '0',
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ip/productivity-vs-costs/timeline', {
      params: {
        industry_code: industryCode,
        duration_code: durationCode,
        ...(startYear && { start_year: startYear }),
      },
    }),
};

// ============================================================================
// SU (Chained CPI - All Urban Consumers) Research API
// ============================================================================

export const suResearchAPI = {
  // Get available dimensions (areas, items)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/series', { params }),

  // Get a specific series by ID
  getSeriesById: <T = unknown>(seriesId: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/su/series/${seriesId}`),

  // Get time series data for multiple series
  getData: <T = unknown>(
    seriesIds: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/data', {
      params: {
        series_ids: seriesIds,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Overview - key metrics for all categories
  getOverview: <T = unknown>(year?: number, period?: string): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/overview', {
      params: {
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Overview timeline
  getOverviewTimeline: <T = unknown>(
    itemCodes?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/overview/timeline', {
      params: {
        ...(itemCodes && { item_codes: itemCodes }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Category analysis - subcategories within a category
  getCategoryAnalysis: <T = unknown>(
    itemCode: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/su/category/${itemCode}`, {
      params: {
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Category timeline
  getCategoryTimeline: <T = unknown>(
    itemCode: string,
    startYear?: number,
    includeSubcategories: boolean = true
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/su/category/${itemCode}/timeline`, {
      params: {
        ...(startYear && { start_year: startYear }),
        include_subcategories: includeSubcategories,
      },
    }),

  // Comparison - multiple items at a point in time
  getComparison: <T = unknown>(
    itemCodes: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/comparison', {
      params: {
        item_codes: itemCodes,
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Comparison timeline
  getComparisonTimeline: <T = unknown>(
    itemCodes: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/comparison/timeline', {
      params: {
        item_codes: itemCodes,
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Top movers - biggest price gainers and losers
  getTopMovers: <T = unknown>(
    changeType: string = 'year_over_year',
    direction: string = 'highest',
    limit: number = 10,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/top-movers', {
      params: {
        change_type: changeType,
        direction,
        limit,
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Inflation analysis for a specific item
  getInflationAnalysis: <T = unknown>(
    itemCode: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/su/inflation/${itemCode}`, {
      params: {
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Year-over-year comparison timeline
  getYoYComparison: <T = unknown>(
    itemCodes?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/su/yoy-comparison', {
      params: {
        ...(itemCodes && { item_codes: itemCodes }),
        ...(startYear && { start_year: startYear }),
      },
    }),
};

// ============================================================================
// BD (Business Employment Dynamics) Research API
// ============================================================================

export const bdResearchAPI = {
  // Get available dimensions
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/series', { params }),

  // Get a specific series by ID
  getSeriesById: <T = unknown>(seriesId: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/bd/series/${seriesId}`),

  // Get time series data for multiple series
  getData: <T = unknown>(
    seriesIds: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/data', {
      params: {
        series_ids: seriesIds,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Overview - job flow metrics for state/industry
  getOverview: <T = unknown>(
    stateCode?: string,
    industryCode?: string,
    seasonalCode?: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/overview', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(industryCode && { industry_code: industryCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Overview timeline
  getOverviewTimeline: <T = unknown>(
    stateCode?: string,
    industryCode?: string,
    seasonalCode?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/overview/timeline', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(industryCode && { industry_code: industryCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // State comparison
  getStateComparison: <T = unknown>(
    industryCode?: string,
    seasonalCode?: string,
    dataelementCode?: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/states/comparison', {
      params: {
        ...(industryCode && { industry_code: industryCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(dataelementCode && { dataelement_code: dataelementCode }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // State timeline
  getStateTimeline: <T = unknown>(
    stateCodes: string,
    industryCode?: string,
    dataclassCode?: string,
    ratelevelCode?: string,
    seasonalCode?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/states/timeline', {
      params: {
        state_codes: stateCodes,
        ...(industryCode && { industry_code: industryCode }),
        ...(dataclassCode && { dataclass_code: dataclassCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Industry comparison
  getIndustryComparison: <T = unknown>(
    stateCode?: string,
    seasonalCode?: string,
    dataelementCode?: string,
    displayLevel?: number,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/industries/comparison', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(dataelementCode && { dataelement_code: dataelementCode }),
        ...(displayLevel !== undefined && { display_level: displayLevel }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Industry timeline
  getIndustryTimeline: <T = unknown>(
    industryCodes: string,
    stateCode?: string,
    dataclassCode?: string,
    ratelevelCode?: string,
    seasonalCode?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/industries/timeline', {
      params: {
        industry_codes: industryCodes,
        ...(stateCode && { state_code: stateCode }),
        ...(dataclassCode && { dataclass_code: dataclassCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Job flow component analysis
  getJobFlow: <T = unknown>(
    stateCode?: string,
    industryCode?: string,
    seasonalCode?: string,
    ratelevelCode?: string,
    dataelementCode?: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/job-flow', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(industryCode && { industry_code: industryCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(dataelementCode && { dataelement_code: dataelementCode }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Job flow timeline
  getJobFlowTimeline: <T = unknown>(
    stateCode?: string,
    industryCode?: string,
    seasonalCode?: string,
    ratelevelCode?: string,
    dataelementCode?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/job-flow/timeline', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(industryCode && { industry_code: industryCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(dataelementCode && { dataelement_code: dataelementCode }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Size class analysis
  getSizeClass: <T = unknown>(
    sizeclassType?: string,
    seasonalCode?: string,
    ratelevelCode?: string,
    dataelementCode?: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/size-class', {
      params: {
        ...(sizeclassType && { sizeclass_type: sizeclassType }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(dataelementCode && { dataelement_code: dataelementCode }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Size class timeline
  getSizeClassTimeline: <T = unknown>(
    sizeclassCodes: string,
    dataclassCode?: string,
    ratelevelCode?: string,
    seasonalCode?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/size-class/timeline', {
      params: {
        sizeclass_codes: sizeclassCodes,
        ...(dataclassCode && { dataclass_code: dataclassCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Establishment births and deaths
  getBirthsDeaths: <T = unknown>(
    stateCode?: string,
    industryCode?: string,
    seasonalCode?: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/births-deaths', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(industryCode && { industry_code: industryCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Births/deaths timeline
  getBirthsDeathsTimeline: <T = unknown>(
    stateCode?: string,
    industryCode?: string,
    seasonalCode?: string,
    ratelevelCode?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/births-deaths/timeline', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(industryCode && { industry_code: industryCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Top movers (states or industries)
  getTopMovers: <T = unknown>(
    comparisonType?: string,
    metric?: string,
    ratelevelCode?: string,
    dataelementCode?: string,
    seasonalCode?: string,
    limit?: number,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/top-movers', {
      params: {
        ...(comparisonType && { comparison_type: comparisonType }),
        ...(metric && { metric }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(dataelementCode && { dataelement_code: dataelementCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(limit && { limit }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Historical trend
  getTrend: <T = unknown>(
    stateCode?: string,
    industryCode?: string,
    dataclassCode?: string,
    ratelevelCode?: string,
    dataelementCode?: string,
    seasonalCode?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/bd/trend', {
      params: {
        ...(stateCode && { state_code: stateCode }),
        ...(industryCode && { industry_code: industryCode }),
        ...(dataclassCode && { dataclass_code: dataclassCode }),
        ...(ratelevelCode && { ratelevel_code: ratelevelCode }),
        ...(dataelementCode && { dataelement_code: dataelementCode }),
        ...(seasonalCode && { seasonal_code: seasonalCode }),
        ...(startYear && { start_year: startYear }),
      },
    }),
};

// ============================================================================
// BLS EI (Import/Export Price Indexes) Research API
// ============================================================================

export const eiResearchAPI = {
  // Get available dimensions (indexes, countries, years)
  getDimensions: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/dimensions'),

  // Get series list with filters
  getSeries: <T = unknown>(params: Record<string, unknown> = {}): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/series', { params }),

  // Get a specific series by ID
  getSeriesById: <T = unknown>(seriesId: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bls/ei/series/${seriesId}`),

  // Get time series data for multiple series
  getData: <T = unknown>(
    seriesIds: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/data', {
      params: {
        series_ids: seriesIds,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Overview - key import/export metrics
  getOverview: <T = unknown>(
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/overview', {
      params: {
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Overview timeline
  getOverviewTimeline: <T = unknown>(startYear?: number): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/overview/timeline', {
      params: {
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Country comparison (import by origin / export by destination)
  getCountryComparison: <T = unknown>(
    direction?: string,
    industry?: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/countries/comparison', {
      params: {
        ...(direction && { direction }),
        ...(industry && { industry }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Country timeline
  getCountryTimeline: <T = unknown>(
    countryCodes: string,
    direction?: string,
    industry?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/countries/timeline', {
      params: {
        country_codes: countryCodes,
        ...(direction && { direction }),
        ...(industry && { industry }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Trade flow data (imports/exports by country for visualization)
  getTradeFlow: <T = unknown>(
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/trade-flow', {
      params: {
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Trade balance (price differential by country)
  getTradeBalance: <T = unknown>(
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/trade-balance', {
      params: {
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Trade balance timeline for a country
  getTradeBalanceTimeline: <T = unknown>(
    country: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/trade-balance/timeline', {
      params: {
        country,
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Index categories by classification (BEA, NAICS, Harmonized)
  getCategories: <T = unknown>(
    direction?: string,
    classification?: string,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/categories', {
      params: {
        ...(direction && { direction }),
        ...(classification && { classification }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Category timeline
  getCategoryTimeline: <T = unknown>(
    seriesIds: string,
    direction?: string,
    classification?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/categories/timeline', {
      params: {
        series_ids: seriesIds,
        ...(direction && { direction }),
        ...(classification && { classification }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Services trade indexes
  getServices: <T = unknown>(
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/services', {
      params: {
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Terms of trade indexes
  getTermsOfTrade: <T = unknown>(
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/terms-of-trade', {
      params: {
        ...(year && { year }),
        ...(period && { period }),
      },
    }),

  // Terms of trade timeline
  getTermsOfTradeTimeline: <T = unknown>(
    seriesIds?: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/terms-of-trade/timeline', {
      params: {
        ...(seriesIds && { series_ids: seriesIds }),
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Historical trend for a series
  getTrend: <T = unknown>(
    seriesId: string,
    startYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/trend', {
      params: {
        series_id: seriesId,
        ...(startYear && { start_year: startYear }),
      },
    }),

  // Top movers by price change
  getTopMovers: <T = unknown>(
    direction?: string,
    metric?: string,
    limit?: number,
    year?: number,
    period?: string
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bls/ei/top-movers', {
      params: {
        ...(direction && { direction }),
        ...(metric && { metric }),
        ...(limit && { limit }),
        ...(year && { year }),
        ...(period && { period }),
      },
    }),
};

// ============================================================================
// BEA (Bureau of Economic Analysis) Research API
// ============================================================================

export const beaResearchAPI = {
  // NIPA endpoints
  getNIPATables: <T = unknown>(activeOnly?: boolean): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/nipa/tables', {
      params: { ...(activeOnly !== undefined && { active_only: activeOnly }) },
    }),

  getNIPATable: <T = unknown>(tableName: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bea/nipa/tables/${tableName}`),

  getNIPASeries: <T = unknown>(tableName: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bea/nipa/tables/${tableName}/series`),

  getNIPASeriesData: <T = unknown>(
    seriesCode: string,
    startYear?: number,
    endYear?: number,
    frequency?: string
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bea/nipa/series/${seriesCode}/data`, {
      params: {
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
        ...(frequency && { frequency }),
      },
    }),

  getNIPAHeadline: <T = unknown>(): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/nipa/headline'),

  // Regional endpoints
  getRegionalTables: <T = unknown>(activeOnly?: boolean): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/regional/tables', {
      params: { ...(activeOnly !== undefined && { active_only: activeOnly }) },
    }),

  getRegionalLineCodes: <T = unknown>(tableName: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bea/regional/tables/${tableName}/linecodes`),

  getRegionalGeographies: <T = unknown>(geoType?: string): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/regional/geographies', {
      params: { ...(geoType && { geo_type: geoType }) },
    }),

  getRegionalData: <T = unknown>(
    tableName: string,
    lineCode: number,
    geoFips: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/regional/data', {
      params: {
        table_name: tableName,
        line_code: lineCode,
        geo_fips: geoFips,
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // Batch endpoint - fetches all states in ONE query (50x more efficient)
  getRegionalDataBatch: <T = unknown>(
    tableName: string,
    lineCode: number,
    geoFipsList: string[],
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/regional/data/batch', {
      params: {
        table_name: tableName,
        line_code: lineCode,
        geo_fips_list: geoFipsList.join(','),
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  getRegionalSnapshot: <T = unknown>(
    tableName?: string,
    lineCode?: number,
    geoType?: string,
    year?: number,
    limit?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/regional/snapshot', {
      params: {
        ...(tableName && { table_name: tableName }),
        ...(lineCode && { line_code: lineCode }),
        ...(geoType && { geo_type: geoType }),
        ...(year && { year }),
        ...(limit && { limit }),
      },
    }),

  // GDP by Industry endpoints
  getGDPByIndustryTables: <T = unknown>(activeOnly?: boolean): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/gdpbyindustry/tables', {
      params: { ...(activeOnly !== undefined && { active_only: activeOnly }) },
    }),

  getGDPByIndustryIndustries: <T = unknown>(
    parentCode?: string,
    level?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/gdpbyindustry/industries', {
      params: {
        ...(parentCode && { parent_code: parentCode }),
        ...(level && { level }),
      },
    }),

  getGDPByIndustryData: <T = unknown>(
    tableId: number,
    industryCode: string,
    frequency?: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/gdpbyindustry/data', {
      params: {
        table_id: tableId,
        industry_code: industryCode,
        ...(frequency && { frequency }),
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  getGDPByIndustrySnapshot: <T = unknown>(
    tableId?: number,
    frequency?: string,
    year?: number,
    quarter?: string,
    limit?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/gdpbyindustry/snapshot', {
      params: {
        ...(tableId && { table_id: tableId }),
        ...(frequency && { frequency }),
        ...(year && { year }),
        ...(quarter && { quarter }),
        ...(limit && { limit }),
      },
    }),

  // ITA (International Trade and Investment) endpoints
  getITAIndicators: <T = unknown>(activeOnly?: boolean): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/ita/indicators', {
      params: { ...(activeOnly !== undefined && { active_only: activeOnly }) },
    }),

  getITAAreas: <T = unknown>(
    areaType?: string,
    activeOnly?: boolean
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/ita/areas', {
      params: {
        ...(areaType && { area_type: areaType }),
        ...(activeOnly !== undefined && { active_only: activeOnly }),
      },
    }),

  getITAData: <T = unknown>(
    indicatorCode: string,
    areaCode: string,
    frequency?: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/ita/data', {
      params: {
        indicator_code: indicatorCode,
        area_code: areaCode,
        ...(frequency && { frequency }),
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  getITAHeadline: <T = unknown>(year?: number): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/ita/headline', {
      params: { ...(year && { year }) },
    }),

  getITASnapshot: <T = unknown>(
    indicatorCode?: string,
    areaType?: string,
    year?: number,
    limit?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/ita/snapshot', {
      params: {
        ...(indicatorCode && { indicator_code: indicatorCode }),
        ...(areaType && { area_type: areaType }),
        ...(year && { year }),
        ...(limit && { limit }),
      },
    }),

  // Fixed Assets endpoints
  getFixedAssetsTables: <T = unknown>(activeOnly?: boolean): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/fixedassets/tables', {
      params: { ...(activeOnly !== undefined && { active_only: activeOnly }) },
    }),

  getFixedAssetsSeries: <T = unknown>(tableName: string): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bea/fixedassets/tables/${tableName}/series`),

  getFixedAssetsSeriesData: <T = unknown>(
    seriesCode: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get(`/api/research/bea/fixedassets/series/${seriesCode}/data`, {
      params: {
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  getFixedAssetsHeadline: <T = unknown>(year?: number): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/fixedassets/headline', {
      params: { ...(year && { year }) },
    }),

  getFixedAssetsSnapshot: <T = unknown>(
    tableName?: string,
    year?: number,
    limit?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/fixedassets/snapshot', {
      params: {
        ...(tableName && { table_name: tableName }),
        ...(year && { year }),
        ...(limit && { limit }),
      },
    }),

  // ========== BATCH ENDPOINTS FOR IMPROVED PERFORMANCE ==========

  // Fixed Assets batch - get multiple series in one call
  getFixedAssetsDataBatch: <T = unknown>(
    seriesCodes: string[],
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/fixedassets/data/batch', {
      params: {
        series_codes: seriesCodes.join(','),
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // NIPA batch - get multiple series in one call
  getNIPADataBatch: <T = unknown>(
    seriesCodes: string[],
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/nipa/data/batch', {
      params: {
        series_codes: seriesCodes.join(','),
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // GDP by Industry batch - get multiple industries in one call
  getGDPByIndustryDataBatch: <T = unknown>(
    tableId: number,
    industryCodes: string[],
    yearType?: string,
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/gdpbyindustry/data/batch', {
      params: {
        table_id: tableId,
        industry_codes: industryCodes.join(','),
        ...(yearType && { year_type: yearType }),
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),

  // ITA batch - get multiple areas in one call
  getITADataBatch: <T = unknown>(
    indicator: string,
    areaCodes: string[],
    startYear?: number,
    endYear?: number
  ): Promise<AxiosResponse<T>> =>
    api.get('/api/research/bea/ita/data/batch', {
      params: {
        indicator,
        area_codes: areaCodes.join(','),
        ...(startYear && { start_year: startYear }),
        ...(endYear && { end_year: endYear }),
      },
    }),
};

// ============================================================================
// Stocks Module - Stock Screener API
// ============================================================================

export interface ScreenFilter {
  feature: string;
  operator: string;  // "<", ">", "=", "!=", ">=", "<=", "in", "between", etc.
  value: number | string | number[] | string[];
}

export interface UniverseFilter {
  min_market_cap?: number;
  max_market_cap?: number;
  sectors?: string[];
  industries?: string[];
  exchanges?: string[];
  countries?: string[];
  exclude_etfs?: boolean;
  exclude_adrs?: boolean;
  min_price?: number;
  min_volume?: number;
}

export interface ScreenRequest {
  universe?: UniverseFilter;
  filters?: ScreenFilter[];
  columns?: string[];
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

export interface StockResult {
  symbol: string;
  company_name?: string;
  sector?: string;
  industry?: string;
  country?: string;
  price?: number;
  price_change?: number;
  price_change_pct?: number;
  market_cap?: number;
  volume?: number;
  avg_volume?: number;
  exchange?: string;
  beta?: number;
  pe_ratio_ttm?: number;
  pb_ratio?: number;
  ev_to_ebitda?: number;
  earnings_yield?: number;
  fcf_yield?: number;
  roe?: number;
  roic?: number;
  gross_margin?: number;
  net_profit_margin?: number;
  debt_to_equity?: number;
  current_ratio?: number;
  dividend_yield?: number;
  peg_ratio?: number;
  payout_ratio?: number;
  data?: Record<string, unknown>;
}

export interface ScreenResponse {
  total_count: number;
  returned_count: number;
  offset: number;
  limit: number;
  results: StockResult[];
  execution_time_ms: number;
}

// Computed features types
export interface Week52Stats {
  symbol: string;
  high_52w?: number;
  low_52w?: number;
  pct_from_high?: number;
  pct_from_low?: number;
}

export interface ReturnsData {
  symbol: string;
  return_1d?: number;
  return_1w?: number;
  return_1m?: number;
  return_3m?: number;
  return_6m?: number;
  return_ytd?: number;
  return_1y?: number;
}

export interface ComputedFeatures extends Week52Stats, Omit<ReturnsData, 'symbol'> {
  symbol: string;
}

export interface ComputedFeaturesBatchResponse {
  data: Record<string, ComputedFeatures>;
  symbols_requested: number;
  symbols_found: number;
}

export interface ScreenTemplate {
  template_key: string;
  name: string;
  description: string;
  category: string;
  filters: ScreenFilter[];
  universe?: UniverseFilter;
  default_columns: string[];
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

export interface TemplateCategory {
  category: string;
  count: number;
  templates: string[];
}

export interface SavedScreenSummary {
  screen_id: string;
  name: string;
  description?: string;
  filter_count: number;
  is_template: boolean;
  template_key?: string;
  last_run_at?: string;
  run_count: number;
  last_result_count?: number;
}

export interface SavedScreenResponse {
  screen_id: string;
  user_id: string;
  name: string;
  description?: string;
  filters: ScreenFilter[];
  universe?: UniverseFilter;
  columns?: string[];
  sort_by?: string;
  sort_order: string;
  is_template: boolean;
  template_key?: string;
  last_run_at?: string;
  run_count: number;
  last_result_count?: number;
  created_at: string;
  updated_at: string;
}

export interface SavedScreenCreate {
  name: string;
  description?: string;
  filters?: ScreenFilter[];
  universe?: UniverseFilter;
  columns?: string[];
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export const stocksAPI = {
  // Universe endpoints (public)
  getUniverseStats: (): Promise<AxiosResponse> =>
    api.get('/api/stocks/universe/stats'),

  getSectors: (): Promise<AxiosResponse<{ sectors: Array<{ name: string; count: number }> }>> =>
    api.get('/api/stocks/universe/sectors'),

  getIndustries: (sector?: string): Promise<AxiosResponse> =>
    api.get('/api/stocks/universe/industries', { params: sector ? { sector } : {} }),

  // Screen endpoint (requires auth)
  runScreen: (
    request: ScreenRequest,
    includeCount: boolean = false
  ): Promise<AxiosResponse<ScreenResponse>> =>
    api.post('/api/stocks/screen', request, {
      params: { include_count: includeCount },
    }),

  // Saved screens (requires auth)
  listSavedScreens: (): Promise<AxiosResponse<SavedScreenSummary[]>> =>
    api.get('/api/stocks/screens/'),

  createSavedScreen: (data: SavedScreenCreate): Promise<AxiosResponse<SavedScreenResponse>> =>
    api.post('/api/stocks/screens/', data),

  getSavedScreen: (screenId: string): Promise<AxiosResponse<SavedScreenResponse>> =>
    api.get(`/api/stocks/screens/${screenId}`),

  updateSavedScreen: (screenId: string, data: Partial<SavedScreenCreate>): Promise<AxiosResponse<SavedScreenResponse>> =>
    api.put(`/api/stocks/screens/${screenId}`, data),

  deleteSavedScreen: (screenId: string): Promise<AxiosResponse<void>> =>
    api.delete(`/api/stocks/screens/${screenId}`),

  duplicateSavedScreen: (screenId: string, newName?: string): Promise<AxiosResponse<SavedScreenResponse>> =>
    api.post(`/api/stocks/screens/${screenId}/duplicate`, null, {
      params: newName ? { new_name: newName } : {},
    }),

  logScreenRun: (
    screenId: string,
    resultCount: number,
    executionTimeMs?: number
  ): Promise<AxiosResponse<{ success: boolean; run_count: number }>> =>
    api.post(`/api/stocks/screens/${screenId}/log-run`, null, {
      params: {
        result_count: resultCount,
        ...(executionTimeMs && { execution_time_ms: executionTimeMs }),
      },
    }),

  runSavedScreen: (
    screenId: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<AxiosResponse<ScreenResponse>> =>
    api.post(`/api/stocks/screens/${screenId}/run`, null, {
      params: { limit, offset },
    }),

  // Templates (public)
  listTemplates: (category?: string): Promise<AxiosResponse<ScreenTemplate[]>> =>
    api.get('/api/stocks/templates/', { params: category ? { category } : {} }),

  getTemplateCategories: (): Promise<AxiosResponse<{
    total_templates: number;
    categories: TemplateCategory[];
  }>> =>
    api.get('/api/stocks/templates/categories'),

  getTemplate: (templateKey: string): Promise<AxiosResponse<ScreenTemplate>> =>
    api.get(`/api/stocks/templates/${templateKey}`),

  runTemplate: (
    templateKey: string,
    limit: number = 100,
    offset: number = 0,
    includeCount: boolean = false,
    sortBy?: string,
    sortOrder?: 'asc' | 'desc'
  ): Promise<AxiosResponse<ScreenResponse>> =>
    api.post(`/api/stocks/templates/${templateKey}/run`, null, {
      params: {
        limit,
        offset,
        include_count: includeCount,
        ...(sortBy && { sort_by: sortBy }),
        ...(sortOrder && { sort_order: sortOrder }),
      },
    }),

  // Computed features
  getComputedFeatures: (symbol: string): Promise<AxiosResponse<ComputedFeatures>> =>
    api.get(`/api/stocks/computed/${symbol}`),

  getComputedFeaturesBatch: (
    symbols: string[],
    include52w: boolean = true,
    includeReturns: boolean = true
  ): Promise<AxiosResponse<ComputedFeaturesBatchResponse>> =>
    api.post('/api/stocks/computed/batch', {
      symbols,
      include_52w: include52w,
      include_returns: includeReturns,
    }),

  get52WeekStats: (symbol: string): Promise<AxiosResponse<Week52Stats>> =>
    api.get(`/api/stocks/computed/${symbol}/52week`),

  getReturns: (symbol: string): Promise<AxiosResponse<ReturnsData>> =>
    api.get(`/api/stocks/computed/${symbol}/returns`),
};

// ============================================================================
// Error formatting utility
// ============================================================================

interface ApiErrorResponse {
  response?: {
    data?: {
      detail?: string;
      message?: string;
    };
  };
  message?: string;
}

export const formatError = (error: ApiErrorResponse): string => {
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
