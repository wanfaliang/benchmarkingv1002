import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { leadingResearchAPI } from '../services/api';
import FREDExplorerNav from '../components/FREDExplorerNav';
import {
  TrendingUp,
  LineChart,
  Info,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Clock,
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
  ReferenceLine,
  ReferenceArea,
} from 'recharts';

// ============================================================================
// TYPES
// ============================================================================

interface RecessionPeriod {
  start_date: string;
  end_date: string | null;
  duration_months: number;
  ongoing?: boolean;
  months_since_previous?: number;
}

interface OverviewData {
  as_of: string;
  leading_index: {
    value: number | null;
    date: string | null;
    trend: string | null;
    consecutive_declines: number | null;
  };
  recession_status: {
    in_recession: boolean;
    nber_indicator: number | null;
    date: string | null;
  };
  recession_probability: {
    value: number | null;
    date: string | null;
    risk_level: string | null;
  };
  recent_recessions: RecessionPeriod[];
  recession_stats: {
    total_recessions: number;
    avg_duration_months: number | null;
  };
  series_info: {
    last_updated: string | null;
  };
}

interface TimelinePoint {
  date: string;
  leading_index: number | null;
  recession: number | null;
  recession_probability: number | null;
}

interface TimelineData {
  months_back: number;
  data_points: number;
  timeline: TimelinePoint[];
}

interface SignalsData {
  as_of: string;
  signals: {
    leading_index: {
      signal: string;
      consecutive_declines: number;
      value: number | null;
    };
    yield_curve: {
      signal: string;
      spread_10y3m: number | null;
      spread_10y2y: number | null;
    };
    probability_model: {
      signal: string;
      probability: number | null;
    };
  };
  overall_assessment: string;
  warning_count: number;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const PERIOD_OPTIONS = [
  { label: '5Y', value: 60 },
  { label: '10Y', value: 120 },
  { label: '20Y', value: 240 },
  { label: '30Y', value: 360 },
  { label: '50Y', value: 600 },
];

const RISK_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  low: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
  moderate: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-300' },
  elevated: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300' },
  high: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' },
};

