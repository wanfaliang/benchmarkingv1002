import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fredResearchAPI } from '../services/api';
import FREDExplorerNav from '../components/FREDExplorerNav';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronDown,
  ChevronUp,
  Info,
  Loader2,
  Activity,
  AlertTriangle,
  Table,
  LineChart,
} from 'lucide-react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Area,
  ReferenceLine,
} from 'recharts';

// ============================================================================
// TYPES
// ============================================================================

interface CurvePoint {
  tenor: string;
  series_id: string;
  yield: number | null;
  date: string | null;
  source: string | null;
  daily_change_bps: number | null;
  weekly_change_bps: number | null;
  monthly_change_bps: number | null;
}

interface TipsPoint {
  tenor: string;
  series_id: string;
  real_yield: number;
  date: string;
}

interface BreakevenPoint {
  tenor: string;
  series_id: string;
  breakeven: number;
  date: string;
}

interface YieldCurveData {
  as_of_date: string;
  curve: CurvePoint[];
  spreads: Record<string, number>;
  tips_real_yields: TipsPoint[];
  breakeven_inflation: BreakevenPoint[];
}

interface SpreadHistoryData {
  spread: string;
  data: { date: string; value: number }[];
}

type ChangeView = 'daily' | 'weekly' | 'monthly';
type ColorKey = 'indigo' | 'blue' | 'purple' | 'gray' | 'green' | 'amber' | 'red';

// ============================================================================
// CONSTANTS
// ============================================================================

const SECTION_COLORS: Record<ColorKey, { main: string; light: string; border: string }> = {
  indigo: { main: '#4f46e5', light: 'bg-indigo-50', border: 'border-indigo-500' },
  blue: { main: '#3b82f6', light: 'bg-blue-50', border: 'border-blue-500' },
  purple: { main: '#8b5cf6', light: 'bg-violet-50', border: 'border-violet-500' },
  gray: { main: '#6b7280', light: 'bg-gray-50', border: 'border-gray-300' },
  green: { main: '#10b981', light: 'bg-emerald-50', border: 'border-emerald-500' },
  amber: { main: '#f59e0b', light: 'bg-amber-50', border: 'border-amber-500' },
  red: { main: '#ef4444', light: 'bg-red-50', border: 'border-red-500' },
};

const TENOR_ORDER = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y'];
const TENOR_MONTHS: Record<string, number> = {
  '1M': 1, '3M': 3, '6M': 6, '1Y': 12, '2Y': 24, '3Y': 36,
  '5Y': 60, '7Y': 84, '10Y': 120, '20Y': 240, '30Y': 360,
};

const SPREAD_OPTIONS = [
  { label: '2s10s', value: '2s10s' },
  { label: '2s30s', value: '2s30s' },
  { label: '5s30s', value: '5s30s' },
  { label: '3m10y', value: '3m10y' },
];

