// frontend/src/pages/bls/CUExplorer.tsx
import { useState, useEffect, useMemo, ReactElement, ChangeEvent, ReactNode } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { TrendingUp, TrendingDown, Loader2, X } from 'lucide-react';
import { cuResearchAPI } from '../../services/api';
import { getAreaCoordinates } from '../../utils/areaCoordinates';
import 'leaflet/dist/leaflet.css';

/**
 * CU Explorer - Consumer Price Index Explorer
 *
 * Full-featured explorer with:
 * 1. Overview - Headline & Core CPI with timeline chart and period selector
 * 2. Category Analysis - Major CPI categories with timeline and period selector
 * 3. Area Comparison - Compare across metro areas with timeline
 * 4. Geographic View - Map with clickable markers
 * 5. Series Explorer - Search, filter, and chart specific series
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface PeriodSelection {
  year: number;
  period: string;
}

interface TimelinePoint {
  year: number;
  period: string;
  period_name: string;
  headline_value?: number;
  headline_mom?: number;
  headline_yoy?: number;
  core_value?: number;
  core_mom?: number;
  core_yoy?: number;
  categories?: CategoryData[];
  areas?: AreaData[];
}

interface CPIMetric {
  latest_value?: number;
  month_over_month?: number;
  year_over_year?: number;
  latest_date?: string;
}

interface OverviewData {
  headline_cpi?: CPIMetric;
  core_cpi?: CPIMetric;
  area_name?: string;
}

interface TimelineData {
  timeline: TimelinePoint[];
}

interface CategoryData {
  category_code: string;
  category_name: string;
  latest_value?: number;
  month_over_month?: number;
  year_over_year?: number;
}

interface CategoryAnalysisData {
  area_name: string;
  categories: CategoryData[];
}

interface AreaData {
  area_code: string;
  area_name: string;
  latest_value?: number;
  month_over_month?: number;
  year_over_year?: number;
  series_id?: string;
}

interface AreaComparisonData {
  item_name: string;
  areas: AreaData[];
}

interface DimensionArea {
  area_code: string;
  area_name: string;
  selectable?: boolean;
}

interface DimensionItem {
  item_code: string;
  item_name: string;
  selectable?: boolean;
}

interface DimensionsData {
  areas?: DimensionArea[];
  items?: DimensionItem[];
}

interface SeriesInfo {
  series_id: string;
  area_name?: string;
  item_name?: string;
  seasonal_code?: string;
  begin_period?: string;
  begin_year?: number;
  end_period?: string;
  end_year?: number;
  data_points?: DataPoint[];
}

interface DataPoint {
  year: number;
  period: string;
  period_name: string;
  value: number;
}

interface SeriesListData {
  total: number;
  series: SeriesInfo[];
}

interface SeriesDataResponse {
  series: SeriesInfo[];
}

interface SeriesChartDataMap {
  [seriesId: string]: SeriesDataResponse;
}

interface MapAreaWithCoords extends AreaData {
  lat: number;
  lng: number;
  displayValue: number | null | undefined;
  color: string;
}

interface SelectOption {
  value: string | number;
  label: string;
}

interface ChartDataPoint {
  period_name: string;
  sortKey: number;
  [key: string]: string | number;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatPercent = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

const CHART_COLORS = [
  '#3b82f6', '#22c55e', '#ef4444', '#f97316', '#8b5cf6',
  '#06b6d4', '#ec4899', '#78716c', '#14b8a6', '#f59e0b',
  '#6366f1', '#84cc16', '#a855f7', '#0ea5e9', '#d946ef'
];

const getInflationColor = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '#9e9e9e';
  if (value < 0) return '#22c55e';
  if (value < 1) return '#86efac';
  if (value < 2) return '#bef264';
  if (value < 3) return '#fde047';
  if (value < 4) return '#fb923c';
  if (value < 5) return '#f87171';
  return '#ef4444';
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

interface CardProps {
  children: ReactNode;
  className?: string;
}

function Card({ children, className = '' }: CardProps): ReactElement {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm ${className}`}>
      {children}
    </div>
  );
}

type SectionColor = 'blue' | 'purple' | 'green' | 'amber' | 'cyan';

interface SectionHeaderProps {
  title: string;
  color?: SectionColor;
}

function SectionHeader({ title, color = 'blue' }: SectionHeaderProps): ReactElement {
  const colorClasses: Record<SectionColor, string> = {
    blue: 'border-blue-500 bg-blue-50 text-blue-700',
    purple: 'border-purple-500 bg-purple-50 text-purple-700',
    green: 'border-green-500 bg-green-50 text-green-700',
    amber: 'border-amber-500 bg-amber-50 text-amber-700',
    cyan: 'border-cyan-500 bg-cyan-50 text-cyan-700',
  };
  return (
    <div className={`px-5 py-3 border-b-2 ${colorClasses[color]}`}>
      <h2 className="text-lg font-bold">{title}</h2>
    </div>
  );
}

function LoadingSpinner(): ReactElement {
  return (
    <div className="flex justify-center items-center py-12">
      <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );
}

interface MetricCardProps {
  title: string;
  subtitle: string;
  value?: number;
  mom?: number;
  yoy?: number;
  variant?: 'blue' | 'purple';
}

function MetricCard({ title, subtitle, value, mom, yoy, variant = 'blue' }: MetricCardProps): ReactElement {
  const bgClass = variant === 'blue' ? 'bg-blue-50 border-blue-200' : 'bg-purple-50 border-purple-200';

  return (
    <div className={`p-4 rounded-lg border ${bgClass}`}>
      <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</div>
      <div className="text-xs text-gray-500 mb-1">{subtitle}</div>
      <div className="text-base font-semibold text-gray-600 mb-3">
        Index: {value?.toFixed(2) || 'N/A'}
      </div>
      <div className="flex gap-6">
        <div>
          <div className="text-xs text-gray-500 mb-0.5">Month/Month</div>
          <div className={`text-2xl font-bold ${(mom ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
            {formatPercent(mom)}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500 mb-0.5">Year/Year</div>
          <div className={`text-2xl font-bold ${(yoy ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
            {formatPercent(yoy)}
          </div>
        </div>
      </div>
    </div>
  );
}

interface SelectProps {
  label?: string;
  value: string | number;
  onChange: (value: string) => void;
  options: SelectOption[];
  className?: string;
}

function Select({ label, value, onChange, options, className = '' }: SelectProps): ReactElement {
  return (
    <div className={className}>
      {label && <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>}
      <select
        value={value}
        onChange={(e: ChangeEvent<HTMLSelectElement>) => onChange(e.target.value)}
        className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

type TimelineColor = 'blue' | 'purple' | 'green';

interface TimelineSelectorProps {
  timeline: TimelinePoint[];
  selectedPeriod: PeriodSelection | null;
  onSelect: (period: PeriodSelection) => void;
  color?: TimelineColor;
}

function TimelineSelector({ timeline, selectedPeriod, onSelect, color = 'blue' }: TimelineSelectorProps): ReactElement | null {
  if (!timeline || timeline.length === 0) return null;

  const colorClasses: Record<TimelineColor, { active: string; light: string; text: string }> = {
    blue: { active: 'bg-blue-600 border-blue-800', light: 'bg-blue-400', text: 'text-blue-600' },
    purple: { active: 'bg-purple-600 border-purple-800', light: 'bg-purple-400', text: 'text-purple-600' },
    green: { active: 'bg-green-600 border-green-800', light: 'bg-green-400', text: 'text-green-600' },
  };
  const colors = colorClasses[color] || colorClasses.blue;

  return (
    <div className="mt-4 px-2">
      <p className="text-xs text-gray-500 mb-3">Select Month (click any point):</p>
      <div className="relative h-14">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-300" />
        <div className="relative flex justify-between">
          {timeline.map((point, index) => {
            const isSelected = selectedPeriod?.year === point.year && selectedPeriod?.period === point.period;
            const isLatest = index === timeline.length - 1;
            const shouldShowLabel = index % Math.max(1, Math.floor(timeline.length / 8)) === 0 || index === timeline.length - 1;

            return (
              <div
                key={`${point.year}-${point.period}`}
                className="relative flex flex-col items-center cursor-pointer group"
                onClick={() => onSelect({ year: point.year, period: point.period })}
              >
                <div
                  className={`
                    w-3 h-3 rounded-full border-2 transition-all duration-200 group-hover:scale-150
                    ${isSelected
                      ? `w-3.5 h-3.5 ${colors.active} border-2 shadow-md z-10`
                      : isLatest && !selectedPeriod
                        ? `${colors.light} border-white`
                        : 'bg-gray-400 border-white'
                    }
                  `}
                />
                {(shouldShowLabel || isSelected) && (
                  <span
                    className={`
                      absolute top-7 text-[10px] whitespace-nowrap origin-top-left -rotate-45
                      ${isSelected ? `font-semibold ${colors.text}` : 'text-gray-500'}
                    `}
                  >
                    {point.period_name}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function CUExplorer(): ReactElement {
  // Dimensions state
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [loadingDimensions, setLoadingDimensions] = useState(true);

  // Overview state
  const [selectedAreaOverview, setSelectedAreaOverview] = useState('0000');
  const [overviewTimeRange, setOverviewTimeRange] = useState(12);
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [overviewTimeline, setOverviewTimeline] = useState<TimelineData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [selectedOverviewPeriod, setSelectedOverviewPeriod] = useState<PeriodSelection | null>(null);

  // Category state
  const [selectedAreaCategory, setSelectedAreaCategory] = useState('0000');
  const [categoryTimeRange, setCategoryTimeRange] = useState(12);
  const [categories, setCategories] = useState<CategoryAnalysisData | null>(null);
  const [categoryTimeline, setCategoryTimeline] = useState<TimelineData | null>(null);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [selectedCategoryPeriod, setSelectedCategoryPeriod] = useState<PeriodSelection | null>(null);

  // Area comparison state
  const [selectedItem, setSelectedItem] = useState('SA0');
  const [areaTimeRange, setAreaTimeRange] = useState(12);
  const [areaComparison, setAreaComparison] = useState<AreaComparisonData | null>(null);
  const [areaTimeline, setAreaTimeline] = useState<TimelineData | null>(null);
  const [loadingAreas, setLoadingAreas] = useState(true);
  const [selectedAreaPeriod, setSelectedAreaPeriod] = useState<PeriodSelection | null>(null);

  // Map state
  const [mapItem, setMapItem] = useState('SA0');
  const [mapMetric, setMapMetric] = useState<'yoy' | 'mom'>('yoy');
  const [mapData, setMapData] = useState<AreaComparisonData | null>(null);
  const [loadingMap, setLoadingMap] = useState(true);
  const [mapSelectedSeries, setMapSelectedSeries] = useState<string[]>([]);

  // Series explorer state - Search method
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Series explorer state - Drill-down method (existing filter-based approach)
  const [selectedAreaDetail, setSelectedAreaDetail] = useState('');
  const [selectedItemDetail, setSelectedItemDetail] = useState('');
  const [selectedSeasonal, setSelectedSeasonal] = useState('');
  const [seriesData, setSeriesData] = useState<SeriesListData | null>(null);
  const [loadingSeries, setLoadingSeries] = useState(false);

  // Series explorer state - Browse method
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseLimit] = useState(50);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series explorer state - Selected series for comparison
  const [selectedSeries, setSelectedSeries] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<SeriesChartDataMap>({});
  const [seriesView, setSeriesView] = useState<'chart' | 'table'>('chart');
  const [seriesTimeRange, setSeriesTimeRange] = useState(60);

  // Load dimensions
  useEffect(() => {
    const loadDimensions = async (): Promise<void> => {
      try {
        const response = await cuResearchAPI.getDimensions();
        setDimensions(response.data as DimensionsData);
      } catch (error) {
        console.error('Failed to load dimensions:', error);
      } finally {
        setLoadingDimensions(false);
      }
    };
    loadDimensions();
  }, []);

  // Load overview data
  useEffect(() => {
    const loadOverview = async (): Promise<void> => {
      setLoadingOverview(true);
      setSelectedOverviewPeriod(null);
      try {
        const [overviewRes, timelineRes] = await Promise.all([
          cuResearchAPI.getOverview(selectedAreaOverview),
          cuResearchAPI.getOverviewTimeline(selectedAreaOverview, overviewTimeRange)
        ]);
        setOverview(overviewRes.data as OverviewData);
        setOverviewTimeline(timelineRes.data as TimelineData);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    loadOverview();
  }, [selectedAreaOverview, overviewTimeRange]);

  // Load category data
  useEffect(() => {
    const loadCategories = async (): Promise<void> => {
      setLoadingCategories(true);
      setSelectedCategoryPeriod(null);
      try {
        const [categoriesRes, timelineRes] = await Promise.all([
          cuResearchAPI.getCategoryAnalysis(selectedAreaCategory),
          cuResearchAPI.getCategoryTimeline(selectedAreaCategory, categoryTimeRange)
        ]);
        setCategories(categoriesRes.data as CategoryAnalysisData);
        setCategoryTimeline(timelineRes.data as TimelineData);
      } catch (error) {
        console.error('Failed to load categories:', error);
      } finally {
        setLoadingCategories(false);
      }
    };
    loadCategories();
  }, [selectedAreaCategory, categoryTimeRange]);

  // Load area comparison
  useEffect(() => {
    const loadAreas = async (): Promise<void> => {
      setLoadingAreas(true);
      setSelectedAreaPeriod(null);
      try {
        const [areasRes, timelineRes] = await Promise.all([
          cuResearchAPI.compareAreas(selectedItem),
          cuResearchAPI.getAreaComparisonTimeline(selectedItem, areaTimeRange)
        ]);
        setAreaComparison(areasRes.data as AreaComparisonData);
        setAreaTimeline(timelineRes.data as TimelineData);
      } catch (error) {
        console.error('Failed to load area comparison:', error);
      } finally {
        setLoadingAreas(false);
      }
    };
    loadAreas();
  }, [selectedItem, areaTimeRange]);

  // Load map data
  useEffect(() => {
    const loadMapData = async (): Promise<void> => {
      setLoadingMap(true);
      try {
        const response = await cuResearchAPI.compareAreas(mapItem);
        setMapData(response.data as AreaComparisonData);
      } catch (error) {
        console.error('Failed to load map data:', error);
      } finally {
        setLoadingMap(false);
      }
    };
    loadMapData();
  }, [mapItem]);

  // Load series list
  useEffect(() => {
    const loadSeries = async (): Promise<void> => {
      setLoadingSeries(true);
      try {
        const params: Record<string, string | number | boolean> = {
          limit: 100,
          active_only: true,
        };
        if (selectedAreaDetail) params.area_code = selectedAreaDetail;
        if (selectedItemDetail) params.item_code = selectedItemDetail;
        if (selectedSeasonal) params.seasonal_code = selectedSeasonal;

        const response = await cuResearchAPI.getSeries(params);
        setSeriesData(response.data as SeriesListData);
      } catch (error) {
        console.error('Failed to load series:', error);
      } finally {
        setLoadingSeries(false);
      }
    };
    loadSeries();
  }, [selectedAreaDetail, selectedItemDetail, selectedSeasonal]);

  // Load chart data for selected series
  useEffect(() => {
    const loadChartData = async (): Promise<void> => {
      const newChartData: SeriesChartDataMap = {};
      for (const seriesId of selectedSeries) {
        if (!seriesChartData[seriesId]) {
          try {
            const response = await cuResearchAPI.getSeriesData(seriesId);
            newChartData[seriesId] = response.data as SeriesDataResponse;
          } catch (error) {
            console.error(`Failed to load data for ${seriesId}:`, error);
          }
        }
      }
      if (Object.keys(newChartData).length > 0) {
        setSeriesChartData(prev => ({ ...prev, ...newChartData }));
      }
    };
    if (selectedSeries.length > 0) {
      loadChartData();
    }
  }, [selectedSeries, seriesChartData]);

  // Load chart data for map-selected series
  useEffect(() => {
    const loadMapChartData = async (): Promise<void> => {
      const newChartData: SeriesChartDataMap = {};
      for (const seriesId of mapSelectedSeries) {
        if (!seriesChartData[seriesId]) {
          try {
            const response = await cuResearchAPI.getSeriesData(seriesId);
            newChartData[seriesId] = response.data as SeriesDataResponse;
          } catch (error) {
            console.error(`Failed to load data for ${seriesId}:`, error);
          }
        }
      }
      if (Object.keys(newChartData).length > 0) {
        setSeriesChartData(prev => ({ ...prev, ...newChartData }));
      }
    };
    if (mapSelectedSeries.length > 0) {
      loadMapChartData();
    }
  }, [mapSelectedSeries, seriesChartData]);

  // Browse series (paginated)
  useEffect(() => {
    const loadBrowse = async (): Promise<void> => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, string | number | boolean> = {
          limit: browseLimit,
          offset: browseOffset,
          active_only: true,
        };
        const response = await cuResearchAPI.getSeries(params);
        setBrowseResults(response.data as SeriesListData);
      } catch (error) {
        console.error('Failed to browse series:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    loadBrowse();
  }, [browseLimit, browseOffset]);

  // Search handler
  const handleSearch = async (): Promise<void> => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const params: Record<string, string | number | boolean> = {
        search: searchQuery,
        limit: 100,
        active_only: true,
      };
      const response = await cuResearchAPI.getSeries(params);
      setSearchResults(response.data as SeriesListData);
    } catch (error) {
      console.error('Failed to search series:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  // Toggle series selection
  const toggleSeriesSelection = (seriesId: string): void => {
    if (selectedSeries.includes(seriesId)) {
      setSelectedSeries(selectedSeries.filter(id => id !== seriesId));
    } else if (selectedSeries.length < 5) {
      setSelectedSeries([...selectedSeries, seriesId]);
    }
  };

  // Selectable areas for dropdowns
  const selectableAreas = useMemo((): DimensionArea[] => {
    if (!dimensions?.areas) return [];
    const seen = new Set<string>();
    return dimensions.areas.filter(a => {
      if (!a.selectable || seen.has(a.area_code)) return false;
      seen.add(a.area_code);
      return true;
    });
  }, [dimensions]);

  // Selectable items for dropdowns
  const selectableItems = useMemo((): DimensionItem[] => {
    if (!dimensions?.items) return [];
    return dimensions.items.filter(i => i.selectable);
  }, [dimensions]);

  // Get overview data for selected period
  const overviewDisplayData = useMemo(() => {
    if (selectedOverviewPeriod && overviewTimeline?.timeline) {
      const point = overviewTimeline.timeline.find(
        p => p.year === selectedOverviewPeriod.year && p.period === selectedOverviewPeriod.period
      );
      if (point) {
        return {
          headline: {
            latest_value: point.headline_value,
            month_over_month: point.headline_mom,
            year_over_year: point.headline_yoy,
            latest_date: point.period_name
          },
          core: {
            latest_value: point.core_value,
            month_over_month: point.core_mom,
            year_over_year: point.core_yoy,
            latest_date: point.period_name
          }
        };
      }
    }
    return {
      headline: overview?.headline_cpi,
      core: overview?.core_cpi
    };
  }, [selectedOverviewPeriod, overviewTimeline, overview]);

  // Get category data for selected period
  const categoryDisplayData = useMemo(() => {
    if (selectedCategoryPeriod && categoryTimeline?.timeline) {
      const point = categoryTimeline.timeline.find(
        p => p.year === selectedCategoryPeriod.year && p.period === selectedCategoryPeriod.period
      );
      if (point) {
        return { categories: point.categories, period_name: point.period_name };
      }
    }
    return { categories: categories?.categories, period_name: null as string | null };
  }, [selectedCategoryPeriod, categoryTimeline, categories]);

  // Get area data for selected period
  const areaDisplayData = useMemo(() => {
    if (selectedAreaPeriod && areaTimeline?.timeline) {
      const point = areaTimeline.timeline.find(
        p => p.year === selectedAreaPeriod.year && p.period === selectedAreaPeriod.period
      );
      if (point) {
        return { areas: point.areas, period_name: point.period_name };
      }
    }
    return { areas: areaComparison?.areas, period_name: null as string | null };
  }, [selectedAreaPeriod, areaTimeline, areaComparison]);

  // Combined chart data for selected series
  const combinedChartData = useMemo((): ChartDataPoint[] => {
    const periodMap = new Map<string, ChartDataPoint>();
    selectedSeries.forEach(seriesId => {
      const data = seriesChartData[seriesId]?.series?.[0]?.data_points;
      if (data) {
        data.forEach(point => {
          const key = `${point.year}-${point.period}`;
          if (!periodMap.has(key)) {
            periodMap.set(key, {
              period_name: point.period_name,
              sortKey: point.year * 100 + parseInt(point.period.substring(1))
            });
          }
          const existing = periodMap.get(key)!;
          existing[seriesId] = point.value;
        });
      }
    });
    return Array.from(periodMap.values()).sort((a, b) => a.sortKey - b.sortKey);
  }, [selectedSeries, seriesChartData]);

  // Combined chart data for map-selected series
  const mapCombinedChartData = useMemo((): ChartDataPoint[] => {
    const periodMap = new Map<string, ChartDataPoint>();
    mapSelectedSeries.forEach(seriesId => {
      const data = seriesChartData[seriesId]?.series?.[0]?.data_points;
      if (data) {
        data.forEach(point => {
          const key = `${point.year}-${point.period}`;
          if (!periodMap.has(key)) {
            periodMap.set(key, {
              period_name: point.period_name,
              sortKey: point.year * 100 + parseInt(point.period.substring(1))
            });
          }
          const existing = periodMap.get(key)!;
          existing[seriesId] = point.value;
        });
      }
    });
    return Array.from(periodMap.values()).sort((a, b) => a.sortKey - b.sortKey);
  }, [mapSelectedSeries, seriesChartData]);

  // Map areas with coordinates
  const mapAreas = useMemo((): MapAreaWithCoords[] => {
    if (!mapData?.areas) return [];
    const result: MapAreaWithCoords[] = [];
    for (const area of mapData.areas) {
      const coords = getAreaCoordinates(area.area_code);
      if (!coords) continue;
      const value = mapMetric === 'yoy' ? area.year_over_year : area.month_over_month;
      result.push({
        ...area,
        lat: coords.lat,
        lng: coords.lng,
        displayValue: value,
        color: getInflationColor(value),
      });
    }
    return result;
  }, [mapData, mapMetric]);

  if (loadingDimensions) {
    return <LoadingSpinner />;
  }

  const areaOptions: SelectOption[] = [
    { value: '', label: 'All Areas' },
    ...selectableAreas.map(a => ({ value: a.area_code, label: a.area_name }))
  ];

  const itemOptions: SelectOption[] = [
    { value: '', label: 'All Items' },
    ...selectableItems.map(i => ({ value: i.item_code, label: i.item_name }))
  ];

  const timeRangeOptions: SelectOption[] = [
    { value: 12, label: 'Last 12 months' },
    { value: 24, label: 'Last 2 years' },
    { value: 60, label: 'Last 5 years' },
    { value: 120, label: 'Last 10 years' },
    { value: 240, label: 'Last 20 years' },
    { value: 0, label: 'All Time' },
  ];

  const seasonalOptions: SelectOption[] = [
    { value: '', label: 'All' },
    { value: 'S', label: 'Adjusted' },
    { value: 'U', label: 'Unadjusted' },
  ];

  const cpiCategoryOptions: SelectOption[] = [
    { value: 'SA0', label: 'All items' },
    { value: 'SAF', label: 'Food and beverages' },
    { value: 'SAH', label: 'Housing' },
    { value: 'SAA', label: 'Apparel' },
    { value: 'SAT', label: 'Transportation' },
    { value: 'SAM', label: 'Medical care' },
    { value: 'SAR', label: 'Recreation' },
    { value: 'SAE', label: 'Education and communication' },
    { value: 'SAG', label: 'Other goods and services' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">CU - Consumer Price Index Explorer</h1>
        <p className="text-sm text-gray-600 mt-1">Analyze CPI trends, categories, and area comparisons</p>
      </div>

      {/* Section 1: Overview */}
      <Card>
        <SectionHeader title="Overview" color="blue" />
        <div className="p-5">
          {/* Filters */}
          <div className="flex gap-4 mb-5">
            <Select
              label="Area"
              value={selectedAreaOverview}
              onChange={setSelectedAreaOverview}
              options={selectableAreas.map(a => ({ value: a.area_code, label: a.area_name }))}
              className="w-64"
            />
            <Select
              label="Time Range"
              value={overviewTimeRange}
              onChange={(v) => setOverviewTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-48"
            />
          </div>

          {loadingOverview ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Timeline Chart */}
              {overviewTimeline?.timeline?.length && overviewTimeline.timeline.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Year-over-Year % Change</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={overviewTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={60} />
                        <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="headline_yoy" stroke="#3b82f6" name="Headline YoY" strokeWidth={2} dot={{ r: 2 }} />
                        <Line type="monotone" dataKey="core_yoy" stroke="#8b5cf6" name="Core YoY" strokeWidth={2} dot={{ r: 2 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Timeline Selector */}
                  <TimelineSelector
                    timeline={overviewTimeline.timeline}
                    selectedPeriod={selectedOverviewPeriod}
                    onSelect={setSelectedOverviewPeriod}
                    color="blue"
                  />
                </div>
              )}

              {/* Metric Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <MetricCard
                  title="Headline CPI"
                  subtitle={`All items - ${overviewDisplayData.headline?.latest_date || ''}`}
                  value={overviewDisplayData.headline?.latest_value}
                  mom={overviewDisplayData.headline?.month_over_month}
                  yoy={overviewDisplayData.headline?.year_over_year}
                  variant="blue"
                />
                <MetricCard
                  title="Core CPI"
                  subtitle={`All items less food and energy - ${overviewDisplayData.core?.latest_date || ''}`}
                  value={overviewDisplayData.core?.latest_value}
                  mom={overviewDisplayData.core?.month_over_month}
                  yoy={overviewDisplayData.core?.year_over_year}
                  variant="purple"
                />
              </div>
            </>
          )}
        </div>
      </Card>

      {/* Section 2: Category Analysis */}
      <Card>
        <SectionHeader title="Category Analysis" color="purple" />
        <div className="p-5">
          {/* Filters */}
          <div className="flex gap-4 mb-5">
            <Select
              label="Area"
              value={selectedAreaCategory}
              onChange={setSelectedAreaCategory}
              options={selectableAreas.map(a => ({ value: a.area_code, label: a.area_name }))}
              className="w-64"
            />
            <Select
              label="Time Range"
              value={categoryTimeRange}
              onChange={(v) => setCategoryTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-48"
            />
          </div>

          {loadingCategories ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Timeline Chart */}
              {categoryTimeline?.timeline?.length && categoryTimeline.timeline.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Year-over-Year % Change by Category</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={categoryTimeline.timeline.map(point => ({
                        period_name: point.period_name,
                        ...Object.fromEntries((point.categories || []).map(cat => [cat.category_name, cat.year_over_year]))
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '10px' }} />
                        {categoryTimeline.timeline[0]?.categories?.map((cat, idx) => (
                          <Line
                            key={cat.category_code}
                            type="monotone"
                            dataKey={cat.category_name}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            strokeWidth={2}
                            dot={{ r: 1 }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Timeline Selector */}
                  <TimelineSelector
                    timeline={categoryTimeline.timeline}
                    selectedPeriod={selectedCategoryPeriod}
                    onSelect={setSelectedCategoryPeriod}
                    color="purple"
                  />
                </div>
              )}

              {/* Category Table */}
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-gray-700">
                  {categories?.area_name}
                  {categoryDisplayData.period_name && (
                    <span className="font-normal text-gray-500 ml-2">- {categoryDisplayData.period_name}</span>
                  )}
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 px-3 font-semibold text-gray-700">Category</th>
                      <th className="text-right py-2 px-3 font-semibold text-gray-700">Latest Value</th>
                      <th className="text-right py-2 px-3 font-semibold text-gray-700">M/M Change</th>
                      <th className="text-right py-2 px-3 font-semibold text-gray-700">Y/Y Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryDisplayData.categories?.map((cat) => (
                      <tr key={cat.category_code} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-2 px-3">{cat.category_name}</td>
                        <td className="text-right py-2 px-3">{cat.latest_value?.toFixed(2) || 'N/A'}</td>
                        <td className="text-right py-2 px-3">
                          <span className={`inline-flex items-center gap-1 font-medium ${(cat.month_over_month ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {(cat.month_over_month ?? 0) >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {formatPercent(cat.month_over_month)}
                          </span>
                        </td>
                        <td className="text-right py-2 px-3">
                          <span className={`inline-flex items-center gap-1 font-medium ${(cat.year_over_year ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {(cat.year_over_year ?? 0) >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {formatPercent(cat.year_over_year)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Bar Chart */}
              {categoryDisplayData.categories && categoryDisplayData.categories.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Year-over-Year Changes by Category</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={categoryDisplayData.categories}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="category_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={100} />
                        <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                        <Tooltip />
                        <Bar dataKey="year_over_year">
                          {categoryDisplayData.categories.map((_, idx) => (
                            <Cell key={`cell-${idx}`} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 3: Area Comparison */}
      <Card>
        <SectionHeader title="Area Comparison" color="green" />
        <div className="p-5">
          {/* Filters */}
          <div className="flex gap-4 mb-5">
            <Select
              label="CPI Category"
              value={selectedItem}
              onChange={setSelectedItem}
              options={cpiCategoryOptions}
              className="w-64"
            />
            <Select
              label="Time Range"
              value={areaTimeRange}
              onChange={(v) => setAreaTimeRange(Number(v))}
              options={timeRangeOptions}
              className="w-48"
            />
          </div>

          {loadingAreas ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Timeline Chart */}
              {areaTimeline?.timeline?.length && areaTimeline.timeline.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Year-over-Year % Change by Area</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={areaTimeline.timeline.map(point => ({
                        period_name: point.period_name,
                        ...Object.fromEntries(point.areas?.map(area => [area.area_name, area.year_over_year]) || [])
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '9px' }} />
                        {areaTimeline.timeline[0]?.areas?.map((area, idx) => (
                          <Line
                            key={area.area_code}
                            type="monotone"
                            dataKey={area.area_name}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            strokeWidth={2}
                            dot={{ r: 1 }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Timeline Selector */}
                  <TimelineSelector
                    timeline={areaTimeline.timeline}
                    selectedPeriod={selectedAreaPeriod}
                    onSelect={setSelectedAreaPeriod}
                    color="green"
                  />
                </div>
              )}

              {/* Area Table */}
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-gray-700">
                  {areaComparison?.item_name} - Comparison Across Metro Areas ({areaDisplayData.areas?.length || 0} areas)
                  {areaDisplayData.period_name && (
                    <span className="font-normal text-gray-500 ml-2">- {areaDisplayData.period_name}</span>
                  )}
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 px-3 font-semibold text-gray-700">Area</th>
                      <th className="text-right py-2 px-3 font-semibold text-gray-700">Latest Value</th>
                      <th className="text-right py-2 px-3 font-semibold text-gray-700">Y/Y Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {areaDisplayData.areas?.map((area) => (
                      <tr key={area.area_code} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-2 px-3">{area.area_name}</td>
                        <td className="text-right py-2 px-3">{area.latest_value?.toFixed(2) || 'N/A'}</td>
                        <td className="text-right py-2 px-3">
                          <span className={`inline-flex items-center gap-1 font-medium ${(area.year_over_year ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {(area.year_over_year ?? 0) >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {formatPercent(area.year_over_year)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Bar Chart */}
              {areaDisplayData.areas && areaDisplayData.areas.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Year-over-Year Changes by Area</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={areaDisplayData.areas}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="area_name" tick={{ fontSize: 8 }} angle={-45} textAnchor="end" height={120} />
                        <YAxis label={{ value: '% Change', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                        <Tooltip />
                        <Bar dataKey="year_over_year">
                          {areaDisplayData.areas.map((_, idx) => (
                            <Cell key={`cell-${idx}`} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 4: Geographic View */}
      <Card>
        <SectionHeader title="Geographic View" color="amber" />
        <div className="p-5">
          {/* Controls */}
          <div className="flex gap-4 mb-5 items-end">
            <Select
              label="CPI Category"
              value={mapItem}
              onChange={setMapItem}
              options={cpiCategoryOptions}
              className="w-64"
            />
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Metric</label>
              <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                <button
                  onClick={() => setMapMetric('yoy')}
                  className={`px-3 py-1.5 text-sm ${mapMetric === 'yoy' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                >
                  Year-over-Year %
                </button>
                <button
                  onClick={() => setMapMetric('mom')}
                  className={`px-3 py-1.5 text-sm border-l ${mapMetric === 'mom' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                >
                  Month-over-Month %
                </button>
              </div>
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
                  { label: '< 0% (Deflation)', color: '#22c55e' },
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
              <div className="h-[500px] rounded-lg border border-gray-200 overflow-hidden">
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
                            const series_id = `CU${seasonal_code}R${area.area_code}${mapItem}`;
                            if (!mapSelectedSeries.includes(series_id)) {
                              setMapSelectedSeries([...mapSelectedSeries, series_id]);
                            }
                          },
                        }}
                      >
                        <Popup>
                          <div className="p-1">
                            <div className="font-semibold text-sm">
                              {area.area_name}
                              {isUSAverage && ' ⭐'}
                            </div>
                            <div className="text-xs text-gray-500">{mapData?.item_name}</div>
                            <div className="text-sm mt-1">
                              <strong>{mapMetric === 'yoy' ? 'Y/Y' : 'M/M'}:</strong> {formatPercent(area.displayValue)}
                            </div>
                            <div className="text-sm">
                              <strong>CPI Value:</strong> {area.latest_value?.toFixed(2) || 'N/A'}
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
                    <h3 className="text-sm font-semibold text-gray-700">
                      Selected Areas Comparison
                    </h3>
                    <button
                      onClick={() => setMapSelectedSeries([])}
                      className="px-3 py-1 text-xs text-gray-600 border border-gray-300 rounded-lg hover:bg-white"
                    >
                      Clear All
                    </button>
                  </div>

                  {/* Series chips */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {mapSelectedSeries.map((seriesId, idx) => {
                      const seriesInfo = seriesChartData[seriesId]?.series?.[0];
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

                  {/* Chart */}
                  {mapCombinedChartData.length > 0 && (
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={mapCombinedChartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={70} />
                          <YAxis label={{ value: 'CPI Value', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '10px' }} />
                          {mapSelectedSeries.map((seriesId, idx) => {
                            const seriesInfo = seriesChartData[seriesId]?.series?.[0];
                            return (
                              <Line
                                key={seriesId}
                                type="monotone"
                                dataKey={seriesId}
                                name={seriesInfo?.area_name || seriesId}
                                stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                                strokeWidth={2}
                                dot={{ r: 2 }}
                                connectNulls
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

      {/* Section 5: Series Explorer - 3 Methods */}
      <Card>
        <SectionHeader title="Series Detail Explorer" color="cyan" />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-6">
            Access all CPI series through search, hierarchical navigation, or paginated browsing.
            Select series to compare in charts (max 5).
          </p>

          <div className="grid lg:grid-cols-3 gap-6 mb-6">
            {/* Method 1: Search */}
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
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="e.g., food, housing, energy..."
                    className="flex-1 px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleSearch}
                    disabled={loadingSearch}
                    className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loadingSearch ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
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
                            className={`border-b cursor-pointer ${selectedSeries.includes(s.series_id) ? 'bg-blue-50' : 'hover:bg-gray-50'}`}
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

            {/* Method 2: Drill-down */}
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-2 bg-green-50 border-b border-gray-200 rounded-t-lg">
                <h4 className="text-sm font-bold text-green-700">2. Drill-down</h4>
                <p className="text-xs text-gray-600">Navigate by Area → Item → Seasonal</p>
              </div>
              <div className="p-4">
                <div className="space-y-3 mb-3">
                  <Select
                    label="Area"
                    value={selectedAreaDetail}
                    onChange={setSelectedAreaDetail}
                    options={areaOptions}
                  />
                  <Select
                    label="Item/Category"
                    value={selectedItemDetail}
                    onChange={setSelectedItemDetail}
                    options={itemOptions}
                  />
                  <Select
                    label="Seasonal"
                    value={selectedSeasonal}
                    onChange={setSelectedSeasonal}
                    options={seasonalOptions}
                  />
                </div>

                {loadingSeries ? (
                  <div className="py-4 text-center">
                    <Loader2 className="w-5 h-5 animate-spin mx-auto text-green-600" />
                  </div>
                ) : seriesData?.series && seriesData.series.length > 0 ? (
                  <div className="border border-gray-200 rounded-lg max-h-48 overflow-auto">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b text-left text-xs font-semibold text-gray-600">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series</th>
                        </tr>
                      </thead>
                      <tbody>
                        {seriesData.series.slice(0, 20).map((s) => (
                          <tr
                            key={s.series_id}
                            className={`border-b cursor-pointer ${selectedSeries.includes(s.series_id) ? 'bg-green-50' : 'hover:bg-gray-50'}`}
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
                            <td className="py-2 px-3">
                              <div className="font-mono text-xs">{s.series_id}</div>
                              <div className="text-xs text-gray-500">{s.item_name?.substring(0, 30)}</div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-xs text-gray-500 text-center py-4">Select filters to find series</p>
                )}
              </div>
            </div>

            {/* Method 3: Browse All */}
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-2 bg-purple-50 border-b border-gray-200 rounded-t-lg">
                <h4 className="text-sm font-bold text-purple-700">3. Browse All</h4>
                <p className="text-xs text-gray-600">Paginated view of all series</p>
              </div>
              <div className="p-4">
                {loadingBrowse ? (
                  <div className="py-4 text-center">
                    <Loader2 className="w-5 h-5 animate-spin mx-auto text-purple-600" />
                  </div>
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
                              className={`border-b cursor-pointer ${selectedSeries.includes(s.series_id) ? 'bg-purple-50' : 'hover:bg-gray-50'}`}
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
          {selectedSeries.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-3 bg-gradient-to-r from-cyan-100 to-blue-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-cyan-800">
                    {seriesView === 'chart' ? 'Series Comparison Chart' : 'Series Data Table'}
                  </p>
                  <p className="text-xs text-gray-600">{selectedSeries.length}/5 series selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={seriesTimeRange.toString()}
                    onChange={(v) => setSeriesTimeRange(Number(v))}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <div className="flex border border-gray-300 rounded-md overflow-hidden">
                    <button
                      onClick={() => setSeriesView('table')}
                      className={`px-3 py-1 text-sm ${seriesView === 'table' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                    >
                      Table
                    </button>
                    <button
                      onClick={() => setSeriesView('chart')}
                      className={`px-3 py-1 text-sm ${seriesView === 'chart' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                    >
                      Chart
                    </button>
                  </div>
                  <button
                    onClick={() => setSelectedSeries([])}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                <div className="flex flex-wrap gap-2 mb-4">
                  {selectedSeries.map((seriesId, idx) => {
                    const seriesInfo = seriesChartData[seriesId]?.series?.[0];
                    return (
                      <div
                        key={seriesId}
                        className="flex items-center gap-1 px-2 py-1 bg-gray-50 rounded border text-xs"
                        style={{ borderLeftColor: CHART_COLORS[idx % CHART_COLORS.length], borderLeftWidth: 3 }}
                      >
                        <span>{seriesInfo?.item_name?.substring(0, 30) || seriesId}</span>
                        <button
                          onClick={() => toggleSeriesSelection(seriesId)}
                          className="ml-1 text-gray-400 hover:text-gray-600"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    );
                  })}
                </div>

                {combinedChartData.length > 0 && (
                  seriesView === 'chart' ? (
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={combinedChartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis dataKey="period_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={70} />
                          <YAxis label={{ value: 'CPI Value', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '10px' }} />
                          {selectedSeries.map((seriesId, idx) => (
                            <Line
                              key={seriesId}
                              type="monotone"
                              dataKey={seriesId}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={{ r: 2 }}
                              connectNulls
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
                            {selectedSeries.map((seriesId) => (
                              <th key={seriesId} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                {seriesChartData[seriesId]?.series?.[0]?.item_name?.substring(0, 20) || seriesId}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {combinedChartData.slice().reverse().map((row) => (
                            <tr key={row.period_name} className="border-b border-gray-100 hover:bg-gray-50">
                              <td className="py-2 px-3 font-medium">{row.period_name}</td>
                              {selectedSeries.map((seriesId) => (
                                <td key={seriesId} className="py-2 px-3 text-right">
                                  {row[seriesId] != null ? (row[seriesId] as number).toFixed(1) : '-'}
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
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
