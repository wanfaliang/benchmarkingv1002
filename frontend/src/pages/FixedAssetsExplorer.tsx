import React, { useState, useMemo, useEffect } from 'react';
import { useQuery, useQueries } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  LineChart,
  Table,
  Search,
  Building2,
  Landmark,
  Home,
  Loader2,
  Zap,
  BarChart3,
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
  Treemap,
  BarChart,
  Bar,
} from 'recharts';
import { beaResearchAPI } from '../services/api';

// ============================================================================
// CONSTANTS & TYPES
// ============================================================================

type ColorKey = 'blue' | 'green' | 'purple' | 'orange' | 'cyan' | 'red' | 'teal' | 'gray';

const SECTION_COLORS: Record<ColorKey, { main: string; light: string; border: string }> = {
  blue: { main: '#3b82f6', light: '#eff6ff', border: '#3b82f6' },
  green: { main: '#10b981', light: '#ecfdf5', border: '#10b981' },
  purple: { main: '#8b5cf6', light: '#f5f3ff', border: '#8b5cf6' },
  orange: { main: '#f59e0b', light: '#fffbeb', border: '#f59e0b' },
  cyan: { main: '#06b6d4', light: '#ecfeff', border: '#06b6d4' },
  red: { main: '#ef4444', light: '#fef2f2', border: '#ef4444' },
  teal: { main: '#14b8a6', light: '#f0fdfa', border: '#14b8a6' },
  gray: { main: '#6b7280', light: '#f9fafb', border: '#e5e7eb' },
};

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

const PERIOD_OPTIONS = [
  { label: '10Y', value: 10 },
  { label: '20Y', value: 20 },
  { label: '30Y', value: 30 },
  { label: '50Y', value: 50 },
  { label: 'All', value: 0 },
];

interface CategoryConfig {
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  color: ColorKey;
  tableName: string;
}

const ASSET_CATEGORIES: Record<string, CategoryConfig> = {
  private: {
    name: 'Private Fixed Assets',
    description: 'Equipment, Structures, and Intellectual Property',
    icon: Building2,
    color: 'green',
    tableName: 'FAAt201',
  },
  government: {
    name: 'Government Assets',
    description: 'Federal, State, and Local Government Fixed Assets',
    icon: Landmark,
    color: 'purple',
    tableName: 'FAAt701',
  },
  consumer: {
    name: 'Consumer Durables',
    description: 'Consumer Durable Goods',
    icon: Home,
    color: 'orange',
    tableName: 'FAAt801',
  },
};

// ============================================================================
// INTERFACES
// ============================================================================

interface FixedAssetsTable {
  table_name: string;
  table_description: string | null;
}

interface FixedAssetsSeries {
  series_code: string;
  table_name: string;
  line_number: number;
  line_description: string | null;
}

interface FixedAssetsTimeSeriesData {
  time_period: string;
  value: number;
}

interface FixedAssetsTimeSeries {
  series_code: string;
  line_description: string | null;
  unit: string | null;
  unit_mult: number | null;
  data: FixedAssetsTimeSeriesData[];
}

interface FixedAssetsHeadlineMetric {
  series_code: string;
  name: string;
  value: number | null;
  time_period: string;
  unit: string | null;
  unit_mult: number | null;
}

interface FixedAssetsHeadline {
  data: FixedAssetsHeadlineMetric[];
}

interface FixedAssetsSnapshotItem {
  line_number: number;
  line_description: string | null;
  value: number;
}