const PERIOD_OPTIONS = [
  { label: '1Y', value: 365 },
  { label: '2Y', value: 730 },
  { label: '5Y', value: 1825 },
  { label: '10Y', value: 3650 },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

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

interface ChangeDisplayProps {
  value: number | null;
  unit?: string;
}

function ChangeDisplay({ value, unit = 'bps' }: ChangeDisplayProps) {
  if (value === null || value === undefined) return <span className="text-gray-400">—</span>;

  const isPositive = value > 0;
  const isNegative = value < 0;
  const color = isPositive ? 'text-red-500' : isNegative ? 'text-emerald-500' : 'text-gray-500';
  const Icon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;
  const sign = value > 0 ? '+' : '';

  return (
    <div className="flex items-center gap-1 justify-end">
      <Icon className={`w-4 h-4 ${color}`} />
      <span className={`font-mono font-medium ${color}`}>
        {sign}{value.toFixed(1)} {unit}
      </span>
    </div>
  );
}

// ============================================================================
// YIELD CURVE SECTION
// ============================================================================

interface YieldCurveSectionProps {
  data: YieldCurveData;
}

function YieldCurveSection({ data }: YieldCurveSectionProps) {
  const chartData = useMemo(() => {
    return TENOR_ORDER.map(tenor => {
      const point = data.curve.find(p => p.tenor === tenor);
      return {
        tenor,
        months: TENOR_MONTHS[tenor],
        yield: point?.yield ?? null,
      };
    }).filter(d => d.yield !== null);
  }, [data]);

  return (
    <SectionCard
      title="Treasury Yield Curve"
      description={`U.S. Treasury Constant Maturity Rates — As of ${formatDate(data.as_of_date)}`}
      color="indigo"
      icon={Activity}
      collapsible={false}
    >
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="tenor"
              tick={{ fontSize: 12 }}
              tickLine={false}
            />
            <YAxis
              domain={['auto', 'auto']}
              tick={{ fontSize: 12 }}
              tickLine={false}
              tickFormatter={(v) => `${v.toFixed(2)}%`}
            />
            <Tooltip
              formatter={(value: number) => [`${value.toFixed(3)}%`, 'Yield']}
              labelFormatter={(label) => `${label} Treasury`}
              contentStyle={{ fontSize: 12, borderRadius: 8 }}
            />
            <Area
              type="monotone"
              dataKey="yield"
              fill="#4f46e5"
              fillOpacity={0.1}
              stroke="none"
            />
            <Line
              type="monotone"
              dataKey="yield"
              stroke="#4f46e5"
              strokeWidth={3}
              dot={{ r: 5, fill: '#4f46e5', strokeWidth: 2, stroke: '#fff' }}
              activeDot={{ r: 7, fill: '#3730a3' }}
            />
            <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Spreads Summary */}
      <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-gray-100">
        {Object.entries(data.spreads).map(([spread, value]) => {
          const isInverted = value < 0;
          return (
            <div
              key={spread}
              className={`px-4 py-2 rounded-lg border ${isInverted ? 'border-red-300 bg-red-50' : 'border-gray-200 bg-white'}`}
            >
              <div className="text-xs text-gray-500 uppercase">{spread} Spread</div>
              <div className={`text-xl font-bold font-mono ${isInverted ? 'text-red-600' : 'text-gray-900'}`}>
                {value > 0 ? '+' : ''}{value} <span className="text-sm font-normal">bps</span>
              </div>
              {isInverted && (
                <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                  <AlertTriangle className="w-3 h-3" />
                  Inverted
                </div>
              )}
            </div>
          );
        })}
      </div>
    </SectionCard>
  );
}

// ============================================================================
// YIELDS TABLE SECTION
// ============================================================================

interface YieldsTableSectionProps {
  data: YieldCurveData;
}

