import { useState, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fedfundsResearchAPI } from '../services/api';
import FREDExplorerNav from '../components/FREDExplorerNav';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Table,
  ChevronDown,
  ChevronUp,
  Loader2,
  Activity,
  Target,
  Info,
  BookOpen,
  ExternalLink,
  Calendar,
  ArrowRightLeft,
  Database,
} from 'lucide-react';
import {
  LineChart,
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
} from 'recharts';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface RateChange {
  date: string;
  old_rate: number;
  new_rate: number;
  change_bps: number;
  direction: 'hike' | 'cut';
  cumulative_bps?: number;
}

interface OverviewData {
  as_of: string;
  current: {
    lower_limit: number | null;
    upper_limit: number | null;
    midpoint: number | null;
    effective_rate: number | null;
    date: string | null;
  };
  target_range_display: string | null;
  last_change: RateChange | null;
  recent_changes: RateChange[];
  change_stats: {
    total_changes: number;
    hikes: number;
    cuts: number;
  };
  series_info: {
    last_updated: string | null;
    observation_start: string | null;
  };
}

interface TimelinePoint {
  date: string;
  lower: number | null;
  upper: number | null;
  midpoint: number | null;
  effective: number | null;
}

interface HistoricalTableData {
  years_back: number | string;
  frequency: string;
  data_points: number;
  data: Array<{
    date: string;
    period?: string;
    target_lower: number | null;
    target_upper: number | null;
    target_midpoint: number | null;
    target_range: string | null;
    effective_rate: number | null;
  }>;
}

interface SiblingSeriesData {
  release: {
    id: number;
    name: string;
    link: string;
    notes: string | null;
  };
  categories: Record<string, {
    name: string;
    series: Array<{
      series_id: string;
      title: string;
      frequency: string;
      units: string;
      latest_value: number | null;
      latest_date: string | null;
      observation_start: string | null;
      observation_end: string | null;
      available: boolean;
    }>;
  }>;
}

interface AboutData {
  title: string;
  subtitle: string;
  description: string;
  key_concepts: Array<{ term: string; definition: string }>;
  data_source: {
    name: string;
    provider: string;
    release: string;
    release_id: number;
    url: string;
  };
  series: Array<{
    series_id: string;
    name: string;
    description: string;
    frequency: string;
    category: string;
    title: string | null;
    notes: string | null;
    observation_start: string | null;
    observation_end: string | null;
    last_updated: string | null;
    latest_value: number | null;
    latest_date: string | null;
  }>;
  related_concepts: string[];
}

// OPTIMIZED: Combined chart data from single endpoint
interface ChartData {
  years_back: number;
  timeline: {
    data_points: number;
    total_points: number;
    data: TimelinePoint[];
  };
  comparison: {
    data_points: number;
    total_points: number;
    tracking_stats: {
      avg_deviation_bps: number;
      max_deviation_bps: number;
      within_5bps_pct: number;
    };
    data: Array<{
      date: string;
      target_lower: number;
      target_upper: number;
      target_midpoint: number;
      effective: number;
      deviation_bps: number;
    }>;
  };
  changes: {
    total_changes: number;
    data: RateChange[];
    by_year: Record<string, { hikes: number; cuts: number; net_bps: number }>;
  };
}

type ViewType = 'chart' | 'table';

// ============================================================================
// CONSTANTS
// ============================================================================

const PERIOD_OPTIONS = [
  { label: '1Y', value: 1 },
  { label: '2Y', value: 2 },
  { label: '5Y', value: 5 },
  { label: '10Y', value: 10 },
  { label: '20Y', value: 20 },
  { label: 'All', value: 0 },
];

const CHART_COLORS = {
  lower: '#94a3b8',
  upper: '#475569',
  midpoint: '#6366f1',
  effective: '#f59e0b',
  range: 'rgba(99, 102, 241, 0.15)',
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatDateShort(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    year: 'numeric',
  });
}

function formatRate(value: number | null): string {
  if (value === null || value === undefined) return '-';
  return `${value.toFixed(2)}%`;
}