interface FixedAssetsSnapshot {
  table_name: string;
  period: string;
  unit: string | null;
  unit_mult: number | null;
  data: FixedAssetsSnapshotItem[];
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatValue = (value: number | null, unit?: string | null, unitMult?: number | null): string => {
  if (value === null || value === undefined) return 'N/A';

  if (unit?.toLowerCase().includes('percent')) {
    return `${value.toFixed(1)}%`;
  }
  if (unit?.toLowerCase().includes('index')) {
    return value.toFixed(1);
  }

  const multiplier = unitMult ? Math.pow(10, unitMult) : 1;
  const actualValue = value * multiplier;

  if (Math.abs(actualValue) >= 1e12) return `$${(actualValue / 1e12).toFixed(2)}T`;
  if (Math.abs(actualValue) >= 1e9) return `$${(actualValue / 1e9).toFixed(2)}B`;
  if (Math.abs(actualValue) >= 1e6) return `$${(actualValue / 1e6).toFixed(1)}M`;
  if (Math.abs(actualValue) >= 1e3) return `$${(actualValue / 1e3).toFixed(1)}K`;

  return `$${actualValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
};

const calcPctChange = (current: number | null, previous: number | null): number | null => {
  if (current === null || previous === null || previous === 0) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
};

// Blue gradient for treemap
const getTreemapColor = (value: number, maxValue: number, minValue: number) => {
  const colors = [
    { r: 191, g: 219, b: 254 },
    { r: 147, g: 197, b: 253 },
    { r: 96, g: 165, b: 250 },
    { r: 59, g: 130, b: 246 },
    { r: 37, g: 99, b: 235 },
    { r: 29, g: 78, b: 216 },
  ];

  if (maxValue === minValue) return `rgb(${colors[3].r}, ${colors[3].g}, ${colors[3].b})`;

  const ratio = (value - minValue) / (maxValue - minValue);
  const colorIndex = Math.min(Math.floor(ratio * (colors.length - 1)), colors.length - 2);
  const localRatio = (ratio * (colors.length - 1)) - colorIndex;

  const c1 = colors[colorIndex];
  const c2 = colors[colorIndex + 1];

  const r = Math.round(c1.r + (c2.r - c1.r) * localRatio);
  const g = Math.round(c1.g + (c2.g - c1.g) * localRatio);
  const b = Math.round(c1.b + (c2.b - c1.b) * localRatio);

  return `rgb(${r}, ${g}, ${b})`;
};

// ============================================================================
// REUSABLE COMPONENTS
// ============================================================================

interface SectionCardProps {
  title: string;
  description?: string;
  color: ColorKey;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  collapsible?: boolean;
  rightContent?: React.ReactNode;
}

function SectionCard({ title, description, color, icon: Icon, children, defaultExpanded = true, collapsible = true, rightContent }: SectionCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const colorSet = SECTION_COLORS[color];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4 overflow-hidden">
      <div
        className={`flex items-center justify-between px-5 py-3 ${collapsible ? 'cursor-pointer' : ''}`}
        style={{
          backgroundColor: colorSet.light,
          borderBottom: `4px solid ${colorSet.border}`,
        }}
        onClick={() => collapsible && setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <Icon className="w-6 h-6" style={{ color: colorSet.main }} />
          <div>
            <h3 className="text-lg font-bold leading-tight" style={{ color: colorSet.main }}>{title}</h3>
            {description && <p className="text-xs text-gray-500">{description}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {rightContent && <div onClick={e => e.stopPropagation()}>{rightContent}</div>}
          {collapsible && (
            <button className="p-1 rounded-full hover:bg-white/50 transition-colors" style={{ color: colorSet.main }}>
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
  period?: string;
  color?: string;
  isLoading?: boolean;
}

function MetricCard({ title, value, change, period, color = '#3b82f6', isLoading }: MetricCardProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
      <div className="flex items-start justify-between mb-1">
        <span className="text-xs text-gray-500 font-medium truncate" title={title}>{title}</span>
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
      </div>
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
      ) : (
        <>
          <div className="text-lg font-bold text-gray-900">{value}</div>
          <div className="flex items-center justify-between mt-1">
            {change !== null && change !== undefined && (
              <span className={`text-xs font-medium ${change > 0 ? 'text-emerald-600' : change < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                {change > 0 ? '+' : ''}{change.toFixed(1)}%
              </span>
            )}
            {period && <span className="text-[10px] text-gray-400">{period}</span>}
          </div>
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

interface ChartMetricToggleProps {
  value: 'pct' | 'value';
  onChange: (v: 'pct' | 'value') => void;
  color?: string;
}

function ChartMetricToggle({ value, onChange, color = '#3b82f6' }: ChartMetricToggleProps) {
  return (
    <div className="flex rounded-lg overflow-hidden border border-gray-300">
      <button
        onClick={() => onChange('pct')}
        className={`px-3 py-1.5 text-xs font-medium transition-colors ${value === 'pct' ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
        style={value === 'pct' ? { backgroundColor: color } : {}}
      >
        % Change
      </button>
      <button
        onClick={() => onChange('value')}
        className={`px-3 py-1.5 text-xs font-medium transition-colors ${value === 'value' ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
        style={value === 'value' ? { backgroundColor: color } : {}}
      >
        Value
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
          className={`px-2 py-1 text-xs font-medium transition-colors ${value === opt.value ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
          style={value === opt.value ? { backgroundColor: color } : {}}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

function ChangeIndicator({ value }: { value: number | null }) {
  if (value === null || value === undefined) return <span className="text-gray-400 text-xs">-</span>;
  const isPositive = value > 0.1;
  const isNegative = value < -0.1;
  return (
    <span className={`text-xs font-medium ${isPositive ? 'text-emerald-600' : isNegative ? 'text-red-600' : 'text-gray-500'}`}>
      {value > 0 ? '+' : ''}{value.toFixed(1)}%
    </span>
  );
}

// ============================================================================
// ASSET OVERVIEW HISTORY SECTION
// ============================================================================

interface AssetOverviewHistorySectionProps {
  headlineData: FixedAssetsHeadlineMetric[] | undefined;
}

function AssetOverviewHistorySection({ headlineData }: AssetOverviewHistorySectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('table');
  const [periodYears, setPeriodYears] = useState(20);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('value');

  const colorSet = SECTION_COLORS.blue;

  const seriesCodes = useMemo(() => {
    return headlineData?.map(h => h.series_code) || [];
  }, [headlineData]);

  const seriesQueries = useQueries({
    queries: seriesCodes.map(code => ({
      queryKey: ['fixedassets-overview-history', code],
      queryFn: async () => {
        const response = await beaResearchAPI.getFixedAssetsSeriesData<FixedAssetsTimeSeries>(code);
        return response.data;
      },
      enabled: !!code,
      staleTime: 5 * 60 * 1000,
    })),
  });

  const historicalData = useMemo(() => {
    if (seriesCodes.length === 0) return [];

    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    seriesQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: FixedAssetsTimeSeriesData) => {
          const year = parseInt(d.time_period);
          if (year >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      }
    });

    const sortedPeriods = Array.from(allPeriods).sort();

    return sortedPeriods.map((period) => {
      const point: Record<string, unknown> = { period };

      seriesCodes.forEach((code, idx) => {
        const queryData = seriesQueries[idx]?.data;
        const seriesData = queryData?.data || [];

        const currentIdx = seriesData.findIndex((d: FixedAssetsTimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        point[`${code}_value`] = current?.value ?? null;
        point[`${code}_yoy`] = calcPctChange(current?.value ?? null, prev?.value ?? null);
      });

      return point;
    });
  }, [seriesCodes, seriesQueries, periodYears]);

  const isLoading = seriesQueries.some(q => q.isLoading);
  const loadedCount = seriesQueries.filter(q => !q.isLoading).length;

  if (!headlineData || headlineData.length === 0) return null;

  return (
    <SectionCard
      title="Asset Overview History"
      description={`Time series for ${headlineData.length} key metrics`}
      color="blue"
      icon={LineChart}
      rightContent={
        <div className="flex gap-2 items-center">
          <ChartMetricToggle value={chartMetric} onChange={setChartMetric} color={colorSet.main} />
          <PeriodSelector value={periodYears} onChange={setPeriodYears} color={colorSet.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {isLoading && (
        <div className="flex items-center gap-2 mb-3">
          <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
          <span className="text-xs text-gray-500">Loading {loadedCount}/{seriesCodes.length} series...</span>
        </div>
      )}

      {historicalData.length === 0 && !isLoading ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available</div>
      ) : viewMode === 'chart' ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={historicalData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
              <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis
                tick={{ fontSize: 10 }}
                width={80}
                tickFormatter={(v) => chartMetric === 'pct' ? `${v?.toFixed(1)}%` : formatValue(v, null, null)}
              />
              {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />}
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  const code = name.split('_')[0];
                  const metric = headlineData.find(h => h.series_code === code);
                  if (chartMetric === 'pct') {
                    return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}%`, `${metric?.name || code} (YoY)`];
                  }
                  return [formatValue(value, metric?.unit, metric?.unit_mult), metric?.name || code];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => {
                const code = v.split('_')[0];
                return headlineData.find(h => h.series_code === code)?.name || code;
              }} />
              {headlineData.map((metric, idx) => (
                <Line
                  key={metric.series_code}
                  type="monotone"
                  dataKey={chartMetric === 'pct' ? `${metric.series_code}_yoy` : `${metric.series_code}_value`}
                  name={chartMetric === 'pct' ? `${metric.series_code}_yoy` : metric.series_code}
                  stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-20">Year</th>
                {headlineData.map((metric, idx) => (
                  <React.Fragment key={metric.series_code}>
                    <th className="text-right p-2 font-semibold whitespace-nowrap text-xs">
                      <div className="flex items-center justify-end gap-1">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                        {metric.name?.substring(0, 12)}
                      </div>
                    </th>
                    <th className="text-right p-2 font-semibold text-[10px] text-gray-500">YoY%</th>
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {historicalData.slice().reverse().map((row, rowIdx) => {
                const typedRow = row as Record<string, unknown>;
                return (
                  <tr key={typedRow.period as string} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className={`p-2 font-medium sticky left-0 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} z-10`}>
                      {typedRow.period as string}
                    </td>
                    {headlineData.map((metric) => (
                      <React.Fragment key={metric.series_code}>
                        <td className="text-right p-2 font-mono text-xs">
                          {formatValue(typedRow[`${metric.series_code}_value`] as number | null, metric.unit, metric.unit_mult)}
                        </td>
                        <td className="text-right p-2">
                          <ChangeIndicator value={typedRow[`${metric.series_code}_yoy`] as number | null} />
                        </td>
                      </React.Fragment>
                    ))}
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
// CATEGORY SECTION COMPONENT
// ============================================================================

interface CategorySectionProps {
  categoryKey: string;
  category: CategoryConfig;
}

function CategorySection({ category }: CategorySectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('table');
  const [periodYears, setPeriodYears] = useState(20);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('value');

  const colorSet = SECTION_COLORS[category.color];

  // Fetch ALL series for this table
  const { data: seriesList, isLoading: seriesLoading } = useQuery({
    queryKey: ['fixedassets-category-series', category.tableName],
    queryFn: async () => {
      const response = await beaResearchAPI.getFixedAssetsSeries<FixedAssetsSeries[]>(category.tableName);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Fetch data for ALL series
  const seriesQueries = useQueries({
    queries: (seriesList || []).map(s => ({
      queryKey: ['fixedassets-series-data', s.series_code],
      queryFn: async () => {
        const response = await beaResearchAPI.getFixedAssetsSeriesData<FixedAssetsTimeSeries>(s.series_code);
        return response.data;
      },
      enabled: !!seriesList,
      staleTime: 5 * 60 * 1000,
    })),
  });

  // Prepare historical data from ALL series
  const historicalData = useMemo(() => {
    if (!seriesList || seriesList.length === 0) return [];

    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    seriesQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: FixedAssetsTimeSeriesData) => {
          const year = parseInt(d.time_period);
          if (year >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      }
    });

    const sortedPeriods = Array.from(allPeriods).sort();

    return sortedPeriods.map((period) => {
      const point: Record<string, unknown> = { period };

      seriesList.forEach((s, idx) => {
        const queryData = seriesQueries[idx]?.data;
        const seriesData = queryData?.data || [];

        const currentIdx = seriesData.findIndex((d: FixedAssetsTimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        point[`${s.series_code}_value`] = current?.value ?? null;
        point[`${s.series_code}_unit`] = queryData?.unit;
        point[`${s.series_code}_unitMult`] = queryData?.unit_mult;
        point[`${s.series_code}_yoy`] = calcPctChange(current?.value ?? null, prev?.value ?? null);
        point[`${s.series_code}_name`] = s.line_description;
        point[`${s.series_code}_lineNum`] = s.line_number;
      });

      return point;
    });
  }, [seriesList, seriesQueries, periodYears]);

  const isLoading = seriesLoading || seriesQueries.some(q => q.isLoading);
  const loadedCount = seriesQueries.filter(q => !q.isLoading).length;

  // Get latest with YoY change for a series
  const getLatestWithChange = (seriesCode: string) => {
    const idx = seriesList?.findIndex(s => s.series_code === seriesCode) ?? -1;
    if (idx < 0) return { latest: null, yoy: null, unit: null, unitMult: null };
    const data = seriesQueries[idx]?.data?.data;
    if (!data || data.length === 0) return { latest: null, yoy: null, unit: null, unitMult: null };
    const validData = data.filter((d: FixedAssetsTimeSeriesData) => d.value !== null);
    if (validData.length === 0) return { latest: null, yoy: null, unit: null, unitMult: null };
    const latest = validData[validData.length - 1];
    const prev = validData.length > 1 ? validData[validData.length - 2] : null;
    const yoy = calcPctChange(latest.value, prev?.value ?? null);
    return { latest, yoy, unit: seriesQueries[idx]?.data?.unit, unitMult: seriesQueries[idx]?.data?.unit_mult };
  };

  // Get first 6 series for headline cards
  const headlineSeries = seriesList?.slice(0, 6) || [];

  return (
    <SectionCard
      title={category.name}
      description={`${category.description} - ${seriesList?.length || 0} series`}
      color={category.color}
      icon={category.icon}
      rightContent={
        <div className="flex gap-2 items-center">
          <ChartMetricToggle value={chartMetric} onChange={setChartMetric} color={colorSet.main} />
          <PeriodSelector value={periodYears} onChange={setPeriodYears} color={colorSet.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Loading indicator */}
      {isLoading && (
        <div className="flex items-center gap-2 mb-3">
          <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
          <span className="text-xs text-gray-500">Loading {loadedCount}/{seriesList?.length || 0} series...</span>
        </div>
      )}

      {/* Headline Metrics - first 6 series */}
      {headlineSeries.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 mb-4">
          {headlineSeries.map((s, idx) => {
            const { latest, yoy, unit, unitMult } = getLatestWithChange(s.series_code);
            return (
              <MetricCard
                key={s.series_code}
                title={s.line_description?.substring(0, 25) || `Line ${s.line_number}`}
                value={formatValue(latest?.value ?? null, unit, unitMult)}
                change={yoy}
                period={latest?.time_period}
                color={CHART_COLORS[idx % CHART_COLORS.length]}
                isLoading={seriesQueries[idx]?.isLoading}
              />
            );
          })}
        </div>
      )}

      {/* Chart or Table */}
      {historicalData.length === 0 && !isLoading ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available</div>
      ) : viewMode === 'chart' ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={historicalData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
              <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis
                tick={{ fontSize: 10 }}
                width={80}
                tickFormatter={(v) => chartMetric === 'pct' ? `${v?.toFixed(1)}%` : formatValue(v, null, null)}
              />
              {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />}
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  const code = name.split('_')[0];
                  const series = seriesList?.find(s => s.series_code === code);
                  if (chartMetric === 'pct') {
                    return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}%`, `${series?.line_description?.substring(0, 20) || code} (YoY)`];
                  }
                  const queryIdx = seriesList?.findIndex(s => s.series_code === code) ?? -1;
                  const unit = queryIdx >= 0 ? seriesQueries[queryIdx]?.data?.unit : null;
                  const unitMult = queryIdx >= 0 ? seriesQueries[queryIdx]?.data?.unit_mult : null;
                  return [formatValue(value, unit, unitMult), series?.line_description?.substring(0, 20) || code];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => {
                const code = v.split('_')[0];
                return seriesList?.find(s => s.series_code === code)?.line_description?.substring(0, 15) || code;
              }} />
              {headlineSeries.slice(0, 6).map((s, idx) => (
                <Line
                  key={s.series_code}
                  type="monotone"
                  dataKey={chartMetric === 'pct' ? `${s.series_code}_yoy` : `${s.series_code}_value`}
                  name={chartMetric === 'pct' ? `${s.series_code}_yoy` : s.series_code}
                  stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="overflow-auto max-h-[500px]">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-20 min-w-[60px]">Year</th>
                {seriesList?.map((s, idx) => (
                  <React.Fragment key={s.series_code}>
                    <th className="text-right p-2 font-semibold whitespace-nowrap text-[11px]" style={{ borderLeft: idx === 0 ? 'none' : '1px solid #e5e7eb' }}>
                      <div className="flex items-center justify-end gap-1">
                        <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                        {s.line_description?.substring(0, 20) || `Line ${s.line_number}`}
                      </div>
                    </th>
                    <th className="text-right p-2 font-semibold text-[10px] text-gray-500">YoY%</th>
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {historicalData.slice().reverse().map((row, rowIdx) => {
                const typedRow = row as Record<string, unknown>;
                return (
                  <tr key={typedRow.period as string} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className={`p-2 font-medium sticky left-0 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} z-[1]`}>
                      {typedRow.period as string}
                    </td>
                    {seriesList?.map((s, sIdx) => (
                      <React.Fragment key={s.series_code}>
                        <td className="text-right p-2 font-mono text-xs" style={{ borderLeft: sIdx === 0 ? 'none' : '1px solid #e5e7eb' }}>
                          {formatValue(
                            typedRow[`${s.series_code}_value`] as number | null,
                            typedRow[`${s.series_code}_unit`] as string | null,
                            typedRow[`${s.series_code}_unitMult`] as number | null
                          )}
                        </td>
                        <td className="text-right p-2">
                          <ChangeIndicator value={typedRow[`${s.series_code}_yoy`] as number | null} />
                        </td>
                      </React.Fragment>
                    ))}
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
// TOP CATEGORIES SECTION (with Timeline)
// ============================================================================

interface TopCategoriesSectionProps {
  tables: FixedAssetsTable[];
}

function TopCategoriesSection({ tables }: TopCategoriesSectionProps) {
  const [periodYears, setPeriodYears] = useState(20);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState('FAAt101');

  const colorSet = SECTION_COLORS.red;

  // Calculate year range
  const currentYear = new Date().getFullYear();
  const years = useMemo(() => {
    const count = periodYears === 0 ? 50 : periodYears;
    const result: string[] = [];
    for (let i = count - 1; i >= 0; i--) {
      result.push(String(currentYear - i));
    }
    return result;
  }, [currentYear, periodYears]);

  // Fetch snapshot data for selected table and year
  const { data: snapshotData, isLoading } = useQuery({
    queryKey: ['fixedassets-top-categories', selectedTable, selectedYear],
    queryFn: async () => {
      const response = await beaResearchAPI.getFixedAssetsSnapshot<FixedAssetsSnapshot>(
        selectedTable,
        selectedYear ? parseInt(selectedYear) : undefined
      );
      return response.data;
    },
    enabled: !!selectedTable,
    staleTime: 5 * 60 * 1000,
  });

  // Set default selected year to latest when data loads
  useEffect(() => {
    if (!selectedYear && snapshotData?.period) {
      setSelectedYear(snapshotData.period);
    }
  }, [snapshotData, selectedYear]);

  // Reset year when table changes
  useEffect(() => {
    setSelectedYear(null);
  }, [selectedTable]);

  // Calculate top categories for selected year
  const topCategories = useMemo(() => {
    if (!snapshotData?.data) return [];
    return [...snapshotData.data]
      .filter(d => d.value > 0)
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);
  }, [snapshotData]);

  // Get available years
  const availableYears = years.filter(y => parseInt(y) <= currentYear);

  return (
    <SectionCard
      title="Top Categories"
      description="Largest Asset Categories by Value"
      color="red"
      icon={Zap}
      rightContent={
        <div className="flex gap-2 items-center">
          <select
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            className="px-2 py-1 text-xs border border-gray-300 rounded-lg"
          >
            {tables.slice(0, 10).map(t => (
              <option key={t.table_name} value={t.table_name}>{t.table_name}</option>
            ))}
          </select>
          <PeriodSelector value={periodYears} onChange={(v) => {
            setPeriodYears(v);
            setSelectedYear(null);
          }} color={colorSet.main} />
        </div>
      }
    >
      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center gap-2 mb-3">
          <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
          <span className="text-xs text-gray-500">Loading data...</span>
        </div>
      )}

      {/* Table */}
      {snapshotData?.data ? (
        <>
          <div className="mb-4">
            <h4 className="text-sm font-bold mb-2 flex items-center gap-1" style={{ color: colorSet.main }}>
              <TrendingUp className="w-4 h-4" />
              Top 10 Categories ({selectedYear || snapshotData.period})
            </h4>
            <table className="w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left p-2 font-semibold w-10">#</th>
                  <th className="text-left p-2 font-semibold">Category</th>
                  <th className="text-right p-2 font-semibold">Value</th>
                </tr>
              </thead>
              <tbody>
                {topCategories.length > 0 ? topCategories.map((cat, idx) => (
                  <tr key={cat.line_number} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="p-2">{idx + 1}</td>
                    <td className="p-2">{cat.line_description?.substring(0, 50)}</td>
                    <td className="p-2 text-right font-mono" style={{ color: colorSet.main }}>
                      {formatValue(cat.value, snapshotData.unit, snapshotData.unit_mult)}
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={3} className="p-4 text-center text-gray-500">No data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Timeline */}
          <div className="mt-6 px-4">
            <p className="text-xs text-gray-500 mb-2 text-center">
              Click a year to view historical rankings
            </p>
            <div className="relative py-4">
              {/* Timeline Line */}
              <div className="absolute top-1/2 left-5 right-5 h-1 bg-gray-300 -translate-y-1/2 rounded" />

              {/* Year Points */}
              <div className="flex justify-between relative px-2 overflow-x-auto">
                {availableYears.slice(-20).map((year, idx, arr) => {
                  const isSelected = year === (selectedYear || snapshotData.period);
                  const labelInterval = arr.length <= 10 ? 1 : arr.length <= 20 ? 2 : 5;
                  const showLabel = idx === 0 || idx === arr.length - 1 || idx % labelInterval === 0;

                  return (
                    <div
                      key={year}
                      className="flex flex-col items-center cursor-pointer transition-transform hover:scale-110"
                      onClick={() => setSelectedYear(year)}
                    >
                      {/* Year Point */}
                      <div
                        className={`rounded-full transition-all z-10 ${
                          isSelected
                            ? 'w-5 h-5 border-[3px] border-white shadow-lg'
                            : 'w-3 h-3 border-2 border-gray-300 hover:bg-gray-500'
                        }`}
                        style={{
                          backgroundColor: isSelected ? colorSet.main : '#9ca3af',
                          boxShadow: isSelected ? `0 0 0 3px ${colorSet.main}40, 0 2px 8px rgba(0,0,0,0.2)` : '0 1px 3px rgba(0,0,0,0.1)',
                        }}
                      />

                      {/* Year Label */}
                      <span
                        className={`mt-1 transition-all ${
                          isSelected
                            ? 'text-xs font-bold'
                            : 'text-[10px] font-normal text-gray-500'
                        } ${showLabel || isSelected ? 'opacity-100' : 'opacity-0 hover:opacity-100'}`}
                        style={{ color: isSelected ? colorSet.main : undefined }}
                      >
                        {year}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </>
      ) : !isLoading ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available for the selected period</div>
      ) : null}
    </SectionCard>
  );
}

// ============================================================================
// DATA EXPLORER
// ============================================================================

interface DataExplorerProps {
  tables: FixedAssetsTable[];
}

function DataExplorer({ tables }: DataExplorerProps) {
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [selectedSeries, setSelectedSeries] = useState<FixedAssetsSeries | null>(null);

  const { data: seriesList, isLoading: seriesLoading } = useQuery({
    queryKey: ['fixedassets-explorer-series', selectedTable],
    queryFn: async () => {
      const response = await beaResearchAPI.getFixedAssetsSeries<FixedAssetsSeries[]>(selectedTable);
      return response.data;
    },
    enabled: !!selectedTable,
  });

  const { data: seriesData, isLoading: dataLoading } = useQuery({
    queryKey: ['fixedassets-explorer-data', selectedSeries?.series_code],
    queryFn: async () => {
      const response = await beaResearchAPI.getFixedAssetsSeriesData<FixedAssetsTimeSeries>(selectedSeries!.series_code);
      return response.data;
    },
    enabled: !!selectedSeries,
  });

  return (
    <SectionCard
      title="Data Explorer"
      description="Browse all Fixed Assets tables and series"
      color="gray"
      icon={Search}
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Table Selector */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Select Table</label>
          <select
            value={selectedTable}
            onChange={(e) => {
              setSelectedTable(e.target.value);
              setSelectedSeries(null);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">Choose a table...</option>
            {tables.map(t => (
              <option key={t.table_name} value={t.table_name}>
                {t.table_name} - {t.table_description?.substring(0, 40)}
              </option>
            ))}
          </select>
        </div>

        {/* Series Selector */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Select Series</label>
          <select
            value={selectedSeries?.series_code || ''}
            onChange={(e) => {
              const series = seriesList?.find(s => s.series_code === e.target.value);
              setSelectedSeries(series || null);
            }}
            disabled={!selectedTable || seriesLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm disabled:bg-gray-100"
          >
            <option value="">Choose a series...</option>
            {seriesList?.map(s => (
              <option key={s.series_code} value={s.series_code}>
                {s.line_number}. {s.line_description?.substring(0, 40)}
              </option>
            ))}
          </select>
        </div>

        {/* Info */}
        <div className="flex items-end">
          {seriesLoading && <Loader2 className="w-5 h-5 animate-spin text-gray-400" />}
          {selectedSeries && (
            <div className="text-xs text-gray-500">
              <strong>Code:</strong> {selectedSeries.series_code}
            </div>
          )}
        </div>
      </div>

      {/* Data Display */}
      {selectedSeries && (
        <div className="mt-4">
          {dataLoading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
          ) : seriesData?.data ? (
            <div className="overflow-auto max-h-80">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-100">
                  <tr>
                    <th className="text-left p-2 font-semibold">Year</th>
                    <th className="text-right p-2 font-semibold">Value</th>
                  </tr>
                </thead>
                <tbody>
                  {seriesData.data.slice().reverse().map((d: FixedAssetsTimeSeriesData, idx: number) => (
                    <tr key={d.time_period} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="p-2 font-medium">{d.time_period}</td>
                      <td className="p-2 text-right font-mono">
                        {formatValue(d.value, seriesData.unit, seriesData.unit_mult)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available</div>
          )}
        </div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function FixedAssetsExplorer() {
  const [snapshotTable, setSnapshotTable] = useState('FAAt101');
  const [snapshotViewMode, setSnapshotViewMode] = useState<'treemap' | 'bar'>('treemap');

  const { data: tables, isLoading: tablesLoading } = useQuery({
    queryKey: ['fixedassets-tables'],
    queryFn: async () => {
      const response = await beaResearchAPI.getFixedAssetsTables<FixedAssetsTable[]>();
      return response.data;
    },
  });

  const { data: headlineData, isLoading: headlineLoading } = useQuery({
    queryKey: ['fixedassets-headline'],
    queryFn: async () => {
      const response = await beaResearchAPI.getFixedAssetsHeadline<FixedAssetsHeadline>();
      return response.data;
    },
  });

  const { data: snapshotData, isLoading: snapshotLoading } = useQuery({
    queryKey: ['fixedassets-snapshot', snapshotTable],
    queryFn: async () => {
      const response = await beaResearchAPI.getFixedAssetsSnapshot<FixedAssetsSnapshot>(snapshotTable);
      return response.data;
    },
    enabled: !!snapshotTable,
  });

  // Prepare treemap data
  const treemapData = useMemo(() => {
    if (!snapshotData?.data) return [];
    return snapshotData.data
      .filter(d => d.value > 0)
      .sort((a, b) => b.value - a.value)
      .slice(0, 20)
      .map(d => ({
        name: d.line_description?.substring(0, 25) || `Line ${d.line_number}`,
        fullName: d.line_description || `Line ${d.line_number}`,
        value: d.value,
        lineNumber: d.line_number,
      }));
  }, [snapshotData]);

  const treemapMaxValue = Math.max(...treemapData.map(d => d.value), 0);
  const treemapMinValue = Math.min(...treemapData.map(d => d.value), 0);

  // Custom treemap content renderer
  const TreemapContent = (props: { x: number; y: number; width: number; height: number; name: string; value: number }) => {
    const { x, y, width, height, name, value } = props;
    if (width < 40 || height < 30) return null;

    const bgColor = getTreemapColor(value, treemapMaxValue, treemapMinValue);

    return (
      <g>
        <rect x={x} y={y} width={width} height={height} style={{ fill: bgColor, stroke: '#fff', strokeWidth: 2 }} />
        <text x={x + width / 2} y={y + height / 2 - 6} textAnchor="middle" fill="#1e3a5f" fontSize={10} fontWeight="bold">
          {name.substring(0, Math.floor(width / 7))}
        </text>
        <text x={x + width / 2} y={y + height / 2 + 8} textAnchor="middle" fill="#1e3a5f" fontSize={9}>
          {formatValue(value, snapshotData?.unit, snapshotData?.unit_mult)}
        </text>
      </g>
    );
  };

  if (tablesLoading) {
    return (
      <div className="flex justify-center items-center h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-2">
        <Link to="/research" className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Fixed Assets Explorer</h1>
          <p className="text-sm text-gray-500">Current-Cost Net Stock of Fixed Assets and Consumer Durable Goods</p>
        </div>
      </div>

      <hr className="my-6 border-gray-200" />

      {/* Section 1: Asset Overview */}
      <SectionCard title="Asset Overview" description="Key Fixed Asset Metrics" color="blue" icon={Building2} collapsible={false}>
        {headlineLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
            {Array.from({ length: 6 }).map((_, idx) => (
              <MetricCard key={idx} title="Loading..." value="-" isLoading={true} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
            {headlineData?.data?.slice(0, 6).map((metric, idx) => (
              <MetricCard
                key={metric.series_code}
                title={metric.name || 'Metric'}
                value={formatValue(metric.value, metric.unit, metric.unit_mult)}
                period={metric.time_period}
                color={CHART_COLORS[idx % CHART_COLORS.length]}
              />
            ))}
          </div>
        )}
      </SectionCard>

      {/* Section 2: Asset Overview History */}
      <AssetOverviewHistorySection headlineData={headlineData?.data} />

      {/* Section 3: Asset Composition */}
      <SectionCard
        title="Asset Composition"
        description={`Breakdown by Category - ${snapshotData?.period || 'Latest'}`}
        color="cyan"
        icon={BarChart3}
        rightContent={
          <div className="flex gap-2 items-center">
            <select
              value={snapshotTable}
              onChange={(e) => setSnapshotTable(e.target.value)}
              className="min-w-[200px] px-2 py-1 text-xs border border-gray-300 rounded-lg"
            >
              {tables?.map(t => (
                <option key={t.table_name} value={t.table_name}>
                  {t.table_name} - {t.table_description?.substring(0, 30)}
                </option>
              ))}
            </select>
            <div className="flex rounded-lg overflow-hidden border border-gray-300">
              <button
                onClick={() => setSnapshotViewMode('treemap')}
                className={`px-3 py-1.5 text-xs font-medium ${snapshotViewMode === 'treemap' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                Treemap
              </button>
              <button
                onClick={() => setSnapshotViewMode('bar')}
                className={`px-3 py-1.5 text-xs font-medium ${snapshotViewMode === 'bar' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                Bar
              </button>
            </div>
          </div>
        }
      >
        {snapshotLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : treemapData.length === 0 ? (
          <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No snapshot data available for this table</div>
        ) : snapshotViewMode === 'treemap' ? (
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={treemapData}
                dataKey="value"
                aspectRatio={4 / 3}
                stroke="#fff"
                content={<TreemapContent x={0} y={0} width={0} height={0} name="" value={0} />}
              />
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={treemapData.slice(0, 12)} layout="vertical" margin={{ top: 10, right: 30, left: 150, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => formatValue(v, snapshotData?.unit, snapshotData?.unit_mult)} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={140} />
                <Tooltip formatter={(value: number) => [formatValue(value, snapshotData?.unit, snapshotData?.unit_mult), 'Value']} />
                <Bar dataKey="value" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </SectionCard>

      {/* Section 4: Private Fixed Assets */}
      <CategorySection categoryKey="private" category={ASSET_CATEGORIES.private} />

      {/* Section 5: Government Assets */}
      <CategorySection categoryKey="government" category={ASSET_CATEGORIES.government} />

      {/* Section 6: Consumer Durables */}
      <CategorySection categoryKey="consumer" category={ASSET_CATEGORIES.consumer} />

      {/* Section 7: Top Categories with Timeline */}
      <TopCategoriesSection tables={tables || []} />

      {/* Section 8: Data Explorer */}
      <DataExplorer tables={tables || []} />
    </div>
  );
}
