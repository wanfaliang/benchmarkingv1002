import React, { useState, useMemo } from 'react';
import { useQuery, useQueries } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  LineChart,
  Table,
  Search,
  BarChart3,
  Building2,
  ShoppingCart,
  Landmark,
  Globe,
  PiggyBank,
  Loader2,
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
} from 'recharts';
import { beaResearchAPI } from '../services/api';

// ============================================================================
// CONSTANTS & TYPES
// ============================================================================

interface NIPASeries {
  series_code: string;
  table_name: string;
  line_number: number;
  line_description: string;
  metric_name?: string | null;
  cl_unit?: string | null;
  unit_mult?: number | null;
  data_points_count: number;
}

interface NIPATimeSeriesData {
  time_period: string;
  value: number | null;
}

interface NIPATimeSeries {
  series_code: string;
  line_description: string;
  metric_name?: string | null;
  unit?: string | null;
  unit_mult?: number | null;
  data: NIPATimeSeriesData[];
}

interface NIPATable {
  table_name: string;
  table_description: string;
  has_annual: boolean;
  has_quarterly: boolean;
  has_monthly: boolean;
  first_year?: number | null;
  last_year?: number | null;
  series_count: number;
  is_active: boolean;
}

type ColorKey = 'blue' | 'green' | 'purple' | 'orange' | 'cyan' | 'red' | 'teal' | 'gray';

const SECTION_COLORS: Record<ColorKey, { main: string; light: string; border: string }> = {
  blue: { main: '#3b82f6', light: 'bg-blue-50', border: 'border-blue-500' },
  green: { main: '#10b981', light: 'bg-emerald-50', border: 'border-emerald-500' },
  purple: { main: '#8b5cf6', light: 'bg-violet-50', border: 'border-violet-500' },
  orange: { main: '#f59e0b', light: 'bg-amber-50', border: 'border-amber-500' },
  cyan: { main: '#06b6d4', light: 'bg-cyan-50', border: 'border-cyan-500' },
  red: { main: '#ef4444', light: 'bg-red-50', border: 'border-red-500' },
  teal: { main: '#14b8a6', light: 'bg-teal-50', border: 'border-teal-500' },
  gray: { main: '#6b7280', light: 'bg-gray-50', border: 'border-gray-300' },
};

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

const TIME_RANGE_OPTIONS = [
  { label: '2Y', value: 2 },
  { label: '5Y', value: 5 },
  { label: '10Y', value: 10 },
  { label: '20Y', value: 20 },
  { label: 'All', value: 0 },
];

interface CategoryConfig {
  name: string;
  description: string;
  icon: React.ElementType;
  color: ColorKey;
  headlines: { tableCode: string; lineNumber: number; name: string; freq: string }[];
}

const NIPA_CATEGORIES: Record<string, CategoryConfig> = {
  gdp: {
    name: 'GDP & Output',
    description: 'Real and Nominal GDP Growth',
    icon: BarChart3,
    color: 'green',
    headlines: [
      { tableCode: 'T10101', lineNumber: 1, name: 'Real GDP', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 2, name: 'PCE', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 7, name: 'Investment', freq: 'Q' },
    ],
  },
  consumption: {
    name: 'Personal Consumption',
    description: 'PCE Components - Monthly Data',
    icon: ShoppingCart,
    color: 'purple',
    headlines: [
      { tableCode: 'T20801', lineNumber: 1, name: 'PCE Total', freq: 'M' },
      { tableCode: 'T20801', lineNumber: 2, name: 'Goods', freq: 'M' },
      { tableCode: 'T20801', lineNumber: 13, name: 'Services', freq: 'M' },
    ],
  },
  investment: {
    name: 'Private Investment',
    description: 'Fixed Investment, Equipment, Structures',
    icon: Building2,
    color: 'teal',
    headlines: [
      { tableCode: 'T10101', lineNumber: 7, name: 'Gross Investment', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 8, name: 'Fixed Investment', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 13, name: 'Residential', freq: 'Q' },
    ],
  },
  income: {
    name: 'Personal Income (Quarterly)',
    description: 'Income Sources, Savings Rate - Quarterly',
    icon: PiggyBank,
    color: 'orange',
    headlines: [
      { tableCode: 'T70100', lineNumber: 3, name: 'Personal Income', freq: 'Q' },
      { tableCode: 'T20100', lineNumber: 41, name: 'Disposable Income', freq: 'Q' },
      { tableCode: 'T20100', lineNumber: 35, name: 'Savings Rate', freq: 'Q' },
    ],
  },
  government: {
    name: 'Government',
    description: 'Federal, State/Local Spending',
    icon: Landmark,
    color: 'red',
    headlines: [
      { tableCode: 'T10101', lineNumber: 22, name: 'Gov Spending', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 23, name: 'Federal', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 26, name: 'State/Local', freq: 'Q' },
    ],
  },
  trade: {
    name: 'Foreign Trade',
    description: 'Exports, Imports, Net Exports',
    icon: Globe,
    color: 'cyan',
    headlines: [
      { tableCode: 'T10105', lineNumber: 15, name: 'Net Exports', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 16, name: 'Exports', freq: 'Q' },
      { tableCode: 'T10101', lineNumber: 19, name: 'Imports', freq: 'Q' },
    ],
  },
};

