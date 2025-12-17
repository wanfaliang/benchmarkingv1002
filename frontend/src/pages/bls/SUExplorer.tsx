import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, DollarSign, ShoppingCart, Home, Car, Activity, Search, LucideIcon } from 'lucide-react';
import { suResearchAPI } from '../../services/api';

/**
 * SU Explorer - Chained Consumer Price Index (C-CPI-U) Explorer
 *
 * The C-CPI-U uses a Tornqvist formula to account for consumer substitution.
 * - U.S. city average only
 * - 29 expenditure categories in hierarchical structure
 * - Base period: December 1999 = 100
 * - Monthly data from December 1999 to present
 *
 * Sections:
 * 1. Overview - Key metrics for all categories with timeline
 * 2. Category Analysis - Detailed breakdown with subcategories
 * 3. Top Movers - Categories with largest price changes
 * 4. Inflation Comparison - YoY% comparison across categories
 * 5. Series Explorer - Search, browse, and chart specific series
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

interface CategoryMetric {
  item_code: string;
  item_name: string;
  display_level?: number | null;
  series_id: string;
  latest_value?: number | null;
  latest_date?: string;
  month_over_month?: number | null;
  month_over_month_pct?: number | null;
  year_over_year?: number | null;
  year_over_year_pct?: number | null;
}

interface OverviewData {
  year: number;
  period: string;
  period_name: string;
  all_items?: CategoryMetric | null;
  core_items?: CategoryMetric | null;
  food?: CategoryMetric | null;
  energy?: CategoryMetric | null;
  housing?: CategoryMetric | null;
  transportation?: CategoryMetric | null;
  medical_care?: CategoryMetric | null;
  categories: CategoryMetric[];
}

interface TimelinePoint {
  year: number;
  period: string;
  period_name: string;
  items: Record<string, number | null>;
}

interface OverviewTimelineData {
  timeline: TimelinePoint[];
  item_names: Record<string, string>;
}

interface CategoryAnalysisData {
  item_code: string;
  item_name: string;
  year: number;
  period: string;
  period_name: string;
  main_metric?: CategoryMetric | null;
  subcategories: CategoryMetric[];
}

interface CategoryTimelineData {
  item_code: string;
  item_name: string;
  timeline: TimelinePoint[];
  item_names: Record<string, string>;
}

interface TopMover {
  rank: number;
  item_code: string;
  item_name: string;
  series_id: string;
  latest_value?: number | null;
  change_pct?: number | null;
}

interface TopMoversData {
  year: number;
  period: string;
  period_name: string;
  change_type: string;
  direction: string;
  movers: TopMover[];
}

interface YoYTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  items: Record<string, number | null>;
}

interface YoYComparisonData {
  timeline: YoYTimelinePoint[];
  item_names: Record<string, string>;
}

interface SeriesInfo {
  series_id: string;
  area_code?: string;
  area_name?: string;
  item_code?: string;
  item_name?: string;
  seasonal_code?: string;
  periodicity_code?: string;
  base_code?: string;
  base_period?: string;
  series_title?: string;
  begin_year?: number;
  end_year?: number;
  is_active?: boolean;
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
  data: DataPoint[];
}

interface SeriesDataResponse {
  series: SeriesDataItem[];
}

interface ItemOption {
  item_code: string;
  item_name: string;
  display_level?: number | null;
}

interface DimensionsData {
  areas: { area_code: string; area_name: string }[];
  items: ItemOption[];
}

interface AvailablePeriod {
  year: number;
  period: string;
  period_name: string;
}

type ViewType = 'table' | 'chart';

// ============================================================================
// CONSTANTS
// ============================================================================

const COLORS = ['#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

const timeRangeOptions: TimeRangeOption[] = [
  { value: 2, label: '2 Years' },
  { value: 5, label: '5 Years' },
  { value: 10, label: '10 Years' },
  { value: 15, label: '15 Years' },
  { value: 0, label: 'All Time' },
];

const changeTypeOptions: SelectOption[] = [
  { value: 'year_over_year', label: 'Year-over-Year' },
  { value: 'month_over_month', label: 'Month-over-Month' },
];

const directionOptions: SelectOption[] = [
  { value: 'highest', label: 'Highest' },
  { value: 'lowest', label: 'Lowest' },
];

const KEY_ITEMS = ['SA0', 'SA0L1E', 'SAF', 'SA0E', 'SAH', 'SAT', 'SAM'];

// ============================================================================
// HELPER COMPONENTS
// ============================================================================

interface SectionCardProps {
  title: string;
  icon: LucideIcon;
  color: string;
  children: React.ReactNode;
}

function SectionCard({ title, icon: Icon, color, children }: SectionCardProps): ReactElement {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    orange: 'bg-orange-50 border-orange-200',
    purple: 'bg-purple-50 border-purple-200',
    cyan: 'bg-cyan-50 border-cyan-200',
  };

  const iconColorClasses: Record<string, string> = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    purple: 'text-purple-600',
    cyan: 'text-cyan-600',
  };

  return (
    <div className={`rounded-lg border ${colorClasses[color] || colorClasses.blue} p-4`}>
      <div className="flex items-center gap-2 mb-4">
        <Icon className={`h-5 w-5 ${iconColorClasses[color] || iconColorClasses.blue}`} />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {children}
    </div>
  );
}

interface SelectProps {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  options: SelectOption[];
  className?: string;
}

function Select({ label, value, onChange, options, className = '' }: SelectProps): ReactElement {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <label className="text-sm text-gray-600 whitespace-nowrap">{label}:</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: number | null | undefined;
  change?: number | null;
  format?: 'index' | 'percent';
  icon?: LucideIcon;
}

function MetricCard({ label, value, change, format = 'index', icon: Icon }: MetricCardProps): ReactElement {
  const displayValue = value != null ? (format === 'percent' ? `${value.toFixed(2)}%` : value.toFixed(1)) : 'N/A';
  const changeColor = change != null ? (change >= 0 ? 'text-red-600' : 'text-green-600') : 'text-gray-500';
  const changeIcon = change != null ? (change >= 0 ? TrendingUp : TrendingDown) : null;
  const ChangeIcon = changeIcon;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3 shadow-sm">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-500 truncate flex-1">{label}</span>
        {Icon && <Icon className="h-4 w-4 text-gray-400 ml-1" />}
      </div>
      <div className="text-xl font-bold text-gray-900">{displayValue}</div>
      {change != null && (
        <div className={`flex items-center gap-1 text-xs ${changeColor}`}>
          {ChangeIcon && <ChangeIcon className="h-3 w-3" />}
          <span>{change >= 0 ? '+' : ''}{change.toFixed(2)}%</span>
          <span className="text-gray-400">YoY</span>
        </div>
      )}
    </div>
  );
}

function LoadingSpinner(): ReactElement {
  return (
    <div className="flex items-center justify-center py-8">
      <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function SUExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);

  // Section 1: Overview
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [overviewTimelineData, setOverviewTimelineData] = useState<OverviewTimelineData | null>(null);
  const [overviewTimeRange, setOverviewTimeRange] = useState<number>(5);
  const [overviewLoading, setOverviewLoading] = useState(false);
  const [overviewView, setOverviewView] = useState<ViewType>('chart');
  const [availablePeriods, setAvailablePeriods] = useState<AvailablePeriod[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState<string>('');

  // Section 2: Category Analysis
  const [selectedCategory, setSelectedCategory] = useState<string>('SAF');
  const [categoryData, setCategoryData] = useState<CategoryAnalysisData | null>(null);
  const [categoryTimelineData, setCategoryTimelineData] = useState<CategoryTimelineData | null>(null);
  const [categoryTimeRange, setCategoryTimeRange] = useState<number>(5);
  const [categoryLoading, setCategoryLoading] = useState(false);
  const [categoryView, setCategoryView] = useState<ViewType>('chart');

  // Section 3: Top Movers
  const [topMoversData, setTopMoversData] = useState<TopMoversData | null>(null);
  const [moversChangeType, setMoversChangeType] = useState<string>('year_over_year');
  const [moversDirection, setMoversDirection] = useState<string>('highest');
  const [moversLoading, setMoversLoading] = useState(false);

  // Section 4: YoY Comparison
  const [yoyData, setYoyData] = useState<YoYComparisonData | null>(null);
  const [yoyTimeRange, setYoyTimeRange] = useState<number>(5);
  const [yoyLoading, setYoyLoading] = useState(false);
  const [yoyView, setYoyView] = useState<ViewType>('chart');

  // Section 5: Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);

  // Section 5: Series Explorer - Drill-down
  const [drillItem, setDrillItem] = useState<string>('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [drillLoading, setDrillLoading] = useState(false);

  // Section 5: Series Explorer - Browse
  const [browseItem, setBrowseItem] = useState<string>('');
  const [browseLimit, setBrowseLimit] = useState<number>(25);
  const [browseOffset, setBrowseOffset] = useState<number>(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [browseLoading, setBrowseLoading] = useState(false);

  // Section 5: Series Explorer - Shared
  const [selectedSeries, setSelectedSeries] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<SeriesDataResponse | null>(null);
  const [seriesTimeRange, setSeriesTimeRange] = useState<number>(10);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');
  const [allSeriesInfo, setAllSeriesInfo] = useState<Record<string, SeriesInfo>>({});

  // ============================================================================
  // DATA FETCHING
  // ============================================================================

  // Load dimensions on mount
  useEffect(() => {
    const fetchDimensions = async () => {
      try {
        const response = await suResearchAPI.getDimensions<DimensionsData>();
        setDimensions(response.data);
      } catch (error) {
        console.error('Error fetching dimensions:', error);
      }
    };
    fetchDimensions();
  }, []);

  // Load overview data
  useEffect(() => {
    const fetchOverview = async () => {
      setOverviewLoading(true);
      try {
        const [period, ...rest] = selectedPeriod.split('-');
        const year = rest.length > 0 ? parseInt(rest[0]) : undefined;
        const periodCode = period || undefined;

        const response = await suResearchAPI.getOverview<OverviewData>(year, periodCode);
        setOverviewData(response.data);

        // Build available periods from timeline data
        const startYear = overviewTimeRange === 0 ? 1999 : new Date().getFullYear() - overviewTimeRange;
        const timelineResponse = await suResearchAPI.getOverviewTimeline<OverviewTimelineData>(
          KEY_ITEMS.join(','),
          startYear
        );
        setOverviewTimelineData(timelineResponse.data);

        // Extract available periods for timeline selector
        if (timelineResponse.data.timeline && timelineResponse.data.timeline.length > 0) {
          const periods = timelineResponse.data.timeline.map(t => ({
            year: t.year,
            period: t.period,
            period_name: t.period_name,
          }));
          setAvailablePeriods(periods);
          if (!selectedPeriod && periods.length > 0) {
            const latest = periods[periods.length - 1];
            setSelectedPeriod(`${latest.period}-${latest.year}`);
          }
        }
      } catch (error) {
        console.error('Error fetching overview:', error);
      } finally {
        setOverviewLoading(false);
      }
    };
    fetchOverview();
  }, [overviewTimeRange, selectedPeriod]);

  // Load category data
  useEffect(() => {
    if (!selectedCategory) return;

    const fetchCategory = async () => {
      setCategoryLoading(true);
      try {
        const [response, timelineResponse] = await Promise.all([
          suResearchAPI.getCategoryAnalysis<CategoryAnalysisData>(selectedCategory),
          suResearchAPI.getCategoryTimeline<CategoryTimelineData>(
            selectedCategory,
            categoryTimeRange === 0 ? 1999 : new Date().getFullYear() - categoryTimeRange
          ),
        ]);
        setCategoryData(response.data);
        setCategoryTimelineData(timelineResponse.data);
      } catch (error) {
        console.error('Error fetching category:', error);
      } finally {
        setCategoryLoading(false);
      }
    };
    fetchCategory();
  }, [selectedCategory, categoryTimeRange]);

  // Load top movers data
  useEffect(() => {
    const fetchTopMovers = async () => {
      setMoversLoading(true);
      try {
        const response = await suResearchAPI.getTopMovers<TopMoversData>(
          moversChangeType,
          moversDirection,
          15
        );
        setTopMoversData(response.data);
      } catch (error) {
        console.error('Error fetching top movers:', error);
      } finally {
        setMoversLoading(false);
      }
    };
    fetchTopMovers();
  }, [moversChangeType, moversDirection]);

  // Load YoY comparison data
  useEffect(() => {
    const fetchYoY = async () => {
      setYoyLoading(true);
      try {
        const response = await suResearchAPI.getYoYComparison<YoYComparisonData>(
          KEY_ITEMS.join(','),
          yoyTimeRange === 0 ? 1999 : new Date().getFullYear() - yoyTimeRange
        );
        setYoyData(response.data);
      } catch (error) {
        console.error('Error fetching YoY comparison:', error);
      } finally {
        setYoyLoading(false);
      }
    };
    fetchYoY();
  }, [yoyTimeRange]);

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const response = await suResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 50 });
      setSearchResults(response.data);
      // Store series info
      const infoMap: Record<string, SeriesInfo> = { ...allSeriesInfo };
      response.data.series.forEach(s => { infoMap[s.series_id] = s; });
      setAllSeriesInfo(infoMap);
    } catch (error) {
      console.error('Error searching series:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSearchKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  // Drill-down handler
  useEffect(() => {
    if (!drillItem) {
      setDrillResults(null);
      return;
    }
    const load = async () => {
      setDrillLoading(true);
      try {
        const params: Record<string, unknown> = { limit: 100 };
        if (drillItem) params.item_code = drillItem;
        const response = await suResearchAPI.getSeries<SeriesListData>(params);
        setDrillResults(response.data);
        // Store series info
        const infoMap: Record<string, SeriesInfo> = { ...allSeriesInfo };
        response.data.series.forEach(s => { infoMap[s.series_id] = s; });
        setAllSeriesInfo(infoMap);
      } catch (error) {
        console.error('Error in drill-down:', error);
      } finally {
        setDrillLoading(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [drillItem]);

  // Browse handler
  useEffect(() => {
    const load = async () => {
      setBrowseLoading(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseItem) params.item_code = browseItem;
        const response = await suResearchAPI.getSeries<SeriesListData>(params);
        setBrowseResults(response.data);
        // Store series info
        const infoMap: Record<string, SeriesInfo> = { ...allSeriesInfo };
        response.data.series.forEach(s => { infoMap[s.series_id] = s; });
        setAllSeriesInfo(infoMap);
      } catch (error) {
        console.error('Error in browse:', error);
      } finally {
        setBrowseLoading(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [browseItem, browseLimit, browseOffset]);

  // Load series data when selection changes
  useEffect(() => {
    if (selectedSeries.length === 0) {
      setSeriesChartData(null);
      return;
    }

    const fetchSeriesData = async () => {
      try {
        const startYear = seriesTimeRange === 0 ? undefined : new Date().getFullYear() - seriesTimeRange;
        const response = await suResearchAPI.getData<SeriesDataResponse>(
          selectedSeries.join(','),
          startYear
        );
        setSeriesChartData(response.data);
      } catch (error) {
        console.error('Error fetching series data:', error);
      }
    };
    fetchSeriesData();
  }, [selectedSeries, seriesTimeRange]);

  // Toggle series selection
  const toggleSeriesSelection = (seriesId: string) => {
    setSelectedSeries(prev =>
      prev.includes(seriesId)
        ? prev.filter(id => id !== seriesId)
        : prev.length < 5 ? [...prev, seriesId] : prev
    );
  };

  // Get category options for Section 2
  const categoryOptions: SelectOption[] = dimensions?.items
    ?.filter(i => i.display_level === 0)
    ?.map(i => ({ value: i.item_code, label: i.item_name })) || [];

  // Get item options for Series Explorer filters
  const itemOptions: SelectOption[] = [
    { value: '', label: 'All Items' },
    ...(dimensions?.items?.map(i => ({ value: i.item_code, label: i.item_name })) || [])
  ];

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900">Chained CPI (C-CPI-U) Explorer</h1>
        <p className="text-sm text-gray-600 mt-1">
          The Chained Consumer Price Index uses a Tornqvist formula to account for consumer substitution.
          Base period: December 1999 = 100. Monthly data for U.S. city average.
        </p>
      </div>

      {/* Section 1: Overview */}
      <SectionCard title="C-CPI-U Overview" icon={DollarSign} color="blue">
        <div className="space-y-4">
          {/* Controls */}
          <div className="flex flex-wrap items-center gap-4">
            <Select
              label="Time Range"
              value={overviewTimeRange}
              onChange={(v) => setOverviewTimeRange(Number(v))}
              options={timeRangeOptions}
            />
            {availablePeriods.length > 0 && (
              <Select
                label="Period"
                value={selectedPeriod}
                onChange={setSelectedPeriod}
                options={availablePeriods.slice(-24).map(p => ({
                  value: `${p.period}-${p.year}`,
                  label: p.period_name,
                }))}
                className="w-48"
              />
            )}
            <div className="flex gap-1 ml-auto">
              <button
                onClick={() => setOverviewView('chart')}
                className={`px-3 py-1 text-sm rounded ${overviewView === 'chart' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
              >
                Chart
              </button>
              <button
                onClick={() => setOverviewView('table')}
                className={`px-3 py-1 text-sm rounded ${overviewView === 'table' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
              >
                Table
              </button>
            </div>
          </div>

          {overviewLoading ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Key Metrics Cards */}
              {overviewData && (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                  <MetricCard
                    label="All Items"
                    value={overviewData.all_items?.latest_value}
                    change={overviewData.all_items?.year_over_year_pct}
                    icon={ShoppingCart}
                  />
                  <MetricCard
                    label="Core (ex Food & Energy)"
                    value={overviewData.core_items?.latest_value}
                    change={overviewData.core_items?.year_over_year_pct}
                    icon={Activity}
                  />
                  <MetricCard
                    label="Food & Beverages"
                    value={overviewData.food?.latest_value}
                    change={overviewData.food?.year_over_year_pct}
                    icon={ShoppingCart}
                  />
                  <MetricCard
                    label="Energy"
                    value={overviewData.energy?.latest_value}
                    change={overviewData.energy?.year_over_year_pct}
                    icon={Activity}
                  />
                  <MetricCard
                    label="Housing"
                    value={overviewData.housing?.latest_value}
                    change={overviewData.housing?.year_over_year_pct}
                    icon={Home}
                  />
                  <MetricCard
                    label="Transportation"
                    value={overviewData.transportation?.latest_value}
                    change={overviewData.transportation?.year_over_year_pct}
                    icon={Car}
                  />
                  <MetricCard
                    label="Medical Care"
                    value={overviewData.medical_care?.latest_value}
                    change={overviewData.medical_care?.year_over_year_pct}
                    icon={Activity}
                  />
                </div>
              )}

              {/* Timeline Chart / Table */}
              {overviewTimelineData && overviewTimelineData.timeline.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Historical Trend - {overviewData?.period_name}
                  </h4>
                  {overviewView === 'chart' ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={overviewTimelineData.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="period_name"
                          tick={{ fontSize: 10 }}
                          interval="preserveStartEnd"
                        />
                        <YAxis tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
                        <Tooltip />
                        <Legend />
                        {Object.keys(overviewTimelineData.item_names).map((key, idx) => (
                          <Line
                            key={key}
                            type="monotone"
                            dataKey={`items.${key}`}
                            name={overviewTimelineData.item_names[key]}
                            stroke={COLORS[idx % COLORS.length]}
                            dot={false}
                            strokeWidth={key === 'SA0' ? 2 : 1}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="overflow-x-auto max-h-64">
                      <table className="min-w-full text-sm">
                        <thead className="bg-gray-50 sticky top-0">
                          <tr>
                            <th className="px-3 py-2 text-left text-gray-600">Period</th>
                            {Object.entries(overviewTimelineData.item_names).map(([code, name]) => (
                              <th key={code} className="px-3 py-2 text-right text-gray-600">{name}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {overviewTimelineData.timeline.slice().reverse().map((row, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              <td className="px-3 py-2 text-gray-900">{row.period_name}</td>
                              {Object.keys(overviewTimelineData.item_names).map(code => (
                                <td key={code} className="px-3 py-2 text-right text-gray-700">
                                  {row.items[code]?.toFixed(1) ?? 'N/A'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </SectionCard>

      {/* Section 2: Category Analysis */}
      <SectionCard title="Category Analysis" icon={ShoppingCart} color="green">
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <Select
              label="Category"
              value={selectedCategory}
              onChange={setSelectedCategory}
              options={categoryOptions}
              className="w-64"
            />
            <Select
              label="Time Range"
              value={categoryTimeRange}
              onChange={(v) => setCategoryTimeRange(Number(v))}
              options={timeRangeOptions}
            />
            <div className="flex gap-1 ml-auto">
              <button
                onClick={() => setCategoryView('chart')}
                className={`px-3 py-1 text-sm rounded ${categoryView === 'chart' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700'}`}
              >
                Chart
              </button>
              <button
                onClick={() => setCategoryView('table')}
                className={`px-3 py-1 text-sm rounded ${categoryView === 'table' ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700'}`}
              >
                Table
              </button>
            </div>
          </div>

          {categoryLoading ? (
            <LoadingSpinner />
          ) : categoryData && (
            <>
              {/* Main Category Metric */}
              {categoryData.main_metric && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <MetricCard
                    label={categoryData.item_name}
                    value={categoryData.main_metric.latest_value}
                    change={categoryData.main_metric.year_over_year_pct}
                  />
                  <div className="bg-white rounded-lg border border-gray-200 p-3">
                    <div className="text-xs text-gray-500">MoM Change</div>
                    <div className={`text-lg font-bold ${(categoryData.main_metric.month_over_month_pct ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {categoryData.main_metric.month_over_month_pct != null
                        ? `${categoryData.main_metric.month_over_month_pct >= 0 ? '+' : ''}${categoryData.main_metric.month_over_month_pct.toFixed(2)}%`
                        : 'N/A'}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg border border-gray-200 p-3">
                    <div className="text-xs text-gray-500">YoY Change</div>
                    <div className={`text-lg font-bold ${(categoryData.main_metric.year_over_year_pct ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {categoryData.main_metric.year_over_year_pct != null
                        ? `${categoryData.main_metric.year_over_year_pct >= 0 ? '+' : ''}${categoryData.main_metric.year_over_year_pct.toFixed(2)}%`
                        : 'N/A'}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg border border-gray-200 p-3">
                    <div className="text-xs text-gray-500">Period</div>
                    <div className="text-lg font-bold text-gray-900">{categoryData.period_name}</div>
                  </div>
                </div>
              )}

              {/* Subcategories Bar Chart */}
              {categoryData.subcategories.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Subcategories - YoY% Change</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={categoryData.subcategories} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" tick={{ fontSize: 10 }} />
                      <YAxis dataKey="item_name" type="category" width={150} tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Bar dataKey="year_over_year_pct" name="YoY %">
                        {categoryData.subcategories.map((entry, idx) => (
                          <rect
                            key={idx}
                            fill={(entry.year_over_year_pct ?? 0) >= 0 ? '#ef4444' : '#22c55e'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Timeline */}
              {categoryTimelineData && categoryTimelineData.timeline.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Historical Trend</h4>
                  {categoryView === 'chart' ? (
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={categoryTimelineData.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                        <YAxis tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
                        <Tooltip />
                        <Legend />
                        {Object.keys(categoryTimelineData.item_names).map((key, idx) => (
                          <Line
                            key={key}
                            type="monotone"
                            dataKey={`items.${key}`}
                            name={categoryTimelineData.item_names[key]}
                            stroke={COLORS[idx % COLORS.length]}
                            dot={false}
                            strokeWidth={key === selectedCategory ? 2 : 1}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="overflow-x-auto max-h-64">
                      <table className="min-w-full text-sm">
                        <thead className="bg-gray-50 sticky top-0">
                          <tr>
                            <th className="px-3 py-2 text-left text-gray-600">Period</th>
                            {Object.entries(categoryTimelineData.item_names).map(([code, name]) => (
                              <th key={code} className="px-3 py-2 text-right text-gray-600">{name}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {categoryTimelineData.timeline.slice().reverse().map((row, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              <td className="px-3 py-2 text-gray-900">{row.period_name}</td>
                              {Object.keys(categoryTimelineData.item_names).map(code => (
                                <td key={code} className="px-3 py-2 text-right text-gray-700">
                                  {row.items[code]?.toFixed(1) ?? 'N/A'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </SectionCard>

      {/* Section 3: Top Movers */}
      <SectionCard title="Top Movers" icon={TrendingUp} color="orange">
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <Select
              label="Change Type"
              value={moversChangeType}
              onChange={setMoversChangeType}
              options={changeTypeOptions}
            />
            <Select
              label="Direction"
              value={moversDirection}
              onChange={setMoversDirection}
              options={directionOptions}
            />
          </div>

          {moversLoading ? (
            <LoadingSpinner />
          ) : topMoversData && (
            <div className="grid md:grid-cols-2 gap-4">
              {/* Bar Chart */}
              <div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topMoversData.movers} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tick={{ fontSize: 10 }} />
                    <YAxis
                      dataKey="item_name"
                      type="category"
                      width={120}
                      tick={{ fontSize: 10 }}
                    />
                    <Tooltip
                      formatter={(value: number) => [`${value.toFixed(2)}%`, 'Change']}
                    />
                    <Bar dataKey="change_pct" name="Change %">
                      {topMoversData.movers.map((entry, idx) => (
                        <rect
                          key={idx}
                          fill={(entry.change_pct ?? 0) >= 0 ? '#ef4444' : '#22c55e'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-gray-600">#</th>
                      <th className="px-3 py-2 text-left text-gray-600">Category</th>
                      <th className="px-3 py-2 text-right text-gray-600">Index</th>
                      <th className="px-3 py-2 text-right text-gray-600">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topMoversData.movers.map((m, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-3 py-2 text-gray-500">{m.rank}</td>
                        <td className="px-3 py-2 text-gray-900">{m.item_name}</td>
                        <td className="px-3 py-2 text-right text-gray-700">
                          {m.latest_value?.toFixed(1) ?? 'N/A'}
                        </td>
                        <td className={`px-3 py-2 text-right font-medium ${(m.change_pct ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {m.change_pct != null ? `${m.change_pct >= 0 ? '+' : ''}${m.change_pct.toFixed(2)}%` : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {topMoversData && (
            <p className="text-xs text-gray-500">
              Data as of: {topMoversData.period_name}
            </p>
          )}
        </div>
      </SectionCard>

      {/* Section 4: YoY Inflation Comparison */}
      <SectionCard title="Inflation Comparison (YoY %)" icon={Activity} color="purple">
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <Select
              label="Time Range"
              value={yoyTimeRange}
              onChange={(v) => setYoyTimeRange(Number(v))}
              options={timeRangeOptions}
            />
            <div className="flex gap-1 ml-auto">
              <button
                onClick={() => setYoyView('chart')}
                className={`px-3 py-1 text-sm rounded ${yoyView === 'chart' ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700'}`}
              >
                Chart
              </button>
              <button
                onClick={() => setYoyView('table')}
                className={`px-3 py-1 text-sm rounded ${yoyView === 'table' ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-700'}`}
              >
                Table
              </button>
            </div>
          </div>

          {yoyLoading ? (
            <LoadingSpinner />
          ) : yoyData && yoyData.timeline.length > 0 && (
            yoyView === 'chart' ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={yoyData.timeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period_name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `${v}%`} />
                  <Tooltip formatter={(value: number) => [`${value?.toFixed(2)}%`, '']} />
                  <Legend />
                  {Object.keys(yoyData.item_names).map((key, idx) => (
                    <Line
                      key={key}
                      type="monotone"
                      dataKey={`items.${key}`}
                      name={yoyData.item_names[key]}
                      stroke={COLORS[idx % COLORS.length]}
                      dot={false}
                      strokeWidth={key === 'SA0' ? 2 : 1}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="overflow-x-auto max-h-64">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left text-gray-600">Period</th>
                      {Object.entries(yoyData.item_names).map(([code, name]) => (
                        <th key={code} className="px-3 py-2 text-right text-gray-600">{name}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {yoyData.timeline.slice().reverse().map((row, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-3 py-2 text-gray-900">{row.period_name}</td>
                        {Object.keys(yoyData.item_names).map(code => (
                          <td key={code} className={`px-3 py-2 text-right ${(row.items[code] ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {row.items[code] != null ? `${row.items[code]! >= 0 ? '+' : ''}${row.items[code]!.toFixed(2)}%` : 'N/A'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}
        </div>
      </SectionCard>

      {/* Section 5: Series Explorer */}
      <SectionCard title="Series Explorer" icon={Search} color="cyan">
        <div>
          <p className="text-xs text-gray-500 mb-6">
            Access all C-CPI-U series through search, hierarchical navigation, or paginated browsing.
            Select series to compare in charts (max 5).
          </p>

          {/* Sub-section 5A: Search by Keyword */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-cyan-50 to-blue-50 border-b border-gray-200 rounded-t-lg">
              <h4 className="text-sm font-bold text-cyan-800">Search Series</h4>
              <p className="text-xs text-gray-600">Find series by keyword in item name</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Enter keyword (e.g., 'food', 'energy', 'medical')..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || searchLoading}
                  className="px-6 py-2 bg-cyan-600 text-white rounded-md hover:bg-cyan-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {searchLoading && <Loader2 className="w-4 h-4 animate-spin" />}
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

              {/* Search Results */}
              {searchResults && (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-700">
                      Found {searchResults.total} series matching "{searchQuery}"
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-64">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Item</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.series.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeries.includes(s.series_id) ? 'bg-cyan-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(s.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeries.includes(s.series_id)}
                                disabled={!selectedSeries.includes(s.series_id) && selectedSeries.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{s.series_id}</td>
                            <td className="py-2 px-3 text-xs">{s.item_name}</td>
                            <td className="py-2 px-3 text-xs">{s.begin_year} - {s.end_year || 'Present'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sub-section 5B: Hierarchical Drill-down */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 rounded-t-lg">
              <h4 className="text-sm font-bold text-green-800">Hierarchical Drill-down</h4>
              <p className="text-xs text-gray-600">Select an item category to find related series</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <Select
                  label="Item Category"
                  value={drillItem}
                  onChange={setDrillItem}
                  options={itemOptions}
                  className="w-80"
                />
              </div>

              {/* Drill-down Results */}
              {drillLoading ? (
                <LoadingSpinner />
              ) : drillResults && drillResults.series.length > 0 ? (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-700">
                      {drillResults.total} series in selected category
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-64">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Item</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {drillResults.series.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeries.includes(s.series_id) ? 'bg-green-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(s.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeries.includes(s.series_id)}
                                disabled={!selectedSeries.includes(s.series_id) && selectedSeries.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{s.series_id}</td>
                            <td className="py-2 px-3 text-xs">{s.item_name}</td>
                            <td className="py-2 px-3 text-xs">{s.begin_year} - {s.end_year || 'Present'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : drillResults ? (
                <div className="text-gray-500 text-center py-4 border border-gray-200 rounded-lg">No series found for this item</div>
              ) : (
                <div className="text-sm text-gray-500 py-4">Select an item category above to view series</div>
              )}
            </div>
          </div>

          {/* Sub-section 5C: Browse All Series */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200 rounded-t-lg">
              <h4 className="text-sm font-bold text-purple-800">Browse All Series</h4>
              <p className="text-xs text-gray-600">Paginated view of all available series with filters</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4 flex-wrap">
                <Select
                  label="Item Filter"
                  value={browseItem}
                  onChange={(v) => { setBrowseItem(v); setBrowseOffset(0); }}
                  options={itemOptions}
                  className="w-80"
                />
                <Select
                  label="Per Page"
                  value={browseLimit}
                  onChange={(v) => { setBrowseLimit(Number(v)); setBrowseOffset(0); }}
                  options={[
                    { value: 10, label: '10' },
                    { value: 25, label: '25' },
                    { value: 50, label: '50' },
                  ]}
                  className="w-24"
                />
              </div>

              {/* Browse Results with Pagination */}
              <div className="border border-gray-200 rounded-lg">
                <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">
                    {browseResults ? `${browseResults.total} total series` : 'Loading...'}
                  </span>
                  {selectedSeries.length > 0 && (
                    <button
                      onClick={() => setSelectedSeries([])}
                      className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100"
                    >
                      Clear Selection ({selectedSeries.length})
                    </button>
                  )}
                </div>
                <div className="overflow-x-auto max-h-80">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                        <th className="py-2 px-3 w-8"></th>
                        <th className="py-2 px-3">Series ID</th>
                        <th className="py-2 px-3">Item</th>
                        <th className="py-2 px-3">Base Period</th>
                        <th className="py-2 px-3">Data Range</th>
                      </tr>
                    </thead>
                    <tbody>
                      {browseLoading ? (
                        <tr><td colSpan={5} className="py-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-gray-400" /></td></tr>
                      ) : browseResults?.series?.length === 0 ? (
                        <tr><td colSpan={5} className="py-8 text-center text-gray-500">No series found.</td></tr>
                      ) : (
                        browseResults?.series?.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeries.includes(s.series_id) ? 'bg-purple-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(s.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeries.includes(s.series_id)}
                                disabled={!selectedSeries.includes(s.series_id) && selectedSeries.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{s.series_id}</td>
                            <td className="py-2 px-3 text-xs">{s.item_name}</td>
                            <td className="py-2 px-3 text-xs text-gray-500">{s.base_period || '-'}</td>
                            <td className="py-2 px-3 text-xs">{s.begin_year} - {s.end_year || 'Present'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                {browseResults && browseResults.total > 0 && (
                  <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
                    <span className="text-sm text-gray-600">
                      Showing {browseOffset + 1} - {Math.min(browseOffset + browseLimit, browseResults.total)} of {browseResults.total}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setBrowseOffset(0)}
                        disabled={browseOffset === 0}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        First
                      </button>
                      <button
                        onClick={() => setBrowseOffset(Math.max(0, browseOffset - browseLimit))}
                        disabled={browseOffset === 0}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <span className="px-3 py-1 text-sm text-gray-600">
                        Page {Math.floor(browseOffset / browseLimit) + 1} of {Math.ceil(browseResults.total / browseLimit)}
                      </span>
                      <button
                        onClick={() => setBrowseOffset(browseOffset + browseLimit)}
                        disabled={browseOffset + browseLimit >= browseResults.total}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                      <button
                        onClick={() => setBrowseOffset(Math.floor((browseResults.total - 1) / browseLimit) * browseLimit)}
                        disabled={browseOffset + browseLimit >= browseResults.total}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Last
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Selected Series Chart/Table */}
          {selectedSeries.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-3 bg-gradient-to-r from-cyan-100 to-blue-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-cyan-800">
                    {seriesView === 'chart' ? 'Series Comparison Chart' : 'Series Data Table'}
                  </p>
                  <p className="text-xs text-gray-600">{selectedSeries.length} series selected - click series above to add/remove</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    label="Time Range"
                    value={seriesTimeRange}
                    onChange={(v) => setSeriesTimeRange(Number(v))}
                    options={timeRangeOptions}
                  />
                  <div className="flex gap-1">
                    <button
                      onClick={() => setSeriesView('chart')}
                      className={`px-3 py-1 text-sm rounded ${seriesView === 'chart' ? 'bg-cyan-600 text-white' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}
                    >
                      Chart
                    </button>
                    <button
                      onClick={() => setSeriesView('table')}
                      className={`px-3 py-1 text-sm rounded ${seriesView === 'table' ? 'bg-cyan-600 text-white' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'}`}
                    >
                      Table
                    </button>
                  </div>
                </div>
              </div>

              {seriesChartData && seriesChartData.series.length > 0 ? (
                seriesView === 'chart' ? (
                  <div className="p-4 h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis
                          dataKey="period_name"
                          tick={{ fontSize: 10 }}
                          interval="preserveStartEnd"
                          allowDuplicatedCategory={false}
                          angle={-45}
                          textAnchor="end"
                          height={60}
                        />
                        <YAxis tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {seriesChartData.series.map((s, idx) => (
                          <Line
                            key={s.series_id}
                            data={s.data}
                            type="monotone"
                            dataKey="value"
                            name={s.series_info.item_name || s.series_id}
                            stroke={COLORS[idx % COLORS.length]}
                            strokeWidth={2}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="overflow-x-auto max-h-96">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200">
                          <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Period</th>
                          {seriesChartData.series.map(s => (
                            <th key={s.series_id} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                              {s.series_info.item_name || s.series_id}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {(() => {
                          const allPeriods = new Set<string>();
                          seriesChartData.series.forEach(s => {
                            s.data.forEach(d => allPeriods.add(`${d.year}-${d.period}`));
                          });
                          const sortedPeriods = Array.from(allPeriods).sort().reverse();
                          return sortedPeriods.slice(0, 50).map((periodKey, idx) => {
                            const [year, period] = periodKey.split('-');
                            return (
                              <tr key={periodKey} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                <td className="py-2 px-3 text-gray-900">
                                  {seriesChartData.series[0].data.find(d => d.year === parseInt(year) && d.period === period)?.period_name || periodKey}
                                </td>
                                {seriesChartData.series.map(s => {
                                  const dp = s.data.find(d => d.year === parseInt(year) && d.period === period);
                                  return (
                                    <td key={s.series_id} className="py-2 px-3 text-right text-gray-700">
                                      {dp?.value?.toFixed(3) ?? 'N/A'}
                                    </td>
                                  );
                                })}
                              </tr>
                            );
                          });
                        })()}
                      </tbody>
                    </table>
                  </div>
                )
              ) : (
                <div className="p-8">
                  <LoadingSpinner />
                </div>
              )}
            </div>
          )}
        </div>
      </SectionCard>
    </div>
  );
}
