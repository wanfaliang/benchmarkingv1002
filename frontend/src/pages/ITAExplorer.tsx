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
  Globe,
  Truck,
  Briefcase,
  DollarSign,
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
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { beaResearchAPI } from '../services/api';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';
import { Map as MapIcon } from 'lucide-react';

// ============================================================================
// CONSTANTS & TYPES
// ============================================================================

interface ITAIndicator {
  indicator_code: string;
  indicator_description: string;
  unit?: string | null;
  unit_mult?: number | null;
  is_active: boolean;
}

interface ITAArea {
  area_code: string;
  area_name: string;
  area_type?: string | null;
  is_active: boolean;
}

interface ITATimeSeriesData {
  time_period: string;
  value: number | null;
}

interface ITATimeSeries {
  indicator_code: string;
  indicator_description: string;
  area_code: string;
  area_name: string;
  frequency: string;
  unit?: string | null;
  unit_mult?: number | null;
  data: ITATimeSeriesData[];
}

interface ITAHeadlineMetric {
  indicator_code: string;
  indicator_description: string;
  value: number;
  time_period: string;
  unit?: string | null;
  unit_mult?: number | null;
}

interface ITAHeadline {
  data: ITAHeadlineMetric[];
  frequency: string;
}

// Snapshot interfaces reserved for future use

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

const HEADLINE_INDICATORS = [
  { code: 'BalGds', name: 'Goods Balance', description: 'Trade balance in goods' },
  { code: 'BalServ', name: 'Services Balance', description: 'Trade balance in services' },
  { code: 'BalGdsServ', name: 'Goods & Services', description: 'Combined trade balance' },
  { code: 'BalCurrAcct', name: 'Current Account', description: 'Current account balance' },
  { code: 'BalPrimInc', name: 'Primary Income', description: 'Primary income balance' },
  { code: 'BalSecInc', name: 'Secondary Income', description: 'Secondary income balance' },
];

interface CategoryConfig {
  name: string;
  description: string;
  icon: React.ElementType;
  color: ColorKey;
  headlines: { indicatorCode: string; name: string }[];
}

