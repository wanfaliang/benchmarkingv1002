// frontend/src/types/index.ts
// Shared type definitions for the Finexus application

// ============================================================================
// User & Authentication Types
// ============================================================================

export interface User {
  id: number;
  user_id?: string;  // Backend returns user_id as string
  email: string;
  username?: string;
  full_name?: string;
  is_active: boolean;
  email_verified: boolean;  // Backend uses email_verified
  auth_provider?: string;   // 'local' | 'google'
  avatar_url?: string;
  roles?: string[];
  created_at: string;
  updated_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginResult {
  success: boolean;
  error?: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

// ============================================================================
// Analysis Types
// ============================================================================

export interface Company {
  ticker: string;
  name?: string;
}

export interface Analysis {
  analysis_id: number;
  name: string;
  status: AnalysisStatus;
  phase?: 'A' | 'B';
  progress: number;
  companies?: Company[];
  years_back?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  updated_at?: string;
  user_id?: number;
}

export type AnalysisStatus =
  | 'created'
  | 'collecting'
  | 'collection_complete'
  | 'generating'
  | 'complete'
  | 'failed';

export interface AnalysisSection {
  section_number: number;
  section_name: string;
  status: SectionStatus;
  error_message?: string;
  processing_time?: number;
}

export type SectionStatus = 'complete' | 'processing' | 'pending' | 'failed';

export interface Section {
  section_num: number;
  title: string;
  content: string;
  analysis_id: number;
}

export interface CreateAnalysisPayload {
  companies: Company[];
  years_back: number;
  name?: string;
}

export interface TickerValidationResponse {
  valid: boolean;
  symbol: string;
  name: string;
  currency?: string;
  exchange?: string;
}

// ============================================================================
// Dataset Types
// ============================================================================

export interface DatasetCompany {
  ticker: string;
  name?: string;
}

export interface Dataset {
  id: string;           // UUID string
  dataset_id?: string;  // API sometimes returns dataset_id
  name: string;
  description?: string;
  tickers?: string[];
  companies?: DatasetCompany[];
  status: DatasetStatus;
  progress?: number;
  visibility: 'private' | 'shared' | 'public';
  data_size_mb?: number;
  row_count?: number;
  created_at: string;
  updated_at?: string;
  user_id: string;      // UUID string
}

export type DatasetStatus =
  | 'created'
  | 'collecting'
  | 'ready'
  | 'failed';

export interface DatasetProgress {
  status: DatasetStatus;
  progress: number;
  current_task?: string;
  error?: string;
}

export interface DatasetMetadata {
  id: number;
  name: string;
  tickers: string[];
  record_counts: Record<string, number>;
  date_ranges: Record<string, { min: string; max: string }>;
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface Dashboard {
  id: number;
  name: string;
  dataset_id: number;
  config: DashboardConfig;
  is_default: boolean;
  created_at: string;
  updated_at?: string;
}

export interface DashboardConfig {
  layout: LayoutItem[];
  widgets: Widget[];
}

export interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Widget {
  id: string;
  type: 'chart' | 'table' | 'metric' | 'text';
  title: string;
  config: Record<string, unknown>;
}

// ============================================================================
// Query Types
// ============================================================================

export interface SavedQuery {
  query_id: number;
  name: string;
  description?: string;
  data_source: string;
  query_config: QueryConfig;
  is_public: boolean;
  user_id?: number;
  usage_count?: number;
  last_used_at?: string;
  created_at?: string;
  updated_at?: string;
}

export interface QueryConfig {
  filters?: Array<{ field: string; operator: string; value: unknown }>;
  columns?: string[];
  sort_by?: string;
  sort_order?: string;
  companies?: string[];
  years?: number[];
  limit?: number;
  offset?: number;
}

// ============================================================================
// Research Module Types
// ============================================================================

// Treasury
export interface TreasuryTerm {
  security_term: string;
  auction_count: number;
  latest_yield: number;
  latest_date: string;
}

export interface TreasuryAuction {
  id: number;
  security_term: string;
  auction_date: string;
  issue_date: string;
  maturity_date: string;
  high_yield: number;
  bid_to_cover: number;
}

// BLS Common
export interface BLSSeriesData {
  series_id: string;
  date: string;
  value: number;
  period: string;
  year: number;
}

export interface BLSDimension {
  code: string;
  name: string;
  description?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: string[];
}

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: string | number;
}
