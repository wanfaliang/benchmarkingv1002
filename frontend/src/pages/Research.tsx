import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import {
  Landmark,
  Users,
  Globe,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  DollarSign,
  Briefcase,
  Factory,
  Truck,
  Building2,
  Target,
  Zap,
  BarChart3,
  PieChart,
} from 'lucide-react';
import {
  ceResearchAPI,
  lnResearchAPI,
  cuResearchAPI,
  laResearchAPI,
  wpResearchAPI,
  pcResearchAPI,
  jtResearchAPI,
} from '../services/api';
import { ChevronLeft } from 'lucide-react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getLAAreaCoordinates, US_BOUNDS } from '../utils/laAreaCoordinates';
import type { LatLngBoundsExpression } from 'leaflet';

// ============================================================================
// TYPE DEFINITIONS FOR API DATA
// ============================================================================

interface CEOverviewItem {
  latest_value?: number;
  month_over_month?: number;
  year_over_year?: number;
  latest_date?: string;
}

interface CEOverviewData {
  total_nonfarm?: CEOverviewItem;
  total_private?: CEOverviewItem;
  goods_producing?: CEOverviewItem;
  service_providing?: CEOverviewItem;
  government?: CEOverviewItem;
}

interface CETimelinePoint {
  year: number;
  period: string;
  period_name: string;
  total_nonfarm?: number;
}

interface LNOverviewData {
  headline_unemployment?: {
    latest_value?: number;
    month_over_month?: number;
    year_over_year?: number;
    latest_date?: string;
  };
  labor_force_participation?: {
    latest_value?: number;
    month_over_month?: number;
    year_over_year?: number;
    latest_date?: string;
  };
}

interface LNTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  headline_value?: number;  // Unemployment Rate
  lfpr_value?: number;      // Labor Force Participation Rate
  epop_value?: number;      // Employment-Population Ratio
}

interface SupersectorItem {
  supersector_code: string;
  supersector_name: string;
  latest_value?: number;
  month_over_month?: number;
}

interface EmploymentDataProps {
  ceOverview: CEOverviewData | null;
  ceTimeline: CETimelinePoint[];
  lnOverview: LNOverviewData | null;
  lnTimeline: LNTimelinePoint[];
  supersectors: SupersectorItem[];
  loading: boolean;
}

// ============================================================================
// CAROUSEL TYPE DEFINITIONS
// ============================================================================

interface CarouselSurveyConfig {
  id: string;
  name: string;
  fullName: string;
  description: string;
  color: string;
  bgGradient: string;
  icon: React.ComponentType<{ className?: string }>;
}

// CU (CPI) Overview types
interface CUOverviewData {
  headline_cpi?: {
    latest_value?: number;
    month_over_month?: number;
    year_over_year?: number;
    latest_date?: string;
  };
  core_cpi?: {
    latest_value?: number;
    month_over_month?: number;
    year_over_year?: number;
    latest_date?: string;
  };
}

interface CUTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  headline_value?: number;
  headline_yoy?: number;
  core_value?: number;
  core_yoy?: number;
}

// LA Overview types - using states data for map view
interface LAStateData {
  area_code: string;
  area_name: string;
  unemployment_rate?: number;
  labor_force?: number;
  month_over_month?: number;
  year_over_year?: number;
}

interface LAStatesData {
  states: LAStateData[];
  rankings?: {
    highest?: string[];
    lowest?: string[];
  };
}

// LAOverviewData and LATimelinePoint removed - using LAStatesData for map view instead

// WP (PPI) Overview types - matches actual API structure
interface WPHeadlinePPI {
  series_id: string;
  name: string;
  latest_date?: string;
  mom_pct?: number | null;
  yoy_pct?: number | null;
  index_value?: number | null;
}

interface WPOverviewData {
  headline?: WPHeadlinePPI;
  components?: WPHeadlinePPI[];
  last_updated?: string;
}

interface WPTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  final_demand_value?: number;
  final_demand_yoy?: number;
  goods_yoy?: number;
  services_yoy?: number;
}

// PC (PPI Industry) Overview types - matches actual API structure
interface PCOverviewSector {
  sector_code: string;
  sector_name: string;
  mom_pct?: number | null;
  yoy_pct?: number | null;
  index_value?: number | null;
  latest_date?: string;
}

interface PCOverviewData {
  sectors?: PCOverviewSector[];
}

// JT (JOLTS) Overview types - matches actual API structure
interface JTMetric {
  series_id?: string;
  dataelement_code?: string;
  dataelement_name?: string;
  ratelevel_code?: string;
  value?: number | null;
  latest_date?: string;
  month_over_month?: number | null;
  month_over_month_pct?: number | null;
  year_over_year?: number | null;
  year_over_year_pct?: number | null;
}

interface JTOverviewData {
  industry_code?: string;
  industry_name?: string;
  state_code?: string;
  state_name?: string;
  job_openings_rate?: JTMetric | null;
  hires_rate?: JTMetric | null;
  total_separations_rate?: JTMetric | null;
  quits_rate?: JTMetric | null;
  layoffs_rate?: JTMetric | null;
  job_openings_level?: JTMetric | null;
  hires_level?: JTMetric | null;
  total_separations_level?: JTMetric | null;
  quits_level?: JTMetric | null;
  layoffs_level?: JTMetric | null;
  unemployed_per_opening?: JTMetric | null;
  last_updated?: string;
}

interface JTTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  job_openings_rate?: number | null;
  hires_rate?: number | null;
  total_separations_rate?: number | null;
  quits_rate?: number | null;
  layoffs_rate?: number | null;
  job_openings_level?: number | null;
  hires_level?: number | null;
}

// Unified carousel data state
interface CarouselData {
  ln: { overview: LNOverviewData | null; timeline: LNTimelinePoint[] };
  ce: { overview: CEOverviewData | null; timeline: CETimelinePoint[]; supersectors: SupersectorItem[] };
  cu: { overview: CUOverviewData | null; timeline: CUTimelinePoint[] };
  la: { states: LAStatesData | null };
  wp: { overview: WPOverviewData | null; timeline: WPTimelinePoint[] };
  pc: { overview: PCOverviewData | null };
  jt: { overview: JTOverviewData | null; timeline: JTTimelinePoint[] };
  loading: boolean;
}

/**
 * Research Portal v4 - Data-Dense Visual Design
 *
 * Inspired by Yahoo Finance & WSJ Market pages:
 * - Inline sparklines in tables
 * - Heatmaps for sector/category views
 * - Compact metric cards with mini charts
 * - High information density
 * - Auto-generated context (no CMS needed)
 */

// ============================================================================
// SAMPLE DATA - Would come from API
// ============================================================================

const marketData = {
  indices: [
    { name: 'S&P 500', value: 6090.27, change: -0.54, data: [6050, 6080, 6070, 6095, 6085, 6090] },
    { name: 'Nasdaq', value: 19859.77, change: -0.66, data: [19700, 19800, 19750, 19900, 19850, 19860] },
    { name: 'DJIA', value: 44642.52, change: -0.20, data: [44500, 44600, 44550, 44700, 44650, 44642] },
    { name: 'Russell 2000', value: 2393.67, change: 0.42, data: [2370, 2380, 2375, 2390, 2385, 2394] },
  ],
  yields: [
    { maturity: '2Y', yield: 4.15, change: -0.03, weekAgo: 4.27 },
    { maturity: '5Y', yield: 4.05, change: -0.04, weekAgo: 4.20 },
    { maturity: '10Y', yield: 4.18, change: -0.05, weekAgo: 4.32 },
    { maturity: '30Y', yield: 4.36, change: -0.04, weekAgo: 4.46 },
  ],
  yieldCurve: [
    { term: '1M', yield: 4.62 },
    { term: '3M', yield: 4.55 },
    { term: '6M', yield: 4.42 },
    { term: '1Y', yield: 4.25 },
    { term: '2Y', yield: 4.15 },
    { term: '3Y', yield: 4.08 },
    { term: '5Y', yield: 4.05 },
    { term: '7Y', yield: 4.10 },
    { term: '10Y', yield: 4.18 },
    { term: '20Y', yield: 4.45 },
    { term: '30Y', yield: 4.36 },
  ],
};

const laborData = {
  headline: {
    payrolls: { value: 227, prior: 12, expected: 200, unit: 'K' },
    unemployment: { value: 4.2, prior: 4.1, expected: 4.1, unit: '%' },
    participation: { value: 62.5, prior: 62.6, unit: '%' },
    earnings: { value: 4.0, prior: 4.0, unit: '% YoY' },
  },
  payrollsTrend: [
    { month: 'Jun', value: 179 },
    { month: 'Jul', value: 144 },
    { month: 'Aug', value: 78 },
    { month: 'Sep', value: 255 },
    { month: 'Oct', value: 12 },
    { month: 'Nov', value: 227 },
  ],
  sectorJobs: [
    { sector: 'Healthcare', change: 54, color: '#10b981' },
    { sector: 'Leisure & Hospitality', change: 53, color: '#10b981' },
    { sector: 'Government', change: 33, color: '#10b981' },
    { sector: 'Prof. Services', change: 26, color: '#10b981' },
    { sector: 'Manufacturing', change: 22, color: '#10b981' },
    { sector: 'Retail', change: -28, color: '#ef4444' },
    { sector: 'Temp Help', change: -17, color: '#ef4444' },
  ],
  jolts: {
    openings: { value: 7.74, prior: 7.37, trend: [8.1, 7.9, 7.7, 7.4, 7.7, 7.74] },
    hires: { value: 5.3, prior: 5.4, trend: [5.6, 5.5, 5.4, 5.3, 5.4, 5.3] },
    quits: { value: 3.3, prior: 3.2, trend: [3.5, 3.4, 3.3, 3.2, 3.2, 3.3] },
    ratio: { value: 1.1, text: 'Openings per unemployed' },
  },
};

