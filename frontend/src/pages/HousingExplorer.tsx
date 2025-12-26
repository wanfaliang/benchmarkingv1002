import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { housingResearchAPI } from '../services/api';
import FREDExplorerNav from '../components/FREDExplorerNav';
import {
  Info,
  Loader2,
  Home,
  Building2,
  MapPin,
  Percent,
  LineChart as LineChartIcon,
} from 'lucide-react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Legend,
  Area,
  Cell,
  PieChart,
  Pie,
} from 'recharts';

// ============================================================================
// TYPES
// ============================================================================

interface SeriesData {
  value: number;
  date: string;
  prior_value: number | null;
  mom_change: number | null;
  mom_pct: number | null;
  year_ago_value: number | null;
  yoy_change: number | null;
  yoy_pct: number | null;
}

interface RegionalData {
  series_id: string;
  name: string;
  value: number;
  date: string;
  mom_change: number | null;
  mom_pct: number | null;
  yoy_change: number | null;
  yoy_pct: number | null;
}

interface OverviewData {
  as_of: string;
  housing_starts: {
    total: SeriesData | null;
    single_family: SeriesData | null;
    multi_family: SeriesData | null;
    single_family_share: number | null;
    activity_level: string | null;
  };
  building_permits: {
    total: SeriesData | null;
    single_family: SeriesData | null;
  };
  pipeline: {
    completions: SeriesData | null;
    under_construction: SeriesData | null;
  };
  mortgage_rates: {
    rate_30y: SeriesData | null;
    rate_15y: SeriesData | null;
    spread: number | null;
  };
  regional: Record<string, RegionalData>;
  series_info: {
    last_updated: string | null;
  };
}

interface TimelinePoint {
  date: string;
  starts: number | null;
  permits: number | null;
  starts_1f: number | null;
  starts_5f: number | null;
}

interface TimelineData {
  months_back: number;
  data_points: number;
  timeline: TimelinePoint[];
}

interface MortgageData {
  months_back: number;
  data_points: number;
  statistics: {
    current: number | null;
    avg: number | null;
    min: number | null;
    max: number | null;
  };
  timeline: Array<{
    date: string;
    rate_30y: number | null;
    rate_15y: number | null;
    spread: number | null;
  }>;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const PERIOD_OPTIONS = [
  { label: '2Y', value: 24 },
  { label: '5Y', value: 60 },
  { label: '10Y', value: 120 },
  { label: '20Y', value: 240 },
];

const CHART_COLORS = {
  starts: '#6366f1',
  permits: '#10b981',
  sf: '#f59e0b',
  mf: '#8b5cf6',
  rate30: '#ef4444',
  rate15: '#f97316',
};

const ACTIVITY_COLORS: Record<string, { bg: string; text: string }> = {
  weak: { bg: 'bg-red-100', text: 'text-red-700' },
  below_average: { bg: 'bg-orange-100', text: 'text-orange-700' },
  normal: { bg: 'bg-green-100', text: 'text-green-700' },
  strong: { bg: 'bg-emerald-100', text: 'text-emerald-700' },
};

const REGION_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444'];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
    </div>
  );
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

function formatValue(value: number | null | undefined, decimals: number = 0): string {
  if (value === null || value === undefined) return '-';
  return value.toFixed(decimals);
}

