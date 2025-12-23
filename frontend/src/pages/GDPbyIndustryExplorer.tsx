import React, { useState, useMemo, useEffect } from 'react';
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
  Factory,
  Layers,
  Loader2,
  Zap,
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
  Treemap,
  ReferenceLine,
} from 'recharts';
import { beaResearchAPI } from '../services/api';

// ============================================================================
// CONSTANTS & TYPES
// ============================================================================

interface GDPByIndustryTable {
  table_id: number;
  table_description: string;
  has_annual: boolean;
  has_quarterly: boolean;
  first_annual_year?: number | null;
  last_annual_year?: number | null;
  first_quarterly_year?: number | null;
  last_quarterly_year?: number | null;
  is_active: boolean;
}

interface GDPByIndustryIndustry {
  industry_code: string;
  industry_description: string;
  parent_code?: string | null;
  industry_level?: number | null;
}

interface GDPByIndustryTimeSeriesData {
  time_period: string;
  value: number | null;
}

interface GDPByIndustryTimeSeries {
  table_id: number;
  table_description: string;
  industry_code: string;
  industry_description: string;
  frequency: string;
  unit?: string | null;
  unit_mult?: number | null;
  data: GDPByIndustryTimeSeriesData[];
}

interface GDPByIndustrySnapshotItem {
  industry_code: string;
  industry_description: string;
  value: number;
}

interface GDPByIndustrySnapshot {
  table_id: number;
  table_description: string;
  frequency: string;
  year?: number;
  quarter?: string;
  unit?: string | null;
  unit_mult?: number | null;
  data: GDPByIndustrySnapshotItem[];
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

const PERIOD_OPTIONS = [
  { label: '5Y', value: 5 },
  { label: '10Y', value: 10 },
  { label: '20Y', value: 20 },
  { label: '30Y', value: 30 },
  { label: 'All', value: 0 },
];

const HEADLINE_INDUSTRIES = [
  { code: 'FIRE', name: 'Finance/RE', description: 'Finance, insurance, real estate' },
  { code: 'PROF', name: 'Professional', description: 'Professional and business services' },
  { code: '31G', name: 'Manufacturing', description: 'Durable and non-durable goods' },
  { code: 'G', name: 'Government', description: 'Federal, state, and local' },
  { code: '62', name: 'Healthcare', description: 'Healthcare and social assistance' },
  { code: '44RT', name: 'Retail Trade', description: 'Retail trade' },
];

const AGGREGATE_INDUSTRY_CODES = ['GDP', 'ALL', 'PVT', 'PRV'];

interface CategoryConfig {
  name: string;
  description: string;
  icon: React.ElementType;
  color: ColorKey;
  tableId: number;
  headlines: { code: string; name: string }[];
}

const INDUSTRY_CATEGORIES: Record<string, CategoryConfig> = {
  valueAdded: {
    name: 'Value Added',
    description: 'Contributions to GDP by Industry',
    icon: BarChart3,
    color: 'green',
    tableId: 1,
    headlines: [
      { code: 'FIRE', name: 'Finance/RE' },
      { code: 'PROF', name: 'Professional' },
      { code: '31G', name: 'Manufacturing' },
      { code: 'G', name: 'Government' },
      { code: '62', name: 'Healthcare' },
      { code: '44RT', name: 'Retail Trade' },
    ],
  },
  grossOutput: {
    name: 'Gross Output',
    description: 'Total Industry Output Value',
    icon: Factory,
    color: 'purple',
    tableId: 8,
    headlines: [
      { code: '31G', name: 'Manufacturing' },
      { code: 'FIRE', name: 'Finance/RE' },
      { code: '23', name: 'Construction' },
      { code: '42', name: 'Wholesale Trade' },
      { code: 'PROF', name: 'Professional' },
      { code: '48TW', name: 'Transport/Warehouse' },
    ],
  },
  compensation: {
    name: 'Compensation',
    description: 'Employee Compensation by Industry',
    icon: Layers,
    color: 'orange',
    tableId: 6,
    headlines: [
      { code: 'G', name: 'Government' },
      { code: '62', name: 'Healthcare' },
      { code: 'PROF', name: 'Professional' },
      { code: '31G', name: 'Manufacturing' },
      { code: '61', name: 'Education' },
      { code: 'FIRE', name: 'Finance/RE' },
    ],
  },
};

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