const inflationData = {
  cpi: {
    headline: { value: 2.6, prior: 2.4, trend: [3.0, 2.9, 2.5, 2.4, 2.6, 2.6] },
    core: { value: 3.3, prior: 3.3, trend: [3.4, 3.3, 3.2, 3.3, 3.3, 3.3] },
    shelter: { value: 4.9, prior: 5.0 },
    energy: { value: -4.9, prior: -6.8 },
    food: { value: 2.3, prior: 2.3 },
  },
  components: [
    { name: 'Shelter', weight: 36.2, yoy: 4.9, mom: 0.4, trend: 'down' },
    { name: 'Transportation', weight: 14.8, yoy: 8.2, mom: 0.1, trend: 'down' },
    { name: 'Food', weight: 13.5, yoy: 2.3, mom: 0.2, trend: 'flat' },
    { name: 'Medical', weight: 8.4, yoy: 3.0, mom: 0.3, trend: 'up' },
    { name: 'Apparel', weight: 2.5, yoy: -1.2, mom: -0.2, trend: 'down' },
    { name: 'Energy', weight: 6.8, yoy: -4.9, mom: -0.4, trend: 'up' },
  ],
};

const gdpData = {
  current: { value: 2.8, prior: 3.0, unit: '% SAAR' },
  components: [
    { name: 'Consumption', contribution: 2.37, pct: 85 },
    { name: 'Investment', contribution: 0.52, pct: 19 },
    { name: 'Government', contribution: 0.43, pct: 15 },
    { name: 'Net Exports', contribution: -0.52, pct: -19 },
  ],
  trend: [
    { q: 'Q1 23', value: 2.2 },
    { q: 'Q2 23', value: 2.1 },
    { q: 'Q3 23', value: 4.9 },
    { q: 'Q4 23', value: 3.4 },
    { q: 'Q1 24', value: 1.4 },
    { q: 'Q2 24', value: 3.0 },
    { q: 'Q3 24', value: 2.8 },
  ],
};

const calendarEvents = [
  { date: 'Dec 11', time: '8:30 AM', name: 'CPI', source: 'BLS', importance: 3 },
  { date: 'Dec 11', time: '1:00 PM', name: '10Y Auction', source: 'Treasury', importance: 2 },
  { date: 'Dec 12', time: '8:30 AM', name: 'PPI', source: 'BLS', importance: 2 },
  { date: 'Dec 12', time: '1:00 PM', name: '30Y Auction', source: 'Treasury', importance: 2 },
  { date: 'Dec 18', time: '2:00 PM', name: 'FOMC', source: 'Fed', importance: 3 },
  { date: 'Jan 10', time: '8:30 AM', name: 'Employment', source: 'BLS', importance: 3 },
];

// ============================================================================
// MICRO COMPONENTS - Sparklines & Indicators
// ============================================================================

