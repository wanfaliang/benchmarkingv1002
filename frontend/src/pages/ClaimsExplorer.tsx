import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { claimsResearchAPI } from '../services/api';
import FREDExplorerNav from '../components/FREDExplorerNav';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronDown,
  ChevronUp,
  FileText,
  BarChart3,
  Table,
  LineChart,
  Info,
  Calendar,
  Loader2,
  Activity,
  Map,
  ArrowUpDown,
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
  Bar,
  BarChart,
  Cell,
} from 'recharts';

// ============================================================================
// CONSTANTS & TYPES
// ============================================================================

interface ClaimsSeriesData {
  series_id: string;
  name: string;
  description: string;
  value: number;
  date: string;
  prior_value: number | null;
  wow_change: number | null;
  wow_pct: number | null;
  year_ago_value: number | null;
  yoy_change: number | null;
  yoy_pct: number | null;
}

interface ClaimsOverview {
  as_of: string;
  claims: {
    icsa?: ClaimsSeriesData;
    ccsa?: ClaimsSeriesData;
    icnsa?: ClaimsSeriesData;
    ic4wsa?: ClaimsSeriesData;
    iursa?: ClaimsSeriesData;
    iurnsa?: ClaimsSeriesData;
  };
  icsa_ccsa_ratio: number | null;
}

interface StateClaimsData {
  state_code: string;
  state_name: string;
  iclaims: {
    value: number;
    date: string;
    prior_value: number | null;
    wow_change: number | null;
    wow_pct: number | null;
    period_start_value: number | null;
    period_change: number | null;
    period_pct: number | null;
  } | null;
}

interface StatesOverview {
  as_of: string;
  weeks_back: number;
  states_count: number;
  states: StateClaimsData[];
}

interface TimelinePoint {
  date: string;
  icsa: number | null;
  ccsa: number | null;
  ic4wsa: number | null;
}

interface TimelineData {
  weeks_back: number;
  timeline: TimelinePoint[];
}

interface CompareData {
  current: {
    value: number;
    date: string;
    percentile: number;
  };
  statistics: {
    min: number;
    max: number;
    avg: number;
    median: number;
    p25: number;
    p75: number;
  };
  recent_range: {
    weeks: number;
    min: number;
    max: number;
    avg: number;
  };
}

type ColorKey = 'amber' | 'blue' | 'purple' | 'gray' | 'green' | 'red';

const SECTION_COLORS: Record<ColorKey, { main: string; light: string; border: string }> = {
  amber: { main: '#f59e0b', light: 'bg-amber-50', border: 'border-amber-500' },
  blue: { main: '#3b82f6', light: 'bg-blue-50', border: 'border-blue-500' },
  purple: { main: '#8b5cf6', light: 'bg-violet-50', border: 'border-violet-500' },
  gray: { main: '#6b7280', light: 'bg-gray-50', border: 'border-gray-300' },
  green: { main: '#10b981', light: 'bg-emerald-50', border: 'border-emerald-500' },
  red: { main: '#ef4444', light: 'bg-red-50', border: 'border-red-500' },
};

const PERIOD_OPTIONS = [
  { label: '1Y', value: 52 },
  { label: '2Y', value: 104 },
  { label: '5Y', value: 260 },
  { label: '10Y', value: 520 },
  { label: 'All', value: 2600 },
];

const CHART_COLORS = {
  icsa: '#6366f1',
  ic4wsa: '#f59e0b',
  ccsa: '#10b981',
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return 'N/A';
  if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
  return value.toLocaleString();
};

const formatChange = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '--';
  const sign = value >= 0 ? '+' : '';
  if (Math.abs(value) >= 1000) return `${sign}${(value / 1000).toFixed(1)}K`;
  return `${sign}${value.toLocaleString()}`;
};

const formatPct = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
};

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

const formatShortDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

// ============================================================================
// REUSABLE COMPONENTS
// ============================================================================

