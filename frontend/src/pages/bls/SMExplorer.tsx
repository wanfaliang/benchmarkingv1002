// frontend/src/pages/bls/SMExplorer.tsx
import { useState, useEffect, ReactElement, ChangeEvent, ReactNode } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, X, Search } from 'lucide-react';
import { MapContainer, TileLayer, CircleMarker, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { LatLngBoundsExpression } from 'leaflet';
import { smResearchAPI } from '../../services/api';
import { stateCoordinates, US_BOUNDS } from '../../utils/laAreaCoordinates';

// City coordinates for metro areas (reuse from laAreaCoordinates concept)
import { getLAAreaCoordinates } from '../../utils/laAreaCoordinates';

/**
 * SM Explorer - State and Metro Area Employment Statistics Explorer
 *
 * Sections:
 * 1. State Selection & Overview - Employment by supersector for a state
 * 2. Geographic View - Interactive map of employment
 * 3. State Comparison - All states ranked by employment
 * 4. Metropolitan Areas - Metro area employment data
 * 5. Supersector Analysis - Employment breakdown by supersector
 * 6. Series Detail Explorer - Advanced queries with 3 methods
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
  states?: Record<string, number>;
  metros?: Record<string, number>;
  supersectors?: Record<string, number>;
}

interface StateItem {
  state_code: string;
  state_name: string;
}

interface AreaItem {
  area_code: string;
  area_name: string;
}

interface SupersectorItem {
  supersector_code: string;
  supersector_name: string;
}

interface StateMetric {
  state_code: string;
  state_name: string;
  series_id: string;
  employment?: number;
  latest_date?: string;
  month_over_month?: number;
  month_over_month_pct?: number;
  year_over_year?: number;
  year_over_year_pct?: number;
}

interface MetroMetric {
  state_code: string;
  state_name?: string;
  area_code: string;
  area_name: string;
  series_id: string;
  employment?: number;
  latest_date?: string;
  month_over_month?: number;
  month_over_month_pct?: number;
  year_over_year?: number;
  year_over_year_pct?: number;
}

interface SupersectorMetric {
  supersector_code: string;
  supersector_name: string;
  series_id: string;
  employment?: number;
  latest_date?: string;
  mom_change?: number;
  mom_pct?: number;
  yoy_change?: number;
  yoy_pct?: number;
}

interface OverviewData {
  state_code: string;
  state_name: string;
  area_code: string;
  area_name: string;
  supersectors: SupersectorMetric[];
  last_updated?: string;
}

interface StatesData {
  states: StateMetric[];
  rankings: {
    highest_employment?: string[];
    highest_growth?: string[];
  };
}

interface MetrosData {
  metros: MetroMetric[];
  total_count: number;
}

interface TimelineData {
  timeline: TimelinePoint[];
  state_names?: Record<string, string>;
  metro_names?: Record<string, string>;
  supersector_names?: Record<string, string>;
}

interface DimensionsData {
  states?: StateItem[];
  areas?: AreaItem[];
  supersectors?: SupersectorItem[];
  data_types?: { data_type_code: string; data_type_name: string }[];
}

interface SeriesInfo {
  series_id: string;
  state_name?: string;
  area_name?: string;
  supersector_name?: string;
  industry_name?: string;
  data_type_name?: string;
  seasonal_code?: string;
  begin_year?: number;
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

interface SelectOption {
  value: string | number;
  label: string;
}

type ViewType = 'table' | 'chart';
type SectionColor = 'red' | 'orange' | 'blue' | 'green' | 'cyan' | 'purple';

// ============================================================================
// CONSTANTS
// ============================================================================

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'];

const TIME_RANGE_OPTIONS: SelectOption[] = [
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

const formatEmployment = (val: number | undefined | null): string =>
  val != null ? `${val.toLocaleString(undefined, { maximumFractionDigits: 1 })}K` : 'N/A';

const formatChange = (val: number | undefined | null): string => {
  if (val == null) return 'N/A';
  const sign = val >= 0 ? '+' : '';
  return `${sign}${val.toFixed(1)}K`;
};

const formatPct = (val: number | undefined | null): string => {
  if (val == null) return 'N/A';
  const sign = val >= 0 ? '+' : '';
  return `${sign}${val.toFixed(2)}%`;
};

const formatPeriod = (period: string): string => {
  const monthMap: Record<string, string> = {
    'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
    'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
    'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
  };
  return monthMap[period] || period;
};

// Get coordinates for SM state code (2-digit FIPS)
const getSMStateCoordinates = (stateCode: string): { lat: number; lng: number } | null => {
  // Convert SM state code (e.g., "01") to LA format (e.g., "ST0100000000000")
  const laStateCode = `ST${stateCode}00000000000`;
  const coords = stateCoordinates[laStateCode];
  if (coords) {
    return { lat: coords.lat, lng: coords.lng };
  }
  return null;
};

// Get coordinates for SM metro area by parsing area name
const getSMMetroCoordinates = (areaCode: string, areaName: string): { lat: number; lng: number } | null => {
  // Use LA's city matching logic - construct a fake MT code to trigger metro matching
  const coords = getLAAreaCoordinates(`MT${areaCode}`, areaName);
  if (coords) {
    return { lat: coords.lat, lng: coords.lng };
  }
  return null;
};

// Color scale for employment (thousands) - different from unemployment rate
const getEmploymentColor = (employment: number | null | undefined): string => {
  if (employment == null) return '#9ca3af'; // gray
  if (employment >= 5000) return '#1e40af'; // dark blue - very large
  if (employment >= 2000) return '#3b82f6'; // blue - large
  if (employment >= 1000) return '#06b6d4'; // cyan - medium-large
  if (employment >= 500) return '#10b981'; // green - medium
  if (employment >= 100) return '#84cc16'; // lime - small-medium
  return '#fbbf24'; // amber - small
};

// Color scale for Y/Y percent change
const getChangeColor = (changePct: number | null | undefined): string => {
  if (changePct == null) return '#9ca3af'; // gray
  if (changePct >= 3) return '#16a34a'; // strong growth
  if (changePct >= 1) return '#4ade80'; // moderate growth
  if (changePct >= 0) return '#86efac'; // slight growth
  if (changePct >= -1) return '#fbbf24'; // slight decline
  if (changePct >= -3) return '#fb923c'; // moderate decline
  return '#dc2626'; // strong decline
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

interface CardProps {
  children: ReactNode;
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
}

const SectionHeader = ({ title, color = 'blue' }: SectionHeaderProps): ReactElement => {
  const colorClasses: Record<SectionColor, string> = {
    red: 'border-red-500 bg-red-50 text-red-700',
    orange: 'border-orange-500 bg-orange-50 text-orange-700',
    blue: 'border-blue-500 bg-blue-50 text-blue-700',
    green: 'border-green-500 bg-green-50 text-green-700',
    cyan: 'border-cyan-500 bg-cyan-50 text-cyan-700',
    purple: 'border-purple-500 bg-purple-50 text-purple-700',
  };
  return (
    <div className={`px-5 py-3 border-b-4 ${colorClasses[color]}`}>
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
      onChange={(e: ChangeEvent<HTMLSelectElement>) => onChange(e.target.value)}
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
  selectedPeriod: PeriodSelection | null;
  onSelectPeriod: (period: PeriodSelection) => void;
}

const TimelineSelector = ({ timeline, selectedPeriod, onSelectPeriod }: TimelineSelectorProps): ReactElement => (
  <div className="mt-4 px-2">
    <p className="text-xs text-gray-500 mb-2">Select Month (click any point):</p>
    <div className="relative h-12">
      <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-300" />
      <div className="flex justify-between">
        {timeline.map((point, index) => {
          const isSelected = selectedPeriod?.year === point.year && selectedPeriod?.period === point.period;
          const isLatest = index === timeline.length - 1;
          const showLabel = index % Math.max(1, Math.floor(timeline.length / 8)) === 0 || index === timeline.length - 1 || isSelected;
          return (
            <div
              key={`${point.year}-${point.period}`}
              className="flex flex-col items-center cursor-pointer flex-1"
              onClick={() => onSelectPeriod({ year: point.year, period: point.period })}
            >
              <div
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  isSelected ? 'w-3.5 h-3.5 bg-blue-600 shadow-md' :
                  isLatest && !selectedPeriod ? 'bg-blue-400' : 'bg-gray-400'
                } hover:scale-125 hover:bg-blue-400`}
              />
              {showLabel && (
                <span className={`text-[10px] mt-1 whitespace-nowrap ${isSelected ? 'text-blue-600 font-semibold' : 'text-gray-500'}`}>
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

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function SMExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);

  // State selection and overview
  const [selectedStateCode, setSelectedStateCode] = useState('36'); // Default: New York
  const [selectedAreaCode, setSelectedAreaCode] = useState('00000'); // Default: Statewide
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeRange, setOverviewTimeRange] = useState(24);
  const [overviewTimeline, setOverviewTimeline] = useState<TimelineData | null>(null);
  const [selectedOverviewPeriod, setSelectedOverviewPeriod] = useState<PeriodSelection | null>(null);
  const [overviewView, setOverviewView] = useState<ViewType>('chart');

  // State comparison
  const [states, setStates] = useState<StatesData | null>(null);
  const [stateTimeline, setStateTimeline] = useState<TimelineData | null>(null);
  const [loadingStates, setLoadingStates] = useState(true);
  const [stateTimeRange, setStateTimeRange] = useState(24);
  const [selectedStatePeriod, setSelectedStatePeriod] = useState<PeriodSelection | null>(null);
  const [stateView, setStateView] = useState<ViewType>('table');
  const [selectedStatesForTimeline, setSelectedStatesForTimeline] = useState<string[]>([]);

  // Metro analysis
  const [metros, setMetros] = useState<MetrosData | null>(null);
  const [metroTimeline, setMetroTimeline] = useState<TimelineData | null>(null);
  const [loadingMetros, setLoadingMetros] = useState(true);
  const [metroTimeRange, setMetroTimeRange] = useState(24);
  const [selectedMetroPeriod, setSelectedMetroPeriod] = useState<PeriodSelection | null>(null);
  const [metroView, setMetroView] = useState<ViewType>('table');
  const [selectedMetrosForTimeline, setSelectedMetrosForTimeline] = useState<string[]>([]);
  const [metroPage, setMetroPage] = useState(0);
  const [metroStateFilter, setMetroStateFilter] = useState('');

  // Geographic view
  const [geoTimeRange, setGeoTimeRange] = useState(24);
  const [selectedGeoPeriod, setSelectedGeoPeriod] = useState<PeriodSelection | null>(null);
  const [geoColorMode, setGeoColorMode] = useState<'employment' | 'change'>('employment');

  // Supersector analysis
  const [supersectors, setSupersectors] = useState<SupersectorMetric[] | null>(null);
  const [loadingSupersectors, setLoadingSupersectors] = useState(false);
  const [supersectorTimeRange, setSupersectorTimeRange] = useState(24);
  const [supersectorTimeline, setSupersectorTimeline] = useState<TimelineData | null>(null);
  const [selectedSupersectorsForTimeline, setSelectedSupersectorsForTimeline] = useState<string[]>(['00', '05', '10']);
  const [supersectorView, setSupersectorView] = useState<ViewType>('chart');
  const [selectedSupersectorPeriod, setSelectedSupersectorPeriod] = useState<PeriodSelection | null>(null);

  // Series explorer
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseLimit] = useState(50);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);
  const [drillStateCode, setDrillStateCode] = useState('');
  const [drillAreaCode, setDrillAreaCode] = useState('');
  const [drillSupersector, setDrillSupersector] = useState('');
  const [drillDataType, setDrillDataType] = useState('01');
  const [drilldownResults, setDrilldownResults] = useState<SeriesListData | null>(null);
  const [loadingDrilldown, setLoadingDrilldown] = useState(false);
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<SeriesChartDataMap>({});
  const [seriesTimeRange, setSeriesTimeRange] = useState(60);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');

  // Load dimensions
  useEffect(() => {
    smResearchAPI.getDimensions()
      .then(res => setDimensions(res.data as DimensionsData))
      .catch(console.error);
  }, []);

  // Load overview for selected state/area
  useEffect(() => {
    const load = async (): Promise<void> => {
      setLoadingOverview(true);
      try {
        const monthsBack = overviewTimeRange === 0 ? 9999 : overviewTimeRange;
        const [overviewRes, timelineRes] = await Promise.all([
          smResearchAPI.getOverview(selectedStateCode, selectedAreaCode),
          smResearchAPI.getOverviewTimeline(selectedStateCode, selectedAreaCode, monthsBack)
        ]);
        setOverview(overviewRes.data as OverviewData);
        setOverviewTimeline(timelineRes.data as TimelineData);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    if (selectedStateCode) load();
  }, [selectedStateCode, selectedAreaCode, overviewTimeRange]);

  // Load all states
  useEffect(() => {
    const load = async (): Promise<void> => {
      setLoadingStates(true);
      try {
        const monthsBack = stateTimeRange === 0 ? 9999 : stateTimeRange;
        const [statesRes, timelineRes] = await Promise.all([
          smResearchAPI.getStates(),
          smResearchAPI.getStatesTimeline(monthsBack)
        ]);
        setStates(statesRes.data as StatesData);
        setStateTimeline(timelineRes.data as TimelineData);
      } catch (error) {
        console.error('Failed to load states:', error);
      } finally {
        setLoadingStates(false);
      }
    };
    load();
  }, [stateTimeRange]);

  // Load metros
  useEffect(() => {
    const load = async (): Promise<void> => {
      setLoadingMetros(true);
      try {
        const monthsBack = metroTimeRange === 0 ? 9999 : metroTimeRange;
        const [metrosRes, timelineRes] = await Promise.all([
          smResearchAPI.getMetros(metroStateFilter || null, 500),
          smResearchAPI.getMetrosTimeline(monthsBack, null, 50)
        ]);
        setMetros(metrosRes.data as MetrosData);
        setMetroTimeline(timelineRes.data as TimelineData);
      } catch (error) {
        console.error('Failed to load metros:', error);
      } finally {
        setLoadingMetros(false);
      }
    };
    load();
  }, [metroTimeRange, metroStateFilter]);

  // Load supersectors for selected state/area
  useEffect(() => {
    const load = async (): Promise<void> => {
      if (!selectedStateCode) return;
      setLoadingSupersectors(true);
      try {
        const res = await smResearchAPI.getSupersectors(selectedStateCode, selectedAreaCode);
        const data = res.data as { supersectors: SupersectorMetric[] };
        setSupersectors(data.supersectors);
      } catch (error) {
        console.error('Failed to load supersectors:', error);
      } finally {
        setLoadingSupersectors(false);
      }
    };
    load();
  }, [selectedStateCode, selectedAreaCode]);

  // Load supersector timeline
  useEffect(() => {
    const load = async (): Promise<void> => {
      if (!selectedStateCode || selectedSupersectorsForTimeline.length === 0) return;
      try {
        const monthsBack = supersectorTimeRange === 0 ? 9999 : supersectorTimeRange;
        const res = await smResearchAPI.getSupersectorsTimeline(
          selectedStateCode,
          selectedAreaCode,
          selectedSupersectorsForTimeline.join(','),
          monthsBack
        );
        setSupersectorTimeline(res.data as TimelineData);
      } catch (error) {
        console.error('Failed to load supersector timeline:', error);
      }
    };
    load();
  }, [selectedStateCode, selectedAreaCode, selectedSupersectorsForTimeline, supersectorTimeRange]);

  // Search handler
  const handleSearch = async (): Promise<void> => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await smResearchAPI.getSeries({
        search: searchQuery,
        data_type_code: '01',
        active_only: true,
        limit: 50
      });
      setSearchResults(res.data as SeriesListData);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  // Browse series - always load for the Browse All section
  useEffect(() => {
    const load = async (): Promise<void> => {
      setLoadingBrowse(true);
      try {
        const res = await smResearchAPI.getSeries({
          data_type_code: '01',
          active_only: true,
          limit: browseLimit,
          offset: browseOffset
        });
        setBrowseResults(res.data as SeriesListData);
      } catch (error) {
        console.error('Failed to browse series:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    load();
  }, [browseOffset, browseLimit]);

  // Drill-down series - triggers when filter selections change
  useEffect(() => {
    if (!drillStateCode) {
      setDrilldownResults(null);
      return;
    }
    const load = async (): Promise<void> => {
      setLoadingDrilldown(true);
      try {
        const params: Record<string, unknown> = {
          state_code: drillStateCode,
          data_type_code: drillDataType,
          active_only: true,
          limit: 100
        };
        if (drillAreaCode) params.area_code = drillAreaCode;
        if (drillSupersector) params.supersector_code = drillSupersector;
        const res = await smResearchAPI.getSeries(params);
        setDrilldownResults(res.data as SeriesListData);
      } catch (error) {
        console.error('Failed to drill down:', error);
      } finally {
        setLoadingDrilldown(false);
      }
    };
    load();
  }, [drillStateCode, drillAreaCode, drillSupersector, drillDataType]);

  // Load series data for selected series
  useEffect(() => {
    const load = async (): Promise<void> => {
      const currentYear = new Date().getFullYear();
      const yearsBack = seriesTimeRange === 0 ? 100 : Math.ceil(seriesTimeRange / 12);
      const startYear = currentYear - yearsBack;
      for (const seriesId of selectedSeriesIds) {
        if (seriesChartData[seriesId]) continue;
        try {
          const res = await smResearchAPI.getSeriesData(seriesId, { start_year: startYear });
          setSeriesChartData(prev => ({ ...prev, [seriesId]: res.data as SeriesDataResponse }));
        } catch (error) {
          console.error(`Failed to load ${seriesId}:`, error);
        }
      }
    };
    if (selectedSeriesIds.length > 0) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSeriesIds, seriesTimeRange]);

  const toggleSeriesSelection = (seriesId: string): void => {
    if (selectedSeriesIds.includes(seriesId)) {
      setSelectedSeriesIds(selectedSeriesIds.filter(id => id !== seriesId));
    } else if (selectedSeriesIds.length < 5) {
      setSelectedSeriesIds([...selectedSeriesIds, seriesId]);
    }
  };

  const stateOptions: SelectOption[] = [
    { value: '', label: 'Select a state...' },
    ...(dimensions?.states?.map(s => ({ value: s.state_code, label: s.state_name })) || [])
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">SM - State & Metro Area Employment Explorer</h1>
        <p className="text-sm text-gray-600 mt-1">Explore employment statistics by state, metropolitan area, and industry sector</p>
      </div>

      {/* Section 1: State Overview */}
      <Card>
        <SectionHeader title="State & Area Overview" color="blue" />
        <div className="p-5">
          <div className="flex flex-wrap gap-4 items-end mb-4">
            <Select
              label="State"
              value={selectedStateCode}
              onChange={(v) => { setSelectedStateCode(v); setSelectedAreaCode('00000'); }}
              options={stateOptions}
              className="min-w-[200px]"
            />
            <Select
              label="Area"
              value={selectedAreaCode}
              onChange={setSelectedAreaCode}
              options={[
                { value: '00000', label: 'Statewide' },
                ...(dimensions?.areas?.filter(a => a.area_code !== '00000' && a.area_code !== '99999').slice(0, 100).map(a => ({ value: a.area_code, label: a.area_name })) || [])
              ]}
              className="min-w-[250px]"
            />
            <Select
              label="Time Range"
              value={overviewTimeRange}
              onChange={(v) => setOverviewTimeRange(Number(v))}
              options={TIME_RANGE_OPTIONS}
            />
            <ViewToggle value={overviewView} onChange={setOverviewView} />
          </div>

          {loadingOverview ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>
          ) : overview ? (
            <>
              <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="text-lg font-semibold text-blue-800">{overview.state_name} - {overview.area_name}</h3>
                <p className="text-sm text-blue-600">Last updated: {overview.last_updated}</p>
              </div>

              {overviewView === 'table' ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-2 px-3 font-semibold">Supersector</th>
                        <th className="text-right py-2 px-3 font-semibold">Employment (K)</th>
                        <th className="text-right py-2 px-3 font-semibold">M/M Change</th>
                        <th className="text-right py-2 px-3 font-semibold">M/M %</th>
                        <th className="text-right py-2 px-3 font-semibold">Y/Y Change</th>
                        <th className="text-right py-2 px-3 font-semibold">Y/Y %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {overview.supersectors.map(ss => (
                        <tr key={ss.supersector_code} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3 font-medium">{ss.supersector_name}</td>
                          <td className="py-2 px-3 text-right font-mono">{formatEmployment(ss.employment)}</td>
                          <td className="py-2 px-3 text-right">
                            <span className={ss.mom_change && ss.mom_change >= 0 ? 'text-green-600' : 'text-red-600'}>
                              {formatChange(ss.mom_change)}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-right">
                            <span className={ss.mom_pct && ss.mom_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                              {formatPct(ss.mom_pct)}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-right">
                            <span className={ss.yoy_change && ss.yoy_change >= 0 ? 'text-green-600' : 'text-red-600'}>
                              {formatChange(ss.yoy_change)}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-right">
                            <span className={ss.yoy_pct && ss.yoy_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                              {formatPct(ss.yoy_pct)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : overviewTimeline?.timeline && overviewTimeline.timeline.length > 0 && (
                <>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={overviewTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="period_name"
                          tick={{ fontSize: 10 }}
                          angle={-45}
                          textAnchor="end"
                          height={60}
                          interval={Math.max(0, Math.floor(overviewTimeline.timeline.length / 12) - 1)}
                        />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {Object.entries(overviewTimeline.supersector_names || {}).slice(0, 8).map(([code, name], idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={(point: TimelinePoint) => point.supersectors?.[code]}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            strokeWidth={code === '00' ? 3 : 1.5}
                            dot={false}
                            name={name.substring(0, 25)}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <TimelineSelector
                    timeline={overviewTimeline.timeline}
                    selectedPeriod={selectedOverviewPeriod}
                    onSelectPeriod={setSelectedOverviewPeriod}
                  />
                </>
              )}
            </>
          ) : null}
        </div>
      </Card>

      {/* Section 2: Geographic View */}
      <Card>
        <SectionHeader title="Geographic View" color="orange" />
        <div className="p-5">
          <div className="flex justify-between items-center mb-4">
            <p className="text-xs text-gray-500">
              View employment across states and metros. {selectedGeoPeriod ? `Showing: ${formatPeriod(selectedGeoPeriod.period)} ${selectedGeoPeriod.year}` : 'Showing latest data.'}
            </p>
            <div className="flex gap-3 items-center">
              <div className="flex border border-gray-300 rounded-md overflow-hidden">
                <button
                  onClick={() => setGeoColorMode('employment')}
                  className={`px-3 py-1 text-sm ${geoColorMode === 'employment' ? 'bg-blue-500 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                >
                  Employment
                </button>
                <button
                  onClick={() => setGeoColorMode('change')}
                  className={`px-3 py-1 text-sm ${geoColorMode === 'change' ? 'bg-blue-500 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
                >
                  Y/Y Change
                </button>
              </div>
              <Select
                value={geoTimeRange}
                onChange={(v) => { setGeoTimeRange(Number(v)); setSelectedGeoPeriod(null); }}
                options={TIME_RANGE_OPTIONS}
              />
              {selectedGeoPeriod && (
                <button onClick={() => setSelectedGeoPeriod(null)} className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50">
                  Show Latest
                </button>
              )}
            </div>
          </div>

          {/* Color Legend */}
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            {geoColorMode === 'employment' ? (
              <>
                <span className="text-xs font-semibold">Employment (K):</span>
                {[
                  { label: '< 100', color: '#fbbf24' },
                  { label: '100-500', color: '#84cc16' },
                  { label: '500-1000', color: '#10b981' },
                  { label: '1000-2000', color: '#06b6d4' },
                  { label: '2000-5000', color: '#3b82f6' },
                  { label: '> 5000', color: '#1e40af' },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-1">
                    <div className="w-4 h-4 rounded-full border border-gray-300" style={{ backgroundColor: item.color }} />
                    <span className="text-xs">{item.label}</span>
                  </div>
                ))}
              </>
            ) : (
              <>
                <span className="text-xs font-semibold">Y/Y Change:</span>
                {[
                  { label: '< -3%', color: '#dc2626' },
                  { label: '-3 to -1%', color: '#fb923c' },
                  { label: '-1 to 0%', color: '#fbbf24' },
                  { label: '0 to 1%', color: '#86efac' },
                  { label: '1 to 3%', color: '#4ade80' },
                  { label: '> 3%', color: '#16a34a' },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-1">
                    <div className="w-4 h-4 rounded-full border border-gray-300" style={{ backgroundColor: item.color }} />
                    <span className="text-xs">{item.label}</span>
                  </div>
                ))}
              </>
            )}
          </div>

          {loadingStates || loadingMetros ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-orange-500" /></div>
          ) : (
            <>
              <div className="h-[700px] border border-gray-200 rounded-lg overflow-hidden">
                <MapContainer
                  center={[39.8283, -98.5795]}
                  zoom={4}
                  minZoom={3}
                  maxZoom={10}
                  maxBounds={US_BOUNDS as LatLngBoundsExpression}
                  style={{ height: '100%', width: '100%', background: '#f5f5f5' }}
                  scrollWheelZoom={true}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
                  />
                  <TileLayer url="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png" />

                  {/* State markers - square icons */}
                  {states?.states?.map(state => {
                    const coords = getSMStateCoordinates(state.state_code);
                    if (!coords) return null;

                    let employment = state.employment;
                    let yoyPct = state.year_over_year_pct;

                    // If a specific period is selected and we have timeline data, get that period's value
                    if (selectedGeoPeriod && stateTimeline?.timeline) {
                      const point = stateTimeline.timeline.find(
                        p => p.year === selectedGeoPeriod.year && p.period === selectedGeoPeriod.period
                      );
                      if (point?.states?.[state.state_code] !== undefined) {
                        employment = point.states[state.state_code];
                        // Y/Y change not available in timeline, use latest
                      }
                    }

                    const color = geoColorMode === 'employment'
                      ? getEmploymentColor(employment)
                      : getChangeColor(yoyPct);

                    const icon = L.divIcon({
                      className: '',
                      html: `<div style="width:14px;height:14px;background:${color};border:2px solid #1976d2;cursor:pointer;"></div>`,
                      iconSize: [14, 14],
                      iconAnchor: [7, 7],
                    });

                    return (
                      <Marker
                        key={`state-${state.state_code}`}
                        position={[coords.lat, coords.lng]}
                        icon={icon}
                        eventHandlers={{
                          click: () => {
                            if (!selectedStatesForTimeline.includes(state.state_code) && selectedStatesForTimeline.length < 10) {
                              setSelectedStatesForTimeline([...selectedStatesForTimeline, state.state_code]);
                            }
                          },
                        }}
                      >
                        <Popup>
                          <div className="p-1">
                            <p className="font-semibold">{state.state_name}</p>
                            <p className="text-sm">Employment: {formatEmployment(employment)}</p>
                            <p className="text-sm">M/M: {formatPct(state.month_over_month_pct)}</p>
                            <p className="text-sm">Y/Y: {formatPct(state.year_over_year_pct)}</p>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  })}

                  {/* Metro markers - circle markers */}
                  {metros?.metros?.map(metro => {
                    const coords = getSMMetroCoordinates(metro.area_code, metro.area_name);
                    if (!coords) return null;

                    let employment = metro.employment;
                    let yoyPct = metro.year_over_year_pct;

                    if (selectedGeoPeriod && metroTimeline?.timeline) {
                      const point = metroTimeline.timeline.find(
                        p => p.year === selectedGeoPeriod.year && p.period === selectedGeoPeriod.period
                      );
                      if (point?.metros?.[metro.area_code] !== undefined) {
                        employment = point.metros[metro.area_code];
                      }
                    }

                    const color = geoColorMode === 'employment'
                      ? getEmploymentColor(employment)
                      : getChangeColor(yoyPct);

                    return (
                      <CircleMarker
                        key={`metro-${metro.area_code}`}
                        center={[coords.lat, coords.lng]}
                        radius={6}
                        fillColor={color}
                        color="#7b1fa2"
                        weight={1}
                        fillOpacity={0.85}
                        eventHandlers={{
                          click: () => {
                            if (!selectedMetrosForTimeline.includes(metro.area_code) && selectedMetrosForTimeline.length < 10) {
                              setSelectedMetrosForTimeline([...selectedMetrosForTimeline, metro.area_code]);
                            }
                          },
                        }}
                      >
                        <Popup>
                          <div className="p-1">
                            <p className="font-semibold text-sm">{metro.area_name}</p>
                            <p className="text-sm">State: {metro.state_name}</p>
                            <p className="text-sm">Employment: {formatEmployment(employment)}</p>
                            <p className="text-sm">Y/Y: {formatPct(metro.year_over_year_pct)}</p>
                          </div>
                        </Popup>
                      </CircleMarker>
                    );
                  })}
                </MapContainer>
              </div>

              {stateTimeline?.timeline && stateTimeline.timeline.length > 0 && (
                <TimelineSelector
                  timeline={stateTimeline.timeline}
                  selectedPeriod={selectedGeoPeriod}
                  onSelectPeriod={setSelectedGeoPeriod}
                />
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 3: State Comparison */}
      <Card>
        <SectionHeader title="State Employment Comparison" color="blue" />
        <div className="p-5">
          <div className="flex justify-end items-center gap-3 mb-4">
            <Select
              value={stateTimeRange}
              onChange={(v) => { setStateTimeRange(Number(v)); setSelectedStatePeriod(null); }}
              options={TIME_RANGE_OPTIONS}
            />
            <ViewToggle value={stateView} onChange={setStateView} />
          </div>

          {loadingStates ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-orange-500" /></div>
          ) : states ? (
            <>
              {/* Rankings */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <Card>
                  <div className="p-4">
                    <p className="text-sm font-semibold text-blue-600 mb-2">Highest Employment</p>
                    {states.rankings.highest_employment?.map((name, idx) => (
                      <p key={idx} className="text-sm text-gray-600">{idx + 1}. {name}</p>
                    ))}
                  </div>
                </Card>
                <Card>
                  <div className="p-4">
                    <p className="text-sm font-semibold text-green-600 mb-2">Highest Growth (Y/Y)</p>
                    {states.rankings.highest_growth?.map((name, idx) => (
                      <p key={idx} className="text-sm text-gray-600">{idx + 1}. {name}</p>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Timeline chart */}
              {stateTimeline?.timeline && stateTimeline.timeline.length > 0 && selectedStatesForTimeline.length > 0 && (
                <Card className="mb-4">
                  <div className="p-4">
                    <p className="text-sm font-semibold mb-1">State Employment Trends</p>
                    <p className="text-xs text-gray-500 mb-3">Click states in the table to add them to the chart (max 10)</p>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={stateTimeline.timeline}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} interval={Math.floor(stateTimeline.timeline.length / 12)} />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '11px' }} />
                          {selectedStatesForTimeline.slice(0, 10).map((stateCode, idx) => (
                            <Line
                              key={stateCode}
                              type="monotone"
                              dataKey={(point: TimelinePoint) => point.states?.[stateCode]}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={false}
                              name={stateTimeline?.state_names?.[stateCode] || stateCode}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <TimelineSelector
                      timeline={stateTimeline.timeline}
                      selectedPeriod={selectedStatePeriod}
                      onSelectPeriod={setSelectedStatePeriod}
                    />
                  </div>
                </Card>
              )}

              {/* State data table/chart */}
              <Card>
                <div className="px-4 py-2 border-b border-gray-200">
                  <p className="text-sm font-semibold">State Employment Data ({states.states.length} states)</p>
                  {selectedStatePeriod && (
                    <p className="text-xs text-blue-600">Showing: {formatPeriod(selectedStatePeriod.period)} {selectedStatePeriod.year}</p>
                  )}
                </div>
                {stateView === 'table' ? (
                  <div className="overflow-x-auto max-h-[500px]">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-2 px-3 font-semibold">State</th>
                          <th className="text-right py-2 px-3 font-semibold">Employment (K)</th>
                          {!selectedStatePeriod && <th className="text-right py-2 px-3 font-semibold">M/M</th>}
                          {!selectedStatePeriod && <th className="text-right py-2 px-3 font-semibold">Y/Y</th>}
                        </tr>
                      </thead>
                      <tbody>
                        {states.states.map(state => (
                          <tr
                            key={state.state_code}
                            className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${selectedStatesForTimeline.includes(state.state_code) ? 'bg-orange-50' : ''}`}
                            onClick={() => {
                              if (selectedStatesForTimeline.includes(state.state_code)) {
                                setSelectedStatesForTimeline(selectedStatesForTimeline.filter(c => c !== state.state_code));
                              } else if (selectedStatesForTimeline.length < 10) {
                                setSelectedStatesForTimeline([...selectedStatesForTimeline, state.state_code]);
                              }
                            }}
                          >
                            <td className="py-2 px-3">{state.state_name}</td>
                            <td className="py-2 px-3 text-right font-mono">{formatEmployment(state.employment)}</td>
                            {!selectedStatePeriod && (
                              <td className="py-2 px-3 text-right">
                                <span className="flex items-center justify-end gap-1">
                                  {state.month_over_month != null && (state.month_over_month >= 0 ? <TrendingUp className="w-4 h-4 text-green-500" /> : <TrendingDown className="w-4 h-4 text-red-500" />)}
                                  {formatPct(state.month_over_month_pct)}
                                </span>
                              </td>
                            )}
                            {!selectedStatePeriod && (
                              <td className="py-2 px-3 text-right">
                                <span className="flex items-center justify-end gap-1">
                                  {state.year_over_year != null && (state.year_over_year >= 0 ? <TrendingUp className="w-4 h-4 text-green-500" /> : <TrendingDown className="w-4 h-4 text-red-500" />)}
                                  {formatPct(state.year_over_year_pct)}
                                </span>
                              </td>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-4 h-[500px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={states.states.slice(0, 20)} layout="vertical" margin={{ left: 120 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" tick={{ fontSize: 11 }} />
                        <YAxis type="category" dataKey="state_name" tick={{ fontSize: 10 }} width={110} />
                        <Tooltip formatter={(v) => [`${Number(v)?.toLocaleString()}K`, 'Employment']} />
                        <Bar dataKey="employment" fill="#f59e0b" name="Employment (thousands)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </Card>
            </>
          ) : null}
        </div>
      </Card>

      {/* Section 4: Metropolitan Areas */}
      <Card>
        <SectionHeader title="Metropolitan Areas" color="green" />
        <div className="p-5">
          <div className="flex flex-wrap justify-between items-center gap-3 mb-4">
            <Select
              label="Filter by State"
              value={metroStateFilter}
              onChange={(v) => { setMetroStateFilter(v); setMetroPage(0); }}
              options={[{ value: '', label: 'All States' }, ...stateOptions.slice(1)]}
              className="min-w-[200px]"
            />
            <div className="flex gap-3 items-center">
              <Select
                value={metroTimeRange}
                onChange={(v) => { setMetroTimeRange(Number(v)); setSelectedMetroPeriod(null); }}
                options={TIME_RANGE_OPTIONS}
              />
              <ViewToggle value={metroView} onChange={setMetroView} />
            </div>
          </div>

          {loadingMetros ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-green-500" /></div>
          ) : metros ? (
            <>
              {/* Metro timeline chart */}
              {metroTimeline?.timeline && metroTimeline.timeline.length > 0 && selectedMetrosForTimeline.length > 0 && (
                <Card className="mb-4">
                  <div className="p-4">
                    <p className="text-sm font-semibold mb-1">Metro Employment Trends</p>
                    <p className="text-xs text-gray-500 mb-3">Click metros in the table to add them to the chart</p>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={metroTimeline.timeline}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} interval={Math.floor(metroTimeline.timeline.length / 12)} />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '10px' }} />
                          {selectedMetrosForTimeline.slice(0, 10).map((areaCode, idx) => (
                            <Line
                              key={areaCode}
                              type="monotone"
                              dataKey={(point: TimelinePoint) => point.metros?.[areaCode]}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={false}
                              name={metroTimeline?.metro_names?.[areaCode]?.substring(0, 30) || areaCode}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <TimelineSelector
                      timeline={metroTimeline.timeline}
                      selectedPeriod={selectedMetroPeriod}
                      onSelectPeriod={setSelectedMetroPeriod}
                    />
                  </div>
                </Card>
              )}

              {/* Metro data table/chart */}
              <Card>
                <div className="px-4 py-2 border-b border-gray-200">
                  <p className="text-sm font-semibold">Metro Area Data ({metros.total_count} metros)</p>
                </div>
                {metroView === 'table' ? (
                  <>
                    <div className="overflow-x-auto max-h-[500px]">
                      <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-gray-50">
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-2 px-3 font-semibold">Metro Area</th>
                            <th className="text-left py-2 px-3 font-semibold">State</th>
                            <th className="text-right py-2 px-3 font-semibold">Employment (K)</th>
                            <th className="text-right py-2 px-3 font-semibold">M/M</th>
                            <th className="text-right py-2 px-3 font-semibold">Y/Y</th>
                          </tr>
                        </thead>
                        <tbody>
                          {metros.metros.slice(metroPage * 25, metroPage * 25 + 25).map(metro => (
                            <tr
                              key={metro.area_code}
                              className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${selectedMetrosForTimeline.includes(metro.area_code) ? 'bg-green-50' : ''}`}
                              onClick={() => {
                                if (selectedMetrosForTimeline.includes(metro.area_code)) {
                                  setSelectedMetrosForTimeline(selectedMetrosForTimeline.filter(c => c !== metro.area_code));
                                } else if (selectedMetrosForTimeline.length < 10) {
                                  setSelectedMetrosForTimeline([...selectedMetrosForTimeline, metro.area_code]);
                                }
                              }}
                            >
                              <td className="py-2 px-3 text-sm">{metro.area_name}</td>
                              <td className="py-2 px-3 text-sm">{metro.state_name}</td>
                              <td className="py-2 px-3 text-right font-mono">{formatEmployment(metro.employment)}</td>
                              <td className="py-2 px-3 text-right">
                                <span className={metro.month_over_month_pct && metro.month_over_month_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                                  {formatPct(metro.month_over_month_pct)}
                                </span>
                              </td>
                              <td className="py-2 px-3 text-right">
                                <span className={metro.year_over_year_pct && metro.year_over_year_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                                  {formatPct(metro.year_over_year_pct)}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200">
                      <span className="text-sm text-gray-500">Page {metroPage + 1} of {Math.ceil(metros.metros.length / 25)}</span>
                      <div className="flex gap-2">
                        <button disabled={metroPage === 0} onClick={() => setMetroPage(metroPage - 1)} className="px-3 py-1 text-sm border rounded disabled:opacity-50">Prev</button>
                        <button disabled={metroPage >= Math.ceil(metros.metros.length / 25) - 1} onClick={() => setMetroPage(metroPage + 1)} className="px-3 py-1 text-sm border rounded disabled:opacity-50">Next</button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="p-4 h-[500px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={metros.metros.slice(0, 20).map(m => ({ ...m, short_name: m.area_name.substring(0, 35) }))} layout="vertical" margin={{ left: 200 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" tick={{ fontSize: 11 }} />
                        <YAxis type="category" dataKey="short_name" tick={{ fontSize: 9 }} width={190} />
                        <Tooltip formatter={(v) => [`${Number(v)?.toLocaleString()}K`, 'Employment']} />
                        <Bar dataKey="employment" fill="#10b981" name="Employment (thousands)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </Card>
            </>
          ) : null}
        </div>
      </Card>

      {/* Section 5: Supersector Analysis */}
      <Card>
        <SectionHeader title="Supersector Analysis" color="purple" />
        <div className="p-5">
          <div className="flex flex-wrap gap-4 items-end mb-4">
            <Select
              label="State"
              value={selectedStateCode}
              onChange={(v) => { setSelectedStateCode(v); setSelectedAreaCode('00000'); }}
              options={stateOptions}
              className="min-w-[200px]"
            />
            <Select
              label="Time Range"
              value={supersectorTimeRange}
              onChange={(v) => setSupersectorTimeRange(Number(v))}
              options={TIME_RANGE_OPTIONS}
            />
            <ViewToggle value={supersectorView} onChange={setSupersectorView} />
          </div>

          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">Select supersectors to compare (click to toggle):</p>
            <div className="flex flex-wrap gap-2">
              {supersectors?.map((ss, idx) => (
                <button
                  key={ss.supersector_code}
                  onClick={() => {
                    if (selectedSupersectorsForTimeline.includes(ss.supersector_code)) {
                      setSelectedSupersectorsForTimeline(selectedSupersectorsForTimeline.filter(c => c !== ss.supersector_code));
                    } else if (selectedSupersectorsForTimeline.length < 8) {
                      setSelectedSupersectorsForTimeline([...selectedSupersectorsForTimeline, ss.supersector_code]);
                    }
                  }}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedSupersectorsForTimeline.includes(ss.supersector_code)
                      ? 'text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  style={selectedSupersectorsForTimeline.includes(ss.supersector_code) ? { backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] } : {}}
                >
                  {ss.supersector_name.substring(0, 20)}
                </button>
              ))}
            </div>
          </div>

          {loadingSupersectors ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-purple-500" /></div>
          ) : supersectorView === 'chart' && supersectorTimeline?.timeline && supersectorTimeline.timeline.length > 0 ? (
            <>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={supersectorTimeline.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="period_name"
                      tick={{ fontSize: 10 }}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                      interval={Math.max(0, Math.floor(supersectorTimeline.timeline.length / 12) - 1)}
                    />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                    {selectedSupersectorsForTimeline.map((code, idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={(point: TimelinePoint) => point.supersectors?.[code]}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        strokeWidth={2}
                        dot={false}
                        name={supersectorTimeline.supersector_names?.[code]?.substring(0, 25) || code}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <TimelineSelector
                timeline={supersectorTimeline.timeline}
                selectedPeriod={selectedSupersectorPeriod}
                onSelectPeriod={setSelectedSupersectorPeriod}
              />
            </>
          ) : supersectorView === 'table' && supersectors ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-3 font-semibold">Supersector</th>
                    <th className="text-right py-2 px-3 font-semibold">Employment (K)</th>
                    <th className="text-right py-2 px-3 font-semibold">M/M</th>
                    <th className="text-right py-2 px-3 font-semibold">Y/Y</th>
                  </tr>
                </thead>
                <tbody>
                  {supersectors.map(ss => (
                    <tr key={ss.supersector_code} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-2 px-3">{ss.supersector_name}</td>
                      <td className="py-2 px-3 text-right font-mono">{formatEmployment(ss.employment)}</td>
                      <td className="py-2 px-3 text-right">
                        <span className={ss.mom_pct && ss.mom_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {formatPct(ss.mom_pct)}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right">
                        <span className={ss.yoy_pct && ss.yoy_pct >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {formatPct(ss.yoy_pct)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      </Card>

      {/* Section 6: Series Detail Explorer */}
      <Card>
        <SectionHeader title="Series Detail Explorer" color="cyan" />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-6">
            Access all SM series through search, hierarchical navigation, or paginated browsing.
            Select series to compare in charts (max 5).
          </p>

          {/* Sub-section 5A: Search-based Access */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-cyan-50 to-blue-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-cyan-800">Search Series</h3>
              <p className="text-xs text-gray-600">Find series by keyword in state, area, or industry name</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Enter keyword (e.g., 'manufacturing', 'construction', 'New York')..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || loadingSearch}
                  className="px-6 py-2 bg-cyan-600 text-white rounded-md hover:bg-cyan-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loadingSearch && <Loader2 className="w-4 h-4 animate-spin" />}
                  <Search className="w-4 h-4" />
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
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      Found {searchResults.total} series matching "{searchQuery}"
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-[400px]">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">State</th>
                          <th className="py-2 px-3">Area</th>
                          <th className="py-2 px-3">Supersector</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.series?.map((series) => (
                          <tr
                            key={series.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(series.series_id) ? 'bg-cyan-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(series.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(series.series_id)}
                                disabled={!selectedSeriesIds.includes(series.series_id) && selectedSeriesIds.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{series.series_id}</td>
                            <td className="py-2 px-3 text-xs">{series.state_name || 'N/A'}</td>
                            <td className="py-2 px-3 text-xs">{series.area_name || 'Statewide'}</td>
                            <td className="py-2 px-3 text-xs">{series.supersector_name || '-'}</td>
                            <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {searchResults.total > searchResults.series.length && (
                    <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
                      Showing {searchResults.series.length} of {searchResults.total} results. Use more specific keywords or drill-down below.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Sub-section 5B: Hierarchical Drill-down */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-green-800">Hierarchical Drill-down</h3>
              <p className="text-xs text-gray-600">Navigate: State → Area → Supersector → Data Type</p>
            </div>
            <div className="p-4">
              <div className="grid grid-cols-4 gap-4 mb-4">
                <Select
                  label="1. State"
                  value={drillStateCode}
                  onChange={(v) => {
                    setDrillStateCode(v);
                    setDrillAreaCode('');
                    setDrillSupersector('');
                    setDrilldownResults(null);
                  }}
                  options={[{ value: '', label: 'Select state...' }, ...stateOptions.slice(1)]}
                />
                <Select
                  label="2. Area"
                  value={drillAreaCode}
                  onChange={(v) => {
                    setDrillAreaCode(v);
                    setDrilldownResults(null);
                  }}
                  options={[
                    { value: '', label: drillStateCode ? 'All Areas' : 'Select state first' },
                    { value: '00000', label: 'Statewide Only' },
                  ]}
                />
                <Select
                  label="3. Supersector"
                  value={drillSupersector}
                  onChange={(v) => {
                    setDrillSupersector(v);
                    setDrilldownResults(null);
                  }}
                  options={[
                    { value: '', label: 'All Supersectors' },
                    ...(dimensions?.supersectors?.map(s => ({ value: s.supersector_code, label: s.supersector_name })) || [])
                  ]}
                />
                <Select
                  label="4. Data Type"
                  value={drillDataType}
                  onChange={setDrillDataType}
                  options={dimensions?.data_types?.map(dt => ({ value: dt.data_type_code, label: dt.data_type_name })) || [{ value: '01', label: 'All Employees' }]}
                />
              </div>

              {/* Drill-down Results */}
              {loadingDrilldown ? (
                <div className="py-8"><Loader2 className="w-6 h-6 animate-spin mx-auto text-green-500" /></div>
              ) : drilldownResults ? (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      {drilldownResults.total} series in selected category
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-[400px]">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Area</th>
                          <th className="py-2 px-3">Supersector</th>
                          <th className="py-2 px-3">Data Type</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {drilldownResults.series?.map((series) => (
                          <tr
                            key={series.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(series.series_id) ? 'bg-green-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(series.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(series.series_id)}
                                disabled={!selectedSeriesIds.includes(series.series_id) && selectedSeriesIds.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{series.series_id}</td>
                            <td className="py-2 px-3 text-xs">{series.area_name || 'Statewide'}</td>
                            <td className="py-2 px-3 text-xs">{series.supersector_name?.substring(0, 25) || '-'}</td>
                            <td className="py-2 px-3 text-xs">{series.data_type_name || '-'}</td>
                            <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {drilldownResults.total > drilldownResults.series.length && (
                    <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
                      Showing {drilldownResults.series.length} of {drilldownResults.total} series. Narrow down with filters above.
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">Select a state to start drilling down.</p>
              )}
            </div>
          </div>

          {/* Sub-section 5C: Paginated Browse */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-purple-800">Browse All Series</h3>
              <p className="text-xs text-gray-600">Paginated view of all available series</p>
            </div>
            <div className="p-4">
              {/* Browse Results with Pagination */}
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
                <div className="overflow-x-auto max-h-[1000px]">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                        <th className="py-2 px-3 w-8"></th>
                        <th className="py-2 px-3">Series ID</th>
                        <th className="py-2 px-3">State</th>
                        <th className="py-2 px-3">Area</th>
                        <th className="py-2 px-3">Supersector</th>
                        <th className="py-2 px-3">Data Type</th>
                        <th className="py-2 px-3">Period</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loadingBrowse ? (
                        <tr><td colSpan={7} className="py-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-purple-400" /></td></tr>
                      ) : browseResults?.series?.length === 0 ? (
                        <tr><td colSpan={7} className="py-8 text-center text-gray-500">No series found.</td></tr>
                      ) : (
                        browseResults?.series?.map((series) => (
                          <tr
                            key={series.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(series.series_id) ? 'bg-purple-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(series.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(series.series_id)}
                                disabled={!selectedSeriesIds.includes(series.series_id) && selectedSeriesIds.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{series.series_id}</td>
                            <td className="py-2 px-3 text-xs">{series.state_name?.substring(0, 15) || 'N/A'}</td>
                            <td className="py-2 px-3 text-xs">{series.area_name?.substring(0, 20) || 'Statewide'}</td>
                            <td className="py-2 px-3 text-xs">{series.supersector_name?.substring(0, 20) || '-'}</td>
                            <td className="py-2 px-3 text-xs">{series.data_type_name || '-'}</td>
                            <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
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

          {/* Chart/Table for Selected Series */}
          {selectedSeriesIds.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-3 bg-gradient-to-r from-cyan-100 to-blue-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-cyan-800">
                    {seriesView === 'chart' ? 'Series Comparison Chart' : 'Series Data Table'}
                  </p>
                  <p className="text-xs text-gray-600">{selectedSeriesIds.length} series selected - click series above to add/remove</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={seriesTimeRange}
                    onChange={(v) => setSeriesTimeRange(Number(v))}
                    options={TIME_RANGE_OPTIONS}
                    className="w-36"
                  />
                  <ViewToggle value={seriesView} onChange={setSeriesView} />
                </div>
              </div>

              <div className="p-4">
                <div className="flex flex-wrap gap-2 mb-4">
                  {selectedSeriesIds.map((seriesId, idx) => (
                    <span key={seriesId} className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs" style={{ backgroundColor: `${CHART_COLORS[idx % CHART_COLORS.length]}20`, color: CHART_COLORS[idx % CHART_COLORS.length] }}>
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                      {seriesId.substring(0, 15)}...
                      <button onClick={() => setSelectedSeriesIds(selectedSeriesIds.filter(s => s !== seriesId))} className="ml-1 hover:opacity-70"><X className="w-3 h-3" /></button>
                    </span>
                  ))}
                </div>

                {seriesView === 'chart' && (() => {
                const allDataLoaded = selectedSeriesIds.every(id => seriesChartData[id]);
                if (!allDataLoaded) return <div className="py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto text-cyan-500" /></div>;

                const allPeriods = new Map<string, { period_name: string; year: number; period: string }>();
                selectedSeriesIds.forEach(seriesId => {
                  const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                  data.forEach(dp => {
                    const key = `${dp.year}-${dp.period}`;
                    if (!allPeriods.has(key)) {
                      allPeriods.set(key, { period_name: dp.period_name, year: dp.year, period: dp.period });
                    }
                  });
                });

                const sortedPeriods = Array.from(allPeriods.values()).sort((a, b) => a.year - b.year || a.period.localeCompare(b.period));
                const chartData = sortedPeriods.map(p => {
                  const row: Record<string, string | number | null> = { period_name: p.period_name };
                  selectedSeriesIds.forEach(seriesId => {
                    const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                    const dp = data.find(d => d.year === p.year && d.period === p.period);
                    row[seriesId] = dp?.value ?? null;
                  });
                  return row;
                });

                return (
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} interval={Math.max(0, Math.floor(chartData.length / 12) - 1)} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {selectedSeriesIds.map((seriesId, idx) => {
                          const seriesInfo = seriesChartData[seriesId]?.series?.[0];
                          const label = seriesInfo ? `${seriesInfo.state_name} - ${seriesInfo.supersector_name || ''} - ${seriesInfo.data_type_name || ''}` : seriesId;
                          return (
                            <Line key={seriesId} type="monotone" dataKey={seriesId} stroke={CHART_COLORS[idx % CHART_COLORS.length]} strokeWidth={2} dot={false} name={label.substring(0, 40)} connectNulls />
                          );
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                );
              })()}

              {seriesView === 'table' && (() => {
                const allDataLoaded = selectedSeriesIds.every(id => seriesChartData[id]);
                if (!allDataLoaded) return <div className="py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto text-cyan-500" /></div>;

                const allPeriods = new Map<string, { period_name: string; year: number; period: string }>();
                selectedSeriesIds.forEach(seriesId => {
                  const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                  data.forEach(dp => {
                    const key = `${dp.year}-${dp.period}`;
                    if (!allPeriods.has(key)) {
                      allPeriods.set(key, { period_name: dp.period_name, year: dp.year, period: dp.period });
                    }
                  });
                });

                const sortedPeriods = Array.from(allPeriods.values()).sort((a, b) => b.year - a.year || b.period.localeCompare(a.period));
                const valueMap: Record<string, Record<string, number>> = {};
                selectedSeriesIds.forEach(seriesId => {
                  valueMap[seriesId] = {};
                  const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                  data.forEach(dp => { valueMap[seriesId][`${dp.year}-${dp.period}`] = dp.value; });
                });

                return (
                  <div className="overflow-x-auto max-h-[500px] border border-gray-200 rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-2 px-3 font-semibold sticky left-0 bg-gray-50 z-10">Period</th>
                          {selectedSeriesIds.map((seriesId, idx) => (
                            <th key={seriesId} className="text-right py-2 px-3 font-semibold min-w-[100px]" style={{ color: CHART_COLORS[idx % CHART_COLORS.length] }}>
                              {seriesId.substring(0, 12)}...
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {sortedPeriods.map((p, rowIdx) => (
                          <tr key={`${p.year}-${p.period}`} className={`border-b border-gray-100 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                            <td className="py-2 px-3 font-medium sticky left-0 bg-inherit">{p.period_name}</td>
                            {selectedSeriesIds.map(seriesId => {
                              const value = valueMap[seriesId][`${p.year}-${p.period}`];
                              return <td key={seriesId} className="text-right py-2 px-3 font-mono">{value != null ? value.toFixed(1) : '-'}</td>;
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                );
              })()}
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Info box */}
      <Card className="bg-blue-50 border-blue-200">
        <div className="p-4">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> SM Survey provides state and metropolitan area employment statistics including Total Nonfarm employment,
            employment by supersector (industry groupings), average weekly hours, and average earnings.
            Data is available for all 50 states, DC, Puerto Rico, and Virgin Islands, plus ~450 metropolitan areas.
            Most data starts from 1990, though some series have data back to 1939.
          </p>
        </div>
      </Card>
    </div>
  );
}
