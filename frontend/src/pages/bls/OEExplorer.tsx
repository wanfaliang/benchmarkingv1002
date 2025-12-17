import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, Users, DollarSign, MapPin, Building2, ArrowUpCircle, ArrowDownCircle, LucideIcon, Briefcase } from 'lucide-react';
import { oeResearchAPI } from '../../services/api';

/**
 * OE Explorer - Occupational Employment and Wage Statistics Explorer
 *
 * OEWS provides employment and wage estimates for ~800 occupations by:
 * - Geographic area (National, State, Metropolitan/Nonmetropolitan)
 * - Industry (450+ NAICS-based industries at national level)
 * - Occupation (SOC-based classification)
 *
 * Data Types Available:
 * - Employment, Employment per 1,000 jobs, Location Quotient
 * - Hourly/Annual mean wages
 * - Wage percentiles (10th, 25th, 50th/median, 75th, 90th)
 *
 * Data available annually, updated in March.
 *
 * Sections:
 * 1. Overview - Summary by major occupation groups
 * 2. Occupation Analysis - Detailed occupation metrics
 * 3. State Comparison - Compare wages/employment across states
 * 4. Industry Analysis - Wages by industry (national)
 * 5. Top Rankings - Highest paying, most employed
 * 6. Top Movers - Year-over-year changes
 * 7. Wage Distribution - Wage percentile chart
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

interface MajorGroupSummary {
  occupation_code: string;
  occupation_name: string;
  employment?: number | null;
  annual_mean?: number | null;
  hourly_mean?: number | null;
  employment_pct_of_total?: number | null;
  yoy_employment_change?: number | null;
  yoy_wage_change?: number | null;
}

interface OverviewData {
  area_code?: string;
  area_name?: string;
  total_employment?: number | null;
  mean_annual_wage?: number | null;
  median_annual_wage?: number | null;
  latest_year?: number | null;
  major_groups: MajorGroupSummary[];
}

interface TimelinePoint {
  year: number;
  major_groups?: Record<string, number | null>;
  occupations?: Record<string, number | null>;
  states?: Record<string, number | null>;
  industries?: Record<string, number | null>;
}

interface OverviewTimelineData {
  datatype: string;
  timeline: TimelinePoint[];
  group_names: Record<string, string>;
}

interface OccupationMetric {
  occupation_code: string;
  occupation_name: string;
  display_level?: number;
  employment?: number | null;
  employment_per_1000?: number | null;
  location_quotient?: number | null;
  hourly_mean?: number | null;
  hourly_median?: number | null;
  annual_mean?: number | null;
  annual_median?: number | null;
  yoy_employment_pct?: number | null;
  yoy_wage_pct?: number | null;
  latest_year?: number | null;
}

interface OccupationAnalysisData {
  area_code?: string;
  area_name?: string;
  industry_code?: string;
  industry_name?: string;
  occupations: OccupationMetric[];
  total_count: number;
  latest_year?: number | null;
}

interface OccupationTimelineData {
  datatype: string;
  timeline: TimelinePoint[];
  occupation_names: Record<string, string>;
}

interface StateMetric {
  state_code: string;
  state_name: string;
  employment?: number | null;
  employment_per_1000?: number | null;
  location_quotient?: number | null;
  hourly_mean?: number | null;
  annual_mean?: number | null;
  latest_year?: number | null;
}

interface StateComparisonData {
  occupation_code?: string;
  occupation_name?: string;
  states: StateMetric[];
  latest_year?: number | null;
}

interface StateTimelineData {
  occupation_code?: string;
  occupation_name?: string;
  datatype: string;
  timeline: TimelinePoint[];
  state_names: Record<string, string>;
}

interface IndustryMetric {
  industry_code: string;
  industry_name: string;
  sector_code?: string;
  sector_name?: string;
  display_level?: number;
  employment?: number | null;
  employment_per_1000?: number | null;
  location_quotient?: number | null;
  hourly_mean?: number | null;
  annual_mean?: number | null;
  annual_median?: number | null;
  yoy_employment_pct?: number | null;
  yoy_wage_pct?: number | null;
  latest_year?: number | null;
}

interface IndustryAnalysisData {
  occupation_code?: string;
  occupation_name?: string;
  industries: IndustryMetric[];
  total_count: number;
  latest_year?: number | null;
}

interface IndustryTimelineData {
  occupation_code?: string;
  occupation_name?: string;
  datatype: string;
  timeline: TimelinePoint[];
  industry_names: Record<string, string>;
}

interface TopOccupation {
  occupation_code: string;
  occupation_name: string;
  area_code?: string;
  area_name?: string;
  value?: number | null;
  rank: number;
}

interface TopRankingsData {
  area_code?: string;
  area_name?: string;
  ranking_type: string;
  occupations: TopOccupation[];
  latest_year?: number | null;
}

interface TopMover {
  occupation_code: string;
  occupation_name: string;
  area_code?: string;
  area_name?: string;
  value?: number | null;
  prev_value?: number | null;
  change?: number | null;
  change_pct?: number | null;
  latest_year?: number | null;
}

interface TopMoversData {
  area_code?: string;
  area_name?: string;
  metric: string;
  gainers: TopMover[];
  losers: TopMover[];
  latest_year?: number | null;
}

interface WageDistribution {
  occupation_code: string;
  occupation_name: string;
  area_code: string;
  area_name: string;
  latest_year?: number | null;
  hourly_10th?: number | null;
  hourly_25th?: number | null;
  hourly_median?: number | null;
  hourly_75th?: number | null;
  hourly_90th?: number | null;
  hourly_mean?: number | null;
  annual_10th?: number | null;
  annual_25th?: number | null;
  annual_median?: number | null;
  annual_75th?: number | null;
  annual_90th?: number | null;
  annual_mean?: number | null;
}

interface WageDistributionData {
  distributions: WageDistribution[];
}

interface OccupationItem {
  occupation_code: string;
  occupation_name: string;
  occupation_description?: string;
  display_level?: number;
  selectable?: boolean;
}

interface SectorItem {
  sector_code: string;
  sector_name: string;
}

interface AreaItem {
  state_code: string;
  area_code: string;
  areatype_code: string;
  area_name: string;
}

interface DataTypeItem {
  datatype_code: string;
  datatype_name: string;
}

interface DimensionsData {
  occupations: OccupationItem[];
  sectors: SectorItem[];
  states: AreaItem[];
  data_types: DataTypeItem[];
}

interface SeriesInfo {
  series_id: string;
  seasonal?: string;
  areatype_code?: string;
  areatype_name?: string;
  state_code?: string;
  area_code?: string;
  area_name?: string;
  sector_code?: string;
  sector_name?: string;
  industry_code?: string;
  industry_name?: string;
  occupation_code?: string;
  occupation_name?: string;
  datatype_code?: string;
  datatype_name?: string;
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
  value: number;
}

interface SeriesDataItem {
  series_id: string;
  occupation_name?: string;
  area_name?: string;
  industry_name?: string;
  datatype_name?: string;
  data_points: DataPoint[];
}

interface SeriesDataResponse {
  series: SeriesDataItem[];
}

interface SeriesChartDataMap {
  [seriesId: string]: SeriesDataResponse;
}

type ViewType = 'table' | 'chart';
type SectionColor = 'blue' | 'green' | 'orange' | 'purple' | 'cyan' | 'red';
type MoverMetric = 'employment' | 'annual_mean';

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

const dataTypeOptions: SelectOption[] = [
  { value: 'employment', label: 'Employment' },
  { value: 'annual_mean', label: 'Annual Mean Wage' },
  { value: 'hourly_mean', label: 'Hourly Mean Wage' },
  { value: 'location_quotient', label: 'Location Quotient' },
];

const rankingTypeOptions: SelectOption[] = [
  { value: 'highest_paying', label: 'Highest Paying' },
  { value: 'most_employed', label: 'Most Employed' },
  { value: 'highest_lq', label: 'Highest Location Quotient' },
];

// Major occupation groups (2-digit SOC codes)
const majorOccupationGroups: SelectOption[] = [
  { value: '110000', label: 'Management' },
  { value: '130000', label: 'Business and Financial' },
  { value: '150000', label: 'Computer and Mathematical' },
  { value: '170000', label: 'Architecture and Engineering' },
  { value: '190000', label: 'Life, Physical, and Social Science' },
  { value: '210000', label: 'Community and Social Service' },
  { value: '230000', label: 'Legal' },
  { value: '250000', label: 'Educational Instruction and Library' },
  { value: '270000', label: 'Arts, Design, Entertainment, Sports, Media' },
  { value: '290000', label: 'Healthcare Practitioners and Technical' },
  { value: '310000', label: 'Healthcare Support' },
  { value: '330000', label: 'Protective Service' },
  { value: '350000', label: 'Food Preparation and Serving' },
  { value: '370000', label: 'Building and Grounds Cleaning and Maintenance' },
  { value: '390000', label: 'Personal Care and Service' },
  { value: '410000', label: 'Sales and Related' },
  { value: '430000', label: 'Office and Administrative Support' },
  { value: '450000', label: 'Farming, Fishing, and Forestry' },
  { value: '470000', label: 'Construction and Extraction' },
  { value: '490000', label: 'Installation, Maintenance, and Repair' },
  { value: '510000', label: 'Production' },
  { value: '530000', label: 'Transportation and Material Moving' },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatNumber = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return value.toLocaleString();
};

const formatWage = (value: number | undefined | null, isHourly: boolean = false): string => {
  if (value === undefined || value === null) return 'N/A';
  const formatted = value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: isHourly ? 2 : 0 });
  return formatted;
};

const formatLQ = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return value.toFixed(2);
};

const formatChange = (value: number | undefined | null, suffix: string = ''): string => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}${suffix}`;
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
  color?: SectionColor;
  icon?: LucideIcon;
}

const SectionHeader = ({ title, color = 'blue', icon: Icon }: SectionHeaderProps): ReactElement => {
  const colorClasses: Record<SectionColor, string> = {
    blue: 'border-blue-500 bg-blue-50 text-blue-700',
    green: 'border-green-500 bg-green-50 text-green-700',
    orange: 'border-orange-500 bg-orange-50 text-orange-700',
    purple: 'border-purple-500 bg-purple-50 text-purple-700',
    cyan: 'border-cyan-500 bg-cyan-50 text-cyan-700',
    red: 'border-red-500 bg-red-50 text-red-700',
  };
  return (
    <div className={`px-5 py-3 border-b-4 ${colorClasses[color]} flex items-center gap-2`}>
      {Icon && <Icon className="w-5 h-5" />}
      <h2 className="text-xl font-bold">{title}</h2>
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

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function OEExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [, setLoadingDimensions] = useState(true);

  // Overview
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [overviewTimeRange, setOverviewTimeRange] = useState(10);
  const [overviewDataType, setOverviewDataType] = useState('employment');
  const [selectedMajorGroups, setSelectedMajorGroups] = useState<string[]>([]);

  // Occupation Analysis
  const [occupations, setOccupations] = useState<OccupationAnalysisData | null>(null);
  const [loadingOccupations, setLoadingOccupations] = useState(true);
  const [occupationMajorGroup, setOccupationMajorGroup] = useState('');
  const [occupationTimeline, setOccupationTimeline] = useState<OccupationTimelineData | null>(null);
  const [occupationTimeRange, setOccupationTimeRange] = useState(10);
  const [occupationDataType, setOccupationDataType] = useState('annual_mean');
  const [selectedOccupations, setSelectedOccupations] = useState<string[]>([]);
  const [occupationView, setOccupationView] = useState<ViewType>('table');

  // State Comparison
  const [states, setStates] = useState<StateComparisonData | null>(null);
  const [loadingStates, setLoadingStates] = useState(false);
  const [stateOccupation, setStateOccupation] = useState('000000');
  const [stateTimeline, setStateTimeline] = useState<StateTimelineData | null>(null);
  const [stateTimeRange, setStateTimeRange] = useState(10);
  const [stateDataType, setStateDataType] = useState('annual_mean');
  const [selectedStates, setSelectedStates] = useState<string[]>([]);
  const [stateView, setStateView] = useState<ViewType>('table');

  // Industry Analysis
  const [industries, setIndustries] = useState<IndustryAnalysisData | null>(null);
  const [loadingIndustries, setLoadingIndustries] = useState(false);
  const [industryOccupation, setIndustryOccupation] = useState('000000');
  const [industrySector, setIndustrySector] = useState('');
  const [industryTimeline, setIndustryTimeline] = useState<IndustryTimelineData | null>(null);
  const [industryTimeRange, setIndustryTimeRange] = useState(10);
  const [industryDataType, setIndustryDataType] = useState('annual_mean');
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [industryView, setIndustryView] = useState<ViewType>('table');

  // Top Rankings
  const [topRankings, setTopRankings] = useState<TopRankingsData | null>(null);
  const [loadingTopRankings, setLoadingTopRankings] = useState(true);
  const [rankingType, setRankingType] = useState('highest_paying');

  // Top Movers
  const [topMovers, setTopMovers] = useState<TopMoversData | null>(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(true);
  const [moverMetric, setMoverMetric] = useState<MoverMetric>('annual_mean');

  // Wage Distribution
  const [wageDistribution, setWageDistribution] = useState<WageDistributionData | null>(null);
  const [loadingWageDistribution, setLoadingWageDistribution] = useState(false);
  const [wageOccupation, setWageOccupation] = useState('');

  // Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Series Explorer - Drill-down
  const [drillOccupation, setDrillOccupation] = useState('');
  const [drillState, setDrillState] = useState('');
  const [drillDataType, setDrillDataType] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);

  // Series Explorer - Browse
  const [browseOccupation, setBrowseOccupation] = useState('');
  const [browseState, setBrowseState] = useState('');
  const [browseDataType, setBrowseDataType] = useState('');
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
        const res = await oeResearchAPI.getDimensions<DimensionsData>();
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
        const res = await oeResearchAPI.getOverview<OverviewData>('0000000');
        setOverview(res.data);
        // Pre-select first 5 major groups
        if (res.data?.major_groups?.length > 0 && selectedMajorGroups.length === 0) {
          setSelectedMajorGroups(res.data.major_groups.slice(0, 5).map(g => g.occupation_code));
        }
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load overview timeline
  useEffect(() => {
    const load = async () => {
      if (selectedMajorGroups.length === 0) return;
      try {
        const res = await oeResearchAPI.getOverviewTimeline<OverviewTimelineData>(
          '0000000',
          overviewDataType,
          overviewTimeRange
        );
        setOverviewTimeline(res.data);
      } catch (error) {
        console.error('Failed to load overview timeline:', error);
      }
    };
    load();
  }, [selectedMajorGroups, overviewDataType, overviewTimeRange]);

  // Load occupation analysis
  useEffect(() => {
    const load = async () => {
      setLoadingOccupations(true);
      try {
        const res = await oeResearchAPI.getOccupations<OccupationAnalysisData>(
          '0000000',
          '000000',
          occupationMajorGroup || null,
          100
        );
        setOccupations(res.data);
        // Pre-select first 3 occupations
        if (res.data?.occupations?.length > 0 && selectedOccupations.length === 0) {
          setSelectedOccupations(res.data.occupations.slice(0, 3).map(o => o.occupation_code));
        }
      } catch (error) {
        console.error('Failed to load occupations:', error);
      } finally {
        setLoadingOccupations(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [occupationMajorGroup]);

  // Load occupation timeline
  useEffect(() => {
    const load = async () => {
      if (selectedOccupations.length === 0) {
        setOccupationTimeline(null);
        return;
      }
      try {
        const res = await oeResearchAPI.getOccupationsTimeline<OccupationTimelineData>(
          '0000000',
          '000000',
          occupationDataType,
          selectedOccupations.join(','),
          occupationTimeRange
        );
        setOccupationTimeline(res.data);
      } catch (error) {
        console.error('Failed to load occupation timeline:', error);
      }
    };
    load();
  }, [selectedOccupations, occupationDataType, occupationTimeRange]);

  // Load state comparison
  useEffect(() => {
    const load = async () => {
      if (!stateOccupation || stateOccupation === '000000') {
        setStates(null);
        return;
      }
      setLoadingStates(true);
      try {
        const res = await oeResearchAPI.getStates<StateComparisonData>(stateOccupation);
        setStates(res.data);
        // Pre-select top 5 states by employment
        if (res.data?.states?.length > 0 && selectedStates.length === 0) {
          const sorted = [...res.data.states].sort((a, b) => (b.employment || 0) - (a.employment || 0));
          setSelectedStates(sorted.slice(0, 5).map(s => s.state_code));
        }
      } catch (error) {
        console.error('Failed to load states:', error);
      } finally {
        setLoadingStates(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stateOccupation]);

  // Load state timeline
  useEffect(() => {
    const load = async () => {
      if (selectedStates.length === 0 || !stateOccupation || stateOccupation === '000000') {
        setStateTimeline(null);
        return;
      }
      try {
        const res = await oeResearchAPI.getStatesTimeline<StateTimelineData>(
          stateOccupation,
          stateDataType,
          selectedStates.join(','),
          stateTimeRange
        );
        setStateTimeline(res.data);
      } catch (error) {
        console.error('Failed to load state timeline:', error);
      }
    };
    load();
  }, [selectedStates, stateOccupation, stateDataType, stateTimeRange]);

  // Load industry analysis
  useEffect(() => {
    const load = async () => {
      if (!industryOccupation || industryOccupation === '000000') {
        setIndustries(null);
        return;
      }
      setLoadingIndustries(true);
      try {
        const res = await oeResearchAPI.getIndustries<IndustryAnalysisData>(
          industryOccupation,
          industrySector || null,
          50
        );
        setIndustries(res.data);
        // Pre-select first 3 industries
        if (res.data?.industries?.length > 0 && selectedIndustries.length === 0) {
          setSelectedIndustries(res.data.industries.slice(0, 3).map(i => i.industry_code));
        }
      } catch (error) {
        console.error('Failed to load industries:', error);
      } finally {
        setLoadingIndustries(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [industryOccupation, industrySector]);

  // Load industry timeline
  useEffect(() => {
    const load = async () => {
      if (selectedIndustries.length === 0 || !industryOccupation || industryOccupation === '000000') {
        setIndustryTimeline(null);
        return;
      }
      try {
        const res = await oeResearchAPI.getIndustriesTimeline<IndustryTimelineData>(
          industryOccupation,
          industryDataType,
          selectedIndustries.join(','),
          industryTimeRange
        );
        setIndustryTimeline(res.data);
      } catch (error) {
        console.error('Failed to load industry timeline:', error);
      }
    };
    load();
  }, [selectedIndustries, industryOccupation, industryDataType, industryTimeRange]);

  // Load top rankings
  useEffect(() => {
    const load = async () => {
      setLoadingTopRankings(true);
      try {
        const res = await oeResearchAPI.getTopRankings<TopRankingsData>('0000000', rankingType, 20);
        setTopRankings(res.data);
      } catch (error) {
        console.error('Failed to load top rankings:', error);
      } finally {
        setLoadingTopRankings(false);
      }
    };
    load();
  }, [rankingType]);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await oeResearchAPI.getTopMovers<TopMoversData>('0000000', moverMetric, 10);
        setTopMovers(res.data);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [moverMetric]);

  // Load wage distribution
  useEffect(() => {
    const load = async () => {
      if (!wageOccupation) {
        setWageDistribution(null);
        return;
      }
      setLoadingWageDistribution(true);
      try {
        const res = await oeResearchAPI.getWageDistribution<WageDistributionData>(wageOccupation, '0000000');
        setWageDistribution(res.data);
      } catch (error) {
        console.error('Failed to load wage distribution:', error);
      } finally {
        setLoadingWageDistribution(false);
      }
    };
    load();
  }, [wageOccupation]);

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await oeResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 50 });
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
      if (!drillOccupation && !drillState && !drillDataType) {
        setDrillResults(null);
        return;
      }
      setLoadingDrill(true);
      try {
        const params: Record<string, unknown> = { limit: 100 };
        if (drillOccupation) params.occupation_code = drillOccupation;
        if (drillState) params.state_code = drillState;
        if (drillDataType) params.datatype_code = drillDataType;
        const res = await oeResearchAPI.getSeries<SeriesListData>(params);
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
  }, [drillOccupation, drillState, drillDataType]);

  // Browse handler
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseOccupation) params.occupation_code = browseOccupation;
        if (browseState) params.state_code = browseState;
        if (browseDataType) params.datatype_code = browseDataType;
        const res = await oeResearchAPI.getSeries<SeriesListData>(params);
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
  }, [browseOccupation, browseState, browseDataType, browseLimit, browseOffset]);

  // Load chart data for selected series
  useEffect(() => {
    const load = async () => {
      const newData: SeriesChartDataMap = { ...seriesChartData };
      for (const seriesId of selectedSeriesIds) {
        if (!newData[seriesId]) {
          try {
            const res = await oeResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, seriesTimeRange || 20);
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

  // Build occupation options for dropdowns
  const occupationOptions: SelectOption[] = [
    { value: '', label: 'All Occupations' },
    ...(dimensions?.occupations || [])
      .filter(o => o.selectable !== false && o.display_level !== undefined && o.display_level <= 2)
      .map(o => ({ value: o.occupation_code, label: o.occupation_name }))
  ];

  // Build state options for dropdowns
  const stateOptions: SelectOption[] = [
    { value: '', label: 'All States' },
    ...(dimensions?.states || [])
      .filter(s => s.areatype_code === 'S')
      .map(s => ({ value: s.state_code, label: s.area_name }))
  ];

  // Build sector options for dropdowns
  const sectorOptions: SelectOption[] = [
    { value: '', label: 'All Sectors' },
    ...(dimensions?.sectors || []).map(s => ({ value: s.sector_code, label: s.sector_name }))
  ];

  // Build data type options for dropdown in series explorer
  const dataTypeOptionsForSeries: SelectOption[] = [
    { value: '', label: 'All Data Types' },
    ...(dimensions?.data_types || []).map(dt => ({ value: dt.datatype_code, label: dt.datatype_name }))
  ];

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">OEWS Explorer</h1>
          <p className="text-sm text-gray-600 mt-1">
            Occupational Employment and Wage Statistics - Employment and wage estimates for ~800 occupations
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Annual data, updated in March. National, State, and Metro area data available.
          </p>
        </div>
      </div>

      {/* Section 1: Overview by Major Groups */}
      <Card>
        <SectionHeader title="1. Overview by Major Occupation Groups" color="blue" icon={Users} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Data Type"
              value={overviewDataType}
              onChange={setOverviewDataType}
              options={dataTypeOptions}
              className="w-48"
            />
            <Select
              label="Time Range"
              value={overviewTimeRange}
              onChange={(v) => setOverviewTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-40"
            />
          </div>

          {loadingOverview ? (
            <LoadingSpinner />
          ) : overview ? (
            <>
              {/* Summary Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-xs text-blue-600 font-medium mb-1">Total Employment</div>
                  <div className="text-2xl font-bold text-blue-700">
                    {formatNumber(overview.total_employment)}
                  </div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-xs text-green-600 font-medium mb-1">Mean Annual Wage</div>
                  <div className="text-2xl font-bold text-green-700">
                    {formatWage(overview.mean_annual_wage)}
                  </div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-xs text-purple-600 font-medium mb-1">Median Annual Wage</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {formatWage(overview.median_annual_wage)}
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-xs text-gray-600 font-medium mb-1">Latest Year</div>
                  <div className="text-2xl font-bold text-gray-700">
                    {overview.latest_year || 'N/A'}
                  </div>
                </div>
              </div>

              {/* Major Groups Table */}
              <div className="overflow-x-auto max-h-[400px] overflow-y-auto mb-6">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                      <th className="px-3 py-2 text-left font-medium text-gray-600">Major Occupation Group</th>
                      <th className="px-3 py-2 text-right font-medium text-gray-600">Employment</th>
                      <th className="px-3 py-2 text-right font-medium text-gray-600">% of Total</th>
                      <th className="px-3 py-2 text-right font-medium text-gray-600">Annual Mean Wage</th>
                      <th className="px-3 py-2 text-right font-medium text-gray-600">YoY Emp%</th>
                      <th className="px-3 py-2 text-right font-medium text-gray-600">YoY Wage%</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {overview.major_groups.map((group) => (
                      <tr key={group.occupation_code} className="hover:bg-gray-50">
                        <td className="px-3 py-2">
                          <input
                            type="checkbox"
                            checked={selectedMajorGroups.includes(group.occupation_code)}
                            onChange={() => {
                              setSelectedMajorGroups(prev =>
                                prev.includes(group.occupation_code)
                                  ? prev.filter(c => c !== group.occupation_code)
                                  : [...prev, group.occupation_code]
                              );
                            }}
                            className="rounded border-gray-300"
                          />
                        </td>
                        <td className="px-3 py-2 font-medium text-gray-800">{group.occupation_name}</td>
                        <td className="px-3 py-2 text-right">{formatNumber(group.employment)}</td>
                        <td className="px-3 py-2 text-right">{group.employment_pct_of_total?.toFixed(1)}%</td>
                        <td className="px-3 py-2 text-right">{formatWage(group.annual_mean)}</td>
                        <td className="px-3 py-2 text-right">
                          <ChangeIndicator value={group.yoy_employment_change} suffix="%" />
                        </td>
                        <td className="px-3 py-2 text-right">
                          <ChangeIndicator value={group.yoy_wage_change} suffix="%" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Timeline Chart */}
              {overviewTimeline?.timeline && overviewTimeline.timeline.length > 0 && selectedMajorGroups.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">
                    Historical {overviewDataType === 'employment' ? 'Employment' : 'Mean Annual Wage'}
                  </h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={overviewTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip formatter={(value: number) => overviewDataType === 'employment' ? formatNumber(value) : formatWage(value)} />
                        <Legend />
                        {selectedMajorGroups.map((code, idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`major_groups.${code}`}
                            name={overviewTimeline.group_names?.[code] || code}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 2: Occupation Analysis */}
      <Card>
        <SectionHeader title="2. Occupation Analysis" color="green" icon={Briefcase} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Major Group Filter"
              value={occupationMajorGroup}
              onChange={setOccupationMajorGroup}
              options={[{ value: '', label: 'All Major Groups' }, ...majorOccupationGroups]}
              className="w-64"
            />
            <Select
              label="Data Type"
              value={occupationDataType}
              onChange={setOccupationDataType}
              options={dataTypeOptions}
              className="w-48"
            />
            <Select
              label="Time Range"
              value={occupationTimeRange}
              onChange={(v) => setOccupationTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <div className="flex items-end">
              <ViewToggle value={occupationView} onChange={setOccupationView} />
            </div>
          </div>

          {loadingOccupations ? (
            <LoadingSpinner />
          ) : occupations ? (
            <>
              {occupationView === 'table' ? (
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Occupation</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Employment</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Hourly Mean</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Annual Mean</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Annual Median</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">LQ</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">YoY Wage%</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {occupations.occupations.map((occ) => (
                        <tr key={occ.occupation_code} className="hover:bg-gray-50">
                          <td className="px-3 py-2">
                            <input
                              type="checkbox"
                              checked={selectedOccupations.includes(occ.occupation_code)}
                              onChange={() => {
                                setSelectedOccupations(prev =>
                                  prev.includes(occ.occupation_code)
                                    ? prev.filter(c => c !== occ.occupation_code)
                                    : [...prev, occ.occupation_code]
                                );
                              }}
                              className="rounded border-gray-300"
                            />
                          </td>
                          <td className="px-3 py-2 font-medium" style={{ paddingLeft: `${(occ.display_level || 0) * 12 + 12}px` }}>
                            {occ.occupation_name}
                          </td>
                          <td className="px-3 py-2 text-right">{formatNumber(occ.employment)}</td>
                          <td className="px-3 py-2 text-right">{formatWage(occ.hourly_mean, true)}</td>
                          <td className="px-3 py-2 text-right">{formatWage(occ.annual_mean)}</td>
                          <td className="px-3 py-2 text-right">{formatWage(occ.annual_median)}</td>
                          <td className="px-3 py-2 text-right">{formatLQ(occ.location_quotient)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={occ.yoy_wage_pct} suffix="%" />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                occupationTimeline?.timeline && occupationTimeline.timeline.length > 0 && (
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={occupationTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        {selectedOccupations.map((code, idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`occupations.${code}`}
                            name={occupationTimeline.occupation_names?.[code] || code}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            dot={false}
                          />
                        ))}
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

      {/* Section 3: State Comparison */}
      <Card>
        <SectionHeader title="3. State Comparison" color="cyan" icon={MapPin} />
        <div className="p-5">
          <p className="text-sm text-gray-600 mb-4">
            Compare wages and employment for a specific occupation across all U.S. states.
          </p>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Occupation"
              value={stateOccupation}
              onChange={(v) => { setStateOccupation(v); setSelectedStates([]); }}
              options={[{ value: '000000', label: 'Select an Occupation...' }, ...occupationOptions.filter(o => o.value !== '')]}
              className="w-64"
            />
            <Select
              label="Data Type"
              value={stateDataType}
              onChange={setStateDataType}
              options={dataTypeOptions}
              className="w-48"
            />
            <Select
              label="Time Range"
              value={stateTimeRange}
              onChange={(v) => setStateTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <div className="flex items-end">
              <ViewToggle value={stateView} onChange={setStateView} />
            </div>
          </div>

          {stateOccupation === '000000' ? (
            <div className="text-center text-gray-500 py-8">Select an occupation to see state comparison</div>
          ) : loadingStates ? (
            <LoadingSpinner />
          ) : states ? (
            <>
              {stateView === 'table' ? (
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">State</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Employment</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Emp/1,000</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">LQ</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Hourly Mean</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Annual Mean</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {states.states.map((st) => (
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
                          <td className="px-3 py-2 text-right">{formatNumber(st.employment)}</td>
                          <td className="px-3 py-2 text-right">{st.employment_per_1000?.toFixed(2) || 'N/A'}</td>
                          <td className="px-3 py-2 text-right">{formatLQ(st.location_quotient)}</td>
                          <td className="px-3 py-2 text-right">{formatWage(st.hourly_mean, true)}</td>
                          <td className="px-3 py-2 text-right">{formatWage(st.annual_mean)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                stateTimeline?.timeline && stateTimeline.timeline.length > 0 && (
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={stateTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        {selectedStates.map((code, idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`states.${code}`}
                            name={stateTimeline.state_names?.[code] || code}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No state data available</div>
          )}
        </div>
      </Card>

      {/* Section 4: Industry Analysis */}
      <Card>
        <SectionHeader title="4. Industry Analysis" color="purple" icon={Building2} />
        <div className="p-5">
          <p className="text-sm text-gray-600 mb-4">
            Compare wages and employment for a specific occupation across industries (national level only).
          </p>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Occupation"
              value={industryOccupation}
              onChange={(v) => { setIndustryOccupation(v); setSelectedIndustries([]); }}
              options={[{ value: '000000', label: 'Select an Occupation...' }, ...occupationOptions.filter(o => o.value !== '')]}
              className="w-64"
            />
            <Select
              label="Sector Filter"
              value={industrySector}
              onChange={setIndustrySector}
              options={sectorOptions}
              className="w-48"
            />
            <Select
              label="Data Type"
              value={industryDataType}
              onChange={setIndustryDataType}
              options={dataTypeOptions}
              className="w-48"
            />
            <Select
              label="Time Range"
              value={industryTimeRange}
              onChange={(v) => setIndustryTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <div className="flex items-end">
              <ViewToggle value={industryView} onChange={setIndustryView} />
            </div>
          </div>

          {industryOccupation === '000000' ? (
            <div className="text-center text-gray-500 py-8">Select an occupation to see industry comparison</div>
          ) : loadingIndustries ? (
            <LoadingSpinner />
          ) : industries ? (
            <>
              {industryView === 'table' ? (
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Industry</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Employment</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Hourly Mean</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Annual Mean</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">LQ</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">YoY Wage%</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {industries.industries.map((ind) => (
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
                          <td className="px-3 py-2 text-right">{formatNumber(ind.employment)}</td>
                          <td className="px-3 py-2 text-right">{formatWage(ind.hourly_mean, true)}</td>
                          <td className="px-3 py-2 text-right">{formatWage(ind.annual_mean)}</td>
                          <td className="px-3 py-2 text-right">{formatLQ(ind.location_quotient)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={ind.yoy_wage_pct} suffix="%" />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                industryTimeline?.timeline && industryTimeline.timeline.length > 0 && (
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={industryTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        {selectedIndustries.map((code, idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`industries.${code}`}
                            name={industryTimeline.industry_names?.[code] || code}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No industry data available</div>
          )}
        </div>
      </Card>

      {/* Section 5: Top Rankings */}
      <Card>
        <SectionHeader title="5. Top Rankings" color="orange" icon={DollarSign} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Ranking Type"
              value={rankingType}
              onChange={setRankingType}
              options={rankingTypeOptions}
              className="w-48"
            />
          </div>

          {loadingTopRankings ? (
            <LoadingSpinner />
          ) : topRankings ? (
            <div className="grid md:grid-cols-2 gap-4">
              {topRankings.occupations.slice(0, 20).map((occ) => (
                <div key={occ.occupation_code} className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 flex items-center justify-center bg-orange-100 text-orange-700 font-bold rounded-full mr-3">
                    {occ.rank}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-800 truncate">{occ.occupation_name}</div>
                    <div className="text-sm text-gray-600">
                      {rankingType === 'highest_paying' && formatWage(occ.value)}
                      {rankingType === 'most_employed' && `${formatNumber(occ.value)} employed`}
                      {rankingType === 'highest_lq' && `LQ: ${formatLQ(occ.value)}`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">No ranking data available</div>
          )}
        </div>
      </Card>

      {/* Section 6: Top Movers */}
      <Card>
        <SectionHeader title="6. Top Movers (Year-over-Year)" color="red" icon={TrendingUp} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Metric"
              value={moverMetric}
              onChange={(v) => setMoverMetric(v as MoverMetric)}
              options={[
                { value: 'annual_mean', label: 'Annual Mean Wage' },
                { value: 'employment', label: 'Employment' },
              ]}
              className="w-48"
            />
          </div>

          {loadingTopMovers ? (
            <LoadingSpinner />
          ) : topMovers ? (
            <div className="grid md:grid-cols-2 gap-6">
              {/* Gainers */}
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold text-green-700 mb-3">
                  <ArrowUpCircle className="w-5 h-5" />
                  Top Gainers
                </h3>
                <div className="space-y-2">
                  {topMovers.gainers.map((m, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-800 truncate">{m.occupation_name}</div>
                        <div className="text-xs text-gray-500">
                          {moverMetric === 'annual_mean' ? formatWage(m.value) : formatNumber(m.value)}
                        </div>
                      </div>
                      <div className="text-green-600 font-semibold">
                        +{m.change_pct?.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                  {topMovers.gainers.length === 0 && (
                    <div className="text-gray-500 text-center py-4">No gainers</div>
                  )}
                </div>
              </div>

              {/* Losers */}
              <div>
                <h3 className="flex items-center gap-2 text-lg font-semibold text-red-700 mb-3">
                  <ArrowDownCircle className="w-5 h-5" />
                  Top Losers
                </h3>
                <div className="space-y-2">
                  {topMovers.losers.map((m, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-800 truncate">{m.occupation_name}</div>
                        <div className="text-xs text-gray-500">
                          {moverMetric === 'annual_mean' ? formatWage(m.value) : formatNumber(m.value)}
                        </div>
                      </div>
                      <div className="text-red-600 font-semibold">
                        {m.change_pct?.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                  {topMovers.losers.length === 0 && (
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

      {/* Section 7: Wage Distribution */}
      <Card>
        <SectionHeader title="7. Wage Distribution" color="purple" icon={DollarSign} />
        <div className="p-5">
          <p className="text-sm text-gray-600 mb-4">
            View wage percentile distribution (10th, 25th, 50th, 75th, 90th) for a specific occupation.
          </p>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Occupation"
              value={wageOccupation}
              onChange={setWageOccupation}
              options={[{ value: '', label: 'Select an Occupation...' }, ...occupationOptions.filter(o => o.value !== '')]}
              className="w-64"
            />
          </div>

          {!wageOccupation ? (
            <div className="text-center text-gray-500 py-8">Select an occupation to see wage distribution</div>
          ) : loadingWageDistribution ? (
            <LoadingSpinner />
          ) : wageDistribution?.distributions?.[0] ? (
            <>
              {/* Bar Chart for Wage Distribution */}
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={[
                      { name: '10th', hourly: wageDistribution.distributions[0].hourly_10th, annual: wageDistribution.distributions[0].annual_10th },
                      { name: '25th', hourly: wageDistribution.distributions[0].hourly_25th, annual: wageDistribution.distributions[0].annual_25th },
                      { name: 'Median', hourly: wageDistribution.distributions[0].hourly_median, annual: wageDistribution.distributions[0].annual_median },
                      { name: 'Mean', hourly: wageDistribution.distributions[0].hourly_mean, annual: wageDistribution.distributions[0].annual_mean },
                      { name: '75th', hourly: wageDistribution.distributions[0].hourly_75th, annual: wageDistribution.distributions[0].annual_75th },
                      { name: '90th', hourly: wageDistribution.distributions[0].hourly_90th, annual: wageDistribution.distributions[0].annual_90th },
                    ]}
                    layout="vertical"
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={60} />
                    <Tooltip formatter={(value: number) => formatWage(value)} />
                    <Legend />
                    <Bar dataKey="annual" name="Annual Wage" fill="#8b5cf6">
                      {[0, 1, 2, 3, 4, 5].map((_, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Wage Details Table */}
              <div className="mt-6 grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Hourly Wages</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>10th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].hourly_10th, true)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>25th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].hourly_25th, true)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-purple-50 rounded">
                      <span>Median (50th)</span>
                      <span className="font-bold text-purple-700">{formatWage(wageDistribution.distributions[0].hourly_median, true)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-blue-50 rounded">
                      <span>Mean</span>
                      <span className="font-bold text-blue-700">{formatWage(wageDistribution.distributions[0].hourly_mean, true)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>75th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].hourly_75th, true)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>90th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].hourly_90th, true)}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Annual Wages</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>10th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].annual_10th)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>25th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].annual_25th)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-purple-50 rounded">
                      <span>Median (50th)</span>
                      <span className="font-bold text-purple-700">{formatWage(wageDistribution.distributions[0].annual_median)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-blue-50 rounded">
                      <span>Mean</span>
                      <span className="font-bold text-blue-700">{formatWage(wageDistribution.distributions[0].annual_mean)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>75th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].annual_75th)}</span>
                    </div>
                    <div className="flex justify-between p-2 bg-gray-50 rounded">
                      <span>90th Percentile</span>
                      <span className="font-medium">{formatWage(wageDistribution.distributions[0].annual_90th)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No wage distribution data available</div>
          )}
        </div>
      </Card>

      {/* Section 8: Series Detail Explorer */}
      <Card>
        <SectionHeader title="8. Series Detail Explorer" color="red" icon={Briefcase} />
        <div className="p-5 space-y-6">
          {/* Sub-section A: Search by Keyword */}
          <div className="border-l-4 border-cyan-500 pl-4">
            <h3 className="text-lg font-semibold bg-gradient-to-r from-cyan-600 to-cyan-400 bg-clip-text text-transparent mb-3">
              Search by Keyword
            </h3>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                placeholder="Search by occupation or area name..."
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
                      <th className="px-3 py-2 text-left">Occupation</th>
                      <th className="px-3 py-2 text-left">Area</th>
                      <th className="px-3 py-2 text-left">Data Type</th>
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
                        <td className="px-3 py-2">{s.occupation_name}</td>
                        <td className="px-3 py-2">{s.area_name}</td>
                        <td className="px-3 py-2">{s.datatype_name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Sub-section B: Hierarchical Drill-down */}
          <div className="border-l-4 border-green-500 pl-4">
            <h3 className="text-lg font-semibold bg-gradient-to-r from-green-600 to-green-400 bg-clip-text text-transparent mb-3">
              Hierarchical Drill-down
            </h3>
            <div className="flex flex-wrap gap-4 mb-4">
              <Select
                label="Occupation"
                value={drillOccupation}
                onChange={setDrillOccupation}
                options={occupationOptions}
                className="w-64"
              />
              <Select
                label="State"
                value={drillState}
                onChange={setDrillState}
                options={stateOptions}
                className="w-40"
              />
              <Select
                label="Data Type"
                value={drillDataType}
                onChange={setDrillDataType}
                options={dataTypeOptionsForSeries}
                className="w-48"
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
                      <th className="px-3 py-2 text-left">Occupation</th>
                      <th className="px-3 py-2 text-left">Area</th>
                      <th className="px-3 py-2 text-left">Data Type</th>
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
                        <td className="px-3 py-2">{s.occupation_name}</td>
                        <td className="px-3 py-2">{s.area_name}</td>
                        <td className="px-3 py-2">{s.datatype_name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : drillResults ? (
              <div className="text-gray-500 text-center py-4">No series found</div>
            ) : null}
          </div>

          {/* Sub-section C: Browse All Series */}
          <div className="border-l-4 border-purple-500 pl-4">
            <h3 className="text-lg font-semibold bg-gradient-to-r from-purple-600 to-purple-400 bg-clip-text text-transparent mb-3">
              Browse All Series
            </h3>
            <div className="flex flex-wrap gap-4 mb-4">
              <Select
                label="Occupation"
                value={browseOccupation}
                onChange={(v) => { setBrowseOccupation(v); setBrowseOffset(0); }}
                options={occupationOptions}
                className="w-64"
              />
              <Select
                label="State"
                value={browseState}
                onChange={(v) => { setBrowseState(v); setBrowseOffset(0); }}
                options={stateOptions}
                className="w-40"
              />
              <Select
                label="Data Type"
                value={browseDataType}
                onChange={(v) => { setBrowseDataType(v); setBrowseOffset(0); }}
                options={dataTypeOptionsForSeries}
                className="w-48"
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
                        <th className="px-3 py-2 text-left">Occupation</th>
                        <th className="px-3 py-2 text-left">Area</th>
                        <th className="px-3 py-2 text-left">Data Type</th>
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
                          <td className="px-3 py-2">{s.occupation_name}</td>
                          <td className="px-3 py-2">{s.area_name}</td>
                          <td className="px-3 py-2">{s.datatype_name}</td>
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
                            name={info ? `${info.occupation_name} - ${info.datatype_name}` : seriesId}
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
                        <th className="px-3 py-2 text-left">Year</th>
                        {selectedSeriesIds.map((seriesId) => {
                          const info = allSeriesInfo[seriesId];
                          return (
                            <th key={seriesId} className="px-3 py-2 text-right">
                              {info ? `${info.datatype_name}` : seriesId}
                            </th>
                          );
                        })}
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {/* Get union of all periods */}
                      {(() => {
                        const allPeriods: Record<string, Record<string, number>> = {};
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
                          .slice(0, 30)
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
