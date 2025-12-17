import { useState, useEffect, useMemo, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, BarChart, Bar
} from 'recharts';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import {
  TrendingUp, TrendingDown, Loader2, DollarSign, Home, Car, Utensils,
  Shirt, Heart, Gamepad2, GraduationCap, ShoppingBag, Zap,
  Search, MapPin, LucideIcon, X
} from 'lucide-react';
import { cwResearchAPI } from '../../services/api';
import { getAreaCoordinates } from '../../utils/areaCoordinates';
import 'leaflet/dist/leaflet.css';

/**
 * CW Explorer - CPI for Urban Wage Earners & Clerical Workers
 *
 * CPI-W is used for:
 * - Social Security COLA adjustments (Q3 average)
 * - Federal civil service retirees
 * - Military retirees
 * - Food stamp program benefits
 *
 * Sections:
 * 1. Key Inflation Metrics - Headline & Core CPI-W with summary
 * 2. Inflation Timeline - Headline vs Core with timeline selector
 * 3. Expenditure Categories - 8 major categories with timeline
 * 4. Geographic View - Map with clickable metro areas
 * 5. Area Comparison - Table comparison across regions
 * 6. Top Movers - Largest CPI changes
 * 7. Series Explorer - Search, Drill-down, Browse methods
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface CWArea {
  area_code: string;
  area_name: string;
  display_level: number;
  selectable: boolean;
  sort_sequence: number;
}

interface CWItem {
  item_code: string;
  item_name: string;
  display_level: number;
  selectable: boolean;
  sort_sequence: number;
}

interface DimensionsData {
  areas: CWArea[];
  items: CWItem[];
  total_series: number;
  data_range?: string;
}

interface InflationMetric {
  series_id: string;
  item_code: string;
  item_name: string;
  latest_value?: number;
  latest_date?: string;
  month_over_month?: number;
  year_over_year?: number;
}

interface OverviewData {
  headline_cpi?: InflationMetric;
  core_cpi?: InflationMetric;
  food_beverages?: InflationMetric;
  housing?: InflationMetric;
  apparel?: InflationMetric;
  transportation?: InflationMetric;
  medical_care?: InflationMetric;
  recreation?: InflationMetric;
  education_communication?: InflationMetric;
  other_goods_services?: InflationMetric;
  energy?: InflationMetric;
  last_updated?: string;
}

interface TimelineDataPoint {
  year: number;
  period: string;
  period_name: string;
  date: string;
  headline_value?: number;
  headline_yoy?: number;
  headline_mom?: number;
  core_value?: number;
  core_yoy?: number;
  core_mom?: number;
}

interface OverviewTimelineData {
  area_code: string;
  area_name: string;
  timeline: TimelineDataPoint[];
}

interface CategoryMetric {
  category_code: string;
  category_name: string;
  series_id: string;
  latest_value?: number;
  latest_date?: string;
  month_over_month?: number;
  year_over_year?: number;
}

interface CategoryAnalysisData {
  area_code: string;
  area_name: string;
  categories: CategoryMetric[];
}

interface CategoryTimelineItem {
  category_code: string;
  category_name: string;
  series_id: string;
  data: { date: string; value?: number; yoy?: number }[];
}

interface CategoryTimelineData {
  area_code: string;
  area_name: string;
  categories: CategoryTimelineItem[];
}

interface AreaComparisonMetric {
  area_code: string;
  area_name: string;
  area_type?: string;
  series_id: string;
  latest_value?: number;
  latest_date?: string;
  month_over_month?: number;
  year_over_year?: number;
}

interface AreaComparisonData {
  item_code: string;
  item_name: string;
  areas: AreaComparisonMetric[];
}

interface CWTopMover {
  series_id: string;
  item_code: string;
  item_name: string;
  area_name?: string;
  latest_value?: number;
  change?: number;
  pct_change?: number;
  direction: string;
}

interface TopMoversData {
  period: string;
  latest_date?: string;
  gainers: CWTopMover[];
  losers: CWTopMover[];
}

interface CWSeriesInfo {
  series_id: string;
  series_title: string;
  area_code: string;
  area_name: string;
  item_code: string;
  item_name: string;
  seasonal_code: string;
  periodicity_code?: string;
  base_period?: string;
  begin_year?: number;
  end_year?: number;
  is_active: boolean;
}

interface SeriesListData {
  total: number;
  limit: number;
  offset: number;
  series: CWSeriesInfo[];
}

interface CWDataPoint {
  year: number;
  period: string;
  period_name: string;
  value?: number;
}

interface CWSeriesData {
  series_id: string;
  series_title: string;
  area_name: string;
  item_name: string;
  data_points: CWDataPoint[];
}

interface SeriesDataResponse {
  series: CWSeriesData[];
}

interface MapAreaData {
  area_code: string;
  area_name: string;
  lat: number;
  lng: number;
  latest_value?: number;
  yoy?: number;
  mom?: number;
  displayValue?: number;
  color: string;
}

type MoverPeriod = 'mom' | 'yoy';
type ViewType = 'chart' | 'table';

// ============================================================================
// CONSTANTS
// ============================================================================

const CHART_COLORS = [
  '#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#9333ea',
  '#0891b2', '#c026d3', '#ea580c', '#4f46e5', '#059669'
];

const TIME_RANGE_OPTIONS = [
  { value: 12, label: 'Last 12 months' },
  { value: 24, label: 'Last 2 years' },
  { value: 60, label: 'Last 5 years' },
  { value: 120, label: 'Last 10 years' },
  { value: 240, label: 'Last 20 years' },
  { value: 0, label: 'All Time' },
];

type SectionColor = 'blue' | 'green' | 'orange' | 'purple' | 'cyan' | 'red';

const CATEGORY_ICONS: Record<string, LucideIcon> = {
  'SAF': Utensils,
  'SAH': Home,
  'SAA': Shirt,
  'SAT': Car,
  'SAM': Heart,
  'SAR': Gamepad2,
  'SAE': GraduationCap,
  'SAG': ShoppingBag,
  'SA0E': Zap,
};

const CPI_CATEGORIES = [
  { value: 'SA0', label: 'All items' },
  { value: 'SA0L1E', label: 'Core (less food & energy)' },
  { value: 'SAF', label: 'Food and beverages' },
  { value: 'SAH', label: 'Housing' },
  { value: 'SAA', label: 'Apparel' },
  { value: 'SAT', label: 'Transportation' },
  { value: 'SAM', label: 'Medical care' },
  { value: 'SAR', label: 'Recreation' },
  { value: 'SAE', label: 'Education & Communication' },
  { value: 'SAG', label: 'Other goods & services' },
  { value: 'SA0E', label: 'Energy' },
];

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getInflationColor(value: number | null | undefined): string {
  if (value === null || value === undefined) return '#9ca3af';
  if (value < 0) return '#22c55e';
  if (value < 1) return '#86efac';
  if (value < 2) return '#bef264';
  if (value < 3) return '#fde047';
  if (value < 4) return '#fb923c';
  if (value < 5) return '#f87171';
  return '#ef4444';
}

function formatPct(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

function formatPeriod(periodCode: string | undefined | null): string {
  if (!periodCode) return '';
  const monthMap: Record<string, string> = {
    'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
    'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
    'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
  };
  return monthMap[periodCode] || periodCode;
}

// ============================================================================
// UI COMPONENTS
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
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  className?: string;
}

function Select({ label, value, onChange, options, className = '' }: SelectProps): ReactElement {
  return (
    <div className={className}>
      {label && <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

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

interface ButtonGroupProps {
  options: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
}

const ButtonGroup = ({ options, value, onChange }: ButtonGroupProps): ReactElement => (
  <div className="flex border border-gray-300 rounded-md overflow-hidden">
    {options.map((opt) => (
      <button
        key={opt.value}
        onClick={() => onChange(opt.value)}
        className={`px-3 py-1 text-sm ${value === opt.value ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
      >
        {opt.label}
      </button>
    ))}
  </div>
);

function LoadingSpinner(): ReactElement {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
    </div>
  );
}

function PctBadge({ value }: { value: number | null | undefined }): ReactElement {
  if (value === null || value === undefined) {
    return <span className="text-gray-400">N/A</span>;
  }
  const isPositive = value >= 0;
  return (
    <span className={`inline-flex items-center gap-0.5 text-xs font-medium ${
      isPositive ? 'text-red-600' : 'text-green-600'
    }`}>
      {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
      {formatPct(value)}
    </span>
  );
}

interface TimelinePoint {
  year?: number;
  period?: string;
  period_name?: string;
  date?: string;
}

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

            // Support both formats: {year, period} or {date: "2024-01"}
            const displayLabel = point.date
              ? point.date
              : `${formatPeriod(point.period)} ${point.year}`;
            const pointKey = point.date || `${point.year}-${point.period}`;

            return (
              <div
                key={pointKey}
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
                    {displayLabel}
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

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function CWExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);

  // Overview
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewArea, setOverviewArea] = useState('0000');

  // Overview Timeline
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [loadingTimeline, setLoadingTimeline] = useState(true);
  const [timelineMonths, setTimelineMonths] = useState(24);
  const [timelineSelectedIndex, setTimelineSelectedIndex] = useState<number | null>(null);

  // Category Analysis
  const [categoryData, setCategoryData] = useState<CategoryAnalysisData | null>(null);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [categoryView, setCategoryView] = useState<ViewType>('chart');

  // Category Timeline
  const [categoryTimeline, setCategoryTimeline] = useState<CategoryTimelineData | null>(null);
  const [loadingCategoryTimeline, setLoadingCategoryTimeline] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['SAF', 'SAH', 'SAT', 'SAM']);
  const [categoryTimelineMonths, setCategoryTimelineMonths] = useState(24);
  const [categorySelectedIndex, setCategorySelectedIndex] = useState<number | null>(null);

  // Geographic Map
  const [mapItem, setMapItem] = useState('SA0');
  const [mapMetric, setMapMetric] = useState<'yoy' | 'mom'>('yoy');
  const [areaComparison, setAreaComparison] = useState<AreaComparisonData | null>(null);
  const [loadingMap, setLoadingMap] = useState(false);
  const [mapSelectedSeries, setMapSelectedSeries] = useState<string[]>([]);
  const [mapSeriesData, setMapSeriesData] = useState<Record<string, SeriesDataResponse>>({});

  // Area Comparison Table
  const [comparisonItem, setComparisonItem] = useState('SA0');
  const [loadingAreaComparison, setLoadingAreaComparison] = useState(false);

  // Top Movers
  const [topMovers, setTopMovers] = useState<TopMoversData | null>(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(true);
  const [moverPeriod, setMoverPeriod] = useState<MoverPeriod>('yoy');

  // Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Series Explorer - Drill-down
  const [drillArea, setDrillArea] = useState('');
  const [drillItem, setDrillItem] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);

  // Series Explorer - Browse
  const [browseArea, setBrowseArea] = useState('');
  const [browseSeasonal, setBrowseSeasonal] = useState('');
  const [browseLimit, setBrowseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series Explorer - Shared Chart
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<Record<string, SeriesDataResponse>>({});
  const [seriesTimeRange, setSeriesTimeRange] = useState(60);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');

  // ============================================================================
  // DATA LOADING
  // ============================================================================

  // Load dimensions
  useEffect(() => {
    const load = async () => {
      try {
        const res = await cwResearchAPI.getDimensions<DimensionsData>();
        setDimensions(res.data);
      } catch (error) {
        console.error('Failed to load dimensions:', error);
      }
    };
    load();
  }, []);

  // Load overview
  useEffect(() => {
    const load = async () => {
      setLoadingOverview(true);
      try {
        const res = await cwResearchAPI.getOverview<OverviewData>(overviewArea);
        setOverview(res.data);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
  }, [overviewArea]);

  // Load overview timeline
  useEffect(() => {
    const load = async () => {
      setLoadingTimeline(true);
      try {
        const res = await cwResearchAPI.getOverviewTimeline<OverviewTimelineData>(overviewArea, timelineMonths);
        setOverviewTimeline(res.data);
        setTimelineSelectedIndex(null);
      } catch (error) {
        console.error('Failed to load timeline:', error);
      } finally {
        setLoadingTimeline(false);
      }
    };
    load();
  }, [overviewArea, timelineMonths]);

  // Load categories
  useEffect(() => {
    const load = async () => {
      setLoadingCategories(true);
      try {
        const res = await cwResearchAPI.getCategories<CategoryAnalysisData>(overviewArea);
        setCategoryData(res.data);
      } catch (error) {
        console.error('Failed to load categories:', error);
      } finally {
        setLoadingCategories(false);
      }
    };
    load();
  }, [overviewArea]);

  // Load category timeline
  useEffect(() => {
    const load = async () => {
      setLoadingCategoryTimeline(true);
      try {
        const res = await cwResearchAPI.getCategoryTimeline<CategoryTimelineData>(overviewArea, categoryTimelineMonths);
        setCategoryTimeline(res.data);
        setCategorySelectedIndex(null);
      } catch (error) {
        console.error('Failed to load category timeline:', error);
      } finally {
        setLoadingCategoryTimeline(false);
      }
    };
    load();
  }, [overviewArea, categoryTimelineMonths]);

  // Load area comparison (for both map and table)
  useEffect(() => {
    const load = async () => {
      setLoadingMap(true);
      setLoadingAreaComparison(true);
      try {
        const res = await cwResearchAPI.compareAreas<AreaComparisonData>(mapItem);
        setAreaComparison(res.data);
      } catch (error) {
        console.error('Failed to load area comparison:', error);
      } finally {
        setLoadingMap(false);
        setLoadingAreaComparison(false);
      }
    };
    load();
  }, [mapItem]);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await cwResearchAPI.getTopMovers<TopMoversData>(moverPeriod, overviewArea, 10);
        setTopMovers(res.data);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [moverPeriod, overviewArea]);

  // Load map selected series data
  useEffect(() => {
    const load = async () => {
      const newData: Record<string, SeriesDataResponse> = {};
      for (const seriesId of mapSelectedSeries) {
        if (!mapSeriesData[seriesId]) {
          try {
            const res = await cwResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, 60);
            newData[seriesId] = res.data;
          } catch (error) {
            console.error(`Failed to load series ${seriesId}:`, error);
          }
        }
      }
      if (Object.keys(newData).length > 0) {
        setMapSeriesData(prev => ({ ...prev, ...newData }));
      }
    };
    if (mapSelectedSeries.length > 0) {
      load();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapSelectedSeries]);

  // Load browse results
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseArea) params.area_code = browseArea;
        if (browseSeasonal) params.seasonal_code = browseSeasonal;
        const res = await cwResearchAPI.getSeries<SeriesListData>(params);
        setBrowseResults(res.data);
      } catch (error) {
        console.error('Failed to load browse results:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    load();
  }, [browseArea, browseSeasonal, browseLimit, browseOffset]);

  // Load selected series data
  useEffect(() => {
    const load = async () => {
      const newData: Record<string, SeriesDataResponse> = {};
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const res = await cwResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, seriesTimeRange);
            newData[seriesId] = res.data;
          } catch (error) {
            console.error(`Failed to load series ${seriesId}:`, error);
          }
        }
      }
      if (Object.keys(newData).length > 0) {
        setSeriesChartData(prev => ({ ...prev, ...newData }));
      }
    };
    if (selectedSeriesIds.length > 0) {
      load();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSeriesIds]);

  // ============================================================================
  // COMPUTED DATA
  // ============================================================================

  // Map areas with coordinates and colors
  const mapAreas = useMemo((): MapAreaData[] => {
    if (!areaComparison?.areas) return [];

    const result: MapAreaData[] = [];
    for (const area of areaComparison.areas) {
      const coords = getAreaCoordinates(area.area_code);
      if (!coords) continue;

      const displayValue = mapMetric === 'yoy' ? area.year_over_year : area.month_over_month;
      result.push({
        area_code: area.area_code,
        area_name: area.area_name,
        lat: coords.lat,
        lng: coords.lng,
        latest_value: area.latest_value,
        yoy: area.year_over_year,
        mom: area.month_over_month,
        displayValue,
        color: getInflationColor(displayValue),
      });
    }
    return result;
  }, [areaComparison, mapMetric]);

  // Timeline point data when slider is used
  const timelinePointData = useMemo(() => {
    if (!overviewTimeline?.timeline || timelineSelectedIndex === null) return null;
    return overviewTimeline.timeline[timelineSelectedIndex];
  }, [overviewTimeline, timelineSelectedIndex]);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await cwResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 100 });
      setSearchResults(res.data);
    } catch (error) {
      console.error('Failed to search:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleSearchKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  const handleDrillDown = async () => {
    if (!drillArea && !drillItem) return;
    setLoadingDrill(true);
    try {
      const params: Record<string, unknown> = { limit: 200 };
      if (drillArea) params.area_code = drillArea;
      if (drillItem) params.item_code = drillItem;
      const res = await cwResearchAPI.getSeries<SeriesListData>(params);
      setDrillResults(res.data);
    } catch (error) {
      console.error('Failed to drill-down:', error);
    } finally {
      setLoadingDrill(false);
    }
  };

  const toggleSeriesSelection = (seriesId: string) => {
    if (selectedSeriesIds.includes(seriesId)) {
      setSelectedSeriesIds(selectedSeriesIds.filter(id => id !== seriesId));
    } else if (selectedSeriesIds.length < 5) {
      setSelectedSeriesIds([...selectedSeriesIds, seriesId]);
    }
  };

  const toggleCategory = (code: string) => {
    setSelectedCategories(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : [...prev, code]
    );
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-5">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <DollarSign className="w-6 h-6 text-blue-600" />
              CPI-W: Urban Wage Earners & Clerical Workers
            </h1>
            <p className="text-gray-600 mt-1">
              Used for Social Security COLA adjustments, federal retirees, and food stamp benefits
            </p>
          </div>
          <div className="text-right text-sm text-gray-500">
            {overview?.last_updated && <div>Data through: <span className="font-medium">{overview.last_updated}</span></div>}
            {dimensions && (
              <div className="mt-1">
                {dimensions.total_series.toLocaleString()} series | {dimensions.data_range}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Section 1: Key Inflation Metrics */}
      <Card>
        <SectionHeader title="Key Inflation Metrics" color="blue" icon={TrendingUp} />
        <div className="p-5">
          <div className="mb-4">
            <Select
              label="Area"
              value={overviewArea}
              onChange={setOverviewArea}
              options={[
                { value: '0000', label: 'U.S. city average' },
                ...(dimensions?.areas?.filter(a => a.area_code !== '0000').slice(0, 30).map(a => ({
                  value: a.area_code,
                  label: a.area_name
                })) || [])
              ]}
              className="w-72"
            />
          </div>

          {loadingOverview ? (
            <LoadingSpinner />
          ) : overview ? (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {/* Headline CPI */}
              {overview.headline_cpi && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div className="text-xs font-medium text-blue-600 mb-1">Headline CPI-W</div>
                  <div className="text-2xl font-bold text-blue-900">{overview.headline_cpi.latest_value?.toFixed(1)}</div>
                  <div className="mt-2 space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">MoM:</span>
                      <PctBadge value={overview.headline_cpi.month_over_month} />
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">YoY:</span>
                      <PctBadge value={overview.headline_cpi.year_over_year} />
                    </div>
                  </div>
                </div>
              )}

              {/* Core CPI */}
              {overview.core_cpi && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <div className="text-xs font-medium text-green-600 mb-1">Core CPI-W</div>
                  <div className="text-2xl font-bold text-green-900">{overview.core_cpi.latest_value?.toFixed(1)}</div>
                  <div className="mt-2 space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">MoM:</span>
                      <PctBadge value={overview.core_cpi.month_over_month} />
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">YoY:</span>
                      <PctBadge value={overview.core_cpi.year_over_year} />
                    </div>
                  </div>
                </div>
              )}

              {/* Energy */}
              {overview.energy && (
                <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                  <div className="text-xs font-medium text-yellow-600 mb-1 flex items-center gap-1">
                    <Zap className="w-3 h-3" /> Energy
                  </div>
                  <div className="text-xl font-bold text-yellow-900">{overview.energy.latest_value?.toFixed(1)}</div>
                  <div className="mt-2 flex justify-between text-xs">
                    <span className="text-gray-500">YoY:</span>
                    <PctBadge value={overview.energy.year_over_year} />
                  </div>
                </div>
              )}

              {/* Food */}
              {overview.food_beverages && (
                <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                  <div className="text-xs font-medium text-orange-600 mb-1 flex items-center gap-1">
                    <Utensils className="w-3 h-3" /> Food
                  </div>
                  <div className="text-xl font-bold text-orange-900">{overview.food_beverages.latest_value?.toFixed(1)}</div>
                  <div className="mt-2 flex justify-between text-xs">
                    <span className="text-gray-500">YoY:</span>
                    <PctBadge value={overview.food_beverages.year_over_year} />
                  </div>
                </div>
              )}

              {/* Housing */}
              {overview.housing && (
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <div className="text-xs font-medium text-purple-600 mb-1 flex items-center gap-1">
                    <Home className="w-3 h-3" /> Housing
                  </div>
                  <div className="text-xl font-bold text-purple-900">{overview.housing.latest_value?.toFixed(1)}</div>
                  <div className="mt-2 flex justify-between text-xs">
                    <span className="text-gray-500">YoY:</span>
                    <PctBadge value={overview.housing.year_over_year} />
                  </div>
                </div>
              )}

              {/* Transportation */}
              {overview.transportation && (
                <div className="bg-cyan-50 rounded-lg p-4 border border-cyan-200">
                  <div className="text-xs font-medium text-cyan-600 mb-1 flex items-center gap-1">
                    <Car className="w-3 h-3" /> Transportation
                  </div>
                  <div className="text-xl font-bold text-cyan-900">{overview.transportation.latest_value?.toFixed(1)}</div>
                  <div className="mt-2 flex justify-between text-xs">
                    <span className="text-gray-500">YoY:</span>
                    <PctBadge value={overview.transportation.year_over_year} />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 2: Inflation Timeline */}
      <Card>
        <SectionHeader title="Inflation Timeline (YoY %)" color="green" icon={TrendingUp} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end">
            <Select
              label="Time Range"
              value={timelineMonths.toString()}
              onChange={(v) => setTimelineMonths(parseInt(v))}
              options={TIME_RANGE_OPTIONS.map(o => ({ value: o.value.toString(), label: o.label }))}
              className="w-40"
            />
            {timelinePointData && (
              <div className="text-sm bg-blue-50 px-3 py-1 rounded border border-blue-200">
                <span className="font-medium">{timelinePointData.date}:</span>{' '}
                Headline {timelinePointData.headline_yoy?.toFixed(2)}% | Core {timelinePointData.core_yoy?.toFixed(2)}%
              </div>
            )}
          </div>

          {loadingTimeline ? (
            <LoadingSpinner />
          ) : overviewTimeline?.timeline && overviewTimeline.timeline.length > 0 ? (
            <>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={overviewTimeline.timeline} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                    <Tooltip formatter={(value: number) => [`${value?.toFixed(2)}%`]} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="headline_yoy"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={false}
                      name="Headline CPI-W"
                    />
                    <Line
                      type="monotone"
                      dataKey="core_yoy"
                      stroke="#16a34a"
                      strokeWidth={2}
                      dot={false}
                      name="Core CPI-W"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <TimelineSelector
                timeline={overviewTimeline.timeline}
                selectedIndex={timelineSelectedIndex}
                onSelectIndex={setTimelineSelectedIndex}
              />
            </>
          ) : (
            <div className="text-center text-gray-500">No timeline data available</div>
          )}
        </div>
      </Card>

      {/* Section 3: Expenditure Categories */}
      <Card>
        <SectionHeader title="Expenditure Categories" color="orange" icon={ShoppingBag} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end flex-wrap">
            <ViewToggle value={categoryView} onChange={setCategoryView} />
            <Select
              label="Timeline Range"
              value={categoryTimelineMonths.toString()}
              onChange={(v) => setCategoryTimelineMonths(parseInt(v))}
              options={TIME_RANGE_OPTIONS.map(o => ({ value: o.value.toString(), label: o.label }))}
              className="w-40"
            />
          </div>

          {/* Category chips for selection */}
          <div className="flex flex-wrap gap-2 mb-4">
            {categoryData?.categories.map((cat) => {
              const Icon = CATEGORY_ICONS[cat.category_code] || ShoppingBag;
              const isSelected = selectedCategories.includes(cat.category_code);
              return (
                <button
                  key={cat.category_code}
                  onClick={() => toggleCategory(cat.category_code)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-full flex items-center gap-1 transition-colors ${
                    isSelected
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  {cat.category_name.split(' ')[0]}
                </button>
              );
            })}
          </div>

          {loadingCategories ? (
            <LoadingSpinner />
          ) : categoryData?.categories && categoryData.categories.length > 0 ? (
            categoryView === 'table' ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600">Category</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">Index</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">MoM %</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">YoY %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {categoryData.categories.map((cat) => {
                      const Icon = CATEGORY_ICONS[cat.category_code] || ShoppingBag;
                      return (
                        <tr key={cat.category_code} className="hover:bg-gray-50">
                          <td className="px-4 py-2">
                            <div className="flex items-center gap-2">
                              <Icon className="w-4 h-4 text-gray-400" />
                              <span className="text-sm text-gray-800">{cat.category_name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                            {cat.latest_value?.toFixed(1)}
                          </td>
                          <td className="px-4 py-2 text-right">
                            <PctBadge value={cat.month_over_month} />
                          </td>
                          <td className="px-4 py-2 text-right">
                            <PctBadge value={cat.year_over_year} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={categoryData.categories.map(c => ({
                      name: c.category_name.substring(0, 15),
                      yoy: c.year_over_year || 0,
                    }))}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tickFormatter={(v) => `${v}%`} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={110} />
                    <Tooltip formatter={(value: number) => [`${value.toFixed(2)}%`, 'YoY Change']} />
                    <Bar dataKey="yoy" fill="#3b82f6" name="YoY %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )
          ) : (
            <div className="text-center text-gray-500">No category data available</div>
          )}

          {/* Category Timeline Chart */}
          {!loadingCategoryTimeline && categoryTimeline?.categories && selectedCategories.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-4">Category Trends Over Time</h4>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      type="category"
                      allowDuplicatedCategory={false}
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                    <Tooltip formatter={(value: number) => [`${value?.toFixed(2)}%`]} />
                    <Legend />
                    {categoryTimeline.categories
                      .filter(c => selectedCategories.includes(c.category_code))
                      .map((cat, idx) => (
                        <Line
                          key={cat.category_code}
                          data={cat.data}
                          type="monotone"
                          dataKey="yoy"
                          stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                          strokeWidth={2}
                          dot={false}
                          name={cat.category_name.split(' ')[0]}
                        />
                      ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {categoryTimeline.categories.length > 0 && categoryTimeline.categories[0].data.length > 0 && (
                <TimelineSelector
                  timeline={categoryTimeline.categories[0].data.map(d => ({ date: d.date }))}
                  selectedIndex={categorySelectedIndex}
                  onSelectIndex={setCategorySelectedIndex}
                />
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Section 4: Geographic View */}
      <Card>
        <SectionHeader title="Geographic View" color="purple" icon={MapPin} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end">
            <Select
              label="CPI Category"
              value={mapItem}
              onChange={setMapItem}
              options={CPI_CATEGORIES}
              className="w-64"
            />
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Metric</label>
              <ButtonGroup
                options={[
                  { value: 'yoy', label: 'Year-over-Year' },
                  { value: 'mom', label: 'Month-over-Month' },
                ]}
                value={mapMetric}
                onChange={(v) => setMapMetric(v as 'yoy' | 'mom')}
              />
            </div>
          </div>

          {loadingMap ? (
            <LoadingSpinner />
          ) : (
            <>
              <p className="text-xs text-gray-500 mb-3">Click on a metro area to add it to the comparison chart below</p>

              {/* Color legend */}
              <div className="flex items-center gap-2 mb-4 flex-wrap">
                <span className="text-xs font-medium text-gray-600">Legend:</span>
                {[
                  { label: '< 0%', color: '#22c55e' },
                  { label: '0-1%', color: '#86efac' },
                  { label: '1-2%', color: '#bef264' },
                  { label: '2-3%', color: '#fde047' },
                  { label: '3-4%', color: '#fb923c' },
                  { label: '4-5%', color: '#f87171' },
                  { label: '> 5%', color: '#ef4444' },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-1">
                    <div className="w-4 h-4 rounded-full border border-white" style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-gray-600">{item.label}</span>
                  </div>
                ))}
              </div>

              {/* Map */}
              <div className="h-[450px] rounded-lg border border-gray-200 overflow-hidden">
                <MapContainer
                  center={[39.8283, -98.5795]}
                  zoom={4}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {mapAreas.map(area => {
                    const isUSAverage = area.area_code === '0000';
                    return (
                      <CircleMarker
                        key={area.area_code}
                        center={[area.lat, area.lng]}
                        radius={isUSAverage ? 15 : 10}
                        fillColor={area.color}
                        color={isUSAverage ? '#fbbf24' : '#fff'}
                        weight={isUSAverage ? 3 : 2}
                        fillOpacity={0.8}
                        eventHandlers={{
                          click: () => {
                            const seasonal_code = area.area_code === '0000' ? 'S' : 'U';
                            const series_id = `CW${seasonal_code}R${area.area_code}${mapItem}`;
                            if (!mapSelectedSeries.includes(series_id) && mapSelectedSeries.length < 5) {
                              setMapSelectedSeries([...mapSelectedSeries, series_id]);
                            }
                          },
                        }}
                      >
                        <Popup>
                          <div className="p-1">
                            <div className="font-semibold text-sm">
                              {area.area_name}
                              {isUSAverage && ' (National)'}
                            </div>
                            <div className="text-xs text-gray-500">{areaComparison?.item_name}</div>
                            <div className="text-sm mt-1">
                              <strong>{mapMetric === 'yoy' ? 'Y/Y' : 'M/M'}:</strong> {formatPct(area.displayValue)}
                            </div>
                            <div className="text-sm">
                              <strong>Index:</strong> {area.latest_value?.toFixed(2) || 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">Click to add to chart</div>
                          </div>
                        </Popup>
                      </CircleMarker>
                    );
                  })}
                </MapContainer>
              </div>

              {/* Map Selection Chart */}
              {mapSelectedSeries.length > 0 && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-sm font-semibold text-gray-700">Selected Areas Comparison</h4>
                    <button
                      onClick={() => setMapSelectedSeries([])}
                      className="px-3 py-1 text-xs text-gray-600 border border-gray-300 rounded hover:bg-white"
                    >
                      Clear All
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {mapSelectedSeries.map((seriesId, idx) => {
                      const seriesInfo = mapSeriesData[seriesId]?.series?.[0];
                      return (
                        <div
                          key={seriesId}
                          className="flex items-center gap-1 px-2 py-1 bg-white rounded border text-xs"
                          style={{ borderLeftColor: CHART_COLORS[idx % CHART_COLORS.length], borderLeftWidth: 3 }}
                        >
                          <span>{seriesInfo?.area_name || seriesId}</span>
                          <button
                            onClick={() => setMapSelectedSeries(mapSelectedSeries.filter(s => s !== seriesId))}
                            className="ml-1 text-gray-400 hover:text-gray-600"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      );
                    })}
                  </div>

                  {Object.keys(mapSeriesData).length > 0 && (
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            dataKey="date"
                            type="category"
                            allowDuplicatedCategory={false}
                            tick={{ fontSize: 10 }}
                          />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '11px' }} />
                          {mapSelectedSeries.map((seriesId, idx) => {
                            const data = mapSeriesData[seriesId]?.series?.[0]?.data_points?.map(d => ({
                              date: `${d.year}-${d.period.slice(1)}`,
                              value: d.value,
                            })) || [];
                            return (
                              <Line
                                key={seriesId}
                                data={data}
                                type="monotone"
                                dataKey="value"
                                stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                                strokeWidth={2}
                                dot={false}
                                name={mapSeriesData[seriesId]?.series?.[0]?.area_name || seriesId}
                              />
                            );
                          })}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 5: Area Comparison Table */}
      <Card>
        <SectionHeader title="Area Comparison" color="cyan" icon={MapPin} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end">
            <Select
              label="Compare Item"
              value={comparisonItem}
              onChange={(v) => { setComparisonItem(v); setMapItem(v); }}
              options={CPI_CATEGORIES}
              className="w-64"
            />
          </div>

          {loadingAreaComparison ? (
            <LoadingSpinner />
          ) : areaComparison?.areas && areaComparison.areas.length > 0 ? (
            <div className="overflow-x-auto max-h-96">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600">Area</th>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600">Type</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">Index</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">MoM %</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">YoY %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {areaComparison.areas.map((area) => (
                    <tr key={area.area_code} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm text-gray-800">{area.area_name}</td>
                      <td className="px-4 py-2 text-xs text-gray-500 capitalize">{area.area_type}</td>
                      <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                        {area.latest_value?.toFixed(1)}
                      </td>
                      <td className="px-4 py-2 text-right">
                        <PctBadge value={area.month_over_month} />
                      </td>
                      <td className="px-4 py-2 text-right">
                        <PctBadge value={area.year_over_year} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center text-gray-500">No area data available</div>
          )}
        </div>
      </Card>

      {/* Section 6: Top Movers */}
      <Card>
        <SectionHeader title="Top CPI-W Movers" color="red" icon={TrendingUp} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end">
            <ButtonGroup
              options={[
                { value: 'mom', label: 'Month-over-Month' },
                { value: 'yoy', label: 'Year-over-Year' },
              ]}
              value={moverPeriod}
              onChange={(v) => setMoverPeriod(v as MoverPeriod)}
            />
          </div>

          {loadingTopMovers ? (
            <LoadingSpinner />
          ) : topMovers ? (
            <div className="grid md:grid-cols-2 gap-6">
              {/* Gainers */}
              <div>
                <h4 className="text-sm font-semibold text-red-600 mb-2 flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" /> Largest Increases
                </h4>
                <div className="space-y-2">
                  {topMovers.gainers.slice(0, 10).map((item, idx) => (
                    <div key={item.series_id} className="flex items-center justify-between p-2 bg-red-50 rounded border border-red-100">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs font-medium text-gray-400 w-4">{idx + 1}</span>
                        <span className="text-sm text-gray-800 truncate" title={item.item_name}>
                          {item.item_name.length > 35 ? item.item_name.substring(0, 35) + '...' : item.item_name}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-red-600 flex-shrink-0">
                        +{item.pct_change?.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                  {topMovers.gainers.length === 0 && (
                    <div className="text-center text-gray-500 py-4">No gainers</div>
                  )}
                </div>
              </div>

              {/* Losers */}
              <div>
                <h4 className="text-sm font-semibold text-green-600 mb-2 flex items-center gap-1">
                  <TrendingDown className="w-4 h-4" /> Largest Decreases
                </h4>
                <div className="space-y-2">
                  {topMovers.losers.slice(0, 10).map((item, idx) => (
                    <div key={item.series_id} className="flex items-center justify-between p-2 bg-green-50 rounded border border-green-100">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs font-medium text-gray-400 w-4">{idx + 1}</span>
                        <span className="text-sm text-gray-800 truncate" title={item.item_name}>
                          {item.item_name.length > 35 ? item.item_name.substring(0, 35) + '...' : item.item_name}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-green-600 flex-shrink-0">
                        {item.pct_change?.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                  {topMovers.losers.length === 0 && (
                    <div className="text-center text-gray-500 py-4">No losers</div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 7: Series Explorer */}
      <Card>
        <SectionHeader title="Series Explorer" color="blue" icon={Search} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-6">
            Access all CW series through search, hierarchical navigation, or paginated browsing.
            Select series to compare in charts (max 5).
          </p>

          {/* 7A: Search */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-cyan-50 to-blue-50 border-b border-gray-200 rounded-t-lg">
              <h4 className="text-sm font-bold text-cyan-800">Search Series</h4>
              <p className="text-xs text-gray-600">Find series by keyword in title</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearchKeyDown}
                  placeholder="Enter keyword (e.g., 'food', 'housing', 'energy')..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                />
                <button
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || loadingSearch}
                  className="px-6 py-2 bg-cyan-600 text-white rounded-md hover:bg-cyan-700 disabled:bg-gray-300 flex items-center gap-2"
                >
                  {loadingSearch && <Loader2 className="w-4 h-4 animate-spin" />}
                  Search
                </button>
                {searchResults && (
                  <button
                    onClick={() => { setSearchResults(null); setSearchQuery(''); }}
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
                  >
                    Clear
                  </button>
                )}
              </div>

              {searchResults && (
                <div className="border border-gray-200 rounded-lg max-h-64 overflow-auto">
                  <div className="px-4 py-2 bg-gray-50 border-b text-sm font-medium">
                    Found {searchResults.total} series
                  </div>
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr className="border-b text-left text-xs font-semibold text-gray-600">
                        <th className="py-2 px-3 w-8"></th>
                        <th className="py-2 px-3">Series ID</th>
                        <th className="py-2 px-3">Area</th>
                        <th className="py-2 px-3">Item</th>
                        <th className="py-2 px-3">SA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {searchResults.series?.map((s) => (
                        <tr
                          key={s.series_id}
                          className={`border-b cursor-pointer ${selectedSeriesIds.includes(s.series_id) ? 'bg-cyan-50' : 'hover:bg-gray-50'}`}
                          onClick={() => toggleSeriesSelection(s.series_id)}
                        >
                          <td className="py-2 px-3">
                            <input
                              type="checkbox"
                              checked={selectedSeriesIds.includes(s.series_id)}
                              disabled={!selectedSeriesIds.includes(s.series_id) && selectedSeriesIds.length >= 5}
                              readOnly
                              className="rounded"
                            />
                          </td>
                          <td className="py-2 px-3 font-mono text-xs">{s.series_id}</td>
                          <td className="py-2 px-3 text-xs">{s.area_name}</td>
                          <td className="py-2 px-3 text-xs">{s.item_name?.substring(0, 30)}</td>
                          <td className="py-2 px-3 text-xs">{s.seasonal_code === 'S' ? 'SA' : 'NSA'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* 7B: Drill-down */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 rounded-t-lg">
              <h4 className="text-sm font-bold text-green-800">Hierarchical Drill-down</h4>
              <p className="text-xs text-gray-600">Navigate: Area → Item → Series</p>
            </div>
            <div className="p-4">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <Select
                  label="Area"
                  value={drillArea}
                  onChange={(v) => { setDrillArea(v); setDrillResults(null); }}
                  options={[
                    { value: '', label: 'All areas...' },
                    ...(dimensions?.areas?.map(a => ({
                      value: a.area_code,
                      label: a.area_name
                    })) || [])
                  ]}
                />
                <Select
                  label="Item Category"
                  value={drillItem}
                  onChange={(v) => { setDrillItem(v); setDrillResults(null); }}
                  options={[
                    { value: '', label: 'All items...' },
                    ...(dimensions?.items?.filter(i => i.display_level === 0).map(i => ({
                      value: i.item_code,
                      label: `${i.item_code} - ${i.item_name.substring(0, 30)}`
                    })) || [])
                  ]}
                />
                <div className="flex items-end">
                  <button
                    onClick={handleDrillDown}
                    disabled={(!drillArea && !drillItem) || loadingDrill}
                    className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 flex items-center justify-center gap-2"
                  >
                    {loadingDrill && <Loader2 className="w-4 h-4 animate-spin" />}
                    Find Series
                  </button>
                </div>
              </div>

              {drillResults && (
                <div className="border border-gray-200 rounded-lg max-h-64 overflow-auto">
                  <div className="px-4 py-2 bg-gray-50 border-b text-sm font-medium">
                    {drillResults.total} series found
                  </div>
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr className="border-b text-left text-xs font-semibold text-gray-600">
                        <th className="py-2 px-3 w-8"></th>
                        <th className="py-2 px-3">Series ID</th>
                        <th className="py-2 px-3">Area</th>
                        <th className="py-2 px-3">Item</th>
                      </tr>
                    </thead>
                    <tbody>
                      {drillResults.series?.map((s) => (
                        <tr
                          key={s.series_id}
                          className={`border-b cursor-pointer ${selectedSeriesIds.includes(s.series_id) ? 'bg-green-50' : 'hover:bg-gray-50'}`}
                          onClick={() => toggleSeriesSelection(s.series_id)}
                        >
                          <td className="py-2 px-3">
                            <input
                              type="checkbox"
                              checked={selectedSeriesIds.includes(s.series_id)}
                              disabled={!selectedSeriesIds.includes(s.series_id) && selectedSeriesIds.length >= 5}
                              readOnly
                              className="rounded"
                            />
                          </td>
                          <td className="py-2 px-3 font-mono text-xs">{s.series_id}</td>
                          <td className="py-2 px-3 text-xs">{s.area_name}</td>
                          <td className="py-2 px-3 text-xs">{s.item_name?.substring(0, 40)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* 7C: Browse */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200 rounded-t-lg">
              <h4 className="text-sm font-bold text-purple-800">Browse All Series</h4>
              <p className="text-xs text-gray-600">Paginated view with filters</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4 flex-wrap">
                <Select
                  label="Area"
                  value={browseArea}
                  onChange={(v) => { setBrowseArea(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'All areas' },
                    ...(dimensions?.areas?.slice(0, 50).map(a => ({
                      value: a.area_code,
                      label: a.area_name
                    })) || [])
                  ]}
                  className="w-48"
                />
                <Select
                  label="Seasonal Adjustment"
                  value={browseSeasonal}
                  onChange={(v) => { setBrowseSeasonal(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'All' },
                    { value: 'S', label: 'Seasonally Adjusted' },
                    { value: 'U', label: 'Not Adjusted' },
                  ]}
                  className="w-48"
                />
                <Select
                  label="Per Page"
                  value={browseLimit.toString()}
                  onChange={(v) => { setBrowseLimit(parseInt(v)); setBrowseOffset(0); }}
                  options={[
                    { value: '25', label: '25' },
                    { value: '50', label: '50' },
                    { value: '100', label: '100' },
                  ]}
                  className="w-24"
                />
              </div>

              {loadingBrowse ? (
                <LoadingSpinner />
              ) : browseResults ? (
                <>
                  <div className="border border-gray-200 rounded-lg max-h-64 overflow-auto">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b text-left text-xs font-semibold text-gray-600">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Area</th>
                          <th className="py-2 px-3">Item</th>
                          <th className="py-2 px-3">SA</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {browseResults.series?.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b cursor-pointer ${selectedSeriesIds.includes(s.series_id) ? 'bg-purple-50' : 'hover:bg-gray-50'}`}
                            onClick={() => toggleSeriesSelection(s.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(s.series_id)}
                                disabled={!selectedSeriesIds.includes(s.series_id) && selectedSeriesIds.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{s.series_id}</td>
                            <td className="py-2 px-3 text-xs">{s.area_name?.substring(0, 25)}</td>
                            <td className="py-2 px-3 text-xs">{s.item_name?.substring(0, 30)}</td>
                            <td className="py-2 px-3 text-xs">{s.seasonal_code === 'S' ? 'SA' : 'NSA'}</td>
                            <td className="py-2 px-3 text-xs">{s.begin_year} - {s.end_year || 'Present'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination */}
                  <div className="flex justify-between items-center mt-3 text-sm">
                    <span className="text-gray-600">
                      Showing {browseOffset + 1}-{Math.min(browseOffset + browseLimit, browseResults.total)} of {browseResults.total}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setBrowseOffset(Math.max(0, browseOffset - browseLimit))}
                        disabled={browseOffset === 0}
                        className="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-50"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setBrowseOffset(browseOffset + browseLimit)}
                        disabled={browseOffset + browseLimit >= browseResults.total}
                        className="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-50"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          </div>

          {/* Selected Series Chart/Table */}
          {selectedSeriesIds.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-3 bg-gradient-to-r from-cyan-100 to-blue-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-cyan-800">
                    {seriesView === 'chart' ? 'Series Comparison Chart' : 'Series Data Table'}
                  </p>
                  <p className="text-xs text-gray-600">{selectedSeriesIds.length}/5 series selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={seriesTimeRange.toString()}
                    onChange={(v) => setSeriesTimeRange(parseInt(v))}
                    options={TIME_RANGE_OPTIONS.map(o => ({ value: o.value.toString(), label: o.label }))}
                    className="w-40"
                  />
                  <ViewToggle value={seriesView} onChange={setSeriesView} />
                  <button
                    onClick={() => { setSelectedSeriesIds([]); setSeriesChartData({}); }}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">

              <div className="flex flex-wrap gap-2 mb-4">
                {selectedSeriesIds.map((seriesId, idx) => (
                  <div
                    key={seriesId}
                    className="flex items-center gap-1 px-2 py-1 bg-gray-50 rounded border text-xs"
                    style={{ borderLeftColor: CHART_COLORS[idx % CHART_COLORS.length], borderLeftWidth: 3 }}
                  >
                    <span>{seriesChartData[seriesId]?.series?.[0]?.series_title?.substring(0, 40) || seriesId}</span>
                    <button
                      onClick={() => toggleSeriesSelection(seriesId)}
                      className="ml-1 text-gray-400 hover:text-gray-600"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>

              {Object.keys(seriesChartData).length > 0 && (
                seriesView === 'chart' ? (
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis
                          dataKey="date"
                          type="category"
                          allowDuplicatedCategory={false}
                          tick={{ fontSize: 10 }}
                          angle={-45}
                          textAnchor="end"
                          height={70}
                        />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {selectedSeriesIds.map((seriesId, idx) => {
                          const rawData = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                          const data = (seriesTimeRange === 0 ? rawData : rawData.slice(-seriesTimeRange)).map(d => ({
                            date: `${d.year}-${d.period.slice(1)}`,
                            value: d.value,
                          }));
                          const name = seriesChartData[seriesId]?.series?.[0]?.item_name?.substring(0, 20) || seriesId;
                          return (
                            <Line
                              key={seriesId}
                              data={data}
                              type="monotone"
                              dataKey="value"
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={false}
                              name={name}
                            />
                          );
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="overflow-x-auto max-h-96">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200">
                          <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Period</th>
                          {selectedSeriesIds.map((seriesId) => (
                            <th key={seriesId} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                              <div>{seriesChartData[seriesId]?.series?.[0]?.item_name?.substring(0, 20) || seriesId}</div>
                              <div className="font-normal text-gray-400">{seriesChartData[seriesId]?.series?.[0]?.area_name?.substring(0, 15) || '-'}</div>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {(() => {
                          const allPeriods = new Map<string, { year: number; period: string; date: string; values: Record<string, number | undefined> }>();
                          selectedSeriesIds.forEach((seriesId) => {
                            const rawData = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                            const data = seriesTimeRange === 0 ? rawData : rawData.slice(-seriesTimeRange);
                            data.forEach((dp) => {
                              const key = `${dp.year}-${dp.period}`;
                              if (!allPeriods.has(key)) {
                                allPeriods.set(key, { year: dp.year, period: dp.period, date: `${dp.year}-${dp.period.slice(1)}`, values: {} });
                              }
                              const periodData = allPeriods.get(key);
                              if (periodData) {
                                periodData.values[seriesId] = dp.value;
                              }
                            });
                          });
                          const sortedPeriods = Array.from(allPeriods.values()).sort((a, b) => {
                            if (b.year !== a.year) return b.year - a.year;
                            return b.period.localeCompare(a.period);
                          });
                          return sortedPeriods.map((period) => (
                            <tr key={`${period.year}-${period.period}`} className="border-b border-gray-100 hover:bg-gray-50">
                              <td className="py-2 px-3 font-medium">{period.date}</td>
                              {selectedSeriesIds.map((seriesId) => (
                                <td key={seriesId} className="py-2 px-3 text-right">
                                  {period.values[seriesId] != null ? period.values[seriesId]?.toFixed(1) : '-'}
                                </td>
                              ))}
                            </tr>
                          ));
                        })()}
                      </tbody>
                    </table>
                  </div>
                )
              )}
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
