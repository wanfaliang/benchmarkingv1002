import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { sentimentResearchAPI } from '../services/api';
import FREDExplorerNav from '../components/FREDExplorerNav';
import {
  BarChart3,
  LineChart,
  Info,
  Loader2,
  Smile,
  Frown,
  Meh,
  ThermometerSun,
  Users,
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
  ReferenceLine,
  Area,
} from 'recharts';

// ============================================================================
// TYPES
// ============================================================================

interface SeriesData {
  series_id: string;
  name: string;
  category: string;
  value: number;
  date: string;
  prior_value: number | null;
  mom_change: number | null;
  mom_pct: number | null;
  year_ago_value: number | null;
  yoy_change: number | null;
  yoy_pct: number | null;
}

interface OverviewData {
  as_of: string;
  headline: SeriesData & { sentiment_level: string | null };
  components: {
    current_conditions: SeriesData | null;
  };
  inflation_expectations: SeriesData | null;
  historical_stats: {
    all_time_min: number;
    all_time_max: number;
    all_time_avg: number;
    current_percentile: number;
    observation_count: number;
  };
  series_info: {
    last_updated: string | null;
    observation_start: string | null;
  };
}

interface TimelinePoint {
  date: string;
  sentiment: number | null;
  current_conditions: number | null;
  inflation_expectations: number | null;
}