interface SectionCardProps {
  title: string;
  description?: string;
  color: ColorKey;
  icon?: React.ElementType;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  collapsible?: boolean;
  rightContent?: React.ReactNode;
}

function SectionCard({ title, description, color, icon: Icon, children, defaultExpanded = true, collapsible = true, rightContent }: SectionCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const colorSet = SECTION_COLORS[color];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6 overflow-hidden">
      <div
        className={`px-5 py-3 ${colorSet.light} border-b-4 ${colorSet.border} flex items-center justify-between ${collapsible ? 'cursor-pointer' : ''}`}
        onClick={() => collapsible && setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          {Icon && <Icon className="w-6 h-6" style={{ color: colorSet.main }} />}
          <div>
            <h3 className="text-lg font-bold" style={{ color: colorSet.main }}>{title}</h3>
            {description && <p className="text-xs text-gray-500">{description}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
          {rightContent}
          {collapsible && (
            <button className="p-1 hover:bg-white/50 rounded" style={{ color: colorSet.main }}>
              {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
          )}
        </div>
      </div>
      {expanded && <div className="p-5">{children}</div>}
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  change?: number | null;
  changePct?: number | null;
  changeLabel?: string;
  period?: string;
  subtitle?: string;
  isLoading?: boolean;
  trendReversed?: boolean; // For claims, up is bad
  color?: string;
}

function MetricCard({ title, value, change, changePct, changeLabel = 'WoW', period, subtitle, isLoading, trendReversed = true, color }: MetricCardProps) {
  // For claims: up is bad (red), down is good (green)
  const isPositive = change !== null && change !== undefined && change > 0;
  const isNegative = change !== null && change !== undefined && change < 0;

  let changeColor = 'text-gray-500';
  if (trendReversed) {
    changeColor = isPositive ? 'text-red-500' : isNegative ? 'text-emerald-500' : 'text-gray-500';
  } else {
    changeColor = isPositive ? 'text-emerald-500' : isNegative ? 'text-red-500' : 'text-gray-500';
  }

  const TrendIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;

  return (
    <div className="p-4 rounded-lg border border-gray-200 bg-white hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-gray-600 font-medium">{title}</p>
        {color && <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />}
      </div>
      {isLoading ? (
        <div className="flex justify-center py-4"><Loader2 className="w-5 h-5 animate-spin text-gray-400" /></div>
      ) : (
        <>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">{value}</span>
            {period && <span className="text-xs text-gray-400">{period}</span>}
          </div>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
          {(change !== null && change !== undefined) && (
            <div className="flex items-center gap-1 mt-2">
              <TrendIcon className={`w-4 h-4 ${changeColor}`} />
              <span className={`text-sm font-semibold ${changeColor}`}>
                {formatChange(change)}
              </span>
              {changePct !== null && changePct !== undefined && (
                <span className={`text-xs ${changeColor}`}>({formatPct(changePct)})</span>
              )}
              <span className="text-xs text-gray-400 ml-1">{changeLabel}</span>
            </div>
          )}
        </>
      )}
    </div>
  );
}

interface ViewToggleProps {
  value: 'chart' | 'table';
  onChange: (v: 'chart' | 'table') => void;
}

function ViewToggle({ value, onChange }: ViewToggleProps) {
  return (
    <div className="flex rounded-lg overflow-hidden border border-gray-300">
      <button
        onClick={() => onChange('chart')}
        className={`px-3 py-1.5 text-xs font-medium flex items-center gap-1 ${value === 'chart' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
      >
        <LineChart className="w-4 h-4" />Chart
      </button>
      <button
        onClick={() => onChange('table')}
        className={`px-3 py-1.5 text-xs font-medium flex items-center gap-1 ${value === 'table' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
      >
        <Table className="w-4 h-4" />Table
      </button>
    </div>
  );
}

interface PeriodSelectorProps {
  value: number;
  onChange: (v: number) => void;
  color?: string;
}

function PeriodSelector({ value, onChange, color = '#3b82f6' }: PeriodSelectorProps) {
  return (
    <div className="flex rounded-lg overflow-hidden border border-gray-300">
      {PERIOD_OPTIONS.map(opt => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-3 py-1.5 text-xs font-medium transition-colors ${value === opt.value ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
          style={value === opt.value ? { backgroundColor: color } : {}}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// ============================================================================
// CLAIMS OVERVIEW SECTION
// ============================================================================

interface ClaimsOverviewSectionProps {
  data: ClaimsOverview | undefined;
  isLoading: boolean;
}

function ClaimsOverviewSection({ data, isLoading }: ClaimsOverviewSectionProps) {
  const icsa = data?.claims?.icsa;
  const ccsa = data?.claims?.ccsa;
  const ic4wsa = data?.claims?.ic4wsa;
  const icnsa = data?.claims?.icnsa;
  const iursa = data?.claims?.iursa;

  return (
    <SectionCard
      title="Claims Overview"
      description={`Latest data as of ${icsa?.date ? formatDate(icsa.date) : '--'}`}
      color="amber"
      icon={FileText}
      collapsible={false}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Initial Claims (SA)"
          value={formatNumber(icsa?.value)}
          change={icsa?.wow_change}
          changePct={icsa?.wow_pct}
          changeLabel="WoW"
          subtitle={`YoY: ${formatPct(icsa?.yoy_pct)}`}
          isLoading={isLoading}
          color={CHART_COLORS.icsa}
        />
        <MetricCard
          title="Continued Claims (SA)"
          value={formatNumber(ccsa?.value)}
          change={ccsa?.wow_change}
          changePct={ccsa?.wow_pct}
          changeLabel="WoW"
          subtitle={`YoY: ${formatPct(ccsa?.yoy_pct)}`}
          isLoading={isLoading}
          color={CHART_COLORS.ccsa}
        />
        <MetricCard
          title="4-Week Moving Avg"
          value={formatNumber(ic4wsa?.value)}
          change={ic4wsa?.wow_change}
          changePct={ic4wsa?.wow_pct}
          changeLabel="WoW"
          subtitle="Smoothed trend indicator"
          isLoading={isLoading}
          color={CHART_COLORS.ic4wsa}
        />
        <MetricCard
          title="Insured Unemp. Rate"
          value={iursa?.value !== undefined ? `${iursa.value.toFixed(1)}%` : 'N/A'}
          change={iursa?.wow_change}
          changePct={iursa?.wow_pct}
          changeLabel="WoW"
          subtitle={`YoY: ${formatPct(iursa?.yoy_pct)}`}
          isLoading={isLoading}
          color="#8b5cf6"
        />
        <MetricCard
          title="Initial Claims (NSA)"
          value={formatNumber(icnsa?.value)}
          change={icnsa?.wow_change}
          changePct={icnsa?.wow_pct}
          changeLabel="WoW"
          subtitle="Not seasonally adjusted"
          isLoading={isLoading}
          trendReversed={true}
        />
      </div>

      {/* Key Insights Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100">
        <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
          <Activity className="w-5 h-5 text-amber-600" />
          <div>
            <p className="text-xs text-gray-500">ICSA/CCSA Ratio</p>
            <p className="text-lg font-bold text-gray-900">{data?.icsa_ccsa_ratio?.toFixed(3) ?? '--'}</p>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
          <Calendar className="w-5 h-5 text-amber-600" />
          <div>
            <p className="text-xs text-gray-500">Release Schedule</p>
            <p className="text-sm font-semibold text-gray-900">Every Thursday, 8:30 AM ET</p>
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
          <FileText className="w-5 h-5 text-amber-600" />
          <div>
            <p className="text-xs text-gray-500">Data Source</p>
            <p className="text-sm font-semibold text-gray-900">U.S. Dept. of Labor</p>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}

// ============================================================================
// HISTORICAL TRENDS SECTION
// ============================================================================

interface HistoricalTrendsSectionProps {
  weeksBack: number;
  onWeeksChange: (w: number) => void;
}

function HistoricalTrendsSection({ weeksBack, onWeeksChange }: HistoricalTrendsSectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [showCCSA, setShowCCSA] = useState(false);

  const { data: timeline, isLoading } = useQuery({
    queryKey: ['claims-timeline', weeksBack],
    queryFn: async () => {
      const res = await claimsResearchAPI.getTimeline<TimelineData>(weeksBack);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const chartData = useMemo(() => {
    if (!timeline?.timeline) return [];
    return timeline.timeline.map(t => ({
      date: formatShortDate(t.date),
      fullDate: t.date,
      icsa: t.icsa,
      ic4wsa: t.ic4wsa,
      ccsa: t.ccsa ? t.ccsa / 1000 : null, // Scale down for dual axis
    }));
  }, [timeline]);

  // Calculate average for reference line
  const icsaAvg = useMemo(() => {
    const values = chartData.map(d => d.icsa).filter((v): v is number => v !== null);
    return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : null;
  }, [chartData]);

  return (
    <SectionCard
      title="Historical Trends"
      description="Weekly claims data over time"
      color="blue"
      icon={BarChart3}
      rightContent={
        <div className="flex gap-2 items-center">
          <label className="flex items-center gap-2 text-xs text-gray-600">
            <input
              type="checkbox"
              checked={showCCSA}
              onChange={(e) => setShowCCSA(e.target.checked)}
              className="rounded text-blue-600"
            />
            Show CCSA
          </label>
          <PeriodSelector value={weeksBack} onChange={onWeeksChange} color={SECTION_COLORS.blue.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      ) : viewMode === 'chart' ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: showCCSA ? 60 : 20, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                tickLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 11 }}
                tickLine={false}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`}
                domain={['auto', 'auto']}
              />
              {showCCSA && (
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  tickFormatter={(v) => `${v.toFixed(0)}K`}
                  domain={['auto', 'auto']}
                  label={{ value: 'CCSA (K)', angle: 90, position: 'insideRight', fontSize: 10 }}
                />
              )}
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8, boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  if (name === 'ccsa') return [`${(value * 1000).toLocaleString()}`, 'Continued Claims'];
                  if (name === 'icsa') return [value?.toLocaleString() ?? 'N/A', 'Initial Claims'];
                  if (name === 'ic4wsa') return [value?.toLocaleString() ?? 'N/A', '4-Week MA'];
                  return [value, name];
                }}
                labelFormatter={(label) => `Week of ${label}`}
              />
              <Legend />
              {icsaAvg && (
                <ReferenceLine
                  yAxisId="left"
                  y={icsaAvg}
                  stroke="#94a3b8"
                  strokeDasharray="5 5"
                  label={{ value: `Avg: ${formatNumber(icsaAvg)}`, fontSize: 10, fill: '#64748b' }}
                />
              )}
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="icsa"
                name="Initial Claims"
                stroke={CHART_COLORS.icsa}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, strokeWidth: 2 }}
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="ic4wsa"
                name="4-Week MA"
                stroke={CHART_COLORS.ic4wsa}
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
              />
              {showCCSA && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="ccsa"
                  name="Continued Claims (K)"
                  stroke={CHART_COLORS.ccsa}
                  strokeWidth={2}
                  dot={false}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="overflow-auto max-h-96">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100">
              <tr>
                <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-10">Week</th>
                <th className="text-right p-2 font-semibold">
                  <div className="flex items-center justify-end gap-1">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS.icsa }} />
                    Initial Claims
                  </div>
                </th>
                <th className="text-right p-2 font-semibold">
                  <div className="flex items-center justify-end gap-1">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS.ic4wsa }} />
                    4-Week MA
                  </div>
                </th>
                <th className="text-right p-2 font-semibold">
                  <div className="flex items-center justify-end gap-1">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS.ccsa }} />
                    Continued Claims
                  </div>
                </th>
                <th className="text-right p-2 font-semibold">WoW Δ</th>
              </tr>
            </thead>
            <tbody>
              {timeline?.timeline?.slice().reverse().map((row, idx, arr) => {
                const prevRow = arr[idx + 1];
                const wowChange = row.icsa && prevRow?.icsa ? row.icsa - prevRow.icsa : null;
                return (
                  <tr key={row.date} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className={`p-2 font-medium sticky left-0 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                      {formatShortDate(row.date)}
                    </td>
                    <td className="text-right p-2 font-mono">{row.icsa?.toLocaleString() ?? '--'}</td>
                    <td className="text-right p-2 font-mono">{row.ic4wsa?.toLocaleString() ?? '--'}</td>
                    <td className="text-right p-2 font-mono">{row.ccsa?.toLocaleString() ?? '--'}</td>
                    <td className={`text-right p-2 font-mono font-semibold ${wowChange !== null ? (wowChange > 0 ? 'text-red-500' : 'text-emerald-500') : ''}`}>
                      {wowChange !== null ? formatChange(wowChange) : '--'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// STATISTICAL ANALYSIS SECTION
// ============================================================================

function StatisticalAnalysisSection() {
  const { data: compareData, isLoading } = useQuery({
    queryKey: ['claims-compare'],
    queryFn: async () => {
      const res = await claimsResearchAPI.compare<CompareData>(520); // 10 years
      return res.data;
    },
    staleTime: 10 * 60 * 1000,
  });

  const barChartData = useMemo(() => {
    if (!compareData) return [];
    return [
      { name: 'Min', value: compareData.statistics.min, fill: '#10b981' },
      { name: 'P25', value: compareData.statistics.p25, fill: '#6ee7b7' },
      { name: 'Avg', value: compareData.statistics.avg, fill: '#94a3b8' },
      { name: 'Current', value: compareData.current.value, fill: '#6366f1' },
      { name: 'P75', value: compareData.statistics.p75, fill: '#fbbf24' },
      { name: 'Max', value: compareData.statistics.max, fill: '#ef4444' },
    ];
  }, [compareData]);

  const percentileColor = useMemo(() => {
    if (!compareData) return 'text-gray-600';
    const p = compareData.current.percentile;
    if (p <= 25) return 'text-emerald-600';
    if (p <= 50) return 'text-blue-600';
    if (p <= 75) return 'text-amber-600';
    return 'text-red-600';
  }, [compareData]);

  return (
    <SectionCard
      title="Statistical Analysis"
      description="Current claims vs. 10-year historical distribution"
      color="purple"
      icon={Activity}
    >
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
        </div>
      ) : compareData ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Stats Cards */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-100">
                <p className="text-xs text-gray-500 mb-1">Current Percentile</p>
                <p className={`text-3xl font-bold ${percentileColor}`}>
                  {compareData.current.percentile.toFixed(0)}th
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {compareData.current.percentile <= 50 ? 'Below median (favorable)' : 'Above median (elevated)'}
                </p>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-100">
                <p className="text-xs text-gray-500 mb-1">vs. 10-Year Average</p>
                <p className={`text-3xl font-bold ${compareData.current.value < compareData.statistics.avg ? 'text-emerald-600' : 'text-red-600'}`}>
                  {((compareData.current.value - compareData.statistics.avg) / compareData.statistics.avg * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Avg: {formatNumber(compareData.statistics.avg)}
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm font-semibold text-gray-700 mb-3">10-Year Distribution</p>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Minimum</span>
                  <span className="font-mono font-semibold text-emerald-600">{formatNumber(compareData.statistics.min)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">25th Percentile</span>
                  <span className="font-mono">{formatNumber(compareData.statistics.p25)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Median</span>
                  <span className="font-mono">{formatNumber(compareData.statistics.median)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">75th Percentile</span>
                  <span className="font-mono">{formatNumber(compareData.statistics.p75)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Maximum</span>
                  <span className="font-mono font-semibold text-red-600">{formatNumber(compareData.statistics.max)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bar Chart */}
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barChartData} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} tickLine={false} tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} />
                <Tooltip
                  formatter={(value: number) => [value.toLocaleString(), 'Claims']}
                  contentStyle={{ fontSize: 12, borderRadius: 8 }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {barChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : null}
    </SectionCard>
  );
}

// ============================================================================
// STATE COMPARISON SECTION
// ============================================================================

type SortField = 'state_name' | 'iclaims' | 'wow_change' | 'wow_pct' | 'period_change' | 'period_pct';
type SortDirection = 'asc' | 'desc';

function StateComparisonSection() {
  const [sortField, setSortField] = useState<SortField>('iclaims');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('table');
  const [weeksBack, setWeeksBack] = useState(52);

  const { data: statesData, isLoading } = useQuery({
    queryKey: ['claims-states-overview', weeksBack],
    queryFn: async () => {
      const res = await claimsResearchAPI.getStatesOverview<StatesOverview>(weeksBack);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const sortedStates = useMemo(() => {
    if (!statesData?.states) return [];
    return [...statesData.states].sort((a, b) => {
      let aVal: number | string | null = null;
      let bVal: number | string | null = null;

      switch (sortField) {
        case 'state_name':
          aVal = a.state_name;
          bVal = b.state_name;
          break;
        case 'iclaims':
          aVal = a.iclaims?.value ?? null;
          bVal = b.iclaims?.value ?? null;
          break;
        case 'wow_change':
          aVal = a.iclaims?.wow_change ?? null;
          bVal = b.iclaims?.wow_change ?? null;
          break;
        case 'wow_pct':
          aVal = a.iclaims?.wow_pct ?? null;
          bVal = b.iclaims?.wow_pct ?? null;
          break;
        case 'period_change':
          aVal = a.iclaims?.period_change ?? null;
          bVal = b.iclaims?.period_change ?? null;
          break;
        case 'period_pct':
          aVal = a.iclaims?.period_pct ?? null;
          bVal = b.iclaims?.period_pct ?? null;
          break;
      }

      if (aVal === null && bVal === null) return 0;
      if (aVal === null) return 1;
      if (bVal === null) return -1;

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }

      return sortDirection === 'asc'
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number);
    });
  }, [statesData, sortField, sortDirection]);

  // Top changers for the chart view
  const topChangers = useMemo(() => {
    if (!statesData?.states) return [];
    return [...statesData.states]
      .filter(s => s.iclaims?.period_pct !== null && s.iclaims?.period_pct !== undefined)
      .sort((a, b) => Math.abs(b.iclaims?.period_pct ?? 0) - Math.abs(a.iclaims?.period_pct ?? 0))
      .slice(0, 15);
  }, [statesData]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const SortHeader = ({ field, label, className = '' }: { field: SortField; label: string; className?: string }) => (
    <th
      className={`text-right p-2 font-semibold cursor-pointer hover:bg-gray-200 select-none ${className}`}
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center justify-end gap-1">
        {label}
        <ArrowUpDown className={`w-3 h-3 ${sortField === field ? 'text-green-600' : 'text-gray-400'}`} />
      </div>
    </th>
  );

  const periodLabel = weeksBack === 52 ? '1Y' : weeksBack === 104 ? '2Y' : weeksBack === 26 ? '6M' : `${weeksBack}W`;

  return (
    <SectionCard
      title="State Comparison"
      description={`${statesData?.states_count ?? 0} states and territories • Initial Claims`}
      color="green"
      icon={Map}
      rightContent={
        <div className="flex gap-2 items-center">
          <PeriodSelector value={weeksBack} onChange={setWeeksBack} color={SECTION_COLORS.green.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-green-500" />
        </div>
      ) : viewMode === 'chart' ? (
        <div className="h-[450px]">
          <p className="text-sm text-gray-500 mb-2 text-center">Top 15 States by {periodLabel} Change (%)</p>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart
              data={topChangers}
              layout="vertical"
              margin={{ top: 10, right: 40, left: 100, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={true} vertical={false} />
              <XAxis
                type="number"
                tick={{ fontSize: 11 }}
                tickLine={false}
                tickFormatter={(v) => `${v > 0 ? '+' : ''}${v.toFixed(0)}%`}
                domain={['auto', 'auto']}
              />
              <YAxis
                type="category"
                dataKey="state_name"
                tick={{ fontSize: 11 }}
                tickLine={false}
                width={95}
              />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 8 }}
                formatter={(value: number) => [`${value > 0 ? '+' : ''}${value.toFixed(1)}%`, `${periodLabel} Change`]}
              />
              <ReferenceLine x={0} stroke="#6b7280" strokeWidth={1} />
              <Bar
                dataKey={(d: StateClaimsData) => d.iclaims?.period_pct}
                name={`${periodLabel} Change`}
                radius={[0, 4, 4, 0]}
              >
                {topChangers.map((entry, index) => {
                  const pct = entry.iclaims?.period_pct ?? 0;
                  return (
                    <Cell
                      key={`cell-${index}`}
                      fill={pct > 0 ? '#ef4444' : '#10b981'}
                    />
                  );
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-6 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-emerald-500" /> Claims decreased over period
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-red-500" /> Claims increased over period
            </span>
          </div>
        </div>
      ) : (
        <div className="overflow-auto max-h-[500px]">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th
                  className="text-left p-2 font-semibold cursor-pointer hover:bg-gray-200 select-none sticky left-0 bg-gray-100"
                  onClick={() => handleSort('state_name')}
                >
                  <div className="flex items-center gap-1">
                    State
                    <ArrowUpDown className={`w-3 h-3 ${sortField === 'state_name' ? 'text-green-600' : 'text-gray-400'}`} />
                  </div>
                </th>
                <SortHeader field="iclaims" label="Current" />
                <SortHeader field="wow_change" label="WoW Δ" />
                <SortHeader field="wow_pct" label="WoW %" />
                <th className="text-right p-2 font-semibold text-gray-400">{periodLabel} Start</th>
                <SortHeader field="period_change" label={`${periodLabel} Δ`} />
                <SortHeader field="period_pct" label={`${periodLabel} %`} />
              </tr>
            </thead>
            <tbody>
              {sortedStates.map((state, idx) => {
                const wowChange = state.iclaims?.wow_change;
                const wowPct = state.iclaims?.wow_pct;
                const periodChange = state.iclaims?.period_change;
                const periodPct = state.iclaims?.period_pct;
                const wowColor = wowChange !== null && wowChange !== undefined
                  ? wowChange > 0 ? 'text-red-500' : wowChange < 0 ? 'text-emerald-500' : 'text-gray-500'
                  : 'text-gray-400';
                const periodColor = periodChange !== null && periodChange !== undefined
                  ? periodChange > 0 ? 'text-red-500' : periodChange < 0 ? 'text-emerald-500' : 'text-gray-500'
                  : 'text-gray-400';

                return (
                  <tr key={state.state_code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className={`p-2 font-medium sticky left-0 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                      <span className="text-gray-400 mr-2">{state.state_code}</span>
                      {state.state_name}
                    </td>
                    <td className="text-right p-2 font-mono font-semibold">
                      {state.iclaims?.value?.toLocaleString() ?? '--'}
                    </td>
                    <td className={`text-right p-2 font-mono ${wowColor}`}>
                      {wowChange !== null && wowChange !== undefined ? formatChange(wowChange) : '--'}
                    </td>
                    <td className={`text-right p-2 font-mono ${wowColor}`}>
                      {wowPct !== null && wowPct !== undefined ? formatPct(wowPct) : '--'}
                    </td>
                    <td className="text-right p-2 font-mono text-gray-400">
                      {state.iclaims?.period_start_value?.toLocaleString() ?? '--'}
                    </td>
                    <td className={`text-right p-2 font-mono ${periodColor}`}>
                      {periodChange !== null && periodChange !== undefined ? formatChange(periodChange) : '--'}
                    </td>
                    <td className={`text-right p-2 font-mono font-semibold ${periodColor}`}>
                      {periodPct !== null && periodPct !== undefined ? formatPct(periodPct) : '--'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary stats */}
      {statesData && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-100">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">WoW Increases</p>
            <p className="text-lg font-bold text-red-600">
              {statesData.states.filter(s => s.iclaims?.wow_change && s.iclaims.wow_change > 0).length}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">WoW Decreases</p>
            <p className="text-lg font-bold text-emerald-600">
              {statesData.states.filter(s => s.iclaims?.wow_change && s.iclaims.wow_change < 0).length}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">{periodLabel} Increases</p>
            <p className="text-lg font-bold text-red-600">
              {statesData.states.filter(s => s.iclaims?.period_change && s.iclaims.period_change > 0).length}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">{periodLabel} Decreases</p>
            <p className="text-lg font-bold text-emerald-600">
              {statesData.states.filter(s => s.iclaims?.period_change && s.iclaims.period_change < 0).length}
            </p>
          </div>
        </div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// ABOUT SECTION
// ============================================================================

function AboutSection() {
  return (
    <SectionCard
      title="About This Data"
      description="Understanding unemployment claims"
      color="gray"
      icon={Info}
      defaultExpanded={false}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">Initial Claims (ICSA)</h4>
          <p className="text-sm text-gray-600 mb-4">
            Measures the number of people filing for unemployment insurance benefits for the first time.
            It's considered a leading indicator of labor market health - rising claims often signal
            economic weakness and potential job losses.
          </p>

          <h4 className="font-semibold text-gray-900 mb-2">Continued Claims (CCSA)</h4>
          <p className="text-sm text-gray-600">
            Measures the number of people who remain on unemployment insurance after their initial claim.
            Also known as "insured unemployment," it indicates how difficult it is for unemployed
            workers to find new jobs.
          </p>
        </div>
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">Key Insights</h4>
          <ul className="text-sm text-gray-600 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-amber-500 mt-0.5">•</span>
              <span><strong>Release:</strong> Every Thursday at 8:30 AM Eastern</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-500 mt-0.5">•</span>
              <span><strong>4-Week MA:</strong> Smooths out weekly volatility for trend analysis</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-500 mt-0.5">•</span>
              <span><strong>NSA Data:</strong> Shows seasonal patterns (e.g., holiday layoffs)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-amber-500 mt-0.5">•</span>
              <span><strong>Market Impact:</strong> Unexpected changes can move equity and bond markets</span>
            </li>
          </ul>

          <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
            <p className="text-xs text-amber-800">
              <strong>Interpretation:</strong> Lower claims generally indicate a healthy labor market.
              Claims below 300K are historically considered strong; above 400K may signal recession risk.
            </p>
          </div>

          {/* TODO: Additional data available in database for future enhancement:
              - Extended Benefits (EB) claims
              - Pandemic Emergency UC (PEUC) - historical
              - State-level Continued Claims (CCLAIMS series)
              - Claims by industry/program type
              - Advance vs revised estimates comparison
          */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-blue-800">
              <strong>Coming Soon:</strong> Extended benefits data, industry breakdowns, and historical program comparisons.
            </p>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function ClaimsExplorer() {
  const [weeksBack, setWeeksBack] = useState(104);

  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['claims-overview'],
    queryFn: async () => {
      const res = await claimsResearchAPI.getOverview<ClaimsOverview>();
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* FRED Explorer Navigation */}
      <FREDExplorerNav />

      {/* Main Content */}
      <div className="px-6 py-6 space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Unemployment Claims Explorer</h1>
          <p className="text-sm text-gray-600 mt-1">FRED Weekly Claims Data • ICSA, CCSA, IC4WSA</p>
        </div>

        <ClaimsOverviewSection data={overview} isLoading={loadingOverview} />
        <HistoricalTrendsSection weeksBack={weeksBack} onWeeksChange={setWeeksBack} />
        <StateComparisonSection />
        <StatisticalAnalysisSection />
        <AboutSection />
      </div>
    </div>
  );
}
