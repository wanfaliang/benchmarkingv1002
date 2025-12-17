import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, Loader2, Package, ArrowUpCircle, ArrowDownCircle, LucideIcon, Layers } from 'lucide-react';
import { wpResearchAPI } from '../../services/api';

/**
 * WP Explorer - Producer Price Index (Commodities / Final Demand) Explorer
 *
 * WP survey contains:
 * - FINAL DEMAND PPI: The headline numbers reported in BLS press releases
 * - INTERMEDIATE DEMAND: Price indexes by production stage
 * - Traditional commodity groups (01-15)
 *
 * Sections:
 * 1. Final Demand Overview - HEADLINE PPI with MoM% and YoY% (THE main numbers)
 * 2. Intermediate Demand - Prices by production stage (Stage 1-4)
 * 3. Commodity Groups - Traditional commodity groupings
 * 4. Item Analysis - Items within a selected group
 * 5. Top Movers - Biggest price gainers and losers
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
  categories?: Record<string, number | null>;
  groups?: Record<string, number | null>;
  [key: string]: unknown;
}

interface HeadlinePPI {
  series_id: string;
  name: string;
  latest_date?: string;
  mom_pct?: number | null;
  yoy_pct?: number | null;
  index_value?: number | null;
}

interface OverviewData {
  headline: HeadlinePPI;
  components: HeadlinePPI[];
  last_updated?: string;
}

interface OverviewTimelineData {
  timeline: TimelinePoint[];
  category_names?: Record<string, string>;
}

interface IntermediateStage {
  stage: string;
  stage_name: string;
  series_id: string;
  latest_date?: string;
  mom_pct?: number | null;
  yoy_pct?: number | null;
  index_value?: number | null;
}

interface IntermediateDemandData {
  stages: IntermediateStage[];
  last_updated?: string;
}

interface GroupMetric {
  group_code: string;
  group_name: string;
  series_id: string;
  latest_value?: number | null;
  latest_date?: string;
  mom_pct?: number | null;
  yoy_pct?: number | null;
}

interface GroupsData {
  groups: GroupMetric[];
  last_updated?: string;
}

interface GroupTimelineData {
  timeline: TimelinePoint[];
  group_names?: Record<string, string>;
}

interface ItemMetric {
  group_code: string;
  group_name: string;
  item_code: string;
  item_name: string;
  series_id: string;
  latest_value?: number | null;
  latest_date?: string;
  mom_pct?: number | null;
  yoy_pct?: number | null;
}

interface ItemsData {
  items: ItemMetric[];
  group_code: string;
  group_name: string;
  total_count: number;
  last_updated?: string;
}

interface Mover {
  group_code: string;
  group_name: string;
  item_code?: string;
  item_name?: string;
  latest_value?: number;
  change_pct?: number;
}

interface TopMoversData {
  gainers: Mover[];
  losers: Mover[];
  last_updated?: string;
}

interface GroupInfo {
  group_code: string;
  group_name: string;
  is_final_demand?: boolean;
}

interface DimensionsData {
  groups?: GroupInfo[];
  final_demand_groups?: GroupInfo[];
  commodity_groups?: GroupInfo[];
  base_years?: number[];
  start_years?: number[];
}

interface SeriesInfo {
  series_id: string;
  group_code: string;
  group_name?: string;
  item_code?: string;
  item_name?: string;
  seasonal_code?: string;
  begin_year?: number;
  end_year?: number | null;
  base_date?: string;
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

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatIndex = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return value.toFixed(1);
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

const LoadingSpinner = (): ReactElement => (
  <div className="flex justify-center items-center p-8">
    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
  </div>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function WPExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);

  // Final Demand Overview (HEADLINE)
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [overviewTimeRange, setOverviewTimeRange] = useState(24);

  // Intermediate Demand
  const [intermediateDemand, setIntermediateDemand] = useState<IntermediateDemandData | null>(null);
  const [loadingIntermediate, setLoadingIntermediate] = useState(true);

  // Groups Analysis
  const [groupsData, setGroupsData] = useState<GroupsData | null>(null);
  const [loadingGroups, setLoadingGroups] = useState(true);
  const [selectedGroups, setSelectedGroups] = useState<string[]>([]);
  const [groupTimeline, setGroupTimeline] = useState<GroupTimelineData | null>(null);
  const [groupTimeRange, setGroupTimeRange] = useState(24);
  const [groupView, setGroupView] = useState<ViewType>('chart');
  const [groupFilter, setGroupFilter] = useState<'all' | 'commodity' | 'fd'>('commodity');

  // Items Analysis
  const [selectedGroupForItems, setSelectedGroupForItems] = useState('');
  const [itemsData, setItemsData] = useState<ItemsData | null>(null);
  const [loadingItems, setLoadingItems] = useState(false);
  const [itemTimeRange, setItemTimeRange] = useState(24);
  const [itemView, setItemView] = useState<ViewType>('chart');

  // Top Movers
  const [topMovers, setTopMovers] = useState<TopMoversData | null>(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(true);
  const [moverPeriod, setMoverPeriod] = useState<MoverPeriod>('mom');

  // Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Series Explorer - Drill-down
  const [drillGroup, setDrillGroup] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);

  // Series Explorer - Browse
  const [browseGroup, setBrowseGroup] = useState('');
  const [browseSeasonal, setBrowseSeasonal] = useState('');
  const [browseBaseYear, setBrowseBaseYear] = useState('');
  const [browseLimit, setBrowseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series Explorer - Shared
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesTimeRange, setSeriesTimeRange] = useState(24);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');
  const [seriesChartData, setSeriesChartData] = useState<SeriesChartDataMap>({});
  const [allSeriesInfo, setAllSeriesInfo] = useState<Record<string, SeriesInfo>>({});

  // ============================================================================
  // DATA LOADING
  // ============================================================================

  // Load dimensions
  useEffect(() => {
    const load = async () => {
      try {
        const res = await wpResearchAPI.getDimensions<DimensionsData>();
        setDimensions(res.data);
      } catch (error) {
        console.error('Failed to load dimensions:', error);
      }
    };
    load();
  }, []);

  // Load Final Demand overview
  useEffect(() => {
    const load = async () => {
      setLoadingOverview(true);
      try {
        const res = await wpResearchAPI.getOverview<OverviewData>();
        setOverview(res.data);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
  }, []);

  // Load overview timeline
  useEffect(() => {
    const load = async () => {
      try {
        const res = await wpResearchAPI.getOverviewTimeline<OverviewTimelineData>(overviewTimeRange);
        setOverviewTimeline(res.data);
      } catch (error) {
        console.error('Failed to load overview timeline:', error);
      }
    };
    load();
  }, [overviewTimeRange]);

  // Load Intermediate Demand
  useEffect(() => {
    const load = async () => {
      setLoadingIntermediate(true);
      try {
        const res = await wpResearchAPI.getIntermediateDemand<IntermediateDemandData>();
        setIntermediateDemand(res.data);
      } catch (error) {
        console.error('Failed to load intermediate demand:', error);
      } finally {
        setLoadingIntermediate(false);
      }
    };
    load();
  }, []);

  // Load Groups analysis
  useEffect(() => {
    const load = async () => {
      setLoadingGroups(true);
      try {
        const params: Record<string, unknown> = { limit: 25 };
        if (groupFilter === 'commodity') params.commodity_only = true;
        if (groupFilter === 'fd') params.final_demand_only = true;
        const res = await wpResearchAPI.getGroupsAnalysis<GroupsData>(params);
        setGroupsData(res.data);
        // Pre-select first 3 groups
        if (res.data?.groups?.length > 0) {
          setSelectedGroups(res.data.groups.slice(0, 3).map(g => g.group_code));
        }
      } catch (error) {
        console.error('Failed to load groups:', error);
      } finally {
        setLoadingGroups(false);
      }
    };
    load();
  }, [groupFilter]);

  // Load group timeline
  useEffect(() => {
    const load = async () => {
      if (selectedGroups.length === 0) {
        setGroupTimeline(null);
        return;
      }
      try {
        const res = await wpResearchAPI.getGroupsTimeline<GroupTimelineData>(selectedGroups, groupTimeRange);
        setGroupTimeline(res.data);
      } catch (error) {
        console.error('Failed to load group timeline:', error);
      }
    };
    load();
  }, [selectedGroups, groupTimeRange]);

  // Load items for selected group
  useEffect(() => {
    const load = async () => {
      if (!selectedGroupForItems) {
        setItemsData(null);
        return;
      }
      setLoadingItems(true);
      try {
        const res = await wpResearchAPI.getItemsAnalysis<ItemsData>(selectedGroupForItems, 30);
        setItemsData(res.data);
      } catch (error) {
        console.error('Failed to load items:', error);
      } finally {
        setLoadingItems(false);
      }
    };
    load();
  }, [selectedGroupForItems]);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await wpResearchAPI.getTopMovers<TopMoversData>(moverPeriod, 10, true);
        setTopMovers(res.data);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [moverPeriod]);

  // Load browse results
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = {
          active_only: true,
          limit: browseLimit,
          offset: browseOffset,
          commodity_only: true  // Default to commodity series
        };
        if (browseGroup) params.group_code = browseGroup;
        if (browseSeasonal) params.seasonal_code = browseSeasonal;
        if (browseBaseYear) params.base_year = parseInt(browseBaseYear);
        const res = await wpResearchAPI.getSeries<SeriesListData>(params);
        setBrowseResults(res.data);
        // Cache series info
        const newInfo: Record<string, SeriesInfo> = {};
        res.data?.series?.forEach((s: SeriesInfo) => {
          newInfo[s.series_id] = s;
        });
        setAllSeriesInfo(prev => ({ ...prev, ...newInfo }));
      } catch (error) {
        console.error('Failed to load browse results:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    load();
  }, [browseGroup, browseSeasonal, browseBaseYear, browseLimit, browseOffset]);

  // Load data for selected series
  useEffect(() => {
    const load = async () => {
      const newData: SeriesChartDataMap = {};
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const res = await wpResearchAPI.getSeriesData<SeriesDataResponse>(seriesId);
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
  // HANDLERS
  // ============================================================================

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await wpResearchAPI.getSeries<SeriesListData>({ search: searchQuery.trim(), limit: 100 });
      setSearchResults(res.data);
      const newInfo: Record<string, SeriesInfo> = {};
      res.data?.series?.forEach((s: SeriesInfo) => {
        newInfo[s.series_id] = s;
      });
      setAllSeriesInfo(prev => ({ ...prev, ...newInfo }));
    } catch (error) {
      console.error('Failed to search series:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleDrillDown = async () => {
    if (!drillGroup) return;
    setLoadingDrill(true);
    try {
      const res = await wpResearchAPI.getSeries<SeriesListData>({ group_code: drillGroup, limit: 200 });
      setDrillResults(res.data);
      const newInfo: Record<string, SeriesInfo> = {};
      res.data?.series?.forEach((s: SeriesInfo) => {
        newInfo[s.series_id] = s;
      });
      setAllSeriesInfo(prev => ({ ...prev, ...newInfo }));
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
      const allResults = [...(searchResults?.series || []), ...(drillResults?.series || []), ...(browseResults?.series || [])];
      const found = allResults.find(s => s.series_id === seriesId);
      if (found) {
        setAllSeriesInfo(prev => ({ ...prev, [seriesId]: found }));
      }
    }
  };

  const toggleGroup = (code: string) => {
    setSelectedGroups(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : prev.length < 6 ? [...prev, code] : prev
    );
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Section 1: Final Demand Overview - HEADLINE PPI */}
      <Card>
        <SectionHeader title="Final Demand PPI (Headline)" color="blue" icon={TrendingUp} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">
            The headline Producer Price Index reported in BLS press releases. Final Demand measures price changes for goods, services, and construction sold for personal consumption, capital investment, government, and export.
          </p>
          {loadingOverview ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Headline Card - THE main number */}
              {overview?.headline && (
                <div className="mb-6 p-6 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-blue-100 text-sm font-medium">Producer Price Index - Final Demand</p>
                      <p className="text-3xl font-bold mt-1">{overview.headline.name}</p>
                      <p className="text-blue-200 text-sm mt-1">{overview.headline.latest_date}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-blue-100 text-xs">Month-over-Month</p>
                      <p className="text-4xl font-bold">
                        {overview.headline.mom_pct != null
                          ? `${overview.headline.mom_pct >= 0 ? '+' : ''}${overview.headline.mom_pct.toFixed(1)}%`
                          : 'N/A'}
                      </p>
                      <p className="text-blue-200 text-sm mt-2">
                        YoY: {overview.headline.yoy_pct != null
                          ? `${overview.headline.yoy_pct >= 0 ? '+' : ''}${overview.headline.yoy_pct.toFixed(1)}%`
                          : 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Component Cards */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
                {overview?.components?.map((comp) => (
                  <div key={comp.series_id} className="p-3 rounded-lg border border-gray-200 bg-gray-50 hover:shadow-md transition-shadow">
                    <p className="text-xs font-medium text-gray-600 line-clamp-2 mb-2" title={comp.name}>
                      {comp.name}
                    </p>
                    <div className="space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] text-gray-500">MoM</span>
                        <span className={`text-base font-bold ${
                          (comp.mom_pct ?? 0) > 0 ? 'text-green-600' : (comp.mom_pct ?? 0) < 0 ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          {comp.mom_pct != null ? `${comp.mom_pct >= 0 ? '+' : ''}${comp.mom_pct.toFixed(2)}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] text-gray-500">YoY</span>
                        <span className={`text-sm font-semibold ${
                          (comp.yoy_pct ?? 0) > 0 ? 'text-green-600' : (comp.yoy_pct ?? 0) < 0 ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          {comp.yoy_pct != null ? `${comp.yoy_pct >= 0 ? '+' : ''}${comp.yoy_pct.toFixed(2)}%` : 'N/A'}
                        </span>
                      </div>
                    </div>
                    <p className="text-[9px] text-gray-400 mt-1.5">
                      Idx: {comp.index_value?.toFixed(1) || 'N/A'}
                    </p>
                  </div>
                ))}
              </div>

              {/* Timeline Chart */}
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold text-gray-700">Final Demand Price Changes (%)</h3>
                <Select
                  value={overviewTimeRange}
                  onChange={(v) => setOverviewTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
              </div>
              {overviewTimeline?.timeline && (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={overviewTimeline.timeline}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis
                        dataKey="period_name"
                        tick={{ fontSize: 10 }}
                        angle={-45}
                        textAnchor="end"
                        height={60}
                      />
                      <YAxis
                        tick={{ fontSize: 11 }}
                        tickFormatter={(v) => `${v}%`}
                        domain={['auto', 'auto']}
                      />
                      <Tooltip formatter={(value: number) => [`${value?.toFixed(2)}%`, '']} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      {Object.keys(overviewTimeline.category_names || {}).map((key, idx) => (
                        <Line
                          key={key}
                          type="monotone"
                          dataKey={`categories.${key}`}
                          stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                          strokeWidth={key === 'fd_total' ? 3 : 2}
                          dot={false}
                          name={overviewTimeline.category_names?.[key] || key}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 2: Intermediate Demand */}
      <Card>
        <SectionHeader title="Intermediate Demand (Production Stages)" color="purple" icon={Layers} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">
            Price indexes at different stages of production. Stage 4 is most processed (closest to final demand), Stage 1 is least processed (raw materials).
          </p>
          {loadingIntermediate ? (
            <LoadingSpinner />
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {intermediateDemand?.stages?.map((stage, idx) => (
                <div
                  key={stage.stage}
                  className={`p-4 rounded-lg border-2 ${
                    idx === 0 ? 'border-purple-500 bg-purple-50' : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <p className="text-xs font-bold text-gray-600 mb-1">{stage.stage_name}</p>
                  <p className="text-[10px] text-gray-400 mb-3">{stage.latest_date}</p>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">MoM</span>
                      <span className={`text-lg font-bold ${
                        (stage.mom_pct ?? 0) > 0 ? 'text-green-600' : (stage.mom_pct ?? 0) < 0 ? 'text-red-600' : 'text-gray-500'
                      }`}>
                        {stage.mom_pct != null ? `${stage.mom_pct >= 0 ? '+' : ''}${stage.mom_pct.toFixed(2)}%` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">YoY</span>
                      <span className={`text-sm font-semibold ${
                        (stage.yoy_pct ?? 0) > 0 ? 'text-green-600' : (stage.yoy_pct ?? 0) < 0 ? 'text-red-600' : 'text-gray-500'
                      }`}>
                        {stage.yoy_pct != null ? `${stage.yoy_pct >= 0 ? '+' : ''}${stage.yoy_pct.toFixed(2)}%` : 'N/A'}
                      </span>
                    </div>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-2">
                    Index: {stage.index_value?.toFixed(1) || 'N/A'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Section 3: Commodity Groups */}
      <Card>
        <SectionHeader title="Commodity Group Analysis" color="green" icon={Package} />
        <div className="p-5">
          <div className="flex flex-wrap gap-4 mb-4 items-end">
            <Select
              label="Show"
              value={groupFilter}
              onChange={(v) => setGroupFilter(v as 'all' | 'commodity' | 'fd')}
              options={[
                { value: 'commodity', label: 'Commodity Groups' },
                { value: 'fd', label: 'Final Demand Groups' },
                { value: 'all', label: 'All Groups' },
              ]}
              className="w-48"
            />
            <Select
              label="Time Range"
              value={groupTimeRange}
              onChange={(v) => setGroupTimeRange(parseInt(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <ViewToggle value={groupView} onChange={setGroupView} />
          </div>

          {loadingGroups ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Group Selection */}
              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-2">Select groups to compare (max 6):</p>
                <div className="flex flex-wrap gap-2">
                  {groupsData?.groups?.slice(0, 15).map((group) => (
                    <button
                      key={group.group_code}
                      onClick={() => toggleGroup(group.group_code)}
                      className={`px-3 py-1.5 text-xs rounded-full border transition-colors ${
                        selectedGroups.includes(group.group_code)
                          ? 'bg-green-500 text-white border-green-500'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-green-400'
                      }`}
                    >
                      <span className="font-mono mr-1">{group.group_code}</span>
                      {group.group_name.substring(0, 25)}{group.group_name.length > 25 ? '...' : ''}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chart/Table */}
              {groupView === 'chart' && groupTimeline?.timeline && (
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={groupTimeline.timeline}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={60} />
                      <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      {selectedGroups.map((code, idx) => (
                        <Line
                          key={code}
                          type="monotone"
                          dataKey={`groups.${code}`}
                          stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                          strokeWidth={2}
                          dot={false}
                          name={groupTimeline.group_names?.[code]?.substring(0, 30) || code}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {groupView === 'table' && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                        <th className="py-2 px-3">Code</th>
                        <th className="py-2 px-3">Group Name</th>
                        <th className="py-2 px-3 text-right">MoM %</th>
                        <th className="py-2 px-3 text-right">YoY %</th>
                        <th className="py-2 px-3 text-right">Index</th>
                      </tr>
                    </thead>
                    <tbody>
                      {groupsData?.groups?.map((group) => (
                        <tr key={group.group_code} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3 font-mono text-xs">{group.group_code}</td>
                          <td className="py-2 px-3">{group.group_name}</td>
                          <td className={`py-2 px-3 text-right font-semibold ${
                            (group.mom_pct ?? 0) > 0 ? 'text-green-600' : (group.mom_pct ?? 0) < 0 ? 'text-red-600' : ''
                          }`}>
                            {formatChange(group.mom_pct, '%')}
                          </td>
                          <td className={`py-2 px-3 text-right ${
                            (group.yoy_pct ?? 0) > 0 ? 'text-green-600' : (group.yoy_pct ?? 0) < 0 ? 'text-red-600' : ''
                          }`}>
                            {formatChange(group.yoy_pct, '%')}
                          </td>
                          <td className="py-2 px-3 text-right text-gray-500">{formatIndex(group.latest_value)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 4: Item Analysis */}
      <Card>
        <SectionHeader title="Item Analysis" color="orange" />
        <div className="p-5">
          <div className="flex gap-4 mb-4 items-end">
            <Select
              label="Select Group"
              value={selectedGroupForItems}
              onChange={(v) => setSelectedGroupForItems(v)}
              options={[
                { value: '', label: 'Choose a group...' },
                ...(dimensions?.commodity_groups?.slice(0, 50)?.map(g => ({
                  value: g.group_code,
                  label: `${g.group_code} - ${g.group_name.substring(0, 40)}`
                })) || [])
              ]}
              className="w-80"
            />
            <Select
              label="Time Range"
              value={itemTimeRange}
              onChange={(v) => setItemTimeRange(parseInt(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <ViewToggle value={itemView} onChange={setItemView} />
          </div>

          {loadingItems ? (
            <LoadingSpinner />
          ) : itemsData?.items?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                    <th className="py-2 px-3">Code</th>
                    <th className="py-2 px-3">Item Name</th>
                    <th className="py-2 px-3 text-right">MoM %</th>
                    <th className="py-2 px-3 text-right">YoY %</th>
                    <th className="py-2 px-3 text-right">Index</th>
                  </tr>
                </thead>
                <tbody>
                  {itemsData.items.map((item) => (
                    <tr key={item.item_code} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-2 px-3 font-mono text-xs">{item.item_code}</td>
                      <td className="py-2 px-3">{item.item_name}</td>
                      <td className={`py-2 px-3 text-right font-semibold ${
                        (item.mom_pct ?? 0) > 0 ? 'text-green-600' : (item.mom_pct ?? 0) < 0 ? 'text-red-600' : ''
                      }`}>
                        {formatChange(item.mom_pct, '%')}
                      </td>
                      <td className={`py-2 px-3 text-right ${
                        (item.yoy_pct ?? 0) > 0 ? 'text-green-600' : (item.yoy_pct ?? 0) < 0 ? 'text-red-600' : ''
                      }`}>
                        {formatChange(item.yoy_pct, '%')}
                      </td>
                      <td className="py-2 px-3 text-right text-gray-500">{formatIndex(item.latest_value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Select a group to view items</p>
          )}
        </div>
      </Card>

      {/* Section 5: Top Movers */}
      <Card>
        <SectionHeader title="Top Price Movers" color="red" />
        <div className="p-5">
          <div className="mb-4">
            <Select
              label="Period"
              value={moverPeriod}
              onChange={(v) => setMoverPeriod(v as MoverPeriod)}
              options={[
                { value: 'mom', label: 'Month-over-Month' },
                { value: 'yoy', label: 'Year-over-Year' },
              ]}
              className="w-48"
            />
          </div>

          {loadingTopMovers ? (
            <LoadingSpinner />
          ) : (
            <div className="grid md:grid-cols-2 gap-6">
              {/* Gainers */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <ArrowUpCircle className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-green-700">Top Gainers</h3>
                </div>
                <div className="space-y-2">
                  {topMovers?.gainers?.map((m, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2 bg-green-50 rounded border border-green-100">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{m.group_name}</p>
                        {m.item_name && <p className="text-xs text-gray-500">{m.item_name}</p>}
                      </div>
                      <span className="text-green-600 font-bold">
                        +{m.change_pct?.toFixed(2)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Losers */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <ArrowDownCircle className="w-5 h-5 text-red-600" />
                  <h3 className="font-semibold text-red-700">Top Losers</h3>
                </div>
                <div className="space-y-2">
                  {topMovers?.losers?.map((m, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2 bg-red-50 rounded border border-red-100">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{m.group_name}</p>
                        {m.item_name && <p className="text-xs text-gray-500">{m.item_name}</p>}
                      </div>
                      <span className="text-red-600 font-bold">
                        {m.change_pct?.toFixed(2)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Section 6: Series Explorer */}
      <Card>
        <SectionHeader title="Series Explorer" color="cyan" />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-6">
            Access all WP series through search, drill-down by group, or paginated browsing.
          </p>

          {/* Search */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-cyan-50 to-blue-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-cyan-800">Search Series</h3>
              <p className="text-xs text-gray-600">Find series by keyword</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleSearch()}
                  placeholder="Enter keyword (e.g., 'gasoline', 'steel', 'lumber')..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || loadingSearch}
                  className="px-6 py-2 bg-cyan-600 text-white rounded-md hover:bg-cyan-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loadingSearch && <Loader2 className="w-4 h-4 animate-spin" />}
                  Search
                </button>
              </div>

              {searchResults && (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-700">
                      Found {searchResults.total} series
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-64">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Group</th>
                          <th className="py-2 px-3">Item</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.series?.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(s.series_id) ? 'bg-cyan-50' : 'hover:bg-gray-50'
                            }`}
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
                            <td className="py-2 px-3 text-xs">{s.group_name || s.group_code}</td>
                            <td className="py-2 px-3 text-xs">{s.item_name || '-'}</td>
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

          {/* Drill-down */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-green-800">Drill-down by Group</h3>
              <p className="text-xs text-gray-600">Select a commodity group to see all its series</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <Select
                  label="Select Group"
                  value={drillGroup}
                  onChange={(v) => { setDrillGroup(v); setDrillResults(null); }}
                  options={[
                    { value: '', label: 'Choose a group...' },
                    ...(dimensions?.commodity_groups?.map(g => ({
                      value: g.group_code,
                      label: `${g.group_code} - ${g.group_name.substring(0, 40)}`
                    })) || [])
                  ]}
                  className="w-80"
                />
                <button
                  onClick={handleDrillDown}
                  disabled={!drillGroup || loadingDrill}
                  className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 self-end"
                >
                  {loadingDrill && <Loader2 className="w-4 h-4 animate-spin" />}
                  Find Series
                </button>
              </div>

              {drillResults && (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-700">
                      {drillResults.total} series in this group
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-64">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Item</th>
                          <th className="py-2 px-3">SA</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {drillResults.series?.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(s.series_id) ? 'bg-green-50' : 'hover:bg-gray-50'
                            }`}
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
                            <td className="py-2 px-3 text-xs">{s.item_name || '-'}</td>
                            <td className="py-2 px-3">
                              <span className="px-1.5 py-0.5 text-xs bg-gray-100 rounded">
                                {s.seasonal_code === 'S' ? 'SA' : 'NSA'}
                              </span>
                            </td>
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

          {/* Browse */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-purple-800">Browse All Series</h3>
              <p className="text-xs text-gray-600">Paginated view with filters</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4 flex-wrap">
                <Select
                  label="Group"
                  value={browseGroup}
                  onChange={(v) => { setBrowseGroup(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'All Groups' },
                    ...(dimensions?.commodity_groups?.slice(0, 50)?.map(g => ({
                      value: g.group_code,
                      label: `${g.group_code} - ${g.group_name.substring(0, 30)}`
                    })) || [])
                  ]}
                  className="w-64"
                />
                <Select
                  label="Seasonal"
                  value={browseSeasonal}
                  onChange={(v) => { setBrowseSeasonal(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'All' },
                    { value: 'S', label: 'Seasonally Adjusted' },
                    { value: 'U', label: 'Not Adjusted' },
                  ]}
                  className="w-40"
                />
                <Select
                  label="Base Year"
                  value={browseBaseYear}
                  onChange={(v) => { setBrowseBaseYear(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'Any' },
                    ...(dimensions?.base_years?.map(y => ({
                      value: y.toString(),
                      label: y.toString()
                    })) || [])
                  ]}
                  className="w-28"
                />
                <Select
                  label="Per Page"
                  value={browseLimit}
                  onChange={(v) => { setBrowseLimit(parseInt(v)); setBrowseOffset(0); }}
                  options={[
                    { value: 25, label: '25' },
                    { value: 50, label: '50' },
                    { value: 100, label: '100' },
                  ]}
                  className="w-24"
                />
              </div>

              <div className="border border-gray-200 rounded-lg">
                <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">
                    {browseResults ? `${browseResults.total.toLocaleString()} total series` : 'Loading...'}
                  </span>
                  {selectedSeriesIds.length > 0 && (
                    <button
                      onClick={() => setSelectedSeriesIds([])}
                      className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100"
                    >
                      Clear Selection ({selectedSeriesIds.length})
                    </button>
                  )}
                </div>
                <div className="overflow-x-auto max-h-80">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                        <th className="py-2 px-3 w-8"></th>
                        <th className="py-2 px-3">Series ID</th>
                        <th className="py-2 px-3">Group</th>
                        <th className="py-2 px-3">Item</th>
                        <th className="py-2 px-3">SA</th>
                        <th className="py-2 px-3">Period</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loadingBrowse ? (
                        <tr><td colSpan={6} className="py-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-gray-400" /></td></tr>
                      ) : browseResults?.series?.length === 0 ? (
                        <tr><td colSpan={6} className="py-8 text-center text-gray-500">No series found.</td></tr>
                      ) : (
                        browseResults?.series?.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(s.series_id) ? 'bg-purple-50' : 'hover:bg-gray-50'
                            }`}
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
                            <td className="py-2 px-3 text-xs">{s.group_name?.substring(0, 25) || s.group_code}</td>
                            <td className="py-2 px-3 text-xs">{s.item_name?.substring(0, 20) || '-'}</td>
                            <td className="py-2 px-3">
                              <span className="px-1.5 py-0.5 text-xs bg-gray-100 rounded">
                                {s.seasonal_code === 'S' ? 'SA' : 'NSA'}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-xs">{s.begin_year} - {s.end_year || 'Present'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {browseResults && browseResults.total > 0 && (
                  <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
                    <span className="text-sm text-gray-600">
                      Showing {browseOffset + 1} - {Math.min(browseOffset + browseLimit, browseResults.total)} of {browseResults.total.toLocaleString()}
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

          {/* Selected Series Chart */}
          {selectedSeriesIds.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-3 bg-gradient-to-r from-cyan-100 to-blue-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-cyan-800">
                    {seriesView === 'chart' ? 'Series Comparison Chart' : 'Series Data Table'}
                  </p>
                  <p className="text-xs text-gray-600">{selectedSeriesIds.length} series selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={seriesTimeRange}
                    onChange={(v) => setSeriesTimeRange(parseInt(v))}
                    options={timeRangeOptions}
                    className="w-36"
                  />
                  <ViewToggle value={seriesView} onChange={setSeriesView} />
                </div>
              </div>

              {seriesView === 'chart' ? (
                <div className="p-4 h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="period_name" type="category" allowDuplicatedCategory={false} tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={80} />
                      <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      {selectedSeriesIds.map((seriesId, idx) => {
                        const chartData = seriesChartData[seriesId];
                        if (!chartData?.series?.[0]) return null;
                        const seriesInfo = allSeriesInfo[seriesId];
                        const label = seriesInfo?.group_name?.substring(0, 20) || seriesId;
                        const filteredData = seriesTimeRange === 0
                          ? chartData.series[0].data_points
                          : chartData.series[0].data_points.slice(-seriesTimeRange);
                        return (
                          <Line
                            key={seriesId}
                            data={filteredData}
                            type="monotone"
                            dataKey="value"
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            strokeWidth={2}
                            dot={false}
                            name={label}
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
                        {selectedSeriesIds.map((seriesId) => {
                          const info = allSeriesInfo[seriesId];
                          return (
                            <th key={seriesId} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                              {info?.group_name?.substring(0, 15) || seriesId}
                            </th>
                          );
                        })}
                      </tr>
                    </thead>
                    <tbody>
                      {(() => {
                        const allPeriods = new Map<string, { year: number; period: string; period_name: string; values: Record<string, number> }>();
                        selectedSeriesIds.forEach((seriesId) => {
                          const chartData = seriesChartData[seriesId];
                          if (!chartData?.series?.[0]) return;
                          const filteredData = seriesTimeRange === 0
                            ? chartData.series[0].data_points
                            : chartData.series[0].data_points.slice(-seriesTimeRange);
                          filteredData.forEach((dp) => {
                            const key = `${dp.year}-${dp.period}`;
                            if (!allPeriods.has(key)) {
                              allPeriods.set(key, { year: dp.year, period: dp.period, period_name: dp.period_name, values: {} });
                            }
                            allPeriods.get(key)!.values[seriesId] = dp.value;
                          });
                        });
                        const sortedPeriods = Array.from(allPeriods.values()).sort((a, b) => {
                          if (b.year !== a.year) return b.year - a.year;
                          return b.period.localeCompare(a.period);
                        });
                        return sortedPeriods.map((period) => (
                          <tr key={`${period.year}-${period.period}`} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-2 px-3 font-medium">{period.period_name}</td>
                            {selectedSeriesIds.map((seriesId) => (
                              <td key={seriesId} className="py-2 px-3 text-right">
                                {period.values[seriesId] != null ? period.values[seriesId].toFixed(1) : '-'}
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