  const defaultUnitMult = 9;
  const multiplier = Math.pow(10, unitMult ?? defaultUnitMult);
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

const getTreemapColor = (value: number, maxValue: number, minValue: number) => {
  if (value === null || value === undefined || maxValue === minValue) {
    return 'rgb(59, 130, 246)';
  }
  const ratio = Math.max(0, Math.min(1, (value - minValue) / (maxValue - minValue)));
  const colors = [
    { r: 191, g: 219, b: 254 },
    { r: 147, g: 197, b: 253 },
    { r: 96, g: 165, b: 250 },
    { r: 59, g: 130, b: 246 },
    { r: 37, g: 99, b: 235 },
    { r: 29, g: 78, b: 216 },
  ];

  const scaledIndex = ratio * (colors.length - 1);
  const lowerIndex = Math.floor(scaledIndex);
  const upperIndex = Math.min(lowerIndex + 1, colors.length - 1);
  const t = scaledIndex - lowerIndex;

  const lower = colors[lowerIndex] || colors[0];
  const upper = colors[upperIndex] || colors[colors.length - 1];

  const r = Math.round(lower.r + (upper.r - lower.r) * t);
  const g = Math.round(lower.g + (upper.g - lower.g) * t);
  const b = Math.round(lower.b + (upper.b - lower.b) * t);

  return `rgb(${r}, ${g}, ${b})`;
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
  isPercentagePoints?: boolean;
  period?: string;
  isLoading?: boolean;
}

function MetricCard({ title, value, change, isPercentagePoints, period, isLoading }: MetricCardProps) {
  const colorClass = change && change > 0.1 ? 'text-emerald-500' : change && change < -0.1 ? 'text-red-500' : 'text-gray-500';

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
          {change !== null && change !== undefined && (
            <div className="flex items-center gap-0.5 mt-1">
              {change > 0.1 ? <TrendingUp className="w-3 h-3 text-emerald-500" /> :
               change < -0.1 ? <TrendingDown className="w-3 h-3 text-red-500" /> :
               <Minus className="w-3 h-3 text-gray-500" />}
              <span className={`text-[11px] font-medium ${colorClass}`}>
                {change > 0 ? '+' : ''}{change.toFixed(1)}{isPercentagePoints ? 'pp' : '%'}
              </span>
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
          className={`px-2 py-1 text-xs font-medium transition-colors ${value === opt.value ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
          style={value === opt.value ? { backgroundColor: color } : {}}
        >
          {opt.label}
        </button>
      ))}
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
        className={`px-2 py-1 text-xs font-medium transition-colors ${value === 'pct' ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
        style={value === 'pct' ? { backgroundColor: color } : {}}
      >
        % Change
      </button>
      <button
        onClick={() => onChange('value')}
        className={`px-2 py-1 text-xs font-medium transition-colors ${value === 'value' ? 'text-white' : 'text-gray-600 hover:bg-gray-100'}`}
        style={value === 'value' ? { backgroundColor: color } : {}}
      >
        Value
      </button>
    </div>
  );
}

// ============================================================================
// CATEGORY SECTION COMPONENT (Shows ALL industries)
// ============================================================================

interface CategorySectionProps {
  categoryKey: string;
  category: CategoryConfig;
  industries: GDPByIndustryIndustry[];
}

function CategorySection({ categoryKey, category, industries }: CategorySectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('table');
  const [periodYears, setPeriodYears] = useState(10);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('value');

  const colorSet = SECTION_COLORS[category.color];

  // Filter industries - exclude aggregates - these are ALL the industries
  const allIndustries = useMemo(() => {
    return industries
      .filter(ind =>
        !AGGREGATE_INDUSTRY_CODES.includes(ind.industry_code) &&
        !ind.industry_description?.toLowerCase().includes('gross domestic product') &&
        !ind.industry_description?.toLowerCase().includes('private industries') &&
        !ind.industry_description?.toLowerCase().includes('all industries')
      )
      .map(ind => ({
        code: ind.industry_code,
        name: ind.industry_description || ind.industry_code,
      }));
  }, [industries]);

  // Fetch time series data for ALL industries
  const industryQueries = useQueries({
    queries: allIndustries.map(ind => ({
      queryKey: ['gdpbyindustry-category-data', categoryKey, category.tableId, ind.code],
      queryFn: async () => {
        try {
          const response = await beaResearchAPI.getGDPByIndustryData<GDPByIndustryTimeSeries>(
            category.tableId,
            ind.code,
            'A'
          );
          return response.data;
        } catch {
          return null;
        }
      },
      staleTime: 5 * 60 * 1000,
    })),
  });

  // Prepare chart data from ALL industries
  const chartData = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    industryQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: GDPByIndustryTimeSeriesData) => {
          const yearMatch = d.time_period.match(/^(\d{4})/);
          if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      }
    });

    const sortedPeriods = Array.from(allPeriods).sort();
    return sortedPeriods.map(period => {
      const point: Record<string, unknown> = { period };
      allIndustries.forEach((ind, idx) => {
        const data = industryQueries[idx]?.data;
        const seriesData = data?.data || [];
        const currentIdx = seriesData.findIndex((d: GDPByIndustryTimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        const isPercentOrIndex = data?.unit?.toLowerCase().includes('percent') || data?.unit?.toLowerCase().includes('index');

        let pctChange: number | null = null;
        if (current?.value !== null && current?.value !== undefined && prev?.value !== null && prev?.value !== undefined) {
          if (isPercentOrIndex) {
            pctChange = current.value - prev.value;
          } else {
            pctChange = calcPctChange(current.value, prev.value);
          }
        }

        point[`${ind.code}_value`] = current?.value ?? null;
        point[`${ind.code}_pct`] = pctChange;
        point[`${ind.code}_isPercentOrIndex`] = isPercentOrIndex;
      });
      return point;
    });
  }, [industryQueries, allIndustries, periodYears]);

  const primaryData = industryQueries[0]?.data;
  const isLoading = industryQueries.some(q => q.isLoading);
  const loadedCount = industryQueries.filter(q => !q.isLoading).length;

  // For chart, limit to top industries by latest value to avoid visual clutter
  const topIndustriesForChart = useMemo(() => {
    if (chartData.length === 0) return allIndustries.slice(0, 8);
    const latestPeriod = chartData[chartData.length - 1] as Record<string, unknown>;
    return [...allIndustries]
      .sort((a, b) => ((latestPeriod[`${b.code}_value`] as number) || 0) - ((latestPeriod[`${a.code}_value`] as number) || 0))
      .slice(0, 8);
  }, [allIndustries, chartData]);

  return (
    <SectionCard
      title={category.name}
      description={`${category.description} - All ${allIndustries.length} industries`}
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
          <span className="text-xs text-gray-500">Loading {loadedCount}/{allIndustries.length} industries...</span>
        </div>
      )}