function formatChange(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}`;
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

// ============================================================================
// HOUSING STARTS CARD
// ============================================================================

function HousingStartsCard({ data }: { data: OverviewData }) {
  const { housing_starts } = data;
  const activityStyle = housing_starts.activity_level
    ? ACTIVITY_COLORS[housing_starts.activity_level]
    : ACTIVITY_COLORS.normal;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <Home className="w-5 h-5 text-indigo-600" />
        <h3 className="font-semibold text-gray-900">Housing Starts</h3>
      </div>

      {/* Main Value */}
      <div className="text-center mb-4">
        <div className="text-4xl font-bold text-indigo-600 mb-1">
          {formatValue(housing_starts.total?.value)}K
        </div>
        <div className="text-sm text-gray-500">Units (SAAR)</div>
        {housing_starts.total?.date && (
          <div className="text-xs text-gray-400 mt-1">{formatDate(housing_starts.total.date)}</div>
        )}
      </div>

      {/* Activity Level */}
      <div className={`rounded-lg px-3 py-2 text-center mb-4 ${activityStyle.bg}`}>
        <span className={`text-sm font-medium ${activityStyle.text} capitalize`}>
          {housing_starts.activity_level?.replace('_', ' ')} Activity
        </span>
      </div>

      {/* Changes */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gray-50 rounded-lg p-2 text-center">
          <div className="text-xs text-gray-500">MoM</div>
          <div className={`text-sm font-semibold ${
            (housing_starts.total?.mom_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatPercent(housing_starts.total?.mom_pct)}
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-2 text-center">
          <div className="text-xs text-gray-500">YoY</div>
          <div className={`text-sm font-semibold ${
            (housing_starts.total?.yoy_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatPercent(housing_starts.total?.yoy_pct)}
          </div>
        </div>
      </div>

      {/* Breakdown */}
      <div className="border-t pt-4">
        <div className="text-xs font-medium text-gray-500 mb-2">By Structure Type</div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Single Family</span>
            <div className="text-right">
              <span className="font-medium">{formatValue(housing_starts.single_family?.value)}K</span>
              <span className="text-xs text-gray-400 ml-1">({housing_starts.single_family_share}%)</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Multi-Family (5+)</span>
            <span className="font-medium">{formatValue(housing_starts.multi_family?.value)}K</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MORTGAGE RATES CARD
// ============================================================================

function MortgageRatesCard({ data }: { data: OverviewData }) {
  const { mortgage_rates } = data;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <Percent className="w-5 h-5 text-red-500" />
        <h3 className="font-semibold text-gray-900">Mortgage Rates</h3>
      </div>

      {/* 30-Year Rate */}
      <div className="bg-red-50 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium text-gray-700">30-Year Fixed</span>
          <span className="text-2xl font-bold text-red-600">
            {formatValue(mortgage_rates.rate_30y?.value, 2)}%
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className={`${
            (mortgage_rates.rate_30y?.mom_change || 0) >= 0 ? 'text-red-500' : 'text-green-500'
          }`}>
            {formatChange(mortgage_rates.rate_30y?.mom_change)} WoW
          </span>
          <span className="text-gray-400">|</span>
          <span className={`${
            (mortgage_rates.rate_30y?.yoy_change || 0) >= 0 ? 'text-red-500' : 'text-green-500'
          }`}>
            {formatChange(mortgage_rates.rate_30y?.yoy_change)} YoY
          </span>
        </div>
      </div>

      {/* 15-Year Rate */}
      <div className="bg-orange-50 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium text-gray-700">15-Year Fixed</span>
          <span className="text-xl font-bold text-orange-600">
            {formatValue(mortgage_rates.rate_15y?.value, 2)}%
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className={`${
            (mortgage_rates.rate_15y?.mom_change || 0) >= 0 ? 'text-red-500' : 'text-green-500'
          }`}>
            {formatChange(mortgage_rates.rate_15y?.mom_change)} WoW
          </span>
        </div>
      </div>

      {/* Spread */}
      <div className="border-t pt-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">30Y - 15Y Spread</span>
          <span className="font-medium">{formatValue(mortgage_rates.spread, 2)}%</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// BUILDING PERMITS CARD
// ============================================================================

function BuildingPermitsCard({ data }: { data: OverviewData }) {
  const { building_permits, pipeline } = data;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <Building2 className="w-5 h-5 text-green-600" />
        <h3 className="font-semibold text-gray-900">Building Permits & Pipeline</h3>
      </div>

      {/* Permits */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Total Permits</span>
          <span className="text-xl font-bold text-green-600">
            {formatValue(building_permits.total?.value)}K
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className={`${
            (building_permits.total?.yoy_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatPercent(building_permits.total?.yoy_pct)} YoY
          </span>
        </div>
      </div>

      <div className="border-t pt-4 space-y-3">
        {/* Under Construction */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Under Construction</span>
          <span className="font-medium">{formatValue(pipeline.under_construction?.value)}K units</span>
        </div>
        {/* Completions */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Completions</span>
          <span className="font-medium">{formatValue(pipeline.completions?.value)}K</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// REGIONAL BREAKDOWN
// ============================================================================

function RegionalBreakdown({ data }: { data: OverviewData }) {
  const regions = Object.entries(data.regional || {});

  if (!regions.length) return null;

  const total = regions.reduce((sum, [, r]) => sum + (r.value || 0), 0);
  const pieData = regions.map(([, r], idx) => ({
    name: r.name,
    value: r.value,
    share: total > 0 ? (r.value / total) * 100 : 0,
    color: REGION_COLORS[idx % REGION_COLORS.length],
  }));

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-indigo-600" />
        <h3 className="font-semibold text-gray-900">Regional Housing Starts</h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Pie Chart */}
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={70}
                dataKey="value"
                label={(props: any) => `${props.name}: ${(props.percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {pieData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => [`${value.toFixed(0)}K`, 'Starts']} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* List */}
        <div className="space-y-2">
          {regions.map(([key, r], idx) => (
            <div key={key} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: REGION_COLORS[idx] }} />
                <span className="text-gray-700">{r.name}</span>
              </div>
              <div className="text-right">
                <span className="font-medium">{formatValue(r.value)}K</span>
                <span className={`ml-2 text-xs ${
                  (r.yoy_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatPercent(r.yoy_pct)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// HOUSING TIMELINE CHART
// ============================================================================

function HousingTimelineChart({ monthsBack }: { monthsBack: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['housing-timeline', monthsBack],
    queryFn: () => housingResearchAPI.getTimeline<TimelineData>(monthsBack),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error || !data?.data) return <div className="text-red-500 p-4">Failed to load chart</div>;

  const chartData = data.data.timeline;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <LineChartIcon className="w-5 h-5 text-indigo-600" />
          <h3 className="font-semibold text-gray-900">Starts & Permits History</h3>
        </div>
        <div className="text-sm text-gray-500">{data.data.data_points} data points</div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tickFormatter={(val) => formatDate(val)}
              tick={{ fontSize: 11 }}
              tickLine={false}
              interval="preserveStartEnd"
              minTickGap={50}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              domain={['auto', 'auto']}
              tickFormatter={(val) => `${val}K`}
            />
            <Tooltip
              formatter={(value: number, name: string) => [
                `${value?.toFixed(0)}K`,
                name === 'starts' ? 'Housing Starts' :
                name === 'permits' ? 'Building Permits' :
                name === 'starts_1f' ? 'Single Family' : 'Multi-Family'
              ]}
              labelFormatter={(label) => formatDate(label)}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="starts"
              stroke={CHART_COLORS.starts}
              strokeWidth={2}
              dot={false}
              name="Housing Starts"
            />
            <Line
              type="monotone"
              dataKey="permits"
              stroke={CHART_COLORS.permits}
              strokeWidth={2}
              dot={false}
              name="Building Permits"
            />
            <Line
              type="monotone"
              dataKey="starts_1f"
              stroke={CHART_COLORS.sf}
              strokeWidth={1.5}
              strokeDasharray="5 5"
              dot={false}
              name="Single Family"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ============================================================================
// MORTGAGE RATES CHART
// ============================================================================

function MortgageRatesChart({ monthsBack }: { monthsBack: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['housing-mortgage', monthsBack],
    queryFn: () => housingResearchAPI.getMortgageRates<MortgageData>(monthsBack),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error || !data?.data) return <div className="text-red-500 p-4">Failed to load chart</div>;

  const chartData = data.data.timeline;
  const stats = data.data.statistics;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Percent className="w-5 h-5 text-red-500" />
          <h3 className="font-semibold text-gray-900">Mortgage Rate History</h3>
        </div>
        <div className="text-sm text-gray-500">
          Avg: {stats.avg}% | Range: {stats.min}% - {stats.max}%
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tickFormatter={(val) => formatDate(val)}
              tick={{ fontSize: 11 }}
              tickLine={false}
              interval="preserveStartEnd"
              minTickGap={50}
            />
            <YAxis
              tickFormatter={(val) => `${val}%`}
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              domain={['auto', 'auto']}
            />
            <Tooltip
              formatter={(value: number) => [`${value?.toFixed(2)}%`, '']}
              labelFormatter={(label) => formatDate(label)}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="rate_30y"
              stroke={CHART_COLORS.rate30}
              fill="rgba(239, 68, 68, 0.1)"
              strokeWidth={2}
              name="30-Year"
            />
            <Line
              type="monotone"
              dataKey="rate_15y"
              stroke={CHART_COLORS.rate15}
              strokeWidth={1.5}
              dot={false}
              name="15-Year"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function HousingExplorer() {
  const [monthsBack, setMonthsBack] = useState(60);

  const { data: overviewData, isLoading, error } = useQuery({
    queryKey: ['housing-overview'],
    queryFn: () => housingResearchAPI.getOverview<OverviewData>(),
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (error || !overviewData?.data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-500">Failed to load housing data</div>
      </div>
    );
  }

  const overview = overviewData.data;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* FRED Explorer Navigation */}
      <FREDExplorerNav />

      {/* Content */}
      <div className="px-6 py-6 space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Housing Market Explorer</h1>
            <p className="text-sm text-gray-600 mt-1">Starts, Permits & Mortgage Rates</p>
          </div>
          <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
            {PERIOD_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setMonthsBack(opt.value)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  monthsBack === opt.value
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Top Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <HousingStartsCard data={overview} />
          <BuildingPermitsCard data={overview} />
          <MortgageRatesCard data={overview} />
        </div>

        {/* Regional */}
        <RegionalBreakdown data={overview} />

        {/* Charts */}
        <HousingTimelineChart monthsBack={monthsBack} />
        <MortgageRatesChart monthsBack={monthsBack} />

        {/* Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">About Housing Data</p>
              <p className="text-blue-700">
                Housing starts and building permits are leading indicators of construction activity and economic health.
                Building permits typically precede starts by 1-2 months. Single-family construction is more sensitive
                to mortgage rates and consumer confidence, while multi-family responds more to rental market conditions.
                Data source: U.S. Census Bureau via FRED.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
