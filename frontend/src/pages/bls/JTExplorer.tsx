import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, Briefcase, ArrowUpCircle, ArrowDownCircle, LucideIcon, Building2, MapPin, Users } from 'lucide-react';
import { jtResearchAPI } from '../../services/api';

/**
 * JT Explorer - Job Openings and Labor Turnover Survey (JOLTS) Explorer
 *
 * JOLTS provides national estimates of rates and levels for:
 * - Job openings (JO)
 * - Hires (HI)
 * - Total separations (TS)
 * - Quits (QU)
 * - Layoffs and discharges (LD)
 * - Other separations (OS)
 * - Unemployed persons per job opening ratio (UO)
 *
 * Sections:
 * 1. JOLTS Overview - Summary metrics for selected industry/region
 * 2. Industry Analysis - JOLTS metrics by industry
 * 3. Regional Analysis - JOLTS metrics by state/region
 * 4. Size Class Analysis - JOLTS by establishment size
 * 5. Top Movers - Industries with largest changes
 * 6. Series Explorer - Search, drill-down, and browse series
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

interface TimelinePoint {
  year: number;
  period: string;
  period_name: string;
  job_openings_rate?: number | null;
  hires_rate?: number | null;
  total_separations_rate?: number | null;
  quits_rate?: number | null;
  layoffs_rate?: number | null;
  job_openings_level?: number | null;
  hires_level?: number | null;
  total_separations_level?: number | null;
  quits_level?: number | null;
  layoffs_level?: number | null;
  industries?: Record<string, number | null>;
  regions?: Record<string, number | null>;
  size_classes?: Record<string, number | null>;
  [key: string]: unknown;
}

interface JTMetric {
  series_id: string;
  dataelement_code: string;
  dataelement_name: string;
  ratelevel_code: string;
  value?: number | null;
  latest_date?: string;
  month_over_month?: number | null;
  month_over_month_pct?: number | null;
  year_over_year?: number | null;
  year_over_year_pct?: number | null;
}

interface OverviewData {
  industry_code?: string;
  industry_name?: string;
  state_code?: string;
  state_name?: string;
  job_openings_rate?: JTMetric | null;
  hires_rate?: JTMetric | null;
  total_separations_rate?: JTMetric | null;
  quits_rate?: JTMetric | null;
  layoffs_rate?: JTMetric | null;
  job_openings_level?: JTMetric | null;
  hires_level?: JTMetric | null;
  total_separations_level?: JTMetric | null;
  quits_level?: JTMetric | null;
  layoffs_level?: JTMetric | null;
  unemployed_per_opening?: JTMetric | null;
  last_updated?: string;
}

interface OverviewTimelineData {
  industry_name?: string;
  state_name?: string;
  timeline: TimelinePoint[];
}

interface IndustryMetric {
  industry_code: string;
  industry_name: string;
  display_level?: number;
  job_openings_rate?: number | null;
  hires_rate?: number | null;
  quits_rate?: number | null;
  layoffs_rate?: number | null;
  total_separations_rate?: number | null;
  job_openings_level?: number | null;
  job_openings_yoy_pct?: number | null;
  hires_yoy_pct?: number | null;
  quits_yoy_pct?: number | null;
  latest_date?: string;
}

interface IndustryAnalysisData {
  state_code?: string;
  state_name?: string;
  industries: IndustryMetric[];
  last_updated?: string;
}

interface IndustryTimelineData {
  dataelement_code: string;
  dataelement_name: string;
  ratelevel_code: string;
  timeline: TimelinePoint[];
  industry_names: Record<string, string>;
}

interface RegionMetric {
  state_code: string;
  state_name: string;
  is_region: boolean;
  job_openings_rate?: number | null;
  hires_rate?: number | null;
  quits_rate?: number | null;
  layoffs_rate?: number | null;
  total_separations_rate?: number | null;
  job_openings_level?: number | null;
  job_openings_yoy_pct?: number | null;
  latest_date?: string;
}

interface RegionAnalysisData {
  industry_code?: string;
  industry_name?: string;
  regions: RegionMetric[];
  last_updated?: string;
}

interface RegionTimelineData {
  dataelement_code: string;
  dataelement_name: string;
  ratelevel_code: string;
  timeline: TimelinePoint[];
  region_names: Record<string, string>;
}

interface SizeClassMetric {
  sizeclass_code: string;
  sizeclass_name: string;
  job_openings_rate?: number | null;
  hires_rate?: number | null;
  quits_rate?: number | null;
  layoffs_rate?: number | null;
  total_separations_rate?: number | null;
  job_openings_level?: number | null;
  latest_date?: string;
}

interface SizeClassAnalysisData {
  industry_code?: string;
  industry_name?: string;
  size_classes: SizeClassMetric[];
  last_updated?: string;
}

interface SizeClassTimelineData {
  dataelement_code: string;
  dataelement_name: string;
  ratelevel_code: string;
  timeline: TimelinePoint[];
  sizeclass_names: Record<string, string>;
}

interface Mover {
  series_id: string;
  industry_code: string;
  industry_name: string;
  dataelement_code: string;
  dataelement_name: string;
  value?: number | null;
  latest_date?: string;
  change?: number | null;
  change_pct?: number | null;
}

interface TopMoversData {
  dataelement_code: string;
  dataelement_name: string;
  period: string;
  gainers: Mover[];
  losers: Mover[];
  last_updated?: string;
}

interface IndustryItem {
  industry_code: string;
  industry_name: string;
  display_level?: number;
  selectable?: boolean;
}

interface StateItem {
  state_code: string;
  state_name: string;
  display_level?: number;
  selectable?: boolean;
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
  industries: IndustryItem[];
  states: StateItem[];
  data_elements: DataElementItem[];
  size_classes: SizeClassItem[];
  rate_levels: RateLevelItem[];
}

interface SeriesInfo {
  series_id: string;
  industry_code?: string;
  industry_name?: string;
  state_code?: string;
  state_name?: string;
  dataelement_code?: string;
  dataelement_name?: string;
  ratelevel_code?: string;
  ratelevel_name?: string;
  sizeclass_code?: string;
  sizeclass_name?: string;
  seasonal_code?: string;
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
  industry_name?: string;
  state_name?: string;
  dataelement_name?: string;
  ratelevel_name?: string;
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
type MoverPeriod = 'mom' | 'yoy';

// ============================================================================
// CONSTANTS
// ============================================================================

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'];

const timeRangeOptions: TimeRangeOption[] = [
  { value: 12, label: 'Last 12 months' },
  { value: 24, label: 'Last 2 years' },
  { value: 60, label: 'Last 5 years' },
  { value: 120, label: 'Last 10 years' },
  { value: 240, label: 'Last 20 years' },
  { value: 0, label: 'All Time' },
];

const dataElementOptions: SelectOption[] = [
  { value: 'JO', label: 'Job Openings' },
  { value: 'HI', label: 'Hires' },
  { value: 'QU', label: 'Quits' },
  { value: 'LD', label: 'Layoffs & Discharges' },
  { value: 'TS', label: 'Total Separations' },
];

const rateLevelOptions: SelectOption[] = [
  { value: 'R', label: 'Rate (%)' },
  { value: 'L', label: 'Level (Thousands)' },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatRate = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return `${value.toFixed(1)}%`;
};

const formatLevel = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return `${value.toLocaleString()}K`;
};

const formatChange = (value: number | undefined | null, suffix: string = ''): string => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}${suffix}`;
};

const formatPeriod = (periodCode: string | undefined | null): string => {
  if (!periodCode) return '';
  const monthMap: Record<string, string> = {
    'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
    'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
    'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
  };
  return monthMap[periodCode] || periodCode;
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

interface TimelineSelectorProps {
  timeline: TimelinePoint[];
  selectedIndex: number | null;
  onSelectIndex: (index: number) => void;
}

const TimelineSelector = ({ timeline, selectedIndex, onSelectIndex }: TimelineSelectorProps): ReactElement | null => {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="mt-4 mb-2 px-2">
      <p className="text-xs text-gray-500 mb-2">Select Month (click any point):</p>
      <div className="relative h-14">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-300" />
        <div className="relative flex justify-between">
          {timeline.map((point, index) => {
            const isSelected = selectedIndex === index;
            const isLatest = index === timeline.length - 1;
            const shouldShowLabel = index % Math.max(1, Math.floor(timeline.length / 8)) === 0 || index === timeline.length - 1;

            return (
              <div
                key={`${point.year}-${point.period}`}
                className="flex flex-col items-center cursor-pointer flex-1"
                onClick={() => onSelectIndex(index)}
              >
                <div
                  className={`rounded-full transition-all ${
                    isSelected
                      ? 'w-3.5 h-3.5 bg-blue-600 shadow-md'
                      : isLatest && selectedIndex === null
                      ? 'w-2.5 h-2.5 bg-blue-400'
                      : 'w-2.5 h-2.5 bg-gray-400 hover:bg-blue-400 hover:scale-110'
                  }`}
                />
                {(shouldShowLabel || isSelected) && (
                  <span className={`text-[10px] mt-1 ${isSelected ? 'text-blue-600 font-semibold' : 'text-gray-500'}`}>
                    {formatPeriod(point.period)} {point.year}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

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
  <div className="flex justify-center items-center p-8">
    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
  </div>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function JTExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [, setLoadingDimensions] = useState(true);

  // Overview
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewIndustry, setOverviewIndustry] = useState('000000');
  const [overviewState, setOverviewState] = useState('00');
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [overviewTimeRange, setOverviewTimeRange] = useState(60);
  const [overviewSelectedIndex, setOverviewSelectedIndex] = useState<number | null>(null);

  // Industry Analysis
  const [industries, setIndustries] = useState<IndustryAnalysisData | null>(null);
  const [loadingIndustries, setLoadingIndustries] = useState(true);
  const [industryState, setIndustryState] = useState('00');
  const [industryTimeline, setIndustryTimeline] = useState<IndustryTimelineData | null>(null);
  const [industryTimeRange, setIndustryTimeRange] = useState(60);
  const [industryDataElement, setIndustryDataElement] = useState('JO');
  const [industryRateLevel, setIndustryRateLevel] = useState('R');
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [industrySelectedIndex, setIndustrySelectedIndex] = useState<number | null>(null);
  const [industryView, setIndustryView] = useState<ViewType>('chart');

  // Regional Analysis
  const [regions, setRegions] = useState<RegionAnalysisData | null>(null);
  const [loadingRegions, setLoadingRegions] = useState(true);
  const [regionIndustry, setRegionIndustry] = useState('000000');
  const [regionTimeline, setRegionTimeline] = useState<RegionTimelineData | null>(null);
  const [regionTimeRange, setRegionTimeRange] = useState(60);
  const [regionDataElement, setRegionDataElement] = useState('JO');
  const [regionRateLevel, setRegionRateLevel] = useState('R');
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [regionSelectedIndex, setRegionSelectedIndex] = useState<number | null>(null);
  const [regionView, setRegionView] = useState<ViewType>('chart');

  // Size Class Analysis
  const [sizeClasses, setSizeClasses] = useState<SizeClassAnalysisData | null>(null);
  const [loadingSizeClasses, setLoadingSizeClasses] = useState(true);
  const [sizeClassTimeline, setSizeClassTimeline] = useState<SizeClassTimelineData | null>(null);
  const [sizeClassTimeRange, setSizeClassTimeRange] = useState(60);
  const [sizeClassDataElement, setSizeClassDataElement] = useState('JO');
  const [sizeClassRateLevel, setSizeClassRateLevel] = useState('R');
  const [selectedSizeClasses, setSelectedSizeClasses] = useState<string[]>([]);
  const [sizeClassSelectedIndex, setSizeClassSelectedIndex] = useState<number | null>(null);
  const [sizeClassView, setSizeClassView] = useState<ViewType>('chart');

  // Top Movers
  const [topMovers, setTopMovers] = useState<TopMoversData | null>(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(true);
  const [moverPeriod, setMoverPeriod] = useState<MoverPeriod>('yoy');
  const [moverDataElement, setMoverDataElement] = useState('JO');

  // Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Series Explorer - Drill-down
  const [drillIndustry, setDrillIndustry] = useState('');
  const [drillState, setDrillState] = useState('');
  const [drillDataElement, setDrillDataElement] = useState('');
  const [drillRateLevel, setDrillRateLevel] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);

  // Series Explorer - Browse
  const [browseIndustry, setBrowseIndustry] = useState('');
  const [browseState, setBrowseState] = useState('');
  const [browseDataElement, setBrowseDataElement] = useState('');
  const [browseSeasonal, setBrowseSeasonal] = useState('');
  const [browseLimit, setBrowseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series Explorer - Shared
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesTimeRange, setSeriesTimeRange] = useState(60);
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
        const res = await jtResearchAPI.getDimensions<DimensionsData>();
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
        const res = await jtResearchAPI.getOverview<OverviewData>(overviewIndustry, overviewState);
        setOverview(res.data);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
  }, [overviewIndustry, overviewState]);

  // Load overview timeline
  useEffect(() => {
    const load = async () => {
      try {
        const res = await jtResearchAPI.getOverviewTimeline<OverviewTimelineData>(
          overviewIndustry, overviewState, overviewTimeRange
        );
        setOverviewTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setOverviewSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load overview timeline:', error);
      }
    };
    load();
  }, [overviewIndustry, overviewState, overviewTimeRange]);

  // Load industry analysis
  useEffect(() => {
    const load = async () => {
      setLoadingIndustries(true);
      try {
        const res = await jtResearchAPI.getIndustries<IndustryAnalysisData>(industryState);
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
  }, [industryState]);

  // Load industry timeline
  useEffect(() => {
    const load = async () => {
      if (selectedIndustries.length === 0) {
        setIndustryTimeline(null);
        return;
      }
      try {
        const res = await jtResearchAPI.getIndustriesTimeline<IndustryTimelineData>(
          industryDataElement, industryRateLevel, industryState, industryTimeRange,
          selectedIndustries.join(',')
        );
        setIndustryTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setIndustrySelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load industry timeline:', error);
      }
    };
    load();
  }, [selectedIndustries, industryDataElement, industryRateLevel, industryState, industryTimeRange]);

  // Load regional analysis
  useEffect(() => {
    const load = async () => {
      setLoadingRegions(true);
      try {
        const res = await jtResearchAPI.getRegions<RegionAnalysisData>(regionIndustry);
        setRegions(res.data);
        // Pre-select regions (00 = Total US, NE, MW, SO, WE)
        if (res.data?.regions?.length > 0 && selectedRegions.length === 0) {
          setSelectedRegions(['00', 'NE', 'MW', 'SO', 'WE']);
        }
      } catch (error) {
        console.error('Failed to load regions:', error);
      } finally {
        setLoadingRegions(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [regionIndustry]);

  // Load region timeline
  useEffect(() => {
    const load = async () => {
      if (selectedRegions.length === 0) {
        setRegionTimeline(null);
        return;
      }
      try {
        const res = await jtResearchAPI.getRegionsTimeline<RegionTimelineData>(
          regionDataElement, regionRateLevel, regionIndustry, regionTimeRange,
          selectedRegions.join(',')
        );
        setRegionTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setRegionSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load region timeline:', error);
      }
    };
    load();
  }, [selectedRegions, regionDataElement, regionRateLevel, regionIndustry, regionTimeRange]);

  // Load size class analysis
  useEffect(() => {
    const load = async () => {
      setLoadingSizeClasses(true);
      try {
        const res = await jtResearchAPI.getSizeClasses<SizeClassAnalysisData>();
        setSizeClasses(res.data);
        // Pre-select all size classes
        if (res.data?.size_classes?.length > 0 && selectedSizeClasses.length === 0) {
          setSelectedSizeClasses(res.data.size_classes.map(s => s.sizeclass_code));
        }
      } catch (error) {
        console.error('Failed to load size classes:', error);
      } finally {
        setLoadingSizeClasses(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load size class timeline
  useEffect(() => {
    const load = async () => {
      if (selectedSizeClasses.length === 0) {
        setSizeClassTimeline(null);
        return;
      }
      try {
        const res = await jtResearchAPI.getSizeClassesTimeline<SizeClassTimelineData>(
          sizeClassDataElement, sizeClassRateLevel, sizeClassTimeRange,
          selectedSizeClasses.join(',')
        );
        setSizeClassTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setSizeClassSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load size class timeline:', error);
      }
    };
    load();
  }, [selectedSizeClasses, sizeClassDataElement, sizeClassRateLevel, sizeClassTimeRange]);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await jtResearchAPI.getTopMovers<TopMoversData>(moverDataElement, moverPeriod, 10);
        setTopMovers(res.data);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [moverDataElement, moverPeriod]);

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await jtResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 50 });
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
      if (!drillIndustry && !drillState && !drillDataElement) {
        setDrillResults(null);
        return;
      }
      setLoadingDrill(true);
      try {
        const params: Record<string, unknown> = { limit: 100 };
        if (drillIndustry) params.industry_code = drillIndustry;
        if (drillState) params.state_code = drillState;
        if (drillDataElement) params.dataelement_code = drillDataElement;
        if (drillRateLevel) params.ratelevel_code = drillRateLevel;
        const res = await jtResearchAPI.getSeries<SeriesListData>(params);
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
  }, [drillIndustry, drillState, drillDataElement, drillRateLevel]);

  // Browse handler
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseIndustry) params.industry_code = browseIndustry;
        if (browseState) params.state_code = browseState;
        if (browseDataElement) params.dataelement_code = browseDataElement;
        if (browseSeasonal) params.seasonal = browseSeasonal;
        const res = await jtResearchAPI.getSeries<SeriesListData>(params);
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
  }, [browseIndustry, browseState, browseDataElement, browseSeasonal, browseLimit, browseOffset]);

  // Load chart data for selected series
  useEffect(() => {
    const load = async () => {
      const newData: SeriesChartDataMap = { ...seriesChartData };
      for (const seriesId of selectedSeriesIds) {
        if (!newData[seriesId]) {
          try {
            const res = await jtResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, seriesTimeRange || 240);
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

  // Build industry options for dropdowns
  const industryOptions: SelectOption[] = [
    { value: '', label: 'All Industries' },
    ...(dimensions?.industries || [])
      .filter(i => i.selectable !== false)
      .map(i => ({ value: i.industry_code, label: i.industry_name }))
  ];

  // Build state options for dropdowns
  const stateOptions: SelectOption[] = [
    { value: '', label: 'All States' },
    ...(dimensions?.states || [])
      .filter(s => s.selectable !== false)
      .map(s => ({ value: s.state_code, label: s.state_name }))
  ];

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">JOLTS Explorer</h1>
          <p className="text-sm text-gray-600 mt-1">
            Job Openings and Labor Turnover Survey - Rates and levels for job openings, hires, quits, and separations
          </p>
        </div>
      </div>

      {/* Section 1: JOLTS Overview */}
      <Card>
        <SectionHeader title="1. JOLTS Overview" color="blue" icon={Briefcase} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Industry"
              value={overviewIndustry}
              onChange={setOverviewIndustry}
              options={[
                { value: '000000', label: 'Total Nonfarm' },
                ...industryOptions.filter(o => o.value !== '')
              ]}
              className="w-48"
            />
            <Select
              label="Region"
              value={overviewState}
              onChange={setOverviewState}
              options={[
                { value: '00', label: 'Total US' },
                ...stateOptions.filter(o => o.value !== '')
              ]}
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
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                {/* Job Openings Rate */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-xs text-blue-600 font-medium mb-1">Job Openings Rate</div>
                  <div className="text-2xl font-bold text-blue-700">
                    {formatRate(overview.job_openings_rate?.value)}
                  </div>
                  <div className="mt-1">
                    <ChangeIndicator value={overview.job_openings_rate?.year_over_year_pct} suffix="% YoY" />
                  </div>
                </div>

                {/* Hires Rate */}
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-xs text-green-600 font-medium mb-1">Hires Rate</div>
                  <div className="text-2xl font-bold text-green-700">
                    {formatRate(overview.hires_rate?.value)}
                  </div>
                  <div className="mt-1">
                    <ChangeIndicator value={overview.hires_rate?.year_over_year_pct} suffix="% YoY" />
                  </div>
                </div>

                {/* Quits Rate */}
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-xs text-purple-600 font-medium mb-1">Quits Rate</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {formatRate(overview.quits_rate?.value)}
                  </div>
                  <div className="mt-1">
                    <ChangeIndicator value={overview.quits_rate?.year_over_year_pct} suffix="% YoY" />
                  </div>
                </div>

                {/* Layoffs Rate */}
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-xs text-red-600 font-medium mb-1">Layoffs Rate</div>
                  <div className="text-2xl font-bold text-red-700">
                    {formatRate(overview.layoffs_rate?.value)}
                  </div>
                  <div className="mt-1">
                    <ChangeIndicator value={overview.layoffs_rate?.year_over_year_pct} suffix="% YoY" />
                  </div>
                </div>

                {/* Total Separations Rate */}
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-xs text-orange-600 font-medium mb-1">Total Separations</div>
                  <div className="text-2xl font-bold text-orange-700">
                    {formatRate(overview.total_separations_rate?.value)}
                  </div>
                  <div className="mt-1">
                    <ChangeIndicator value={overview.total_separations_rate?.year_over_year_pct} suffix="% YoY" />
                  </div>
                </div>

                {/* Unemployed per Opening */}
                {overview.unemployed_per_opening && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-xs text-gray-600 font-medium mb-1">Unemployed/Opening</div>
                    <div className="text-2xl font-bold text-gray-700">
                      {overview.unemployed_per_opening.value?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {overview.unemployed_per_opening.latest_date}
                    </div>
                  </div>
                )}
              </div>

              {/* Levels Grid */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Levels (Thousands)</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="bg-blue-50/50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Job Openings</div>
                    <div className="text-lg font-semibold text-gray-800">{formatLevel(overview.job_openings_level?.value)}</div>
                  </div>
                  <div className="bg-green-50/50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Hires</div>
                    <div className="text-lg font-semibold text-gray-800">{formatLevel(overview.hires_level?.value)}</div>
                  </div>
                  <div className="bg-purple-50/50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Quits</div>
                    <div className="text-lg font-semibold text-gray-800">{formatLevel(overview.quits_level?.value)}</div>
                  </div>
                  <div className="bg-red-50/50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Layoffs</div>
                    <div className="text-lg font-semibold text-gray-800">{formatLevel(overview.layoffs_level?.value)}</div>
                  </div>
                  <div className="bg-orange-50/50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600">Total Separations</div>
                    <div className="text-lg font-semibold text-gray-800">{formatLevel(overview.total_separations_level?.value)}</div>
                  </div>
                </div>
              </div>

              {/* Timeline Chart */}
              {overviewTimeline?.timeline && overviewTimeline.timeline.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Historical Rates</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={overviewTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="period_name"
                          tick={{ fontSize: 10 }}
                          interval={Math.floor(overviewTimeline.timeline.length / 8)}
                        />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="job_openings_rate" name="Job Openings" stroke="#3b82f6" dot={false} />
                        <Line type="monotone" dataKey="hires_rate" name="Hires" stroke="#10b981" dot={false} />
                        <Line type="monotone" dataKey="quits_rate" name="Quits" stroke="#8b5cf6" dot={false} />
                        <Line type="monotone" dataKey="layoffs_rate" name="Layoffs" stroke="#ef4444" dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <TimelineSelector
                    timeline={overviewTimeline.timeline}
                    selectedIndex={overviewSelectedIndex}
                    onSelectIndex={setOverviewSelectedIndex}
                  />
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 2: Industry Analysis */}
      <Card>
        <SectionHeader title="2. Industry Analysis" color="green" icon={Building2} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Region"
              value={industryState}
              onChange={setIndustryState}
              options={[{ value: '00', label: 'Total US' }, ...stateOptions.filter(o => o.value !== '')]}
              className="w-40"
            />
            <Select
              label="Metric"
              value={industryDataElement}
              onChange={setIndustryDataElement}
              options={dataElementOptions}
              className="w-40"
            />
            <Select
              label="Type"
              value={industryRateLevel}
              onChange={setIndustryRateLevel}
              options={rateLevelOptions}
              className="w-32"
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

          {loadingIndustries ? (
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
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Job Openings</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Hires</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Quits</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Layoffs</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">JO YoY%</th>
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
                          <td className="px-3 py-2 text-right">{formatRate(ind.job_openings_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(ind.hires_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(ind.quits_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(ind.layoffs_rate)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={ind.job_openings_yoy_pct} suffix="%" />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                industryTimeline?.timeline && industryTimeline.timeline.length > 0 && (
                  <>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={industryTimeline.timeline}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="period_name"
                            tick={{ fontSize: 10 }}
                            interval={Math.floor(industryTimeline.timeline.length / 8)}
                          />
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
                    <TimelineSelector
                      timeline={industryTimeline.timeline}
                      selectedIndex={industrySelectedIndex}
                      onSelectIndex={setIndustrySelectedIndex}
                    />
                  </>
                )
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 3: Regional Analysis */}
      <Card>
        <SectionHeader title="3. Regional Analysis" color="cyan" icon={MapPin} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Industry"
              value={regionIndustry}
              onChange={setRegionIndustry}
              options={[{ value: '000000', label: 'Total Nonfarm' }, ...industryOptions.filter(o => o.value !== '')]}
              className="w-48"
            />
            <Select
              label="Metric"
              value={regionDataElement}
              onChange={setRegionDataElement}
              options={dataElementOptions}
              className="w-40"
            />
            <Select
              label="Type"
              value={regionRateLevel}
              onChange={setRegionRateLevel}
              options={rateLevelOptions}
              className="w-32"
            />
            <Select
              label="Time Range"
              value={regionTimeRange}
              onChange={(v) => setRegionTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <div className="flex items-end">
              <ViewToggle value={regionView} onChange={setRegionView} />
            </div>
          </div>

          {loadingRegions ? (
            <LoadingSpinner />
          ) : regions ? (
            <>
              {regionView === 'table' ? (
                <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Region/State</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Job Openings</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Hires</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Quits</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Layoffs</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">JO YoY%</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {regions.regions.map((reg) => (
                        <tr key={reg.state_code} className={`hover:bg-gray-50 ${reg.is_region ? 'bg-blue-50/30' : ''}`}>
                          <td className="px-3 py-2">
                            <input
                              type="checkbox"
                              checked={selectedRegions.includes(reg.state_code)}
                              onChange={() => {
                                setSelectedRegions(prev =>
                                  prev.includes(reg.state_code)
                                    ? prev.filter(c => c !== reg.state_code)
                                    : [...prev, reg.state_code]
                                );
                              }}
                              className="rounded border-gray-300"
                            />
                          </td>
                          <td className="px-3 py-2 font-medium">
                            {reg.is_region ? <span className="text-blue-600">{reg.state_name}</span> : reg.state_name}
                          </td>
                          <td className="px-3 py-2 text-right">{formatRate(reg.job_openings_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(reg.hires_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(reg.quits_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(reg.layoffs_rate)}</td>
                          <td className="px-3 py-2 text-right">
                            <ChangeIndicator value={reg.job_openings_yoy_pct} suffix="%" />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                regionTimeline?.timeline && regionTimeline.timeline.length > 0 && (
                  <>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={regionTimeline.timeline}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="period_name"
                            tick={{ fontSize: 10 }}
                            interval={Math.floor(regionTimeline.timeline.length / 8)}
                          />
                          <YAxis tick={{ fontSize: 10 }} />
                          <Tooltip />
                          <Legend />
                          {selectedRegions.map((code, idx) => (
                            <Line
                              key={code}
                              type="monotone"
                              dataKey={`regions.${code}`}
                              name={regionTimeline.region_names?.[code] || code}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              dot={false}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <TimelineSelector
                      timeline={regionTimeline.timeline}
                      selectedIndex={regionSelectedIndex}
                      onSelectIndex={setRegionSelectedIndex}
                    />
                  </>
                )
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 4: Size Class Analysis */}
      <Card>
        <SectionHeader title="4. Size Class Analysis" color="purple" icon={Users} />
        <div className="p-5">
          <p className="text-sm text-gray-600 mb-4">
            JOLTS data by establishment size (available for Total Nonfarm, Total US only)
          </p>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Metric"
              value={sizeClassDataElement}
              onChange={setSizeClassDataElement}
              options={dataElementOptions}
              className="w-40"
            />
            <Select
              label="Type"
              value={sizeClassRateLevel}
              onChange={setSizeClassRateLevel}
              options={rateLevelOptions}
              className="w-32"
            />
            <Select
              label="Time Range"
              value={sizeClassTimeRange}
              onChange={(v) => setSizeClassTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <div className="flex items-end">
              <ViewToggle value={sizeClassView} onChange={setSizeClassView} />
            </div>
          </div>

          {loadingSizeClasses ? (
            <LoadingSpinner />
          ) : sizeClasses ? (
            <>
              {sizeClassView === 'table' ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Select</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">Size Class</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Job Openings</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Hires</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Quits</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Layoffs</th>
                        <th className="px-3 py-2 text-right font-medium text-gray-600">Total Sep.</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {sizeClasses.size_classes.map((sc) => (
                        <tr key={sc.sizeclass_code} className="hover:bg-gray-50">
                          <td className="px-3 py-2">
                            <input
                              type="checkbox"
                              checked={selectedSizeClasses.includes(sc.sizeclass_code)}
                              onChange={() => {
                                setSelectedSizeClasses(prev =>
                                  prev.includes(sc.sizeclass_code)
                                    ? prev.filter(c => c !== sc.sizeclass_code)
                                    : [...prev, sc.sizeclass_code]
                                );
                              }}
                              className="rounded border-gray-300"
                            />
                          </td>
                          <td className="px-3 py-2 font-medium">{sc.sizeclass_name}</td>
                          <td className="px-3 py-2 text-right">{formatRate(sc.job_openings_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(sc.hires_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(sc.quits_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(sc.layoffs_rate)}</td>
                          <td className="px-3 py-2 text-right">{formatRate(sc.total_separations_rate)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                sizeClassTimeline?.timeline && sizeClassTimeline.timeline.length > 0 && (
                  <>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={sizeClassTimeline.timeline}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="period_name"
                            tick={{ fontSize: 10 }}
                            interval={Math.floor(sizeClassTimeline.timeline.length / 8)}
                          />
                          <YAxis tick={{ fontSize: 10 }} />
                          <Tooltip />
                          <Legend />
                          {selectedSizeClasses.map((code, idx) => (
                            <Line
                              key={code}
                              type="monotone"
                              dataKey={`size_classes.${code}`}
                              name={sizeClassTimeline.sizeclass_names?.[code] || code}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              dot={false}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <TimelineSelector
                      timeline={sizeClassTimeline.timeline}
                      selectedIndex={sizeClassSelectedIndex}
                      onSelectIndex={setSizeClassSelectedIndex}
                    />
                  </>
                )
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 5: Top Movers */}
      <Card>
        <SectionHeader title="5. Top Movers" color="orange" icon={TrendingUp} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <Select
              label="Metric"
              value={moverDataElement}
              onChange={setMoverDataElement}
              options={dataElementOptions}
              className="w-40"
            />
            <Select
              label="Period"
              value={moverPeriod}
              onChange={(v) => setMoverPeriod(v as MoverPeriod)}
              options={[
                { value: 'mom', label: 'Month over Month' },
                { value: 'yoy', label: 'Year over Year' },
              ]}
              className="w-40"
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
                      <div>
                        <div className="font-medium text-gray-800">{m.industry_name}</div>
                        <div className="text-xs text-gray-500">{formatRate(m.value)}</div>
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
                      <div>
                        <div className="font-medium text-gray-800">{m.industry_name}</div>
                        <div className="text-xs text-gray-500">{formatRate(m.value)}</div>
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

      {/* Section 6: Series Detail Explorer */}
      <Card>
        <SectionHeader title="6. Series Detail Explorer" color="red" icon={Briefcase} />
        <div className="p-5 space-y-6">
          {/* Sub-section A: Search by Keyword */}
          <div className="border-l-4 border-cyan-500 pl-4">
            <h3 className="text-lg font-semibold bg-gradient-to-r from-cyan-600 to-cyan-400 bg-clip-text text-transparent mb-3">
              Search by Keyword
            </h3>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                placeholder="Search by industry or state name..."
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
                      <th className="px-3 py-2 text-left">Industry</th>
                      <th className="px-3 py-2 text-left">State</th>
                      <th className="px-3 py-2 text-left">Element</th>
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
                        <td className="px-3 py-2">{s.industry_name}</td>
                        <td className="px-3 py-2">{s.state_name}</td>
                        <td className="px-3 py-2">{s.dataelement_name}</td>
                        <td className="px-3 py-2">{s.ratelevel_name}</td>
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
                label="Industry"
                value={drillIndustry}
                onChange={setDrillIndustry}
                options={industryOptions}
                className="w-48"
              />
              <Select
                label="State/Region"
                value={drillState}
                onChange={setDrillState}
                options={stateOptions}
                className="w-40"
              />
              <Select
                label="Data Element"
                value={drillDataElement}
                onChange={setDrillDataElement}
                options={[{ value: '', label: 'All Elements' }, ...dataElementOptions]}
                className="w-40"
              />
              <Select
                label="Rate/Level"
                value={drillRateLevel}
                onChange={setDrillRateLevel}
                options={[{ value: '', label: 'Both' }, ...rateLevelOptions]}
                className="w-32"
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
                      <th className="px-3 py-2 text-left">Industry</th>
                      <th className="px-3 py-2 text-left">State</th>
                      <th className="px-3 py-2 text-left">Element</th>
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
                        <td className="px-3 py-2">{s.industry_name}</td>
                        <td className="px-3 py-2">{s.state_name}</td>
                        <td className="px-3 py-2">{s.dataelement_name}</td>
                        <td className="px-3 py-2">{s.ratelevel_name}</td>
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
                label="Industry"
                value={browseIndustry}
                onChange={(v) => { setBrowseIndustry(v); setBrowseOffset(0); }}
                options={industryOptions}
                className="w-48"
              />
              <Select
                label="State"
                value={browseState}
                onChange={(v) => { setBrowseState(v); setBrowseOffset(0); }}
                options={stateOptions}
                className="w-40"
              />
              <Select
                label="Data Element"
                value={browseDataElement}
                onChange={(v) => { setBrowseDataElement(v); setBrowseOffset(0); }}
                options={[{ value: '', label: 'All' }, ...dataElementOptions]}
                className="w-40"
              />
              <Select
                label="Seasonal"
                value={browseSeasonal}
                onChange={(v) => { setBrowseSeasonal(v); setBrowseOffset(0); }}
                options={[
                  { value: '', label: 'All' },
                  { value: 'S', label: 'Seasonally Adjusted' },
                  { value: 'U', label: 'Unadjusted' },
                ]}
                className="w-44"
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
                <div className="max-h-[1000px] overflow-y-auto border rounded-md">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left">Select</th>
                        <th className="px-3 py-2 text-left">Series ID</th>
                        <th className="px-3 py-2 text-left">Industry</th>
                        <th className="px-3 py-2 text-left">State</th>
                        <th className="px-3 py-2 text-left">Element</th>
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
                          <td className="px-3 py-2">{s.industry_name}</td>
                          <td className="px-3 py-2">{s.state_name}</td>
                          <td className="px-3 py-2">{s.dataelement_name}</td>
                          <td className="px-3 py-2">{s.ratelevel_name}</td>
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
                            name={info ? `${info.industry_name} - ${info.dataelement_name} (${info.ratelevel_name})` : seriesId}
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
                              {info ? `${info.dataelement_name} (${info.ratelevel_name})` : seriesId}
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
                          .slice(0, 60)
                          .map(([period, values]) => (
                            <tr key={period} className="hover:bg-gray-50">
                              <td className="px-3 py-2">{period}</td>
                              {selectedSeriesIds.map((seriesId) => (
                                <td key={seriesId} className="px-3 py-2 text-right">
                                  {values[seriesId]?.toFixed(1) ?? 'N/A'}
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
