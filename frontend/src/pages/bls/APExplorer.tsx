import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, BarChart, Bar
} from 'recharts';
import {
  TrendingUp, TrendingDown, Loader2, DollarSign,
  Fuel, Zap, ShoppingCart, Search, LucideIcon, MapPin, X
} from 'lucide-react';
import { apResearchAPI } from '../../services/api';

// ============================================================================
// TYPES
// ============================================================================

interface APArea {
  area_code: string;
  area_name: string;
  area_type?: string;
}

interface APItem {
  item_code: string;
  item_name: string;
  category?: string;
  unit?: string;
}

interface DimensionsData {
  areas: APArea[];
  items: APItem[];
  categories: string[];
  total_series: number;
  data_range?: string;
}

interface APPriceMetric {
  series_id: string;
  item_code: string;
  item_name: string;
  area_code?: string;
  area_name?: string;
  unit?: string;
  latest_date?: string;
  latest_price?: number;
  prev_month_price?: number;
  prev_year_price?: number;
  mom_change?: number;
  mom_pct?: number;
  yoy_change?: number;
  yoy_pct?: number;
}

interface APCategoryOverview {
  category: string;
  item_count: number;
  series_count: number;
  top_items: APPriceMetric[];
}

interface OverviewData {
  latest_date?: string;
  total_items: number;
  total_series: number;
  categories: APCategoryOverview[];
  featured_prices: APPriceMetric[];
}

interface APTopMover {
  series_id: string;
  item_code: string;
  item_name: string;
  category?: string;
  unit?: string;
  area_name?: string;
  latest_price?: number;
  change?: number;
  pct_change?: number;
  direction: string;
}

interface TopMoversData {
  period: string;
  latest_date?: string;
  gainers: APTopMover[];
  losers: APTopMover[];
}

interface APItemMetric {
  item_code: string;
  item_name: string;
  category?: string;
  unit?: string;
  series_id: string;
  latest_date?: string;
  latest_price?: number;
  mom_change?: number;
  mom_pct?: number;
  yoy_change?: number;
  yoy_pct?: number;
  price_52w_high?: number;
  price_52w_low?: number;
}

interface ItemsAnalysisData {
  category: string;
  latest_date?: string;
  items: APItemMetric[];
}

interface APAreaMetric {
  area_code: string;
  area_name: string;
  area_type?: string;
  item_code: string;
  item_name: string;
  unit?: string;
  latest_price?: number;
  mom_pct?: number;
  yoy_pct?: number;
}

interface AreaComparisonData {
  item_code: string;
  item_name: string;
  unit?: string;
  latest_date?: string;
  areas: APAreaMetric[];
}

interface APTimelinePoint {
  date: string;
  year: number;
  period: string;
  value?: number;
}

interface ItemTimelineData {
  item_code: string;
  item_name: string;
  unit?: string;
  area_name?: string;
  timeline: APTimelinePoint[];
}

interface APSeriesInfo {
  series_id: string;
  series_title: string;
  area_code?: string;
  area_name?: string;
  item_code?: string;
  item_name?: string;
  category?: string;
  unit?: string;
  seasonal_code?: string;
  begin_year?: number;
  end_year?: number;
  is_active?: boolean;
}

interface SeriesListData {
  series: APSeriesInfo[];
  total: number;
  limit: number;
  offset: number;
}

interface APDataPoint {
  year: number;
  period: string;
  period_name?: string;
  value?: number;
  footnote_codes?: string;
}

interface APSeriesData {
  series_id: string;
  series_title: string;
  area_name?: string;
  item_name?: string;
  unit?: string;
  data: APDataPoint[];
}

interface SeriesDataResponse {
  series: { series_id: string; item_name?: string; area_name?: string; data_points: APDataPoint[] }[];
}

type MoverPeriod = 'mom' | 'yoy';
type ViewType = 'chart' | 'table';
type SectionColor = 'blue' | 'green' | 'orange' | 'purple' | 'cyan' | 'red';

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

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

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