const SIGNAL_COLORS: Record<string, string> = {
  neutral: 'text-gray-500',
  caution: 'text-yellow-600',
  warning: 'text-red-600',
  inverted: 'text-red-600',
  flattening: 'text-yellow-600',
  low: 'text-green-600',
  moderate: 'text-yellow-600',
  elevated: 'text-orange-600',
  high: 'text-red-600',
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

function formatValue(value: number | null, decimals: number = 1): string {
  if (value === null || value === undefined) return '-';
  return value.toFixed(decimals);
}

// ============================================================================
// RECESSION STATUS CARD
// ============================================================================

function RecessionStatusCard({ data }: { data: OverviewData }) {
  const { recession_status, recession_probability, recession_stats } = data;
  const riskStyle = recession_probability.risk_level
    ? RISK_COLORS[recession_probability.risk_level]
    : RISK_COLORS.low;

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-indigo-600" />
        <h3 className="font-semibold text-gray-900">Recession Status</h3>
      </div>

      {/* Current Status */}
      <div className="mb-6">
        {recession_status.in_recession ? (
          <div className="bg-red-100 border border-red-300 rounded-lg p-4 text-center">
            <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <div className="text-lg font-bold text-red-700">IN RECESSION</div>
            <div className="text-sm text-red-600">NBER Official Dating</div>
          </div>
        ) : (
          <div className="bg-green-100 border border-green-300 rounded-lg p-4 text-center">
            <CheckCircle2 className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <div className="text-lg font-bold text-green-700">EXPANSION</div>
            <div className="text-sm text-green-600">No recession indicated</div>
          </div>
        )}
      </div>

      {/* Recession Probability */}
      <div className={`rounded-lg p-4 border ${riskStyle.bg} ${riskStyle.border} mb-4`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Recession Probability</span>
          <span className={`text-2xl font-bold ${riskStyle.text}`}>
            {formatValue(recession_probability.value)}%
          </span>
        </div>
        <div className="text-xs text-gray-500">
          Risk Level: <span className={`font-medium ${riskStyle.text} capitalize`}>
            {recession_probability.risk_level}
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="border-t pt-4">
        <div className="text-xs font-medium text-gray-500 mb-2">Historical Context</div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Total Recessions:</span>
            <span className="font-medium ml-1">{recession_stats.total_recessions}</span>
          </div>
          <div>
            <span className="text-gray-500">Avg Duration:</span>
            <span className="font-medium ml-1">{formatValue(recession_stats.avg_duration_months)} mo</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// LEADING INDEX CARD
// ============================================================================

function LeadingIndexCard({ data }: { data: OverviewData }) {
  const { leading_index } = data;

  const trendColor = leading_index.trend === 'deteriorating'
    ? 'text-red-600'
    : leading_index.trend === 'improving'
    ? 'text-green-600'
    : 'text-yellow-600';

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5 text-indigo-600" />
        <h3 className="font-semibold text-gray-900">Leading Economic Index</h3>
      </div>

      {/* Current Value */}
      <div className="text-center mb-6">
        <div className="text-4xl font-bold text-indigo-600 mb-1">
          {formatValue(leading_index.value)}%
        </div>
        <div className="text-sm text-gray-500">Monthly Change</div>
        {leading_index.date && (
          <div className="text-xs text-gray-400 mt-1">{formatDate(leading_index.date)}</div>
        )}
      </div>

      {/* Trend Indicator */}
      <div className={`rounded-lg p-4 ${
        leading_index.trend === 'deteriorating' ? 'bg-red-50' :
        leading_index.trend === 'improving' ? 'bg-green-50' : 'bg-yellow-50'
      }`}>
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Trend</span>
          <span className={`font-semibold capitalize ${trendColor}`}>
            {leading_index.trend || 'N/A'}
          </span>
        </div>
        {leading_index.consecutive_declines && leading_index.consecutive_declines > 0 && (
          <div className="text-xs text-red-600 mt-1">
            {leading_index.consecutive_declines} consecutive monthly declines
          </div>
        )}
      </div>

      {/* Warning Note */}
      {leading_index.consecutive_declines && leading_index.consecutive_declines >= 6 && (
        <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg">
          <div className="flex items-center gap-2 text-red-700 text-sm">
            <AlertTriangle className="w-4 h-4" />
            <span className="font-medium">Recession Warning Signal</span>
          </div>
          <div className="text-xs text-red-600 mt-1">
            6+ consecutive declines in the LEI often precede recessions
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// SIGNALS DASHBOARD
// ============================================================================

function SignalsDashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['leading-signals'],
    queryFn: () => leadingResearchAPI.getSignals<SignalsData>(),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error || !data?.data) return null;

  const { signals, overall_assessment, warning_count } = data.data;

  const overallColor = overall_assessment === 'elevated_risk'
    ? 'bg-red-100 border-red-300 text-red-700'
    : overall_assessment === 'caution'
    ? 'bg-yellow-100 border-yellow-300 text-yellow-700'
    : 'bg-green-100 border-green-300 text-green-700';

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-indigo-600" />
          <h3 className="font-semibold text-gray-900">Recession Warning Signals</h3>
        </div>
        <div className={`px-3 py-1 rounded-full border text-sm font-medium ${overallColor}`}>
          {warning_count} / 3 signals active
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Leading Index Signal */}
        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-2">Leading Index</div>
          <div className={`text-lg font-semibold capitalize ${SIGNAL_COLORS[signals.leading_index.signal] || 'text-gray-600'}`}>
            {signals.leading_index.signal}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {signals.leading_index.consecutive_declines} declines • {formatValue(signals.leading_index.value)}%
          </div>
        </div>

        {/* Yield Curve Signal */}
        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-2">Yield Curve</div>
          <div className={`text-lg font-semibold capitalize ${SIGNAL_COLORS[signals.yield_curve.signal] || 'text-gray-600'}`}>
            {signals.yield_curve.signal}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            10Y-3M: {formatValue(signals.yield_curve.spread_10y3m, 2)}%
          </div>
        </div>

        {/* Probability Model Signal */}
        <div className="border rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-2">Probability Model</div>
          <div className={`text-lg font-semibold capitalize ${SIGNAL_COLORS[signals.probability_model.signal] || 'text-gray-600'}`}>
            {signals.probability_model.signal}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {formatValue(signals.probability_model.probability)}% probability
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// TIMELINE CHART
// ============================================================================

function LeadingTimelineChart({ monthsBack }: { monthsBack: number }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['leading-timeline', monthsBack],
    queryFn: () => leadingResearchAPI.getTimeline<TimelineData>(monthsBack),
  });

  if (isLoading) return <LoadingSpinner />;
  if (error || !data?.data) return <div className="text-red-500 p-4">Failed to load chart data</div>;

  const chartData = data.data.timeline;

  // Find recession periods for shading
  const recessionRanges: { start: string; end: string }[] = [];
  let inRecession = false;
  let recStart = '';

  for (const point of chartData) {
    if (point.recession === 1 && !inRecession) {
      inRecession = true;
      recStart = point.date;
    } else if (point.recession === 0 && inRecession) {
      inRecession = false;
      recessionRanges.push({ start: recStart, end: point.date });
    }
  }
  if (inRecession) {
    recessionRanges.push({ start: recStart, end: chartData[chartData.length - 1]?.date });
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <LineChart className="w-5 h-5 text-indigo-600" />
          <h3 className="font-semibold text-gray-900">Leading Index & Recession History</h3>
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
              yAxisId="left"
              tickFormatter={(val) => `${val}%`}
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              tickFormatter={(val) => `${val}%`}
              tick={{ fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              domain={[0, 100]}
            />
            <Tooltip
              formatter={(value: number, name: string) => [
                name === 'recession_probability' ? `${value?.toFixed(1)}%` : `${value?.toFixed(2)}%`,
                name === 'leading_index' ? 'Leading Index' : 'Recession Probability'
              ]}
              labelFormatter={(label) => formatDate(label)}
            />
            <Legend />
            {/* Recession shading */}
            {recessionRanges.map((range, idx) => (
              <ReferenceArea
                key={idx}
                yAxisId="left"
                x1={range.start}
                x2={range.end}
                fill="#fecaca"
                fillOpacity={0.5}
              />
            ))}
            <ReferenceLine yAxisId="left" y={0} stroke="#9ca3af" strokeDasharray="3 3" />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="leading_index"
              stroke="#6366f1"
              strokeWidth={2}
              dot={false}
              name="Leading Index"
            />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="recession_probability"
              stroke="#ef4444"
              fill="rgba(239, 68, 68, 0.1)"
              strokeWidth={1.5}
              name="Recession Probability"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-200 rounded" />
          <span>Recession Period</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// RECENT RECESSIONS TABLE
// ============================================================================

function RecentRecessionsTable({ recessions }: { recessions: RecessionPeriod[] }) {
  if (!recessions.length) return null;

  return (
    <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
      <div className="p-4 border-b">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-indigo-600" />
          <h3 className="font-semibold text-gray-900">Recent Recessions</h3>
        </div>
      </div>

      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left p-3 font-medium text-gray-600">Period</th>
            <th className="text-right p-3 font-medium text-gray-600">Duration</th>
            <th className="text-right p-3 font-medium text-gray-600">Status</th>
          </tr>
        </thead>
        <tbody>
          {recessions.map((rec, idx) => (
            <tr key={idx} className="border-b hover:bg-gray-50">
              <td className="p-3">
                <span className="font-medium">{formatDate(rec.start_date)}</span>
                <span className="text-gray-400 mx-1">→</span>
                <span>{rec.end_date ? formatDate(rec.end_date) : 'Present'}</span>
              </td>
              <td className="p-3 text-right">
                {rec.duration_months} months
              </td>
              <td className="p-3 text-right">
                {rec.ongoing ? (
                  <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                    Ongoing
                  </span>
                ) : (
                  <span className="text-gray-500">Ended</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function LeadingIndexExplorer() {
  const [monthsBack, setMonthsBack] = useState(120);

  const { data: overviewData, isLoading, error } = useQuery({
    queryKey: ['leading-overview'],
    queryFn: () => leadingResearchAPI.getOverview<OverviewData>(),
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
        <div className="text-red-500">Failed to load leading index data</div>
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
            <h1 className="text-2xl font-bold text-gray-900">Leading Index & Recession Explorer</h1>
            <p className="text-sm text-gray-600 mt-1">Economic Cycle Indicators</p>
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
          <RecessionStatusCard data={overview} />
          <LeadingIndexCard data={overview} />
        </div>

        {/* Signals Dashboard */}
        <SignalsDashboard />

        {/* Timeline Chart */}
        <LeadingTimelineChart monthsBack={monthsBack} />

        {/* Recent Recessions */}
        <RecentRecessionsTable recessions={overview.recent_recessions} />

        {/* Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">About Economic Cycle Indicators</p>
              <p className="text-blue-700">
                The Conference Board Leading Economic Index (LEI) is a composite of 10 indicators designed to signal
                peaks and troughs in the business cycle. Six consecutive monthly declines often precede recessions.
                Recession probabilities are calculated using a smoothed model based on nonfarm payrolls, industrial
                production, and other economic data. Data source: Federal Reserve Economic Data (FRED).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