function MiniSparkline({
  data,
  color = '#6366f1',
  width = 80,
  height = 24,
  showArea = true
}: {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
  showArea?: boolean;
}) {
  const chartData = data.map((value, i) => ({ value, i }));
  const isUp = data[data.length - 1] >= data[0];
  const lineColor = color === 'auto' ? (isUp ? '#10b981' : '#ef4444') : color;

  return (
    <div style={{ width, height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
          <defs>
            <linearGradient id={`gradient-${lineColor}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={lineColor} stopOpacity={0.3} />
              <stop offset="100%" stopColor={lineColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          {showArea && (
            <Area
              type="monotone"
              dataKey="value"
              stroke={lineColor}
              fill={`url(#gradient-${lineColor})`}
              strokeWidth={1.5}
            />
          )}
          {!showArea && (
            <Line type="monotone" dataKey="value" stroke={lineColor} strokeWidth={1.5} dot={false} />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

function ChangeIndicator({ value, suffix = '%' }: { value: number; suffix?: string }) {
  const isPositive = value >= 0;
  return (
    <span className={`inline-flex items-center text-xs font-medium ${isPositive ? 'text-emerald-600' : 'text-red-500'}`}>
      {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
      {Math.abs(value).toFixed(2)}{suffix}
    </span>
  );
}

function TrendBadge({ trend }: { trend: 'up' | 'down' | 'flat' }) {
  const config = {
    up: { icon: TrendingUp, color: 'text-emerald-600 bg-emerald-50', label: '↑' },
    down: { icon: TrendingDown, color: 'text-red-500 bg-red-50', label: '↓' },
    flat: { icon: Activity, color: 'text-gray-500 bg-gray-100', label: '→' },
  };
  const { color, label } = config[trend];
  return (
    <span className={`inline-flex items-center justify-center w-5 h-5 rounded text-xs font-bold ${color}`}>
      {label}
    </span>
  );
}

// DataPill component - reserved for future use
function _DataPill({ label, value, change, small = false }: { label: string; value: string; change?: number; small?: boolean }) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${small ? 'px-2 py-1.5' : 'px-3 py-2'}`}>
      <div className={`text-gray-500 ${small ? 'text-[10px]' : 'text-xs'}`}>{label}</div>
      <div className="flex items-baseline gap-1.5">
        <span className={`font-semibold text-gray-900 ${small ? 'text-sm' : 'text-base'}`}>{value}</span>
        {change !== undefined && <ChangeIndicator value={change} />}
      </div>
    </div>
  );
}
void _DataPill; // Suppress unused warning

// ============================================================================
// SECTION COMPONENTS
// ============================================================================

function MarketTickerBar() {
  return (
    <div className="bg-gray-900 text-white">
      <div className="max-w-[1800px] mx-auto">
        <div className="flex items-center divide-x divide-gray-700 overflow-x-auto">
          {marketData.indices.map((idx, i) => (
            <div key={i} className="flex items-center gap-3 px-4 py-2 min-w-fit">
              <div>
                <div className="text-[10px] text-gray-400 uppercase tracking-wide">{idx.name}</div>
                <div className="text-sm font-medium">{idx.value.toLocaleString()}</div>
              </div>
              <MiniSparkline data={idx.data} color="auto" width={50} height={20} />
              <ChangeIndicator value={idx.change} />
            </div>
          ))}
          <div className="flex items-center gap-3 px-4 py-2 min-w-fit">
            <div>
              <div className="text-[10px] text-gray-400 uppercase tracking-wide">10Y Yield</div>
              <div className="text-sm font-medium">{marketData.yields[2].yield}%</div>
            </div>
            <ChangeIndicator value={marketData.yields[2].change} suffix=" bps" />
          </div>
          <div className="flex items-center gap-3 px-4 py-2 min-w-fit">
            <div>
              <div className="text-[10px] text-gray-400 uppercase tracking-wide">2s10s</div>
              <div className="text-sm font-medium text-emerald-400">+3 bps</div>
            </div>
            <span className="text-[10px] text-gray-500">First positive since Jul '22</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function YieldCurveCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900 text-sm">Treasury Yield Curve</h3>
        <span className="text-xs text-gray-500">Updated 4:00 PM ET</span>
      </div>
      <div className="h-32">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={marketData.yieldCurve} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
            <defs>
              <linearGradient id="yieldGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="term" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
            <YAxis domain={[3.8, 4.8]} tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={30} />
            <Tooltip
              contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }}
              formatter={(value: number) => [`${value}%`, 'Yield']}
            />
            <Area type="monotone" dataKey="yield" stroke="#6366f1" fill="url(#yieldGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="flex gap-4 mt-3 pt-3 border-t border-gray-100">
        {marketData.yields.map((y, i) => (
          <div key={i} className="text-center flex-1">
            <div className="text-[10px] text-gray-500">{y.maturity}</div>
            <div className="text-sm font-semibold text-gray-900">{y.yield}%</div>
            <div className={`text-[10px] ${y.change >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
              {y.change >= 0 ? '+' : ''}{y.change}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function LaborMarketCard({ data }: { data: EmploymentDataProps }) {
  const { ceOverview, lnOverview, lnTimeline, loading } = data;

  // Format payrolls change
  const payrollsChange = ceOverview?.total_nonfarm?.month_over_month;
  const payrollsFormatted = payrollsChange != null ? `${payrollsChange >= 0 ? '+' : ''}${payrollsChange.toFixed(0)}K` : '--';

  // Unemployment data (from LN survey - headline_unemployment)
  const unemploymentRate = lnOverview?.headline_unemployment?.latest_value;
  const unemploymentChange = lnOverview?.headline_unemployment?.month_over_month;

  // Participation rate (from LN survey - labor_force_participation)
  const participationRate = lnOverview?.labor_force_participation?.latest_value;
  const participationChange = lnOverview?.labor_force_participation?.month_over_month;

  // Format period for badge
  const latestDate = lnOverview?.headline_unemployment?.latest_date || ceOverview?.total_nonfarm?.latest_date || '';

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-indigo-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Employment Situation</h3>
        </div>
        {latestDate && (
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">{latestDate}</span>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <>
          {/* Headline Numbers */}
          <div className="grid grid-cols-4 gap-2 mb-4">
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-[10px] text-gray-500">Payrolls</div>
              <div className="text-lg font-bold text-gray-900">{payrollsFormatted}</div>
              <div className="text-[10px] text-gray-400">MoM change</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-[10px] text-gray-500">Unemployment</div>
              <div className="text-lg font-bold text-gray-900">
                {unemploymentRate != null ? `${unemploymentRate.toFixed(1)}%` : '--'}
              </div>
              {unemploymentChange != null && (
                <div className={`text-[10px] ${unemploymentChange > 0 ? 'text-red-500' : unemploymentChange < 0 ? 'text-emerald-500' : 'text-gray-400'}`}>
                  {unemploymentChange > 0 ? '↑' : unemploymentChange < 0 ? '↓' : ''} {Math.abs(unemploymentChange).toFixed(2)}pp
                </div>
              )}
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-[10px] text-gray-500">Participation</div>
              <div className="text-lg font-bold text-gray-900">
                {participationRate != null ? `${participationRate.toFixed(1)}%` : '--'}
              </div>
              {participationChange != null && (
                <div className={`text-[10px] ${participationChange < 0 ? 'text-red-500' : participationChange > 0 ? 'text-emerald-500' : 'text-gray-400'}`}>
                  {participationChange > 0 ? '↑' : participationChange < 0 ? '↓' : ''} {Math.abs(participationChange).toFixed(2)}pp
                </div>
              )}
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-[10px] text-gray-500">Total Nonfarm</div>
              <div className="text-lg font-bold text-gray-900">
                {ceOverview?.total_nonfarm?.latest_value
                  ? `${(ceOverview.total_nonfarm.latest_value / 1000).toFixed(1)}M`
                  : '--'}
              </div>
              <div className="text-[10px] text-gray-400">jobs</div>
            </div>
          </div>

          {/* Unemployment Rate Trend Chart */}
          {lnTimeline.length > 0 && (
            <div className="h-20 mb-1">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={lnTimeline} margin={{ top: 5, right: 5, bottom: 0, left: 5 }}>
                  <defs>
                    <linearGradient id="unemploymentGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="period_name"
                    tick={{ fontSize: 8, fill: '#9ca3af' }}
                    axisLine={false}
                    tickLine={false}
                    interval="preserveStartEnd"
                  />
                  <Tooltip
                    contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }}
                    formatter={(value: number) => [`${value?.toFixed(1)}%`, 'Unemployment']}
                    labelFormatter={(label) => label}
                  />
                  <Area
                    type="monotone"
                    dataKey="headline_value"
                    stroke="#ef4444"
                    fill="url(#unemploymentGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
          <div className="text-[10px] text-gray-500 text-center">Unemployment Rate Trend (12 months)</div>
        </>
      )}

      <Link to="/research/bls/ln" className="flex items-center justify-center gap-1 mt-3 pt-3 border-t border-gray-100 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
        Labor Force Explorer <ChevronRight className="w-3 h-3" />
      </Link>
    </div>
  );
}

function SectorJobsCard({ data }: { data: EmploymentDataProps }) {
  const { supersectors, loading, ceOverview } = data;

  // Transform supersectors to sector jobs format, sorted by MoM change
  const sectorJobs = supersectors
    .filter(s => s.month_over_month != null)
    .map(s => ({
      sector: s.supersector_name.replace(' and ', ' & ').replace('Professional and Business Services', 'Prof. Services'),
      change: s.month_over_month || 0,
    }))
    .sort((a, b) => b.change - a.change)
    .slice(0, 7); // Show top 7

  // Fallback to sample data if no real data
  const displayData = sectorJobs.length > 0 ? sectorJobs : laborData.sectorJobs;
  const maxChange = Math.max(...displayData.map(s => Math.abs(s.change)), 1);

  // Get latest date from CE overview
  const latestDate = ceOverview?.total_nonfarm?.latest_date || '';

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900 text-sm">Jobs by Sector</h3>
        {latestDate && (
          <span className="text-xs text-gray-500">{latestDate}</span>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <div className="space-y-2">
          {displayData.map((sector, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="w-24 text-xs text-gray-600 truncate" title={sector.sector}>{sector.sector}</div>
              <div className="flex-1 h-4 bg-gray-100 rounded relative overflow-hidden">
                <div
                  className={`absolute h-full rounded ${sector.change >= 0 ? 'bg-emerald-500' : 'bg-red-400'}`}
                  style={{
                    width: `${(Math.abs(sector.change) / maxChange) * 50}%`,
                    [sector.change >= 0 ? 'left' : 'right']: '50%'
                  }}
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-px h-full bg-gray-300" />
                </div>
              </div>
              <div className={`w-12 text-xs font-medium text-right ${sector.change >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                {sector.change >= 0 ? '+' : ''}{sector.change.toFixed(0)}K
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
// Suppress unused warnings - these may be used in future layouts
void LaborMarketCard;
void SectorJobsCard;
void JOLTSCard;

function JOLTSCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900 text-sm">JOLTS Overview</h3>
        <span className="text-xs text-gray-500">Oct 2024</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-gray-500">Openings</span>
            <MiniSparkline data={laborData.jolts.openings.trend} width={40} height={16} color="#6366f1" />
          </div>
          <div className="text-lg font-semibold text-gray-900">{laborData.jolts.openings.value}M</div>
          <div className="text-[10px] text-emerald-600">↑ from {laborData.jolts.openings.prior}M</div>
        </div>
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-gray-500">Hires</span>
            <MiniSparkline data={laborData.jolts.hires.trend} width={40} height={16} color="#f59e0b" />
          </div>
          <div className="text-lg font-semibold text-gray-900">{laborData.jolts.hires.value}M</div>
          <div className="text-[10px] text-red-500">↓ from {laborData.jolts.hires.prior}M</div>
        </div>
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-gray-500">Quits</span>
            <MiniSparkline data={laborData.jolts.quits.trend} width={40} height={16} color="#10b981" />
          </div>
          <div className="text-lg font-semibold text-gray-900">{laborData.jolts.quits.value}M</div>
          <div className="text-[10px] text-emerald-600">↑ from {laborData.jolts.quits.prior}M</div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
        <div className="text-xs text-gray-600">
          <span className="font-semibold text-gray-900">{laborData.jolts.ratio.value}x</span> {laborData.jolts.ratio.text}
        </div>
        <Link to="/research/bls/jt" className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
          JOLTS Explorer →
        </Link>
      </div>
    </div>
  );
}

function InflationCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-red-500" />
          <h3 className="font-semibold text-gray-900 text-sm">Consumer Prices (CPI)</h3>
        </div>
        <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded font-medium">Preview Wed</span>
      </div>

      {/* Headline vs Core */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-600">Headline CPI</span>
            <MiniSparkline data={inflationData.cpi.headline.trend} width={50} height={20} color="#6366f1" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{inflationData.cpi.headline.value}%</div>
          <div className="text-xs text-gray-500">YoY • Prior {inflationData.cpi.headline.prior}%</div>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-600">Core CPI</span>
            <MiniSparkline data={inflationData.cpi.core.trend} width={50} height={20} color="#ef4444" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{inflationData.cpi.core.value}%</div>
          <div className="text-xs text-gray-500">YoY • Unchanged</div>
        </div>
      </div>

      {/* Components Table */}
      <div className="text-xs">
        <div className="grid grid-cols-12 gap-1 text-gray-500 border-b border-gray-100 pb-1 mb-1">
          <div className="col-span-4">Component</div>
          <div className="col-span-2 text-right">Weight</div>
          <div className="col-span-2 text-right">YoY</div>
          <div className="col-span-2 text-right">MoM</div>
          <div className="col-span-2 text-center">Trend</div>
        </div>
        {inflationData.components.slice(0, 4).map((c, i) => (
          <div key={i} className="grid grid-cols-12 gap-1 py-1 hover:bg-gray-50">
            <div className="col-span-4 text-gray-700">{c.name}</div>
            <div className="col-span-2 text-right text-gray-500">{c.weight}%</div>
            <div className={`col-span-2 text-right font-medium ${c.yoy >= 3 ? 'text-red-500' : 'text-gray-900'}`}>{c.yoy}%</div>
            <div className="col-span-2 text-right text-gray-600">{c.mom >= 0 ? '+' : ''}{c.mom}%</div>
            <div className="col-span-2 text-center"><TrendBadge trend={c.trend as 'up' | 'down' | 'flat'} /></div>
          </div>
        ))}
      </div>

      <Link to="/research/bls/cu" className="flex items-center justify-center gap-1 mt-3 pt-3 border-t border-gray-100 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
        CPI Explorer <ChevronRight className="w-3 h-3" />
      </Link>
    </div>
  );
}

// Types for Employment Tabbed Card
interface CESupersector {
  supersector_code: string;
  supersector_name: string;
  latest_value?: number;
}

interface CESupersectorsData {
  supersectors: CESupersector[];
}

interface CETimelinePoint {
  year: number;
  period: string;
  period_name: string;
  supersectors?: Record<string, number>;
}

interface CESupersectorTimelineData {
  timeline: CETimelinePoint[];
  supersector_names?: Record<string, string>;
}

interface CEEarningsItem {
  industry_code: string;
  industry_name: string;
  avg_hourly_earnings?: number;
  hourly_yoy_pct?: number;
}

interface CEEarningsData {
  earnings: CEEarningsItem[];
}

interface JTTimelinePointCard {
  year: number;
  period: string;
  period_name: string;
  job_openings_rate?: number;
  hires_rate?: number;
  quits_rate?: number;
  layoffs_rate?: number;
}

interface JTTimelineDataCard {
  timeline: JTTimelinePointCard[];
}

type EmploymentTabType = 'sectors' | 'earnings' | 'jolts';

function EmploymentTabbedCard() {
  const [activeTab, setActiveTab] = useState<EmploymentTabType>('sectors');
  const [supersectors, setSupersectors] = useState<CESupersectorsData | null>(null);
  const [ceTimeline, setCeTimeline] = useState<CESupersectorTimelineData | null>(null);
  const [earnings, setEarnings] = useState<CEEarningsData | null>(null);
  const [jtTimeline, setJtTimeline] = useState<JTTimelineDataCard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [ssRes, ceTlRes, earningsRes, jtTlRes] = await Promise.all([
          ceResearchAPI.getSupersectors<CESupersectorsData>(),
          ceResearchAPI.getSupersectorsTimeline<CESupersectorTimelineData>({
            supersector_codes: '05,06,07,08,10,20,30,40,41,42,43,50,55,60,65,70,80,90',
            months_back: 60
          }),
          ceResearchAPI.getEarnings<CEEarningsData>({ limit: 10 }),
          jtResearchAPI.getOverviewTimeline<JTTimelineDataCard>('000000', '00', 60),
        ]);
        setSupersectors(ssRes.data);
        setCeTimeline(ceTlRes.data);
        setEarnings(earningsRes.data);
        setJtTimeline(jtTlRes.data);
      } catch (error) {
        console.error('Failed to load employment data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Get same-month data for YoY comparison (5 years of same month)
  const getSameMonthData = <T extends { year: number; period: string }>(timeline: T[] | undefined): T[] => {
    if (!timeline || timeline.length === 0) return [];
    const latest = timeline[timeline.length - 1];
    const targetPeriod = latest.period;
    return timeline.filter(p => p.period === targetPeriod).slice(-5);
  };

  const ceSameMonthData = getSameMonthData(ceTimeline?.timeline);
  const jtSameMonthData = getSameMonthData(jtTimeline?.timeline);

  // Get top supersectors by employment
  const topSupersectors = supersectors?.supersectors
    ?.filter(ss => ss.latest_value && ss.latest_value > 0)
    .sort((a, b) => (b.latest_value || 0) - (a.latest_value || 0))
    .slice(0, 8) || [];

  // Top earnings industries
  const topEarnings = earnings?.earnings?.slice(0, 8) || [];

  const tabs: { id: EmploymentTabType; label: string }[] = [
    { id: 'sectors', label: 'Sectors' },
    { id: 'earnings', label: 'Wages' },
    { id: 'jolts', label: 'JOLTS' },
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header with tabs */}
      <div className="flex items-center justify-between border-b border-gray-100 px-3 py-2 bg-gray-50">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-blue-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Labor Market</h3>
        </div>
        <div className="flex gap-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-2">
        {loading ? (
          <div className="flex items-center justify-center h-[220px]">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : activeTab === 'sectors' ? (
          <div className="overflow-x-auto max-h-[220px]">
            <table className="w-full text-xs">
              <thead className="sticky top-0 bg-gray-50 z-10">
                <tr className="border-b border-gray-200">
                  <th className="text-left py-1.5 px-2 font-semibold text-gray-600 sticky left-0 bg-gray-50 z-20 min-w-[110px]">Sector</th>
                  {ceSameMonthData.slice().reverse().map((point, idx) => (
                    <th
                      key={`${point.year}-${point.period}`}
                      className={`text-right py-1.5 px-1.5 font-semibold min-w-[55px] whitespace-nowrap ${idx === 0 ? 'bg-blue-100 text-blue-700' : 'text-gray-600'}`}
                    >
                      {point.period_name.split(' ')[0].slice(0, 3)} '{String(point.year).slice(2)}
                    </th>
                  ))}
                  <th className="text-right py-1.5 px-1.5 font-semibold text-gray-600 min-w-[45px]">YoY</th>
                </tr>
              </thead>
              <tbody>
                {topSupersectors.map((ss) => {
                  const values = ceSameMonthData.slice().reverse().map(p => p.supersectors?.[ss.supersector_code]);
                  const latestVal = values[0];
                  const priorYearVal = values[1];
                  const yoyChange = latestVal && priorYearVal ? ((latestVal - priorYearVal) / priorYearVal * 100) : null;

                  return (
                    <tr key={ss.supersector_code} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-1 px-2 font-medium text-gray-700 sticky left-0 bg-white z-10 truncate max-w-[110px]" title={ss.supersector_name}>
                        {ss.supersector_name.length > 16 ? ss.supersector_name.slice(0, 16) + '…' : ss.supersector_name}
                      </td>
                      {values.map((val, idx) => (
                        <td
                          key={idx}
                          className={`text-right py-1 px-1.5 font-mono ${idx === 0 ? 'bg-blue-50 font-semibold text-blue-700' : 'text-gray-600'}`}
                        >
                          {val != null ? (val / 1000).toFixed(1) : '-'}
                        </td>
                      ))}
                      <td className={`text-right py-1 px-1.5 font-semibold ${yoyChange != null ? (yoyChange >= 0 ? 'text-green-600' : 'text-red-600') : 'text-gray-400'}`}>
                        {yoyChange != null ? (yoyChange >= 0 ? '+' : '') + yoyChange.toFixed(1) + '%' : '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : activeTab === 'earnings' ? (
          <div className="overflow-x-auto max-h-[220px]">
            <table className="w-full text-xs">
              <thead className="sticky top-0 bg-gray-50 z-10">
                <tr className="border-b border-gray-200">
                  <th className="text-left py-1.5 px-2 font-semibold text-gray-600 sticky left-0 bg-gray-50 z-20 min-w-[140px]">Industry</th>
                  <th className="text-right py-1.5 px-2 font-semibold text-gray-600 min-w-[70px]">Hourly $</th>
                  <th className="text-right py-1.5 px-2 font-semibold text-gray-600 min-w-[55px]">YoY</th>
                </tr>
              </thead>
              <tbody>
                {topEarnings.map((e) => (
                  <tr key={e.industry_code} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-1.5 px-2 font-medium text-gray-700 sticky left-0 bg-white z-10 truncate max-w-[140px]" title={e.industry_name}>
                      {e.industry_name.length > 22 ? e.industry_name.slice(0, 22) + '…' : e.industry_name}
                    </td>
                    <td className="text-right py-1.5 px-2 font-mono font-semibold text-purple-700">
                      ${e.avg_hourly_earnings?.toFixed(2) || '-'}
                    </td>
                    <td className={`text-right py-1.5 px-2 font-semibold ${e.hourly_yoy_pct != null ? (e.hourly_yoy_pct >= 0 ? 'text-green-600' : 'text-red-600') : 'text-gray-400'}`}>
                      {e.hourly_yoy_pct != null ? (e.hourly_yoy_pct >= 0 ? '+' : '') + e.hourly_yoy_pct.toFixed(1) + '%' : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto max-h-[220px]">
            <table className="w-full text-xs">
              <thead className="sticky top-0 bg-gray-50 z-10">
                <tr className="border-b border-gray-200">
                  <th className="text-left py-1.5 px-2 font-semibold text-gray-600 sticky left-0 bg-gray-50 z-20 min-w-[80px]">Metric</th>
                  {jtSameMonthData.slice().reverse().map((point, idx) => (
                    <th
                      key={`${point.year}-${point.period}`}
                      className={`text-right py-1.5 px-1.5 font-semibold min-w-[55px] whitespace-nowrap ${idx === 0 ? 'bg-amber-100 text-amber-700' : 'text-gray-600'}`}
                    >
                      {point.period_name.split(' ')[0].slice(0, 3)} '{String(point.year).slice(2)}
                    </th>
                  ))}
                  <th className="text-right py-1.5 px-1.5 font-semibold text-gray-600 min-w-[45px]">YoY</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { key: 'job_openings_rate', label: 'Job Openings' },
                  { key: 'hires_rate', label: 'Hires Rate' },
                  { key: 'quits_rate', label: 'Quits Rate' },
                  { key: 'layoffs_rate', label: 'Layoffs Rate' },
                ].map((metric) => {
                  const values = jtSameMonthData.slice().reverse().map(p => p[metric.key as keyof JTTimelinePointCard] as number | undefined);
                  const latestVal = values[0];
                  const priorYearVal = values[1];
                  const yoyChange = latestVal != null && priorYearVal != null && priorYearVal !== 0
                    ? ((latestVal - priorYearVal) / priorYearVal * 100)
                    : null;

                  return (
                    <tr key={metric.key} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-1.5 px-2 font-medium text-gray-700 sticky left-0 bg-white z-10">{metric.label}</td>
                      {values.map((val, idx) => (
                        <td
                          key={idx}
                          className={`text-right py-1.5 px-1.5 font-mono ${idx === 0 ? 'bg-amber-50 font-semibold text-amber-700' : 'text-gray-600'}`}
                        >
                          {val != null ? val.toFixed(1) + '%' : '-'}
                        </td>
                      ))}
                      <td className={`text-right py-1.5 px-1.5 font-semibold ${yoyChange != null ? (yoyChange >= 0 ? 'text-green-600' : 'text-red-600') : 'text-gray-400'}`}>
                        {yoyChange != null ? (yoyChange >= 0 ? '+' : '') + yoyChange.toFixed(1) + '%' : '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function GDPCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-emerald-600" />
          <h3 className="font-semibold text-gray-900 text-sm">GDP Growth</h3>
        </div>
        <span className="text-xs text-gray-500">Q3 2024</span>
      </div>

      <div className="flex gap-4 mb-4">
        <div>
          <div className="text-3xl font-bold text-gray-900">{gdpData.current.value}%</div>
          <div className="text-xs text-gray-500">SAAR • Prior {gdpData.current.prior}%</div>
        </div>
        <div className="flex-1 h-20">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={gdpData.trend} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
              <XAxis dataKey="q" tick={{ fontSize: 8, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
              <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                {gdpData.trend.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={index === gdpData.trend.length - 1 ? '#6366f1' : '#e5e7eb'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Contributions */}
      <div className="text-xs text-gray-500 mb-2">Contribution to Growth</div>
      <div className="space-y-1.5">
        {gdpData.components.map((c, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="w-20 text-xs text-gray-600">{c.name}</div>
            <div className="flex-1 h-2 bg-gray-100 rounded overflow-hidden">
              <div
                className={`h-full ${c.contribution >= 0 ? 'bg-emerald-500' : 'bg-red-400'}`}
                style={{ width: `${Math.abs(c.pct)}%`, marginLeft: c.contribution < 0 ? 'auto' : 0 }}
              />
            </div>
            <div className={`w-12 text-xs font-medium text-right ${c.contribution >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
              {c.contribution >= 0 ? '+' : ''}{c.contribution.toFixed(2)}
            </div>
          </div>
        ))}
      </div>

      <Link to="/research/bea" className="flex items-center justify-center gap-1 mt-3 pt-3 border-t border-gray-100 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
        GDP & BEA Data <ChevronRight className="w-3 h-3" />
      </Link>
    </div>
  );
}

function CalendarCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-gray-400" />
          <h3 className="font-semibold text-gray-900 text-sm">Economic Calendar</h3>
        </div>
      </div>
      <div className="divide-y divide-gray-100">
        {calendarEvents.map((e, i) => (
          <div key={i} className="px-4 py-2 flex items-center gap-3 hover:bg-gray-50">
            <div className="w-12 text-center">
              <div className="text-xs font-medium text-gray-900">{e.date}</div>
              <div className="text-[10px] text-gray-400">{e.time}</div>
            </div>
            <div className="flex-1">
              <div className="text-sm text-gray-900">{e.name}</div>
              <div className="text-[10px] text-gray-500">{e.source}</div>
            </div>
            <div className="flex gap-0.5">
              {[...Array(3)].map((_, j) => (
                <div key={j} className={`w-1.5 h-1.5 rounded-full ${j < e.importance ? 'bg-red-400' : 'bg-gray-200'}`} />
              ))}
            </div>
          </div>
        ))}
      </div>
      <Link to="/research/calendar" className="block px-4 py-2 text-center text-xs text-indigo-600 hover:text-indigo-700 font-medium border-t border-gray-100">
        View Full Calendar →
      </Link>
    </div>
  );
}

function DataExplorerGrid() {
  const explorers = [
    { code: 'CE', name: 'Employment', desc: 'Payrolls, hours, earnings', icon: Users, series: '22K', color: 'bg-blue-500' },
    { code: 'CU', name: 'Consumer Prices', desc: 'CPI all components', icon: DollarSign, series: '6.8K', color: 'bg-red-500' },
    { code: 'JT', name: 'JOLTS', desc: 'Openings, hires, quits', icon: Briefcase, series: '2K', color: 'bg-amber-500' },
    { code: 'LN', name: 'Labor Force', desc: 'Demographics, rates', icon: Users, series: '65K', color: 'bg-indigo-500' },
    { code: 'OE', name: 'Occupational', desc: 'Employment & wages', icon: Factory, series: '6M', color: 'bg-emerald-500' },
    { code: 'LA', name: 'Local Area', desc: 'State & metro data', icon: Building2, series: '33K', color: 'bg-purple-500' },
    { code: 'PC', name: 'Producer Prices', desc: 'PPI by commodity', icon: Truck, series: '3.8K', color: 'bg-orange-500' },
    { code: 'PR', name: 'Productivity', desc: 'Labor productivity', icon: Zap, series: '237', color: 'bg-cyan-500' },
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="font-semibold text-gray-900 text-sm mb-3">BLS Data Explorers</h3>
      <div className="grid grid-cols-4 gap-2">
        {explorers.map((e) => {
          const Icon = e.icon;
          return (
            <Link
              key={e.code}
              to={`/research/bls/${e.code.toLowerCase()}`}
              className="group p-2 rounded-lg border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all"
            >
              <div className="flex items-center gap-2 mb-1">
                <div className={`w-6 h-6 rounded flex items-center justify-center ${e.color}`}>
                  <Icon className="w-3 h-3 text-white" />
                </div>
                <span className="text-xs font-bold text-gray-500">{e.code}</span>
              </div>
              <div className="text-xs font-medium text-gray-900 group-hover:text-indigo-600">{e.name}</div>
              <div className="text-[10px] text-gray-500">{e.series} series</div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function AuctionResultsCard() {
  const auctions = [
    { term: '10Y', date: 'Dec 4', yield: 4.235, btc: 2.58, tail: -0.3, result: 'strong' },
    { term: '30Y', date: 'Nov 27', yield: 4.535, btc: 2.39, tail: 0.8, result: 'weak' },
    { term: '5Y', date: 'Nov 26', yield: 4.197, btc: 2.42, tail: 0.2, result: 'neutral' },
    { term: '2Y', date: 'Nov 25', yield: 4.274, btc: 2.68, tail: -0.5, result: 'strong' },
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Landmark className="w-4 h-4 text-indigo-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Recent Auctions</h3>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-gray-500 border-b border-gray-100">
              <th className="pb-2 text-left font-medium">Term</th>
              <th className="pb-2 text-left font-medium">Date</th>
              <th className="pb-2 text-right font-medium">Yield</th>
              <th className="pb-2 text-right font-medium">BTC</th>
              <th className="pb-2 text-right font-medium">Tail</th>
              <th className="pb-2 text-center font-medium">Result</th>
            </tr>
          </thead>
          <tbody>
            {auctions.map((a, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-2 font-medium text-gray-900">{a.term}</td>
                <td className="py-2 text-gray-600">{a.date}</td>
                <td className="py-2 text-right text-gray-900">{a.yield}%</td>
                <td className="py-2 text-right text-gray-600">{a.btc}x</td>
                <td className={`py-2 text-right font-medium ${a.tail <= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                  {a.tail > 0 ? '+' : ''}{a.tail}
                </td>
                <td className="py-2 text-center">
                  <span className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-medium ${
                    a.result === 'strong' ? 'bg-emerald-100 text-emerald-700' :
                    a.result === 'weak' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {a.result}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Link to="/research/treasury/auctions" className="flex items-center justify-center gap-1 mt-3 pt-3 border-t border-gray-100 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
        All Auctions <ChevronRight className="w-3 h-3" />
      </Link>
    </div>
  );
}

// ============================================================================
// SURVEY CAROUSEL COMPONENT
// ============================================================================

const SURVEY_CONFIGS: CarouselSurveyConfig[] = [
  {
    id: 'ln',
    name: 'LN',
    fullName: 'Labor Force Statistics',
    description: 'Unemployment, Labor Force Participation, Employment-Population Ratio',
    color: '#dc2626',
    bgGradient: 'from-red-50 to-orange-50',
    icon: Users,
  },
  {
    id: 'ce',
    name: 'CE',
    fullName: 'Employment Situation',
    description: 'Nonfarm Payrolls, Hours, Earnings by Industry',
    color: '#2563eb',
    bgGradient: 'from-blue-50 to-indigo-50',
    icon: Briefcase,
  },
  {
    id: 'jt',
    name: 'JT',
    fullName: 'JOLTS',
    description: 'Job Openings, Hires, Quits, Separations',
    color: '#f59e0b',
    bgGradient: 'from-amber-50 to-yellow-50',
    icon: Target,
  },
  {
    id: 'cu',
    name: 'CU',
    fullName: 'Consumer Prices (CPI)',
    description: 'Headline & Core Inflation, Major Categories',
    color: '#ef4444',
    bgGradient: 'from-red-50 to-pink-50',
    icon: DollarSign,
  },
  {
    id: 'wp',
    name: 'WP',
    fullName: 'Producer Prices (PPI)',
    description: 'Final Demand, Goods, Services Price Changes',
    color: '#8b5cf6',
    bgGradient: 'from-purple-50 to-violet-50',
    icon: Factory,
  },
  {
    id: 'la',
    name: 'LA',
    fullName: 'Local Area Unemployment',
    description: 'State & Metro Unemployment Rates',
    color: '#10b981',
    bgGradient: 'from-emerald-50 to-teal-50',
    icon: Building2,
  },
  {
    id: 'pc',
    name: 'PC',
    fullName: 'PPI by Industry',
    description: 'Producer Prices by Industry Sector',
    color: '#0891b2',
    bgGradient: 'from-cyan-50 to-sky-50',
    icon: Truck,
  },
];

// Individual slide components for each survey
function LNSlide({ data }: { data: CarouselData['ln'] }) {
  const { overview, timeline } = data;
  const unemployment = overview?.headline_unemployment;
  const lfpr = overview?.labor_force_participation;

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Metrics */}
      <div className="space-y-3">
        <div className="bg-red-50 rounded-lg p-3 border border-red-100">
          <div className="text-xs text-gray-500 mb-1">Unemployment Rate</div>
          <div className="text-3xl font-bold text-gray-900">
            {unemployment?.latest_value?.toFixed(1) ?? '--'}%
          </div>
          {unemployment?.month_over_month != null && (
            <div className={`text-sm ${unemployment.month_over_month > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
              {unemployment.month_over_month > 0 ? '↑' : '↓'} {Math.abs(unemployment.month_over_month).toFixed(2)}pp MoM
            </div>
          )}
        </div>
        <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
          <div className="text-xs text-gray-500 mb-1">Labor Force Participation</div>
          <div className="text-2xl font-bold text-gray-900">
            {lfpr?.latest_value?.toFixed(1) ?? '--'}%
          </div>
          {lfpr?.month_over_month != null && (
            <div className={`text-xs ${lfpr.month_over_month < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
              {lfpr.month_over_month > 0 ? '↑' : '↓'} {Math.abs(lfpr.month_over_month).toFixed(2)}pp MoM
            </div>
          )}
        </div>
        <div className="text-xs text-gray-400 text-center">
          {unemployment?.latest_date || 'Latest data'}
        </div>
      </div>

      {/* Chart */}
      <div className="col-span-2">
        <div className="text-xs font-medium text-gray-600 mb-2">Unemployment Rate Trend</div>
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeline} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="lnGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#dc2626" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#dc2626" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={35} domain={['auto', 'auto']} tickFormatter={(v) => `${v}%`} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }} formatter={(value: number) => [`${value?.toFixed(1)}%`, 'Unemployment']} />
              <Area type="monotone" dataKey="headline_value" stroke="#dc2626" fill="url(#lnGradient)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function CESlide({ data }: { data: CarouselData['ce'] }) {
  const { overview, supersectors } = data;
  const totalNonfarm = overview?.total_nonfarm;
  const payrollsChange = totalNonfarm?.month_over_month;
  const topSectors = supersectors
    .filter(s => s.month_over_month != null)
    .sort((a, b) => (b.month_over_month || 0) - (a.month_over_month || 0))
    .slice(0, 5);

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Metrics */}
      <div className="space-y-3">
        <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
          <div className="text-xs text-gray-500 mb-1">Nonfarm Payrolls</div>
          <div className="text-3xl font-bold text-gray-900">
            {payrollsChange != null ? `${payrollsChange >= 0 ? '+' : ''}${payrollsChange.toFixed(0)}K` : '--'}
          </div>
          <div className="text-xs text-gray-500">MoM change</div>
        </div>
        <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-100">
          <div className="text-xs text-gray-500 mb-1">Total Employment</div>
          <div className="text-2xl font-bold text-gray-900">
            {totalNonfarm?.latest_value ? `${(totalNonfarm.latest_value / 1000).toFixed(1)}M` : '--'}
          </div>
          <div className="text-xs text-gray-500">jobs</div>
        </div>
        <div className="text-xs text-gray-400 text-center">
          {totalNonfarm?.latest_date || 'Latest data'}
        </div>
      </div>

      {/* Sector changes */}
      <div className="col-span-2">
        <div className="text-xs font-medium text-gray-600 mb-2">Jobs by Sector (MoM, 000s)</div>
        <div className="space-y-2">
          {topSectors.map((sector, i) => {
            const change = sector.month_over_month || 0;
            const maxChange = Math.max(...topSectors.map(s => Math.abs(s.month_over_month || 0)), 1);
            return (
              <div key={i} className="flex items-center gap-2">
                <div className="w-28 text-xs text-gray-600 truncate">{sector.supersector_name.replace(' and ', ' & ')}</div>
                <div className="flex-1 h-4 bg-gray-100 rounded relative overflow-hidden">
                  <div
                    className={`absolute h-full rounded ${change >= 0 ? 'bg-emerald-500' : 'bg-red-400'}`}
                    style={{ width: `${(Math.abs(change) / maxChange) * 100}%` }}
                  />
                </div>
                <div className={`w-12 text-xs font-medium text-right ${change >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                  {change >= 0 ? '+' : ''}{change.toFixed(0)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function JTSlide({ data }: { data: CarouselData['jt'] }) {
  const { overview, timeline } = data;

  // Get level data (in thousands) for display
  const openingsLevel = overview?.job_openings_level?.value;
  const hiresLevel = overview?.hires_level?.value;
  const quitsLevel = overview?.quits_level?.value;

  // Get rate data for chart
  const openingsRate = overview?.job_openings_rate;
  const hiresRate = overview?.hires_rate;
  const quitsRate = overview?.quits_rate;

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Metrics */}
      <div className="space-y-2">
        <div className="bg-amber-50 rounded-lg p-2 border border-amber-100">
          <div className="text-[10px] text-gray-500">Job Openings</div>
          <div className="text-xl font-bold text-gray-900">
            {openingsLevel != null ? `${(openingsLevel / 1000).toFixed(1)}M` : (openingsRate?.value?.toFixed(1) ?? '--')}
            {openingsLevel == null && openingsRate?.value != null && '%'}
          </div>
          {openingsRate?.year_over_year_pct != null && (
            <div className={`text-[10px] ${openingsRate.year_over_year_pct > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
              {openingsRate.year_over_year_pct > 0 ? '↑' : '↓'} {Math.abs(openingsRate.year_over_year_pct).toFixed(1)}% YoY
            </div>
          )}
        </div>
        <div className="bg-blue-50 rounded-lg p-2 border border-blue-100">
          <div className="text-[10px] text-gray-500">Hires Rate</div>
          <div className="text-xl font-bold text-gray-900">
            {hiresLevel != null ? `${(hiresLevel / 1000).toFixed(1)}M` : (hiresRate?.value?.toFixed(1) ?? '--')}
            {hiresLevel == null && hiresRate?.value != null && '%'}
          </div>
          {hiresRate?.year_over_year_pct != null && (
            <div className={`text-[10px] ${hiresRate.year_over_year_pct > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
              {hiresRate.year_over_year_pct > 0 ? '↑' : '↓'} {Math.abs(hiresRate.year_over_year_pct).toFixed(1)}% YoY
            </div>
          )}
        </div>
        <div className="bg-emerald-50 rounded-lg p-2 border border-emerald-100">
          <div className="text-[10px] text-gray-500">Quits Rate</div>
          <div className="text-xl font-bold text-gray-900">
            {quitsLevel != null ? `${(quitsLevel / 1000).toFixed(1)}M` : (quitsRate?.value?.toFixed(1) ?? '--')}
            {quitsLevel == null && quitsRate?.value != null && '%'}
          </div>
          {quitsRate?.year_over_year_pct != null && (
            <div className={`text-[10px] ${quitsRate.year_over_year_pct > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
              {quitsRate.year_over_year_pct > 0 ? '↑' : '↓'} {Math.abs(quitsRate.year_over_year_pct).toFixed(1)}% YoY
            </div>
          )}
        </div>
        <div className="text-xs text-gray-400 text-center">
          {openingsRate?.latest_date || overview?.last_updated || 'Latest data'}
        </div>
      </div>

      {/* Chart - using rates */}
      <div className="col-span-2">
        <div className="text-xs font-medium text-gray-600 mb-2">JOLTS Rates (%)</div>
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeline} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
              <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={35} tickFormatter={(v) => `${v}%`} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }} formatter={(value: number) => [`${value?.toFixed(1)}%`]} />
              <Area type="monotone" dataKey="job_openings_rate" stroke="#f59e0b" fill="#fef3c7" strokeWidth={2} name="Openings" />
              <Area type="monotone" dataKey="hires_rate" stroke="#2563eb" fill="#dbeafe" strokeWidth={1.5} name="Hires" />
              <Area type="monotone" dataKey="quits_rate" stroke="#10b981" fill="#d1fae5" strokeWidth={1.5} name="Quits" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function CUSlide({ data }: { data: CarouselData['cu'] }) {
  const { overview, timeline } = data;
  const headline = overview?.headline_cpi;
  const core = overview?.core_cpi;

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Metrics */}
      <div className="space-y-3">
        <div className="bg-red-50 rounded-lg p-3 border border-red-100">
          <div className="text-xs text-gray-500 mb-1">Headline CPI YoY</div>
          <div className="text-3xl font-bold text-gray-900">
            {headline?.year_over_year?.toFixed(1) ?? '--'}%
          </div>
          {headline?.month_over_month != null && (
            <div className="text-xs text-gray-500">
              {headline.month_over_month >= 0 ? '+' : ''}{headline.month_over_month.toFixed(2)}% MoM
            </div>
          )}
        </div>
        <div className="bg-purple-50 rounded-lg p-3 border border-purple-100">
          <div className="text-xs text-gray-500 mb-1">Core CPI YoY</div>
          <div className="text-2xl font-bold text-gray-900">
            {core?.year_over_year?.toFixed(1) ?? '--'}%
          </div>
          {core?.month_over_month != null && (
            <div className="text-xs text-gray-500">
              {core.month_over_month >= 0 ? '+' : ''}{core.month_over_month.toFixed(2)}% MoM
            </div>
          )}
        </div>
        <div className="text-xs text-gray-400 text-center">
          {headline?.latest_date || 'Latest data'}
        </div>
      </div>

      {/* Chart */}
      <div className="col-span-2">
        <div className="text-xs font-medium text-gray-600 mb-2">Inflation Rate (YoY %)</div>
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeline} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="cuHeadlineGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={35} tickFormatter={(v) => `${v}%`} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }} formatter={(value: number) => [`${value?.toFixed(2)}%`]} />
              <Area type="monotone" dataKey="headline_yoy" stroke="#ef4444" fill="url(#cuHeadlineGradient)" strokeWidth={2} name="Headline" />
              <Line type="monotone" dataKey="core_yoy" stroke="#8b5cf6" strokeWidth={2} dot={false} name="Core" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function WPSlide({ data }: { data: CarouselData['wp'] }) {
  const { overview, timeline } = data;
  const headline = overview?.headline;
  // Find goods and services from components
  const components = overview?.components || [];
  const goods = components.find(c => c.name?.toLowerCase().includes('goods'));
  const services = components.find(c => c.name?.toLowerCase().includes('services'));

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Metrics */}
      <div className="space-y-2">
        <div className="bg-purple-50 rounded-lg p-2 border border-purple-100">
          <div className="text-[10px] text-gray-500">Final Demand YoY</div>
          <div className="text-2xl font-bold text-gray-900">
            {headline?.yoy_pct?.toFixed(1) ?? '--'}%
          </div>
          {headline?.mom_pct != null && (
            <div className="text-[10px] text-gray-500">
              {headline.mom_pct >= 0 ? '+' : ''}{headline.mom_pct.toFixed(2)}% MoM
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-blue-50 rounded-lg p-2 border border-blue-100">
            <div className="text-[10px] text-gray-500">Goods</div>
            <div className="text-lg font-bold text-gray-900">
              {goods?.yoy_pct?.toFixed(1) ?? '--'}%
            </div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-2 border border-emerald-100">
            <div className="text-[10px] text-gray-500">Services</div>
            <div className="text-lg font-bold text-gray-900">
              {services?.yoy_pct?.toFixed(1) ?? '--'}%
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-400 text-center">
          {headline?.latest_date || overview?.last_updated || 'Latest data'}
        </div>
      </div>

      {/* Chart - show components breakdown */}
      <div className="col-span-2">
        <div className="text-xs font-medium text-gray-600 mb-2">PPI Components (YoY %)</div>
        {components.length > 0 ? (
          <div className="space-y-2">
            {components.slice(0, 5).map((comp, i) => {
              const maxYoy = Math.max(...components.map(c => Math.abs(c.yoy_pct || 0)), 1);
              const yoy = comp.yoy_pct || 0;
              return (
                <div key={i} className="flex items-center gap-2">
                  <div className="w-32 text-xs text-gray-600 truncate" title={comp.name}>{comp.name}</div>
                  <div className="flex-1 h-4 bg-gray-100 rounded relative overflow-hidden">
                    <div
                      className={`absolute h-full rounded ${yoy >= 0 ? 'bg-purple-500' : 'bg-red-400'}`}
                      style={{ width: `${(Math.abs(yoy) / maxYoy) * 100}%` }}
                    />
                  </div>
                  <div className={`w-14 text-xs font-medium text-right ${yoy >= 0 ? 'text-purple-600' : 'text-red-500'}`}>
                    {yoy >= 0 ? '+' : ''}{yoy.toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="h-40 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeline} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                <defs>
                  <linearGradient id="wpGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={35} tickFormatter={(v) => `${v}%`} />
                <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }} formatter={(value: number) => [`${value?.toFixed(2)}%`]} />
                <Area type="monotone" dataKey="final_demand_yoy" stroke="#8b5cf6" fill="url(#wpGradient)" strokeWidth={2} name="Final Demand" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}

// Color scale for unemployment rates (matching LAExplorer)
function getColorFromRate(rate: number): string {
  if (rate < 3) return '#16a34a'; // green-600
  if (rate < 4) return '#4ade80'; // green-400
  if (rate < 5) return '#fbbf24'; // amber-400
  if (rate < 6) return '#fb923c'; // orange-400
  if (rate < 7) return '#f87171'; // red-400
  return '#dc2626'; // red-600
}

function LASlide({ data }: { data: CarouselData['la'] }) {
  const { states: statesData } = data;
  const states = statesData?.states || [];
  const rankings = statesData?.rankings;

  // Sort states by unemployment rate for sidebar display
  const sortedStates = [...states]
    .filter(s => s.unemployment_rate != null)
    .sort((a, b) => (b.unemployment_rate || 0) - (a.unemployment_rate || 0));

  const highestStates = sortedStates.slice(0, 3);
  const lowestStates = sortedStates.slice(-3).reverse();

  return (
    <div className="grid grid-cols-3 gap-3 h-full">
      {/* Rankings sidebar */}
      <div className="space-y-2">
        <div className="bg-red-50 rounded-lg p-2 border border-red-100">
          <div className="text-[10px] text-red-700 font-medium mb-1">Highest Rates</div>
          {(rankings?.highest || highestStates.map(s => `${s.area_name}: ${s.unemployment_rate?.toFixed(1)}%`)).slice(0, 3).map((name, i) => (
            <div key={i} className="text-xs text-gray-700 truncate">{i + 1}. {name}</div>
          ))}
        </div>
        <div className="bg-green-50 rounded-lg p-2 border border-green-100">
          <div className="text-[10px] text-green-700 font-medium mb-1">Lowest Rates</div>
          {(rankings?.lowest || lowestStates.map(s => `${s.area_name}: ${s.unemployment_rate?.toFixed(1)}%`)).slice(0, 3).map((name, i) => (
            <div key={i} className="text-xs text-gray-700 truncate">{i + 1}. {name}</div>
          ))}
        </div>
        {/* Color legend */}
        <div className="text-[9px] text-gray-500">
          <div className="flex flex-wrap gap-1">
            {[
              { label: '<3%', color: '#16a34a' },
              { label: '3-4%', color: '#4ade80' },
              { label: '4-5%', color: '#fbbf24' },
              { label: '5-6%', color: '#fb923c' },
              { label: '>6%', color: '#dc2626' },
            ].map(item => (
              <div key={item.label} className="flex items-center gap-0.5">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="col-span-2 h-full min-h-[180px]">
        {states.length > 0 ? (
          <div className="h-full rounded-lg overflow-hidden border border-gray-200">
            <MapContainer
              center={[39.8283, -98.5795]}
              zoom={3}
              minZoom={2}
              maxZoom={6}
              maxBounds={US_BOUNDS as LatLngBoundsExpression}
              style={{ height: '100%', width: '100%', background: '#f5f5f5' }}
              scrollWheelZoom={false}
              dragging={false}
              zoomControl={false}
              attributionControl={false}
            >
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
              />

              {/* State markers */}
              {states.map(state => {
                const coords = getLAAreaCoordinates(state.area_code, state.area_name);
                if (!coords) return null;
                const rate = state.unemployment_rate || 0;

                return (
                  <CircleMarker
                    key={state.area_code}
                    center={[coords.lat, coords.lng]}
                    radius={6}
                    fillColor={getColorFromRate(rate)}
                    color="#1976d2"
                    weight={1}
                    fillOpacity={0.9}
                  >
                    <Popup>
                      <div className="text-xs">
                        <p className="font-semibold">{state.area_name}</p>
                        <p>Unemployment: {rate.toFixed(1)}%</p>
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center text-gray-500">
              <Building2 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm">Loading state data...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function PCSlide({ data }: { data: CarouselData['pc'] }) {
  const { overview } = data;
  const sectors = overview?.sectors || [];
  // Sort by YoY change for display
  const sortedSectors = [...sectors]
    .filter(s => s.yoy_pct != null)
    .sort((a, b) => Math.abs(b.yoy_pct || 0) - Math.abs(a.yoy_pct || 0))
    .slice(0, 6);

  // Get latest date from first sector
  const latestDate = sectors[0]?.latest_date;

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {/* Summary metrics */}
      <div className="space-y-3">
        <div className="bg-cyan-50 rounded-lg p-3 border border-cyan-100">
          <div className="text-xs text-gray-500 mb-1">PPI by Industry</div>
          <div className="text-2xl font-bold text-gray-900">
            {sectors.length > 0 ? `${sectors.length} Sectors` : '--'}
          </div>
          <div className="text-xs text-gray-500">tracked</div>
        </div>
        <div className="text-xs text-gray-400 text-center">
          {latestDate || 'Latest data'}
        </div>
        <div className="text-xs text-gray-500 p-2 bg-gray-50 rounded">
          Producer prices by NAICS industry classification. Shows YoY % change.
        </div>
      </div>

      {/* Sector breakdown */}
      <div className="col-span-2">
        <div className="text-xs font-medium text-gray-600 mb-2">Sectors by YoY Change</div>
        {sortedSectors.length > 0 ? (
          <div className="space-y-2">
            {sortedSectors.map((sector, i) => {
              const maxYoy = Math.max(...sortedSectors.map(s => Math.abs(s.yoy_pct || 0)), 1);
              const yoy = sector.yoy_pct || 0;
              return (
                <div key={i} className="flex items-center gap-2">
                  <div className="w-32 text-xs text-gray-600 truncate" title={sector.sector_name}>{sector.sector_name}</div>
                  <div className="flex-1 h-4 bg-gray-100 rounded relative overflow-hidden">
                    <div
                      className={`absolute h-full rounded ${yoy >= 0 ? 'bg-cyan-500' : 'bg-red-400'}`}
                      style={{ width: `${(Math.abs(yoy) / maxYoy) * 100}%` }}
                    />
                  </div>
                  <div className={`w-14 text-xs font-medium text-right ${yoy >= 0 ? 'text-cyan-600' : 'text-red-500'}`}>
                    {yoy >= 0 ? '+' : ''}{yoy.toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="h-40 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <Truck className="w-10 h-10 text-cyan-400 mx-auto mb-2" />
              <div className="text-sm text-gray-600">Industry-level PPI data</div>
              <Link to="/research/bls/pc" className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">
                Explore all industries →
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Main carousel component
function SurveyCarousel({ data }: { data: CarouselData }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const autoRotateInterval = 8000; // 8 seconds

  // Auto-rotate
  useEffect(() => {
    if (isPaused || data.loading) return;

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % SURVEY_CONFIGS.length);
    }, autoRotateInterval);

    return () => clearInterval(timer);
  }, [isPaused, data.loading]);

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  const goToPrev = () => {
    setCurrentIndex((prev) => (prev - 1 + SURVEY_CONFIGS.length) % SURVEY_CONFIGS.length);
  };

  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % SURVEY_CONFIGS.length);
  };

  const currentSurvey = SURVEY_CONFIGS[currentIndex];
  const SurveyIcon = currentSurvey.icon;

  // Render the appropriate slide based on current index
  const renderSlide = () => {
    if (data.loading) {
      return (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      );
    }

    switch (currentSurvey.id) {
      case 'ln':
        return <LNSlide data={data.ln} />;
      case 'ce':
        return <CESlide data={data.ce} />;
      case 'jt':
        return <JTSlide data={data.jt} />;
      case 'cu':
        return <CUSlide data={data.cu} />;
      case 'wp':
        return <WPSlide data={data.wp} />;
      case 'la':
        return <LASlide data={data.la} />;
      case 'pc':
        return <PCSlide data={data.pc} />;
      default:
        return null;
    }
  };

  return (
    <div
      className="bg-white rounded-lg border border-gray-200 overflow-hidden"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Header */}
      <div className={`px-4 py-3 bg-gradient-to-r ${currentSurvey.bgGradient} border-b border-gray-100 flex items-center justify-between`}>
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: currentSurvey.color }}
          >
            <SurveyIcon className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-gray-500">{currentSurvey.name}</span>
              <h3 className="font-semibold text-gray-900 text-sm">{currentSurvey.fullName}</h3>
            </div>
            <p className="text-xs text-gray-500">{currentSurvey.description}</p>
          </div>
        </div>

        {/* Navigation Arrows */}
        <div className="flex items-center gap-2">
          <button
            onClick={goToPrev}
            className="p-1 rounded hover:bg-white/50 text-gray-500 hover:text-gray-700 transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={goToNext}
            className="p-1 rounded hover:bg-white/50 text-gray-500 hover:text-gray-700 transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
          <Link
            to={`/research/bls/${currentSurvey.id}`}
            className="ml-2 text-xs text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1"
          >
            Full Explorer <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 min-h-[220px]">
        {renderSlide()}
      </div>

      {/* Dot Navigation */}
      <div className="px-4 pb-3 flex items-center justify-center gap-1.5">
        {SURVEY_CONFIGS.map((survey, index) => (
          <button
            key={survey.id}
            onClick={() => goToSlide(index)}
            className={`transition-all duration-200 ${
              index === currentIndex
                ? 'w-6 h-2 rounded-full'
                : 'w-2 h-2 rounded-full hover:scale-125'
            }`}
            style={{
              backgroundColor: index === currentIndex ? currentSurvey.color : '#d1d5db',
            }}
            title={survey.fullName}
          />
        ))}
      </div>
    </div>
  );
}

function MarketImpactStrip() {
  const impacts = [
    { event: 'Strong Payrolls', sector: 'Financials', ticker: 'XLF', impact: 'positive', reason: 'Rate cut bets support NIM' },
    { event: 'Curve Steepening', sector: 'Reg Banks', ticker: 'KRE', impact: 'positive', reason: 'NIM expansion' },
    { event: 'Sticky Core CPI', sector: 'Growth', ticker: 'VUG', impact: 'negative', reason: 'Duration headwind' },
    { event: 'JOLTS Cooling', sector: 'Staffing', ticker: 'RHI', impact: 'negative', reason: 'Hiring slowdown' },
  ];

  return (
    <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Target className="w-4 h-4 text-indigo-400" />
        <h3 className="font-semibold text-white text-sm">Market Impact Summary</h3>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {impacts.map((item, i) => (
          <div key={i} className="bg-white/10 rounded-lg p-3">
            <div className="text-[10px] text-gray-400 mb-1">{item.event}</div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-white">{item.sector}</span>
              <span className="text-xs text-gray-400">({item.ticker})</span>
            </div>
            <div className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${item.impact === 'positive' ? 'bg-emerald-400' : 'bg-red-400'}`} />
              <span className="text-[10px] text-gray-300">{item.reason}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function Research(): React.ReactElement {
  // Carousel data state for all 7 BLS surveys
  const [carouselData, setCarouselData] = useState<CarouselData>({
    ln: { overview: null, timeline: [] },
    ce: { overview: null, timeline: [], supersectors: [] },
    cu: { overview: null, timeline: [] },
    la: { states: null },
    wp: { overview: null, timeline: [] },
    pc: { overview: null },
    jt: { overview: null, timeline: [] },
    loading: true,
  });

  // Fetch all survey data for carousel on mount
  useEffect(() => {
    const fetchCarouselData = async () => {
      try {
        // Fetch all surveys in parallel
        const [
          lnOverviewRes, lnTimelineRes,
          ceOverviewRes, ceSupersectorsRes,
          cuOverviewRes, cuTimelineRes,
          laStatesRes,
          wpOverviewRes, wpTimelineRes,
          pcOverviewRes,
          jtOverviewRes, jtTimelineRes,
        ] = await Promise.all([
          // LN - Labor Force Statistics
          lnResearchAPI.getOverview<LNOverviewData>(),
          lnResearchAPI.getOverviewTimeline<{ timeline: LNTimelinePoint[] }>(24),
          // CE - Employment Situation
          ceResearchAPI.getOverview<CEOverviewData>(),
          ceResearchAPI.getSupersectors<{ supersectors: SupersectorItem[] }>(),
          // CU - Consumer Prices (CPI)
          cuResearchAPI.getOverview<CUOverviewData>(),
          cuResearchAPI.getOverviewTimeline<{ timeline: CUTimelinePoint[] }>('0000', 24),
          // LA - Local Area Unemployment (states for map view)
          laResearchAPI.getStates<LAStatesData>(),
          // WP - Producer Prices (PPI)
          wpResearchAPI.getOverview<WPOverviewData>(),
          wpResearchAPI.getOverviewTimeline<{ timeline: WPTimelinePoint[] }>(24),
          // PC - PPI by Industry
          pcResearchAPI.getOverview<PCOverviewData>(),
          // JT - JOLTS
          jtResearchAPI.getOverview<JTOverviewData>(),
          jtResearchAPI.getOverviewTimeline<{ timeline: JTTimelinePoint[] }>('000000', '00', 24),
        ]);

        setCarouselData({
          ln: {
            overview: lnOverviewRes.data,
            timeline: lnTimelineRes.data?.timeline || [],
          },
          ce: {
            overview: ceOverviewRes.data,
            timeline: [],
            supersectors: ceSupersectorsRes.data?.supersectors || [],
          },
          cu: {
            overview: cuOverviewRes.data,
            timeline: cuTimelineRes.data?.timeline || [],
          },
          la: {
            states: laStatesRes.data,
          },
          wp: {
            overview: wpOverviewRes.data,
            timeline: wpTimelineRes.data?.timeline || [],
          },
          pc: {
            overview: pcOverviewRes.data,
          },
          jt: {
            overview: jtOverviewRes.data,
            timeline: jtTimelineRes.data?.timeline || [],
          },
          loading: false,
        });
      } catch (error) {
        console.error('Failed to fetch carousel data:', error);
        setCarouselData(prev => ({ ...prev, loading: false }));
      }
    };

    fetchCarouselData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Market Ticker */}
      <MarketTickerBar />

      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-[1800px] mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-bold text-gray-900">Macro Impact Lab</h1>
              <p className="text-xs text-gray-500">Economic research & market analysis</p>
            </div>
            <div className="flex items-center gap-3">
              <nav className="flex items-center gap-1">
                {['Overview', 'Labor', 'Inflation', 'GDP', 'Treasury', 'Fed'].map((item, i) => (
                  <button
                    key={item}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                      i === 0 ? 'bg-indigo-100 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {item}
                  </button>
                ))}
              </nav>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1800px] mx-auto px-6 py-4">
        {/* Market Impact Strip */}
        <div className="mb-4">
          <MarketImpactStrip />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-4">
          {/* Left Column - Survey Carousel & Other Data */}
          <div className="col-span-8 space-y-4">
            {/* ROW 1: BLS Survey Carousel */}
            <SurveyCarousel data={carouselData} />

            {/* Employment & Inflation Row */}
            <div className="grid grid-cols-2 gap-4">
              <EmploymentTabbedCard />
              <InflationCard />
            </div>

            {/* GDP & Auctions Row */}
            <div className="grid grid-cols-2 gap-4">
              <GDPCard />
              <AuctionResultsCard />
            </div>

            {/* Data Explorers */}
            <DataExplorerGrid />
          </div>

          {/* Right Column - Yield Curve & Calendar */}
          <div className="col-span-4 space-y-4">
            <YieldCurveCard />
            <CalendarCard />

            {/* Quick Stats */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 text-sm mb-3">Key Spreads & Rates</h3>
              <div className="space-y-3">
                {[
                  { label: '2s10s Spread', value: '+3 bps', note: 'First positive since Jul 2022', positive: true },
                  { label: 'Fed Funds Target', value: '4.50-4.75%', note: '85% odds of Dec cut', positive: false },
                  { label: '10Y Real Yield', value: '1.92%', note: 'TIPS-implied', positive: false },
                  { label: '10Y Breakeven', value: '2.26%', note: 'Inflation expectations', positive: false },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <div>
                      <div className="text-xs text-gray-600">{item.label}</div>
                      <div className="text-[10px] text-gray-400">{item.note}</div>
                    </div>
                    <div className={`text-sm font-semibold ${item.positive ? 'text-emerald-600' : 'text-gray-900'}`}>
                      {item.value}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Coming Soon */}
            <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-700 text-sm mb-2">Coming Soon</h3>
              <div className="space-y-2 text-xs text-gray-500">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-3 h-3" />
                  <span>FRED Financial Conditions</span>
                </div>
                <div className="flex items-center gap-2">
                  <PieChart className="w-3 h-3" />
                  <span>Options Flow & Gamma</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="w-3 h-3" />
                  <span>Market Breadth & Flows</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-6">
        <div className="max-w-[1800px] mx-auto px-6 py-3">
          <p className="text-[10px] text-gray-400">
            Data: BLS, U.S. Treasury, BEA, Federal Reserve. For informational purposes only.
          </p>
        </div>
      </footer>
    </div>
  );
}