function formatBps(value: number | null): string {
  if (value === null || value === undefined) return '-';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(0)} bps`;
}

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
    </div>
  );
}

interface SectionCardProps {
  title: string;
  icon: ReactNode;
  color?: 'indigo' | 'amber' | 'green' | 'blue' | 'purple' | 'red';
  defaultOpen?: boolean;
  rightContent?: ReactNode;
  children: ReactNode;
}

function SectionCard({
  title,
  icon,
  color = 'indigo',
  defaultOpen = true,
  rightContent,
  children,
}: SectionCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const colorClasses = {
    indigo: 'border-indigo-500 bg-indigo-50',
    amber: 'border-amber-500 bg-amber-50',
    green: 'border-green-500 bg-green-50',
    blue: 'border-blue-500 bg-blue-50',
    purple: 'border-purple-500 bg-purple-50',
    red: 'border-red-500 bg-red-50',
  };

  const iconColorClasses = {
    indigo: 'text-indigo-600',
    amber: 'text-amber-600',
    green: 'text-green-600',
    blue: 'text-blue-600',
    purple: 'text-purple-600',
    red: 'text-red-600',
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
      <div
        className={`px-5 py-3 border-b-2 ${colorClasses[color]} flex items-center justify-between cursor-pointer`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2">
          <span className={iconColorClasses[color]}>{icon}</span>
          <h2 className="text-lg font-bold text-gray-900">{title}</h2>
        </div>
        <div className="flex items-center gap-4">
          {rightContent && <div onClick={(e) => e.stopPropagation()}>{rightContent}</div>}
          {isOpen ? (
            <ChevronUp className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          )}
        </div>
      </div>
      {isOpen && <div className="p-5">{children}</div>}
    </div>
  );
}

interface ViewToggleProps {
  value: ViewType;
  onChange: (value: ViewType) => void;
}

function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
      <button
        onClick={() => onChange('chart')}
        className={`p-2 rounded-md transition-colors ${
          value === 'chart' ? 'bg-white shadow-sm text-indigo-600' : 'text-gray-500 hover:text-gray-700'
        }`}
        title="Chart View"
      >
        <BarChart3 className="w-4 h-4" />
      </button>
      <button
        onClick={() => onChange('table')}
        className={`p-2 rounded-md transition-colors ${
          value === 'table' ? 'bg-white shadow-sm text-indigo-600' : 'text-gray-500 hover:text-gray-700'
        }`}
        title="Table View"
      >
        <Table className="w-4 h-4" />
      </button>
    </div>
  );
}

interface PeriodSelectorProps {
  value: number;
  onChange: (value: number) => void;
  options?: typeof PERIOD_OPTIONS;
}

function PeriodSelector({ value, onChange, options = PERIOD_OPTIONS }: PeriodSelectorProps) {
  return (
    <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
            value === opt.value
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-200'
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// ============================================================================
// SECTION 1: OVERVIEW
// ============================================================================

function OverviewSection({ data }: { data: OverviewData }) {
  const { current, target_range_display, last_change, change_stats, recent_changes } = data;

  return (
    <SectionCard title="Overview - Current Rate & Summary" icon={<Target className="w-5 h-5" />} color="indigo">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Rate Card */}
        <div className="bg-gradient-to-br from-indigo-50 to-white rounded-lg border border-indigo-200 p-6">
          <div className="text-center mb-6">
            <div className="text-sm font-medium text-gray-500 mb-1">Federal Funds Target Range</div>
            <div className="text-5xl font-bold text-indigo-600 mb-1">{target_range_display || '-'}</div>
            {current.date && (
              <div className="text-xs text-gray-400">As of {formatDate(current.date)}</div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-white rounded-lg p-3 text-center border">
              <div className="text-xs text-gray-500 mb-1">Midpoint</div>
              <div className="text-xl font-semibold text-gray-900">{formatRate(current.midpoint)}</div>
            </div>
            <div className="bg-amber-50 rounded-lg p-3 text-center border border-amber-200">
              <div className="text-xs text-gray-500 mb-1">Effective Rate</div>
              <div className="text-xl font-semibold text-amber-600">{formatRate(current.effective_rate)}</div>
            </div>
          </div>

          {last_change && (
            <div className={`rounded-lg p-3 ${last_change.direction === 'hike' ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {last_change.direction === 'hike' ? (
                    <TrendingUp className="w-4 h-4 text-red-500" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-green-500" />
                  )}
                  <span className="text-sm font-medium text-gray-700">Last Change</span>
                </div>
                <div className={`text-sm font-bold ${last_change.direction === 'hike' ? 'text-red-600' : 'text-green-600'}`}>
                  {formatBps(last_change.change_bps)}
                </div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {formatDate(last_change.date)} • {formatRate(last_change.old_rate)} → {formatRate(last_change.new_rate)}
              </div>
            </div>
          )}
        </div>

        {/* FOMC Summary Card */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-indigo-600" />
            <h3 className="font-semibold text-gray-900">FOMC Rate Decisions</h3>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{change_stats.total_changes}</div>
              <div className="text-xs text-gray-500">Total Changes</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-500">{change_stats.hikes}</div>
              <div className="text-xs text-gray-500">Rate Hikes</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-500">{change_stats.cuts}</div>
              <div className="text-xs text-gray-500">Rate Cuts</div>
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="text-xs font-medium text-gray-500 mb-2">Recent Changes</div>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {recent_changes.slice(0, 6).map((change, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm py-1 border-b border-gray-100 last:border-0">
                  <div className="flex items-center gap-2">
                    {change.direction === 'hike' ? (
                      <TrendingUp className="w-3 h-3 text-red-500" />
                    ) : (
                      <TrendingDown className="w-3 h-3 text-green-500" />
                    )}
                    <span className="text-gray-600">{formatDate(change.date)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400 text-xs">
                      {formatRate(change.old_rate)} → {formatRate(change.new_rate)}
                    </span>
                    <span className={`font-medium ${change.direction === 'hike' ? 'text-red-600' : 'text-green-600'}`}>
                      {formatBps(change.change_bps)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}

// ============================================================================
// SECTION 2: RATE HISTORY
// ============================================================================

interface RateHistorySectionProps {
  timelineData: ChartData['timeline'] | undefined;
  isLoading: boolean;
  yearsBack: number;
  onYearsBackChange: (value: number) => void;
}

function RateHistorySection({ timelineData, isLoading, yearsBack, onYearsBackChange }: RateHistorySectionProps) {
  const [view, setView] = useState<ViewType>('chart');
  const [frequency, setFrequency] = useState<'monthly' | 'daily'>('monthly');

  const { data: tableData, isLoading: tableLoading } = useQuery({
    queryKey: ['fedfunds-historical-table', yearsBack, frequency],
    queryFn: () => fedfundsResearchAPI.getHistoricalTable<HistoricalTableData>(yearsBack, frequency),
    enabled: view === 'table',
    staleTime: 5 * 60 * 1000,
  });

  const sectionLoading = view === 'chart' ? isLoading : tableLoading;

  return (
    <SectionCard
      title="Rate History Timeline"
      icon={<BarChart3 className="w-5 h-5" />}
      color="blue"
      rightContent={
        <div className="flex items-center gap-3">
          <PeriodSelector value={yearsBack} onChange={onYearsBackChange} />
          <ViewToggle value={view} onChange={setView} />
        </div>
      }
    >
      {sectionLoading ? (
        <LoadingSpinner />
      ) : view === 'chart' && timelineData ? (
        <div>
          <div className="mb-2 text-sm text-gray-500">
            {timelineData.data_points.toLocaleString()} data points
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={timelineData.data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(val) => {
                    const d = new Date(val);
                    return d.getFullYear().toString();
                  }}
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
                  content={({ active, payload, label }) => {
                    if (!active || !payload?.length) return null;
                    return (
                      <div className="bg-white border rounded-lg shadow-lg p-3 text-sm">
                        <div className="font-medium text-gray-900 mb-2">{formatDate(String(label || ''))}</div>
                        {payload.map((entry, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
                            <span className="text-gray-600">{entry.name}:</span>
                            <span className="font-medium">{formatRate(entry.value as number)}</span>
                          </div>
                        ))}
                      </div>
                    );
                  }}
                />
                <Legend />
                <Area
                  type="stepAfter"
                  dataKey="upper"
                  stroke="none"
                  fill={CHART_COLORS.range}
                  name="Target Range"
                />
                <Line
                  type="stepAfter"
                  dataKey="upper"
                  stroke={CHART_COLORS.upper}
                  strokeWidth={2}
                  dot={false}
                  name="Upper Limit"
                />
                <Line
                  type="stepAfter"
                  dataKey="lower"
                  stroke={CHART_COLORS.lower}
                  strokeWidth={2}
                  dot={false}
                  name="Lower Limit"
                />
                <Line
                  type="linear"
                  dataKey="effective"
                  stroke={CHART_COLORS.effective}
                  strokeWidth={1.5}
                  dot={false}
                  name="Effective Rate"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : tableData?.data ? (
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm text-gray-500">
              {tableData.data.data_points.toLocaleString()} records
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFrequency('monthly')}
                className={`px-3 py-1 text-xs rounded ${frequency === 'monthly' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}
              >
                Monthly
              </button>
              <button
                onClick={() => setFrequency('daily')}
                className={`px-3 py-1 text-xs rounded ${frequency === 'daily' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}
              >
                Daily
              </button>
            </div>
          </div>
          <div className="overflow-x-auto max-h-[32rem] border rounded-lg">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="text-left p-3 font-semibold text-gray-600">Date</th>
                  <th className="text-right p-3 font-semibold text-gray-600">Target Range</th>
                  <th className="text-right p-3 font-semibold text-gray-600">Lower</th>
                  <th className="text-right p-3 font-semibold text-gray-600">Upper</th>
                  <th className="text-right p-3 font-semibold text-gray-600">Midpoint</th>
                  <th className="text-right p-3 font-semibold text-gray-600">Effective</th>
                </tr>
              </thead>
              <tbody>
                {tableData.data.data.slice(0, 200).map((row, idx) => (
                  <tr key={idx} className="border-t hover:bg-gray-50">
                    <td className="p-3 font-medium">{frequency === 'monthly' ? formatDateShort(row.date) : formatDate(row.date)}</td>
                    <td className="p-3 text-right text-indigo-600 font-medium">{row.target_range || '-'}</td>
                    <td className="p-3 text-right text-gray-500">{formatRate(row.target_lower)}</td>
                    <td className="p-3 text-right text-gray-500">{formatRate(row.target_upper)}</td>
                    <td className="p-3 text-right">{formatRate(row.target_midpoint)}</td>
                    <td className="p-3 text-right text-amber-600">{formatRate(row.effective_rate)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {tableData.data.data.length > 200 && (
            <div className="text-xs text-gray-400 mt-2 text-center">
              Showing first 200 of {tableData.data.data_points} records
            </div>
          )}
        </div>
      ) : (
        <div className="text-gray-500 text-center py-8">No data available</div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// SECTION 3: FOMC RATE DECISIONS
// ============================================================================

interface RateChangesSectionProps {
  changesData: ChartData['changes'] | undefined;
  isLoading: boolean;
  yearsBack: number;
  onYearsBackChange: (value: number) => void;
}

function RateChangesSection({ changesData, isLoading, yearsBack, onYearsBackChange }: RateChangesSectionProps) {
  const [view, setView] = useState<ViewType>('table');

  if (isLoading) return <SectionCard title="FOMC Rate Decisions" icon={<Calendar className="w-5 h-5" />} color="amber"><LoadingSpinner /></SectionCard>;
  if (!changesData) return null;

  const changes = changesData.data;
  const byYear = changesData.by_year;

  return (
    <SectionCard
      title="FOMC Rate Decisions - All Changes"
      icon={<Calendar className="w-5 h-5" />}
      color="amber"
      rightContent={
        <div className="flex items-center gap-3">
          <PeriodSelector value={yearsBack} onChange={onYearsBackChange} />
          <ViewToggle value={view} onChange={setView} />
        </div>
      }
    >
      {/* Year Summary */}
      <div className="mb-4">
        <div className="text-xs font-medium text-gray-500 mb-2">Summary by Year</div>
        <div className="flex flex-wrap gap-2">
          {Object.entries(byYear)
            .sort((a, b) => b[0].localeCompare(a[0]))
            .slice(0, 15)
            .map(([year, stats]) => (
              <div key={year} className="bg-gray-50 rounded px-2 py-1 text-xs border">
                <span className="font-medium">{year}:</span>
                {stats.hikes > 0 && <span className="text-red-500 ml-1">+{stats.hikes}</span>}
                {stats.cuts > 0 && <span className="text-green-500 ml-1">-{stats.cuts}</span>}
                <span className={`ml-1 ${stats.net_bps >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  ({stats.net_bps >= 0 ? '+' : ''}{stats.net_bps} bps)
                </span>
              </div>
            ))}
        </div>
      </div>

      {view === 'chart' ? (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={changes.slice().reverse().map((c, i) => ({
                ...c,
                idx: i,
                dateDisplay: formatDate(c.date),
              }))}
              margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="dateDisplay" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
              <YAxis tickFormatter={(val) => `${val}%`} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="stepAfter" dataKey="new_rate" stroke="#6366f1" strokeWidth={2} dot={false} name="Fed Funds Rate" />
              <ReferenceLine y={0} stroke="#94a3b8" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="overflow-x-auto max-h-[32rem] border rounded-lg">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="text-left p-3 font-semibold text-gray-600">Date</th>
                <th className="text-right p-3 font-semibold text-gray-600">Old Rate</th>
                <th className="text-right p-3 font-semibold text-gray-600">New Rate</th>
                <th className="text-right p-3 font-semibold text-gray-600">Change</th>
                <th className="text-center p-3 font-semibold text-gray-600">Direction</th>
              </tr>
            </thead>
            <tbody>
              {changes.map((change, idx) => (
                <tr key={idx} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-medium">{formatDate(change.date)}</td>
                  <td className="p-3 text-right text-gray-600">{formatRate(change.old_rate)}</td>
                  <td className="p-3 text-right font-medium">{formatRate(change.new_rate)}</td>
                  <td className={`p-3 text-right font-bold ${change.direction === 'hike' ? 'text-red-600' : 'text-green-600'}`}>
                    {formatBps(change.change_bps)}
                  </td>
                  <td className="p-3 text-center">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                      change.direction === 'hike' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {change.direction === 'hike' ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      {change.direction === 'hike' ? 'Hike' : 'Cut'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-3 text-sm text-gray-500">
        Total: {changesData.total_changes} rate changes in the selected period
      </div>
    </SectionCard>
  );
}

// ============================================================================
// SECTION 4: EFFECTIVE VS TARGET COMPARISON
// ============================================================================

interface EffectiveVsTargetSectionProps {
  comparisonData: ChartData['comparison'] | undefined;
  isLoading: boolean;
  yearsBack: number;
  onYearsBackChange: (value: number) => void;
}

function EffectiveVsTargetSection({ comparisonData, isLoading, yearsBack, onYearsBackChange }: EffectiveVsTargetSectionProps) {
  const [view, setView] = useState<ViewType>('chart');

  if (isLoading) return <SectionCard title="Effective vs Target Comparison" icon={<ArrowRightLeft className="w-5 h-5" />} color="green"><LoadingSpinner /></SectionCard>;
  if (!comparisonData) return null;

  const { tracking_stats, data: comparison } = comparisonData;

  return (
    <SectionCard
      title="Effective vs Target Comparison"
      icon={<ArrowRightLeft className="w-5 h-5" />}
      color="green"
      rightContent={
        <div className="flex items-center gap-3">
          <PeriodSelector value={yearsBack} onChange={onYearsBackChange} />
          <ViewToggle value={view} onChange={setView} />
        </div>
      }
    >
      {/* Tracking Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-green-50 rounded-lg p-4 text-center border border-green-200">
          <div className="text-2xl font-bold text-green-600">{tracking_stats.avg_deviation_bps.toFixed(1)}</div>
          <div className="text-xs text-gray-500">Avg Deviation (bps)</div>
        </div>
        <div className="bg-amber-50 rounded-lg p-4 text-center border border-amber-200">
          <div className="text-2xl font-bold text-amber-600">{tracking_stats.max_deviation_bps.toFixed(1)}</div>
          <div className="text-xs text-gray-500">Max Deviation (bps)</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
          <div className="text-2xl font-bold text-blue-600">{tracking_stats.within_5bps_pct.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Within 5 bps</div>
        </div>
      </div>

      {view === 'chart' ? (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={comparison.slice(-365)} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="date"
                tickFormatter={(val) => formatDateShort(val)}
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
              />
              <YAxis
                yAxisId="rate"
                tickFormatter={(val) => `${val}%`}
                tick={{ fontSize: 11 }}
                orientation="left"
              />
              <YAxis
                yAxisId="bps"
                tickFormatter={(val) => `${val}`}
                tick={{ fontSize: 11 }}
                orientation="right"
                domain={[-20, 20]}
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length) return null;
                  const p = payload[0]?.payload;
                  return (
                    <div className="bg-white border rounded-lg shadow-lg p-3 text-sm">
                      <div className="font-medium text-gray-900 mb-2">{formatDate(String(label || ''))}</div>
                      <div>Target Midpoint: {formatRate(p?.target_midpoint)}</div>
                      <div>Effective Rate: {formatRate(p?.effective)}</div>
                      <div className={`font-medium ${p?.deviation_bps >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        Deviation: {p?.deviation_bps?.toFixed(1)} bps
                      </div>
                    </div>
                  );
                }}
              />
              <Legend />
              <Line yAxisId="rate" type="monotone" dataKey="target_midpoint" stroke="#6366f1" strokeWidth={2} dot={false} name="Target Midpoint" />
              <Line yAxisId="rate" type="monotone" dataKey="effective" stroke="#f59e0b" strokeWidth={2} dot={false} name="Effective Rate" />
              <Line yAxisId="bps" type="monotone" dataKey="deviation_bps" stroke="#10b981" strokeWidth={1} dot={false} name="Deviation (bps)" />
              <ReferenceLine yAxisId="bps" y={0} stroke="#94a3b8" strokeDasharray="3 3" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="overflow-x-auto max-h-[32rem] border rounded-lg">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="text-left p-3 font-semibold text-gray-600">Date</th>
                <th className="text-right p-3 font-semibold text-gray-600">Target Range</th>
                <th className="text-right p-3 font-semibold text-gray-600">Midpoint</th>
                <th className="text-right p-3 font-semibold text-gray-600">Effective</th>
                <th className="text-right p-3 font-semibold text-gray-600">Deviation</th>
              </tr>
            </thead>
            <tbody>
              {comparison.slice().reverse().slice(0, 100).map((row, idx) => (
                <tr key={idx} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-medium">{formatDate(row.date)}</td>
                  <td className="p-3 text-right text-gray-600">{formatRate(row.target_lower)} - {formatRate(row.target_upper)}</td>
                  <td className="p-3 text-right">{formatRate(row.target_midpoint)}</td>
                  <td className="p-3 text-right text-amber-600">{formatRate(row.effective)}</td>
                  <td className={`p-3 text-right font-medium ${row.deviation_bps >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {row.deviation_bps.toFixed(1)} bps
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
        <Info className="w-4 h-4 inline mr-1" />
        The effective rate shows how closely actual interbank lending rates track the Fed's target.
        Small deviations indicate effective monetary policy transmission.
      </div>
    </SectionCard>
  );
}

// ============================================================================
// SECTION 5: ABOUT & RELATED SERIES
// ============================================================================

function AboutSection() {
  const { data: aboutData, isLoading: aboutLoading } = useQuery({
    queryKey: ['fedfunds-about'],
    queryFn: () => fedfundsResearchAPI.getAbout<AboutData>(),
    staleTime: 30 * 60 * 1000, // 30 minutes - static data
  });

  const { data: siblingsData, isLoading: siblingsLoading } = useQuery({
    queryKey: ['fedfunds-siblings'],
    queryFn: () => fedfundsResearchAPI.getSiblingsSeries<SiblingSeriesData>(),
    staleTime: 30 * 60 * 1000, // 30 minutes - static data
  });

  const isLoading = aboutLoading || siblingsLoading;

  if (isLoading) return <SectionCard title="About & Related Series" icon={<BookOpen className="w-5 h-5" />} color="purple" defaultOpen={false}><LoadingSpinner /></SectionCard>;

  const about = aboutData?.data;
  const siblings = siblingsData?.data;

  return (
    <SectionCard
      title="About & Related Series"
      icon={<BookOpen className="w-5 h-5" />}
      color="purple"
      defaultOpen={false}
    >
      <div className="space-y-6">
        {/* About */}
        {about && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">{about.title}</h3>
            <p className="text-sm text-gray-600 mb-4 whitespace-pre-line">{about.description}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              {about.key_concepts.map((concept, idx) => (
                <div key={idx} className="bg-gray-50 rounded-lg p-3">
                  <div className="font-medium text-gray-900 text-sm">{concept.term}</div>
                  <div className="text-xs text-gray-600 mt-1">{concept.definition}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Primary Series */}
        {about && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <Database className="w-4 h-4" />
              Primary Data Series
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {about.series.map((s) => (
                <div key={s.series_id} className="bg-indigo-50 rounded-lg p-3 border border-indigo-200">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-indigo-600">{s.series_id}</span>
                    <span className="text-xs text-gray-500">{s.frequency}</span>
                  </div>
                  <div className="font-medium text-sm text-gray-900 mt-1">{s.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{s.description}</div>
                  {s.latest_value !== null && (
                    <div className="mt-2 text-sm">
                      Latest: <span className="font-semibold">{formatRate(s.latest_value)}</span>
                      <span className="text-gray-400 ml-1">({s.latest_date})</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sibling Series from H.15 Release */}
        {siblings && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <ExternalLink className="w-4 h-4" />
              Related Series from {siblings.release.name}
            </h4>
            <p className="text-xs text-gray-500 mb-3">
              Other interest rate series from the same Federal Reserve release
            </p>

            <div className="space-y-4">
              {Object.entries(siblings.categories).map(([key, category]) => (
                <div key={key}>
                  <div className="text-sm font-medium text-gray-700 mb-2">{category.name}</div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                    {category.series.filter(s => s.available).map((s) => (
                      <div key={s.series_id} className="bg-gray-50 rounded p-2 border text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-blue-600">{s.series_id}</span>
                          {s.latest_value !== null && (
                            <span className="font-semibold">{formatRate(s.latest_value)}</span>
                          )}
                        </div>
                        <div className="text-gray-600 mt-1 truncate" title={s.title}>
                          {s.title}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Data Source */}
        {about && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-medium text-blue-900 mb-1">Data Source</div>
                <div className="text-sm text-blue-800">
                  {about.data_source.name} ({about.data_source.provider})
                  <br />
                  Release: {about.data_source.release}
                </div>
                <a
                  href={about.data_source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-blue-600 hover:underline text-sm mt-2"
                >
                  Visit FRED <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </SectionCard>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function FedFundsExplorer() {
  // Shared years back state for all chart sections
  const [yearsBack, setYearsBack] = useState(5);

  const { data: overviewData, isLoading: overviewLoading, error: overviewError } = useQuery({
    queryKey: ['fedfunds-overview'],
    queryFn: () => fedfundsResearchAPI.getOverview<OverviewData>(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // OPTIMIZED: Single combined endpoint for all chart data
  const { data: chartData, isLoading: chartLoading } = useQuery({
    queryKey: ['fedfunds-chart-data', yearsBack],
    queryFn: () => fedfundsResearchAPI.getChartData<ChartData>(yearsBack),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (overviewLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (overviewError || !overviewData?.data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-500">Failed to load Fed Funds data</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* FRED Explorer Navigation */}
      <FREDExplorerNav />

      {/* Content */}
      <div className="px-6 py-6 space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Fed Funds Rate Explorer</h1>
          <p className="text-sm text-gray-600 mt-1">Federal Reserve Interest Rate Policy • H.15 Release</p>
        </div>

        <OverviewSection data={overviewData.data} />
        <RateHistorySection
          timelineData={chartData?.data?.timeline}
          isLoading={chartLoading}
          yearsBack={yearsBack}
          onYearsBackChange={setYearsBack}
        />
        <RateChangesSection
          changesData={chartData?.data?.changes}
          isLoading={chartLoading}
          yearsBack={yearsBack}
          onYearsBackChange={setYearsBack}
        />
        <EffectiveVsTargetSection
          comparisonData={chartData?.data?.comparison}
          isLoading={chartLoading}
          yearsBack={yearsBack}
          onYearsBackChange={setYearsBack}
        />
        <AboutSection />
      </div>
    </div>
  );
}