interface TimelineData {
  months_back: number;
  data_points: number;
  timeline: TimelinePoint[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const PERIOD_OPTIONS = [
  { label: '1Y', value: 12 },
  { label: '2Y', value: 24 },
  { label: '5Y', value: 60 },
  { label: '10Y', value: 120 },
  { label: '20Y', value: 240 },
];

const CHART_COLORS = {
  sentiment: '#6366f1',
  current: '#10b981',
  inflation: '#ef4444',
};

const SENTIMENT_COLORS: Record<string, { bg: string; text: string; icon: typeof Smile }> = {
  very_pessimistic: { bg: 'bg-red-100', text: 'text-red-700', icon: Frown },
  pessimistic: { bg: 'bg-orange-100', text: 'text-orange-700', icon: Frown },
  neutral: { bg: 'bg-gray-100', text: 'text-gray-700', icon: Meh },
  optimistic: { bg: 'bg-green-100', text: 'text-green-700', icon: Smile },
  very_optimistic: { bg: 'bg-emerald-100', text: 'text-emerald-700', icon: Smile },
};

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
  return date.toLocaleDateString('en-US', {
    month: 'short',
    year: 'numeric',
  });
}

function formatValue(value: number | null): string {
  if (value === null || value === undefined) return '-';
  return value.toFixed(1);
}

function formatChange(value: number | null, showSign: boolean = true): string {
  if (value === null || value === undefined) return '-';
  const sign = showSign && value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}`;
}

function formatPercent(value: number | null): string {
  if (value === null || value === undefined) return '-';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

// ============================================================================
// HEADLINE SENTIMENT CARD
// ============================================================================

function HeadlineSentimentCard({ data }: { data: OverviewData }) {
  const { headline, historical_stats } = data;
  const sentimentStyle = headline.sentiment_level
    ? SENTIMENT_COLORS[headline.sentiment_level]
    : SENTIMENT_COLORS.neutral;
  const SentimentIcon = sentimentStyle.icon;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-indigo-600" />
        <h3 className="font-semibold text-gray-900">Consumer Sentiment Index</h3>
      </div>

      {/* Main Value */}
      <div className="text-center mb-6">
        <div className="text-5xl font-bold text-indigo-600 mb-2">
          {formatValue(headline.value)}
        </div>
        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${sentimentStyle.bg}`}>
          <SentimentIcon className={`w-4 h-4 ${sentimentStyle.text}`} />
          <span className={`text-sm font-medium ${sentimentStyle.text} capitalize`}>
            {headline.sentiment_level?.replace('_', ' ')}
          </span>
        </div>
        {headline.date && (
          <div className="text-xs text-gray-400 mt-2">
            {formatDate(headline.date)}
          </div>
        )}
      </div>

      {/* Changes */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-500 mb-1">Month-over-Month</div>
          <div className={`text-lg font-semibold ${
            headline.mom_change && headline.mom_change >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatChange(headline.mom_change)}
          </div>
          <div className="text-xs text-gray-400">{formatPercent(headline.mom_pct)}</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-xs text-gray-500 mb-1">Year-over-Year</div>
          <div className={`text-lg font-semibold ${
            headline.yoy_change && headline.yoy_change >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {formatChange(headline.yoy_change)}
          </div>
          <div className="text-xs text-gray-400">{formatPercent(headline.yoy_pct)}</div>
        </div>
      </div>

      {/* Historical Context */}
      <div className="border-t pt-4">
        <div className="text-xs font-medium text-gray-500 mb-2">Historical Context</div>
        <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-red-400 via-yellow-400 to-green-400"
            style={{ width: '100%' }}
          />
          <div
            className="absolute top-0 h-full w-1 bg-indigo-700 rounded"
            style={{ left: `${historical_stats.current_percentile}%`, transform: 'translateX(-50%)' }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{historical_stats.all_time_min.toFixed(0)} (Low)</span>
          <span>Avg: {historical_stats.all_time_avg.toFixed(0)}</span>
          <span>{historical_stats.all_time_max.toFixed(0)} (High)</span>
        </div>
        <div className="text-center text-xs text-indigo-600 mt-1">
          Current: {historical_stats.current_percentile.toFixed(0)}th percentile
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// COMPONENTS CARD
// ============================================================================

function ComponentsCard({ data }: { data: OverviewData }) {
  const { components, inflation_expectations } = data;

  const ComponentRow = ({ label, series, color }: { label: string; series: SeriesData | null; color: string }) => {
    if (!series) return null;
    return (
      <div className="flex items-center justify-between py-3 border-b last:border-0">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
          <span className="font-medium text-gray-700">{label}</span>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-gray-900">{formatValue(series.value)}</div>
          <div className="text-xs text-gray-500">
            <span className={series.mom_change && series.mom_change >= 0 ? 'text-green-600' : 'text-red-600'}>
              {formatChange(series.mom_change)} MoM
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-indigo-600" />
        <h3 className="font-semibold text-gray-900">Sentiment Components</h3>
      </div>

      <div className="space-y-1">
        <ComponentRow
          label="Current Conditions"
          series={components.current_conditions}
          color={CHART_COLORS.current}
        />
      </div>

      {/* Inflation Expectations */}
      {inflation_expectations && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center gap-2 mb-2">
            <ThermometerSun className="w-4 h-4 text-red-500" />
            <span className="text-sm font-medium text-gray-700">Inflation Expectations (1Y)</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-red-500">{formatValue(inflation_expectations.value)}%</span>
            <span className={`text-sm ${
              inflation_expectations.mom_change && inflation_expectations.mom_change >= 0
                ? 'text-red-600'
                : 'text-green-600'
            }`}>
              {formatChange(inflation_expectations.mom_change)} MoM
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// SENTIMENT TIMELINE CHART
// ============================================================================

function SentimentTimelineChart({ monthsBack }: { monthsBack: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['sentiment-timeline', monthsBack],
    queryFn: () => sentimentResearchAPI.getTimeline<TimelineData>(monthsBack),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error || !data?.data) return <div className="text-red-500 p-4">Failed to load chart data</div>;

  const chartData = data.data.timeline;

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-white border rounded-lg shadow-lg p-3 text-sm">
        <div className="font-medium text-gray-900 mb-2">{formatDate(label || '')}</div>
        {payload.map((entry, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-gray-600">{entry.name}:</span>
            <span className="font-medium">{formatValue(entry.value)}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <LineChart className="w-5 h-5 text-indigo-600" />
          <h3 className="font-semibold text-gray-900">Sentiment History</h3>
        </div>
        <div className="text-sm text-gray-500">
          {data.data.data_points} data points
        </div>
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
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {/* Reference lines for sentiment thresholds */}
            <ReferenceLine y={100} stroke="#22c55e" strokeDasharray="3 3" label={{ value: 'Optimistic', fontSize: 10, fill: '#22c55e' }} />
            <ReferenceLine y={75} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Neutral', fontSize: 10, fill: '#f59e0b' }} />
            <Line
              type="monotone"
              dataKey="sentiment"
              stroke={CHART_COLORS.sentiment}
              strokeWidth={2}
              dot={false}
              name="Sentiment"
            />
            <Line
              type="monotone"
              dataKey="current_conditions"
              stroke={CHART_COLORS.current}
              strokeWidth={1.5}
              dot={false}
              name="Current Conditions"
              strokeDasharray="5 5"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ============================================================================
// INFLATION EXPECTATIONS CHART
// ============================================================================

function InflationExpectationsChart({ monthsBack }: { monthsBack: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['sentiment-timeline', monthsBack],
    queryFn: () => sentimentResearchAPI.getTimeline<TimelineData>(monthsBack),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error || !data?.data) return <div className="text-red-500 p-4">Failed to load chart data</div>;

  const chartData = data.data.timeline.filter(d => d.inflation_expectations !== null);

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <ThermometerSun className="w-5 h-5 text-red-500" />
        <h3 className="font-semibold text-gray-900">Inflation Expectations (1 Year Ahead)</h3>
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
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Inflation Expectations']}
              labelFormatter={(label) => formatDate(label)}
            />
            <ReferenceLine y={2} stroke="#22c55e" strokeDasharray="3 3" label={{ value: 'Fed Target', fontSize: 10, fill: '#22c55e' }} />
            <Area
              type="monotone"
              dataKey="inflation_expectations"
              stroke={CHART_COLORS.inflation}
              fill="rgba(239, 68, 68, 0.1)"
              strokeWidth={2}
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

export default function SentimentExplorer() {
  const [monthsBack, setMonthsBack] = useState(60);

  const { data: overviewData, isLoading, error } = useQuery({
    queryKey: ['sentiment-overview'],
    queryFn: () => sentimentResearchAPI.getOverview<OverviewData>(),
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
        <div className="text-red-500">Failed to load sentiment data</div>
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
            <h1 className="text-2xl font-bold text-gray-900">Consumer Sentiment Explorer</h1>
            <p className="text-sm text-gray-600 mt-1">University of Michigan Consumer Surveys</p>
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <HeadlineSentimentCard data={overview} />
          <ComponentsCard data={overview} />
        </div>

        {/* Charts */}
        <SentimentTimelineChart monthsBack={monthsBack} />
        <InflationExpectationsChart monthsBack={monthsBack} />

        {/* Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">About Consumer Sentiment</p>
              <p className="text-blue-700">
                The University of Michigan Consumer Sentiment Index measures consumer confidence about personal finances
                and business conditions. A reading above 100 indicates optimism, while below 75 suggests pessimism.
                The index is a leading indicator of consumer spending, which drives roughly 70% of US economic activity.
                Data source: Federal Reserve Economic Data (FRED).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
