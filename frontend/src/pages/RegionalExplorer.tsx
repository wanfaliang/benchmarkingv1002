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
  DollarSign,
  Trophy,
  Loader2,
  Map as MapIcon,
  LayoutGrid,
  Globe,
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
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts';
import { beaResearchAPI } from '../services/api';

// ============================================================================
// CONSTANTS & TYPES
// ============================================================================

interface RegionalTable {
  table_name: string;
  table_description: string;
  geo_scope?: string | null;
  first_year?: number | null;
  last_year?: number | null;
  line_codes_count: number;
  is_active: boolean;
}

interface RegionalLineCode {
  table_name: string;
  line_code: number;
  line_description: string;
  cl_unit?: string | null;
  unit_mult?: number | null;
}

interface RegionalGeo {
  geo_fips: string;
  geo_name: string;
  geo_type?: string | null;
  parent_fips?: string | null;
}

interface RegionalTimeSeriesData {
  time_period: string;
  value: number | null;
}

interface RegionalTimeSeries {
  table_name: string;
  line_code: number;
  line_description: string;
  geo_fips: string;
  geo_name: string;
  unit?: string | null;
  unit_mult?: number | null;
  data: RegionalTimeSeriesData[];
}

interface RegionalBatchTimeSeries {
  table_name: string;
  line_code: number;
  line_description: string;
  unit?: string | null;
  unit_mult?: number | null;
  series: Array<{
    geo_fips: string;
    geo_name: string;
    data: RegionalTimeSeriesData[];
  }>;
}

interface RegionalSnapshotItem {
  geo_fips: string;
  geo_name: string;
  value: number;
}