      {/* Time Series Chart or Table - showing ALL industries */}
      {allIndustries.length === 0 ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">No industry data available</div>
      ) : chartData.length === 0 && !isLoading ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available</div>
      ) : viewMode === 'chart' ? (
        <div>
          <p className="text-xs text-gray-500 mb-2">
            Showing top 8 industries by value (switch to Table view for all {allIndustries.length} industries)
          </p>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
                <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                <YAxis
                  tick={{ fontSize: 10 }}
                  width={80}
                  tickFormatter={(v) => chartMetric === 'pct' ? `${v?.toFixed(1)}%` : formatValue(v, primaryData?.unit, primaryData?.unit_mult)}
                  domain={chartMetric === 'pct' ? ['auto', 'auto'] : undefined}
                />
                {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />}
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                  formatter={(value: number, name: string) => {
                    const code = name.split('_')[0];
                    const idx = allIndustries.findIndex(i => i.code === code);
                    const data = industryQueries[idx]?.data;
                    const isPct = name.endsWith('_pct');
                    const isPercentOrIndex = data?.unit?.toLowerCase().includes('percent') || data?.unit?.toLowerCase().includes('index');
                    if (isPct) {
                      const suffix = isPercentOrIndex ? 'pp' : '%';
                      return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}${suffix}`, `${allIndustries[idx]?.name?.substring(0, 25) || code} (YoY)`];
                    }
                    return [formatValue(value, data?.unit, data?.unit_mult), allIndustries[idx]?.name?.substring(0, 25) || code];
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => {
                  const code = v.split('_')[0];
                  return allIndustries.find(i => i.code === code)?.name?.substring(0, 18) || code;
                }} />
                {topIndustriesForChart.map((ind, idx) => (
                  <Line
                    key={ind.code}
                    type="monotone"
                    dataKey={chartMetric === 'pct' ? `${ind.code}_pct` : `${ind.code}_value`}
                    name={chartMetric === 'pct' ? `${ind.code}_pct` : ind.code}
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
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-20">Period</th>
                {allIndustries.map((ind) => (
                  <React.Fragment key={ind.code}>
                    <th className="text-right p-2 font-semibold whitespace-nowrap text-xs">
                      {ind.name?.substring(0, 15) || ind.code}
                    </th>
                    <th className="text-right p-2 font-semibold text-[10px] text-gray-500">YoY%</th>
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {chartData.slice().reverse().map((row, rowIdx) => {
                const typedRow = row as Record<string, unknown>;
                return (
                  <tr key={typedRow.period as string} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className={`p-2 font-medium sticky left-0 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} z-10`}>
                      {typedRow.period as string}
                    </td>
                    {allIndustries.map((ind, idx) => {
                      const data = industryQueries[idx]?.data;
                      const isPercentOrIndex = typedRow[`${ind.code}_isPercentOrIndex`] as boolean;
                      const pctChange = typedRow[`${ind.code}_pct`] as number | null;
                      return (
                        <React.Fragment key={ind.code}>
                          <td className="text-right p-2 font-mono text-xs">
                            {formatValue(typedRow[`${ind.code}_value`] as number | null, data?.unit, data?.unit_mult)}
                          </td>
                          <td className="text-right p-2 text-xs">
                            {pctChange !== null && pctChange !== undefined ? (
                              <span className={`font-medium font-mono ${pctChange > 0.1 ? 'text-emerald-600' : pctChange < -0.1 ? 'text-red-600' : 'text-gray-500'}`}>
                                {pctChange >= 0 ? '+' : ''}{pctChange.toFixed(2)}{isPercentOrIndex ? 'pp' : '%'}
                              </span>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
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
      )}
    </SectionCard>
  );
}

// ============================================================================
// TOP INDUSTRIES SECTION (with Timeline)
// ============================================================================

function TopIndustriesSection() {
  const [periodYears, setPeriodYears] = useState(20);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);

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

  // Fetch snapshot data for selected year
  const { data: snapshotData, isLoading } = useQuery({
    queryKey: ['gdpbyindustry-top-industries', selectedYear],
    queryFn: async () => {
      const response = await beaResearchAPI.getGDPByIndustrySnapshot<GDPByIndustrySnapshot>(
        1,
        'A',
        selectedYear ? parseInt(selectedYear, 10) : undefined
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Set default selected year to latest when data loads
  useEffect(() => {
    if (!selectedYear && snapshotData?.year) {
      setSelectedYear(snapshotData.year.toString());
    }
  }, [snapshotData, selectedYear]);

  // Reset year when period changes
  useEffect(() => {
    setSelectedYear(null);
  }, [periodYears]);

  // Calculate top and bottom industries for selected year
  const { topIndustries, bottomIndustries } = useMemo(() => {
    if (!snapshotData?.data) return { topIndustries: [], bottomIndustries: [] };
    const filtered = snapshotData.data.filter((d: GDPByIndustrySnapshotItem) =>
      d.value > 0 &&
      !AGGREGATE_INDUSTRY_CODES.includes(d.industry_code) &&
      !d.industry_description?.toLowerCase().includes('gross domestic product') &&
      !d.industry_description?.toLowerCase().includes('private industries') &&
      !d.industry_description?.toLowerCase().includes('all industries')
    );
    const sorted = [...filtered].sort((a, b) => b.value - a.value);
    return {
      topIndustries: sorted.slice(0, 10),
      bottomIndustries: sorted.slice(-5).reverse(),
    };
  }, [snapshotData]);

  // Get available years
  const availableYears = years.filter(y => parseInt(y) <= currentYear);

  return (
    <SectionCard
      title="Top Industries"
      description="Largest and Smallest Industries by Value Added"
      color="red"
      icon={Zap}
      rightContent={
        <div className="flex gap-2 items-center">
          <PeriodSelector value={periodYears} onChange={(v) => {
            setPeriodYears(v);
            setSelectedYear(null);
          }} color={colorSet.main} />
        </div>
      }
    >
      {/* Tables */}
      {snapshotData?.data ? (
        <>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top 10 */}
          <div>
            <h4 className="text-sm font-bold text-emerald-600 mb-2 flex items-center gap-1">
              <TrendingUp className="w-4 h-4" />
              Top 10 Industries ({selectedYear || snapshotData?.year?.toString()})
            </h4>
            <table className="w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left p-2 font-semibold w-10">#</th>
                  <th className="text-left p-2 font-semibold">Industry</th>
                  <th className="text-right p-2 font-semibold">Value</th>
                </tr>
              </thead>
              <tbody>
                {topIndustries.length > 0 ? topIndustries.map((ind, idx) => (
                  <tr key={ind.industry_code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="p-2">{idx + 1}</td>
                    <td className="p-2">{ind.industry_description?.substring(0, 30)}</td>
                    <td className="p-2 text-right font-mono text-emerald-600">
                      {formatValue(ind.value, snapshotData.unit, snapshotData.unit_mult)}
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

          {/* Bottom 5 */}
          <div>
            <h4 className="text-sm font-bold text-gray-600 mb-2 flex items-center gap-1">
              <TrendingDown className="w-4 h-4" />
              Smallest 5 Industries ({selectedYear || snapshotData?.year?.toString()})
            </h4>
            <table className="w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left p-2 font-semibold w-10">#</th>
                  <th className="text-left p-2 font-semibold">Industry</th>
                  <th className="text-right p-2 font-semibold">Value</th>
                </tr>
              </thead>
              <tbody>
                {bottomIndustries.length > 0 ? bottomIndustries.map((ind, idx) => (
                  <tr key={ind.industry_code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="p-2">{idx + 1}</td>
                    <td className="p-2">{ind.industry_description?.substring(0, 30)}</td>
                    <td className="p-2 text-right font-mono text-gray-500">
                      {formatValue(ind.value, snapshotData.unit, snapshotData.unit_mult)}
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
              <div className="flex justify-between relative px-2">
                {availableYears.map((year, idx) => {
                  const isSelected = year === (selectedYear || snapshotData?.year?.toString());
                  const labelInterval = availableYears.length <= 10 ? 1 : availableYears.length <= 20 ? 2 : 5;
                  const showLabel = idx === 0 || idx === availableYears.length - 1 || idx % labelInterval === 0;

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
      ) : isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : null}
    </SectionCard>
  );
}

// ============================================================================
// DATA EXPLORER COMPONENT
// ============================================================================

interface DataExplorerProps {
  tables: GDPByIndustryTable[];
  industries: GDPByIndustryIndustry[];
}

function DataExplorer({ tables, industries }: DataExplorerProps) {
  const [selectedTableId, setSelectedTableId] = useState<number>(1);
  const [frequency, setFrequency] = useState<'A' | 'Q'>('A');
  const [selectedIndustries, setSelectedIndustries] = useState<GDPByIndustryIndustry[]>([]);
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [periodYears, setPeriodYears] = useState(10);

  const industryQueries = useQueries({
    queries: selectedIndustries.map(ind => ({
      queryKey: ['gdpbyindustry-explorer-data', selectedTableId, ind.industry_code, frequency],
      queryFn: async () => {
        const response = await beaResearchAPI.getGDPByIndustryData<GDPByIndustryTimeSeries>(
          selectedTableId,
          ind.industry_code,
          frequency
        );
        return response.data;
      },
      enabled: !!selectedTableId && selectedIndustries.length > 0,
      staleTime: 5 * 60 * 1000,
    })),
  });

  const availablePeriods = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    industryQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: GDPByIndustryTimeSeriesData) => {
          const yearMatch = d.time_period.match(/^(\d{4})/);
          if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      }
    });
    return Array.from(allPeriods).sort();
  }, [industryQueries, periodYears]);

  const chartData = useMemo(() => {
    if (selectedIndustries.length === 0) return [];

    return availablePeriods.map(period => {
      const point: Record<string, unknown> = { period };
      selectedIndustries.forEach((ind, idx) => {
        const data = industryQueries[idx]?.data;
        const seriesData = data?.data || [];
        const entry = seriesData.find((d: GDPByIndustryTimeSeriesData) => d.time_period === period);
        point[ind.industry_code] = entry?.value ?? null;
      });
      return point;
    });
  }, [industryQueries, selectedIndustries, availablePeriods]);

  const toggleIndustry = (industry: GDPByIndustryIndustry) => {
    if (selectedIndustries.find(i => i.industry_code === industry.industry_code)) {
      setSelectedIndustries(selectedIndustries.filter(i => i.industry_code !== industry.industry_code));
    } else if (selectedIndustries.length < 8) {
      setSelectedIndustries([...selectedIndustries, industry]);
    }
  };

  const primaryData = industryQueries[0]?.data;
  const isLoading = industryQueries.some(q => q.isLoading);

  return (
    <SectionCard
      title="Data Explorer"
      description="Explore GDP by Industry data in detail"
      color="gray"
      icon={Search}
      rightContent={
        <div className="flex gap-2 items-center">
          <PeriodSelector value={periodYears} onChange={setPeriodYears} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Selectors */}
      <div className="flex flex-wrap gap-4 mb-4">
        <select
          value={selectedTableId}
          onChange={(e) => {
            setSelectedTableId(Number(e.target.value));
            setSelectedIndustries([]);
          }}
          className="min-w-[300px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {tables.map(t => (
            <option key={t.table_id} value={t.table_id}>
              Table {t.table_id}: {t.table_description?.substring(0, 50)}
            </option>
          ))}
        </select>

        <div className="flex rounded-lg overflow-hidden border border-gray-300">
          {(['A', 'Q'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFrequency(f)}
              className={`px-4 py-2 text-sm font-medium ${frequency === f ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              {f === 'A' ? 'Annual' : 'Quarterly'}
            </button>
          ))}
        </div>

        <select
          value=""
          onChange={(e) => {
            const ind = industries.find(i => i.industry_code === e.target.value);
            if (ind) toggleIndustry(ind);
          }}
          disabled={selectedIndustries.length >= 8}
          className="flex-1 min-w-[250px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        >
          <option value="">{selectedIndustries.length >= 8 ? 'Max 8 industries' : 'Add Industry...'}</option>
          {industries
            .filter(i => !selectedIndustries.find(s => s.industry_code === i.industry_code))
            .filter(i => !AGGREGATE_INDUSTRY_CODES.includes(i.industry_code))
            .map(i => (
              <option key={i.industry_code} value={i.industry_code}>
                {i.industry_code}: {i.industry_description?.substring(0, 50)}
              </option>
            ))}
        </select>
      </div>

      {/* Selected Industries */}
      {selectedIndustries.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {selectedIndustries.map((ind, idx) => (
            <span
              key={ind.industry_code}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs"
              style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
            >
              {ind.industry_description?.substring(0, 20)}...
              <button onClick={() => toggleIndustry(ind)} className="hover:bg-white/20 rounded-full p-0.5">×</button>
            </span>
          ))}
        </div>
      )}

      {/* Chart or Table */}
      {selectedIndustries.length === 0 ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select industries above to view data.</div>
      ) : isLoading ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
      ) : chartData.length === 0 ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available for selected industries</div>
      ) : viewMode === 'chart' ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
              <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis
                tick={{ fontSize: 10 }}
                width={80}
                tickFormatter={(v) => formatValue(v, primaryData?.unit, primaryData?.unit_mult)}
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  const ind = selectedIndustries.find(i => i.industry_code === name);
                  return [formatValue(value, primaryData?.unit, primaryData?.unit_mult), ind?.industry_description?.substring(0, 30) || name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => selectedIndustries.find(i => i.industry_code === v)?.industry_description?.substring(0, 20) || v} />
              {selectedIndustries.map((ind, idx) => (
                <Line
                  key={ind.industry_code}
                  type="monotone"
                  dataKey={ind.industry_code}
                  name={ind.industry_code}
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
        <div className="overflow-auto max-h-96">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100">
              <tr>
                <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-10">Period</th>
                {selectedIndustries.map((ind, idx) => (
                  <th key={ind.industry_code} className="text-right p-2 font-semibold whitespace-nowrap">
                    <div className="flex items-center justify-end gap-1">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                      {ind.industry_description?.substring(0, 15)}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {chartData.slice().reverse().map((row, rowIdx) => {
                const typedRow = row as Record<string, unknown>;
                return (
                  <tr key={typedRow.period as string} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className={`p-2 font-medium sticky left-0 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                      {typedRow.period as string}
                    </td>
                    {selectedIndustries.map((ind) => (
                      <td key={ind.industry_code} className="text-right p-2 font-mono text-sm">
                        {formatValue(typedRow[ind.industry_code] as number | null, primaryData?.unit, primaryData?.unit_mult)}
                      </td>
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
// MAIN COMPONENT
// ============================================================================

export default function GDPbyIndustryExplorer() {
  const { data: tables, isLoading: tablesLoading } = useQuery({
    queryKey: ['gdpbyindustry-tables'],
    queryFn: async () => {
      const response = await beaResearchAPI.getGDPByIndustryTables<GDPByIndustryTable[]>();
      return response.data;
    },
  });

  const { data: industries, isLoading: industriesLoading } = useQuery({
    queryKey: ['gdpbyindustry-industries'],
    queryFn: async () => {
      const response = await beaResearchAPI.getGDPByIndustryIndustries<GDPByIndustryIndustry[]>();
      return response.data;
    },
  });

  const { data: snapshotData, isLoading: snapshotLoading } = useQuery({
    queryKey: ['gdpbyindustry-snapshot', 1, 'A'],
    queryFn: async () => {
      const response = await beaResearchAPI.getGDPByIndustrySnapshot<GDPByIndustrySnapshot>(1, 'A');
      return response.data;
    },
  });

  const headlineQueries = useQueries({
    queries: HEADLINE_INDUSTRIES.map(ind => ({
      queryKey: ['gdpbyindustry-headline', ind.code],
      queryFn: async () => {
        try {
          const response = await beaResearchAPI.getGDPByIndustryData<GDPByIndustryTimeSeries>(1, ind.code, 'A');
          return response.data;
        } catch {
          return null;
        }
      },
      staleTime: 5 * 60 * 1000,
    })),
  });

  const treemapData = useMemo(() => {
    if (!snapshotData?.data) return [];
    return snapshotData.data
      .filter(d =>
        d.value > 0 &&
        !AGGREGATE_INDUSTRY_CODES.includes(d.industry_code) &&
        !d.industry_description?.toLowerCase().includes('gross domestic product') &&
        !d.industry_description?.toLowerCase().includes('private industries') &&
        !d.industry_description?.toLowerCase().includes('all industries')
      )
      .map(d => ({
        name: d.industry_description?.substring(0, 20) || d.industry_code,
        value: d.value,
        code: d.industry_code,
      }))
      .sort((a, b) => b.value - a.value);
  }, [snapshotData]);

  const { maxValue, minValue } = useMemo(() => {
    if (treemapData.length === 0) return { maxValue: 1, minValue: 0 };
    return {
      maxValue: Math.max(...treemapData.map(d => d.value)),
      minValue: Math.min(...treemapData.map(d => d.value)),
    };
  }, [treemapData]);

  if (tablesLoading || industriesLoading) {
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
          <h1 className="text-2xl font-bold">GDP by Industry Explorer</h1>
          <p className="text-sm text-gray-500">Industry-level GDP, Value Added, and Output Data</p>
        </div>
      </div>

      <hr className="my-6 border-gray-200" />

      {/* Industry Snapshot */}
      <SectionCard title="Industry Snapshot" description="GDP Contributions by Industry" color="blue" icon={BarChart3} collapsible={false}>
        {/* Headline Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
          {HEADLINE_INDUSTRIES.map((ind, idx) => {
            const q = headlineQueries[idx];
            const data = q.data;
            const latestValue = data?.data?.[data.data.length - 1]?.value ?? null;
            const prevValue = data?.data?.[data.data.length - 2]?.value ?? null;
            const change = calcPctChange(latestValue, prevValue);
            const period = data?.data?.[data.data.length - 1]?.time_period;

            return (
              <MetricCard
                key={ind.code}
                title={ind.name}
                value={formatValue(latestValue, data?.unit, data?.unit_mult)}
                change={change}
                period={period}
                isLoading={q.isLoading}
              />
            );
          })}
        </div>

        {/* Treemap */}
        {snapshotLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : treemapData.length > 0 ? (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={treemapData}
                dataKey="value"
                aspectRatio={4 / 3}
                stroke="#fff"
                content={({ x, y, width, height, name, value }: { x: number; y: number; width: number; height: number; name: string; value: number }) => {
                  const bgColor = getTreemapColor(value, maxValue, minValue);
                  const canShowText = width > 35 && height > 20;
                  const canShowValue = width > 60 && height > 40;
                  const maxChars = Math.max(3, Math.floor(width / 7));

                  return (
                    <g>
                      <rect x={x} y={y} width={width} height={height} style={{ fill: bgColor, stroke: '#fff', strokeWidth: 2 }} />
                      {canShowText && (
                        <>
                          <text x={x + width / 2} y={y + height / 2 - (canShowValue ? 8 : 0)} textAnchor="middle" fill="#fff" fontSize={Math.min(14, Math.max(8, width / 8))} fontWeight="600">
                            {name?.length > maxChars ? name.substring(0, maxChars) + '...' : name}
                          </text>
                          {canShowValue && (
                            <text x={x + width / 2} y={y + height / 2 + 12} textAnchor="middle" fill="rgba(255,255,255,0.95)" fontSize={Math.min(11, Math.max(7, width / 10))}>
                              {formatValue(value, snapshotData?.unit, snapshotData?.unit_mult)}
                            </text>
                          )}
                        </>
                      )}
                    </g>
                  );
                }}
              />
            </ResponsiveContainer>
          </div>
        ) : null}
      </SectionCard>

      {/* Category Sections */}
      {Object.entries(INDUSTRY_CATEGORIES).map(([key, category]) => (
        <CategorySection key={key} categoryKey={key} category={category} industries={industries || []} />
      ))}

      {/* Top Industries Section */}
      <TopIndustriesSection />

      {/* Data Explorer */}
      <DataExplorer tables={tables || []} industries={industries || []} />
    </div>
  );
}