const TRADE_CATEGORIES: Record<string, CategoryConfig> = {
  goods: {
    name: 'Goods Trade',
    description: 'Trade in Physical Goods',
    icon: Truck,
    color: 'green',
    headlines: [
      { indicatorCode: 'ExpGds', name: 'Goods Exports' },
      { indicatorCode: 'ImpGds', name: 'Goods Imports' },
      { indicatorCode: 'BalGds', name: 'Goods Balance' },
    ],
  },
  services: {
    name: 'Services Trade',
    description: 'Trade in Services',
    icon: Briefcase,
    color: 'purple',
    headlines: [
      { indicatorCode: 'ExpServ', name: 'Services Exports' },
      { indicatorCode: 'ImpServ', name: 'Services Imports' },
      { indicatorCode: 'BalServ', name: 'Services Balance' },
    ],
  },
  income: {
    name: 'Income Flows',
    description: 'Primary and Secondary Income',
    icon: DollarSign,
    color: 'orange',
    headlines: [
      { indicatorCode: 'BalPrimInc', name: 'Primary Income' },
      { indicatorCode: 'BalSecInc', name: 'Secondary Income' },
      { indicatorCode: 'BalCurrAcct', name: 'Current Account' },
    ],
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatValue = (value: number | null, _unit?: string | null, unitMult?: number | null): string => {
  if (value === null || value === undefined) return 'N/A';

  const multiplier = unitMult ? Math.pow(10, unitMult) : 1;
  const actualValue = value * multiplier;

  const isNegative = actualValue < 0;
  const absValue = Math.abs(actualValue);

  let formatted: string;
  if (absValue >= 1e12) formatted = `$${(absValue / 1e12).toFixed(2)}T`;
  else if (absValue >= 1e9) formatted = `$${(absValue / 1e9).toFixed(2)}B`;
  else if (absValue >= 1e6) formatted = `$${(absValue / 1e6).toFixed(1)}M`;
  else if (absValue >= 1e3) formatted = `$${(absValue / 1e3).toFixed(1)}K`;
  else formatted = `$${absValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

  return isNegative ? `-${formatted}` : formatted;
};

const calcPctChange = (current: number | null, previous: number | null): number | null => {
  if (current === null || previous === null || previous === 0) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
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
  period?: string;
  isLoading?: boolean;
  isNegative?: boolean;
}

function MetricCard({ title, value, change, period, isLoading, isNegative }: MetricCardProps) {
  const changeColor = change && change > 0.1 ? 'text-emerald-500' : change && change < -0.1 ? 'text-red-500' : 'text-gray-500';
  const valueColor = isNegative ? 'text-red-600' : '';

  return (
    <div className="p-3 rounded-lg border border-gray-200 bg-white">
      <p className="text-xs text-gray-500 font-medium truncate">{title}</p>
      {isLoading ? (
        <div className="flex justify-center py-2"><Loader2 className="w-4 h-4 animate-spin text-gray-400" /></div>
      ) : (
        <>
          <div className="flex items-baseline gap-1 mt-1">
            <span className={`text-xl font-bold ${valueColor}`}>{value}</span>
            {period && <span className="text-[10px] text-gray-400">{period}</span>}
          </div>
          {change !== null && change !== undefined && (
            <div className="flex items-center gap-0.5 mt-1">
              {change > 0.1 ? <TrendingUp className="w-3 h-3 text-emerald-500" /> :
               change < -0.1 ? <TrendingDown className="w-3 h-3 text-red-500" /> :
               <Minus className="w-3 h-3 text-gray-500" />}
              <span className={`text-[11px] font-medium ${changeColor}`}>
                {change > 0 ? '+' : ''}{change.toFixed(1)}%
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
// CATEGORY SECTION COMPONENT
// ============================================================================

interface CategorySectionProps {
  categoryKey: string;
  category: CategoryConfig;
}

function CategorySection({ categoryKey, category }: CategorySectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [periodYears, setPeriodYears] = useState(10);

  const colorSet = SECTION_COLORS[category.color];
  const frequency = 'A'; // Annual data

  const headlineQueries = useQueries({
    queries: category.headlines.map(h => ({
      queryKey: ['ita-category', categoryKey, h.indicatorCode, frequency],
      queryFn: async () => {
        try {
          const response = await beaResearchAPI.getITAData<ITATimeSeries>(
            h.indicatorCode,
            'AllCountries',
            frequency
          );
          return response.data;
        } catch {
          return null;
        }
      },
      staleTime: 5 * 60 * 1000,
    })),
  });

  const availablePeriods = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    headlineQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: ITATimeSeriesData) => {
          const yearMatch = d.time_period.match(/^(\d{4})/);
          if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      }
    });
    return Array.from(allPeriods).sort();
  }, [headlineQueries, periodYears]);

  const chartData = useMemo(() => {
    if (headlineQueries.some(q => q.isLoading)) return [];

    return availablePeriods.map(period => {
      const point: Record<string, unknown> = { period };
      category.headlines.forEach((h, idx) => {
        const data = headlineQueries[idx]?.data;
        const seriesData = data?.data || [];
        const entry = seriesData.find((d: ITATimeSeriesData) => d.time_period === period);
        point[h.indicatorCode] = entry?.value ?? null;
      });
      return point;
    });
  }, [headlineQueries, availablePeriods, category.headlines]);

  const isLoading = headlineQueries.some(q => q.isLoading);
  const primaryData = headlineQueries[0]?.data;

  return (
    <SectionCard
      title={category.name}
      description={category.description}
      color={category.color}
      icon={category.icon}
      rightContent={
        <div className="flex gap-2 items-center">
          <PeriodSelector value={periodYears} onChange={setPeriodYears} color={colorSet.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Headline Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {headlineQueries.map((q, idx) => {
          const headline = category.headlines[idx];
          const data = q.data;
          const latestValue = data?.data?.[data.data.length - 1]?.value ?? null;
          const prevValue = data?.data?.[data.data.length - 2]?.value ?? null;
          const change = calcPctChange(latestValue, prevValue);
          const period = data?.data?.[data.data.length - 1]?.time_period;

          return (
            <MetricCard
              key={headline.indicatorCode}
              title={headline.name}
              value={formatValue(latestValue, data?.unit, data?.unit_mult)}
              change={change}
              period={period}
              isLoading={q.isLoading}
              isNegative={latestValue !== null && latestValue < 0}
            />
          );
        })}
      </div>

      {/* Chart View */}
      {viewMode === 'chart' && (
        isLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : chartData.length === 0 ? (
          <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Loading data...</div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
                <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                <YAxis
                  tick={{ fontSize: 10 }}
                  width={80}
                  tickFormatter={(v) => formatValue(v, primaryData?.unit, primaryData?.unit_mult)}
                />
                <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                  formatter={(value: number, name: string) => {
                    const ind = category.headlines.find(h => h.indicatorCode === name);
                    return [formatValue(value, primaryData?.unit, primaryData?.unit_mult), ind?.name || name];
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} formatter={(v) => category.headlines.find(h => h.indicatorCode === v)?.name || v} />
                {category.headlines.map((h, idx) => (
                  <Line
                    key={h.indicatorCode}
                    type="monotone"
                    dataKey={h.indicatorCode}
                    name={h.indicatorCode}
                    stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                  />
                ))}
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )
      )}

      {/* Table View */}
      {viewMode === 'table' && (
        isLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : (
          <div className="overflow-auto max-h-96">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-100">
                <tr>
                  <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-10">Period</th>
                  {category.headlines.map((h, idx) => (
                    <th key={h.indicatorCode} className="text-right p-2 font-semibold">
                      <div className="flex items-center justify-end gap-1">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                        {h.name}
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
                      {category.headlines.map((h) => {
                        const val = typedRow[h.indicatorCode] as number | null;
                        return (
                          <td key={h.indicatorCode} className={`text-right p-2 font-mono text-sm ${val !== null && val < 0 ? 'text-red-600' : ''}`}>
                            {formatValue(val, primaryData?.unit, primaryData?.unit_mult)}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )
      )}
    </SectionCard>
  );
}

// ============================================================================
// DATA EXPLORER COMPONENT
// ============================================================================

interface DataExplorerProps {
  indicators: ITAIndicator[];
  areas: ITAArea[];
}

function DataExplorer({ indicators, areas }: DataExplorerProps) {
  const [selectedIndicator, setSelectedIndicator] = useState<string>('');
  const [selectedAreas, setSelectedAreas] = useState<ITAArea[]>([]);
  const [frequency, setFrequency] = useState('A');
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [periodYears, setPeriodYears] = useState(10);

  const areaQueries = useQueries({
    queries: selectedAreas.map(area => ({
      queryKey: ['ita-explorer-data', selectedIndicator, area.area_code, frequency],
      queryFn: async () => {
        const response = await beaResearchAPI.getITAData<ITATimeSeries>(
          selectedIndicator,
          area.area_code,
          frequency
        );
        return response.data;
      },
      enabled: !!selectedIndicator && selectedAreas.length > 0,
      staleTime: 5 * 60 * 1000,
    })),
  });

  const availablePeriods = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    areaQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: ITATimeSeriesData) => {
          const yearMatch = d.time_period.match(/^(\d{4})/);
          if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      }
    });
    return Array.from(allPeriods).sort();
  }, [areaQueries, periodYears]);

  const chartData = useMemo(() => {
    if (selectedAreas.length === 0) return [];

    return availablePeriods.map(period => {
      const point: Record<string, unknown> = { period };
      selectedAreas.forEach((area, idx) => {
        const data = areaQueries[idx]?.data;
        const seriesData = data?.data || [];
        const entry = seriesData.find((d: ITATimeSeriesData) => d.time_period === period);
        point[area.area_code] = entry?.value ?? null;
      });
      return point;
    });
  }, [areaQueries, selectedAreas, availablePeriods]);

  const toggleArea = (area: ITAArea) => {
    if (selectedAreas.find(a => a.area_code === area.area_code)) {
      setSelectedAreas(selectedAreas.filter(a => a.area_code !== area.area_code));
    } else if (selectedAreas.length < 8) {
      setSelectedAreas([...selectedAreas, area]);
    }
  };

  const primaryData = areaQueries[0]?.data;
  const isLoading = areaQueries.some(q => q.isLoading);

  return (
    <SectionCard
      title="Data Explorer"
      description="Explore International Trade and Investment data by country/area"
      color="gray"
      icon={Search}
      rightContent={
        <div className="flex gap-2 items-center">
          <div className="flex rounded-lg overflow-hidden border border-gray-300">
            {(['A', 'Q'] as const).map(f => (
              <button
                key={f}
                onClick={() => setFrequency(f)}
                className={`px-2 py-1 text-xs font-medium ${frequency === f ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                {f === 'A' ? 'Annual' : 'Quarterly'}
              </button>
            ))}
          </div>
          <PeriodSelector value={periodYears} onChange={setPeriodYears} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Selectors */}
      <div className="flex flex-wrap gap-4 mb-4">
        <select
          value={selectedIndicator}
          onChange={(e) => {
            setSelectedIndicator(e.target.value);
            setSelectedAreas([]);
          }}
          className="min-w-[350px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select Indicator...</option>
          {indicators.map(i => (
            <option key={i.indicator_code} value={i.indicator_code}>
              {i.indicator_code}: {i.indicator_description?.substring(0, 60)}
            </option>
          ))}
        </select>

        <select
          value=""
          onChange={(e) => {
            const area = areas.find(a => a.area_code === e.target.value);
            if (area) toggleArea(area);
          }}
          disabled={!selectedIndicator || selectedAreas.length >= 8}
          className="flex-1 min-w-[250px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        >
          <option value="">{selectedAreas.length >= 8 ? 'Max 8 areas' : 'Add Country/Area...'}</option>
          {areas
            .filter(a => !selectedAreas.find(s => s.area_code === a.area_code))
            .map(a => (
              <option key={a.area_code} value={a.area_code}>
                {a.area_name}
              </option>
            ))}
        </select>
      </div>

      {/* Selected Areas */}
      {selectedAreas.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {selectedAreas.map((area, idx) => (
            <span
              key={area.area_code}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs"
              style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
            >
              {area.area_name.substring(0, 20)}
              <button onClick={() => toggleArea(area)} className="hover:bg-white/20 rounded-full p-0.5">×</button>
            </span>
          ))}
        </div>
      )}

      {/* Chart or Table */}
      {selectedAreas.length === 0 || !selectedIndicator ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select an indicator and add countries/areas to view data.</div>
      ) : isLoading ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
      ) : chartData.length === 0 ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available for selected areas</div>
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
              <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  const area = selectedAreas.find(a => a.area_code === name);
                  return [formatValue(value, primaryData?.unit, primaryData?.unit_mult), area?.area_name || name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => selectedAreas.find(a => a.area_code === v)?.area_name?.substring(0, 20) || v} />
              {selectedAreas.map((area, idx) => (
                <Line
                  key={area.area_code}
                  type="monotone"
                  dataKey={area.area_code}
                  name={area.area_code}
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
                {selectedAreas.map((area, idx) => (
                  <th key={area.area_code} className="text-right p-2 font-semibold whitespace-nowrap">
                    <div className="flex items-center justify-end gap-1">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                      {area.area_name.substring(0, 15)}
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
                    {selectedAreas.map((area) => {
                      const val = typedRow[area.area_code] as number | null;
                      return (
                        <td key={area.area_code} className={`text-right p-2 font-mono text-sm ${val !== null && val < 0 ? 'text-red-600' : ''}`}>
                          {formatValue(val, primaryData?.unit, primaryData?.unit_mult)}
                        </td>
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
// TRADE BALANCE HISTORY SECTION (Time Series with YoY%)
// ============================================================================

function TradeBalanceHistorySection({ frequency }: { frequency: string }) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('table');
  const [periodYears, setPeriodYears] = useState(10);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('value');

  const colorSet = SECTION_COLORS.blue;

  // Fetch time series data for ALL headline indicators
  const indicatorQueries = useQueries({
    queries: HEADLINE_INDICATORS.map(ind => ({
      queryKey: ['ita-balance-history', ind.code, frequency],
      queryFn: async () => {
        try {
          const response = await beaResearchAPI.getITAData<ITATimeSeries>(
            ind.code,
            'AllCountries',
            frequency === 'A' ? 'A' : 'QSA'
          );
          return response.data;
        } catch {
          return null;
        }
      },
      staleTime: 5 * 60 * 1000,
    })),
  });

  // Prepare chart data from ALL indicators
  const chartData = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    indicatorQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: ITATimeSeriesData) => {
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
      HEADLINE_INDICATORS.forEach((ind, idx) => {
        const data = indicatorQueries[idx]?.data;
        const seriesData = data?.data || [];
        const currentIdx = seriesData.findIndex((d: ITATimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        let pctChange: number | null = null;
        if (current?.value !== null && current?.value !== undefined && prev?.value !== null && prev?.value !== undefined) {
          pctChange = calcPctChange(current.value, prev.value);
        }

        point[`${ind.code}_value`] = current?.value ?? null;
        point[`${ind.code}_pct`] = pctChange;
      });
      return point;
    });
  }, [indicatorQueries, periodYears]);

  const primaryData = indicatorQueries[0]?.data;
  const isLoading = indicatorQueries.some(q => q.isLoading);
  const loadedCount = indicatorQueries.filter(q => !q.isLoading).length;

  return (
    <SectionCard
      title="Trade Balance History"
      description={`Time series for all ${HEADLINE_INDICATORS.length} balance indicators`}
      color="blue"
      icon={BarChart3}
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
          <span className="text-xs text-gray-500">Loading {loadedCount}/{HEADLINE_INDICATORS.length} indicators...</span>
        </div>
      )}

      {/* Time Series Chart or Table */}
      {chartData.length === 0 && !isLoading ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available</div>
      ) : viewMode === 'chart' ? (
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
              {chartMetric === 'value' && <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />}
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  const code = name.split('_')[0];
                  const idx = HEADLINE_INDICATORS.findIndex(i => i.code === code);
                  const data = indicatorQueries[idx]?.data;
                  const isPct = name.endsWith('_pct');
                  if (isPct) {
                    return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}%`, `${HEADLINE_INDICATORS[idx]?.name || code} (YoY)`];
                  }
                  return [formatValue(value, data?.unit, data?.unit_mult), HEADLINE_INDICATORS[idx]?.name || code];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => {
                const code = v.split('_')[0];
                return HEADLINE_INDICATORS.find(i => i.code === code)?.name || code;
              }} />
              {HEADLINE_INDICATORS.map((ind, idx) => (
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
      ) : (
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-20">Period</th>
                {HEADLINE_INDICATORS.map((ind, idx) => (
                  <React.Fragment key={ind.code}>
                    <th className="text-right p-2 font-semibold whitespace-nowrap text-xs">
                      <div className="flex items-center justify-end gap-1">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                        {ind.name}
                      </div>
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
                    {HEADLINE_INDICATORS.map((ind, idx) => {
                      const data = indicatorQueries[idx]?.data;
                      const pctChange = typedRow[`${ind.code}_pct`] as number | null;
                      return (
                        <React.Fragment key={ind.code}>
                          <td className="text-right p-2 font-mono text-xs">
                            {formatValue(typedRow[`${ind.code}_value`] as number | null, data?.unit, data?.unit_mult)}
                          </td>
                          <td className="text-right p-2 text-xs">
                            {pctChange !== null && pctChange !== undefined ? (
                              <span className={`font-medium font-mono ${pctChange > 0.1 ? 'text-emerald-600' : pctChange < -0.1 ? 'text-red-600' : 'text-gray-500'}`}>
                                {pctChange >= 0 ? '+' : ''}{pctChange.toFixed(2)}%
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
// TOP COUNTRIES SECTION (with Timeline)
// ============================================================================

interface ITASnapshotItem {
  area_code: string;
  area_name: string;
  value: number;
}

interface ITASnapshot {
  indicator_code: string;
  indicator_description: string;
  frequency: string;
  time_period?: string;
  unit?: string | null;
  unit_mult?: number | null;
  data: ITASnapshotItem[];
}

// ============================================================================
// TOP TRADING PARTNERS SECTION (Bar Chart with all countries)
// ============================================================================

function TopTradingPartnersSection() {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [selectedIndicator, setSelectedIndicator] = useState('BalGdsServ');

  // Fetch snapshot data
  const { data: snapshotData, isLoading } = useQuery({
    queryKey: ['ita-trading-partners', selectedIndicator],
    queryFn: async () => {
      const response = await beaResearchAPI.getITASnapshot<ITASnapshot>(selectedIndicator, 'A');
      return response.data;
    },
  });

  // Prepare bar chart data
  const barData = useMemo(() => {
    if (!snapshotData?.data) return [];
    return snapshotData.data
      .filter((d: ITASnapshotItem) =>
        d.area_code !== 'AllCountries' &&
        d.area_code !== 'World' &&
        d.value !== null
      )
      .sort((a, b) => b.value - a.value)
      .slice(0, 25) // Show top 25 countries
      .map((d: ITASnapshotItem) => ({
        code: d.area_code,
        name: d.area_name?.substring(0, 15) || d.area_code,
        fullName: d.area_name || d.area_code,
        value: d.value,
      }));
  }, [snapshotData]);

  const getBarColor = (value: number) => value >= 0 ? '#10b981' : '#ef4444';

  return (
    <SectionCard
      title="Top Trading Partners"
      description={`Trade Balance by Country - ${snapshotData?.time_period || 'Latest'}`}
      color="cyan"
      icon={Globe}
      rightContent={
        <div className="flex gap-2 items-center">
          <select
            value={selectedIndicator}
            onChange={(e) => setSelectedIndicator(e.target.value)}
            className="px-2 py-1 text-xs border border-gray-300 rounded-lg"
          >
            {HEADLINE_INDICATORS.map(ind => (
              <option key={ind.code} value={ind.code}>{ind.name}</option>
            ))}
          </select>
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : barData.length === 0 ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available</div>
      ) : viewMode === 'chart' ? (
        <>
          <div className="h-[450px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} layout="vertical" margin={{ top: 10, right: 30, left: 100, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(v) => formatValue(v, snapshotData?.unit, snapshotData?.unit_mult)}
                />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={95} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                  formatter={(value: number) => [
                    formatValue(value, snapshotData?.unit, snapshotData?.unit_mult),
                    'Balance'
                  ]}
                  labelFormatter={(_, payload) => payload[0]?.payload?.fullName || ''}
                />
                <Bar dataKey="value" name="Balance">
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getBarColor(entry.value || 0)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-8 mt-2">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-emerald-500 rounded" />
              <span className="text-xs text-gray-600">Surplus</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded" />
              <span className="text-xs text-gray-600">Deficit</span>
            </div>
          </div>
        </>
      ) : (
        <div className="overflow-auto max-h-[450px]">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-100">
              <tr>
                <th className="text-left p-2 font-semibold">Country/Region</th>
                <th className="text-right p-2 font-semibold">Balance</th>
                <th className="text-center p-2 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {barData.map((row, idx) => (
                <tr key={row.code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="p-2">{row.fullName}</td>
                  <td className="text-right p-2 font-mono">
                    {formatValue(row.value, snapshotData?.unit, snapshotData?.unit_mult)}
                  </td>
                  <td className="text-center p-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      row.value && row.value >= 0
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {row.value && row.value >= 0 ? 'Surplus' : 'Deficit'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// TOP COUNTRIES SECTION (Top 5 Surplus/Deficit with Timeline)
// ============================================================================

function TopCountriesSection() {
  const [periodYears, setPeriodYears] = useState(20);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const [selectedIndicator, setSelectedIndicator] = useState('BalGdsServ');

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
    queryKey: ['ita-top-countries', selectedIndicator, selectedYear],
    queryFn: async () => {
      const response = await beaResearchAPI.getITASnapshot<ITASnapshot>(
        selectedIndicator,
        'A',
        selectedYear ? parseInt(selectedYear) : undefined
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Set default selected year to latest when data loads
  useEffect(() => {
    if (!selectedYear && snapshotData?.time_period) {
      setSelectedYear(snapshotData.time_period);
    }
  }, [snapshotData, selectedYear]);

  // Reset year when period changes
  useEffect(() => {
    setSelectedYear(null);
  }, [periodYears]);

  // Calculate top surplus and deficit countries
  const { surplusCountries, deficitCountries } = useMemo(() => {
    if (!snapshotData?.data) return { surplusCountries: [], deficitCountries: [] };
    const filtered = snapshotData.data.filter((d: ITASnapshotItem) =>
      d.area_code !== 'AllCountries' &&
      d.area_code !== 'World' &&
      d.value !== null
    );
    const sorted = [...filtered].sort((a, b) => b.value - a.value);
    return {
      surplusCountries: sorted.filter(d => d.value >= 0).slice(0, 5),
      deficitCountries: sorted.filter(d => d.value < 0).slice(-5).reverse(),
    };
  }, [snapshotData]);

  const availableYears = years.filter(y => parseInt(y) <= currentYear);

  return (
    <SectionCard
      title="Top Countries"
      description="Countries with Largest Trade Surplus and Deficit"
      color="red"
      icon={Zap}
      rightContent={
        <div className="flex gap-2 items-center">
          <select
            value={selectedIndicator}
            onChange={(e) => setSelectedIndicator(e.target.value)}
            className="px-2 py-1 text-xs border border-gray-300 rounded-lg"
          >
            {HEADLINE_INDICATORS.map(ind => (
              <option key={ind.code} value={ind.code}>{ind.name}</option>
            ))}
          </select>
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
            {/* Surplus Countries */}
            <div>
              <h4 className="text-sm font-bold text-emerald-600 mb-2 flex items-center gap-1">
                <TrendingUp className="w-4 h-4" />
                Top 5 Surplus ({selectedYear || snapshotData.time_period})
              </h4>
              <table className="w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="text-left p-2 font-semibold w-10">#</th>
                    <th className="text-left p-2 font-semibold">Country</th>
                    <th className="text-right p-2 font-semibold">Balance</th>
                  </tr>
                </thead>
                <tbody>
                  {surplusCountries.length > 0 ? surplusCountries.map((item, idx) => (
                    <tr key={item.area_code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="p-2">{idx + 1}</td>
                      <td className="p-2">{item.area_name?.substring(0, 25)}</td>
                      <td className="p-2 text-right font-mono text-emerald-600">
                        {formatValue(item.value, snapshotData.unit, snapshotData.unit_mult)}
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan={3} className="p-4 text-center text-gray-500">No surplus countries</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Deficit Countries */}
            <div>
              <h4 className="text-sm font-bold text-red-600 mb-2 flex items-center gap-1">
                <TrendingDown className="w-4 h-4" />
                Top 5 Deficit ({selectedYear || snapshotData.time_period})
              </h4>
              <table className="w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="text-left p-2 font-semibold w-10">#</th>
                    <th className="text-left p-2 font-semibold">Country</th>
                    <th className="text-right p-2 font-semibold">Balance</th>
                  </tr>
                </thead>
                <tbody>
                  {deficitCountries.length > 0 ? deficitCountries.map((item, idx) => (
                    <tr key={item.area_code} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="p-2">{idx + 1}</td>
                      <td className="p-2">{item.area_name?.substring(0, 25)}</td>
                      <td className="p-2 text-right font-mono text-red-600">
                        {formatValue(item.value, snapshotData.unit, snapshotData.unit_mult)}
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan={3} className="p-4 text-center text-gray-500">No deficit countries</td>
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
                  const isSelected = year === (selectedYear || snapshotData.time_period);
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
// TRADING PARTNERS HISTORY SECTION
// ============================================================================

interface TradingPartnersHistorySectionProps {
  areas: ITAArea[];
}

function TradingPartnersHistorySection({ areas }: TradingPartnersHistorySectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('table');
  const [periodYears, setPeriodYears] = useState(10);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('value');
  const [indicatorCode, setIndicatorCode] = useState('BalGdsServ');

  // Default top trading partners
  const defaultPartners = [
    { code: 'China', name: 'China' },
    { code: 'Canada', name: 'Canada' },
    { code: 'Mexico', name: 'Mexico' },
    { code: 'Japan', name: 'Japan' },
    { code: 'Germany', name: 'Germany' },
    { code: 'UnitedKingdom', name: 'United Kingdom' },
  ];

  const [selectedAreas, setSelectedAreas] = useState<Array<{ code: string; name: string }>>(defaultPartners);

  const colorSet = SECTION_COLORS.cyan;

  // Filter available areas
  const availableAreas = useMemo(() => {
    return areas.filter(a =>
      a.area_code !== 'AllCountries' &&
      !a.area_name?.toLowerCase().includes('total') &&
      !a.area_name?.toLowerCase().includes('all countries')
    );
  }, [areas]);

  // Fetch time series data for selected areas
  const areaQueries = useQueries({
    queries: selectedAreas.map(area => ({
      queryKey: ['ita-partners-history', indicatorCode, area.code],
      queryFn: async () => {
        try {
          const response = await beaResearchAPI.getITAData<ITATimeSeries>(
            indicatorCode,
            area.code,
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

  // Prepare chart data
  const chartData = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    areaQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: ITATimeSeriesData) => {
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
      selectedAreas.forEach((area, idx) => {
        const data = areaQueries[idx]?.data;
        const seriesData = data?.data || [];
        const currentIdx = seriesData.findIndex((d: ITATimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        let pctChange: number | null = null;
        if (current?.value !== null && current?.value !== undefined && prev?.value !== null && prev?.value !== undefined) {
          pctChange = calcPctChange(current.value, prev.value);
        }

        point[`${area.code}_value`] = current?.value ?? null;
        point[`${area.code}_pct`] = pctChange;
      });
      return point;
    });
  }, [areaQueries, selectedAreas, periodYears]);

  const primaryData = areaQueries[0]?.data;
  const isLoading = areaQueries.some(q => q.isLoading);
  const loadedCount = areaQueries.filter(q => !q.isLoading).length;

  const handleRemoveArea = (code: string) => {
    setSelectedAreas(selectedAreas.filter(a => a.code !== code));
  };

  return (
    <SectionCard
      title="Trading Partners History"
      description={`Time series by country - ${selectedAreas.length} partners selected`}
      color="cyan"
      icon={LineChart}
      rightContent={
        <div className="flex gap-2 items-center">
          <select
            value={indicatorCode}
            onChange={(e) => setIndicatorCode(e.target.value)}
            className="px-2 py-1 text-xs border border-gray-300 rounded-lg"
          >
            {HEADLINE_INDICATORS.map(ind => (
              <option key={ind.code} value={ind.code}>{ind.name}</option>
            ))}
          </select>
          <ChartMetricToggle value={chartMetric} onChange={setChartMetric} color={colorSet.main} />
          <PeriodSelector value={periodYears} onChange={setPeriodYears} color={colorSet.main} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Country Selector */}
      <div className="flex flex-wrap gap-4 mb-4 items-center">
        <select
          value=""
          onChange={(e) => {
            const area = availableAreas.find(a => a.area_code === e.target.value);
            if (area && !selectedAreas.find(s => s.code === area.area_code) && selectedAreas.length < 8) {
              setSelectedAreas([...selectedAreas, { code: area.area_code, name: area.area_name || area.area_code }]);
            }
          }}
          disabled={selectedAreas.length >= 8}
          className="min-w-[300px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:bg-gray-100"
        >
          <option value="">{selectedAreas.length >= 8 ? 'Max 8 countries' : `Add Country (${selectedAreas.length}/8)`}</option>
          {availableAreas
            .filter(a => !selectedAreas.find(s => s.code === a.area_code))
            .map(a => (
              <option key={a.area_code} value={a.area_code}>
                {a.area_code} - {a.area_name}
              </option>
            ))}
        </select>
      </div>

      {/* Selected Countries Chips */}
      {selectedAreas.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {selectedAreas.map((area, idx) => (
            <span
              key={area.code}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs"
              style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
            >
              {area.name.substring(0, 15)}
              <button onClick={() => handleRemoveArea(area.code)} className="hover:bg-white/20 rounded-full p-0.5">×</button>
            </span>
          ))}
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex items-center gap-2 mb-3">
          <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
          <span className="text-xs text-gray-500">Loading {loadedCount}/{selectedAreas.length} countries...</span>
        </div>
      )}

      {/* Chart or Table */}
      {chartData.length === 0 && !isLoading ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available</div>
      ) : viewMode === 'chart' ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
              <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis
                tick={{ fontSize: 10 }}
                width={80}
                tickFormatter={(v) => chartMetric === 'pct' ? `${v?.toFixed(1)}%` : formatValue(v, primaryData?.unit, primaryData?.unit_mult)}
              />
              {chartMetric === 'value' && <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />}
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  const code = name.split('_')[0];
                  const area = selectedAreas.find(a => a.code === code);
                  const isPct = name.endsWith('_pct');
                  if (isPct) {
                    return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}%`, `${area?.name || code} (YoY)`];
                  }
                  return [formatValue(value, primaryData?.unit, primaryData?.unit_mult), area?.name || code];
                }}
              />
              <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => {
                const code = v.split('_')[0];
                return selectedAreas.find(a => a.code === code)?.name || code;
              }} />
              {selectedAreas.map((area, idx) => (
                <Line
                  key={area.code}
                  type="monotone"
                  dataKey={chartMetric === 'pct' ? `${area.code}_pct` : `${area.code}_value`}
                  name={chartMetric === 'pct' ? `${area.code}_pct` : area.code}
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
                <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-20">Period</th>
                {selectedAreas.map((area, idx) => (
                  <React.Fragment key={area.code}>
                    <th className="text-right p-2 font-semibold whitespace-nowrap text-xs">
                      <div className="flex items-center justify-end gap-1">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                        {area.name.substring(0, 12)}
                      </div>
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
                    {selectedAreas.map((area) => {
                      const pctChange = typedRow[`${area.code}_pct`] as number | null;
                      return (
                        <React.Fragment key={area.code}>
                          <td className="text-right p-2 font-mono text-xs">
                            {formatValue(typedRow[`${area.code}_value`] as number | null, primaryData?.unit, primaryData?.unit_mult)}
                          </td>
                          <td className="text-right p-2 text-xs">
                            {pctChange !== null && pctChange !== undefined ? (
                              <span className={`font-medium font-mono ${pctChange > 0.1 ? 'text-emerald-600' : pctChange < -0.1 ? 'text-red-600' : 'text-gray-500'}`}>
                                {pctChange >= 0 ? '+' : ''}{pctChange.toFixed(1)}%
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
// WORLD MAP SECTION
// ============================================================================

// BEA area codes to world map country names mapping
const BEA_TO_WORLD_MAP: Record<string, string> = {
  'China': 'China',
  'Canada': 'Canada',
  'Mexico': 'Mexico',
  'Japan': 'Japan',
  'Germany': 'Germany',
  'UnitedKingdom': 'United Kingdom',
  'Korea': 'South Korea',
  'France': 'France',
  'India': 'India',
  'Italy': 'Italy',
  'Brazil': 'Brazil',
  'Netherlands': 'Netherlands',
  'Switzerland': 'Switzerland',
  'Taiwan': 'Taiwan',
  'Ireland': 'Ireland',
  'Singapore': 'Singapore',
  'Australia': 'Australia',
  'Vietnam': 'Vietnam',
  'Thailand': 'Thailand',
  'Malaysia': 'Malaysia',
  'Indonesia': 'Indonesia',
  'SaudiArabia': 'Saudi Arabia',
  'Belgium': 'Belgium',
  'Spain': 'Spain',
  'HongKong': 'Hong Kong',
  'Russia': 'Russia',
  'SouthAfrica': 'South Africa',
};

interface WorldMapSectionProps {
  indicators: ITAIndicator[];
}

function WorldMapSection({ indicators }: WorldMapSectionProps) {
  const [selectedIndicator, setSelectedIndicator] = useState('BalGdsServ');
  const [worldMapLoaded, setWorldMapLoaded] = useState(false);

  // Load world map GeoJSON
  useEffect(() => {
    if (!worldMapLoaded) {
      fetch('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json')
        .then(res => res.json())
        .then((geoJson) => {
          echarts.registerMap('World', geoJson as Parameters<typeof echarts.registerMap>[1]);
          setWorldMapLoaded(true);
        })
        .catch(err => console.error('Failed to load world map:', err));
    }
  }, [worldMapLoaded]);

  // Fetch snapshot data for selected indicator
  const { data: snapshotData, isLoading } = useQuery({
    queryKey: ['ita-world-map', selectedIndicator],
    queryFn: async () => {
      const response = await beaResearchAPI.getITASnapshot<ITASnapshot>(selectedIndicator, 'A');
      return response.data;
    },
    enabled: worldMapLoaded,
  });

  // Prepare map data
  const mapData = useMemo(() => {
    if (!snapshotData?.data) return [];
    return snapshotData.data
      .filter((d: ITASnapshotItem) => d.value !== null && d.area_code !== 'AllCountries')
      .map((d: ITASnapshotItem) => {
        const worldName = BEA_TO_WORLD_MAP[d.area_code] || d.area_name;
        return {
          name: worldName,
          value: d.value,
          areaCode: d.area_code,
          areaName: d.area_name,
        };
      });
  }, [snapshotData]);

  // Get min/max for color scale
  const { minValue, maxValue } = useMemo(() => {
    if (mapData.length === 0) return { minValue: 0, maxValue: 0 };
    const values = mapData.map(d => d.value).filter((v): v is number => v !== null);
    return {
      minValue: Math.min(...values),
      maxValue: Math.max(...values),
    };
  }, [mapData]);

  // ECharts options for world map
  const mapOptions = useMemo(() => {
    if (!worldMapLoaded) return {};

    const indicatorInfo = indicators.find(i => i.indicator_code === selectedIndicator);
    const isBalance = selectedIndicator.startsWith('Bal');

    return {
      backgroundColor: '#f8fafc',
      title: {
        text: indicatorInfo?.indicator_description || selectedIndicator,
        subtext: snapshotData?.time_period || '',
        left: 'center',
        textStyle: { color: '#334155', fontSize: 14, fontWeight: 'bold' },
        subtextStyle: { color: '#64748b', fontSize: 11 },
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: { name: string; data?: { value: number; areaName?: string } }) => {
          if (!params.data?.value) return `${params.name}: No data`;
          const formattedValue = formatValue(params.data.value, snapshotData?.unit, snapshotData?.unit_mult);
          const status = isBalance ? (params.data.value >= 0 ? ' (Surplus)' : ' (Deficit)') : '';
          return `<strong>${params.data.areaName || params.name}</strong><br/>${formattedValue}${status}`;
        },
      },
      visualMap: {
        min: minValue,
        max: maxValue,
        left: 'left',
        top: 'bottom',
        text: ['High', 'Low'],
        calculable: true,
        inRange: isBalance
          ? { color: ['#ef4444', '#fca5a5', '#fef2f2', '#dcfce7', '#86efac', '#22c55e'] }
          : { color: ['#dbeafe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8'] },
        textStyle: { color: '#64748b', fontSize: 10 },
        itemWidth: 12,
        itemHeight: 80,
      },
      series: [
        {
          name: indicatorInfo?.indicator_description || selectedIndicator,
          type: 'map',
          map: 'World',
          roam: true,
          zoom: 1.2,
          scaleLimit: { min: 0.5, max: 5 },
          emphasis: {
            label: { show: true, color: '#1e293b', fontWeight: 'bold', fontSize: 10 },
            itemStyle: { areaColor: '#fbbf24' },
          },
          itemStyle: {
            areaColor: '#e2e8f0',
            borderColor: '#94a3b8',
            borderWidth: 0.5,
          },
          label: { show: false },
          data: mapData,
        },
      ],
    };
  }, [worldMapLoaded, mapData, minValue, maxValue, selectedIndicator, indicators, snapshotData]);

  // Get indicator options for dropdown
  const indicatorOptions = useMemo(() => {
    const priorityIndicators = [
      'BalGdsServ', 'BalGds', 'BalServ', 'BalCurrAcct',
      'ExpGds', 'ImpGds', 'ExpServ', 'ImpServ',
    ];
    const priority = indicators.filter(i => priorityIndicators.includes(i.indicator_code));
    const others = indicators.filter(i => !priorityIndicators.includes(i.indicator_code));
    return [...priority, ...others];
  }, [indicators]);

  return (
    <SectionCard
      title="World Trade Map"
      description="Trade metrics by country on world map"
      color="teal"
      icon={MapIcon}
      rightContent={
        <div className="flex gap-2 items-center">
          <select
            value={selectedIndicator}
            onChange={(e) => setSelectedIndicator(e.target.value)}
            className="min-w-[200px] px-2 py-1 text-xs border border-gray-300 rounded-lg"
          >
            {indicatorOptions.map(ind => (
              <option key={ind.indicator_code} value={ind.indicator_code}>
                {ind.indicator_description?.substring(0, 40) || ind.indicator_code}
              </option>
            ))}
          </select>
        </div>
      }
    >
      {!worldMapLoaded ? (
        <div className="flex justify-center items-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
          <span className="ml-2 text-gray-500">Loading world map...</span>
        </div>
      ) : isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : mapData.length === 0 ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available for selected indicator</div>
      ) : (
        <div className="h-[500px]">
          <ReactECharts
            option={mapOptions}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'canvas' }}
          />
        </div>
      )}

      {/* Legend for balance indicators */}
      {selectedIndicator.startsWith('Bal') && worldMapLoaded && mapData.length > 0 && (
        <div className="flex justify-center gap-8 mt-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-emerald-500 rounded" />
            <span className="text-xs text-gray-600">Trade Surplus</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded" />
            <span className="text-xs text-gray-600">Trade Deficit</span>
          </div>
        </div>
      )}
    </SectionCard>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function ITAExplorer() {
  const [frequency, setFrequency] = useState('A');

  const { data: indicators, isLoading: indicatorsLoading } = useQuery({
    queryKey: ['ita-indicators'],
    queryFn: async () => {
      const response = await beaResearchAPI.getITAIndicators<ITAIndicator[]>();
      return response.data;
    },
  });

  const { data: areas, isLoading: areasLoading } = useQuery({
    queryKey: ['ita-areas'],
    queryFn: async () => {
      const response = await beaResearchAPI.getITAAreas<ITAArea[]>();
      return response.data;
    },
  });

  const { data: headlineData, isLoading: headlineLoading } = useQuery({
    queryKey: ['ita-headline', frequency],
    queryFn: async () => {
      const response = await beaResearchAPI.getITAHeadline<ITAHeadline>();
      return response.data;
    },
  });

  const getHeadlineMetric = (code: string): ITAHeadlineMetric | undefined => {
    return headlineData?.data?.find(m => m.indicator_code === code);
  };

  if (indicatorsLoading || areasLoading) {
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
          <h1 className="text-2xl font-bold">International Trade Explorer</h1>
          <p className="text-sm text-gray-500">International Trade and Investment - Balance of Payments</p>
        </div>
      </div>

      <hr className="my-6 border-gray-200" />

      {/* Trade Balance Overview */}
      <SectionCard title="Trade Balance Overview" description="U.S. International Trade Balances" color="blue" icon={Globe} collapsible={false}>
        <div className="flex gap-2 mb-4">
          {(['A', 'Q'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFrequency(f)}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg ${frequency === f ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            >
              {f === 'A' ? 'Annual' : 'Quarterly'}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {HEADLINE_INDICATORS.map(ind => {
            const metric = getHeadlineMetric(ind.code);
            const value = metric?.value ?? null;

            return (
              <MetricCard
                key={ind.code}
                title={ind.name}
                value={formatValue(value, metric?.unit, metric?.unit_mult)}
                period={metric?.time_period}
                isLoading={headlineLoading}
                isNegative={value !== null && value < 0}
              />
            );
          })}
        </div>
      </SectionCard>

      {/* Trade Balance History */}
      <TradeBalanceHistorySection frequency={frequency} />

      {/* Top Trading Partners (Bar Chart) */}
      <TopTradingPartnersSection />

      {/* Trading Partners History (Time Series by Country) */}
      <TradingPartnersHistorySection areas={areas || []} />

      {/* World Trade Map */}
      <WorldMapSection indicators={indicators || []} />

      {/* Category Sections */}
      {Object.entries(TRADE_CATEGORIES).map(([key, category]) => (
        <CategorySection key={key} categoryKey={key} category={category} />
      ))}

      {/* Top Countries (Top 5 Surplus/Deficit with Timeline) */}
      <TopCountriesSection />

      {/* Data Explorer */}
      <DataExplorer indicators={indicators || []} areas={areas || []} />
    </div>
  );
}
