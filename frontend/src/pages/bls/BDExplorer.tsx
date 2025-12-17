import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, ComposedChart, Area
} from 'recharts';
import {
  TrendingUp, TrendingDown, Loader2, Building2, MapPin,
  ArrowUpCircle, ArrowDownCircle, LucideIcon, Factory,
  BarChart3, Activity, Building
} from 'lucide-react';
import { bdResearchAPI } from '../../services/api';

/**
 * BD Explorer - Business Employment Dynamics Explorer
 *
 * BED tracks changes in employment at the establishment level, revealing
 * the dynamics underlying net changes in employment.
 *
 * Key Concepts:
 * - Job Flows: Gains (Openings + Expansions) vs Losses (Closings + Contractions)
 * - Establishment Births/Deaths: New/ceased business establishments
 * - Data available as Levels (thousands) or Rates (percentage)
 *
 * Data Classes:
 * - 01: Gross Job Gains (sum of 02+03)
 * - 02: Expansions (existing establishments hiring)
 * - 03: Openings (new establishments or reopenings)
 * - 04: Gross Job Losses (sum of 05+06)
 * - 05: Contractions (existing establishments reducing staff)
 * - 06: Closings (establishments closing or going out of business)
 * - 07: Establishment Births (new establishments)
 * - 08: Establishment Deaths (ceased establishments)
 *
 * Sections:
 * 1. Overview - Job flow summary metrics
 * 2. State Comparison - Compare states by job flow metrics
 * 3. Industry Comparison - Compare industries by job flow metrics
 * 4. Job Flow Components - Detailed breakdown of gains/losses
 * 5. Establishment Births & Deaths - New vs ceased establishments
 * 6. Top Movers - States/Industries with biggest changes
 * 7. Historical Trends - Long-term analysis
 * 8. Series Explorer - Search, drill-down, browse
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface SelectOption {
  value: string | number;
  label: string;
}

interface TimeRangeOption {
  value: number;
  label: string;
}

interface StateItem {
  state_code: string;
  state_name: string;
}

interface IndustryItem {
  industry_code: string;
  industry_name: string;
  display_level?: number;
  selectable?: string;
}

interface DataClassItem {
  dataclass_code: string;
  dataclass_name: string;
}

interface DataElementItem {
  dataelement_code: string;
  dataelement_name: string;
}

interface SizeClassItem {
  sizeclass_code: string;
  sizeclass_name: string;
}

interface RateLevelItem {
  ratelevel_code: string;
  ratelevel_name: string;
}

interface DimensionsData {
  states: StateItem[];
  industries: IndustryItem[];
  dataclasses: DataClassItem[];
  dataelements: DataElementItem[];
  sizeclasses: SizeClassItem[];
  ratelevels: RateLevelItem[];
  firm_sizeclasses?: SizeClassItem[];
  empchange_sizeclasses?: SizeClassItem[];
}

interface OverviewMetric {
  dataclass_code: string;
  dataclass_name: string;
  level_value?: number | null;
  rate_value?: number | null;
  level_change?: number | null;
  rate_change?: number | null;
  level_yoy_change?: number | null;
  rate_yoy_change?: number | null;
}

interface OverviewData {
  year: number;
  period: string;
  period_name: string;
  state_code: string;
  state_name: string;
  industry_code: string;
  industry_name: string;
  seasonal_code: string;
  metrics: OverviewMetric[];
  available_years: number[];
  available_periods: string[];
}

interface TimelinePoint {
  year: number;
  period: string;
  period_name: string;
  gross_gains_level?: number | null;
  gross_losses_level?: number | null;
  net_change?: number | null;
  gross_gains_rate?: number | null;
  gross_losses_rate?: number | null;
}

interface OverviewTimelineData {
  state_code: string;
  state_name: string;
  industry_code: string;
  industry_name: string;
  data: TimelinePoint[];
}

interface StateComparisonItem {
  state_code: string;
  state_name: string;
  gross_gains_level?: number | null;
  gross_losses_level?: number | null;
  net_change?: number | null;
  gross_gains_rate?: number | null;
  gross_losses_rate?: number | null;
  expansions_level?: number | null;
  contractions_level?: number | null;
  openings_level?: number | null;
  closings_level?: number | null;
  births_level?: number | null;
  deaths_level?: number | null;
}

interface StateComparisonData {
  year: number;
  period: string;
  period_name: string;
  industry_code: string;
  industry_name: string;
  states: StateComparisonItem[];
}

interface StateTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  values: Record<string, number | null>;
}

interface StateTimelineData {
  dataclass_code: string;
  dataclass_name: string;
  ratelevel_code: string;
  states: StateItem[];
  data: StateTimelinePoint[];
}

interface IndustryComparisonItem {
  industry_code: string;
  industry_name: string;
  display_level?: number;
  gross_gains_level?: number | null;
  gross_losses_level?: number | null;
  net_change?: number | null;
  gross_gains_rate?: number | null;
  gross_losses_rate?: number | null;
}

interface IndustryComparisonData {
  year: number;
  period: string;
  period_name: string;
  state_code: string;
  state_name: string;
  industries: IndustryComparisonItem[];
}

interface IndustryTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  values: Record<string, number | null>;
}

interface IndustryTimelineData {
  dataclass_code: string;
  dataclass_name: string;
  ratelevel_code: string;
  industries: IndustryItem[];
  data: IndustryTimelinePoint[];
}

interface JobFlowComponents {
  gross_gains?: number | null;
  expansions?: number | null;
  openings?: number | null;
  gross_losses?: number | null;
  contractions?: number | null;
  closings?: number | null;
  net_change?: number | null;
  births?: number | null;
  deaths?: number | null;
}

interface JobFlowData {
  year: number;
  period: string;
  period_name: string;
  state_code: string;
  state_name: string;
  industry_code: string;
  industry_name: string;
  ratelevel_code: string;
  ratelevel_name: string;
  dataelement_code: string;
  dataelement_name: string;
  components: JobFlowComponents;
}

interface JobFlowTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  gross_gains?: number | null;
  expansions?: number | null;
  openings?: number | null;
  gross_losses?: number | null;
  contractions?: number | null;
  closings?: number | null;
  net_change?: number | null;
}

interface JobFlowTimelineData {
  state_code: string;
  state_name: string;
  industry_code: string;
  industry_name: string;
  data: JobFlowTimelinePoint[];
}

interface BirthsDeathsValues {
  births?: number | null;
  deaths?: number | null;
  net?: number | null;
  birth_rate?: number | null;
  death_rate?: number | null;
}

interface BirthsDeathsData {
  year: number;
  period: string;
  period_name: string;
  state_code: string;
  state_name: string;
  industry_code: string;
  industry_name: string;
  employment: BirthsDeathsValues;
  establishments: BirthsDeathsValues;
}

interface BirthsDeathsTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  births_emp?: number | null;
  deaths_emp?: number | null;
  births_est?: number | null;
  deaths_est?: number | null;
  net_emp?: number | null;
  net_est?: number | null;
}

interface BirthsDeathsTimelineData {
  state_code: string;
  state_name: string;
  industry_code: string;
  industry_name: string;
  data: BirthsDeathsTimelinePoint[];
}

interface TopMoverItem {
  code: string;
  name: string;
  value?: number | null;
  change?: number | null;
  pct_change?: number | null;
}

interface TopMoversData {
  year: number;
  period: string;
  period_name: string;
  metric: string;
  comparison_type: string;
  top_gainers: TopMoverItem[];
  top_losers: TopMoverItem[];
}

interface TrendPoint {
  year: number;
  period: string;
  period_name: string;
  value?: number | null;
  yoy_change?: number | null;
  yoy_pct_change?: number | null;
}

interface TrendData {
  state_code: string;
  state_name: string;
  industry_code: string;
  industry_name: string;
  dataclass_code: string;
  dataclass_name: string;
  ratelevel_code: string;
  ratelevel_name: string;
  data: TrendPoint[];
}

interface SeriesInfo {
  series_id: string;
  seasonal_code?: string;
  state_code?: string;
  state_name?: string;
  industry_code?: string;
  industry_name?: string;
  dataelement_code?: string;
  dataelement_name?: string;
  sizeclass_code?: string;
  sizeclass_name?: string;
  dataclass_code?: string;
  dataclass_name?: string;
  ratelevel_code?: string;
  ratelevel_name?: string;
  periodicity_code?: string;
  series_title?: string;
  begin_year?: number;
  end_year?: number | null;
}

interface SeriesListData {
  series: SeriesInfo[];
  total: number;
}

interface DataPoint {
  year: number;
  period: string;
  period_name: string;
  value: number | null;
}

interface SeriesDataItem {
  series_id: string;
  series_info: SeriesInfo;
  data_points: DataPoint[];
}

interface SeriesDataResponse {
  series: SeriesDataItem[];
}

interface SeriesChartDataMap {
  [seriesId: string]: SeriesDataResponse;
}

type ViewType = 'table' | 'chart';
type SectionColor = 'blue' | 'green' | 'orange' | 'purple' | 'cyan' | 'red' | 'amber' | 'teal';

// ============================================================================
// CONSTANTS
// ============================================================================

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'];

const timeRangeOptions: TimeRangeOption[] = [
  { value: 5, label: 'Last 5 years' },
  { value: 10, label: 'Last 10 years' },
  { value: 15, label: 'Last 15 years' },
  { value: 20, label: 'Last 20 years' },
  { value: 0, label: 'All Time' },
];

const rateLevelOptions: SelectOption[] = [
  { value: 'L', label: 'Level (thousands)' },
  { value: 'R', label: 'Rate (%)' },
];

const dataElementOptions: SelectOption[] = [
  { value: '1', label: 'Employment' },
  { value: '2', label: 'Number of Establishments' },
];

const dataClassOptions: SelectOption[] = [
  { value: '01', label: 'Gross Job Gains' },
  { value: '02', label: 'Expansions' },
  { value: '03', label: 'Openings' },
  { value: '04', label: 'Gross Job Losses' },
  { value: '05', label: 'Contractions' },
  { value: '06', label: 'Closings' },
  { value: '07', label: 'Establishment Births' },
  { value: '08', label: 'Establishment Deaths' },
];

const topMoverMetricOptions: SelectOption[] = [
  { value: 'gross_gains', label: 'Gross Job Gains' },
  { value: 'gross_losses', label: 'Gross Job Losses' },
  { value: 'net_change', label: 'Net Employment Change' },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatNumber = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return value.toLocaleString();
};

const formatRate = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return `${value.toFixed(1)}%`;
};

const formatChange = (value: number | undefined | null, suffix: string = ''): string => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}${suffix}`;
};

// ============================================================================
// REUSABLE COMPONENTS
// ============================================================================

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card = ({ children, className = '' }: CardProps): ReactElement => (
  <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
    {children}
  </div>
);

interface SectionHeaderProps {
  title: string;
  description?: string;
  color?: SectionColor;
  icon?: LucideIcon;
}

const SectionHeader = ({ title, description, color = 'blue', icon: Icon }: SectionHeaderProps): ReactElement => {
  const colorClasses: Record<SectionColor, string> = {
    blue: 'border-blue-500 bg-blue-50 text-blue-700',
    green: 'border-green-500 bg-green-50 text-green-700',
    orange: 'border-orange-500 bg-orange-50 text-orange-700',
    purple: 'border-purple-500 bg-purple-50 text-purple-700',
    cyan: 'border-cyan-500 bg-cyan-50 text-cyan-700',
    red: 'border-red-500 bg-red-50 text-red-700',
    amber: 'border-amber-500 bg-amber-50 text-amber-700',
    teal: 'border-teal-500 bg-teal-50 text-teal-700',
  };
  return (
    <div className={`px-5 py-3 border-b-4 ${colorClasses[color]}`}>
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-5 h-5" />}
        <h2 className="text-xl font-bold">{title}</h2>
      </div>
      {description && (
        <p className="text-sm mt-1 opacity-80">{description}</p>
      )}
    </div>
  );
};

interface SelectProps {
  label?: string;
  value: string | number;
  onChange: (value: string) => void;
  options: SelectOption[];
  className?: string;
}

const Select = ({ label, value, onChange, options, className = '' }: SelectProps): ReactElement => (
  <div className={className}>
    {label && <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>}
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  </div>
);

interface ViewToggleProps {
  value: ViewType;
  onChange: (value: ViewType) => void;
}

const ViewToggle = ({ value, onChange }: ViewToggleProps): ReactElement => (
  <div className="flex border border-gray-300 rounded-md overflow-hidden">
    <button
      onClick={() => onChange('table')}
      className={`px-3 py-1 text-sm ${value === 'table' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
    >
      Table
    </button>
    <button
      onClick={() => onChange('chart')}
      className={`px-3 py-1 text-sm ${value === 'chart' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
    >
      Chart
    </button>
  </div>
);

interface ChangeIndicatorProps {
  value: number | undefined | null;
  suffix?: string;
}

const ChangeIndicator = ({ value, suffix = '' }: ChangeIndicatorProps): ReactElement => {
  if (value === undefined || value === null) {
    return <span className="text-gray-400 text-sm">N/A</span>;
  }
  const isPositive = value > 0;
  const isNegative = value < 0;
  const colorClass = isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500';
  const Icon = isPositive ? TrendingUp : isNegative ? TrendingDown : null;

  return (
    <span className={`flex items-center gap-1 text-sm font-medium ${colorClass}`}>
      {Icon && <Icon className="w-4 h-4" />}
      {formatChange(value, suffix)}
    </span>
  );
};

const LoadingSpinner = (): ReactElement => (
  <div className="flex justify-center items-center py-12">
    <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
  </div>
);

// Metric Card Component
interface MetricCardProps {
  label: string;
  value: number | undefined | null;
  isRate?: boolean;
  change?: number | null;
  colorClass?: string;
}

const MetricCard = ({ label, value, isRate = false, change, colorClass = 'bg-blue-50 text-blue-700' }: MetricCardProps): ReactElement => (
  <div className={`p-4 rounded-lg ${colorClass}`}>
    <div className="text-xs font-medium mb-1 opacity-80">{label}</div>
    <div className="text-2xl font-bold">
      {isRate ? formatRate(value) : formatNumber(value)}
    </div>
    {change !== undefined && change !== null && (
      <div className="mt-1">
        <ChangeIndicator value={change} suffix={isRate ? ' pp' : ''} />
      </div>
    )}
  </div>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function BDExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [, setLoadingDimensions] = useState(true);

  // Section 1: Overview
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [overviewState, setOverviewState] = useState('00');
  const [overviewIndustry, setOverviewIndustry] = useState('000000');
  const [overviewYear, setOverviewYear] = useState<number | undefined>();
  const [overviewPeriod, setOverviewPeriod] = useState<string>('');
  const [overviewTimeRange, setOverviewTimeRange] = useState(10);
  const [overviewView, setOverviewView] = useState<ViewType>('chart');

  // Section 2: State Comparison
  const [stateComparison, setStateComparison] = useState<StateComparisonData | null>(null);
  const [loadingStates, setLoadingStates] = useState(false);
  const [stateTimeline, setStateTimeline] = useState<StateTimelineData | null>(null);
  const [stateIndustry, setStateIndustry] = useState('000000');
  const [stateDataClass, setStateDataClass] = useState('01');
  const [stateRateLevel, setStateRateLevel] = useState('L');
  const [stateTimeRange, setStateTimeRange] = useState(10);
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [stateView, setStateView] = useState<ViewType>('table');

  // Section 3: Industry Comparison
  const [industryComparison, setIndustryComparison] = useState<IndustryComparisonData | null>(null);
  const [loadingIndustries, setLoadingIndustries] = useState(false);
  const [industryTimeline, setIndustryTimeline] = useState<IndustryTimelineData | null>(null);
  const [industryState, setIndustryState] = useState('00');
  const [industryDataClass, setIndustryDataClass] = useState('01');
  const [industryRateLevel, setIndustryRateLevel] = useState('L');
  const [industryTimeRange, setIndustryTimeRange] = useState(10);
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [industryView, setIndustryView] = useState<ViewType>('table');

  // Section 4: Job Flow Components
  const [jobFlow, setJobFlow] = useState<JobFlowData | null>(null);
  const [loadingJobFlow, setLoadingJobFlow] = useState(false);
  const [jobFlowTimeline, setJobFlowTimeline] = useState<JobFlowTimelineData | null>(null);
  const [jobFlowState, setJobFlowState] = useState('00');
  const [jobFlowIndustry, setJobFlowIndustry] = useState('000000');
  const [jobFlowRateLevel, setJobFlowRateLevel] = useState('L');
  const [jobFlowDataElement, setJobFlowDataElement] = useState('1');
  const [jobFlowTimeRange, setJobFlowTimeRange] = useState(10);
  const [jobFlowView, setJobFlowView] = useState<ViewType>('chart');

  // Section 5: Births & Deaths
  const [birthsDeaths, setBirthsDeaths] = useState<BirthsDeathsData | null>(null);
  const [loadingBirthsDeaths, setLoadingBirthsDeaths] = useState(false);
  const [birthsDeathsTimeline, setBirthsDeathsTimeline] = useState<BirthsDeathsTimelineData | null>(null);
  const [bdState, setBdState] = useState('00');
  const [bdIndustry, setBdIndustry] = useState('000000');
  const [bdRateLevel, setBdRateLevel] = useState('L');
  const [bdTimeRange, setBdTimeRange] = useState(10);
  const [bdView, setBdView] = useState<ViewType>('chart');

  // Section 6: Top Movers
  const [topMovers, setTopMovers] = useState<TopMoversData | null>(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(false);
  const [topMoverMetric, setTopMoverMetric] = useState('net_change');
  const [topMoverType, setTopMoverType] = useState('state');

  // Section 7: Historical Trends
  const [trend, setTrend] = useState<TrendData | null>(null);
  const [loadingTrend, setLoadingTrend] = useState(false);
  const [trendState, setTrendState] = useState('00');
  const [trendIndustry, setTrendIndustry] = useState('000000');
  const [trendDataClass, setTrendDataClass] = useState('01');
  const [trendRateLevel, setTrendRateLevel] = useState('L');
  const [trendTimeRange, setTrendTimeRange] = useState(0);
  const [trendView, setTrendView] = useState<ViewType>('chart');

  // Section 8: Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Section 8: Series Explorer - Drill-down
  const [drillState, setDrillState] = useState('');
  const [drillIndustry, setDrillIndustry] = useState('');
  const [drillDataClass, setDrillDataClass] = useState('');
  const [drillDataElement, setDrillDataElement] = useState('');
  const [drillRateLevel, setDrillRateLevel] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);

  // Section 8: Series Explorer - Browse
  const [browseState, setBrowseState] = useState('');
  const [browseIndustry, setBrowseIndustry] = useState('');
  const [browseDataClass, setBrowseDataClass] = useState('');
  const [browseLimit, setBrowseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series Explorer - Shared
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesTimeRange, setSeriesTimeRange] = useState(10);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');
  const [seriesChartData, setSeriesChartData] = useState<SeriesChartDataMap>({});
  const [allSeriesInfo, setAllSeriesInfo] = useState<Record<string, SeriesInfo>>({});

  // ============================================================================
  // DATA LOADING
  // ============================================================================

  // Load dimensions on mount
  useEffect(() => {
    const load = async () => {
      try {
        const res = await bdResearchAPI.getDimensions<DimensionsData>();
        setDimensions(res.data);
      } catch (error) {
        console.error('Failed to load dimensions:', error);
      } finally {
        setLoadingDimensions(false);
      }
    };
    load();
  }, []);

  // Load overview
  useEffect(() => {
    const load = async () => {
      setLoadingOverview(true);
      try {
        const res = await bdResearchAPI.getOverview<OverviewData>(
          overviewState,
          overviewIndustry,
          'S',
          overviewYear,
          overviewPeriod || undefined
        );
        setOverview(res.data);
        // Set initial year/period if not set
        if (!overviewYear && res.data?.year) {
          setOverviewYear(res.data.year);
        }
        if (!overviewPeriod && res.data?.period) {
          setOverviewPeriod(res.data.period);
        }
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [overviewState, overviewIndustry, overviewYear, overviewPeriod]);

  // Load overview timeline
  useEffect(() => {
    const load = async () => {
      try {
        const startYear = overviewTimeRange > 0 ? new Date().getFullYear() - overviewTimeRange : undefined;
        const res = await bdResearchAPI.getOverviewTimeline<OverviewTimelineData>(
          overviewState,
          overviewIndustry,
          'S',
          startYear
        );
        setOverviewTimeline(res.data);
      } catch (error) {
        console.error('Failed to load overview timeline:', error);
      }
    };
    load();
  }, [overviewState, overviewIndustry, overviewTimeRange]);

  // Load state comparison
  useEffect(() => {
    const load = async () => {
      setLoadingStates(true);
      try {
        const res = await bdResearchAPI.getStateComparison<StateComparisonData>(stateIndustry);
        setStateComparison(res.data);
        // Pre-select top 5 states by net change
        if (res.data?.states?.length > 0 && selectedStates.length === 0) {
          const sorted = [...res.data.states].sort((a, b) => Math.abs(b.net_change || 0) - Math.abs(a.net_change || 0));
          setSelectedStates(sorted.slice(0, 5).map(s => s.state_code));
        }
      } catch (error) {
        console.error('Failed to load state comparison:', error);
      } finally {
        setLoadingStates(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stateIndustry]);

  // Load state timeline
  useEffect(() => {
    const load = async () => {
      if (selectedStates.length === 0) {
        setStateTimeline(null);
        return;
      }
      try {
        const startYear = stateTimeRange > 0 ? new Date().getFullYear() - stateTimeRange : undefined;
        const res = await bdResearchAPI.getStateTimeline<StateTimelineData>(
          selectedStates.join(','),
          stateIndustry,
          stateDataClass,
          stateRateLevel,
          'S',
          startYear
        );
        setStateTimeline(res.data);
      } catch (error) {
        console.error('Failed to load state timeline:', error);
      }
    };
    load();
  }, [selectedStates, stateIndustry, stateDataClass, stateRateLevel, stateTimeRange]);

  // Load industry comparison
  useEffect(() => {
    const load = async () => {
      setLoadingIndustries(true);
      try {
        const res = await bdResearchAPI.getIndustryComparison<IndustryComparisonData>(industryState);
        setIndustryComparison(res.data);
        // Pre-select first 5 industries
        if (res.data?.industries?.length > 0 && selectedIndustries.length === 0) {
          setSelectedIndustries(res.data.industries.slice(0, 5).map(i => i.industry_code));
        }
      } catch (error) {
        console.error('Failed to load industry comparison:', error);
      } finally {
        setLoadingIndustries(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [industryState]);

  // Load industry timeline
  useEffect(() => {
    const load = async () => {
      if (selectedIndustries.length === 0) {
        setIndustryTimeline(null);
        return;
      }
      try {
        const startYear = industryTimeRange > 0 ? new Date().getFullYear() - industryTimeRange : undefined;
        const res = await bdResearchAPI.getIndustryTimeline<IndustryTimelineData>(
          selectedIndustries.join(','),
          industryState,
          industryDataClass,
          industryRateLevel,
          'S',
          startYear
        );
        setIndustryTimeline(res.data);
      } catch (error) {
        console.error('Failed to load industry timeline:', error);
      }
    };
    load();
  }, [selectedIndustries, industryState, industryDataClass, industryRateLevel, industryTimeRange]);

  // Load job flow components
  useEffect(() => {
    const load = async () => {
      setLoadingJobFlow(true);
      try {
        const res = await bdResearchAPI.getJobFlow<JobFlowData>(
          jobFlowState,
          jobFlowIndustry,
          'S',
          jobFlowRateLevel,
          jobFlowDataElement
        );
        setJobFlow(res.data);
      } catch (error) {
        console.error('Failed to load job flow:', error);
      } finally {
        setLoadingJobFlow(false);
      }
    };
    load();
  }, [jobFlowState, jobFlowIndustry, jobFlowRateLevel, jobFlowDataElement]);

  // Load job flow timeline
  useEffect(() => {
    const load = async () => {
      try {
        const startYear = jobFlowTimeRange > 0 ? new Date().getFullYear() - jobFlowTimeRange : undefined;
        const res = await bdResearchAPI.getJobFlowTimeline<JobFlowTimelineData>(
          jobFlowState,
          jobFlowIndustry,
          'S',
          jobFlowRateLevel,
          jobFlowDataElement,
          startYear
        );
        setJobFlowTimeline(res.data);
      } catch (error) {
        console.error('Failed to load job flow timeline:', error);
      }
    };
    load();
  }, [jobFlowState, jobFlowIndustry, jobFlowRateLevel, jobFlowDataElement, jobFlowTimeRange]);

  // Load births/deaths
  useEffect(() => {
    const load = async () => {
      setLoadingBirthsDeaths(true);
      try {
        const res = await bdResearchAPI.getBirthsDeaths<BirthsDeathsData>(bdState, bdIndustry);
        setBirthsDeaths(res.data);
      } catch (error) {
        console.error('Failed to load births/deaths:', error);
      } finally {
        setLoadingBirthsDeaths(false);
      }
    };
    load();
  }, [bdState, bdIndustry]);

  // Load births/deaths timeline
  useEffect(() => {
    const load = async () => {
      try {
        const startYear = bdTimeRange > 0 ? new Date().getFullYear() - bdTimeRange : undefined;
        const res = await bdResearchAPI.getBirthsDeathsTimeline<BirthsDeathsTimelineData>(
          bdState,
          bdIndustry,
          'S',
          bdRateLevel,
          startYear
        );
        setBirthsDeathsTimeline(res.data);
      } catch (error) {
        console.error('Failed to load births/deaths timeline:', error);
      }
    };
    load();
  }, [bdState, bdIndustry, bdRateLevel, bdTimeRange]);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await bdResearchAPI.getTopMovers<TopMoversData>(
          topMoverType,
          topMoverMetric,
          'L',
          '1',
          'S',
          10
        );
        setTopMovers(res.data);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [topMoverMetric, topMoverType]);

  // Load historical trend
  useEffect(() => {
    const load = async () => {
      setLoadingTrend(true);
      try {
        const startYear = trendTimeRange > 0 ? new Date().getFullYear() - trendTimeRange : undefined;
        const res = await bdResearchAPI.getTrend<TrendData>(
          trendState,
          trendIndustry,
          trendDataClass,
          trendRateLevel,
          '1',
          'S',
          startYear
        );
        setTrend(res.data);
      } catch (error) {
        console.error('Failed to load trend:', error);
      } finally {
        setLoadingTrend(false);
      }
    };
    load();
  }, [trendState, trendIndustry, trendDataClass, trendRateLevel, trendTimeRange]);

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await bdResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 50 });
      setSearchResults(res.data);
      // Store series info
      const infoMap: Record<string, SeriesInfo> = { ...allSeriesInfo };
      res.data.series.forEach(s => { infoMap[s.series_id] = s; });
      setAllSeriesInfo(infoMap);
    } catch (error) {
      console.error('Failed to search:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleSearchKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  // Drill-down handler
  useEffect(() => {
    const load = async () => {
      if (!drillState && !drillIndustry && !drillDataClass && !drillDataElement && !drillRateLevel) {
        setDrillResults(null);
        return;
      }
      setLoadingDrill(true);
      try {
        const params: Record<string, unknown> = { limit: 100 };
        if (drillState) params.state_code = drillState;
        if (drillIndustry) params.industry_code = drillIndustry;
        if (drillDataClass) params.dataclass_code = drillDataClass;
        if (drillDataElement) params.dataelement_code = drillDataElement;
        if (drillRateLevel) params.ratelevel_code = drillRateLevel;
        const res = await bdResearchAPI.getSeries<SeriesListData>(params);
        setDrillResults(res.data);
        // Store series info
        const infoMap: Record<string, SeriesInfo> = { ...allSeriesInfo };
        res.data.series.forEach(s => { infoMap[s.series_id] = s; });
        setAllSeriesInfo(infoMap);
      } catch (error) {
        console.error('Failed to drill:', error);
      } finally {
        setLoadingDrill(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [drillState, drillIndustry, drillDataClass, drillDataElement, drillRateLevel]);

  // Browse handler
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseState) params.state_code = browseState;
        if (browseIndustry) params.industry_code = browseIndustry;
        if (browseDataClass) params.dataclass_code = browseDataClass;
        const res = await bdResearchAPI.getSeries<SeriesListData>(params);
        setBrowseResults(res.data);
        // Store series info
        const infoMap: Record<string, SeriesInfo> = { ...allSeriesInfo };
        res.data.series.forEach(s => { infoMap[s.series_id] = s; });
        setAllSeriesInfo(infoMap);
      } catch (error) {
        console.error('Failed to browse:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [browseState, browseIndustry, browseDataClass, browseLimit, browseOffset]);

  // Load chart data for selected series
  useEffect(() => {
    const load = async () => {
      const newData: SeriesChartDataMap = { ...seriesChartData };
      for (const seriesId of selectedSeriesIds) {
        if (!newData[seriesId]) {
          try {
            const startYear = seriesTimeRange > 0 ? new Date().getFullYear() - seriesTimeRange : undefined;
            const res = await bdResearchAPI.getData<SeriesDataResponse>(seriesId, startYear);
            newData[seriesId] = res.data;
          } catch (error) {
            console.error(`Failed to load series ${seriesId}:`, error);
          }
        }
      }
      setSeriesChartData(newData);
    };
    if (selectedSeriesIds.length > 0) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSeriesIds, seriesTimeRange]);

  // Toggle series selection
  const toggleSeriesSelection = (seriesId: string) => {
    setSelectedSeriesIds(prev =>
      prev.includes(seriesId)
        ? prev.filter(id => id !== seriesId)
        : prev.length < 5 ? [...prev, seriesId] : prev
    );
  };

  // Build options from dimensions
  const stateOptions: SelectOption[] = [
    { value: '00', label: 'United States (National)' },
    ...(dimensions?.states || [])
      .filter(s => s.state_code !== '00')
      .map(s => ({ value: s.state_code, label: s.state_name }))
  ];

  const industryOptions: SelectOption[] = [
    { value: '000000', label: 'Total Private' },
    ...(dimensions?.industries || [])
      .filter(i => i.industry_code !== '000000' && i.selectable === 'T')
      .map(i => ({ value: i.industry_code, label: i.industry_name }))
  ];

  // Build period options from overview
  const periodOptions: SelectOption[] = (overview?.available_periods || [])
    .map(p => ({ value: p, label: p.replace('Q0', 'Q') }));

  const yearOptions: SelectOption[] = (overview?.available_years || [])
    .sort((a, b) => b - a)
    .map(y => ({ value: y, label: String(y) }));

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">BD Explorer</h1>
          <p className="text-sm text-gray-600 mt-1">
            Business Employment Dynamics - Job flows and establishment births/deaths analysis
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Quarterly data, updated ~6 months after quarter end. Private sector only.
          </p>
        </div>
      </div>

      {/* Section 1: Overview */}
      <Card>
        <SectionHeader
          title="1. Overview - Job Flow Summary"
          description="Key metrics on job gains, losses, and net employment change"
          color="blue"
          icon={Activity}
        />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="State"
              value={overviewState}
              onChange={setOverviewState}
              options={stateOptions}
              className="w-52"
            />
            <Select
              label="Industry"
              value={overviewIndustry}
              onChange={setOverviewIndustry}
              options={industryOptions}
              className="w-52"
            />
            {yearOptions.length > 0 && (
              <Select
                label="Year"
                value={overviewYear || ''}
                onChange={(v) => setOverviewYear(Number(v))}
                options={yearOptions}
                className="w-28"
              />
            )}
            {periodOptions.length > 0 && (
              <Select
                label="Quarter"
                value={overviewPeriod}
                onChange={setOverviewPeriod}
                options={periodOptions}
                className="w-28"
              />
            )}
            <Select
              label="Time Range"
              value={overviewTimeRange}
              onChange={(v) => setOverviewTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-36"
            />
            <div className="flex items-end">
              <ViewToggle value={overviewView} onChange={setOverviewView} />
            </div>
          </div>

          {loadingOverview ? (
            <LoadingSpinner />
          ) : overview ? (
            <>
              {/* Summary Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                {overview.metrics.slice(0, 6).map((m) => {
                  const isGain = ['01', '02', '03', '07'].includes(m.dataclass_code);
                  const isLoss = ['04', '05', '06', '08'].includes(m.dataclass_code);
                  const colorClass = isGain
                    ? 'bg-green-50 text-green-700'
                    : isLoss
                    ? 'bg-red-50 text-red-700'
                    : 'bg-gray-50 text-gray-700';
                  return (
                    <MetricCard
                      key={m.dataclass_code}
                      label={m.dataclass_name}
                      value={m.level_value}
                      change={m.level_yoy_change}
                      colorClass={colorClass}
                    />
                  );
                })}
              </div>

              {/* Period Info */}
              <div className="text-sm text-gray-500 mb-4">
                {overview.period_name} {overview.year} | {overview.state_name} | {overview.industry_name}
              </div>

              {/* Chart or Table */}
              {overviewView === 'chart' && overviewTimeline?.data && overviewTimeline.data.length > 0 ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={overviewTimeline.data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="period_name"
                        tick={{ fontSize: 10 }}
                        tickFormatter={(v) => `${v}`}
                      />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="gross_gains_level" name="Gross Job Gains" fill="#10b981" opacity={0.8} />
                      <Bar dataKey="gross_losses_level" name="Gross Job Losses" fill="#ef4444" opacity={0.8} />
                      <Line type="monotone" dataKey="net_change" name="Net Change" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Period</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gross Gains</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gross Losses</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Net Change</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {overviewTimeline?.data?.slice().reverse().map((d, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-3 py-2">{d.period_name}</td>
                          <td className="px-3 py-2 text-right text-green-600">{formatNumber(d.gross_gains_level)}</td>
                          <td className="px-3 py-2 text-right text-red-600">{formatNumber(d.gross_losses_level)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={d.net_change} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 2: State Comparison */}
      <Card>
        <SectionHeader
          title="2. State Comparison"
          description="Compare job flow metrics across U.S. states"
          color="cyan"
          icon={MapPin}
        />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Industry"
              value={stateIndustry}
              onChange={(v) => { setStateIndustry(v); setSelectedStates([]); }}
              options={industryOptions}
              className="w-52"
            />
            <Select
              label="Data Class"
              value={stateDataClass}
              onChange={setStateDataClass}
              options={dataClassOptions}
              className="w-44"
            />
            <Select
              label="Rate/Level"
              value={stateRateLevel}
              onChange={setStateRateLevel}
              options={rateLevelOptions}
              className="w-40"
            />
            <Select
              label="Time Range"
              value={stateTimeRange}
              onChange={(v) => setStateTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-36"
            />
            <div className="flex items-end">
              <ViewToggle value={stateView} onChange={setStateView} />
            </div>
          </div>

          {loadingStates ? (
            <LoadingSpinner />
          ) : stateComparison ? (
            <>
              {stateView === 'table' ? (
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">State</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gross Gains</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gross Losses</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Net Change</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gain Rate</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Loss Rate</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {stateComparison.states.map((st) => (
                        <tr key={st.state_code} className="hover:bg-gray-50">
                          <td className="px-3 py-2">
                            <input
                              type="checkbox"
                              checked={selectedStates.includes(st.state_code)}
                              onChange={() => {
                                setSelectedStates(prev =>
                                  prev.includes(st.state_code)
                                    ? prev.filter(c => c !== st.state_code)
                                    : [...prev, st.state_code]
                                );
                              }}
                              className="rounded border-gray-300"
                            />
                          </td>
                          <td className="px-3 py-2 font-medium">{st.state_name}</td>
                          <td className="px-3 py-2 text-right text-green-600">{formatNumber(st.gross_gains_level)}</td>
                          <td className="px-3 py-2 text-right text-red-600">{formatNumber(st.gross_losses_level)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={st.net_change} />
                          </td>
                          <td className="px-3 py-2 text-right">{formatRate(st.gross_gains_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(st.gross_losses_rate)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                stateTimeline?.data && stateTimeline.data.length > 0 && selectedStates.length > 0 && (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={stateTimeline.data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        {selectedStates.map((code, idx) => {
                          const stateInfo = stateTimeline.states.find(s => s.state_code === code);
                          return (
                            <Line
                              key={code}
                              type="monotone"
                              dataKey={`values.${code}`}
                              name={stateInfo?.state_name || code}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              dot={false}
                            />
                          );
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 3: Industry Comparison */}
      <Card>
        <SectionHeader
          title="3. Industry Comparison"
          description="Compare job flow metrics across industries"
          color="purple"
          icon={Factory}
        />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="State"
              value={industryState}
              onChange={(v) => { setIndustryState(v); setSelectedIndustries([]); }}
              options={stateOptions}
              className="w-52"
            />
            <Select
              label="Data Class"
              value={industryDataClass}
              onChange={setIndustryDataClass}
              options={dataClassOptions}
              className="w-44"
            />
            <Select
              label="Rate/Level"
              value={industryRateLevel}
              onChange={setIndustryRateLevel}
              options={rateLevelOptions}
              className="w-40"
            />
            <Select
              label="Time Range"
              value={industryTimeRange}
              onChange={(v) => setIndustryTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-36"
            />
            <div className="flex items-end">
              <ViewToggle value={industryView} onChange={setIndustryView} />
            </div>
          </div>

          {loadingIndustries ? (
            <LoadingSpinner />
          ) : industryComparison ? (
            <>
              {industryView === 'table' ? (
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Industry</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gross Gains</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gross Losses</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Net Change</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Gain Rate</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Loss Rate</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {industryComparison.industries.map((ind) => (
                        <tr key={ind.industry_code} className="hover:bg-gray-50">
                          <td className="px-3 py-2">
                            <input
                              type="checkbox"
                              checked={selectedIndustries.includes(ind.industry_code)}
                              onChange={() => {
                                setSelectedIndustries(prev =>
                                  prev.includes(ind.industry_code)
                                    ? prev.filter(c => c !== ind.industry_code)
                                    : [...prev, ind.industry_code]
                                );
                              }}
                              className="rounded border-gray-300"
                            />
                          </td>
                          <td className="px-3 py-2 font-medium" style={{ paddingLeft: `${(ind.display_level || 0) * 12 + 12}px` }}>
                            {ind.industry_name}
                          </td>
                          <td className="px-3 py-2 text-right text-green-600">{formatNumber(ind.gross_gains_level)}</td>
                          <td className="px-3 py-2 text-right text-red-600">{formatNumber(ind.gross_losses_level)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={ind.net_change} />
                          </td>
                          <td className="px-3 py-2 text-right">{formatRate(ind.gross_gains_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(ind.gross_losses_rate)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                industryTimeline?.data && industryTimeline.data.length > 0 && selectedIndustries.length > 0 && (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={industryTimeline.data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        {selectedIndustries.map((code, idx) => {
                          const indInfo = industryTimeline.industries.find(i => i.industry_code === code);
                          return (
                            <Line
                              key={code}
                              type="monotone"
                              dataKey={`values.${code}`}
                              name={indInfo?.industry_name || code}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              dot={false}
                            />
                          );
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 4: Job Flow Components */}
      <Card>
        <SectionHeader
          title="4. Job Flow Components"
          description="Detailed breakdown of job gains and losses by component"
          color="green"
          icon={BarChart3}
        />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="State"
              value={jobFlowState}
              onChange={setJobFlowState}
              options={stateOptions}
              className="w-52"
            />
            <Select
              label="Industry"
              value={jobFlowIndustry}
              onChange={setJobFlowIndustry}
              options={industryOptions}
              className="w-52"
            />
            <Select
              label="Rate/Level"
              value={jobFlowRateLevel}
              onChange={setJobFlowRateLevel}
              options={rateLevelOptions}
              className="w-40"
            />
            <Select
              label="Data Element"
              value={jobFlowDataElement}
              onChange={setJobFlowDataElement}
              options={dataElementOptions}
              className="w-48"
            />
            <Select
              label="Time Range"
              value={jobFlowTimeRange}
              onChange={(v) => setJobFlowTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-36"
            />
            <div className="flex items-end">
              <ViewToggle value={jobFlowView} onChange={setJobFlowView} />
            </div>
          </div>

          {loadingJobFlow ? (
            <LoadingSpinner />
          ) : jobFlow ? (
            <>
              {/* Component Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-xs text-green-600 font-medium mb-1">Gross Gains</div>
                  <div className="text-xl font-bold text-green-700">
                    {jobFlowRateLevel === 'L' ? formatNumber(jobFlow.components.gross_gains) : formatRate(jobFlow.components.gross_gains)}
                  </div>
                  <div className="mt-2 flex justify-between text-xs">
                    <span>Expansions: {formatNumber(jobFlow.components.expansions)}</span>
                    <span>Openings: {formatNumber(jobFlow.components.openings)}</span>
                  </div>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-xs text-red-600 font-medium mb-1">Gross Losses</div>
                  <div className="text-xl font-bold text-red-700">
                    {jobFlowRateLevel === 'L' ? formatNumber(jobFlow.components.gross_losses) : formatRate(jobFlow.components.gross_losses)}
                  </div>
                  <div className="mt-2 flex justify-between text-xs">
                    <span>Contractions: {formatNumber(jobFlow.components.contractions)}</span>
                    <span>Closings: {formatNumber(jobFlow.components.closings)}</span>
                  </div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-xs text-blue-600 font-medium mb-1">Net Change</div>
                  <div className="text-xl font-bold text-blue-700">
                    {jobFlowRateLevel === 'L' ? formatNumber(jobFlow.components.net_change) : formatRate(jobFlow.components.net_change)}
                  </div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-xs text-purple-600 font-medium mb-1">Births/Deaths</div>
                  <div className="text-sm font-bold text-purple-700">
                    <div>Births: {formatNumber(jobFlow.components.births)}</div>
                    <div>Deaths: {formatNumber(jobFlow.components.deaths)}</div>
                  </div>
                </div>
              </div>

              {/* Period Info */}
              <div className="text-sm text-gray-500 mb-4">
                {jobFlow.period_name} {jobFlow.year} | {jobFlow.state_name} | {jobFlow.industry_name} | {jobFlow.dataelement_name}
              </div>

              {/* Chart or Table */}
              {jobFlowView === 'chart' && jobFlowTimeline?.data && jobFlowTimeline.data.length > 0 ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={jobFlowTimeline.data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      <Area type="monotone" dataKey="expansions" name="Expansions" fill="#4ade80" stroke="#22c55e" stackId="gains" />
                      <Area type="monotone" dataKey="openings" name="Openings" fill="#86efac" stroke="#22c55e" stackId="gains" />
                      <Area type="monotone" dataKey="contractions" name="Contractions" fill="#f87171" stroke="#ef4444" stackId="losses" />
                      <Area type="monotone" dataKey="closings" name="Closings" fill="#fca5a5" stroke="#ef4444" stackId="losses" />
                      <Line type="monotone" dataKey="net_change" name="Net Change" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Period</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Expansions</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Openings</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Contractions</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Closings</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Net Change</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {jobFlowTimeline?.data?.slice().reverse().map((d, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-3 py-2">{d.period_name}</td>
                          <td className="px-3 py-2 text-right text-green-600">{formatNumber(d.expansions)}</td>
                          <td className="px-3 py-2 text-right text-green-500">{formatNumber(d.openings)}</td>
                          <td className="px-3 py-2 text-right text-red-600">{formatNumber(d.contractions)}</td>
                          <td className="px-3 py-2 text-right text-red-500">{formatNumber(d.closings)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={d.net_change} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 5: Establishment Births & Deaths */}
      <Card>
        <SectionHeader
          title="5. Establishment Births & Deaths"
          description="New establishment creation vs establishment closures"
          color="orange"
          icon={Building}
        />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="State"
              value={bdState}
              onChange={setBdState}
              options={stateOptions}
              className="w-52"
            />
            <Select
              label="Industry"
              value={bdIndustry}
              onChange={setBdIndustry}
              options={industryOptions}
              className="w-52"
            />
            <Select
              label="Rate/Level"
              value={bdRateLevel}
              onChange={setBdRateLevel}
              options={rateLevelOptions}
              className="w-40"
            />
            <Select
              label="Time Range"
              value={bdTimeRange}
              onChange={(v) => setBdTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-36"
            />
            <div className="flex items-end">
              <ViewToggle value={bdView} onChange={setBdView} />
            </div>
          </div>

          {loadingBirthsDeaths ? (
            <LoadingSpinner />
          ) : birthsDeaths ? (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-xs text-green-600 font-medium mb-1">Establishment Births</div>
                  <div className="text-xl font-bold text-green-700">
                    {formatNumber(birthsDeaths.establishments.births)}
                  </div>
                  <div className="text-xs mt-1">Employment: {formatNumber(birthsDeaths.employment.births)}</div>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-xs text-red-600 font-medium mb-1">Establishment Deaths</div>
                  <div className="text-xl font-bold text-red-700">
                    {formatNumber(birthsDeaths.establishments.deaths)}
                  </div>
                  <div className="text-xs mt-1">Employment: {formatNumber(birthsDeaths.employment.deaths)}</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-xs text-blue-600 font-medium mb-1">Net Establishments</div>
                  <div className="text-xl font-bold text-blue-700">
                    {formatNumber(birthsDeaths.establishments.net)}
                  </div>
                  <div className="text-xs mt-1">Net Employment: {formatNumber(birthsDeaths.employment.net)}</div>
                </div>
              </div>

              {/* Period Info */}
              <div className="text-sm text-gray-500 mb-4">
                {birthsDeaths.period_name} {birthsDeaths.year} | {birthsDeaths.state_name} | {birthsDeaths.industry_name}
              </div>

              {/* Chart or Table */}
              {bdView === 'chart' && birthsDeathsTimeline?.data && birthsDeathsTimeline.data.length > 0 ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={birthsDeathsTimeline.data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="births_est" name="Establishment Births" fill="#10b981" />
                      <Bar dataKey="deaths_est" name="Establishment Deaths" fill="#ef4444" />
                      <Line type="monotone" dataKey="net_est" name="Net Establishments" stroke="#3b82f6" strokeWidth={2} dot={false} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Period</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Est. Births</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Est. Deaths</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Net Est.</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Emp. Births</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Emp. Deaths</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Net Emp.</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {birthsDeathsTimeline?.data?.slice().reverse().map((d, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-3 py-2">{d.period_name}</td>
                          <td className="px-3 py-2 text-right text-green-600">{formatNumber(d.births_est)}</td>
                          <td className="px-3 py-2 text-right text-red-600">{formatNumber(d.deaths_est)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={d.net_est} />
                          </td>
                          <td className="px-3 py-2 text-right text-green-600">{formatNumber(d.births_emp)}</td>
                          <td className="px-3 py-2 text-right text-red-600">{formatNumber(d.deaths_emp)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={d.net_emp} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 6: Top Movers */}
      <Card>
        <SectionHeader
          title="6. Top Movers"
          description="States and industries with the largest employment changes"
          color="red"
          icon={TrendingUp}
        />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Metric"
              value={topMoverMetric}
              onChange={setTopMoverMetric}
              options={topMoverMetricOptions}
              className="w-48"
            />
            <Select
              label="Compare By"
              value={topMoverType}
              onChange={setTopMoverType}
              options={[
                { value: 'state', label: 'States' },
                { value: 'industry', label: 'Industries' },
              ]}
              className="w-36"
            />
          </div>

          {loadingTopMovers ? (
            <LoadingSpinner />
          ) : topMovers ? (
            <div className="grid md:grid-cols-2 gap-6">
              {/* Top Gainers */}
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold text-green-700 mb-3">
                  <ArrowUpCircle className="w-5 h-5" />
                  Top Gainers
                </h3>
                <div className="space-y-2">
                  {topMovers.top_gainers.map((m, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-800 truncate">{m.name}</div>
                        <div className="text-xs text-gray-500">
                          Value: {formatNumber(m.value)}
                        </div>
                      </div>
                      <div className="text-green-600 font-semibold">
                        +{m.pct_change?.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                  {topMovers.top_gainers.length === 0 && (
                    <div className="text-gray-500 text-center py-4">No gainers</div>
                  )}
                </div>
              </div>

              {/* Top Losers */}
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold text-red-700 mb-3">
                  <ArrowDownCircle className="w-5 h-5" />
                  Top Losers
                </h3>
                <div className="space-y-2">
                  {topMovers.top_losers.map((m, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-800 truncate">{m.name}</div>
                        <div className="text-xs text-gray-500">
                          Value: {formatNumber(m.value)}
                        </div>
                      </div>
                      <div className="text-red-600 font-semibold">
                        {m.pct_change?.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                  {topMovers.top_losers.length === 0 && (
                    <div className="text-gray-500 text-center py-4">No losers</div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 7: Historical Trends */}
      <Card>
        <SectionHeader
          title="7. Historical Trends"
          description="Long-term analysis with year-over-year changes"
          color="teal"
          icon={TrendingUp}
        />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="State"
              value={trendState}
              onChange={setTrendState}
              options={stateOptions}
              className="w-52"
            />
            <Select
              label="Industry"
              value={trendIndustry}
              onChange={setTrendIndustry}
              options={industryOptions}
              className="w-52"
            />
            <Select
              label="Data Class"
              value={trendDataClass}
              onChange={setTrendDataClass}
              options={dataClassOptions}
              className="w-44"
            />
            <Select
              label="Rate/Level"
              value={trendRateLevel}
              onChange={setTrendRateLevel}
              options={rateLevelOptions}
              className="w-40"
            />
            <Select
              label="Time Range"
              value={trendTimeRange}
              onChange={(v) => setTrendTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-36"
            />
            <div className="flex items-end">
              <ViewToggle value={trendView} onChange={setTrendView} />
            </div>
          </div>

          {loadingTrend ? (
            <LoadingSpinner />
          ) : trend ? (
            <>
              {/* Trend Info */}
              <div className="text-sm text-gray-500 mb-4">
                {trend.state_name} | {trend.industry_name} | {trend.dataclass_name} ({trend.ratelevel_name})
              </div>

              {trendView === 'chart' && trend.data && trend.data.length > 0 ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={trend.data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                      <YAxis yAxisId="left" tick={{ fontSize: 10 }} />
                      <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      <Bar yAxisId="left" dataKey="value" name={trend.dataclass_name} fill="#3b82f6" opacity={0.7} />
                      <Line yAxisId="right" type="monotone" dataKey="yoy_pct_change" name="YoY % Change" stroke="#f59e0b" strokeWidth={2} dot={false} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Period</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Value</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">YoY Change</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">YoY % Change</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {trend.data?.slice().reverse().map((d, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-3 py-2">{d.period_name}</td>
                          <td className="px-3 py-2 text-right">
                            {trendRateLevel === 'L' ? formatNumber(d.value) : formatRate(d.value)}
                          </td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={d.yoy_change} />
                          </td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={d.yoy_pct_change} suffix="%" />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 8: Series Explorer */}
      <Card>
        <SectionHeader
          title="8. Series Explorer"
          description="Search, drill-down, and browse all BD data series"
          color="amber"
          icon={Building2}
        />
        <div className="p-5 space-y-8">
          {/* Sub-section A: Search by Keyword */}
          <div className="border border-cyan-200 rounded-lg overflow-hidden">
            <div className="bg-gradient-to-r from-cyan-50 to-cyan-100 px-4 py-3 border-b border-cyan-200">
              <h3 className="text-lg font-semibold text-cyan-800">
                Search by Keyword
              </h3>
              <p className="text-xs text-cyan-600 mt-1">
                Find series by state name, industry, or data class
              </p>
            </div>
            <div className="p-4">
              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  placeholder="Search by state, industry, or data class name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearchKeyDown}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={loadingSearch}
                  className="px-4 py-2 bg-cyan-600 text-white rounded-md text-sm hover:bg-cyan-700 disabled:opacity-50"
                >
                  {loadingSearch ? 'Searching...' : 'Search'}
                </button>
              </div>
              {searchResults && (
                <div className="max-h-64 overflow-y-auto border rounded-md">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left">Select</th>
                        <th className="px-3 py-2 text-left">Series ID</th>
                        <th className="px-3 py-2 text-left">State</th>
                        <th className="px-3 py-2 text-left">Industry</th>
                        <th className="px-3 py-2 text-left">Data Class</th>
                        <th className="px-3 py-2 text-left">Type</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {searchResults.series.map((s) => (
                        <tr key={s.series_id} className="hover:bg-gray-50">
                          <td className="px-3 py-2">
                            <input
                              type="checkbox"
                              checked={selectedSeriesIds.includes(s.series_id)}
                              onChange={() => toggleSeriesSelection(s.series_id)}
                              className="rounded"
                            />
                          </td>
                          <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                          <td className="px-3 py-2">{s.state_name}</td>
                          <td className="px-3 py-2 truncate max-w-32">{s.industry_name}</td>
                          <td className="px-3 py-2">{s.dataclass_name}</td>
                          <td className="px-3 py-2 text-xs">{s.ratelevel_name}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Sub-section B: Hierarchical Drill-down */}
          <div className="border border-green-200 rounded-lg overflow-hidden">
            <div className="bg-gradient-to-r from-green-50 to-green-100 px-4 py-3 border-b border-green-200">
              <h3 className="text-lg font-semibold text-green-800">
                Hierarchical Drill-down
              </h3>
              <p className="text-xs text-green-600 mt-1">
                Filter series by selecting dimensions step by step
              </p>
            </div>
            <div className="p-4">
              <div className="flex flex-wrap gap-4 mb-4">
                <Select
                  label="State"
                  value={drillState}
                  onChange={setDrillState}
                  options={[{ value: '', label: 'All States' }, ...stateOptions]}
                  className="w-48"
                />
                <Select
                  label="Industry"
                  value={drillIndustry}
                  onChange={setDrillIndustry}
                  options={[{ value: '', label: 'All Industries' }, ...industryOptions]}
                  className="w-48"
                />
                <Select
                  label="Data Class"
                  value={drillDataClass}
                  onChange={setDrillDataClass}
                  options={[{ value: '', label: 'All Classes' }, ...dataClassOptions]}
                  className="w-40"
                />
                <Select
                  label="Data Element"
                  value={drillDataElement}
                  onChange={setDrillDataElement}
                  options={[{ value: '', label: 'All Elements' }, ...dataElementOptions]}
                  className="w-44"
                />
                <Select
                  label="Rate/Level"
                  value={drillRateLevel}
                  onChange={setDrillRateLevel}
                  options={[{ value: '', label: 'All' }, ...rateLevelOptions]}
                  className="w-36"
                />
              </div>
              {loadingDrill ? (
                <LoadingSpinner />
              ) : drillResults && drillResults.series.length > 0 ? (
                <div className="max-h-64 overflow-y-auto border rounded-md">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left">Select</th>
                        <th className="px-3 py-2 text-left">Series ID</th>
                        <th className="px-3 py-2 text-left">State</th>
                        <th className="px-3 py-2 text-left">Industry</th>
                        <th className="px-3 py-2 text-left">Data Class</th>
                        <th className="px-3 py-2 text-left">Type</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {drillResults.series.map((s) => (
                        <tr key={s.series_id} className="hover:bg-gray-50">
                          <td className="px-3 py-2">
                            <input
                              type="checkbox"
                              checked={selectedSeriesIds.includes(s.series_id)}
                              onChange={() => toggleSeriesSelection(s.series_id)}
                              className="rounded"
                            />
                          </td>
                          <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                          <td className="px-3 py-2">{s.state_name}</td>
                          <td className="px-3 py-2 truncate max-w-32">{s.industry_name}</td>
                          <td className="px-3 py-2">{s.dataclass_name}</td>
                          <td className="px-3 py-2 text-xs">{s.ratelevel_name}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : drillResults ? (
                <div className="text-gray-500 text-center py-4">No series found</div>
              ) : null}
            </div>
          </div>

          {/* Sub-section C: Browse All Series */}
          <div className="border border-purple-200 rounded-lg overflow-hidden">
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 px-4 py-3 border-b border-purple-200">
              <h3 className="text-lg font-semibold text-purple-800">
                Browse All Series
              </h3>
              <p className="text-xs text-purple-600 mt-1">
                Paginated view of all available BD series with optional filters
              </p>
            </div>
            <div className="p-4">
              <div className="flex flex-wrap gap-4 mb-4">
                <Select
                  label="State"
                  value={browseState}
                  onChange={(v) => { setBrowseState(v); setBrowseOffset(0); }}
                  options={[{ value: '', label: 'All States' }, ...stateOptions]}
                  className="w-48"
                />
                <Select
                  label="Industry"
                  value={browseIndustry}
                  onChange={(v) => { setBrowseIndustry(v); setBrowseOffset(0); }}
                  options={[{ value: '', label: 'All Industries' }, ...industryOptions]}
                  className="w-48"
                />
                <Select
                  label="Data Class"
                  value={browseDataClass}
                  onChange={(v) => { setBrowseDataClass(v); setBrowseOffset(0); }}
                  options={[{ value: '', label: 'All Classes' }, ...dataClassOptions]}
                  className="w-40"
                />
                <Select
                  label="Per Page"
                  value={browseLimit}
                  onChange={(v) => { setBrowseLimit(Number(v)); setBrowseOffset(0); }}
                  options={[
                    { value: 25, label: '25' },
                    { value: 50, label: '50' },
                    { value: 100, label: '100' },
                  ]}
                  className="w-24"
                />
              </div>
              {loadingBrowse ? (
                <LoadingSpinner />
              ) : browseResults ? (
                <>
                  <div className="max-h-[400px] overflow-y-auto border rounded-md">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left">Select</th>
                          <th className="px-3 py-2 text-left">Series ID</th>
                          <th className="px-3 py-2 text-left">State</th>
                          <th className="px-3 py-2 text-left">Industry</th>
                          <th className="px-3 py-2 text-left">Data Class</th>
                          <th className="px-3 py-2 text-left">Type</th>
                          <th className="px-3 py-2 text-left">Period</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {browseResults.series.map((s) => (
                          <tr key={s.series_id} className="hover:bg-gray-50">
                            <td className="px-3 py-2">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(s.series_id)}
                                onChange={() => toggleSeriesSelection(s.series_id)}
                                className="rounded"
                              />
                            </td>
                            <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                            <td className="px-3 py-2">{s.state_name}</td>
                            <td className="px-3 py-2 truncate max-w-32">{s.industry_name}</td>
                            <td className="px-3 py-2">{s.dataclass_name}</td>
                            <td className="px-3 py-2 text-xs">{s.ratelevel_name}</td>
                            <td className="px-3 py-2 text-xs text-gray-500">
                              {s.begin_year} - {s.end_year || 'present'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="flex justify-between items-center mt-4">
                    <span className="text-sm text-gray-600">
                      Showing {browseOffset + 1} - {Math.min(browseOffset + browseLimit, browseResults.total)} of {browseResults.total}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setBrowseOffset(Math.max(0, browseOffset - browseLimit))}
                        disabled={browseOffset === 0}
                        className="px-3 py-1 border rounded text-sm disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setBrowseOffset(browseOffset + browseLimit)}
                        disabled={browseOffset + browseLimit >= browseResults.total}
                        className="px-3 py-1 border rounded text-sm disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          </div>

          {/* Selected Series Chart */}
          {selectedSeriesIds.length > 0 && (
            <div className="border-t pt-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  Selected Series ({selectedSeriesIds.length}/5)
                </h3>
                <div className="flex gap-4">
                  <Select
                    label="Time Range"
                    value={seriesTimeRange}
                    onChange={(v) => setSeriesTimeRange(Number(v))}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <div className="flex items-end">
                    <ViewToggle value={seriesView} onChange={setSeriesView} />
                  </div>
                  <button
                    onClick={() => setSelectedSeriesIds([])}
                    className="self-end px-3 py-1.5 text-sm text-red-600 border border-red-300 rounded hover:bg-red-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>

              {seriesView === 'chart' ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="period_name"
                        tick={{ fontSize: 10 }}
                        allowDuplicatedCategory={false}
                      />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      {selectedSeriesIds.map((seriesId, idx) => {
                        const chartData = seriesChartData[seriesId]?.series?.[0]?.data_points;
                        const info = allSeriesInfo[seriesId];
                        if (!chartData) return null;
                        return (
                          <Line
                            key={seriesId}
                            data={chartData}
                            type="monotone"
                            dataKey="value"
                            name={info ? `${info.state_name} - ${info.dataclass_name}` : seriesId}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            dot={false}
                          />
                        );
                      })}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-96 overflow-y-auto border rounded-md">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left">Period</th>
                        {selectedSeriesIds.map((seriesId) => {
                          const info = allSeriesInfo[seriesId];
                          return (
                            <th key={seriesId} className="px-3 py-2 text-right">
                              {info ? `${info.state_name} - ${info.dataclass_name}` : seriesId}
                            </th>
                          );
                        })}
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {/* Get union of all periods */}
                      {(() => {
                        const allPeriods: Record<string, Record<string, number | null>> = {};
                        selectedSeriesIds.forEach((seriesId) => {
                          const points = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                          points.forEach((p) => {
                            const key = p.period_name;
                            if (!allPeriods[key]) allPeriods[key] = {};
                            allPeriods[key][seriesId] = p.value;
                          });
                        });
                        return Object.entries(allPeriods)
                          .sort((a, b) => b[0].localeCompare(a[0]))
                          .slice(0, 40)
                          .map(([period, values]) => (
                            <tr key={period} className="hover:bg-gray-50">
                              <td className="px-3 py-2">{period}</td>
                              {selectedSeriesIds.map((seriesId) => (
                                <td key={seriesId} className="px-3 py-2 text-right">
                                  {values[seriesId]?.toLocaleString() ?? 'N/A'}
                                </td>
                              ))}
                            </tr>
                          ));
                      })()}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