function getCategoryIcon(category: string): LucideIcon {
  switch (category) {
    case 'Gasoline': return Fuel;
    case 'Household Fuels': return Zap;
    case 'Food': return ShoppingCart;
    default: return DollarSign;
  }
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function APExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);

  // Overview
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);

  // Top Movers
  const [topMovers, setTopMovers] = useState<TopMoversData | null>(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(true);
  const [moverPeriod, setMoverPeriod] = useState<MoverPeriod>('mom');
  const [moverCategory, setMoverCategory] = useState('');

  // Category Items Analysis
  const [selectedCategory, setSelectedCategory] = useState('Food');
  const [itemsData, setItemsData] = useState<ItemsAnalysisData | null>(null);
  const [loadingItems, setLoadingItems] = useState(false);
  const [itemsView, setItemsView] = useState<ViewType>('table');

  // Area Comparison
  const [selectedItemForArea, setSelectedItemForArea] = useState('');
  const [areaComparison, setAreaComparison] = useState<AreaComparisonData | null>(null);
  const [loadingAreaComparison, setLoadingAreaComparison] = useState(false);

  // Item Timeline
  const [selectedItemForTimeline, setSelectedItemForTimeline] = useState('');
  const [selectedAreaForTimeline, setSelectedAreaForTimeline] = useState('0000');
  const [itemTimeline, setItemTimeline] = useState<ItemTimelineData | null>(null);
  const [loadingTimeline, setLoadingTimeline] = useState(false);
  const [timelineMonths, setTimelineMonths] = useState(60);
  const [timelineSelectedIndex, setTimelineSelectedIndex] = useState<number | null>(null);

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
  const [browseCategory, setBrowseCategory] = useState('');
  const [browseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series Explorer - Selected Series
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
        const res = await apResearchAPI.getDimensions<DimensionsData>();
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
        const res = await apResearchAPI.getOverview<OverviewData>();
        setOverview(res.data);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
  }, []);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await apResearchAPI.getTopMovers<TopMoversData>(moverPeriod, moverCategory || undefined, 10);
        setTopMovers(res.data);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [moverPeriod, moverCategory]);

  // Load category items
  useEffect(() => {
    const load = async () => {
      if (!selectedCategory) return;
      setLoadingItems(true);
      try {
        const res = await apResearchAPI.getItemsAnalysis<ItemsAnalysisData>(selectedCategory, 100);
        setItemsData(res.data);
      } catch (error) {
        console.error('Failed to load items:', error);
      } finally {
        setLoadingItems(false);
      }
    };
    load();
  }, [selectedCategory]);

  // Load area comparison
  useEffect(() => {
    const load = async () => {
      if (!selectedItemForArea) {
        setAreaComparison(null);
        return;
      }
      setLoadingAreaComparison(true);
      try {
        const res = await apResearchAPI.compareAreas<AreaComparisonData>(selectedItemForArea);
        setAreaComparison(res.data);
      } catch (error) {
        console.error('Failed to load area comparison:', error);
      } finally {
        setLoadingAreaComparison(false);
      }
    };
    load();
  }, [selectedItemForArea]);

  // Load item timeline
  useEffect(() => {
    const load = async () => {
      if (!selectedItemForTimeline) {
        setItemTimeline(null);
        return;
      }
      setLoadingTimeline(true);
      try {
        const monthsToFetch = timelineMonths === 0 ? 600 : timelineMonths;
        const res = await apResearchAPI.getItemTimeline<ItemTimelineData>(
          selectedItemForTimeline, selectedAreaForTimeline, monthsToFetch
        );
        setItemTimeline(res.data);
        setTimelineSelectedIndex(null);
      } catch (error) {
        console.error('Failed to load timeline:', error);
      } finally {
        setLoadingTimeline(false);
      }
    };
    load();
  }, [selectedItemForTimeline, selectedAreaForTimeline, timelineMonths]);

  // Load browse series
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseArea) params.area_code = browseArea;
        if (browseCategory) params.category = browseCategory;
        const res = await apResearchAPI.getSeries<SeriesListData>(params);
        setBrowseResults(res.data);
      } catch (error) {
        console.error('Failed to browse series:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    load();
  }, [browseArea, browseCategory, browseLimit, browseOffset]);

  // Load selected series data
  useEffect(() => {
    const loadData = async () => {
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const monthsToFetch = seriesTimeRange === 0 ? 600 : seriesTimeRange;
            const res = await apResearchAPI.getSeriesData<APSeriesData>(seriesId, monthsToFetch);
            setSeriesChartData(prev => ({
              ...prev,
              [seriesId]: {
                series: [{
                  series_id: res.data.series_id,
                  item_name: res.data.item_name,
                  area_name: res.data.area_name,
                  data_points: res.data.data || []
                }]
              }
            }));
          } catch (error) {
            console.error('Failed to load series data:', error);
          }
        }
      }
    };
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSeriesIds, seriesTimeRange]);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await apResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 100 });
      setSearchResults(res.data);
    } catch (error) {
      console.error('Failed to search:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleSearchKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleDrillDown = async () => {
    if (!drillArea && !drillItem) return;
    setLoadingDrill(true);
    try {
      const params: Record<string, unknown> = { limit: 200 };
      if (drillArea) params.area_code = drillArea;
      if (drillItem) params.item_code = drillItem;
      const res = await apResearchAPI.getSeries<SeriesListData>(params);
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
              <DollarSign className="w-6 h-6 text-green-600" />
              Average Price Data (AP)
            </h1>
            <p className="text-gray-600 mt-1">
              Consumer prices for household fuel, motor fuel, and food items
            </p>
          </div>
          <div className="text-right text-sm text-gray-500">
            {overview?.latest_date && <div>Data through: <span className="font-medium">{overview.latest_date}</span></div>}
            {dimensions && (
              <div className="mt-1">
                {dimensions.total_series.toLocaleString()} series | {dimensions.items.length} items
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Section 1: Featured Prices */}
      <Card>
        <SectionHeader title="Featured Prices" color="blue" icon={DollarSign} />
        {loadingOverview ? (
          <LoadingSpinner />
        ) : overview?.featured_prices && overview.featured_prices.length > 0 ? (
          <div className="p-5">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
              {overview.featured_prices.map((item) => {
                const CategoryIcon = getCategoryIcon(item.area_name === 'U.S. city average' ? 'default' : 'Food');
                return (
                  <div
                    key={item.series_id}
                    className="bg-gray-50 rounded-lg p-3 border border-gray-100 hover:border-blue-200 transition-colors"
                  >
                    <div className="flex items-center gap-1 mb-2">
                      <CategoryIcon className="w-3.5 h-3.5 text-gray-400" />
                      <span className="text-xs font-medium text-gray-600 truncate" title={item.item_name}>
                        {item.item_name.length > 25 ? item.item_name.substring(0, 25) + '...' : item.item_name}
                      </span>
                    </div>
                    <div className="text-lg font-bold text-gray-900">
                      ${item.latest_price?.toFixed(2)}
                    </div>
                    {item.unit && (
                      <div className="text-xs text-gray-500 mb-1">{item.unit}</div>
                    )}
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-gray-500">MoM:</span>
                      <PctBadge value={item.mom_pct} />
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-gray-500">YoY:</span>
                      <PctBadge value={item.yoy_pct} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="p-5 text-center text-gray-500">No featured prices available</div>
        )}
      </Card>

      {/* Section 2: Top Movers */}
      <Card>
        <SectionHeader title="Top Price Movers" color="red" icon={TrendingUp} />
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
            <Select
              label="Category"
              value={moverCategory}
              onChange={setMoverCategory}
              options={[
                { value: '', label: 'All Categories' },
                { value: 'Food', label: 'Food' },
                { value: 'Gasoline', label: 'Gasoline' },
                { value: 'Household Fuels', label: 'Household Fuels' },
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
                <h4 className="text-sm font-semibold text-red-600 mb-2 flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" /> Price Increases
                </h4>
                <div className="space-y-2">
                  {topMovers.gainers.slice(0, 8).map((item, idx) => (
                    <div key={item.series_id} className="flex items-center justify-between p-2 bg-red-50 rounded border border-red-100">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs font-medium text-gray-400 w-4">{idx + 1}</span>
                        <span className="text-sm text-gray-800 truncate" title={item.item_name}>
                          {item.item_name.length > 40 ? item.item_name.substring(0, 40) + '...' : item.item_name}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <span className="text-sm text-gray-600">${item.latest_price?.toFixed(2)}</span>
                        <span className="text-sm font-medium text-red-600">+{item.pct_change?.toFixed(1)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Losers */}
              <div>
                <h4 className="text-sm font-semibold text-green-600 mb-2 flex items-center gap-1">
                  <TrendingDown className="w-4 h-4" /> Price Decreases
                </h4>
                <div className="space-y-2">
                  {topMovers.losers.slice(0, 8).map((item, idx) => (
                    <div key={item.series_id} className="flex items-center justify-between p-2 bg-green-50 rounded border border-green-100">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs font-medium text-gray-400 w-4">{idx + 1}</span>
                        <span className="text-sm text-gray-800 truncate" title={item.item_name}>
                          {item.item_name.length > 40 ? item.item_name.substring(0, 40) + '...' : item.item_name}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <span className="text-sm text-gray-600">${item.latest_price?.toFixed(2)}</span>
                        <span className="text-sm font-medium text-green-600">{item.pct_change?.toFixed(1)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 3: Category Analysis */}
      <Card>
        <SectionHeader title="Category Price Analysis" color="orange" icon={ShoppingCart} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end">
            <Select
              label="Category"
              value={selectedCategory}
              onChange={setSelectedCategory}
              options={[
                { value: 'Food', label: 'Food' },
                { value: 'Gasoline', label: 'Gasoline' },
                { value: 'Household Fuels', label: 'Household Fuels' },
              ]}
              className="w-48"
            />
            <ViewToggle value={itemsView} onChange={setItemsView} />
          </div>

          {loadingItems ? (
            <LoadingSpinner />
          ) : itemsData?.items && itemsData.items.length > 0 ? (
            itemsView === 'table' ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600">Item</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">Price</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">MoM %</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">YoY %</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">52W High</th>
                      <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">52W Low</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {itemsData.items.slice(0, 50).map((item) => (
                      <tr key={item.item_code} className="hover:bg-gray-50">
                        <td className="px-4 py-2">
                          <div className="text-sm text-gray-800" title={item.item_name}>
                            {item.item_name.length > 50 ? item.item_name.substring(0, 50) + '...' : item.item_name}
                          </div>
                          {item.unit && <div className="text-xs text-gray-500">{item.unit}</div>}
                        </td>
                        <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                          ${item.latest_price?.toFixed(3)}
                        </td>
                        <td className="px-4 py-2 text-right">
                          <PctBadge value={item.mom_pct} />
                        </td>
                        <td className="px-4 py-2 text-right">
                          <PctBadge value={item.yoy_pct} />
                        </td>
                        <td className="px-4 py-2 text-right text-sm text-gray-600">
                          ${item.price_52w_high?.toFixed(3) || 'N/A'}
                        </td>
                        <td className="px-4 py-2 text-right text-sm text-gray-600">
                          ${item.price_52w_low?.toFixed(3) || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={itemsData.items.slice(0, 20).map(item => ({
                      name: item.item_name.substring(0, 20),
                      yoy: item.yoy_pct || 0,
                      price: item.latest_price || 0,
                    }))}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 150, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis type="number" tickFormatter={(v) => `${v}%`} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={140} />
                    <Tooltip
                      formatter={(value: number) => [`${value.toFixed(2)}%`, 'YoY Change']}
                    />
                    <Bar dataKey="yoy" fill="#3b82f6" name="YoY %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )
          ) : (
            <div className="text-center text-gray-500">Select a category to view items</div>
          )}
        </div>
      </Card>

      {/* Section 4: Area Comparison */}
      <Card>
        <SectionHeader title="Price Comparison by Area" color="purple" icon={MapPin} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end">
            <Select
              label="Select Item"
              value={selectedItemForArea}
              onChange={setSelectedItemForArea}
              options={[
                { value: '', label: 'Choose an item...' },
                ...(dimensions?.items?.slice(0, 100).map(item => ({
                  value: item.item_code,
                  label: `${item.item_name.substring(0, 50)}${item.item_name.length > 50 ? '...' : ''}`
                })) || [])
              ]}
              className="w-96"
            />
          </div>

          {loadingAreaComparison ? (
            <LoadingSpinner />
          ) : areaComparison?.areas && areaComparison.areas.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-gray-600">Area</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">Price</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">MoM %</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-600">YoY %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {areaComparison.areas.map((area) => (
                    <tr key={area.area_code} className="hover:bg-gray-50">
                      <td className="px-4 py-2">
                        <div className="text-sm text-gray-800">{area.area_name}</div>
                        <div className="text-xs text-gray-500">{area.area_type}</div>
                      </td>
                      <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                        ${area.latest_price?.toFixed(3)}
                      </td>
                      <td className="px-4 py-2 text-right">
                        <PctBadge value={area.mom_pct} />
                      </td>
                      <td className="px-4 py-2 text-right">
                        <PctBadge value={area.yoy_pct} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-2 text-xs text-gray-500">
                Data for: {areaComparison.item_name} {areaComparison.unit && `(${areaComparison.unit})`}
              </div>
            </div>
          ) : selectedItemForArea ? (
            <div className="text-center text-gray-500">No area data available for this item</div>
          ) : (
            <div className="text-center text-gray-500">Select an item to compare prices across areas</div>
          )}
        </div>
      </Card>

      {/* Section 5: Price Timeline */}
      <Card>
        <SectionHeader title="Price History Timeline" color="green" icon={TrendingUp} />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end flex-wrap">
            <Select
              label="Select Item"
              value={selectedItemForTimeline}
              onChange={setSelectedItemForTimeline}
              options={[
                { value: '', label: 'Choose an item...' },
                ...(dimensions?.items?.slice(0, 100).map(item => ({
                  value: item.item_code,
                  label: `${item.item_name.substring(0, 50)}${item.item_name.length > 50 ? '...' : ''}`
                })) || [])
              ]}
              className="w-80"
            />
            <Select
              label="Area"
              value={selectedAreaForTimeline}
              onChange={setSelectedAreaForTimeline}
              options={[
                { value: '0000', label: 'U.S. city average' },
                ...(dimensions?.areas?.filter(a => a.area_code !== '0000').slice(0, 50).map(area => ({
                  value: area.area_code,
                  label: area.area_name
                })) || [])
              ]}
              className="w-64"
            />
            <Select
              label="Time Range"
              value={timelineMonths.toString()}
              onChange={(v) => setTimelineMonths(parseInt(v))}
              options={TIME_RANGE_OPTIONS.map(o => ({ value: o.value.toString(), label: o.label }))}
              className="w-40"
            />
          </div>

          {loadingTimeline ? (
            <LoadingSpinner />
          ) : itemTimeline?.timeline && itemTimeline.timeline.length > 0 ? (
            <div>
              <div className="mb-2 text-sm text-gray-600">
                {itemTimeline.item_name} {itemTimeline.unit && `(${itemTimeline.unit})`} - {itemTimeline.area_name}
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={itemTimeline.timeline} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v.toFixed(2)}`} />
                    <Tooltip
                      formatter={(value: number) => [`$${value.toFixed(3)}`, 'Price']}
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#2563eb"
                      strokeWidth={2}
                      dot={false}
                      name="Price"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <TimelineSelector
                timeline={itemTimeline.timeline}
                selectedIndex={timelineSelectedIndex}
                onSelectIndex={setTimelineSelectedIndex}
              />
              {timelineSelectedIndex !== null && itemTimeline.timeline[timelineSelectedIndex] && (
                <div className="mt-2 text-sm bg-blue-50 px-3 py-2 rounded border border-blue-200">
                  <span className="font-medium">{itemTimeline.timeline[timelineSelectedIndex].date}:</span>{' '}
                  ${itemTimeline.timeline[timelineSelectedIndex].value?.toFixed(3)}
                </div>
              )}
            </div>
          ) : selectedItemForTimeline ? (
            <div className="text-center text-gray-500">No timeline data available</div>
          ) : (
            <div className="text-center text-gray-500">Select an item to view price history</div>
          )}
        </div>
      </Card>

      {/* Section 6: Series Explorer */}
      <Card>
        <SectionHeader title="Series Explorer" color="cyan" icon={Search} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-6">
            Access all AP series through search, hierarchical navigation, or paginated browsing.
            Select series to compare in charts (max 5).
          </p>

          <div className="grid lg:grid-cols-3 gap-6 mb-6">
            {/* Search Method */}
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-2 bg-blue-50 border-b border-gray-200 rounded-t-lg">
                <h4 className="text-sm font-bold text-blue-700">1. Search</h4>
                <p className="text-xs text-gray-600">Find series by keyword</p>
              </div>
              <div className="p-4">
                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    placeholder="e.g., eggs, gasoline, bread..."
                    className="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleSearch}
                    disabled={loadingSearch}
                    className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loadingSearch ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                  </button>
                </div>

                {searchResults?.series && searchResults.series.length > 0 && (
                  <div className="border border-gray-200 rounded-lg max-h-48 overflow-auto">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b text-left text-xs font-semibold text-gray-600">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.series.slice(0, 20).map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b cursor-pointer ${selectedSeriesIds.includes(s.series_id) ? 'bg-blue-50' : 'hover:bg-gray-50'}`}
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
                            <td className="py-2 px-3">
                              <div className="font-mono text-xs">{s.series_id}</div>
                              <div className="text-xs text-gray-500">{s.item_name?.substring(0, 30)}</div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Drill-down Method */}
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-2 bg-green-50 border-b border-gray-200 rounded-t-lg">
                <h4 className="text-sm font-bold text-green-700">2. Drill-down</h4>
                <p className="text-xs text-gray-600">Navigate by Area → Item</p>
              </div>
              <div className="p-4">
                <div className="space-y-3 mb-3">
                  <Select
                    label="Area"
                    value={drillArea}
                    onChange={setDrillArea}
                    options={[
                      { value: '', label: 'Select area...' },
                      ...(dimensions?.areas?.slice(0, 50).map(a => ({
                        value: a.area_code,
                        label: a.area_name
                      })) || [])
                    ]}
                  />
                  <Select
                    label="Item"
                    value={drillItem}
                    onChange={setDrillItem}
                    options={[
                      { value: '', label: 'Select item...' },
                      ...(dimensions?.items?.slice(0, 100).map(i => ({
                        value: i.item_code,
                        label: i.item_name.substring(0, 40)
                      })) || [])
                    ]}
                  />
                  <button
                    onClick={handleDrillDown}
                    disabled={loadingDrill || (!drillArea && !drillItem)}
                    className="w-full px-3 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50"
                  >
                    {loadingDrill ? 'Loading...' : 'Find Series'}
                  </button>
                </div>

                {drillResults?.series && drillResults.series.length > 0 && (
                  <div className="border border-gray-200 rounded-lg max-h-48 overflow-auto">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b text-left text-xs font-semibold text-gray-600">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series</th>
                        </tr>
                      </thead>
                      <tbody>
                        {drillResults.series.slice(0, 20).map((s) => (
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
                            <td className="py-2 px-3">
                              <div className="font-mono text-xs">{s.series_id}</div>
                              <div className="text-xs text-gray-500">{s.item_name?.substring(0, 30)}</div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Browse Method */}
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-2 bg-purple-50 border-b border-gray-200 rounded-t-lg">
                <h4 className="text-sm font-bold text-purple-700">3. Browse All</h4>
                <p className="text-xs text-gray-600">Paginated view with filters</p>
              </div>
              <div className="p-4">
                <div className="flex gap-2 mb-3">
                  <Select
                    value={browseArea}
                    onChange={(v) => { setBrowseArea(v); setBrowseOffset(0); }}
                    options={[
                      { value: '', label: 'All areas' },
                      ...(dimensions?.areas?.slice(0, 50).map(a => ({
                        value: a.area_code,
                        label: a.area_name.substring(0, 20)
                      })) || [])
                    ]}
                    className="flex-1"
                  />
                  <Select
                    value={browseCategory}
                    onChange={(v) => { setBrowseCategory(v); setBrowseOffset(0); }}
                    options={[
                      { value: '', label: 'All' },
                      { value: 'Food', label: 'Food' },
                      { value: 'Gasoline', label: 'Gas' },
                      { value: 'Household Fuels', label: 'Fuel' },
                    ]}
                    className="w-20"
                  />
                </div>

                {loadingBrowse ? (
                  <LoadingSpinner />
                ) : browseResults ? (
                  <>
                    <div className="border border-gray-200 rounded-lg max-h-48 overflow-auto">
                      <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-gray-50">
                          <tr className="border-b text-left text-xs font-semibold text-gray-600">
                            <th className="py-2 px-3 w-8"></th>
                            <th className="py-2 px-3">Series</th>
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
                              <td className="py-2 px-3">
                                <div className="font-mono text-xs">{s.series_id}</div>
                                <div className="text-xs text-gray-500">{s.item_name?.substring(0, 30)}</div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination */}
                    <div className="flex justify-between items-center mt-2 text-xs">
                      <span className="text-gray-600">
                        {browseOffset + 1}-{Math.min(browseOffset + browseLimit, browseResults.total)} of {browseResults.total}
                      </span>
                      <div className="flex gap-1">
                        <button
                          onClick={() => setBrowseOffset(Math.max(0, browseOffset - browseLimit))}
                          disabled={browseOffset === 0}
                          className="px-2 py-1 border rounded disabled:opacity-50 hover:bg-gray-50"
                        >
                          Prev
                        </button>
                        <button
                          onClick={() => setBrowseOffset(browseOffset + browseLimit)}
                          disabled={browseOffset + browseLimit >= browseResults.total}
                          className="px-2 py-1 border rounded disabled:opacity-50 hover:bg-gray-50"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  </>
                ) : null}
              </div>
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
                      <span>{seriesChartData[seriesId]?.series?.[0]?.item_name?.substring(0, 30) || seriesId}</span>
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
                          <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v.toFixed(2)}`} />
                          <Tooltip formatter={(value: number) => [`$${value.toFixed(3)}`, 'Price']} />
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
                                    {period.values[seriesId] != null ? `$${period.values[seriesId]?.toFixed(3)}` : '-'}
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
