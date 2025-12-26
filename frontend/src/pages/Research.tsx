import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useQueries } from '@tanstack/react-query';
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
  treasuryResearchAPI,
  fredResearchAPI,
  claimsResearchAPI,
  marketResearchAPI,
  economicCalendarAPI,
  beaResearchAPI,
  fredCalendarAPI,
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

// Market indices now fetched from real API in MarketTickerBar
// Treasury yields now fetched from real API in YieldCurveCard and MarketTickerBar

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

// inflationData removed - replaced with ClaimsCard using real FRED data

// GDP data is now fetched from real NIPA API in GDPCard component

// Economic calendar events now fetched from real API in CalendarCard

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
  const [indicesData, setIndicesData] = useState<MarketIndicesData | null>(null);

  // Use React Query for FRED data - shared cache across components
  const { data: fredData } = useQuery({
    queryKey: ['fred-yield-curve'],
    queryFn: async () => {
      const res = await fredResearchAPI.getYieldCurve<FredYieldCurveData>();
      return res.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes - FRED data doesn't change often
    gcTime: 30 * 60 * 1000, // Keep in cache for 30 min
  });

  // Use React Query for indices data
  const { data: initialIndices } = useQuery({
    queryKey: ['market-indices'],
    queryFn: async () => {
      const res = await marketResearchAPI.getIndices<MarketIndicesData>();
      return res.data;
    },
    staleTime: 30 * 1000, // 30 seconds for market data
  });

  // Update indicesData from query or WebSocket
  useEffect(() => {
    if (initialIndices && !indicesData) {
      setIndicesData(initialIndices);
    }
  }, [initialIndices, indicesData]);

  useEffect(() => {

    // Connect to WebSocket for real-time updates
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname === 'localhost' ? 'localhost:8000' : 'api.finexus.net';
    const wsUrl = `${wsProtocol}//${wsHost}/api/research/market/ws/indices`;

    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    const connectWebSocket = () => {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected for real-time indices');
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'indices_update' && message.data) {
            // Convert WebSocket data to MarketIndicesData format
            const indices = Object.entries(message.data).map(([symbol, data]: [string, any]) => ({
              symbol,
              name: { '^GSPC': 'S&P 500', '^IXIC': 'Nasdaq', '^DJI': 'DJIA', '^RUT': 'Russell 2000' }[symbol] || symbol,
              price: data.price,
              change: data.change,
              change_pct: data.change_pct,
              date: null,
              sparkline: [],
              source: data.source,
              is_realtime: data.source === 'realtime',
            }));

            setIndicesData(prev => ({
              as_of: message.timestamp || new Date().toISOString(),
              market_status: message.market_status || prev?.market_status || 'unknown',
              indices: indices.length > 0 ? indices : (prev?.indices || []),
            }));
          } else if (message.type === 'ping') {
            // Respond to ping with pong
            ws?.send(JSON.stringify({ type: 'pong' }));
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected, reconnecting in 5s...');
        reconnectTimeout = setTimeout(connectWebSocket, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, []);

  // Get 10Y yield for display
  const yield10Y = fredData?.curve?.find(d => d.tenor === '10Y');

  // Get spreads from FRED data
  const spread2s10s = fredData?.spreads?.['2s10s'];
  const isSpreadPositive = spread2s10s != null && spread2s10s > 0;

  // Market status indicator
  const marketStatus = indicesData?.market_status;
  const isRealtime = indicesData?.indices?.some(idx => idx.is_realtime);

  return (
    <div className="bg-gray-900 text-white">
      <div className="max-w-[1800px] mx-auto">
        <div className="flex items-center divide-x divide-gray-700 overflow-x-auto">
          {/* Market Status Indicator */}
          <div className="flex items-center gap-2 px-4 py-2 min-w-fit">
            <div className={`w-2 h-2 rounded-full ${
              marketStatus === 'open' ? 'bg-green-500 animate-pulse' :
              marketStatus === 'pre-market' ? 'bg-yellow-500' :
              marketStatus === 'after-hours' ? 'bg-orange-500' :
              'bg-gray-500'
            }`} />
            <span className="text-[10px] text-gray-400 uppercase">
              {marketStatus === 'open' ? (isRealtime ? 'Live' : 'Open') :
               marketStatus === 'pre-market' ? 'Pre-Mkt' :
               marketStatus === 'after-hours' ? 'After-Hrs' :
               'Closed'}
            </span>
          </div>
          {indicesData?.indices?.map((idx, i) => (
            <div key={i} className="flex items-center gap-3 px-4 py-2 min-w-fit">
              <div>
                <div className="text-[10px] text-gray-400 uppercase tracking-wide">{idx.name}</div>
                <div className="text-sm font-medium">
                  {idx.price != null ? idx.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '--'}
                </div>
              </div>
              {idx.sparkline && idx.sparkline.length > 0 && (
                <MiniSparkline data={idx.sparkline} color="auto" width={50} height={20} />
              )}
              {idx.change_pct != null && <ChangeIndicator value={idx.change_pct} />}
            </div>
          ))}
          <div className="flex items-center gap-3 px-4 py-2 min-w-fit">
            <div>
              <div className="text-[10px] text-gray-400 uppercase tracking-wide">10Y Yield</div>
              <div className="text-sm font-medium">
                {yield10Y?.yield != null ? `${yield10Y.yield.toFixed(2)}%` : '--'}
              </div>
            </div>
            {yield10Y?.daily_change_bps != null && (
              <ChangeIndicator value={yield10Y.daily_change_bps} suffix=" bp" />
            )}
          </div>
          <div className="flex items-center gap-3 px-4 py-2 min-w-fit">
            <div>
              <div className="text-[10px] text-gray-400 uppercase tracking-wide">2s10s</div>
              <div className={`text-sm font-medium ${isSpreadPositive ? 'text-emerald-400' : 'text-red-400'}`}>
                {spread2s10s != null ? `${isSpreadPositive ? '+' : ''}${spread2s10s} bp` : '--'}
              </div>
            </div>
            {spread2s10s != null && (
              <span className="text-[10px] text-gray-500">
                {isSpreadPositive ? 'Curve normal' : 'Curve inverted'}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// FRED Release Calendar Card for Research Portal
interface FredCalendarRelease {
  release_id: number;
  release_name: string;
  release_date: string;
  series_count: number;
}

interface FredCalendarWeekData {
  week_start: string;
  week_end: string;
  total_releases: number;
  releases_by_date: Record<string, FredCalendarRelease[]>;
  releases: FredCalendarRelease[];
}

function FREDCalendarCard() {
  // Fetch this week's releases
  const { data: weekData, isLoading: loading } = useQuery({
    queryKey: ['fred-calendar-week'],
    queryFn: async () => {
      const res = await fredCalendarAPI.getWeek<FredCalendarWeekData>();
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });

  const releases: FredCalendarRelease[] = weekData?.releases || [];

  // Group by date
  const byDate: Record<string, FredCalendarRelease[]> = {};
  releases.forEach((r: FredCalendarRelease) => {
    if (!byDate[r.release_date]) byDate[r.release_date] = [];
    byDate[r.release_date].push(r);
  });

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T12:00:00');
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  // Check if date is today
  const isToday = (dateStr: string) => {
    const today = new Date().toISOString().split('T')[0];
    return dateStr === today;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-indigo-500" />
          <h3 className="font-semibold text-gray-900 text-sm">FRED Release Calendar</h3>
        </div>
        <Link
          to="/research/fred-calendar"
          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
        >
          View All →
        </Link>
      </div>
      <div className="p-4 min-h-[320px]">
        {loading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-16 bg-gray-100 rounded-lg"></div>
            <div className="h-16 bg-gray-100 rounded-lg"></div>
            <div className="h-16 bg-gray-100 rounded-lg"></div>
          </div>
        ) : releases.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-12">No releases this week</p>
        ) : (
          <div className="space-y-3">
            {Object.entries(byDate).slice(0, 6).map(([date, items]) => (
              <div
                key={date}
                className={`p-3 rounded-lg border ${
                  isToday(date)
                    ? 'bg-indigo-50 border-indigo-300 shadow-sm'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className={`text-xs font-bold mb-2 flex items-center gap-2 ${isToday(date) ? 'text-indigo-700' : 'text-gray-600'}`}>
                  {formatDate(date)}
                  {isToday(date) && (
                    <span className="px-2 py-0.5 bg-indigo-500 text-white rounded text-[10px] font-semibold">TODAY</span>
                  )}
                </div>
                <div className="space-y-1.5">
                  {items.slice(0, 4).map((r, i) => (
                    <div key={i} className="flex justify-between items-center py-0.5">
                      <span className="text-sm text-gray-800 truncate mr-3">{r.release_name}</span>
                      <span className="text-xs text-gray-500 bg-white px-1.5 py-0.5 rounded border border-gray-200">{r.series_count}</span>
                    </div>
                  ))}
                  {items.length > 4 && (
                    <div className="text-xs text-gray-500 pt-1">+{items.length - 4} more releases</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="mt-4 pt-3 border-t border-gray-100 text-center">
          <span className="text-sm font-medium text-gray-600">
            {weekData?.total_releases || 0} releases scheduled this week
          </span>
        </div>
      </div>
    </div>
  );
}

function YieldCurveCard() {
  // Use React Query with same key as MarketTickerBar - automatic deduplication!
  const { data: curveData, isLoading: loading } = useQuery({
    queryKey: ['fred-yield-curve'],
    queryFn: async () => {
      const res = await fredResearchAPI.getYieldCurve<FredYieldCurveData>();
      return res.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000,
  });

  // Build chart data from FRED curve
  const chartData = curveData?.curve?.filter(p => p.yield !== null).map(p => ({
    tenor: p.tenor,
    yield: p.yield,
  })) || [];

  // Key yields to display (2Y, 5Y, 10Y, 30Y)
  const keyTenors = ['2Y', '5Y', '10Y', '30Y'];
  const keyYields = keyTenors.map(tenor => {
    const point = curveData?.curve?.find(p => p.tenor === tenor);
    return {
      tenor,
      yield: point?.yield,
      change: point?.daily_change_bps,
    };
  });

  // Format date
  const asOfDate = curveData?.as_of_date;
  const formattedDate = asOfDate ? new Date(asOfDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '';

  // Calculate Y-axis domain
  const yields = chartData.map(d => d.yield).filter((y): y is number => y !== null);
  const minYield = yields.length > 0 ? Math.floor(Math.min(...yields) * 10) / 10 - 0.2 : 3.0;
  const maxYield = yields.length > 0 ? Math.ceil(Math.max(...yields) * 10) / 10 + 0.2 : 5.0;

  // Get key spreads
  const spread2s10s = curveData?.spreads?.['2s10s'];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <h3 className="font-medium text-gray-700 text-xs">Treasury Yield Curve</h3>
          {spread2s10s !== undefined && (
            <span className={`text-[9px] px-1.5 py-0.5 rounded ${
              spread2s10s >= 0 ? 'bg-teal-50 text-teal-600' : 'bg-rose-50 text-rose-600'
            }`}>
              2s10s {spread2s10s >= 0 ? '+' : ''}{spread2s10s}bp
            </span>
          )}
        </div>
        {formattedDate && (
          <span className="text-[9px] text-gray-400">{formattedDate}</span>
        )}
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-56">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* Chart - More prominent */}
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 8, right: 8, bottom: 5, left: 0 }}>
                <defs>
                  <linearGradient id="yieldCurveGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="50%" stopColor="#34d399" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#6ee7b7" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="tenor"
                  tick={{ fontSize: 9, fill: '#6b7280' }}
                  axisLine={false}
                  tickLine={false}
                  interval={0}
                />
                <YAxis
                  domain={[minYield, maxYield]}
                  tick={{ fontSize: 9, fill: '#9ca3af' }}
                  axisLine={false}
                  tickLine={false}
                  width={32}
                  tickFormatter={(v) => `${v.toFixed(1)}%`}
                />
                <Tooltip
                  contentStyle={{
                    fontSize: 11,
                    borderRadius: 8,
                    border: 'none',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                    padding: '8px 12px'
                  }}
                  formatter={(value: number) => [`${value?.toFixed(3)}%`, 'Yield']}
                  labelFormatter={(label) => `${label} Treasury`}
                />
                <Area
                  type="monotone"
                  dataKey="yield"
                  stroke="#059669"
                  fill="url(#yieldCurveGradient)"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 4, fill: '#059669', stroke: '#fff', strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Key Yields - Compact inline */}
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100 px-1">
            {keyYields.map((y, i) => (
              <div key={i} className="text-center">
                <span className="text-[10px] text-gray-400">{y.tenor}</span>
                <span className="text-xs text-gray-600 ml-1">
                  {y.yield != null ? `${y.yield.toFixed(2)}%` : '--'}
                </span>
                {y.change != null && y.change !== 0 && (
                  <span className={`text-[9px] ml-0.5 ${y.change > 0 ? 'text-rose-500' : 'text-teal-500'}`}>
                    {y.change > 0 ? '↑' : '↓'}
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Link to Yield Curve Explorer */}
          <Link to="/research/yield-curve" className="block mt-2 pt-2 text-center text-xs text-indigo-600 hover:text-indigo-700 font-medium border-t border-gray-100">
            Yield Curve Explorer →
          </Link>
        </>
      )}
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
void TrendBadge;

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

// Types for Claims Card
interface ClaimsSeriesData {
  series_id: string;
  name: string;
  value: number;
  date: string;
  prior_value: number | null;
  wow_change: number | null;
  wow_pct: number | null;
  year_ago_value: number | null;
  yoy_change: number | null;
  yoy_pct: number | null;
}

interface ClaimsOverviewData {
  claims: {
    icsa?: ClaimsSeriesData;
    ccsa?: ClaimsSeriesData;
    ic4wsa?: ClaimsSeriesData;
  };
}

interface ClaimsTimelineData {
  timeline: { date: string; icsa: number | null; ic4wsa: number | null }[];
}

function ClaimsCard() {
  // Fetch claims overview
  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['claims-overview'],
    queryFn: async () => {
      const res = await claimsResearchAPI.getOverview<ClaimsOverviewData>();
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Fetch claims timeline for chart
  const { data: timeline } = useQuery({
    queryKey: ['claims-timeline-short'],
    queryFn: async () => {
      const res = await claimsResearchAPI.getTimeline<ClaimsTimelineData>(52);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const formatNumber = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '--';
    if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
    return value.toLocaleString();
  };

  const formatChange = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '';
    const sign = value >= 0 ? '+' : '';
    if (Math.abs(value) >= 1000) return `${sign}${(value / 1000).toFixed(0)}K`;
    return `${sign}${value.toLocaleString()}`;
  };

  const icsa = overview?.claims?.icsa;
  const ic4wsa = overview?.claims?.ic4wsa;
  const ccsa = overview?.claims?.ccsa;

  // Prepare chart data
  const chartData = timeline?.timeline?.map(t => ({
    date: new Date(t.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    icsa: t.icsa,
    ic4wsa: t.ic4wsa,
  })) || [];

  // For claims, up is bad (more unemployment)
  const icsaTrendColor = (icsa?.wow_change ?? 0) > 0 ? 'text-red-500' : 'text-green-500';
  const TrendIcon = (icsa?.wow_change ?? 0) > 0 ? TrendingUp : TrendingDown;

  if (loadingOverview) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4 min-h-[400px] flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 min-h-[400px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-amber-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Unemployment Claims</h3>
        </div>
        <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded font-medium">Weekly</span>
      </div>

      {/* Headline Numbers */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="bg-indigo-50 rounded-lg p-2">
          <div className="text-[10px] text-gray-500 uppercase">Initial Claims</div>
          <div className="text-lg font-bold text-gray-900">{formatNumber(icsa?.value)}</div>
          <div className="flex items-center gap-1 text-xs">
            <TrendIcon className={`w-3 h-3 ${icsaTrendColor}`} />
            <span className={icsaTrendColor}>{formatChange(icsa?.wow_change)}</span>
          </div>
        </div>
        <div className="bg-amber-50 rounded-lg p-2">
          <div className="text-[10px] text-gray-500 uppercase">4-Week MA</div>
          <div className="text-lg font-bold text-gray-900">{formatNumber(ic4wsa?.value)}</div>
          <div className="text-xs text-gray-500">Trend</div>
        </div>
        <div className="bg-emerald-50 rounded-lg p-2">
          <div className="text-[10px] text-gray-500 uppercase">Continued</div>
          <div className="text-lg font-bold text-gray-900">{formatNumber(ccsa?.value)}</div>
          <div className="flex items-center gap-1 text-xs">
            <span className={(ccsa?.wow_change ?? 0) > 0 ? 'text-red-500' : 'text-green-500'}>
              {formatChange(ccsa?.wow_change)}
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-44 mb-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
            <defs>
              <linearGradient id="claimsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="date"
              tick={{ fontSize: 9 }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 9 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`}
              domain={['auto', 'auto']}
            />
            <Tooltip
              contentStyle={{ fontSize: 11, borderRadius: 6 }}
              formatter={(value: number) => [value?.toLocaleString(), '']}
            />
            <Area
              type="monotone"
              dataKey="icsa"
              stroke="#6366f1"
              strokeWidth={2}
              fill="url(#claimsGradient)"
              name="Initial Claims"
            />
            <Line
              type="monotone"
              dataKey="ic4wsa"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              name="4-Week MA"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
        <span className="text-[10px] text-gray-400">
          {icsa?.date ? `As of ${new Date(icsa.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}` : ''}
        </span>
        <Link to="/research/claims" className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
          Explore <ChevronRight className="w-3 h-3" />
        </Link>
      </div>
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

// Treasury Interfaces
interface TreasuryAuctionItem {
  auction_id: number;
  cusip: string;
  auction_date: string;
  security_type: string;
  security_term: string;
  offering_amount: number | null;
  bid_to_cover_ratio: number | null;
  high_yield: number | null;
  coupon_rate: number | null;
  tail_bps: number | null;
  auction_result: string | null;
}

// FRED Yield Curve Interfaces
interface FredYieldCurvePoint {
  tenor: string;
  series_id: string;
  yield: number | null;
  date: string | null;
  source: string | null;
  daily_change_bps: number | null;
  weekly_change_bps: number | null;
  monthly_change_bps: number | null;
}

interface FredYieldCurveData {
  as_of_date: string;
  curve: FredYieldCurvePoint[];
  spreads: {
    '2s10s'?: number;
    '2s30s'?: number;
    '5s30s'?: number;
    '3m10y'?: number;
  };
  tips_real_yields: Array<{ tenor: string; real_yield: number }>;
  breakeven_inflation: Array<{ tenor: string; breakeven: number }>;
}

// Market Indices types
interface MarketIndex {
  symbol: string;
  name: string;
  price: number | null;
  change: number | null;
  change_pct: number | null;
  date: string | null;
  sparkline: number[];
  source: string | null;
  is_realtime: boolean;
}

interface MarketIndicesData {
  as_of: string;
  market_status: string;
  indices: MarketIndex[];
}

// Economic Calendar types
interface EconomicCalendarEvent {
  date: string;
  time: string;
  datetime: string;
  name: string;
  country: string;
  source: string;
  impact: string | null;
  importance: number;
  previous: number | null;
  estimate: number | null;
  actual: number | null;
}

interface EconomicCalendarData {
  as_of: string;
  count: number;
  data_source?: string;  // "upcoming" or "recent"
  events: EconomicCalendarEvent[];
}

type EmploymentTabType = 'sectors' | 'earnings' | 'jolts';

function EmploymentTabbedCard() {
  const [activeTab, setActiveTab] = useState<EmploymentTabType>('sectors');

  // Use React Query for supersectors - shared cache
  const { data: supersectors } = useQuery({
    queryKey: ['ce-supersectors'],
    queryFn: async () => {
      const res = await ceResearchAPI.getSupersectors<CESupersectorsData>();
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // CE Timeline
  const { data: ceTimeline } = useQuery({
    queryKey: ['ce-supersectors-timeline'],
    queryFn: async () => {
      const res = await ceResearchAPI.getSupersectorsTimeline<CESupersectorTimelineData>({
        supersector_codes: '05,06,07,08,10,20,30,40,41,42,43,50,55,60,65,70,80,90',
        months_back: 60
      });
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Earnings
  const { data: earnings } = useQuery({
    queryKey: ['ce-earnings'],
    queryFn: async () => {
      const res = await ceResearchAPI.getEarnings<CEEarningsData>({ limit: 15 });
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // JOLTS Timeline
  const { data: jtTimeline, isLoading: loading } = useQuery({
    queryKey: ['jt-timeline-overview'],
    queryFn: async () => {
      const res = await jtResearchAPI.getOverviewTimeline<JTTimelineDataCard>('000000', '00', 60);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

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
    .slice(0, 12) || [];

  // Top earnings industries
  const topEarnings = earnings?.earnings?.slice(0, 12) || [];

  const tabs: { id: EmploymentTabType; label: string }[] = [
    { id: 'sectors', label: 'Sectors' },
    { id: 'earnings', label: 'Wages' },
    { id: 'jolts', label: 'JOLTS' },
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden min-h-[400px]">
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
          <div className="flex items-center justify-center h-[340px]">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : activeTab === 'sectors' ? (
          <div className="overflow-x-auto max-h-[340px]">
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
          <div className="overflow-x-auto max-h-[340px]">
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
          <div className="overflow-x-auto max-h-[340px]">
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

interface GDPHeadlineData {
  current: {
    value: number | null;
    prior: number | null;
    period: string | null;
    unit: string;
  };
  components: Array<{
    name: string;
    contribution: number;
    pct: number;
  }>;
  trend: Array<{
    q: string;
    period: string;
    value: number | null;
  }>;
}

function GDPCard() {
  // Use React Query for GDP headline data
  const { data: gdpData, isLoading: loading, error } = useQuery({
    queryKey: ['nipa-headline'],
    queryFn: async () => {
      const response = await beaResearchAPI.getNIPAHeadline<GDPHeadlineData>();
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes - GDP data updates infrequently
    gcTime: 60 * 60 * 1000, // Keep in cache for 1 hour
  });

  // Format period like "2024Q3" to "Q3 2024"
  const formatPeriod = (period: string | null) => {
    if (!period) return '';
    if (period.includes('Q')) {
      const year = period.substring(0, 4);
      const quarter = period.substring(4);
      return `${quarter} ${year}`;
    }
    return period;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Globe className="w-4 h-4 text-emerald-600" />
          <h3 className="font-semibold text-gray-900 text-sm">GDP Growth</h3>
        </div>
        <div className="flex justify-center items-center h-32">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  if (error || !gdpData) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Globe className="w-4 h-4 text-emerald-600" />
          <h3 className="font-semibold text-gray-900 text-sm">GDP Growth</h3>
        </div>
        <div className="text-center text-gray-500 text-sm py-4">
          {error ? 'Failed to load GDP data' : 'No data available'}
        </div>
        <Link to="/research/bea" className="flex items-center justify-center gap-1 mt-2 pt-2 border-t border-gray-100 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
          GDP & BEA Data <ChevronRight className="w-3 h-3" />
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-emerald-600" />
          <h3 className="font-semibold text-gray-900 text-sm">GDP Growth</h3>
        </div>
        <span className="text-xs text-gray-500">{formatPeriod(gdpData.current.period)}</span>
      </div>

      <div className="flex gap-4 mb-4">
        <div>
          <div className="text-3xl font-bold text-gray-900">
            {gdpData.current.value != null ? `${gdpData.current.value.toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-xs text-gray-500">
            SAAR • Prior {gdpData.current.prior != null ? `${gdpData.current.prior.toFixed(1)}%` : 'N/A'}
          </div>
        </div>
        <div className="flex-1 h-28">
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
      {gdpData.components.length > 0 && (
        <>
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
        </>
      )}

      <Link to="/research/bea" className="flex items-center justify-center gap-1 mt-3 pt-3 border-t border-gray-100 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
        GDP & BEA Data <ChevronRight className="w-3 h-3" />
      </Link>
    </div>
  );
}

function CalendarCard() {
  const [activeTab, setActiveTab] = useState<'today' | 'upcoming'>('today');

  // Use React Query for calendar events
  const { data: allEvents = [], isLoading: loading } = useQuery({
    queryKey: ['economic-calendar-upcoming'],
    queryFn: async () => {
      const res = await economicCalendarAPI.getUpcoming<EconomicCalendarData>({
        days: 14,
        country: 'US',
        limit: 20
      });
      return res.data.events || [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000,
  });

  // Split events into today and upcoming
  const today = new Date().toDateString();
  const todayEvents = allEvents.filter(e => {
    if (!e.datetime) return false;
    return new Date(e.datetime).toDateString() === today;
  });
  const upcomingEvents = allEvents.filter(e => {
    if (!e.datetime) return false;
    return new Date(e.datetime).toDateString() !== today;
  });

  const displayEvents = activeTab === 'today' ? todayEvents : upcomingEvents;

  // Impact color mapping
  const getImpactColor = (impact: string | null) => {
    switch (impact) {
      case 'High': return 'bg-red-500';
      case 'Medium': return 'bg-amber-500';
      case 'Low': return 'bg-gray-400';
      default: return 'bg-gray-300';
    }
  };

  // Format value with unit
  const formatValue = (val: number | null) => {
    if (val === null) return '--';
    if (Math.abs(val) >= 1000) return `${(val / 1000).toFixed(1)}K`;
    if (Math.abs(val) >= 1) return val.toFixed(1);
    return val.toFixed(2);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-gray-400" />
          <h3 className="font-semibold text-gray-900 text-sm">Economic Calendar</h3>
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('today')}
            className={`px-2 py-0.5 text-xs rounded ${
              activeTab === 'today'
                ? 'bg-indigo-100 text-indigo-700 font-medium'
                : 'text-gray-500 hover:bg-gray-100'
            }`}
          >
            Today ({todayEvents.length})
          </button>
          <button
            onClick={() => setActiveTab('upcoming')}
            className={`px-2 py-0.5 text-xs rounded ${
              activeTab === 'upcoming'
                ? 'bg-indigo-100 text-indigo-700 font-medium'
                : 'text-gray-500 hover:bg-gray-100'
            }`}
          >
            Upcoming ({upcomingEvents.length})
          </button>
        </div>
      </div>
      <div className="divide-y divide-gray-100 max-h-[400px] overflow-y-auto">
        {loading ? (
          <div className="px-4 py-6 text-center text-sm text-gray-400">Loading...</div>
        ) : displayEvents.length === 0 ? (
          <div className="px-4 py-6 text-center text-sm text-gray-400">
            {activeTab === 'today' ? 'No events today' : 'No upcoming events'}
          </div>
        ) : (
          displayEvents.map((e, i) => (
            <div key={i} className="px-3 py-2 hover:bg-gray-50">
              <div className="flex items-start gap-2">
                {/* Impact indicator */}
                <div className={`w-1 h-full min-h-[36px] rounded-full ${getImpactColor(e.impact)}`} />

                {/* Time and Date */}
                <div className="w-14 flex-shrink-0">
                  <div className="text-xs font-medium text-gray-900">{e.time}</div>
                  {activeTab === 'upcoming' && (
                    <div className="text-[10px] text-gray-400">{e.date}</div>
                  )}
                </div>

                {/* Event info */}
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-900 truncate">{e.name}</div>
                  <div className="flex items-center gap-2 mt-0.5">
                    {e.actual !== null ? (
                      <>
                        <span className="text-[10px] text-gray-500">Act: <span className="font-medium text-gray-700">{formatValue(e.actual)}</span></span>
                        <span className="text-[10px] text-gray-400">Est: {formatValue(e.estimate)}</span>
                        <span className="text-[10px] text-gray-400">Prev: {formatValue(e.previous)}</span>
                      </>
                    ) : (
                      <>
                        <span className="text-[10px] text-gray-500">Est: <span className="font-medium text-gray-700">{formatValue(e.estimate)}</span></span>
                        <span className="text-[10px] text-gray-400">Prev: {formatValue(e.previous)}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
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
  const [auctions, setAuctions] = useState<TreasuryAuctionItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAuctions = async () => {
      try {
        setLoading(true);
        const res = await treasuryResearchAPI.getAuctions<TreasuryAuctionItem[]>({ limit: 6 });
        setAuctions(res.data || []);
      } catch (error) {
        console.error('Failed to load recent auctions:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAuctions();
  }, []);

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Format term to standard Treasury term (round to nearest)
  const formatTerm = (term: string): string => {
    const yearMatch = term.match(/(\d+)[- ]?Y/i) || term.match(/(\d+)[- ]?Year/i);
    const monthMatch = term.match(/(\d+)[- ]?M/i) || term.match(/(\d+)[- ]?Month/i);
    const weekMatch = term.match(/(\d+)[- ]?W/i) || term.match(/(\d+)[- ]?Week/i);

    if (weekMatch) {
      return `${weekMatch[1]}W`;
    }

    if (yearMatch) {
      const years = parseInt(yearMatch[1]);
      const months = monthMatch ? parseInt(monthMatch[1]) : 0;
      const totalYears = Math.round(years + months / 12);
      return `${totalYears}Y`;
    }

    return term;
  };

  // Determine auction result based on bid-to-cover and tail
  const getAuctionResult = (btc: number | null, tail: number | null): string => {
    if (btc == null) return 'pending';
    if (btc >= 2.5 && (tail == null || tail <= 0)) return 'strong';
    if (btc < 2.0 || (tail != null && tail > 1)) return 'weak';
    return 'neutral';
  };

  // Get summary stats
  const strongCount = auctions.filter(a => (a.auction_result || getAuctionResult(a.bid_to_cover_ratio, a.tail_bps)) === 'strong').length;
  const weakCount = auctions.filter(a => (a.auction_result || getAuctionResult(a.bid_to_cover_ratio, a.tail_bps)) === 'weak').length;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 min-h-[400px] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Landmark className="w-4 h-4 text-indigo-600" />
          <h3 className="font-semibold text-gray-900 text-sm">Recent Auctions</h3>
        </div>
        {!loading && auctions.length > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="flex items-center gap-1 text-[10px] text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              {strongCount} strong
            </span>
            <span className="flex items-center gap-1 text-[10px] text-red-600 bg-red-50 px-1.5 py-0.5 rounded">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
              {weakCount} weak
            </span>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="flex-1 overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-gray-50 border-y border-gray-200">
                <th className="py-2 px-2 text-left font-semibold text-gray-600 uppercase text-[10px] tracking-wide">Term</th>
                <th className="py-2 px-2 text-left font-semibold text-gray-600 uppercase text-[10px] tracking-wide">Date</th>
                <th className="py-2 px-2 text-right font-semibold text-gray-600 uppercase text-[10px] tracking-wide">Yield</th>
                <th className="py-2 px-2 text-right font-semibold text-gray-600 uppercase text-[10px] tracking-wide">BTC</th>
                <th className="py-2 px-2 text-right font-semibold text-gray-600 uppercase text-[10px] tracking-wide">Tail</th>
                <th className="py-2 px-2 text-center font-semibold text-gray-600 uppercase text-[10px] tracking-wide">Result</th>
              </tr>
            </thead>
            <tbody>
              {auctions.map((a, idx) => {
                const result = a.auction_result || getAuctionResult(a.bid_to_cover_ratio, a.tail_bps);
                return (
                  <tr
                    key={a.auction_id}
                    className={`hover:bg-indigo-50 transition-colors ${idx % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                  >
                    <td className="py-2.5 px-2">
                      <span className="font-semibold text-gray-900">
                        {formatTerm(a.security_term)}
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-gray-500">{formatDate(a.auction_date)}</td>
                    <td className="py-2.5 px-2 text-right">
                      <span className="font-mono font-medium text-gray-900">
                        {a.high_yield != null ? `${a.high_yield.toFixed(3)}%` : '--'}
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-right">
                      <span className={`font-mono ${a.bid_to_cover_ratio != null && a.bid_to_cover_ratio >= 2.5 ? 'text-emerald-600 font-medium' : 'text-gray-600'}`}>
                        {a.bid_to_cover_ratio != null ? `${a.bid_to_cover_ratio.toFixed(2)}x` : '--'}
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-right">
                      <span className={`font-mono font-medium ${a.tail_bps != null ? (a.tail_bps <= 0 ? 'text-emerald-600' : 'text-red-500') : 'text-gray-400'}`}>
                        {a.tail_bps != null ? `${a.tail_bps > 0 ? '+' : ''}${a.tail_bps.toFixed(1)}` : '--'}
                      </span>
                    </td>
                    <td className="py-2.5 px-2 text-center">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        result === 'strong' ? 'bg-emerald-100 text-emerald-700' :
                        result === 'weak' ? 'bg-red-100 text-red-700' :
                        result === 'pending' ? 'bg-amber-100 text-amber-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {result === 'strong' && <TrendingUp className="w-2.5 h-2.5" />}
                        {result === 'weak' && <TrendingDown className="w-2.5 h-2.5" />}
                        {result}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Footer */}
      <Link to="/research/treasury" className="flex items-center justify-center gap-1 mt-auto pt-3 border-t border-gray-100 text-xs text-indigo-600 hover:text-indigo-700 font-medium">
        Treasury Explorer <ChevronRight className="w-3 h-3" />
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
    <div className="grid grid-cols-3 gap-2 h-full">
      {/* Metrics */}
      <div className="space-y-2">
        <div className="bg-red-50 rounded-lg p-2 border border-red-100">
          <div className="text-[10px] text-gray-500">Unemployment Rate</div>
          <div className="text-2xl font-bold text-gray-900">
            {unemployment?.latest_value?.toFixed(1) ?? '--'}%
          </div>
          {unemployment?.month_over_month != null && (
            <div className={`text-xs ${unemployment.month_over_month > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
              {unemployment.month_over_month > 0 ? '↑' : '↓'} {Math.abs(unemployment.month_over_month).toFixed(2)}pp
            </div>
          )}
        </div>
        <div className="bg-blue-50 rounded-lg p-2 border border-blue-100">
          <div className="text-[10px] text-gray-500">Labor Force Participation</div>
          <div className="text-xl font-bold text-gray-900">
            {lfpr?.latest_value?.toFixed(1) ?? '--'}%
          </div>
          {lfpr?.month_over_month != null && (
            <div className={`text-[10px] ${lfpr.month_over_month < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
              {lfpr.month_over_month > 0 ? '↑' : '↓'} {Math.abs(lfpr.month_over_month).toFixed(2)}pp
            </div>
          )}
        </div>
        <div className="text-[10px] text-gray-400 text-center">
          {unemployment?.latest_date || 'Latest data'}
        </div>
      </div>

      {/* Chart */}
      <div className="col-span-2">
        <div className="text-[10px] font-medium text-gray-600 mb-1">Unemployment Rate Trend</div>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeline} margin={{ top: 5, right: 5, bottom: 5, left: -5 }}>
              <defs>
                <linearGradient id="lnGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#dc2626" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#dc2626" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={32} domain={['auto', 'auto']} tickFormatter={(v) => `${v}%`} />
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
    .slice(0, 6);

  return (
    <div className="grid grid-cols-3 gap-2 h-full">
      {/* Metrics */}
      <div className="space-y-2">
        <div className="bg-blue-50 rounded-lg p-2 border border-blue-100">
          <div className="text-[10px] text-gray-500">Nonfarm Payrolls</div>
          <div className="text-2xl font-bold text-gray-900">
            {payrollsChange != null ? `${payrollsChange >= 0 ? '+' : ''}${payrollsChange.toFixed(0)}K` : '--'}
          </div>
          <div className="text-[10px] text-gray-500">MoM change</div>
        </div>
        <div className="bg-indigo-50 rounded-lg p-2 border border-indigo-100">
          <div className="text-[10px] text-gray-500">Total Employment</div>
          <div className="text-xl font-bold text-gray-900">
            {totalNonfarm?.latest_value ? `${(totalNonfarm.latest_value / 1000).toFixed(1)}M` : '--'}
          </div>
          <div className="text-[10px] text-gray-500">jobs</div>
        </div>
        <div className="text-[10px] text-gray-400 text-center">
          {totalNonfarm?.latest_date || 'Latest data'}
        </div>
      </div>

      {/* Sector changes */}
      <div className="col-span-2">
        <div className="text-[10px] font-medium text-gray-600 mb-1">Jobs by Sector (MoM, 000s)</div>
        <div className="space-y-1.5">
          {topSectors.map((sector, i) => {
            const change = sector.month_over_month || 0;
            const maxChange = Math.max(...topSectors.map(s => Math.abs(s.month_over_month || 0)), 1);
            return (
              <div key={i} className="flex items-center gap-1.5">
                <div className="w-24 text-[10px] text-gray-600 truncate">{sector.supersector_name.replace(' and ', ' & ')}</div>
                <div className="flex-1 h-5 bg-gray-100 rounded relative overflow-hidden">
                  <div
                    className={`absolute h-full rounded ${change >= 0 ? 'bg-emerald-500' : 'bg-red-400'}`}
                    style={{ width: `${(Math.abs(change) / maxChange) * 100}%` }}
                  />
                </div>
                <div className={`w-10 text-[10px] font-semibold text-right ${change >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
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
    <div className="grid grid-cols-3 gap-2 h-full">
      {/* Metrics */}
      <div className="space-y-1.5">
        <div className="bg-amber-50 rounded-lg p-2 border border-amber-100">
          <div className="text-[10px] text-gray-500">Job Openings</div>
          <div className="text-lg font-bold text-gray-900">
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
          <div className="text-lg font-bold text-gray-900">
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
          <div className="text-lg font-bold text-gray-900">
            {quitsLevel != null ? `${(quitsLevel / 1000).toFixed(1)}M` : (quitsRate?.value?.toFixed(1) ?? '--')}
            {quitsLevel == null && quitsRate?.value != null && '%'}
          </div>
          {quitsRate?.year_over_year_pct != null && (
            <div className={`text-[10px] ${quitsRate.year_over_year_pct > 0 ? 'text-emerald-600' : 'text-red-500'}`}>
              {quitsRate.year_over_year_pct > 0 ? '↑' : '↓'} {Math.abs(quitsRate.year_over_year_pct).toFixed(1)}% YoY
            </div>
          )}
        </div>
        <div className="text-[10px] text-gray-400 text-center">
          {openingsRate?.latest_date || overview?.last_updated || 'Latest data'}
        </div>
      </div>

      {/* Chart - using rates */}
      <div className="col-span-2">
        <div className="text-[10px] font-medium text-gray-600 mb-1">JOLTS Rates (%)</div>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeline} margin={{ top: 5, right: 5, bottom: 5, left: -5 }}>
              <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={32} tickFormatter={(v) => `${v}%`} />
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
    <div className="grid grid-cols-3 gap-2 h-full">
      {/* Metrics */}
      <div className="space-y-2">
        <div className="bg-red-50 rounded-lg p-2 border border-red-100">
          <div className="text-[10px] text-gray-500">Headline CPI YoY</div>
          <div className="text-2xl font-bold text-gray-900">
            {headline?.year_over_year?.toFixed(1) ?? '--'}%
          </div>
          {headline?.month_over_month != null && (
            <div className="text-[10px] text-gray-500">
              {headline.month_over_month >= 0 ? '+' : ''}{headline.month_over_month.toFixed(2)}% MoM
            </div>
          )}
        </div>
        <div className="bg-purple-50 rounded-lg p-2 border border-purple-100">
          <div className="text-[10px] text-gray-500">Core CPI YoY</div>
          <div className="text-xl font-bold text-gray-900">
            {core?.year_over_year?.toFixed(1) ?? '--'}%
          </div>
          {core?.month_over_month != null && (
            <div className="text-[10px] text-gray-500">
              {core.month_over_month >= 0 ? '+' : ''}{core.month_over_month.toFixed(2)}% MoM
            </div>
          )}
        </div>
        <div className="text-[10px] text-gray-400 text-center">
          {headline?.latest_date || 'Latest data'}
        </div>
      </div>

      {/* Chart */}
      <div className="col-span-2">
        <div className="text-[10px] font-medium text-gray-600 mb-1">Inflation Rate (YoY %)</div>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeline} margin={{ top: 5, right: 5, bottom: 5, left: -5 }}>
              <defs>
                <linearGradient id="cuHeadlineGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={32} tickFormatter={(v) => `${v}%`} />
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
    <div className="grid grid-cols-3 gap-2 h-full">
      {/* Metrics */}
      <div className="space-y-1.5">
        <div className="bg-purple-50 rounded-lg p-2 border border-purple-100">
          <div className="text-[10px] text-gray-500">Final Demand YoY</div>
          <div className="text-xl font-bold text-gray-900">
            {headline?.yoy_pct?.toFixed(1) ?? '--'}%
          </div>
          {headline?.mom_pct != null && (
            <div className="text-[10px] text-gray-500">
              {headline.mom_pct >= 0 ? '+' : ''}{headline.mom_pct.toFixed(2)}% MoM
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-1.5">
          <div className="bg-blue-50 rounded-lg p-2 border border-blue-100">
            <div className="text-[10px] text-gray-500">Goods</div>
            <div className="text-base font-bold text-gray-900">
              {goods?.yoy_pct?.toFixed(1) ?? '--'}%
            </div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-2 border border-emerald-100">
            <div className="text-[10px] text-gray-500">Services</div>
            <div className="text-base font-bold text-gray-900">
              {services?.yoy_pct?.toFixed(1) ?? '--'}%
            </div>
          </div>
        </div>
        <div className="text-[10px] text-gray-400 text-center">
          {headline?.latest_date || overview?.last_updated || 'Latest data'}
        </div>
      </div>

      {/* Chart - show components breakdown */}
      <div className="col-span-2">
        <div className="text-[10px] font-medium text-gray-600 mb-1">PPI Components (YoY %)</div>
        {components.length > 0 ? (
          <div className="space-y-1.5">
            {components.slice(0, 6).map((comp, i) => {
              const maxYoy = Math.max(...components.map(c => Math.abs(c.yoy_pct || 0)), 1);
              const yoy = comp.yoy_pct || 0;
              return (
                <div key={i} className="flex items-center gap-1.5">
                  <div className="w-28 text-[10px] text-gray-600 truncate" title={comp.name}>{comp.name}</div>
                  <div className="flex-1 h-5 bg-gray-100 rounded relative overflow-hidden">
                    <div
                      className={`absolute h-full rounded ${yoy >= 0 ? 'bg-purple-500' : 'bg-red-400'}`}
                      style={{ width: `${(Math.abs(yoy) / maxYoy) * 100}%` }}
                    />
                  </div>
                  <div className={`w-12 text-[10px] font-semibold text-right ${yoy >= 0 ? 'text-purple-600' : 'text-red-500'}`}>
                    {yoy >= 0 ? '+' : ''}{yoy.toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeline} margin={{ top: 5, right: 5, bottom: 5, left: -5 }}>
                <defs>
                  <linearGradient id="wpGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="period_name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={32} tickFormatter={(v) => `${v}%`} />
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
    <div className="grid grid-cols-3 gap-2 h-full">
      {/* Rankings sidebar */}
      <div className="space-y-1.5">
        <div className="bg-red-50 rounded-lg p-2 border border-red-100">
          <div className="text-[10px] text-red-700 font-medium mb-0.5">Highest Rates</div>
          {(rankings?.highest || highestStates.map(s => `${s.area_name}: ${s.unemployment_rate?.toFixed(1)}%`)).slice(0, 3).map((name, i) => (
            <div key={i} className="text-[10px] text-gray-700 truncate">{i + 1}. {name}</div>
          ))}
        </div>
        <div className="bg-green-50 rounded-lg p-2 border border-green-100">
          <div className="text-[10px] text-green-700 font-medium mb-0.5">Lowest Rates</div>
          {(rankings?.lowest || lowestStates.map(s => `${s.area_name}: ${s.unemployment_rate?.toFixed(1)}%`)).slice(0, 3).map((name, i) => (
            <div key={i} className="text-[10px] text-gray-700 truncate">{i + 1}. {name}</div>
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
      <div className="col-span-2 h-full min-h-[200px]">
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
    .slice(0, 7);

  // Get latest date from first sector
  const latestDate = sectors[0]?.latest_date;

  return (
    <div className="grid grid-cols-3 gap-2 h-full">
      {/* Summary metrics */}
      <div className="space-y-2">
        <div className="bg-cyan-50 rounded-lg p-2 border border-cyan-100">
          <div className="text-[10px] text-gray-500">PPI by Industry</div>
          <div className="text-xl font-bold text-gray-900">
            {sectors.length > 0 ? `${sectors.length} Sectors` : '--'}
          </div>
          <div className="text-[10px] text-gray-500">tracked</div>
        </div>
        <div className="text-[10px] text-gray-400 text-center">
          {latestDate || 'Latest data'}
        </div>
        <div className="text-[10px] text-gray-500 p-2 bg-gray-50 rounded">
          Producer prices by NAICS industry classification. Shows YoY % change.
        </div>
      </div>

      {/* Sector breakdown */}
      <div className="col-span-2">
        <div className="text-[10px] font-medium text-gray-600 mb-1">Sectors by YoY Change</div>
        {sortedSectors.length > 0 ? (
          <div className="space-y-1.5">
            {sortedSectors.map((sector, i) => {
              const maxYoy = Math.max(...sortedSectors.map(s => Math.abs(s.yoy_pct || 0)), 1);
              const yoy = sector.yoy_pct || 0;
              return (
                <div key={i} className="flex items-center gap-1.5">
                  <div className="w-28 text-[10px] text-gray-600 truncate" title={sector.sector_name}>{sector.sector_name}</div>
                  <div className="flex-1 h-5 bg-gray-100 rounded relative overflow-hidden">
                    <div
                      className={`absolute h-full rounded ${yoy >= 0 ? 'bg-cyan-500' : 'bg-red-400'}`}
                      style={{ width: `${(Math.abs(yoy) / maxYoy) * 100}%` }}
                    />
                  </div>
                  <div className={`w-12 text-[10px] font-semibold text-right ${yoy >= 0 ? 'text-cyan-600' : 'text-red-500'}`}>
                    {yoy >= 0 ? '+' : ''}{yoy.toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center">
              <Truck className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <div className="text-xs text-gray-600">Industry-level PPI data</div>
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
      <div className="px-3 py-2 min-h-[260px]">
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
  // Use React Query's useQueries for parallel fetching with caching
  const queryConfigs = [
    { key: 'ln-overview', fn: () => lnResearchAPI.getOverview<LNOverviewData>() },
    { key: 'ln-timeline', fn: () => lnResearchAPI.getOverviewTimeline<{ timeline: LNTimelinePoint[] }>(24) },
    { key: 'ce-overview', fn: () => ceResearchAPI.getOverview<CEOverviewData>() },
    { key: 'ce-supersectors', fn: () => ceResearchAPI.getSupersectors<{ supersectors: SupersectorItem[] }>() },
    { key: 'cu-overview', fn: () => cuResearchAPI.getOverview<CUOverviewData>() },
    { key: 'cu-timeline', fn: () => cuResearchAPI.getOverviewTimeline<{ timeline: CUTimelinePoint[] }>('0000', 24) },
    { key: 'la-states', fn: () => laResearchAPI.getStates<LAStatesData>() },
    { key: 'wp-overview', fn: () => wpResearchAPI.getOverview<WPOverviewData>() },
    { key: 'wp-timeline', fn: () => wpResearchAPI.getOverviewTimeline<{ timeline: WPTimelinePoint[] }>(24) },
    { key: 'pc-overview', fn: () => pcResearchAPI.getOverview<PCOverviewData>() },
    { key: 'jt-overview', fn: () => jtResearchAPI.getOverview<JTOverviewData>() },
    { key: 'jt-timeline', fn: () => jtResearchAPI.getOverviewTimeline<{ timeline: JTTimelinePoint[] }>('000000', '00', 24) },
  ];

  const queryResults = useQueries({
    queries: queryConfigs.map(config => ({
      queryKey: [config.key],
      queryFn: async () => {
        const res = await config.fn();
        return res.data;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 30 * 60 * 1000, // 30 minutes
    })),
  });

  // Derive carousel data from query results
  const carouselData = useMemo<CarouselData>(() => {
    const isLoading = queryResults.some(q => q.isLoading);
    const [lnOverview, lnTimeline, ceOverview, ceSupersectors, cuOverview, cuTimeline,
           laStates, wpOverview, wpTimeline, pcOverview, jtOverview, jtTimeline] = queryResults;

    return {
      ln: {
        overview: lnOverview.data as LNOverviewData | null,
        timeline: (lnTimeline.data as { timeline: LNTimelinePoint[] } | undefined)?.timeline || [],
      },
      ce: {
        overview: ceOverview.data as CEOverviewData | null,
        timeline: [],
        supersectors: (ceSupersectors.data as { supersectors: SupersectorItem[] } | undefined)?.supersectors || [],
      },
      cu: {
        overview: cuOverview.data as CUOverviewData | null,
        timeline: (cuTimeline.data as { timeline: CUTimelinePoint[] } | undefined)?.timeline || [],
      },
      la: {
        states: laStates.data as LAStatesData | null,
      },
      wp: {
        overview: wpOverview.data as WPOverviewData | null,
        timeline: (wpTimeline.data as { timeline: WPTimelinePoint[] } | undefined)?.timeline || [],
      },
      pc: {
        overview: pcOverview.data as PCOverviewData | null,
      },
      jt: {
        overview: jtOverview.data as JTOverviewData | null,
        timeline: (jtTimeline.data as { timeline: JTTimelinePoint[] } | undefined)?.timeline || [],
      },
      loading: isLoading,
    };
  }, [queryResults]);

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
              <ClaimsCard />
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

            {/* FRED Release Calendar */}
            <FREDCalendarCard />

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
