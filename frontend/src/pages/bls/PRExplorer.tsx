import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, Activity, Building2, Users, Factory, Briefcase, LucideIcon } from 'lucide-react';
import { prResearchAPI } from '../../services/api';

/**
 * PR Explorer - Major Sector Productivity and Costs Explorer
 *
 * Provides productivity and cost measures for major economic sectors:
 * - Business Sector
 * - Nonfarm Business Sector
 * - Nonfinancial Corporations
 * - Manufacturing (Total, Durable, Nondurable)
 *
 * Key Measures:
 * - Labor productivity (output per hour)
 * - Unit labor costs
 * - Hourly compensation
 * - Real hourly compensation
 * - Output
 * - Hours worked
 *
 * Duration Types:
 * - Index (2017=100)
 * - Percent change from previous year
 * - Percent change from previous quarter
 *
 * Sections:
 * 1. Overview - Productivity metrics across all sectors
 * 2. Sector Analysis - Detailed measures for a specific sector
 * 3. Productivity vs Costs - Compare productivity with labor costs
 * 4. Manufacturing Comparison - Compare manufacturing subsectors
 * 5. Series Explorer - Search, drill-down, browse
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

type ViewType = 'chart' | 'table';

interface SelectOption {
  value: string | number;
  label: string;
}

interface TimeRangeOption {
  value: number;
  label: string;
}

interface SectorItem {
  sector_code: string;
  sector_name: string;
}

interface ClassItem {
  class_code: string;
  class_text: string;
}

interface MeasureItem {
  measure_code: string;
  measure_text: string;
}

interface DurationItem {
  duration_code: string;
  duration_text: string;
}

interface DimensionsData {
  sectors: SectorItem[];
  classes: ClassItem[];
  measures: MeasureItem[];
  durations: DurationItem[];
}

interface SectorMetrics {
  sector_code: string;
  sector_name: string;
  labor_productivity_index: number | null;
  labor_productivity_change: number | null;
  unit_labor_costs_index: number | null;
  unit_labor_costs_change: number | null;
  output_index: number | null;
  output_change: number | null;
  hours_index: number | null;
  hours_change: number | null;
  compensation_index: number | null;
  compensation_change: number | null;
  latest_year: number | null;
  latest_period: string | null;
}

interface OverviewData {
  sectors: SectorMetrics[];
  latest_year: number | null;
  latest_period: string | null;
}

interface OverviewTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  sectors: Record<string, number | null>;
}

interface OverviewTimelineData {
  measure: string;
  duration: string;
  timeline: OverviewTimelinePoint[];
  sector_names: Record<string, string>;
}

interface MeasureMetric {
  measure_code: string;
  measure_text: string;
  index_value: number | null;
  yoy_change: number | null;
  qoq_change: number | null;
  latest_year: number | null;
  latest_period: string | null;
}

interface SectorAnalysisData {
  sector_code: string;
  sector_name: string;
  class_code: string | null;
  class_text: string | null;
  measures: MeasureMetric[];
  latest_year: number | null;
  latest_period: string | null;
}

interface MeasureTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  measures: Record<string, number | null>;
}

interface MeasureTimelineData {
  sector_code: string;
  sector_name: string;
  duration: string;
  timeline: MeasureTimelinePoint[];
  measure_names: Record<string, string>;
}

interface ProductivityVsCosts {
  sector_code: string;
  sector_name: string;
  productivity_index: number | null;
  productivity_change: number | null;
  unit_labor_costs_index: number | null;
  unit_labor_costs_change: number | null;
  hourly_compensation_index: number | null;
  hourly_compensation_change: number | null;
  real_compensation_index: number | null;
  real_compensation_change: number | null;
}

interface ProductivityVsCostsData {
  analysis: ProductivityVsCosts[];
  latest_year: number | null;
  latest_period: string | null;
}

interface ProductivityVsCostsTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  productivity: number | null;
  unit_labor_costs: number | null;
  hourly_compensation: number | null;
}

interface ProductivityVsCostsTimelineData {
  sector_code: string;
  sector_name: string;
  duration: string;
  timeline: ProductivityVsCostsTimelinePoint[];
}

interface ManufacturingMetric {
  sector_code: string;
  sector_name: string;
  productivity_index: number | null;
  productivity_change: number | null;
  unit_labor_costs_index: number | null;
  unit_labor_costs_change: number | null;
  output_index: number | null;
  output_change: number | null;
}

interface ManufacturingData {
  manufacturing_sectors: ManufacturingMetric[];
  latest_year: number | null;
  latest_period: string | null;
}

interface ManufacturingTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  sectors: Record<string, number | null>;
}

interface ManufacturingTimelineData {
  measure: string;
  timeline: ManufacturingTimelinePoint[];
  sector_names: Record<string, string>;
}

interface SeriesInfo {
  series_id: string;
  seasonal: string | null;
  sector_code: string | null;
  sector_name: string | null;
  class_code: string | null;
  class_text: string | null;
  measure_code: string | null;
  measure_text: string | null;
  duration_code: string | null;
  duration_text: string | null;
  base_year: string | null;
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
    sector_name: string | null;
    class_text: string | null;
    measure_text: string | null;
    duration_text: string | null;
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
  value: ViewType;
  onChange: (value: ViewType) => void;
}

const ViewToggle = ({ value, onChange }: ViewToggleProps): ReactElement => (
  <div className="flex border border-gray-300 rounded-md overflow-hidden">
    <button
      onClick={() => onChange('chart')}
      className={`px-3 py-1.5 text-sm font-medium transition-colors ${
        value === 'chart' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
      }`}
    >
      Chart
    </button>
    <button
      onClick={() => onChange('table')}
      className={`px-3 py-1.5 text-sm font-medium transition-colors ${
        value === 'table' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
      }`}
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
      {value != null ? value : 'N/A'}
    </div>
    {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
    {change != null && (
      <div className={`flex items-center gap-1 mt-2 text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
        {change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        <span>{change >= 0 ? '+' : ''}{change.toFixed(2)}%</span>
        {changeLabel && <span className="text-gray-500 ml-1">{changeLabel}</span>}
      </div>
    )}
  </div>
);
interface TimelineSelectorProps {
  timeline: { year: number; period: string; period_name: string }[];
  selectedIndex: number | null;
  onSelectIndex: (index: number) => void;
}

const formatPeriodShort = (period: string): string => {
  if (period.startsWith('Q0')) return period.replace('Q0', 'Q');
  if (period === 'Q05') return 'Ann';
  return period;
};

const TimelineSelector = ({ timeline, selectedIndex, onSelectIndex }: TimelineSelectorProps): ReactElement | null => {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="mt-4 mb-2 px-2">
      <p className="text-xs text-gray-500 mb-2">Select period (click any point):</p>
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
                    {formatPeriodShort(point.period)} {point.year}
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
// CONSTANTS
// ============================================================================

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

const timeRangeOptions: TimeRangeOption[] = [
  { value: 5, label: 'Last 5 years' },
  { value: 10, label: 'Last 10 years' },
  { value: 20, label: 'Last 20 years' },
  { value: 50, label: 'Last 50 years' },
  { value: 0, label: 'All Time' },
];

const periodTypeOptions: SelectOption[] = [
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'annual', label: 'Annual' },
];

const classOptions: SelectOption[] = [
  { value: '5', label: 'All Persons' },
  { value: '6', label: 'Employees' },
];

const measureOptions: SelectOption[] = [
  { value: 'labor_productivity', label: 'Labor Productivity' },
  { value: 'unit_labor_costs', label: 'Unit Labor Costs' },
  { value: 'output', label: 'Output' },
  { value: 'hours', label: 'Hours Worked' },
  { value: 'compensation', label: 'Hourly Compensation' },
];

const durationOptions: SelectOption[] = [
  { value: 'index', label: 'Index (2017=100)' },
  { value: 'pct_change', label: '% Change YoY' },
];

const manufacturingMeasureOptions: SelectOption[] = [
  { value: 'productivity', label: 'Productivity' },
  { value: 'unit_labor_costs', label: 'Unit Labor Costs' },
  { value: 'output', label: 'Output' },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function PRExplorer() {
  // Dimensions data
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [loadingDimensions, setLoadingDimensions] = useState(true);

  // Section 1: Overview
  const [overviewClass, setOverviewClass] = useState('6');
  const [overviewPeriodType, setOverviewPeriodType] = useState('quarterly');
  const [overviewMeasure, setOverviewMeasure] = useState('labor_productivity');
  const [overviewDuration, setOverviewDuration] = useState('index');
  const [overviewYears, setOverviewYears] = useState(20);
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [overviewTimelineData, setOverviewTimelineData] = useState<OverviewTimelineData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(false);
  const [loadingOverviewTimeline, setLoadingOverviewTimeline] = useState(false);
  const [overviewView, setOverviewView] = useState<ViewType>('chart');
  const [overviewSelectedIndex, setOverviewSelectedIndex] = useState<number | null>(null);

  // Section 2: Sector Analysis
  const [analysisSector, setAnalysisSector] = useState('8500'); // Nonfarm Business
  const [analysisClass, setAnalysisClass] = useState('6');
  const [analysisPeriodType, setAnalysisPeriodType] = useState('quarterly');
  const [analysisDuration, setAnalysisDuration] = useState('index');
  const [analysisYears, setAnalysisYears] = useState(20);
  const [analysisData, setAnalysisData] = useState<SectorAnalysisData | null>(null);
  const [analysisTimelineData, setAnalysisTimelineData] = useState<MeasureTimelineData | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [loadingAnalysisTimeline, setLoadingAnalysisTimeline] = useState(false);
  const [analysisView, setAnalysisView] = useState<ViewType>('chart');
  const [selectedMeasureCodes, setSelectedMeasureCodes] = useState<string[]>(['01', '07', '04']);
  const [analysisSelectedIndex, setAnalysisSelectedIndex] = useState<number | null>(null);

  // Section 3: Productivity vs Costs
  const [pvcClass, setPvcClass] = useState('6');
  const [pvcPeriodType, setPvcPeriodType] = useState('quarterly');
  const [pvcSector, setPvcSector] = useState('8500');
  const [pvcDuration, setPvcDuration] = useState('index');
  const [pvcYears, setPvcYears] = useState(20);
  const [pvcData, setPvcData] = useState<ProductivityVsCostsData | null>(null);
  const [pvcTimelineData, setPvcTimelineData] = useState<ProductivityVsCostsTimelineData | null>(null);
  const [loadingPvc, setLoadingPvc] = useState(false);
  const [loadingPvcTimeline, setLoadingPvcTimeline] = useState(false);
  const [pvcView, setPvcView] = useState<ViewType>('chart');
  const [pvcSelectedIndex, setPvcSelectedIndex] = useState<number | null>(null);

  // Section 4: Manufacturing Comparison
  const [mfgClass, setMfgClass] = useState('6');
  const [mfgPeriodType, setMfgPeriodType] = useState('quarterly');
  const [mfgMeasure, setMfgMeasure] = useState('productivity');
  const [mfgDuration, setMfgDuration] = useState('index');
  const [mfgYears, setMfgYears] = useState(20);
  const [mfgData, setMfgData] = useState<ManufacturingData | null>(null);
  const [mfgTimelineData, setMfgTimelineData] = useState<ManufacturingTimelineData | null>(null);
  const [loadingMfg, setLoadingMfg] = useState(false);
  const [loadingMfgTimeline, setLoadingMfgTimeline] = useState(false);
  const [mfgView, setMfgView] = useState<ViewType>('chart');
  const [mfgSelectedIndex, setMfgSelectedIndex] = useState<number | null>(null);

  // Section 5: Series Explorer
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [drillSectorCode, setDrillSectorCode] = useState('');
  const [drillClassCode, setDrillClassCode] = useState('');
  const [drillMeasureCode, setDrillMeasureCode] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);
  const [browseSectorCode, setBrowseSectorCode] = useState('');
  const [browseDurationCode, setBrowseDurationCode] = useState('');
  const [browseSeasonal, setBrowseSeasonal] = useState('');
  const [browseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<Record<string, SeriesDataResponse>>({});
  const [allSeriesInfo, setAllSeriesInfo] = useState<Record<string, SeriesInfo>>({});
  const [seriesTimeRange, setSeriesTimeRange] = useState(0);
  const [seriesPeriodType, setSeriesPeriodType] = useState('quarterly');
  const [seriesView, setSeriesView] = useState<ViewType>('chart');

  // Dropdown options from dimensions
  const [sectorOptions, setSectorOptions] = useState<SelectOption[]>([]);
  const [measureDimOptions, setMeasureDimOptions] = useState<SelectOption[]>([]);
  const [durationDimOptions, setDurationDimOptions] = useState<SelectOption[]>([]);

  // ============================================================================
  // DATA FETCHING
  // ============================================================================

  // Load dimensions on mount
  useEffect(() => {
    const fetchDimensions = async () => {
      try {
        const res = await prResearchAPI.getDimensions<DimensionsData>();
        setDimensions(res.data);
        setSectorOptions([
          { value: '', label: 'All' },
          ...res.data.sectors.map((s) => ({ value: s.sector_code, label: s.sector_name })),
        ]);
        setMeasureDimOptions([
          { value: '', label: 'All' },
          ...res.data.measures.map((m) => ({ value: m.measure_code, label: m.measure_text })),
        ]);
        setDurationDimOptions([
          { value: '', label: 'All' },
          ...res.data.durations.map((d) => ({ value: d.duration_code, label: d.duration_text })),
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
        const res = await prResearchAPI.getOverview<OverviewData>(overviewClass, overviewPeriodType);
        setOverviewData(res.data);
      } catch (err) {
        console.error('Failed to load overview:', err);
      } finally {
        setLoadingOverview(false);
      }
    };
    fetchOverview();
  }, [overviewClass, overviewPeriodType]);

  useEffect(() => {
    const fetchOverviewTimeline = async () => {
      setLoadingOverviewTimeline(true);
      try {
        const res = await prResearchAPI.getOverviewTimeline<OverviewTimelineData>(
          overviewMeasure, overviewDuration, overviewClass, overviewPeriodType, overviewYears
        );
        setOverviewTimelineData(res.data);
        if (res.data?.timeline?.length > 0) {
          setOverviewSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (err) {
        console.error('Failed to load overview timeline:', err);
      } finally {
        setLoadingOverviewTimeline(false);
      }
    };
    fetchOverviewTimeline();
  }, [overviewMeasure, overviewDuration, overviewClass, overviewPeriodType, overviewYears]);

  // Section 2: Sector Analysis
  useEffect(() => {
    const fetchAnalysis = async () => {
      setLoadingAnalysis(true);
      try {
        const res = await prResearchAPI.getSectorAnalysis<SectorAnalysisData>(analysisSector, analysisClass, analysisPeriodType);
        setAnalysisData(res.data);
      } catch (err) {
        console.error('Failed to load sector analysis:', err);
      } finally {
        setLoadingAnalysis(false);
      }
    };
    if (analysisSector) fetchAnalysis();
  }, [analysisSector, analysisClass, analysisPeriodType]);

  useEffect(() => {
    const fetchAnalysisTimeline = async () => {
      setLoadingAnalysisTimeline(true);
      try {
        const res = await prResearchAPI.getSectorTimeline<MeasureTimelineData>(
          analysisSector, analysisDuration, analysisClass, analysisPeriodType,
          selectedMeasureCodes.join(','), analysisYears
        );
        setAnalysisTimelineData(res.data);
        if (res.data?.timeline?.length > 0) {
          setAnalysisSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (err) {
        console.error('Failed to load sector timeline:', err);
      } finally {
        setLoadingAnalysisTimeline(false);
      }
    };
    if (analysisSector && selectedMeasureCodes.length > 0) fetchAnalysisTimeline();
  }, [analysisSector, analysisDuration, analysisClass, analysisPeriodType, selectedMeasureCodes, analysisYears]);

  // Section 3: Productivity vs Costs
  useEffect(() => {
    const fetchPvc = async () => {
      setLoadingPvc(true);
      try {
        const res = await prResearchAPI.getProductivityVsCosts<ProductivityVsCostsData>(pvcClass, pvcPeriodType);
        setPvcData(res.data);
      } catch (err) {
        console.error('Failed to load productivity vs costs:', err);
      } finally {
        setLoadingPvc(false);
      }
    };
    fetchPvc();
  }, [pvcClass, pvcPeriodType]);

  useEffect(() => {
    const fetchPvcTimeline = async () => {
      setLoadingPvcTimeline(true);
      try {
        const res = await prResearchAPI.getProductivityVsCostsTimeline<ProductivityVsCostsTimelineData>(
          pvcSector, pvcDuration, pvcClass, pvcPeriodType, pvcYears
        );
        setPvcTimelineData(res.data);
        if (res.data?.timeline?.length > 0) {
          setPvcSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (err) {
        console.error('Failed to load PvC timeline:', err);
      } finally {
        setLoadingPvcTimeline(false);
      }
    };
    fetchPvcTimeline();
  }, [pvcSector, pvcDuration, pvcClass, pvcPeriodType, pvcYears]);

  // Section 4: Manufacturing
  useEffect(() => {
    const fetchMfg = async () => {
      setLoadingMfg(true);
      try {
        const res = await prResearchAPI.getManufacturing<ManufacturingData>(mfgClass, mfgPeriodType);
        setMfgData(res.data);
      } catch (err) {
        console.error('Failed to load manufacturing:', err);
      } finally {
        setLoadingMfg(false);
      }
    };
    fetchMfg();
  }, [mfgClass, mfgPeriodType]);

  useEffect(() => {
    const fetchMfgTimeline = async () => {
      setLoadingMfgTimeline(true);
      try {
        const res = await prResearchAPI.getManufacturingTimeline<ManufacturingTimelineData>(
          mfgMeasure, mfgDuration, mfgClass, mfgPeriodType, mfgYears
        );
        setMfgTimelineData(res.data);
        if (res.data?.timeline?.length > 0) {
          setMfgSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (err) {
        console.error('Failed to load manufacturing timeline:', err);
      } finally {
        setLoadingMfgTimeline(false);
      }
    };
    fetchMfgTimeline();
  }, [mfgMeasure, mfgDuration, mfgClass, mfgPeriodType, mfgYears]);

  // Fetch series data when selection changes
  useEffect(() => {
    const fetchSeriesData = async () => {
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const res = await prResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, seriesTimeRange, seriesPeriodType);
            setSeriesChartData((prev) => ({ ...prev, [seriesId]: res.data }));
          } catch (err) {
            console.error(`Failed to load series ${seriesId}:`, err);
          }
        }
      }
    };
    if (selectedSeriesIds.length > 0) fetchSeriesData();
  }, [selectedSeriesIds, seriesTimeRange, seriesPeriodType]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await prResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 50 });
      setSearchResults(res.data);
      const newInfo: Record<string, SeriesInfo> = {};
      res.data.series.forEach((s) => { newInfo[s.series_id] = s; });
      setAllSeriesInfo((prev) => ({ ...prev, ...newInfo }));
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoadingSearch(false);
    }
  };

  const handleDrill = async () => {
    setLoadingDrill(true);
    try {
      const params: Record<string, unknown> = { limit: 50 };
      if (drillSectorCode) params.sector_code = drillSectorCode;
      if (drillClassCode) params.class_code = drillClassCode;
      if (drillMeasureCode) params.measure_code = drillMeasureCode;
      const res = await prResearchAPI.getSeries<SeriesListData>(params);
      setDrillResults(res.data);
      const newInfo: Record<string, SeriesInfo> = {};
      res.data.series.forEach((s) => { newInfo[s.series_id] = s; });
      setAllSeriesInfo((prev) => ({ ...prev, ...newInfo }));
    } catch (err) {
      console.error('Drill-down failed:', err);
    } finally {
      setLoadingDrill(false);
    }
  };

  const handleBrowse = async (newOffset = 0) => {
    setLoadingBrowse(true);
    setBrowseOffset(newOffset);
    try {
      const params: Record<string, unknown> = { limit: browseLimit, offset: newOffset };
      if (browseSectorCode) params.sector_code = browseSectorCode;
      if (browseDurationCode) params.duration_code = browseDurationCode;
      if (browseSeasonal) params.seasonal = browseSeasonal;
      const res = await prResearchAPI.getSeries<SeriesListData>(params);
      setBrowseResults(res.data);
      const newInfo: Record<string, SeriesInfo> = {};
      res.data.series.forEach((s) => { newInfo[s.series_id] = s; });
      setAllSeriesInfo((prev) => ({ ...prev, ...newInfo }));
    } catch (err) {
      console.error('Browse failed:', err);
    } finally {
      setLoadingBrowse(false);
    }
  };

  const toggleSeriesSelection = (seriesId: string) => {
    setSelectedSeriesIds((prev) =>
      prev.includes(seriesId) ? prev.filter((id) => id !== seriesId) : [...prev, seriesId]
    );
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
  };

  const toggleMeasureCode = (code: string) => {
    setSelectedMeasureCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const formatNumber = (val: number | null, decimals = 1): string => {
    if (val == null) return 'N/A';
    return val.toFixed(decimals);
  };

  const formatChange = (val: number | null): string => {
    if (val == null) return 'N/A';
    return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
  };

  const getPeriodLabel = (): string => {
    if (overviewData?.latest_period?.startsWith('Q0')) {
      const q = overviewData.latest_period.replace('Q0', 'Q');
      return `${q} ${overviewData.latest_year}`;
    }
    return overviewData?.latest_period === 'Q05' ? `Annual ${overviewData.latest_year}` : `${overviewData?.latest_period} ${overviewData?.latest_year}`;
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  if (loadingDimensions) {
    return <div className="p-6"><LoadingSpinner /></div>;
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Major Sector Productivity and Costs (PR)</h1>
          <p className="text-sm text-gray-600 mt-1">
            Quarterly productivity and cost measures for business and manufacturing sectors (1947-present)
          </p>
        </div>
      </div>

      {/* Section 1: Overview */}
      <Card>
        <SectionHeader title="Productivity Overview" color="blue" icon={Activity} />
        <div className="p-5">
          {/* Controls - ALL controls in one row including ViewToggle */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select label="Worker Class" value={overviewClass} onChange={setOverviewClass} options={classOptions} className="w-40" />
            <Select label="Period Type" value={overviewPeriodType} onChange={setOverviewPeriodType} options={periodTypeOptions} className="w-32" />
            <Select label="Measure" value={overviewMeasure} onChange={setOverviewMeasure} options={measureOptions} className="w-44" />
            <Select label="Duration" value={overviewDuration} onChange={setOverviewDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={overviewYears} onChange={(v) => setOverviewYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={overviewView} onChange={setOverviewView} />
          </div>

          {loadingOverview || loadingOverviewTimeline ? (
            <LoadingSpinner />
          ) : overviewView === 'chart' ? (
            <>
              {/* Headline Metrics - shows selected timeline point or latest */}
              <div className="mb-6">
                <div className="text-sm text-gray-500 mb-3">
                  {overviewSelectedIndex !== null && overviewTimelineData?.timeline?.[overviewSelectedIndex]
                    ? `Selected: ${overviewTimelineData.timeline[overviewSelectedIndex].period_name}`
                    : `Latest: ${getPeriodLabel()}`}
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  {overviewSelectedIndex !== null && overviewTimelineData?.timeline?.[overviewSelectedIndex]
                    ? /* Show data from selected timeline point */
                      Object.entries(overviewTimelineData.sector_names).slice(0, 6).map(([code, name]) => {
                        const timelinePoint = overviewTimelineData.timeline[overviewSelectedIndex];
                        const value = timelinePoint?.sectors?.[code];
                        return (
                          <MetricCard
                            key={code}
                            title={name}
                            value={formatNumber(value)}
                            subtitle="Productivity Index"
                            icon={<Activity className="w-5 h-5 text-blue-400" />}
                          />
                        );
                      })
                    : /* Show latest data from overview endpoint */
                      overviewData?.sectors?.slice(0, 6).map((sector) => (
                        <MetricCard
                          key={sector.sector_code}
                          title={sector.sector_name}
                          value={formatNumber(sector.labor_productivity_index)}
                          subtitle="Productivity Index"
                          change={sector.labor_productivity_change}
                          changeLabel="YoY"
                          icon={<Activity className="w-5 h-5 text-blue-400" />}
                        />
                      ))
                  }
                </div>
              </div>

              {/* Timeline Chart */}
              {overviewTimelineData?.timeline && overviewTimelineData.timeline.length > 0 && (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={overviewTimelineData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period_name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    {Object.keys(overviewTimelineData.sector_names).map((code, idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={`sectors.${code}`}
                        name={overviewTimelineData.sector_names[code]}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        dot={false}
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              )}

              {/* Timeline Selector */}
              {overviewTimelineData?.timeline && overviewTimelineData.timeline.length > 0 && (
                <TimelineSelector
                  timeline={overviewTimelineData.timeline}
                  selectedIndex={overviewSelectedIndex}
                  onSelectIndex={setOverviewSelectedIndex}
                />
              )}
            </>
          ) : (
            /* Table View */
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Sector</th>
                    <th className="px-4 py-2 text-right">Productivity</th>
                    <th className="px-4 py-2 text-right">YoY %</th>
                    <th className="px-4 py-2 text-right">Unit Labor Costs</th>
                    <th className="px-4 py-2 text-right">ULC YoY %</th>
                    <th className="px-4 py-2 text-right">Output</th>
                    <th className="px-4 py-2 text-right">Compensation</th>
                  </tr>
                </thead>
                <tbody>
                  {overviewData?.sectors?.map((sector) => (
                    <tr key={sector.sector_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{sector.sector_name}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(sector.labor_productivity_index)}</td>
                      <td className={`px-4 py-2 text-right ${(sector.labor_productivity_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(sector.labor_productivity_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(sector.unit_labor_costs_index)}</td>
                      <td className={`px-4 py-2 text-right ${(sector.unit_labor_costs_change ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatChange(sector.unit_labor_costs_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(sector.output_index)}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(sector.compensation_index)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Section 2: Sector Analysis */}
      <Card>
        <SectionHeader title="Sector Analysis" color="green" icon={Building2} />
        <div className="p-5">
          {/* Controls - ALL controls in one row including ViewToggle */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select
              label="Sector"
              value={analysisSector}
              onChange={setAnalysisSector}
              options={dimensions?.sectors.map((s) => ({ value: s.sector_code, label: s.sector_name })) || []}
              className="w-52"
            />
            <Select label="Worker Class" value={analysisClass} onChange={setAnalysisClass} options={classOptions} className="w-40" />
            <Select label="Period Type" value={analysisPeriodType} onChange={setAnalysisPeriodType} options={periodTypeOptions} className="w-32" />
            <Select label="Duration" value={analysisDuration} onChange={setAnalysisDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={analysisYears} onChange={(v) => setAnalysisYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={analysisView} onChange={setAnalysisView} />
          </div>

          {/* Measure selection */}
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">Select measures to compare:</p>
            <div className="flex flex-wrap gap-2">
              {dimensions?.measures.slice(0, 12).map((m) => (
                <button
                  key={m.measure_code}
                  onClick={() => toggleMeasureCode(m.measure_code)}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedMeasureCodes.includes(m.measure_code)
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {m.measure_text.substring(0, 25)}
                </button>
              ))}
            </div>
          </div>

          {loadingAnalysis || loadingAnalysisTimeline ? (
            <LoadingSpinner />
          ) : analysisView === 'chart' ? (
            /* Chart View - Timeline */
            <>
              {/* Selected period info */}
              {analysisSelectedIndex !== null && analysisTimelineData?.timeline?.[analysisSelectedIndex] && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div className="text-sm font-medium text-blue-800 mb-2">
                    Selected: {analysisTimelineData.timeline[analysisSelectedIndex].period_name}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {selectedMeasureCodes.map((code) => {
                      const value = analysisTimelineData.timeline[analysisSelectedIndex]?.measures?.[code];
                      return (
                        <div key={code} className="text-xs">
                          <span className="text-gray-600">{analysisTimelineData.measure_names[code] || code}: </span>
                          <span className="font-semibold text-gray-900">{formatNumber(value)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              {analysisTimelineData?.timeline && analysisTimelineData.timeline.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={analysisTimelineData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period_name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    {selectedMeasureCodes.map((code, idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={`measures.${code}`}
                        name={analysisTimelineData.measure_names[code] || code}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        dot={false}
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-500 text-center py-8">No timeline data available</div>
              )}
              {analysisTimelineData?.timeline && analysisTimelineData.timeline.length > 0 && (
                <TimelineSelector
                  timeline={analysisTimelineData.timeline}
                  selectedIndex={analysisSelectedIndex}
                  onSelectIndex={setAnalysisSelectedIndex}
                />
              )}
            </>
          ) : (
            /* Table View */
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Measure</th>
                    <th className="px-4 py-2 text-right">Index</th>
                    <th className="px-4 py-2 text-right">YoY %</th>
                    <th className="px-4 py-2 text-right">QoQ %</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisData?.measures?.map((m) => (
                    <tr key={m.measure_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2">{m.measure_text}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(m.index_value)}</td>
                      <td className={`px-4 py-2 text-right ${(m.yoy_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(m.yoy_change)}
                      </td>
                      <td className={`px-4 py-2 text-right ${(m.qoq_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(m.qoq_change)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Section 3: Productivity vs Costs */}
      <Card>
        <SectionHeader title="Productivity vs Labor Costs" color="purple" icon={Users} />
        <div className="p-5">
          {/* Controls - ALL controls in one row including ViewToggle */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select label="Worker Class" value={pvcClass} onChange={setPvcClass} options={classOptions} className="w-40" />
            <Select label="Period Type" value={pvcPeriodType} onChange={setPvcPeriodType} options={periodTypeOptions} className="w-32" />
            <Select
              label="Sector (for timeline)"
              value={pvcSector}
              onChange={setPvcSector}
              options={dimensions?.sectors.map((s) => ({ value: s.sector_code, label: s.sector_name })) || []}
              className="w-52"
            />
            <Select label="Duration" value={pvcDuration} onChange={setPvcDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={pvcYears} onChange={(v) => setPvcYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={pvcView} onChange={setPvcView} />
          </div>

          {loadingPvc || loadingPvcTimeline ? (
            <LoadingSpinner />
          ) : pvcView === 'chart' ? (
            /* Chart View - Timeline */
            <>
              {/* Selected period info */}
              {pvcSelectedIndex !== null && pvcTimelineData?.timeline?.[pvcSelectedIndex] && (
                <div className="mb-4 p-3 bg-purple-50 rounded-lg">
                  <div className="text-sm font-medium text-purple-800 mb-2">
                    Selected: {pvcTimelineData.timeline[pvcSelectedIndex].period_name}
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-xs text-gray-600">Productivity</div>
                      <div className="text-lg font-bold text-blue-600">{formatNumber(pvcTimelineData.timeline[pvcSelectedIndex].productivity)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-gray-600">Unit Labor Costs</div>
                      <div className="text-lg font-bold text-red-600">{formatNumber(pvcTimelineData.timeline[pvcSelectedIndex].unit_labor_costs)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-gray-600">Compensation</div>
                      <div className="text-lg font-bold text-green-600">{formatNumber(pvcTimelineData.timeline[pvcSelectedIndex].hourly_compensation)}</div>
                    </div>
                  </div>
                </div>
              )}
              {pvcTimelineData?.timeline && pvcTimelineData.timeline.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={pvcTimelineData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period_name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="productivity" name="Productivity" stroke="#3b82f6" dot={false} strokeWidth={2} />
                    <Line type="monotone" dataKey="unit_labor_costs" name="Unit Labor Costs" stroke="#ef4444" dot={false} strokeWidth={2} />
                    <Line type="monotone" dataKey="hourly_compensation" name="Compensation" stroke="#10b981" dot={false} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-500 text-center py-8">No timeline data available</div>
              )}
              {pvcTimelineData?.timeline && pvcTimelineData.timeline.length > 0 && (
                <TimelineSelector
                  timeline={pvcTimelineData.timeline}
                  selectedIndex={pvcSelectedIndex}
                  onSelectIndex={setPvcSelectedIndex}
                />
              )}
            </>
          ) : (
            /* Table View */
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Sector</th>
                    <th className="px-4 py-2 text-right">Productivity</th>
                    <th className="px-4 py-2 text-right">Prod. YoY %</th>
                    <th className="px-4 py-2 text-right">Unit Labor Costs</th>
                    <th className="px-4 py-2 text-right">ULC YoY %</th>
                    <th className="px-4 py-2 text-right">Compensation</th>
                    <th className="px-4 py-2 text-right">Comp. YoY %</th>
                  </tr>
                </thead>
                <tbody>
                  {pvcData?.analysis?.map((row) => (
                    <tr key={row.sector_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{row.sector_name}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.productivity_index)}</td>
                      <td className={`px-4 py-2 text-right ${(row.productivity_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(row.productivity_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.unit_labor_costs_index)}</td>
                      <td className={`px-4 py-2 text-right ${(row.unit_labor_costs_change ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatChange(row.unit_labor_costs_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.hourly_compensation_index)}</td>
                      <td className={`px-4 py-2 text-right ${(row.hourly_compensation_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(row.hourly_compensation_change)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Section 4: Manufacturing Comparison */}
      <Card>
        <SectionHeader title="Manufacturing Comparison" color="orange" icon={Factory} />
        <div className="p-5">
          {/* Controls - ALL controls in one row including ViewToggle */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select label="Worker Class" value={mfgClass} onChange={setMfgClass} options={classOptions} className="w-40" />
            <Select label="Period Type" value={mfgPeriodType} onChange={setMfgPeriodType} options={periodTypeOptions} className="w-32" />
            <Select label="Measure" value={mfgMeasure} onChange={setMfgMeasure} options={manufacturingMeasureOptions} className="w-44" />
            <Select label="Duration" value={mfgDuration} onChange={setMfgDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={mfgYears} onChange={(v) => setMfgYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={mfgView} onChange={setMfgView} />
          </div>

          {loadingMfg || loadingMfgTimeline ? (
            <LoadingSpinner />
          ) : mfgView === 'chart' ? (
            /* Chart View - Timeline */
            <>
              {/* Selected period info */}
              {mfgSelectedIndex !== null && mfgTimelineData?.timeline?.[mfgSelectedIndex] && (
                <div className="mb-4 p-3 bg-orange-50 rounded-lg">
                  <div className="text-sm font-medium text-orange-800 mb-2">
                    Selected: {mfgTimelineData.timeline[mfgSelectedIndex].period_name}
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    {Object.entries(mfgTimelineData.sector_names).map(([code, name], idx) => {
                      const value = mfgTimelineData.timeline[mfgSelectedIndex]?.sectors?.[code];
                      return (
                        <div key={code} className="text-center">
                          <div className="text-xs text-gray-600">{name}</div>
                          <div className="text-lg font-bold" style={{ color: CHART_COLORS[idx % CHART_COLORS.length] }}>
                            {formatNumber(value)}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
              {mfgTimelineData?.timeline && mfgTimelineData.timeline.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={mfgTimelineData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period_name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    {Object.keys(mfgTimelineData.sector_names).map((code, idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={`sectors.${code}`}
                        name={mfgTimelineData.sector_names[code]}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        dot={false}
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-500 text-center py-8">No timeline data available</div>
              )}
              {mfgTimelineData?.timeline && mfgTimelineData.timeline.length > 0 && (
                <TimelineSelector
                  timeline={mfgTimelineData.timeline}
                  selectedIndex={mfgSelectedIndex}
                  onSelectIndex={setMfgSelectedIndex}
                />
              )}
            </>
          ) : (
            /* Table View */
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Sector</th>
                    <th className="px-4 py-2 text-right">Productivity</th>
                    <th className="px-4 py-2 text-right">Prod. YoY %</th>
                    <th className="px-4 py-2 text-right">Unit Labor Costs</th>
                    <th className="px-4 py-2 text-right">ULC YoY %</th>
                    <th className="px-4 py-2 text-right">Output</th>
                    <th className="px-4 py-2 text-right">Output YoY %</th>
                  </tr>
                </thead>
                <tbody>
                  {mfgData?.manufacturing_sectors?.map((row) => (
                    <tr key={row.sector_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{row.sector_name}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.productivity_index)}</td>
                      <td className={`px-4 py-2 text-right ${(row.productivity_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(row.productivity_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.unit_labor_costs_index)}</td>
                      <td className={`px-4 py-2 text-right ${(row.unit_labor_costs_change ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatChange(row.unit_labor_costs_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.output_index)}</td>
                      <td className={`px-4 py-2 text-right ${(row.output_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(row.output_change)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Section 5: Series Explorer */}
      <Card>
        <SectionHeader title="Series Explorer" color="cyan" icon={Briefcase} />
        <div className="p-5">
          {/* Three methods: Search, Drill-down, Browse */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Search */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-800 mb-3">Search</h4>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Search series by ID or keywords..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleSearch}
                  disabled={loadingSearch}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:opacity-50"
                >
                  {loadingSearch ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
                </button>
              </div>
              {searchResults && <div className="mt-3 text-sm text-gray-600">Found {searchResults.total} series</div>}
            </div>

            {/* Drill-down */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-800 mb-3">Drill-down</h4>
              <div className="space-y-2">
                <Select label="Sector" value={drillSectorCode} onChange={setDrillSectorCode} options={sectorOptions} className="w-full" />
                <Select label="Worker Class" value={drillClassCode} onChange={setDrillClassCode} options={[{ value: '', label: 'All' }, ...classOptions]} className="w-full" />
                <Select label="Measure" value={drillMeasureCode} onChange={setDrillMeasureCode} options={measureDimOptions} className="w-full" />
                <button onClick={handleDrill} disabled={loadingDrill} className="w-full px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50">
                  {loadingDrill ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Apply Filters'}
                </button>
              </div>
              {drillResults && <div className="mt-3 text-sm text-gray-600">Found {drillResults.total} series</div>}
            </div>

            {/* Browse */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-800 mb-3">Browse</h4>
              <div className="space-y-2">
                <Select label="Sector" value={browseSectorCode} onChange={setBrowseSectorCode} options={sectorOptions} className="w-full" />
                <Select label="Duration" value={browseDurationCode} onChange={setBrowseDurationCode} options={durationDimOptions} className="w-full" />
                <Select label="Seasonal" value={browseSeasonal} onChange={setBrowseSeasonal} options={[{ value: '', label: 'All' }, { value: 'S', label: 'Seasonally Adjusted' }, { value: 'U', label: 'Not Adjusted' }]} className="w-full" />
                <button onClick={() => handleBrowse(0)} disabled={loadingBrowse} className="w-full px-4 py-2 bg-purple-600 text-white rounded-md text-sm hover:bg-purple-700 disabled:opacity-50">
                  {loadingBrowse ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Browse'}
                </button>
              </div>
              {browseResults && <div className="mt-3 text-sm text-gray-600">Showing {browseResults.series.length} of {browseResults.total} series</div>}
            </div>
          </div>

          {/* Results List */}
          {(searchResults || drillResults || browseResults) && (
            <div className="mt-6">
              <h4 className="font-medium text-gray-800 mb-3">Results</h4>
              <div className="overflow-x-auto max-h-64 border rounded-lg">
                <table className="min-w-full text-sm">
                  <thead className="sticky top-0 bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left w-8"></th>
                      <th className="px-3 py-2 text-left">Series ID</th>
                      <th className="px-3 py-2 text-left">Sector</th>
                      <th className="px-3 py-2 text-left">Measure</th>
                      <th className="px-3 py-2 text-left">Duration</th>
                      <th className="px-3 py-2 text-left">Period</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(searchResults?.series || drillResults?.series || browseResults?.series || []).map((s) => (
                      <tr key={s.series_id} className="border-t hover:bg-gray-50">
                        <td className="px-3 py-2">
                          <input
                            type="checkbox"
                            checked={selectedSeriesIds.includes(s.series_id)}
                            onChange={() => toggleSeriesSelection(s.series_id)}
                            className="rounded"
                          />
                        </td>
                        <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                        <td className="px-3 py-2">{s.sector_name}</td>
                        <td className="px-3 py-2">{s.measure_text}</td>
                        <td className="px-3 py-2">{s.duration_text}</td>
                        <td className="px-3 py-2">{s.begin_year}-{s.end_year}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination for Browse */}
              {browseResults && browseResults.total > browseLimit && (
                <div className="flex justify-center gap-2 mt-4">
                  <button onClick={() => handleBrowse(browseOffset - browseLimit)} disabled={browseOffset === 0} className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50">Previous</button>
                  <span className="px-3 py-1 text-sm text-gray-600">{browseOffset + 1} - {Math.min(browseOffset + browseLimit, browseResults.total)} of {browseResults.total}</span>
                  <button onClick={() => handleBrowse(browseOffset + browseLimit)} disabled={browseOffset + browseLimit >= browseResults.total} className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50">Next</button>
                </div>
              )}
            </div>
          )}

          {/* Selected Series Chart */}
          {selectedSeriesIds.length > 0 && (
            <div className="mt-6 pt-6 border-t">
              <div className="flex flex-wrap justify-between items-end gap-4 mb-4">
                <h4 className="font-medium text-gray-800">Selected Series ({selectedSeriesIds.length})</h4>
                <div className="flex flex-wrap gap-4 items-end">
                  <Select label="Time Range" value={seriesTimeRange} onChange={(v) => { setSeriesTimeRange(Number(v)); setSeriesChartData({}); }} options={timeRangeOptions} className="w-36" />
                  <Select label="Period Type" value={seriesPeriodType} onChange={(v) => { setSeriesPeriodType(v); setSeriesChartData({}); }} options={periodTypeOptions} className="w-32" />
                  <ViewToggle value={seriesView} onChange={setSeriesView} />
                  <button onClick={() => { setSelectedSeriesIds([]); setSeriesChartData({}); }} className="px-3 py-1.5 text-sm text-red-600 border border-red-300 rounded hover:bg-red-50">Clear All</button>
                </div>
              </div>

              {/* Series Legend */}
              <div className="flex flex-wrap gap-2 mb-4">
                {selectedSeriesIds.map((id, idx) => {
                  const info = allSeriesInfo[id];
                  return (
                    <div key={id} className="flex items-center gap-2 px-2 py-1 bg-gray-100 rounded text-xs">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                      <span className="font-mono">{id}</span>
                      {info && <span className="text-gray-500">({info.measure_text?.substring(0, 20)})</span>}
                      <button onClick={() => toggleSeriesSelection(id)} className="text-red-500 hover:text-red-700">x</button>
                    </div>
                  );
                })}
              </div>

              {seriesView === 'chart' ? (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period_name" type="category" allowDuplicatedCategory={false} tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    {selectedSeriesIds.map((seriesId, idx) => {
                      const data = seriesChartData[seriesId]?.series[0]?.data_points || [];
                      return (
                        <Line key={seriesId} data={data} type="monotone" dataKey="value" name={seriesId} stroke={CHART_COLORS[idx % CHART_COLORS.length]} dot={false} strokeWidth={2} />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="overflow-x-auto max-h-96">
                  <table className="min-w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left">Period</th>
                        {selectedSeriesIds.map((id) => (
                          <th key={id} className="px-3 py-2 text-right font-mono text-xs">{id}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(() => {
                        const allPeriods = new Map<string, Record<string, number | null>>();
                        selectedSeriesIds.forEach((id) => {
                          const points = seriesChartData[id]?.series[0]?.data_points || [];
                          points.forEach((p) => {
                            if (!allPeriods.has(p.period_name)) allPeriods.set(p.period_name, {});
                            allPeriods.get(p.period_name)![id] = p.value;
                          });
                        });
                        return Array.from(allPeriods.entries()).map(([period, values]) => (
                          <tr key={period} className="border-t">
                            <td className="px-3 py-2">{period}</td>
                            {selectedSeriesIds.map((id) => (
                              <td key={id} className="px-3 py-2 text-right">{formatNumber(values[id])}</td>
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