const HEADLINE_SERIES = [
  { tableCode: 'T10101', lineNumber: 1, name: 'Real GDP', frequencies: ['Q', 'A'] },
  { tableCode: 'T10105', lineNumber: 1, name: 'Nominal GDP', frequencies: ['Q', 'A'] },
  { tableCode: 'T10101', lineNumber: 2, name: 'PCE', frequencies: ['Q', 'A'] },
  { tableCode: 'T10101', lineNumber: 7, name: 'Investment', frequencies: ['Q', 'A'] },
  { tableCode: 'T10101', lineNumber: 21, name: 'Government', frequencies: ['Q', 'A'] },
];

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

const formatPctChange = (value: number | null): string => {
  if (value === null || value === undefined) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

const calcPctChange = (current: number | null, previous: number | null): number | null => {
  if (current === null || previous === null || previous === 0) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
};

const getLatestWithChanges = (data: NIPATimeSeriesData[] | undefined, unit?: string | null) => {
  if (!data || data.length === 0) return { latest: null, qoq: null, yoy: null, isPercentData: false };

  const validData = data.filter(d => d.value !== null);
  if (validData.length === 0) return { latest: null, qoq: null, yoy: null, isPercentData: false };

  const latest = validData[validData.length - 1];
  const prev = validData.length > 1 ? validData[validData.length - 2] : null;
  const yearAgo = validData.length > 4 ? validData[validData.length - 5] : null;

  const isPercentData = unit?.toLowerCase().includes('percent') || false;

  let qoq: number | null = null;
  let yoy: number | null = null;

  if (isPercentData) {
    qoq = prev?.value !== null && prev?.value !== undefined ? latest.value! - prev.value : null;
    yoy = yearAgo?.value !== null && yearAgo?.value !== undefined ? latest.value! - yearAgo.value : null;
  } else {
    qoq = calcPctChange(latest.value, prev?.value ?? null);
    yoy = calcPctChange(latest.value, yearAgo?.value ?? null);
  }

  return { latest, qoq, yoy, isPercentData };
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
  qoqChange?: number | null;
  yoyChange?: number | null;
  period?: string;
  isLoading?: boolean;
  isPercentData?: boolean;
}

function MetricCard({ title, value, qoqChange, yoyChange, period, isLoading, isPercentData }: MetricCardProps) {
  const formatChange = (val: number | null) => {
    if (val === null || val === undefined) return 'N/A';
    const sign = val >= 0 ? '+' : '';
    if (isPercentData) {
      return `${sign}${val.toFixed(1)}pp`;
    }
    return `${sign}${val.toFixed(1)}%`;
  };

  return (
    <div className="p-3 rounded-lg border border-gray-200 bg-white">
      <p className="text-xs text-gray-500 font-medium truncate">{title}</p>
      {isLoading ? (
        <div className="flex justify-center py-2"><Loader2 className="w-4 h-4 animate-spin text-gray-400" /></div>
      ) : (
        <>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-xl font-bold">{value}</span>
            {period && <span className="text-[10px] text-gray-400">{period}</span>}
          </div>
          <div className="flex gap-3 mt-1">
            {qoqChange !== null && qoqChange !== undefined && (
              <div className="flex items-center gap-0.5">
                {qoqChange > 0 ? <TrendingUp className="w-3 h-3 text-emerald-500" /> :
                 qoqChange < 0 ? <TrendingDown className="w-3 h-3 text-red-500" /> :
                 <Minus className="w-3 h-3 text-gray-500" />}
                <span className={`text-[11px] font-medium ${qoqChange > 0 ? 'text-emerald-500' : qoqChange < 0 ? 'text-red-500' : 'text-gray-500'}`}>
                  {formatChange(qoqChange)} QoQ
                </span>
              </div>
            )}
            {yoyChange !== null && yoyChange !== undefined && (
              <span className={`text-[11px] font-medium ${yoyChange > 0 ? 'text-emerald-500' : yoyChange < 0 ? 'text-red-500' : 'text-gray-500'}`}>
                {formatChange(yoyChange)} YoY
              </span>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function ChangeIndicator({ value, isPercentData }: { value: number | null; isPercentData?: boolean }) {
  if (value === null) return <span className="text-gray-400">N/A</span>;
  const colorClass = value > 0 ? 'text-emerald-500' : value < 0 ? 'text-red-500' : 'text-gray-500';
  const sign = value >= 0 ? '+' : '';
  const suffix = isPercentData ? 'pp' : '%';
  return <span className={`font-semibold ${colorClass}`}>{sign}{value.toFixed(2)}{suffix}</span>;
}

interface TimeRangeSelectorProps {
  value: number;
  onChange: (v: number) => void;
  color?: string;
}

function TimeRangeSelector({ value, onChange, color = '#3b82f6' }: TimeRangeSelectorProps) {
  return (
    <div className="flex rounded-lg overflow-hidden border border-gray-300">
      {TIME_RANGE_OPTIONS.map(opt => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-3 py-1 text-xs font-medium transition-colors ${value === opt.value ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
          style={value === opt.value ? { backgroundColor: color } : {}}
        >
          {opt.label}
        </button>
      ))}
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
  value: 'pct' | 'abs';
  onChange: (v: 'pct' | 'abs') => void;
}

function ChartMetricToggle({ value, onChange }: ChartMetricToggleProps) {
  return (
    <div className="flex rounded-lg overflow-hidden border border-gray-300">
      <button
        onClick={() => onChange('pct')}
        className={`px-2 py-1 text-[11px] font-medium ${value === 'pct' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
      >
        % Change
      </button>
      <button
        onClick={() => onChange('abs')}
        className={`px-2 py-1 text-[11px] font-medium ${value === 'abs' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
      >
        Value
      </button>
    </div>
  );
}

// ============================================================================
// CATEGORY SECTION COMPONENT
// ============================================================================

interface CategorySectionProps {
  categoryKey: string;
  category: CategoryConfig;
}

function CategorySection({ categoryKey, category }: CategorySectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [chartMetric, setChartMetric] = useState<'pct' | 'abs'>('pct');
  const [timeRange, setTimeRange] = useState(5);

  const colorSet = SECTION_COLORS[category.color];

  const headlineQueries = useQueries({
    queries: category.headlines.map(h => ({
      queryKey: ['nipa-category-headline', categoryKey, h.tableCode, h.lineNumber, h.freq],
      queryFn: async () => {
        const response = await beaResearchAPI.getNIPASeries<NIPASeries[]>(h.tableCode);
        const series = response.data;
        const targetSeries = series.find(s => s.line_number === h.lineNumber);
        if (!targetSeries) return null;
        try {
          const dataResponse = await beaResearchAPI.getNIPASeriesData<NIPATimeSeries>(targetSeries.series_code, undefined, undefined, h.freq);
          return { ...h, seriesData: dataResponse.data, seriesInfo: targetSeries };
        } catch {
          return null;
        }
      },
      staleTime: 5 * 60 * 1000,
    })),
  });

  const historicalData = useMemo(() => {
    const validQueries = headlineQueries.filter(q => q.data?.seriesData?.data);
    if (validQueries.length === 0) return [];

    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = timeRange === 0 ? 0 : currentYear - timeRange;

    validQueries.forEach(q => {
      q.data?.seriesData?.data?.forEach((d: NIPATimeSeriesData) => {
        const yearMatch = d.time_period.match(/^(\d{4})/);
        if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
          allPeriods.add(d.time_period);
        }
      });
    });

    const sortedPeriods = Array.from(allPeriods).sort();

    return sortedPeriods.map((period) => {
      const point: Record<string, unknown> = { period };

      category.headlines.forEach((h, idx) => {
        const queryData = headlineQueries[idx]?.data;
        const seriesData = queryData?.seriesData?.data || [];
        const unit = queryData?.seriesData?.unit;
        const isPercentData = unit?.toLowerCase().includes('percent') || false;
        const key = h.name.replace(/\s+/g, '_');

        const currentIdx = seriesData.findIndex((d: NIPATimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;
        const periodsPerYear = h.freq === 'M' ? 12 : 4;
        const yearAgo = currentIdx >= periodsPerYear ? seriesData[currentIdx - periodsPerYear] : null;

        point[`${key}_value`] = current?.value ?? null;
        point[`${key}_isPercentData`] = isPercentData;
        point[`${key}_unit`] = unit;
        point[`${key}_unitMult`] = queryData?.seriesData?.unit_mult;

        if (isPercentData) {
          point[`${key}_qoq`] = (current?.value != null && prev?.value != null)
            ? current.value - prev.value : null;
          point[`${key}_yoy`] = (current?.value != null && yearAgo?.value != null)
            ? current.value - yearAgo.value : null;
        } else {
          point[`${key}_qoq`] = calcPctChange(current?.value ?? null, prev?.value ?? null);
          point[`${key}_yoy`] = calcPctChange(current?.value ?? null, yearAgo?.value ?? null);
        }
      });

      return point;
    });
  }, [headlineQueries, timeRange, category.headlines]);

  const isLoading = headlineQueries.some(q => q.isLoading);

  return (
    <SectionCard
      title={category.name}
      description={category.description}
      color={category.color}
      icon={category.icon}
      rightContent={
        <div className="flex gap-2 items-center">
          <TimeRangeSelector value={timeRange} onChange={setTimeRange} color={colorSet.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Headline Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-6">
        {headlineQueries.map((q, idx) => {
          const headline = category.headlines[idx];
          const data = q.data?.seriesData;
          const { latest, qoq, yoy, isPercentData } = getLatestWithChanges(data?.data, data?.unit);

          return (
            <MetricCard
              key={idx}
              title={headline.name}
              value={formatValue(latest?.value ?? null, data?.unit, data?.unit_mult)}
              qoqChange={qoq}
              yoyChange={yoy}
              period={latest?.time_period}
              isLoading={q.isLoading}
              isPercentData={isPercentData}
            />
          );
        })}
      </div>

      {/* Chart or Table View */}
      {isLoading ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
      ) : historicalData.length > 0 ? (
        viewMode === 'chart' ? (
          <div>
            <div className="flex justify-end mb-2">
              <ChartMetricToggle value={chartMetric} onChange={setChartMetric} />
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={historicalData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
                  <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                  <YAxis
                    tick={{ fontSize: 10 }}
                    width={60}
                    tickFormatter={(v) => chartMetric === 'pct' ? `${v.toFixed(1)}%` : formatValue(v, null, null)}
                  />
                  {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />}
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                    formatter={(value: number, name: string) => {
                      const isQoQ = name.endsWith('_qoq');
                      const baseName = name.replace(/_qoq$|_yoy$|_value$/, '').replace(/_/g, ' ');
                      if (chartMetric === 'pct') {
                        return [formatPctChange(value), `${baseName} (${isQoQ ? 'QoQ' : 'YoY'})`];
                      }
                      return [formatValue(value, null, null), baseName];
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                  {category.headlines.map((h, idx) => {
                    const key = h.name.replace(/\s+/g, '_');
                    return (
                      <Line
                        key={key}
                        type="monotone"
                        dataKey={chartMetric === 'pct' ? `${key}_qoq` : `${key}_value`}
                        name={chartMetric === 'pct' ? `${h.name} QoQ` : h.name}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        strokeWidth={2}
                        dot={false}
                        connectNulls
                      />
                    );
                  })}
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div className="max-h-96 overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-100">
                <tr>
                  <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-10">Period</th>
                  {category.headlines.map((h, idx) => {
                    const key = h.name.replace(/\s+/g, '_');
                    const isPercentData = (historicalData[0] as Record<string, unknown>)?.[`${key}_isPercentData`] || false;
                    const qoqLabel = h.freq === 'M' ? 'MoM' : 'QoQ';
                    return (
                      <React.Fragment key={h.name}>
                        <th className="text-right p-2 font-semibold border-l-2 border-gray-200">
                          <div className="flex items-center justify-end gap-1">
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                            {h.name}
                          </div>
                        </th>
                        <th className="text-right p-2 text-[11px] font-semibold">{isPercentData ? `${qoqLabel} pp` : `${qoqLabel}%`}</th>
                        <th className="text-right p-2 text-[11px] font-semibold">{isPercentData ? 'YoY pp' : 'YoY%'}</th>
                      </React.Fragment>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {historicalData.slice().reverse().map((row, idx) => {
                  const typedRow = row as Record<string, unknown>;
                  return (
                    <tr key={typedRow.period as string} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className={`p-2 font-medium sticky left-0 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                        {typedRow.period as string}
                      </td>
                      {category.headlines.map((h) => {
                        const key = h.name.replace(/\s+/g, '_');
                        const isPercentData = typedRow[`${key}_isPercentData`] || false;
                        return (
                          <React.Fragment key={h.name}>
                            <td className="text-right p-2 font-mono border-l-2 border-gray-200">
                              {formatValue(typedRow[`${key}_value`] as number | null, typedRow[`${key}_unit`] as string | null, typedRow[`${key}_unitMult`] as number | null)}
                            </td>
                            <td className="text-right p-2">
                              <ChangeIndicator value={typedRow[`${key}_qoq`] as number | null} isPercentData={isPercentData as boolean} />
                            </td>
                            <td className="text-right p-2">
                              <ChangeIndicator value={typedRow[`${key}_yoy`] as number | null} isPercentData={isPercentData as boolean} />
                            </td>
                          </React.Fragment>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )
      ) : (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Loading data...</div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// DATA EXPLORER COMPONENT
// ============================================================================

interface DataExplorerProps {
  tables: NIPATable[];
}

function DataExplorer({ tables }: DataExplorerProps) {
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [frequency, setFrequency] = useState<'A' | 'Q' | 'M'>('Q');
  const [timeRange, setTimeRange] = useState(5);
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [chartMetric, setChartMetric] = useState<'pct' | 'abs'>('pct');
  const [selectedSeries, setSelectedSeries] = useState<NIPASeries[]>([]);

  const colorSet = SECTION_COLORS.gray;

  const { data: seriesList, isLoading: seriesLoading } = useQuery({
    queryKey: ['nipa-explorer-series', selectedTable],
    queryFn: async () => {
      const response = await beaResearchAPI.getNIPASeries<NIPASeries[]>(selectedTable);
      return response.data;
    },
    enabled: !!selectedTable,
  });

  const seriesQueries = useQueries({
    queries: selectedSeries.map(s => ({
      queryKey: ['nipa-explorer-data', s.series_code, frequency],
      queryFn: async () => {
        const response = await beaResearchAPI.getNIPASeriesData<NIPATimeSeries>(s.series_code, undefined, undefined, frequency);
        return response.data;
      },
      enabled: !!s,
      staleTime: 5 * 60 * 1000,
    })),
  });

  React.useEffect(() => {
    setSelectedSeries([]);
  }, [selectedTable]);

  const historicalData = useMemo(() => {
    if (selectedSeries.length === 0) return [];

    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = timeRange === 0 ? 0 : currentYear - timeRange;

    seriesQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: NIPATimeSeriesData) => {
          const yearMatch = d.time_period.match(/^(\d{4})/);
          if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      }
    });

    const sortedPeriods = Array.from(allPeriods).sort();
    const periodsPerYear = frequency === 'M' ? 12 : frequency === 'Q' ? 4 : 1;

    return sortedPeriods.map((period) => {
      const point: Record<string, unknown> = { period };

      selectedSeries.forEach((s, sIdx) => {
        const queryData = seriesQueries[sIdx]?.data;
        const seriesData = queryData?.data || [];
        const unit = queryData?.unit;
        const isPercentData = unit?.toLowerCase().includes('percent') || false;

        const currentIdx = seriesData.findIndex((d: NIPATimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;
        const yearAgo = currentIdx >= periodsPerYear ? seriesData[currentIdx - periodsPerYear] : null;

        point[`${s.series_code}_value`] = current?.value ?? null;
        point[`${s.series_code}_isPercentData`] = isPercentData;
        point[`${s.series_code}_unit`] = unit;
        point[`${s.series_code}_unitMult`] = queryData?.unit_mult;

        if (isPercentData) {
          point[`${s.series_code}_qoq`] = (current?.value != null && prev?.value != null)
            ? current.value - prev.value : null;
          point[`${s.series_code}_yoy`] = (current?.value != null && yearAgo?.value != null)
            ? current.value - yearAgo.value : null;
        } else {
          point[`${s.series_code}_qoq`] = calcPctChange(current?.value ?? null, prev?.value ?? null);
          point[`${s.series_code}_yoy`] = calcPctChange(current?.value ?? null, yearAgo?.value ?? null);
        }
      });

      return point;
    });
  }, [selectedSeries, seriesQueries, timeRange, frequency]);

  const toggleSeries = (series: NIPASeries) => {
    if (selectedSeries.find(s => s.series_code === series.series_code)) {
      setSelectedSeries(selectedSeries.filter(s => s.series_code !== series.series_code));
    } else if (selectedSeries.length < 8) {
      setSelectedSeries([...selectedSeries, series]);
    }
  };

  const getPeriodLabel = () => {
    if (frequency === 'M') return 'MoM';
    if (frequency === 'Q') return 'QoQ';
    return 'YoY';
  };

  return (
    <SectionCard
      title="Data Explorer"
      description="Explore all NIPA tables and series"
      color="gray"
      icon={Search}
      rightContent={
        <div className="flex gap-2 items-center">
          <TimeRangeSelector value={timeRange} onChange={setTimeRange} color={colorSet.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Controls Row */}
      <div className="flex flex-wrap gap-4 mb-6 items-start">
        {/* Table Selector */}
        <select
          value={selectedTable}
          onChange={(e) => setSelectedTable(e.target.value)}
          className="min-w-[350px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select a table...</option>
          {tables.map(t => (
            <option key={t.table_name} value={t.table_name}>
              {t.table_name} - {t.table_description?.substring(0, 50)}...
            </option>
          ))}
        </select>

        {/* Frequency Selector */}
        <div className="flex rounded-lg overflow-hidden border border-gray-300">
          {(['A', 'Q', 'M'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFrequency(f)}
              className={`px-4 py-2 text-sm font-medium ${frequency === f ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              {f === 'A' ? 'Annual' : f === 'Q' ? 'Quarterly' : 'Monthly'}
            </button>
          ))}
        </div>

        {selectedTable && (
          <span className="text-sm text-gray-500 self-center">
            {seriesList?.length || 0} series available • {selectedSeries.length}/8 selected
          </span>
        )}
      </div>

      {/* Selected Series Chips */}
      {selectedSeries.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {selectedSeries.map((s, idx) => (
            <span
              key={s.series_code}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs"
              style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
            >
              {s.line_number}. {s.line_description?.substring(0, 30)}...
              <button onClick={() => toggleSeries(s)} className="hover:bg-white/20 rounded-full p-0.5">×</button>
            </span>
          ))}
          <button
            onClick={() => setSelectedSeries([])}
            className="px-2 py-1 border border-dashed border-gray-400 rounded-full text-xs text-gray-500 hover:bg-gray-100"
          >
            Clear All
          </button>
        </div>
      )}

      {/* Main Content Area */}
      {!selectedTable ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select a table above to explore its series data.</div>
      ) : seriesLoading ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
      ) : (
        <div className="flex gap-4 flex-col lg:flex-row">
          {/* Series List Panel */}
          <div className="lg:w-[350px] flex-shrink-0 max-h-[500px] overflow-auto border border-gray-200 rounded-lg">
            <div className="p-3 bg-gray-100 border-b border-gray-200 sticky top-0 z-10">
              <span className="text-sm font-semibold">Available Series (click to add)</span>
            </div>
            <table className="w-full text-sm">
              <tbody>
                {seriesList?.map((s) => {
                  const isSelected = selectedSeries.some(sel => sel.series_code === s.series_code);
                  const idx = selectedSeries.findIndex(sel => sel.series_code === s.series_code);
                  return (
                    <tr
                      key={s.series_code}
                      onClick={() => toggleSeries(s)}
                      className={`cursor-pointer hover:bg-gray-100 ${isSelected ? 'bg-blue-50' : ''}`}
                    >
                      <td className="w-12 py-2 px-3">
                        {isSelected ? (
                          <span
                            className="w-5 h-5 rounded-full flex items-center justify-center text-white text-[10px] font-bold"
                            style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
                          >
                            {idx + 1}
                          </span>
                        ) : (
                          <span className="text-gray-400">{s.line_number}</span>
                        )}
                      </td>
                      <td className={`py-2 pr-3 ${isSelected ? 'font-semibold' : ''}`}>
                        {s.line_description}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Chart/Table View Panel */}
          <div className="flex-1 min-w-0">
            {selectedSeries.length === 0 ? (
              <div className="flex items-center justify-center h-72 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <span className="text-gray-500">Select series from the list to view data</span>
              </div>
            ) : historicalData.length > 0 ? (
              viewMode === 'chart' ? (
                <div>
                  <div className="flex justify-end mb-2">
                    <ChartMetricToggle value={chartMetric} onChange={setChartMetric} />
                  </div>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={historicalData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
                        <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                        <YAxis
                          tick={{ fontSize: 10 }}
                          width={70}
                          tickFormatter={(v) => chartMetric === 'pct' ? `${v.toFixed(1)}%` : formatValue(v, null, null)}
                        />
                        {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />}
                        <Tooltip
                          contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                          formatter={(value: number, name: string) => {
                            const isPeriodChange = name.includes('_qoq');
                            const series = selectedSeries.find(s => name.startsWith(s.series_code));
                            const label = series?.line_description?.substring(0, 30) || name;
                            if (chartMetric === 'pct') {
                              return [formatPctChange(value), `${label} (${isPeriodChange ? getPeriodLabel() : 'YoY'})`];
                            }
                            return [formatValue(value, null, null), label];
                          }}
                        />
                        <Legend wrapperStyle={{ fontSize: '10px' }} />
                        {selectedSeries.map((s, idx) => (
                          <Line
                            key={s.series_code}
                            type="monotone"
                            dataKey={chartMetric === 'pct' ? `${s.series_code}_qoq` : `${s.series_code}_value`}
                            name={`${s.line_description?.substring(0, 20)}${chartMetric === 'pct' ? ` ${getPeriodLabel()}` : ''}`}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            strokeWidth={2}
                            dot={false}
                            connectNulls
                          />
                        ))}
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ) : (
                <div className="max-h-[450px] overflow-auto">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-100">
                      <tr>
                        <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-10">Period</th>
                        {selectedSeries.map((s, idx) => {
                          const isPercentData = seriesQueries[idx]?.data?.unit?.toLowerCase().includes('percent') || false;
                          return (
                            <React.Fragment key={s.series_code}>
                              <th className="text-right p-2 font-semibold border-l-2 border-gray-200">
                                <div className="flex items-center justify-end gap-1">
                                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                                  {s.line_description?.substring(0, 15)}
                                </div>
                              </th>
                              <th className="text-right p-2 text-[11px] font-semibold">{isPercentData ? `${getPeriodLabel()} pp` : `${getPeriodLabel()}%`}</th>
                              <th className="text-right p-2 text-[11px] font-semibold">{isPercentData ? 'YoY pp' : 'YoY%'}</th>
                            </React.Fragment>
                          );
                        })}
                      </tr>
                    </thead>
                    <tbody>
                      {historicalData.slice().reverse().map((row, idx) => {
                        const typedRow = row as Record<string, unknown>;
                        return (
                          <tr key={typedRow.period as string} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                            <td className={`p-2 font-medium sticky left-0 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                              {typedRow.period as string}
                            </td>
                            {selectedSeries.map((s) => {
                              const isPercentData = typedRow[`${s.series_code}_isPercentData`] || false;
                              return (
                                <React.Fragment key={s.series_code}>
                                  <td className="text-right p-2 font-mono border-l-2 border-gray-200">
                                    {formatValue(typedRow[`${s.series_code}_value`] as number | null, typedRow[`${s.series_code}_unit`] as string | null, typedRow[`${s.series_code}_unitMult`] as number | null)}
                                  </td>
                                  <td className="text-right p-2">
                                    <ChangeIndicator value={typedRow[`${s.series_code}_qoq`] as number | null} isPercentData={isPercentData as boolean} />
                                  </td>
                                  <td className="text-right p-2">
                                    <ChangeIndicator value={typedRow[`${s.series_code}_yoy`] as number | null} isPercentData={isPercentData as boolean} />
                                  </td>
                                </React.Fragment>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )
            ) : (
              <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
            )}
          </div>
        </div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function NIPAExplorer() {
  const { data: tables, isLoading: tablesLoading } = useQuery({
    queryKey: ['nipa-tables'],
    queryFn: async () => {
      const response = await beaResearchAPI.getNIPATables<NIPATable[]>();
      return response.data;
    },
  });

  const headlineQueries = useQueries({
    queries: HEADLINE_SERIES.map(hs => ({
      queryKey: ['nipa-headline', hs.tableCode, hs.lineNumber],
      queryFn: async () => {
        const response = await beaResearchAPI.getNIPASeries<NIPASeries[]>(hs.tableCode);
        const series = response.data;
        const targetSeries = series.find(s => s.line_number === hs.lineNumber);
        if (!targetSeries) return null;

        for (const freq of hs.frequencies) {
          try {
            const dataResponse = await beaResearchAPI.getNIPASeriesData<NIPATimeSeries>(targetSeries.series_code, undefined, undefined, freq);
            if (dataResponse.data?.data?.length > 0) {
              return dataResponse.data;
            }
          } catch {
            // Try next frequency
          }
        }
        return null;
      },
      staleTime: 5 * 60 * 1000,
    })),
  });

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
          <h1 className="text-2xl font-bold">NIPA Explorer</h1>
          <p className="text-sm text-gray-500">National Income and Product Accounts - GDP, Personal Income, Government</p>
        </div>
      </div>

      <hr className="my-6 border-gray-200" />

      {/* Economic Snapshot */}
      <SectionCard title="Economic Snapshot" description="Key macroeconomic indicators" color="blue" icon={BarChart3} collapsible={false}>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {HEADLINE_SERIES.map((hs, idx) => {
            const data = headlineQueries[idx].data;
            const { latest, qoq, yoy, isPercentData } = getLatestWithChanges(data?.data, data?.unit);

            return (
              <MetricCard
                key={`${hs.tableCode}-${hs.lineNumber}`}
                title={hs.name}
                value={formatValue(latest?.value ?? null, data?.unit, data?.unit_mult)}
                qoqChange={qoq}
                yoyChange={yoy}
                period={latest?.time_period}
                isLoading={headlineQueries[idx].isLoading}
                isPercentData={isPercentData}
              />
            );
          })}
        </div>
      </SectionCard>

      {/* Category Sections */}
      {Object.entries(NIPA_CATEGORIES).map(([key, category]) => (
        <CategorySection key={key} categoryKey={key} category={category} />
      ))}

      {/* Data Explorer */}
      <DataExplorer tables={tables || []} />
    </div>
  );
}