interface RegionalSnapshot {
  table_name: string;
  line_code: number;
  line_description: string;
  unit?: string | null;
  unit_mult?: number | null;
  year?: string;
  data: RegionalSnapshotItem[];
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

// BEA Regional aggregates FIPS mapping
const REGION_FIPS_TO_NAME: Record<string, string> = {
  '00000': 'United States',
  '91000': 'New England',
  '92000': 'Mideast',
  '93000': 'Great Lakes',
  '94000': 'Plains',
  '95000': 'Southeast',
  '96000': 'Southwest',
  '97000': 'Rocky Mountain',
  '98000': 'Far West',
};

const STATE_FIPS_TO_NAME: Record<string, string> = {
  '01000': 'Alabama', '02000': 'Alaska', '04000': 'Arizona', '05000': 'Arkansas',
  '06000': 'California', '08000': 'Colorado', '09000': 'Connecticut', '10000': 'Delaware',
  '11000': 'District of Columbia', '12000': 'Florida', '13000': 'Georgia', '15000': 'Hawaii',
  '16000': 'Idaho', '17000': 'Illinois', '18000': 'Indiana', '19000': 'Iowa',
  '20000': 'Kansas', '21000': 'Kentucky', '22000': 'Louisiana', '23000': 'Maine',
  '24000': 'Maryland', '25000': 'Massachusetts', '26000': 'Michigan', '27000': 'Minnesota',
  '28000': 'Mississippi', '29000': 'Missouri', '30000': 'Montana', '31000': 'Nebraska',
  '32000': 'Nevada', '33000': 'New Hampshire', '34000': 'New Jersey', '35000': 'New Mexico',
  '36000': 'New York', '37000': 'North Carolina', '38000': 'North Dakota', '39000': 'Ohio',
  '40000': 'Oklahoma', '41000': 'Oregon', '42000': 'Pennsylvania', '44000': 'Rhode Island',
  '45000': 'South Carolina', '46000': 'South Dakota', '47000': 'Tennessee', '48000': 'Texas',
  '49000': 'Utah', '50000': 'Vermont', '51000': 'Virginia', '53000': 'Washington',
  '54000': 'West Virginia', '55000': 'Wisconsin', '56000': 'Wyoming',
};

interface CategoryConfig {
  name: string;
  description: string;
  icon: React.ElementType;
  color: ColorKey;
  geoType: 'State';
  metrics: { tableName: string; lineCode: number; name: string }[];
}

const REGIONAL_CATEGORIES: Record<string, CategoryConfig> = {
  stateGDP: {
    name: 'State GDP',
    description: 'Gross Domestic Product by State',
    icon: BarChart3,
    color: 'green',
    geoType: 'State',
    metrics: [
      { tableName: 'SAGDP1', lineCode: 1, name: 'Real GDP' },
      { tableName: 'SAGDP2N', lineCode: 1, name: 'Real GDP Growth (%)' },
      { tableName: 'SAGDP10N', lineCode: 1, name: 'Per Capita Real GDP' },
    ],
  },
  stateIncome: {
    name: 'State Income',
    description: 'Personal Income by State',
    icon: DollarSign,
    color: 'purple',
    geoType: 'State',
    metrics: [
      { tableName: 'SAINC1', lineCode: 1, name: 'Personal Income' },
      { tableName: 'SAINC1', lineCode: 3, name: 'Per Capita Personal Income' },
      { tableName: 'SAINC4', lineCode: 7100, name: 'Wages and Salaries' },
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

  const multiplier = unitMult ? Math.pow(10, unitMult) : 1;
  const actualValue = value * multiplier;

  if (Math.abs(actualValue) >= 1e12) return `$${(actualValue / 1e12).toFixed(2)}T`;
  if (Math.abs(actualValue) >= 1e9) return `$${(actualValue / 1e9).toFixed(2)}B`;
  if (Math.abs(actualValue) >= 1e6) return `$${(actualValue / 1e6).toFixed(1)}M`;
  if (Math.abs(actualValue) >= 1e3) return `$${(actualValue / 1e3).toFixed(1)}K`;

  return actualValue.toLocaleString(undefined, { maximumFractionDigits: 0 });
};

const calcPctChange = (current: number | null, previous: number | null): number | null => {
  if (current === null || previous === null || previous === 0) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
};

// Treemap color scale
const getTreemapColor = (value: number, maxValue: number, minValue: number) => {
  if (value === null || value === undefined || maxValue === minValue) {
    return 'rgb(59, 130, 246)';
  }

  const ratio = Math.max(0, Math.min(1, (value - minValue) / (maxValue - minValue)));
  const colors = [
    { r: 178, g: 223, b: 219 },
    { r: 79, g: 172, b: 254 },
    { r: 59, g: 130, b: 246 },
    { r: 37, g: 99, b: 235 },
    { r: 29, g: 78, b: 216 },
  ];

  const scaledIdx = ratio * (colors.length - 1);
  const lowerIdx = Math.min(Math.floor(scaledIdx), colors.length - 1);
  const upperIdx = Math.min(lowerIdx + 1, colors.length - 1);
  const t = scaledIdx - lowerIdx;

  const lowerColor = colors[lowerIdx];
  const upperColor = colors[upperIdx];

  const color = {
    r: Math.round(lowerColor.r + (upperColor.r - lowerColor.r) * t),
    g: Math.round(lowerColor.g + (upperColor.g - lowerColor.g) * t),
    b: Math.round(lowerColor.b + (upperColor.b - lowerColor.b) * t),
  };
  return `rgb(${color.r}, ${color.g}, ${color.b})`;
};

// Treemap content renderer
const createTreemapContent = (unit: string | null, unitMult: number | null, maxValue: number, minValue: number) => {
  return (props: { x: number; y: number; width: number; height: number; name: string; value: number }) => {
    const { x, y, width, height, name, value } = props;
    if (width < 30 || height < 20) return null;

    const color = getTreemapColor(value, maxValue, minValue);
    const formattedValue = formatValue(value, unit, unitMult);
    const showValue = width > 60 && height > 35;
    const showName = width > 40 && height > 25;
    const shortName = name?.length > 12 ? name.substring(0, 10) + '...' : name;

    const ratio = maxValue > minValue ? (value - minValue) / (maxValue - minValue) : 0.5;
    const textColor = ratio > 0.3 ? '#ffffff' : '#1e293b';

    return (
      <g>
        <rect x={x} y={y} width={width} height={height}
          style={{ fill: color, stroke: '#fff', strokeWidth: 1.5 }}
        />
        {showName && (
          <text x={x + width / 2} y={y + height / 2 - (showValue ? 8 : 0)}
            textAnchor="middle" dominantBaseline="middle"
            style={{
              fontSize: Math.min(14, Math.max(10, width / 6)),
              fill: textColor,
              fontWeight: 600,
            }}
          >
            {shortName}
          </text>
        )}
        {showValue && (
          <text x={x + width / 2} y={y + height / 2 + 10}
            textAnchor="middle" dominantBaseline="middle"
            style={{
              fontSize: Math.min(13, Math.max(9, width / 7)),
              fill: textColor,
              fontWeight: 500,
            }}
          >
            {formattedValue}
          </text>
        )}
      </g>
    );
  };
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
  onClick?: () => void;
}

function MetricCard({ title, value, change, isPercentagePoints, period, isLoading, onClick }: MetricCardProps) {
  const colorClass = change && change > 0.1 ? 'text-emerald-500' : change && change < -0.1 ? 'text-red-500' : 'text-gray-500';

  return (
    <div
      onClick={onClick}
      className={`p-3 rounded-lg border border-gray-200 bg-white transition-all ${onClick ? 'cursor-pointer hover:border-gray-400 hover:bg-gray-50' : ''}`}
    >
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

// Chart Metric Toggle (% Change vs Value)
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

// Map/Treemap Toggle
interface MapToggleProps {
  value: 'map' | 'treemap';
  onChange: (v: 'map' | 'treemap') => void;
}

function MapToggle({ value, onChange }: MapToggleProps) {
  return (
    <div className="flex rounded-lg overflow-hidden border border-gray-300">
      <button
        onClick={() => onChange('map')}
        className={`px-3 py-1.5 text-xs font-medium flex items-center gap-1 ${value === 'map' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
      >
        <MapIcon className="w-4 h-4" />Map
      </button>
      <button
        onClick={() => onChange('treemap')}
        className={`px-3 py-1.5 text-xs font-medium flex items-center gap-1 ${value === 'treemap' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
      >
        <LayoutGrid className="w-4 h-4" />Treemap
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

function CategorySection({ category }: CategorySectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('table');
  const [periodYears, setPeriodYears] = useState(10);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('value');
  const [selectedMetricIdx, setSelectedMetricIdx] = useState(0);
  const [selectedStates, setSelectedStates] = useState<string[]>([]);

  const colorSet = SECTION_COLORS[category.color];
  const selectedMetric = category.metrics[selectedMetricIdx];
  const validStateFips = Object.keys(STATE_FIPS_TO_NAME);

  const { data: snapshotDataRaw, isLoading: snapshotLoading } = useQuery({
    queryKey: ['regional-category-snapshot', category.name, selectedMetric.tableName, selectedMetric.lineCode],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalSnapshot<RegionalSnapshot>(
        selectedMetric.tableName,
        selectedMetric.lineCode,
        category.geoType
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const snapshotData = useMemo(() => {
    if (!snapshotDataRaw) return null;
    return {
      ...snapshotDataRaw,
      data: snapshotDataRaw.data?.filter(d => validStateFips.includes(d.geo_fips)),
    };
  }, [snapshotDataRaw, validStateFips]);

  // Auto-select ALL states when data loads
  useEffect(() => {
    if (snapshotData?.data && selectedStates.length === 0) {
      const allStates = snapshotData.data.map(s => s.geo_fips);
      setSelectedStates(allStates);
    }
  }, [snapshotData, selectedStates.length]);

  // Use batch endpoint - ONE query for all states instead of 50 separate queries
  const { data: batchData, isLoading: batchLoading } = useQuery({
    queryKey: ['regional-timeseries-batch', selectedMetric.tableName, selectedMetric.lineCode, selectedStates.join(',')],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalDataBatch<RegionalBatchTimeSeries>(
        selectedMetric.tableName,
        selectedMetric.lineCode,
        selectedStates
      );
      return response.data;
    },
    enabled: selectedStates.length > 0,
    staleTime: 5 * 60 * 1000,
  });

  // Convert batch response to map for easier access
  const timeSeriesMap = useMemo(() => {
    if (!batchData?.series) return new Map<string, RegionalTimeSeriesData[]>();
    return new Map(batchData.series.map(s => [s.geo_fips, s.data]));
  }, [batchData]);

  const topStates = useMemo(() => {
    if (!snapshotData?.data) return [];
    return [...snapshotData.data].sort((a, b) => b.value - a.value).slice(0, 5);
  }, [snapshotData]);

  const availablePeriods = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    if (batchData?.series) {
      batchData.series.forEach(s => {
        s.data.forEach((d: RegionalTimeSeriesData) => {
          const yearMatch = d.time_period.match(/^(\d{4})/);
          if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      });
    }
    return Array.from(allPeriods).sort();
  }, [batchData, periodYears]);

  const chartData = useMemo(() => {
    if (selectedStates.length === 0 || batchLoading) return [];

    return availablePeriods.map(period => {
      const point: Record<string, unknown> = { period };
      selectedStates.forEach((fips) => {
        const seriesData = timeSeriesMap.get(fips) || [];
        const currentIdx = seriesData.findIndex((d: RegionalTimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        const isPercentOrIndex = batchData?.unit?.toLowerCase().includes('percent') || batchData?.unit?.toLowerCase().includes('index');
        let yoy: number | null = null;
        if (current?.value !== null && current?.value !== undefined && prev?.value !== null && prev?.value !== undefined) {
          yoy = isPercentOrIndex ? current.value - prev.value : calcPctChange(current.value, prev.value);
        }

        point[`${fips}_value`] = current?.value ?? null;
        point[`${fips}_pct`] = yoy;
      });
      return point;
    });
  }, [selectedStates, batchLoading, batchData, timeSeriesMap, availablePeriods]);

  const tableData = useMemo(() => {
    if (selectedStates.length === 0) return [];

    return selectedStates.map((fips, idx) => {
      const seriesData = timeSeriesMap.get(fips) || [];
      const stateName = snapshotData?.data?.find(s => s.geo_fips === fips)?.geo_name || fips;

      const row: Record<string, unknown> = { fips, name: stateName, color: CHART_COLORS[idx % CHART_COLORS.length] };
      availablePeriods.forEach(period => {
        const entry = seriesData.find((d: RegionalTimeSeriesData) => d.time_period === period);
        row[period] = entry?.value ?? null;
      });
      return row;
    });
  }, [selectedStates, timeSeriesMap, availablePeriods, snapshotData]);

  const toggleStateSelection = (fips: string) => {
    if (selectedStates.includes(fips)) {
      setSelectedStates(selectedStates.filter(f => f !== fips));
    } else if (selectedStates.length < 8) {
      setSelectedStates([...selectedStates, fips]);
    }
  };

  const getStateName = (fips: string) => snapshotData?.data?.find(s => s.geo_fips === fips)?.geo_name || fips;
  const isTimeSeriesLoading = batchLoading;

  return (
    <SectionCard
      title={category.name}
      description={category.description}
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
      {/* Metric Selector */}
      <div className="flex flex-wrap gap-4 mb-4 items-center">
        <select
          value={selectedMetricIdx}
          onChange={(e) => setSelectedMetricIdx(Number(e.target.value))}
          className="min-w-[250px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {category.metrics.map((m, idx) => (
            <option key={idx} value={idx}>{m.name}</option>
          ))}
        </select>

        {snapshotData?.data && (
          <select
            value=""
            onChange={(e) => {
              const fips = e.target.value;
              if (fips && !selectedStates.includes(fips)) {
                toggleStateSelection(fips);
              }
            }}
            className="min-w-[200px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Add State...</option>
            {snapshotData.data
              .filter(s => !selectedStates.includes(s.geo_fips))
              .map(s => (
                <option key={s.geo_fips} value={s.geo_fips}>{s.geo_name}</option>
              ))}
          </select>
        )}
      </div>

      {/* Top 5 States */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-4">
        {snapshotLoading ? (
          Array.from({ length: 5 }).map((_, idx) => (
            <MetricCard key={idx} title="Loading..." value="" isLoading={true} />
          ))
        ) : (
          topStates.map((state, idx) => (
            <MetricCard
              key={state.geo_fips}
              title={`#${idx + 1} ${state.geo_name}`}
              value={formatValue(state.value, snapshotData?.unit, snapshotData?.unit_mult)}
              period={snapshotData?.year?.toString()}
              onClick={() => toggleStateSelection(state.geo_fips)}
            />
          ))
        )}
      </div>

      {/* Selected States Chips */}
      {selectedStates.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {selectedStates.map((fips, idx) => (
            <span
              key={fips}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs"
              style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
            >
              {getStateName(fips)}
              <button onClick={() => toggleStateSelection(fips)} className="hover:bg-white/20 rounded-full p-0.5">×</button>
            </span>
          ))}
        </div>
      )}

      {/* Chart View */}
      {viewMode === 'chart' && (
        isTimeSeriesLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : chartData.length === 0 ? (
          <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select states to view time series chart</div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
                <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                <YAxis
                  tick={{ fontSize: 10 }}
                  width={80}
                  tickFormatter={(v) => chartMetric === 'pct' ? `${v?.toFixed(1)}%` : formatValue(v, batchData?.unit, batchData?.unit_mult)}
                  domain={chartMetric === 'pct' ? ['auto', 'auto'] : undefined}
                />
                {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />}
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                  formatter={(value: number, name: string) => {
                    const fips = name.split('_')[0];
                    const isPct = name.endsWith('_pct');
                    if (isPct) {
                      return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}%`, `${getStateName(fips)} (YoY)`];
                    }
                    return [formatValue(value, batchData?.unit, batchData?.unit_mult), getStateName(fips)];
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} formatter={(v) => getStateName(v.split('_')[0])} />
                {selectedStates.map((fips, idx) => (
                  <Line
                    key={fips}
                    type="monotone"
                    dataKey={chartMetric === 'pct' ? `${fips}_pct` : `${fips}_value`}
                    name={chartMetric === 'pct' ? `${fips}_pct` : `${fips}_value`}
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
        isTimeSeriesLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : tableData.length === 0 ? (
          <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select states to view time series table</div>
        ) : (
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-100">
                <tr>
                  <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-10 min-w-[120px]">State</th>
                  {availablePeriods.slice().reverse().map(period => (
                    <th key={period} className="text-right p-2 font-semibold min-w-[80px]">{period}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, idx) => {
                  const typedRow = row as Record<string, unknown>;
                  return (
                    <tr key={typedRow.fips as string} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className={`p-2 sticky left-0 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: typedRow.color as string }} />
                          {typedRow.name as string}
                        </div>
                      </td>
                      {availablePeriods.slice().reverse().map(period => (
                        <td key={period} className="text-right p-2 font-mono text-sm">
                          {formatValue(typedRow[period] as number | null, batchData?.unit, batchData?.unit_mult)}
                        </td>
                      ))}
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
// REGION SECTION COMPONENT (BEA Regional Aggregates)
// ============================================================================

interface RegionSectionProps {
  category: CategoryConfig;
  title: string;
}

function RegionSection({ category, title }: RegionSectionProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [periodYears, setPeriodYears] = useState(10);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('value');
  const [selectedMetricIdx, setSelectedMetricIdx] = useState(0);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);

  const colorSet = SECTION_COLORS[category.color];
  const selectedMetric = category.metrics[selectedMetricIdx];
  const validRegionFips = Object.keys(REGION_FIPS_TO_NAME).filter(f => f !== '00000');

  // For regions, we need to get State data and filter to regional aggregates (91000, 92000, etc.)
  // These are included in the State geo_type data from BEA
  const { data: snapshotDataRaw, isLoading: snapshotLoading } = useQuery({
    queryKey: ['regional-region-snapshot', title, selectedMetric.tableName, selectedMetric.lineCode],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalSnapshot<RegionalSnapshot>(
        selectedMetric.tableName,
        selectedMetric.lineCode,
        'State' // Get state data which includes regional aggregates
      );
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Filter to only BEA regional aggregates (91000=New England, 92000=Mideast, etc.)
  const snapshotData = useMemo(() => {
    if (!snapshotDataRaw) return null;
    const filteredData = snapshotDataRaw.data?.filter(d => validRegionFips.includes(d.geo_fips)) || [];
    return {
      ...snapshotDataRaw,
      data: filteredData,
    };
  }, [snapshotDataRaw, validRegionFips]);

  useEffect(() => {
    if (snapshotData?.data && selectedRegions.length === 0) {
      const allRegions = snapshotData.data.map(s => s.geo_fips);
      setSelectedRegions(allRegions);
    }
  }, [snapshotData, selectedRegions.length]);

  // Use batch endpoint - ONE query for all regions instead of 8 separate queries
  const { data: batchData, isLoading: batchLoading } = useQuery({
    queryKey: ['regional-region-timeseries-batch', selectedMetric.tableName, selectedMetric.lineCode, selectedRegions.join(',')],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalDataBatch<RegionalBatchTimeSeries>(
        selectedMetric.tableName,
        selectedMetric.lineCode,
        selectedRegions
      );
      return response.data;
    },
    enabled: selectedRegions.length > 0,
    staleTime: 5 * 60 * 1000,
  });

  // Convert batch response to map for easier access
  const timeSeriesMap = useMemo(() => {
    if (!batchData?.series) return new Map<string, RegionalTimeSeriesData[]>();
    return new Map(batchData.series.map(s => [s.geo_fips, s.data]));
  }, [batchData]);

  const availablePeriods = useMemo(() => {
    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    if (batchData?.series) {
      batchData.series.forEach(s => {
        s.data.forEach((d: RegionalTimeSeriesData) => {
          const yearMatch = d.time_period.match(/^(\d{4})/);
          if (!yearMatch || parseInt(yearMatch[1]) >= cutoffYear) {
            allPeriods.add(d.time_period);
          }
        });
      });
    }
    return Array.from(allPeriods).sort();
  }, [batchData, periodYears]);

  const chartData = useMemo(() => {
    if (selectedRegions.length === 0 || batchLoading) return [];

    return availablePeriods.map(period => {
      const point: Record<string, unknown> = { period };
      selectedRegions.forEach((fips) => {
        const seriesData = timeSeriesMap.get(fips) || [];
        const currentIdx = seriesData.findIndex((d: RegionalTimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        const isPercentOrIndex = batchData?.unit?.toLowerCase().includes('percent') || batchData?.unit?.toLowerCase().includes('index');
        let yoy: number | null = null;
        if (current?.value !== null && current?.value !== undefined && prev?.value !== null && prev?.value !== undefined) {
          yoy = isPercentOrIndex ? current.value - prev.value : calcPctChange(current.value, prev.value);
        }

        point[`${fips}_value`] = current?.value ?? null;
        point[`${fips}_pct`] = yoy;
      });
      return point;
    });
  }, [selectedRegions, batchLoading, batchData, timeSeriesMap, availablePeriods]);

  const tableData = useMemo(() => {
    if (selectedRegions.length === 0) return [];

    return selectedRegions.map((fips, idx) => {
      const seriesData = timeSeriesMap.get(fips) || [];
      const regionName = REGION_FIPS_TO_NAME[fips] || snapshotData?.data?.find(s => s.geo_fips === fips)?.geo_name || fips;

      const row: Record<string, unknown> = { fips, name: regionName, color: CHART_COLORS[idx % CHART_COLORS.length] };
      availablePeriods.forEach(period => {
        const entry = seriesData.find((d: RegionalTimeSeriesData) => d.time_period === period);
        row[period] = entry?.value ?? null;
      });
      return row;
    });
  }, [selectedRegions, timeSeriesMap, availablePeriods, snapshotData]);

  const toggleRegionSelection = (fips: string) => {
    if (selectedRegions.includes(fips)) {
      setSelectedRegions(selectedRegions.filter(f => f !== fips));
    } else {
      setSelectedRegions([...selectedRegions, fips]);
    }
  };

  const getRegionName = (fips: string) => REGION_FIPS_TO_NAME[fips] || snapshotData?.data?.find(s => s.geo_fips === fips)?.geo_name || fips;
  const isTimeSeriesLoading = batchLoading;

  return (
    <SectionCard
      title={title}
      description={`${category.description} - BEA Regional Aggregates`}
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
      {/* Metric Selector */}
      <div className="flex flex-wrap gap-4 mb-4 items-center">
        <select
          value={selectedMetricIdx}
          onChange={(e) => setSelectedMetricIdx(Number(e.target.value))}
          className="min-w-[250px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {category.metrics.map((m, idx) => (
            <option key={idx} value={idx}>{m.name}</option>
          ))}
        </select>
      </div>

      {/* Region Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2 mb-4">
        {snapshotLoading ? (
          Array.from({ length: 8 }).map((_, idx) => (
            <MetricCard key={idx} title="Loading..." value="" isLoading={true} />
          ))
        ) : (
          snapshotData?.data?.map((region) => (
            <MetricCard
              key={region.geo_fips}
              title={REGION_FIPS_TO_NAME[region.geo_fips] || region.geo_name}
              value={formatValue(region.value, snapshotData?.unit, snapshotData?.unit_mult)}
              period={snapshotData?.year?.toString()}
              onClick={() => toggleRegionSelection(region.geo_fips)}
            />
          ))
        )}
      </div>

      {/* Selected Regions Chips */}
      {selectedRegions.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {selectedRegions.map((fips, idx) => (
            <span
              key={fips}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs"
              style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
            >
              {getRegionName(fips)}
              <button onClick={() => toggleRegionSelection(fips)} className="hover:bg-white/20 rounded-full p-0.5">×</button>
            </span>
          ))}
        </div>
      )}

      {/* Chart View */}
      {viewMode === 'chart' && (
        isTimeSeriesLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : chartData.length === 0 ? (
          <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select regions to view time series chart</div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
                <XAxis dataKey="period" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                <YAxis
                  tick={{ fontSize: 10 }}
                  width={80}
                  tickFormatter={(v) => chartMetric === 'pct' ? `${v?.toFixed(1)}%` : formatValue(v, batchData?.unit, batchData?.unit_mult)}
                  domain={chartMetric === 'pct' ? ['auto', 'auto'] : undefined}
                />
                {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />}
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                  formatter={(value: number, name: string) => {
                    const fips = name.split('_')[0];
                    const isPct = name.endsWith('_pct');
                    if (isPct) {
                      return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}%`, `${getRegionName(fips)} (YoY)`];
                    }
                    return [formatValue(value, batchData?.unit, batchData?.unit_mult), getRegionName(fips)];
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '10px' }} formatter={(v) => getRegionName(v.split('_')[0])} />
                {selectedRegions.map((fips, idx) => (
                  <Line
                    key={fips}
                    type="monotone"
                    dataKey={chartMetric === 'pct' ? `${fips}_pct` : `${fips}_value`}
                    name={chartMetric === 'pct' ? `${fips}_pct` : `${fips}_value`}
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
        isTimeSeriesLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : tableData.length === 0 ? (
          <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select regions to view time series table</div>
        ) : (
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-100">
                <tr>
                  <th className="text-left p-2 font-semibold sticky left-0 bg-gray-100 z-10 min-w-[140px]">Region</th>
                  {availablePeriods.slice().reverse().map(period => (
                    <th key={period} className="text-right p-2 font-semibold min-w-[80px]">{period}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, idx) => {
                  const typedRow = row as Record<string, unknown>;
                  return (
                    <tr key={typedRow.fips as string} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className={`p-2 sticky left-0 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: typedRow.color as string }} />
                          {typedRow.name as string}
                        </div>
                      </td>
                      {availablePeriods.slice().reverse().map(period => (
                        <td key={period} className="text-right p-2 font-mono text-sm">
                          {formatValue(typedRow[period] as number | null, batchData?.unit, batchData?.unit_mult)}
                        </td>
                      ))}
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
// STATE RANKINGS SECTION (with Timeline)
// ============================================================================

function StateRankingsSection() {
  const [periodYears, setPeriodYears] = useState(20);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const colorSet = SECTION_COLORS.red;
  const validStateFips = Object.keys(STATE_FIPS_TO_NAME);

  const currentYear = new Date().getFullYear();
  const years = useMemo(() => {
    const count = periodYears === 0 ? 50 : periodYears;
    const result: string[] = [];
    for (let i = count - 1; i >= 0; i--) {
      result.push(String(currentYear - i));
    }
    return result;
  }, [currentYear, periodYears]);

  const { data: snapshotDataRaw, isLoading } = useQuery({
    queryKey: ['regional-state-rankings', selectedYear],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalSnapshot<RegionalSnapshot>('SAGDP1', 1, 'State', selectedYear ? parseInt(selectedYear) : undefined);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const snapshotData = useMemo(() => {
    if (!snapshotDataRaw) return null;
    return {
      ...snapshotDataRaw,
      data: snapshotDataRaw.data?.filter(d => validStateFips.includes(d.geo_fips)),
    };
  }, [snapshotDataRaw, validStateFips]);

  useEffect(() => {
    if (!selectedYear && snapshotData?.year) {
      setSelectedYear(snapshotData.year);
    }
  }, [snapshotData, selectedYear]);

  useEffect(() => {
    setSelectedYear(null);
  }, [periodYears]);

  const { topStates, bottomStates } = useMemo(() => {
    if (!snapshotData?.data) return { topStates: [], bottomStates: [] };
    const sorted = [...snapshotData.data].sort((a, b) => b.value - a.value);
    return {
      topStates: sorted.slice(0, 10),
      bottomStates: sorted.slice(-10).reverse(),
    };
  }, [snapshotData]);

  const availableYears = years.filter(y => parseInt(y) <= currentYear);

  return (
    <SectionCard
      title="State Rankings"
      description="Top and Bottom States by GDP"
      color="red"
      icon={Trophy}
      rightContent={
        <PeriodSelector value={periodYears} onChange={(v) => { setPeriodYears(v); setSelectedYear(null); }} color={colorSet.main} />
      }
    >
      {isLoading && (
        <div className="flex items-center gap-2 mb-4">
          <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
          <span className="text-sm text-gray-500">Loading data...</span>
        </div>
      )}

      {snapshotData?.data ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Top 10 */}
            <div>
              <h4 className="text-sm font-semibold text-emerald-600 mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" /> Top 10 States ({selectedYear || snapshotData.year})
              </h4>
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="text-left p-2 font-semibold">#</th>
                    <th className="text-left p-2 font-semibold">State</th>
                    <th className="text-right p-2 font-semibold">GDP</th>
                  </tr>
                </thead>
                <tbody>
                  {topStates.map((state, idx) => (
                    <tr key={state.geo_fips} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="p-2 font-medium text-emerald-600">{idx + 1}</td>
                      <td className="p-2">{state.geo_name}</td>
                      <td className="p-2 text-right font-mono">{formatValue(state.value, snapshotData.unit, snapshotData.unit_mult)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Bottom 10 */}
            <div>
              <h4 className="text-sm font-semibold text-red-600 mb-3 flex items-center gap-2">
                <TrendingDown className="w-4 h-4" /> Bottom 10 States ({selectedYear || snapshotData.year})
              </h4>
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="text-left p-2 font-semibold">#</th>
                    <th className="text-left p-2 font-semibold">State</th>
                    <th className="text-right p-2 font-semibold">GDP</th>
                  </tr>
                </thead>
                <tbody>
                  {bottomStates.map((state, idx) => (
                    <tr key={state.geo_fips} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="p-2 font-medium text-red-600">{(snapshotData.data?.length || 0) - 9 + idx}</td>
                      <td className="p-2">{state.geo_name}</td>
                      <td className="p-2 text-right font-mono">{formatValue(state.value, snapshotData.unit, snapshotData.unit_mult)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Timeline */}
          <div className="mt-6 px-4">
            <p className="text-xs text-gray-500 text-center mb-3">Click a year to view historical rankings</p>
            <div className="relative py-4">
              {/* Timeline Line */}
              <div className="absolute top-1/2 left-5 right-5 h-1 bg-gray-300 rounded-full -translate-y-1/2" />

              {/* Year Points */}
              <div className="flex justify-between relative px-2">
                {availableYears.map((year, idx) => {
                  const isSelected = year === (selectedYear || snapshotData.year);
                  const labelInterval = availableYears.length <= 10 ? 1 : availableYears.length <= 20 ? 2 : 5;
                  const showLabel = idx === 0 || idx === availableYears.length - 1 || idx % labelInterval === 0;

                  return (
                    <div
                      key={year}
                      className="flex flex-col items-center cursor-pointer transition-transform hover:scale-110"
                      onClick={() => setSelectedYear(year)}
                    >
                      <div
                        className={`rounded-full transition-all ${isSelected ? 'w-5 h-5 border-[3px] border-white shadow-lg' : 'w-3 h-3 border-2 border-gray-300 hover:bg-gray-500'}`}
                        style={{
                          backgroundColor: isSelected ? colorSet.main : '#9ca3af',
                          boxShadow: isSelected ? `0 0 0 3px ${colorSet.main}40` : undefined,
                        }}
                      />
                      <span
                        className={`mt-2 text-xs transition-all ${isSelected ? 'font-bold' : 'font-normal'}`}
                        style={{
                          color: isSelected ? colorSet.main : '#6b7280',
                          opacity: showLabel || isSelected ? 1 : 0,
                        }}
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
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">No data available for the selected period</div>
      ) : null}
    </SectionCard>
  );
}

// ============================================================================
// DATA EXPLORER COMPONENT
// ============================================================================

interface DataExplorerProps {
  tables: RegionalTable[];
}

function DataExplorer({ tables }: DataExplorerProps) {
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [selectedLineCode, setSelectedLineCode] = useState<RegionalLineCode | null>(null);
  const [selectedGeos, setSelectedGeos] = useState<Array<{ fips: string; name: string }>>([]);
  const [geoType, setGeoType] = useState<'State' | 'County'>('State');
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [periodYears, setPeriodYears] = useState(10);
  const [chartMetric, setChartMetric] = useState<'pct' | 'value'>('pct');

  useEffect(() => {
    if (tables.length > 0 && !selectedTable) {
      setSelectedTable(tables[0].table_name);
    }
  }, [tables, selectedTable]);

  const { data: lineCodes, isLoading: lineCodesLoading } = useQuery({
    queryKey: ['regional-explorer-linecodes', selectedTable],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalLineCodes<RegionalLineCode[]>(selectedTable);
      return response.data;
    },
    enabled: !!selectedTable,
  });

  useEffect(() => {
    if (lineCodes && lineCodes.length > 0) {
      setSelectedLineCode(lineCodes[0]);
    }
  }, [lineCodes]);

  useEffect(() => {
    setSelectedLineCode(null);
    setSelectedGeos([]);
  }, [selectedTable]);

  const { data: geoOptions } = useQuery({
    queryKey: ['regional-explorer-geos', geoType],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalGeographies<RegionalGeo[]>(geoType);
      return response.data;
    },
  });

  const geoQueries = useQueries({
    queries: selectedGeos.map(geo => ({
      queryKey: ['regional-explorer-data', selectedTable, selectedLineCode?.line_code, geo.fips],
      queryFn: async () => {
        const response = await beaResearchAPI.getRegionalData<RegionalTimeSeries>(
          selectedTable,
          selectedLineCode!.line_code,
          geo.fips
        );
        return response.data;
      },
      enabled: !!selectedTable && !!selectedLineCode && !!geo.fips,
      staleTime: 5 * 60 * 1000,
    })),
  });

  const chartData = useMemo(() => {
    if (selectedGeos.length === 0) return [];

    const allPeriods = new Set<string>();
    const currentYear = new Date().getFullYear();
    const cutoffYear = periodYears === 0 ? 0 : currentYear - periodYears;

    geoQueries.forEach(q => {
      if (q.data?.data) {
        q.data.data.forEach((d: RegionalTimeSeriesData) => {
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
      selectedGeos.forEach((geo, idx) => {
        const data = geoQueries[idx]?.data;
        const seriesData = data?.data || [];
        const currentIdx = seriesData.findIndex((d: RegionalTimeSeriesData) => d.time_period === period);
        const current = seriesData[currentIdx];
        const prev = currentIdx > 0 ? seriesData[currentIdx - 1] : null;

        const isPercentOrIndex = data?.unit?.toLowerCase().includes('percent') || data?.unit?.toLowerCase().includes('index');
        let yoy: number | null = null;
        if (current?.value !== null && current?.value !== undefined && prev?.value !== null && prev?.value !== undefined) {
          yoy = isPercentOrIndex ? current.value - prev.value : calcPctChange(current.value, prev.value);
        }

        point[`${geo.fips}_value`] = current?.value ?? null;
        point[`${geo.fips}_yoy`] = yoy;
      });
      return point;
    });
  }, [geoQueries, selectedGeos, periodYears]);

  const handleAddGeo = (geo: RegionalGeo | null) => {
    if (!geo) return;
    if (selectedGeos.find(g => g.fips === geo.geo_fips)) return;
    if (selectedGeos.length >= 8) return;
    setSelectedGeos([...selectedGeos, { fips: geo.geo_fips, name: geo.geo_name }]);
  };

  const handleRemoveGeo = (fips: string) => {
    setSelectedGeos(selectedGeos.filter(g => g.fips !== fips));
  };

  const primaryData = geoQueries[0]?.data;
  const isLoading = geoQueries.some(q => q.isLoading);

  return (
    <SectionCard
      title="Data Explorer"
      description="Search and explore all regional data - States and Counties"
      color="gray"
      icon={Search}
      rightContent={
        <div className="flex gap-2 items-center">
          <ChartMetricToggle value={chartMetric} onChange={setChartMetric} />
          <PeriodSelector value={periodYears} onChange={setPeriodYears} />
          <ViewToggle value={viewMode} onChange={setViewMode} />
        </div>
      }
    >
      {/* Selectors Row */}
      <div className="flex flex-wrap gap-4 mb-4">
        <select
          value={selectedTable}
          onChange={(e) => setSelectedTable(e.target.value)}
          className="min-w-[300px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {tables.map(t => (
            <option key={t.table_name} value={t.table_name}>
              {t.table_name} - {t.table_description?.substring(0, 40)}
            </option>
          ))}
        </select>

        <select
          value={selectedLineCode?.line_code || ''}
          onChange={(e) => {
            const lc = lineCodes?.find(l => l.line_code === Number(e.target.value));
            setSelectedLineCode(lc || null);
            setSelectedGeos([]);
          }}
          disabled={!selectedTable || lineCodesLoading}
          className="min-w-[300px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        >
          <option value="">Select Metric...</option>
          {lineCodes?.map(lc => (
            <option key={lc.line_code} value={lc.line_code}>
              {lc.line_code}. {lc.line_description?.substring(0, 50)}
            </option>
          ))}
        </select>

        <select
          value={geoType}
          onChange={(e) => {
            setGeoType(e.target.value as 'State' | 'County');
            setSelectedGeos([]);
          }}
          className="min-w-[100px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="State">State</option>
          <option value="County">County</option>
        </select>

        <select
          value=""
          onChange={(e) => {
            const geo = geoOptions?.find(g => g.geo_fips === e.target.value);
            if (geo) handleAddGeo(geo);
          }}
          disabled={!selectedLineCode || selectedGeos.length >= 8}
          className="flex-1 min-w-[250px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        >
          <option value="">{selectedGeos.length >= 8 ? 'Max 8 regions' : 'Add Geography...'}</option>
          {geoOptions?.filter(g => !selectedGeos.find(sg => sg.fips === g.geo_fips)).map(g => (
            <option key={g.geo_fips} value={g.geo_fips}>{g.geo_name}</option>
          ))}
        </select>
      </div>

      {/* Selected Geos */}
      {selectedGeos.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {selectedGeos.map((geo, idx) => (
            <span
              key={geo.fips}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-white text-xs"
              style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}
            >
              {geo.name.length > 20 ? geo.name.substring(0, 18) + '...' : geo.name}
              <button onClick={() => handleRemoveGeo(geo.fips)} className="hover:bg-white/20 rounded-full p-0.5">×</button>
            </span>
          ))}
        </div>
      )}

      {/* Chart or Table */}
      {selectedGeos.length === 0 ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">Select a table, metric, and add geographies to view data.</div>
      ) : isLoading ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
      ) : chartData.length === 0 ? (
        <div className="bg-amber-50 text-amber-700 p-4 rounded-lg">No data available for selected regions</div>
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
              {chartMetric === 'pct' && <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />}
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.96)', border: 'none', borderRadius: 8, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
                formatter={(value: number, name: string) => {
                  const fips = name.split('_')[0];
                  const geoName = selectedGeos.find(g => g.fips === fips)?.name || fips;
                  const isYoy = name.endsWith('_yoy');
                  if (isYoy) {
                    return [`${value >= 0 ? '+' : ''}${value?.toFixed(2)}%`, `${geoName} (YoY)`];
                  }
                  return [formatValue(value, primaryData?.unit, primaryData?.unit_mult), geoName];
                }}
              />
              {selectedGeos.length > 1 && (
                <Legend wrapperStyle={{ fontSize: '11px' }} formatter={(v) => {
                  const fips = v.split('_')[0];
                  return selectedGeos.find(g => g.fips === fips)?.name?.substring(0, 20) || fips;
                }} />
              )}
              {selectedGeos.map((geo, idx) => (
                <Line
                  key={geo.fips}
                  type="monotone"
                  dataKey={chartMetric === 'pct' ? `${geo.fips}_yoy` : `${geo.fips}_value`}
                  name={chartMetric === 'pct' ? `${geo.fips}_yoy` : `${geo.fips}_value`}
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
                {selectedGeos.map((geo, idx) => (
                  <th key={geo.fips} className="text-right p-2 font-semibold whitespace-nowrap">
                    <div className="flex items-center justify-end gap-1">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                      {geo.name.length > 12 ? geo.name.substring(0, 10) + '...' : geo.name}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {chartData.slice().reverse().slice(0, 40).map((row, rowIdx) => {
                const typedRow = row as Record<string, unknown>;
                return (
                  <tr key={typedRow.period as string} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className={`p-2 font-medium sticky left-0 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                      {typedRow.period as string}
                    </td>
                    {selectedGeos.map((geo) => (
                      <td key={geo.fips} className="text-right p-2 font-mono text-sm">
                        {formatValue(typedRow[`${geo.fips}_value`] as number | null, primaryData?.unit, primaryData?.unit_mult)}
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

export default function RegionalExplorer() {
  const [snapshotViewMode, setSnapshotViewMode] = useState<'map' | 'treemap'>('map');
  const [usaMapLoaded, setUsaMapLoaded] = useState(false);

  // Load USA GeoJSON map data
  useEffect(() => {
    if (!usaMapLoaded) {
      fetch('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json')
        .then(res => res.json())
        .then((geoJson) => {
          echarts.registerMap('USA', geoJson as Parameters<typeof echarts.registerMap>[1]);
          setUsaMapLoaded(true);
        })
        .catch(err => console.error('Failed to load USA map:', err));
    }
  }, [usaMapLoaded]);

  const { data: tables, isLoading: tablesLoading } = useQuery({
    queryKey: ['regional-tables'],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalTables<RegionalTable[]>();
      return response.data;
    },
  });

  const validStateFips = useMemo(() => Object.keys(STATE_FIPS_TO_NAME), []);

  const { data: snapshotDataRaw, isLoading: snapshotLoading } = useQuery({
    queryKey: ['regional-snapshot'],
    queryFn: async () => {
      const response = await beaResearchAPI.getRegionalSnapshot<RegionalSnapshot>('SAGDP1', 1, 'State');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const snapshotData = useMemo(() => {
    if (!snapshotDataRaw) return null;
    return {
      ...snapshotDataRaw,
      data: snapshotDataRaw.data?.filter(d => validStateFips.includes(d.geo_fips)),
    };
  }, [snapshotDataRaw, validStateFips]);

  // Prepare treemap data
  const { treemapData, treemapContentRenderer } = useMemo(() => {
    if (!snapshotData?.data?.length) return { treemapData: [], treemapContentRenderer: null };
    const maxValue = Math.max(...snapshotData.data.map(d => d.value));
    const minValue = Math.min(...snapshotData.data.map(d => d.value));
    const data = snapshotData.data.map(d => ({
      name: d.geo_name,
      value: d.value,
      geo_fips: d.geo_fips,
    }));
    const renderer = createTreemapContent(snapshotData.unit || null, snapshotData.unit_mult || null, maxValue, minValue);
    return { treemapData: data, treemapContentRenderer: renderer };
  }, [snapshotData]);

  // ECharts map options
  const mapChartOption = useMemo(() => {
    if (!snapshotData?.data?.length || !usaMapLoaded) return null;

    const mapData = snapshotData.data
      .filter(d => STATE_FIPS_TO_NAME[d.geo_fips])
      .map(d => ({
        name: STATE_FIPS_TO_NAME[d.geo_fips] || d.geo_name,
        value: d.value,
        geo_fips: d.geo_fips,
      }));

    if (mapData.length === 0) return null;

    const values = mapData.map(d => d.value);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const unit = snapshotData.unit;
    const unitMult = snapshotData.unit_mult;

    return {
      backgroundColor: '#f8fafc',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(255,255,255,0.96)',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        textStyle: { color: '#1e293b' },
        formatter: (params: { name: string; data?: { value: number } }) => {
          if (!params.data?.value) return `<span style="font-weight:600">${params.name}</span><br/><span style="color:#94a3b8">No data</span>`;
          const formatted = formatValue(params.data.value, unit, unitMult);
          return `<span style="font-weight:600">${params.name}</span><br/><span style="color:#3b82f6;font-weight:500">Real GDP: ${formatted}</span>`;
        },
      },
      visualMap: {
        min: minVal, max: maxVal, left: 20, bottom: 20,
        text: ['High', 'Low'],
        textStyle: { color: '#64748b', fontSize: 11 },
        calculable: true,
        inRange: { color: ['#dbeafe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8'] },
        formatter: (value: number) => formatValue(value, unit, unitMult),
        itemWidth: 12,
        itemHeight: 100,
      },
      series: [{
        name: 'State GDP', type: 'map', map: 'USA', roam: true,
        zoom: 1.1,
        center: [-96, 37.5],
        emphasis: {
          label: { show: true, fontSize: 11, fontWeight: 'bold', color: '#1e293b' },
          itemStyle: { areaColor: '#fbbf24', shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.2)' },
        },
        select: {
          label: { show: true, fontSize: 11, fontWeight: 'bold', color: '#1e293b' },
          itemStyle: { areaColor: '#f59e0b' },
        },
        data: mapData,
        label: { show: false },
        itemStyle: { borderColor: '#e2e8f0', borderWidth: 1, areaColor: '#f1f5f9' },
      }],
    };
  }, [snapshotData, usaMapLoaded]);

  // Top 5 states for snapshot
  const topStates = useMemo(() => {
    if (!snapshotData?.data?.length) return [];
    return [...snapshotData.data].sort((a, b) => b.value - a.value).slice(0, 5);
  }, [snapshotData]);

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
          <h1 className="text-2xl font-bold">Regional Explorer</h1>
          <p className="text-sm text-gray-500">State and County Economic Data - GDP, Personal Income, Employment</p>
        </div>
      </div>

      <hr className="my-6 border-gray-200" />

      {/* Section 1: National Map Overview */}
      <SectionCard
        title="National Map"
        description="US Economic Overview by State"
        color="blue"
        icon={Globe}
        collapsible={false}
        rightContent={<MapToggle value={snapshotViewMode} onChange={setSnapshotViewMode} />}
      >
        {/* Top 5 States */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-4">
          {topStates.map((state, idx) => (
            <MetricCard
              key={state.geo_fips}
              title={`#${idx + 1} ${state.geo_name}`}
              value={formatValue(state.value, snapshotData?.unit, snapshotData?.unit_mult)}
              period={snapshotData?.year?.toString()}
            />
          ))}
        </div>

        {/* Map or Treemap */}
        {snapshotLoading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-gray-400" /></div>
        ) : snapshotViewMode === 'map' ? (
          mapChartOption ? (
            <div className="h-[450px]">
              <ReactECharts option={mapChartOption} style={{ height: '100%', width: '100%' }} opts={{ renderer: 'svg' }} />
            </div>
          ) : (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-gray-400 mr-2" />
              <span className="text-gray-500">Loading map...</span>
            </div>
          )
        ) : treemapData.length > 0 && treemapContentRenderer ? (
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap data={treemapData} dataKey="value" aspectRatio={4 / 3} stroke="#fff" content={treemapContentRenderer as any}>
                <Tooltip
                  content={({ payload }) => {
                    if (!payload || !payload.length) return null;
                    const data = payload[0].payload as { name: string; value: number };
                    return (
                      <div className="bg-white/95 border border-gray-200 rounded-lg p-3 shadow-lg">
                        <p className="font-semibold">{data.name}</p>
                        <p className="text-gray-600 text-sm">
                          Real GDP: {formatValue(data.value, snapshotData?.unit, snapshotData?.unit_mult)}
                        </p>
                      </div>
                    );
                  }}
                />
              </Treemap>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">No data available</div>
        )}
      </SectionCard>

      {/* Section 2: State GDP */}
      <CategorySection categoryKey="stateGDP" category={REGIONAL_CATEGORIES.stateGDP} />

      {/* Section 3: State Income */}
      <CategorySection categoryKey="stateIncome" category={REGIONAL_CATEGORIES.stateIncome} />

      {/* Section 4: GDP by Region (BEA Regional Aggregates) */}
      <RegionSection category={REGIONAL_CATEGORIES.stateGDP} title="GDP by Region" />

      {/* Section 5: Income by Region (BEA Regional Aggregates) */}
      <RegionSection category={REGIONAL_CATEGORIES.stateIncome} title="Income by Region" />

      {/* Section 6: State Rankings with Timeline */}
      <StateRankingsSection />

      {/* Section 7: Data Explorer */}
      <DataExplorer tables={tables || []} />
    </div>
  );
}