function YieldsTableSection({ data }: YieldsTableSectionProps) {
  const [changeView, setChangeView] = useState<ChangeView>('daily');

  return (
    <SectionCard
      title="Yields & Changes"
      description="Daily, weekly, and monthly yield changes"
      color="blue"
      icon={Table}
      rightContent={
        <div className="flex rounded-lg overflow-hidden border border-gray-300">
          {(['daily', 'weekly', 'monthly'] as ChangeView[]).map(view => (
            <button
              key={view}
              onClick={() => setChangeView(view)}
              className={`px-3 py-1.5 text-xs font-medium capitalize ${changeView === view ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              {view}
            </button>
          ))}
        </div>
      }
    >
      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-3 font-semibold">Tenor</th>
              <th className="text-right p-3 font-semibold">Yield</th>
              <th className="text-right p-3 font-semibold">
                {changeView.charAt(0).toUpperCase() + changeView.slice(1)} Change
              </th>
              <th className="text-left p-3 font-semibold">Series</th>
              <th className="text-left p-3 font-semibold">Source</th>
            </tr>
          </thead>
          <tbody>
            {data.curve.map((point, idx) => (
              <tr key={point.tenor} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="p-3 font-semibold">{point.tenor}</td>
                <td className="text-right p-3 font-mono">
                  {point.yield !== null ? `${point.yield.toFixed(3)}%` : '—'}
                </td>
                <td className="text-right p-3">
                  <ChangeDisplay
                    value={
                      changeView === 'daily' ? point.daily_change_bps :
                      changeView === 'weekly' ? point.weekly_change_bps :
                      point.monthly_change_bps
                    }
                  />
                </td>
                <td className="p-3 font-mono text-gray-500 text-xs">{point.series_id}</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    point.source === 'alfred' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {point.source || '—'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}

// ============================================================================
// SPREAD HISTORY SECTION
// ============================================================================

function SpreadHistorySection() {
  const [selectedSpread, setSelectedSpread] = useState('2s10s');
  const [days, setDays] = useState(365);

  const { data: spreadHistory, isLoading } = useQuery({
    queryKey: ['spread-history', selectedSpread, days],
    queryFn: async () => {
      const res = await fredResearchAPI.getSpreadHistory<SpreadHistoryData>(selectedSpread, days);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const chartData = useMemo(() => {
    if (!spreadHistory?.data) return [];
    return spreadHistory.data.map(d => ({
      date: formatShortDate(d.date),
      fullDate: d.date,
      value: d.value,
    }));
  }, [spreadHistory]);

  // Calculate stats
  const stats = useMemo(() => {
    if (!spreadHistory?.data || spreadHistory.data.length === 0) return null;
    const values = spreadHistory.data.map(d => d.value);
    const current = values[values.length - 1];
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const invertedDays = values.filter(v => v < 0).length;
    return { current, min, max, avg, invertedDays, total: values.length };
  }, [spreadHistory]);

  return (
    <SectionCard
      title="Spread History"
      description="Historical yield curve spreads"
      color="purple"
      icon={LineChart}
      rightContent={
        <div className="flex gap-2">
          <div className="flex rounded-lg overflow-hidden border border-gray-300">
            {SPREAD_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setSelectedSpread(opt.value)}
                className={`px-3 py-1.5 text-xs font-medium ${selectedSpread === opt.value ? 'bg-purple-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <div className="flex rounded-lg overflow-hidden border border-gray-300">
            {PERIOD_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setDays(opt.value)}
                className={`px-3 py-1.5 text-xs font-medium ${days === opt.value ? 'bg-purple-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      }
    >
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
        </div>
      ) : (
        <>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  tickFormatter={(v) => `${v} bps`}
                  domain={['auto', 'auto']}
                />
                <Tooltip
                  formatter={(value: number) => [`${value} bps`, selectedSpread.toUpperCase()]}
                  labelFormatter={(_, payload) => payload?.[0]?.payload?.fullDate ? formatDate(payload[0].payload.fullDate) : ''}
                  contentStyle={{ fontSize: 12, borderRadius: 8 }}
                />
                <ReferenceLine y={0} stroke="#ef4444" strokeWidth={2} label={{ value: 'Inversion', fontSize: 10, fill: '#ef4444' }} />
                <Area
                  type="monotone"
                  dataKey="value"
                  fill="#8b5cf6"
                  fillOpacity={0.1}
                  stroke="none"
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 2 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4 pt-4 border-t border-gray-100">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Current</p>
                <p className={`text-lg font-bold font-mono ${stats.current < 0 ? 'text-red-600' : 'text-gray-900'}`}>
                  {stats.current > 0 ? '+' : ''}{stats.current} bps
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Min</p>
                <p className={`text-lg font-bold font-mono ${stats.min < 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                  {stats.min} bps
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Max</p>
                <p className="text-lg font-bold font-mono text-emerald-600">
                  +{stats.max} bps
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Average</p>
                <p className="text-lg font-bold font-mono text-gray-900">
                  {stats.avg > 0 ? '+' : ''}{stats.avg.toFixed(0)} bps
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Days Inverted</p>
                <p className={`text-lg font-bold ${stats.invertedDays > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                  {stats.invertedDays} <span className="text-xs font-normal text-gray-500">/ {stats.total}</span>
                </p>
              </div>
            </div>
          )}
        </>
      )}
    </SectionCard>
  );
}

// ============================================================================
// TIPS & BREAKEVEN SECTION
// ============================================================================

interface TipsBreakevenSectionProps {
  data: YieldCurveData;
}

function TipsBreakevenSection({ data }: TipsBreakevenSectionProps) {
  return (
    <SectionCard
      title="Real Yields & Inflation Expectations"
      description="TIPS real yields and breakeven inflation rates"
      color="green"
      icon={Activity}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* TIPS Real Yields */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            TIPS Real Yields
          </h4>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left p-2 font-semibold">Tenor</th>
                  <th className="text-right p-2 font-semibold">Real Yield</th>
                  <th className="text-left p-2 font-semibold">Series</th>
                </tr>
              </thead>
              <tbody>
                {data.tips_real_yields.length > 0 ? (
                  data.tips_real_yields.map((point, idx) => (
                    <tr key={point.tenor} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="p-2 font-semibold">{point.tenor}</td>
                      <td className={`text-right p-2 font-mono ${point.real_yield < 0 ? 'text-red-600' : 'text-gray-900'}`}>
                        {point.real_yield.toFixed(3)}%
                      </td>
                      <td className="p-2 font-mono text-gray-500 text-xs">{point.series_id}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="p-4 text-center text-gray-500">No TIPS data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Breakeven Inflation */}
        <div>
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            Breakeven Inflation
          </h4>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left p-2 font-semibold">Tenor</th>
                  <th className="text-right p-2 font-semibold">Breakeven</th>
                  <th className="text-left p-2 font-semibold">Series</th>
                </tr>
              </thead>
              <tbody>
                {data.breakeven_inflation.length > 0 ? (
                  data.breakeven_inflation.map((point, idx) => (
                    <tr key={point.tenor} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="p-2 font-semibold">{point.tenor}</td>
                      <td className="text-right p-2 font-mono">{point.breakeven.toFixed(3)}%</td>
                      <td className="p-2 font-mono text-gray-500 text-xs">{point.series_id}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="p-4 text-center text-gray-500">No breakeven data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-600">
        <strong>TIPS Real Yields:</strong> The yield on Treasury Inflation-Protected Securities, representing the real (inflation-adjusted) return.
        <br />
        <strong>Breakeven Inflation:</strong> The difference between nominal Treasury yields and TIPS real yields, representing the market's inflation expectations.
      </div>
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
      description="Understanding Treasury yield curve data"
      color="gray"
      icon={Info}
      defaultExpanded={false}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">Treasury Constant Maturity Rates</h4>
          <p className="text-sm text-gray-600 mb-4">
            These rates are interpolated by the U.S. Treasury from the daily yield curve, which relates
            the yield on a security to its time to maturity. The curve is based on closing bid yields
            on actively traded Treasury securities.
          </p>

          <h4 className="font-semibold text-gray-900 mb-2">Yield Curve Inversions</h4>
          <p className="text-sm text-gray-600">
            When short-term yields exceed long-term yields (negative spread), the yield curve is said to be
            "inverted." Historically, sustained inversions of the 2s10s spread have preceded recessions.
          </p>
        </div>
        <div>
          <h4 className="font-semibold text-gray-900 mb-2">Key Spreads</h4>
          <ul className="text-sm text-gray-600 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-indigo-500 mt-0.5">•</span>
              <span><strong>2s10s:</strong> Most watched recession indicator</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-500 mt-0.5">•</span>
              <span><strong>3m10y:</strong> Fed's preferred spread for recession risk</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-500 mt-0.5">•</span>
              <span><strong>2s30s:</strong> Broader term structure indicator</span>
            </li>
          </ul>

          <div className="mt-4 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
            <p className="text-xs text-indigo-800">
              <strong>Data Source:</strong> Federal Reserve Economic Data (FRED/ALFRED).
              Updated daily, typically with a 1-day lag.
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

export default function YieldCurveExplorer() {
  const { data: curveData, isLoading, error } = useQuery({
    queryKey: ['fred-yield-curve'],
    queryFn: async () => {
      const res = await fredResearchAPI.getYieldCurve<YieldCurveData>();
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error || !curveData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Failed to load yield curve data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* FRED Explorer Navigation */}
      <FREDExplorerNav />

      {/* Main Content */}
      <div className="px-6 py-6 space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Treasury Yield Curve Explorer</h1>
          <p className="text-sm text-gray-600 mt-1">FRED/ALFRED Data • Nominal Yields, TIPS, Breakevens</p>
        </div>

        <YieldCurveSection data={curveData} />
        <YieldsTableSection data={curveData} />
        <SpreadHistorySection />
        <TipsBreakevenSection data={curveData} />
        <AboutSection />
      </div>
    </div>
  );
}
