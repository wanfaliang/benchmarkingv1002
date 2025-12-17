import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, DollarSign, Building2, Users, Briefcase, LucideIcon } from 'lucide-react';
import { ecResearchAPI } from '../../services/api';

/**
 * EC Explorer - Employment Cost Index Explorer
 *
 * ECI is a quarterly measure of the change in labor costs, free from
 * employment shifts. Legacy survey with data from 1980-2005.
 *
 * Compensation Types:
 * - Total compensation (wages + benefits)
 * - Wages and salaries
 * - Benefits
 *
 * Periodicity Types:
 * - Index (I) - Base June 1989 = 100
 * - 3-month percent change (Q)
 * - 12-month percent change (A)
 *
 * Ownership Types:
 * - Civilian (private + state/local)
 * - Private industry
 * - State and local government
 *
 * Sections:
 * 1. Overview - Headline ECI metrics with YoY change
 * 2. Compensation Timeline - Index/change trends over time
 * 3. Worker Group Analysis - Compare by occupation/industry groups
 * 4. Ownership Comparison - Civilian vs Private vs State/Local
 * 5. Series Explorer - Search, drill-down, browse
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

interface DimensionItem {
  code: string;
  name: string;
}

interface DimensionsData {
  compensations: DimensionItem[];
  groups: DimensionItem[];
  ownerships: DimensionItem[];
  periodicities: DimensionItem[];
}

interface CostMetric {
  series_id: string;
  name: string;
  comp_type: string;
  periodicity_type: string;
  latest_value: number | null;
  latest_year: number | null;
  latest_period: string | null;
  previous_value: number | null;
  yoy_change: number | null;
}

interface OverviewData {
  ownership: string;
  ownership_name: string;
  total_compensation_index: CostMetric | null;
  wages_salaries_index: CostMetric | null;
  benefits_index: CostMetric | null;
  total_compensation_quarterly: CostMetric | null;
  wages_salaries_quarterly: CostMetric | null;
  benefits_quarterly: CostMetric | null;
  total_compensation_annual: CostMetric | null;
  wages_salaries_annual: CostMetric | null;
  benefits_annual: CostMetric | null;
  data_range: string | null;
}

interface TimelinePoint {
  year: number;
  period: string;
  period_name: string;
  total_compensation: number | null;
  wages_salaries: number | null;
  benefits: number | null;
}

interface TimelineData {
  ownership: string;
  ownership_name: string;
  periodicity: string;
  timeline: TimelinePoint[];
}

interface GroupMetric {
  group_code: string;
  group_name: string;
  index_value: number | null;
  quarterly_change: number | null;
  annual_change: number | null;
  latest_year: number | null;
  latest_period: string | null;
}

interface GroupAnalysisData {
  ownership: string;
  ownership_name: string;
  comp_type: string;
  groups: GroupMetric[];
  latest_year: number | null;
}

interface GroupTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  groups: Record<string, number | null>;
}

interface GroupTimelineData {
  ownership: string;
  periodicity: string;
  comp_type: string;
  timeline: GroupTimelinePoint[];
  group_names: Record<string, string>;
}

interface OwnershipMetric {
  ownership_code: string;
  ownership_name: string;
  index_value: number | null;
  quarterly_change: number | null;
  annual_change: number | null;
}

interface OwnershipComparisonData {
  comp_type: string;
  group_name: string;
  ownerships: OwnershipMetric[];
  latest_year: number | null;
  latest_period: string | null;
}

interface OwnershipTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  ownerships: Record<string, number | null>;
}

interface OwnershipTimelineData {
  comp_type: string;
  periodicity: string;
  timeline: OwnershipTimelinePoint[];
  ownership_names: Record<string, string>;
}

interface SeriesInfo {
  series_id: string;
  comp_code: string | null;
  comp_name: string | null;
  group_code: string | null;
  group_name: string | null;
  ownership_code: string | null;
  ownership_name: string | null;
  periodicity_code: string | null;
  periodicity_name: string | null;
  seasonal: string;
  begin_year: number | null;
  begin_period: string | null;
  end_year: number | null;
  end_period: string | null;
  is_active: boolean;
}

interface SeriesListData {
  total: number;
  limit: number;
  offset: number;
  series: SeriesInfo[];
}

interface DataPoint {
  year: number;
  period: string;
  period_name: string;
  value: number | null;
  footnote_codes: string | null;
}

interface SeriesDataResponse {
  series: Array<{
    series_id: string;
    series_title: string;
    data_points: DataPoint[];
  }>;
}

// ============================================================================
// UI COMPONENTS
// ============================================================================

const Card = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
  <div className={`bg-white rounded-lg shadow-md border border-gray-200 ${className}`}>
    {children}
  </div>
);

interface SectionHeaderProps {
  title: string;
  color: string;
  icon: LucideIcon;
}

const SectionHeader = ({ title, color, icon: Icon }: SectionHeaderProps) => {
  const colorClasses: Record<string, string> = {
    blue: 'from-blue-600 to-blue-400',
    green: 'from-green-600 to-green-400',
    purple: 'from-purple-600 to-purple-400',
    orange: 'from-orange-600 to-orange-400',
    red: 'from-red-600 to-red-400',
    cyan: 'from-cyan-600 to-cyan-400',
    indigo: 'from-indigo-600 to-indigo-400',
  };
  return (
    <div className={`bg-gradient-to-r ${colorClasses[color] || colorClasses.blue} px-5 py-3 flex items-center gap-3`}>
      <Icon className="w-5 h-5 text-white" />
      <h2 className="text-lg font-semibold text-white">{title}</h2>
    </div>
  );
};

const LoadingSpinner = () => (
  <div className="flex items-center justify-center py-8">
    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
  </div>
);

interface SelectProps {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  options: SelectOption[];
  className?: string;
}

const Select = ({ label, value, onChange, options, className = '' }: SelectProps) => (
  <div className={className}>
    <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  </div>
);

interface ViewToggleProps {
  value: 'chart' | 'table';
  onChange: (value: 'chart' | 'table') => void;
}

const ViewToggle = ({ value, onChange }: ViewToggleProps) => (
  <div className="flex rounded-md border border-gray-300 overflow-hidden">
    <button
      onClick={() => onChange('chart')}
      className={`px-3 py-1 text-sm ${value === 'chart' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
    >
      Chart
    </button>
    <button
      onClick={() => onChange('table')}
      className={`px-3 py-1 text-sm ${value === 'table' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
    >
      Table
    </button>
  </div>
);

interface MetricCardProps {
  title: string;
  value: string | number | null;
  subtitle?: string;
  change?: number | null;
  changeLabel?: string;
  icon?: ReactElement;
  colorClass?: string;
}

const MetricCard = ({ title, value, subtitle, change, changeLabel, icon, colorClass = 'text-blue-600' }: MetricCardProps) => (
  <div className="bg-gray-50 rounded-lg p-4">
    <div className="flex items-center justify-between mb-2">
      <span className="text-sm text-gray-600">{title}</span>
      {icon}
    </div>
    <div className={`text-2xl font-bold ${colorClass}`}>
      {value !== null && value !== undefined ? value : 'N/A'}
    </div>
    {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
    {change !== null && change !== undefined && (
      <div className={`flex items-center gap-1 mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
        {change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        <span>{change >= 0 ? '+' : ''}{change.toFixed(2)}%</span>
        {changeLabel && <span className="text-gray-500 ml-1">{changeLabel}</span>}
      </div>
    )}
  </div>
);

// ============================================================================
// CONSTANTS
// ============================================================================

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

const timeRangeOptions: TimeRangeOption[] = [
  { value: 5, label: 'Last 5 years' },
  { value: 10, label: 'Last 10 years' },
  { value: 15, label: 'Last 15 years' },
  { value: 20, label: 'Last 20 years' },
  { value: 0, label: 'All Time' },
];

const ownershipOptions: SelectOption[] = [
  { value: '1', label: 'Civilian' },
  { value: '2', label: 'Private Industry' },
  { value: '3', label: 'State & Local Govt' },
];

const compensationOptions: SelectOption[] = [
  { value: '1', label: 'Total Compensation' },
  { value: '2', label: 'Wages & Salaries' },
  { value: '3', label: 'Benefits' },
];

const periodicityOptions: SelectOption[] = [
  { value: 'I', label: 'Index Level' },
  { value: 'Q', label: '3-Month % Change' },
  { value: 'A', label: '12-Month % Change' },
];

const seasonalOptions: SelectOption[] = [
  { value: '', label: 'All' },
  { value: 'S', label: 'Seasonally Adjusted' },
  { value: 'U', label: 'Not Adjusted' },
];

// Major worker groups for selection
const majorGroupOptions: SelectOption[] = [
  { value: '000', label: 'All Workers' },
  { value: '110', label: 'White-collar' },
  { value: '120', label: 'Blue-collar' },
  { value: '130', label: 'Service' },
  { value: '200', label: 'Goods-producing' },
  { value: '210', label: 'Service-producing' },
  { value: '240', label: 'Manufacturing' },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function ECExplorer() {
  // Dimensions data
  const [, setDimensions] = useState<DimensionsData | null>(null);
  const [loadingDimensions, setLoadingDimensions] = useState(true);

  // Section 1: Overview
  const [overviewOwnership, setOverviewOwnership] = useState('2');
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(false);

  // Section 2: Compensation Timeline
  const [timelineOwnership, setTimelineOwnership] = useState('2');
  const [timelinePeriodicity, setTimelinePeriodicity] = useState('I');
  const [timelineYears, setTimelineYears] = useState(10);
  const [timelineData, setTimelineData] = useState<TimelineData | null>(null);
  const [loadingTimeline, setLoadingTimeline] = useState(false);
  const [timelineView, setTimelineView] = useState<'chart' | 'table'>('chart');

  // Section 3: Worker Group Analysis
  const [groupOwnership, setGroupOwnership] = useState('2');
  const [groupCompType, setGroupCompType] = useState('1');
  const [groupData, setGroupData] = useState<GroupAnalysisData | null>(null);
  const [loadingGroups, setLoadingGroups] = useState(false);
  const [groupView, setGroupView] = useState<'chart' | 'table'>('chart');
  // Group timeline
  const [groupTimelinePeriodicity, setGroupTimelinePeriodicity] = useState('I');
  const [groupTimelineYears, setGroupTimelineYears] = useState(10);
  const [groupTimelineData, setGroupTimelineData] = useState<GroupTimelineData | null>(null);
  const [loadingGroupTimeline, setLoadingGroupTimeline] = useState(false);
  const [groupTimelineView, setGroupTimelineView] = useState<'chart' | 'table'>('chart');
  const [selectedGroupCodes, setSelectedGroupCodes] = useState<string[]>(['000', '110', '120', '130']);

  // Section 4: Ownership Comparison
  const [ownerCompType, setOwnerCompType] = useState('1');
  const [ownerGroupCode, setOwnerGroupCode] = useState('000');
  const [ownerData, setOwnerData] = useState<OwnershipComparisonData | null>(null);
  const [loadingOwner, setLoadingOwner] = useState(false);
  const [ownerView, setOwnerView] = useState<'chart' | 'table'>('chart');
  // Ownership timeline
  const [ownerTimelinePeriodicity, setOwnerTimelinePeriodicity] = useState('I');
  const [ownerTimelineYears, setOwnerTimelineYears] = useState(10);
  const [ownerTimelineData, setOwnerTimelineData] = useState<OwnershipTimelineData | null>(null);
  const [loadingOwnerTimeline, setLoadingOwnerTimeline] = useState(false);
  const [ownerTimelineView, setOwnerTimelineView] = useState<'chart' | 'table'>('chart');

  // Section 5: Series Explorer
  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);
  // Drill-down
  const [drillCompCode, setDrillCompCode] = useState('');
  const [drillGroupCode, setDrillGroupCode] = useState('');
  const [drillOwnershipCode, setDrillOwnershipCode] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);
  // Browse
  const [browseCompCode, setBrowseCompCode] = useState('');
  const [browseOwnershipCode, setBrowseOwnershipCode] = useState('');
  const [browseSeasonal, setBrowseSeasonal] = useState('');
  const [browseLimit, setBrowseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);
  // Selected series for charting
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<Record<string, SeriesDataResponse>>({});
  const [allSeriesInfo, setAllSeriesInfo] = useState<Record<string, SeriesInfo>>({});
  const [seriesTimeRange, setSeriesTimeRange] = useState(0); // 0 = All time
  const [seriesView, setSeriesView] = useState<'chart' | 'table'>('chart');

  // Dropdown options from dimensions
  const [groupOptions, setGroupOptions] = useState<SelectOption[]>([]);
  const [compOptions, setCompOptions] = useState<SelectOption[]>([]);
  const [ownerOptions, setOwnerOptions] = useState<SelectOption[]>([]);
  const [, setPeriodOptions] = useState<SelectOption[]>([]);

  // ============================================================================
  // DATA FETCHING
  // ============================================================================

  // Load dimensions on mount
  useEffect(() => {
    const fetchDimensions = async () => {
      try {
        const res = await ecResearchAPI.getDimensions<DimensionsData>();
        setDimensions(res.data);
        // Build dropdown options
        setCompOptions([
          { value: '', label: 'All' },
          ...res.data.compensations.map((c) => ({ value: c.code, label: c.name })),
        ]);
        setGroupOptions([
          { value: '', label: 'All' },
          ...res.data.groups.map((g) => ({ value: g.code, label: `${g.code} - ${g.name}` })),
        ]);
        setOwnerOptions([
          { value: '', label: 'All' },
          ...res.data.ownerships.map((o) => ({ value: o.code, label: o.name })),
        ]);
        setPeriodOptions([
          { value: '', label: 'All' },
          ...res.data.periodicities.map((p) => ({ value: p.code, label: p.name })),
        ]);
      } catch (err) {
        console.error('Failed to load dimensions:', err);
      } finally {
        setLoadingDimensions(false);
      }
    };
    fetchDimensions();
  }, []);

  // Section 1: Overview
  useEffect(() => {
    const fetchOverview = async () => {
      setLoadingOverview(true);
      try {
        const res = await ecResearchAPI.getOverview<OverviewData>(overviewOwnership);
        setOverviewData(res.data);
      } catch (err) {
        console.error('Failed to load overview:', err);
      } finally {
        setLoadingOverview(false);
      }
    };
    fetchOverview();
  }, [overviewOwnership]);

  // Section 2: Timeline
  useEffect(() => {
    const fetchTimeline = async () => {
      setLoadingTimeline(true);
      try {
        const res = await ecResearchAPI.getTimeline<TimelineData>(
          timelineOwnership,
          timelinePeriodicity,
          timelineYears
        );
        setTimelineData(res.data);
      } catch (err) {
        console.error('Failed to load timeline:', err);
      } finally {
        setLoadingTimeline(false);
      }
    };
    fetchTimeline();
  }, [timelineOwnership, timelinePeriodicity, timelineYears]);

  // Section 3: Groups
  useEffect(() => {
    const fetchGroups = async () => {
      setLoadingGroups(true);
      try {
        const res = await ecResearchAPI.getGroups<GroupAnalysisData>(groupOwnership, groupCompType);
        setGroupData(res.data);
      } catch (err) {
        console.error('Failed to load groups:', err);
      } finally {
        setLoadingGroups(false);
      }
    };
    fetchGroups();
  }, [groupOwnership, groupCompType]);

  // Section 3: Group Timeline
  useEffect(() => {
    const fetchGroupTimeline = async () => {
      if (selectedGroupCodes.length === 0) return;
      setLoadingGroupTimeline(true);
      try {
        const res = await ecResearchAPI.getGroupsTimeline<GroupTimelineData>(
          groupOwnership,
          groupCompType,
          groupTimelinePeriodicity,
          selectedGroupCodes.join(','),
          groupTimelineYears
        );
        setGroupTimelineData(res.data);
      } catch (err) {
        console.error('Failed to load group timeline:', err);
      } finally {
        setLoadingGroupTimeline(false);
      }
    };
    fetchGroupTimeline();
  }, [groupOwnership, groupCompType, groupTimelinePeriodicity, selectedGroupCodes, groupTimelineYears]);

  // Section 4: Ownership Comparison
  useEffect(() => {
    const fetchOwnership = async () => {
      setLoadingOwner(true);
      try {
        const res = await ecResearchAPI.getOwnershipComparison<OwnershipComparisonData>(
          ownerCompType,
          ownerGroupCode
        );
        setOwnerData(res.data);
      } catch (err) {
        console.error('Failed to load ownership comparison:', err);
      } finally {
        setLoadingOwner(false);
      }
    };
    fetchOwnership();
  }, [ownerCompType, ownerGroupCode]);

  // Section 4: Ownership Timeline
  useEffect(() => {
    const fetchOwnerTimeline = async () => {
      setLoadingOwnerTimeline(true);
      try {
        const res = await ecResearchAPI.getOwnershipTimeline<OwnershipTimelineData>(
          ownerCompType,
          ownerTimelinePeriodicity,
          ownerTimelineYears
        );
        setOwnerTimelineData(res.data);
      } catch (err) {
        console.error('Failed to load ownership timeline:', err);
      } finally {
        setLoadingOwnerTimeline(false);
      }
    };
    fetchOwnerTimeline();
  }, [ownerCompType, ownerTimelinePeriodicity, ownerTimelineYears]);

  // Drill-down effect
  useEffect(() => {
    const fetchDrill = async () => {
      if (!drillCompCode && !drillGroupCode && !drillOwnershipCode) {
        setDrillResults(null);
        return;
      }
      setLoadingDrill(true);
      try {
        const params: Record<string, unknown> = { limit: 100 };
        if (drillCompCode) params.comp_code = drillCompCode;
        if (drillGroupCode) params.group_code = drillGroupCode;
        if (drillOwnershipCode) params.ownership_code = drillOwnershipCode;
        const res = await ecResearchAPI.getSeries<SeriesListData>(params);
        setDrillResults(res.data);
      } catch (err) {
        console.error('Drill-down failed:', err);
      } finally {
        setLoadingDrill(false);
      }
    };
    fetchDrill();
  }, [drillCompCode, drillGroupCode, drillOwnershipCode]);

  // Browse effect
  useEffect(() => {
    const fetchBrowse = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseCompCode) params.comp_code = browseCompCode;
        if (browseOwnershipCode) params.ownership_code = browseOwnershipCode;
        if (browseSeasonal) params.seasonal = browseSeasonal;
        const res = await ecResearchAPI.getSeries<SeriesListData>(params);
        setBrowseResults(res.data);
      } catch (err) {
        console.error('Browse failed:', err);
      } finally {
        setLoadingBrowse(false);
      }
    };
    fetchBrowse();
  }, [browseCompCode, browseOwnershipCode, browseSeasonal, browseLimit, browseOffset]);

  // Selected series data
  useEffect(() => {
    const fetchSeriesData = async () => {
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const startYear = seriesTimeRange > 0 ? 2005 - seriesTimeRange : undefined;
            const res = await ecResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, startYear);
            setSeriesChartData((prev) => ({ ...prev, [seriesId]: res.data }));
          } catch (err) {
            console.error(`Failed to load data for ${seriesId}:`, err);
          }
        }
      }
    };
    if (selectedSeriesIds.length > 0) fetchSeriesData();
  }, [selectedSeriesIds, seriesTimeRange]);

  // ============================================================================
  // HANDLERS
  // ============================================================================

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await ecResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 100 });
      setSearchResults(res.data);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleSearchKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  const toggleSeriesSelection = (seriesId: string, info?: SeriesInfo) => {
    if (selectedSeriesIds.includes(seriesId)) {
      setSelectedSeriesIds(selectedSeriesIds.filter((id) => id !== seriesId));
    } else if (selectedSeriesIds.length < 5) {
      setSelectedSeriesIds([...selectedSeriesIds, seriesId]);
      if (info) {
        setAllSeriesInfo((prev) => ({ ...prev, [seriesId]: info }));
      }
    }
  };

  const toggleGroupSelection = (groupCode: string) => {
    if (selectedGroupCodes.includes(groupCode)) {
      setSelectedGroupCodes(selectedGroupCodes.filter((c) => c !== groupCode));
    } else if (selectedGroupCodes.length < 7) {
      setSelectedGroupCodes([...selectedGroupCodes, groupCode]);
    }
  };

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const formatValue = (val: number | null | undefined, decimals: number = 1): string => {
    if (val === null || val === undefined) return 'N/A';
    return val.toFixed(decimals);
  };

  const formatPeriodLabel = (point: { year: number; period: string }): string => {
    return `${point.year} ${point.period}`;
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  if (loadingDimensions) {
    return (
      <div className="p-6">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          Employment Cost Index (EC) Explorer
        </h1>
        <p className="text-gray-600">
          Quarterly measure of change in labor costs. Index base: June 1989 = 100.
          <span className="ml-2 px-2 py-0.5 bg-amber-100 text-amber-800 text-xs rounded">Legacy Data: 1980-2005</span>
        </p>
      </div>

      {/* Section 1: Overview */}
      <Card>
        <SectionHeader title="1. Overview - Headline ECI Metrics" color="blue" icon={DollarSign} />
        <div className="p-5">
          <div className="flex gap-4 mb-4">
            <Select
              label="Ownership"
              value={overviewOwnership}
              onChange={setOverviewOwnership}
              options={ownershipOptions}
              className="w-48"
            />
          </div>

          {loadingOverview ? (
            <LoadingSpinner />
          ) : overviewData ? (
            <>
              <div className="mb-2 text-sm text-gray-500">
                Data Range: {overviewData.data_range || 'N/A'}
              </div>

              {/* Index Values */}
              <h3 className="text-md font-semibold text-gray-700 mb-3">Index Levels (June 1989 = 100)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <MetricCard
                  title="Total Compensation"
                  value={formatValue(overviewData.total_compensation_index?.latest_value)}
                  subtitle={`${overviewData.total_compensation_index?.latest_year} ${overviewData.total_compensation_index?.latest_period}`}
                  change={overviewData.total_compensation_index?.yoy_change}
                  changeLabel="YoY"
                  colorClass="text-blue-600"
                />
                <MetricCard
                  title="Wages & Salaries"
                  value={formatValue(overviewData.wages_salaries_index?.latest_value)}
                  subtitle={`${overviewData.wages_salaries_index?.latest_year} ${overviewData.wages_salaries_index?.latest_period}`}
                  change={overviewData.wages_salaries_index?.yoy_change}
                  changeLabel="YoY"
                  colorClass="text-green-600"
                />
                <MetricCard
                  title="Benefits"
                  value={formatValue(overviewData.benefits_index?.latest_value)}
                  subtitle={`${overviewData.benefits_index?.latest_year} ${overviewData.benefits_index?.latest_period}`}
                  change={overviewData.benefits_index?.yoy_change}
                  changeLabel="YoY"
                  colorClass="text-purple-600"
                />
              </div>

              {/* Percent Changes */}
              <h3 className="text-md font-semibold text-gray-700 mb-3">Percent Changes</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <MetricCard
                  title="Total Comp (3-Month)"
                  value={overviewData.total_compensation_quarterly?.latest_value != null
                    ? `${formatValue(overviewData.total_compensation_quarterly?.latest_value)}%` : 'N/A'}
                  colorClass="text-blue-600"
                />
                <MetricCard
                  title="Wages (3-Month)"
                  value={overviewData.wages_salaries_quarterly?.latest_value != null
                    ? `${formatValue(overviewData.wages_salaries_quarterly?.latest_value)}%` : 'N/A'}
                  colorClass="text-green-600"
                />
                <MetricCard
                  title="Benefits (3-Month)"
                  value={overviewData.benefits_quarterly?.latest_value != null
                    ? `${formatValue(overviewData.benefits_quarterly?.latest_value)}%` : 'N/A'}
                  colorClass="text-purple-600"
                />
              </div>
            </>
          ) : (
            <div className="text-gray-500 text-center py-4">No data available</div>
          )}
        </div>
      </Card>

      {/* Section 2: Compensation Timeline */}
      <Card>
        <SectionHeader title="2. Compensation Timeline" color="green" icon={TrendingUp} />
        <div className="p-5">
          <div className="flex flex-wrap gap-4 mb-4">
            <Select
              label="Ownership"
              value={timelineOwnership}
              onChange={setTimelineOwnership}
              options={ownershipOptions}
              className="w-48"
            />
            <Select
              label="Metric Type"
              value={timelinePeriodicity}
              onChange={setTimelinePeriodicity}
              options={periodicityOptions}
              className="w-48"
            />
            <Select
              label="Time Range"
              value={timelineYears}
              onChange={(v) => setTimelineYears(Number(v))}
              options={timeRangeOptions}
              className="w-40"
            />
            <div className="flex items-end">
              <ViewToggle value={timelineView} onChange={setTimelineView} />
            </div>
          </div>

          {loadingTimeline ? (
            <LoadingSpinner />
          ) : timelineData && timelineData.timeline.length > 0 ? (
            timelineView === 'chart' ? (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={timelineData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey={(d) => formatPeriodLabel(d)}
                      tick={{ fontSize: 10 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip
                      labelFormatter={(_, payload) => {
                        if (payload && payload[0]) {
                          const p = payload[0].payload as TimelinePoint;
                          return `${p.year} ${p.period_name}`;
                        }
                        return '';
                      }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="total_compensation" name="Total Compensation" stroke="#3b82f6" dot={false} />
                    <Line type="monotone" dataKey="wages_salaries" name="Wages & Salaries" stroke="#10b981" dot={false} />
                    <Line type="monotone" dataKey="benefits" name="Benefits" stroke="#8b5cf6" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="overflow-x-auto max-h-96 overflow-y-auto border rounded-md">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left">Period</th>
                      <th className="px-3 py-2 text-right">Total Comp</th>
                      <th className="px-3 py-2 text-right">Wages</th>
                      <th className="px-3 py-2 text-right">Benefits</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {timelineData.timeline.map((point, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-3 py-2">{point.year} {point.period_name}</td>
                        <td className="px-3 py-2 text-right">{formatValue(point.total_compensation)}</td>
                        <td className="px-3 py-2 text-right">{formatValue(point.wages_salaries)}</td>
                        <td className="px-3 py-2 text-right">{formatValue(point.benefits)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : (
            <div className="text-gray-500 text-center py-4">No timeline data available</div>
          )}
        </div>
      </Card>

      {/* Section 3: Worker Group Analysis */}
      <Card>
        <SectionHeader title="3. Worker Group Analysis" color="purple" icon={Users} />
        <div className="p-5">
          <div className="flex flex-wrap gap-4 mb-4">
            <Select
              label="Ownership"
              value={groupOwnership}
              onChange={setGroupOwnership}
              options={ownershipOptions}
              className="w-48"
            />
            <Select
              label="Compensation Type"
              value={groupCompType}
              onChange={setGroupCompType}
              options={compensationOptions}
              className="w-48"
            />
            <div className="flex items-end">
              <ViewToggle value={groupView} onChange={setGroupView} />
            </div>
          </div>

          {loadingGroups ? (
            <LoadingSpinner />
          ) : groupData && groupData.groups.length > 0 ? (
            groupView === 'chart' ? (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={groupData.groups.slice(0, 15)} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tick={{ fontSize: 10 }} />
                    <YAxis
                      type="category"
                      dataKey="group_name"
                      tick={{ fontSize: 9 }}
                      width={200}
                    />
                    <Tooltip />
                    <Bar dataKey="index_value" name="Index Value" fill="#8b5cf6">
                      {groupData.groups.slice(0, 15).map((_, idx) => (
                        <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="overflow-x-auto max-h-96 overflow-y-auto border rounded-md">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-3 py-2 text-left">
                        <input
                          type="checkbox"
                          className="mr-2"
                          disabled
                        />
                        Group
                      </th>
                      <th className="px-3 py-2 text-right">Index</th>
                      <th className="px-3 py-2 text-right">3-Mo %</th>
                      <th className="px-3 py-2 text-right">12-Mo %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {groupData.groups.map((g) => (
                      <tr key={g.group_code} className="hover:bg-gray-50">
                        <td className="px-3 py-2">
                          <input
                            type="checkbox"
                            checked={selectedGroupCodes.includes(g.group_code)}
                            onChange={() => toggleGroupSelection(g.group_code)}
                            className="mr-2"
                          />
                          {g.group_name}
                        </td>
                        <td className="px-3 py-2 text-right font-medium">{formatValue(g.index_value)}</td>
                        <td className="px-3 py-2 text-right">{formatValue(g.quarterly_change)}%</td>
                        <td className="px-3 py-2 text-right">{formatValue(g.annual_change)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : (
            <div className="text-gray-500 text-center py-4">No group data available</div>
          )}

          {/* Group Timeline */}
          {selectedGroupCodes.length > 0 && (
            <div className="mt-6 border-t pt-4">
              <h3 className="text-md font-semibold text-gray-700 mb-3">
                Selected Groups Timeline ({selectedGroupCodes.length} selected)
              </h3>
              <div className="flex flex-wrap gap-4 mb-4">
                <Select
                  label="Metric Type"
                  value={groupTimelinePeriodicity}
                  onChange={setGroupTimelinePeriodicity}
                  options={periodicityOptions}
                  className="w-48"
                />
                <Select
                  label="Time Range"
                  value={groupTimelineYears}
                  onChange={(v) => setGroupTimelineYears(Number(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
                <div className="flex items-end">
                  <ViewToggle value={groupTimelineView} onChange={setGroupTimelineView} />
                </div>
              </div>

              {loadingGroupTimeline ? (
                <LoadingSpinner />
              ) : groupTimelineData && groupTimelineData.timeline.length > 0 ? (
                groupTimelineView === 'chart' ? (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={groupTimelineData.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey={(d) => formatPeriodLabel(d)}
                          tick={{ fontSize: 10 }}
                          interval="preserveStartEnd"
                        />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        {selectedGroupCodes.map((code, idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`groups.${code}`}
                            name={groupTimelineData.group_names[code] || code}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="overflow-x-auto max-h-96 overflow-y-auto border rounded-md">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left">Period</th>
                          {selectedGroupCodes.map((code) => (
                            <th key={code} className="px-3 py-2 text-right">
                              {groupTimelineData.group_names[code] || code}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {groupTimelineData.timeline.map((point, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-3 py-2">{point.year} {point.period_name}</td>
                            {selectedGroupCodes.map((code) => (
                              <td key={code} className="px-3 py-2 text-right">
                                {formatValue(point.groups[code])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )
              ) : null}
            </div>
          )}
        </div>
      </Card>

      {/* Section 4: Ownership Comparison */}
      <Card>
        <SectionHeader title="4. Ownership Comparison" color="orange" icon={Building2} />
        <div className="p-5">
          <div className="flex flex-wrap gap-4 mb-4">
            <Select
              label="Compensation Type"
              value={ownerCompType}
              onChange={setOwnerCompType}
              options={compensationOptions}
              className="w-48"
            />
            <Select
              label="Worker Group"
              value={ownerGroupCode}
              onChange={setOwnerGroupCode}
              options={majorGroupOptions}
              className="w-48"
            />
            <div className="flex items-end">
              <ViewToggle value={ownerView} onChange={setOwnerView} />
            </div>
          </div>

          {loadingOwner ? (
            <LoadingSpinner />
          ) : ownerData && ownerData.ownerships.length > 0 ? (
            ownerView === 'chart' ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ownerData.ownerships}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="ownership_name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Bar dataKey="index_value" name="Index Value">
                      {ownerData.ownerships.map((_, idx) => (
                        <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="overflow-x-auto border rounded-md">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left">Ownership</th>
                      <th className="px-3 py-2 text-right">Index</th>
                      <th className="px-3 py-2 text-right">3-Mo %</th>
                      <th className="px-3 py-2 text-right">12-Mo %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {ownerData.ownerships.map((o) => (
                      <tr key={o.ownership_code} className="hover:bg-gray-50">
                        <td className="px-3 py-2 font-medium">{o.ownership_name}</td>
                        <td className="px-3 py-2 text-right">{formatValue(o.index_value)}</td>
                        <td className="px-3 py-2 text-right">{formatValue(o.quarterly_change)}%</td>
                        <td className="px-3 py-2 text-right">{formatValue(o.annual_change)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          ) : (
            <div className="text-gray-500 text-center py-4">No ownership data available</div>
          )}

          {/* Ownership Timeline */}
          <div className="mt-6 border-t pt-4">
            <h3 className="text-md font-semibold text-gray-700 mb-3">Ownership Timeline</h3>
            <div className="flex flex-wrap gap-4 mb-4">
              <Select
                label="Metric Type"
                value={ownerTimelinePeriodicity}
                onChange={setOwnerTimelinePeriodicity}
                options={periodicityOptions}
                className="w-48"
              />
              <Select
                label="Time Range"
                value={ownerTimelineYears}
                onChange={(v) => setOwnerTimelineYears(Number(v))}
                options={timeRangeOptions}
                className="w-40"
              />
              <div className="flex items-end">
                <ViewToggle value={ownerTimelineView} onChange={setOwnerTimelineView} />
              </div>
            </div>

            {loadingOwnerTimeline ? (
              <LoadingSpinner />
            ) : ownerTimelineData && ownerTimelineData.timeline.length > 0 ? (
              ownerTimelineView === 'chart' ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={ownerTimelineData.timeline}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey={(d) => formatPeriodLabel(d)}
                        tick={{ fontSize: 10 }}
                        interval="preserveStartEnd"
                      />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      {Object.keys(ownerTimelineData.ownership_names).map((code, idx) => (
                        <Line
                          key={code}
                          type="monotone"
                          dataKey={`ownerships.${code}`}
                          name={ownerTimelineData.ownership_names[code]}
                          stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                          dot={false}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-96 overflow-y-auto border rounded-md">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left">Period</th>
                        {Object.entries(ownerTimelineData.ownership_names).map(([code, name]) => (
                          <th key={code} className="px-3 py-2 text-right">{name}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {ownerTimelineData.timeline.map((point, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-3 py-2">{point.year} {point.period_name}</td>
                          {Object.keys(ownerTimelineData.ownership_names).map((code) => (
                            <td key={code} className="px-3 py-2 text-right">
                              {formatValue(point.ownerships[code])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            ) : null}
          </div>
        </div>
      </Card>

      {/* Section 5: Series Explorer */}
      <Card>
        <SectionHeader title="5. Series Detail Explorer" color="red" icon={Briefcase} />
        <div className="p-5 space-y-6">
          {/* Sub-section A: Search by Keyword */}
          <div className="border-l-4 border-cyan-500 pl-4">
            <h3 className="text-lg font-semibold bg-gradient-to-r from-cyan-600 to-cyan-400 bg-clip-text text-transparent mb-3">
              Search by Keyword
            </h3>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                placeholder="Search series by group name..."
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
                      <th className="px-3 py-2 text-left">Compensation</th>
                      <th className="px-3 py-2 text-left">Group</th>
                      <th className="px-3 py-2 text-left">Ownership</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {searchResults.series.map((s) => (
                      <tr key={s.series_id} className="hover:bg-gray-50">
                        <td className="px-3 py-2">
                          <input
                            type="checkbox"
                            checked={selectedSeriesIds.includes(s.series_id)}
                            onChange={() => toggleSeriesSelection(s.series_id, s)}
                            className="rounded"
                          />
                        </td>
                        <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                        <td className="px-3 py-2">{s.comp_name}</td>
                        <td className="px-3 py-2 text-xs">{s.group_name}</td>
                        <td className="px-3 py-2">{s.ownership_name}</td>
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
                label="Compensation"
                value={drillCompCode}
                onChange={setDrillCompCode}
                options={compOptions}
                className="w-48"
              />
              <Select
                label="Worker Group"
                value={drillGroupCode}
                onChange={setDrillGroupCode}
                options={groupOptions}
                className="w-64"
              />
              <Select
                label="Ownership"
                value={drillOwnershipCode}
                onChange={setDrillOwnershipCode}
                options={ownerOptions}
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
                      <th className="px-3 py-2 text-left">Comp</th>
                      <th className="px-3 py-2 text-left">Group</th>
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
                            onChange={() => toggleSeriesSelection(s.series_id, s)}
                            className="rounded"
                          />
                        </td>
                        <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                        <td className="px-3 py-2">{s.comp_name}</td>
                        <td className="px-3 py-2 text-xs">{s.group_name}</td>
                        <td className="px-3 py-2">{s.periodicity_name}</td>
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
                label="Compensation"
                value={browseCompCode}
                onChange={(v) => { setBrowseCompCode(v); setBrowseOffset(0); }}
                options={compOptions}
                className="w-48"
              />
              <Select
                label="Ownership"
                value={browseOwnershipCode}
                onChange={(v) => { setBrowseOwnershipCode(v); setBrowseOffset(0); }}
                options={ownerOptions}
                className="w-48"
              />
              <Select
                label="Seasonal Adj"
                value={browseSeasonal}
                onChange={(v) => { setBrowseSeasonal(v); setBrowseOffset(0); }}
                options={seasonalOptions}
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
                        <th className="px-3 py-2 text-left">Compensation</th>
                        <th className="px-3 py-2 text-left">Group</th>
                        <th className="px-3 py-2 text-left">Ownership</th>
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
                              onChange={() => toggleSeriesSelection(s.series_id, s)}
                              className="rounded"
                            />
                          </td>
                          <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                          <td className="px-3 py-2">{s.comp_name}</td>
                          <td className="px-3 py-2 text-xs">{s.group_name}</td>
                          <td className="px-3 py-2">{s.ownership_name}</td>
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
                    onChange={(v) => {
                      setSeriesTimeRange(Number(v));
                      setSeriesChartData({}); // Clear cached data to refetch
                    }}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <div className="flex items-end">
                    <ViewToggle value={seriesView} onChange={setSeriesView} />
                  </div>
                  <button
                    onClick={() => {
                      setSelectedSeriesIds([]);
                      setSeriesChartData({});
                    }}
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
                            name={info ? `${info.comp_name} - ${info.group_name}` : seriesId}
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
                              {info ? `${info.comp_name?.substring(0, 10)}...` : seriesId}
                            </th>
                          );
                        })}
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {(() => {
                        // Get max length timeline
                        const firstSeries = selectedSeriesIds.find((id) => seriesChartData[id]);
                        if (!firstSeries) return null;
                        const points = seriesChartData[firstSeries]?.series?.[0]?.data_points || [];
                        return points.map((pt, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-3 py-2">{pt.year} {pt.period_name}</td>
                            {selectedSeriesIds.map((seriesId) => {
                              const data = seriesChartData[seriesId]?.series?.[0]?.data_points;
                              const val = data?.[idx]?.value;
                              return (
                                <td key={seriesId} className="px-3 py-2 text-right">
                                  {formatValue(val)}
                                </td>
                              );
                            })}
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
