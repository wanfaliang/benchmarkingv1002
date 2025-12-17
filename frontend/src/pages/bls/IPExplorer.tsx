import { useState, useEffect, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, BarChart, Bar
} from 'recharts';
import { Loader2, Activity, Building2, Factory, Briefcase, Award, LucideIcon } from 'lucide-react';
import { ipResearchAPI } from '../../services/api';

/**
 * IP Explorer - Industry Productivity Explorer
 *
 * Provides productivity and cost measures for 800+ industries:
 * - 21 sectors (Agriculture, Mining, Manufacturing, etc.)
 * - 800+ industries (NAICS classification)
 * - Labor productivity, unit labor costs, output, hours, employment
 * - Index values (2017=100) and annual percent changes
 *
 * Sections:
 * 1. Overview - Key metrics by sector
 * 2. Sector Analysis - Industries within a sector
 * 3. Industry Analysis - All measures for a specific industry
 * 4. Productivity vs Costs - Compare productivity with labor costs
 * 5. Top Rankings - Highest/lowest industries by measure
 * 6. Series Explorer - Search, drill-down, browse
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
  sector_text: string;
}

interface IndustryItem {
  industry_code: string;
  industry_text: string;
  naics_code: string | null;
  display_level: number | null;
  selectable: boolean | null;
}

interface MeasureItem {
  measure_code: string;
  measure_text: string;
  display_level: number | null;
  selectable: boolean | null;
}

interface DurationItem {
  duration_code: string;
  duration_text: string;
}

interface DimensionsData {
  sectors: SectorItem[];
  industries: IndustryItem[];
  measures: MeasureItem[];
  durations: DurationItem[];
}

interface SectorSummary {
  sector_code: string;
  sector_text: string;
  labor_productivity: number | null;
  labor_productivity_change: number | null;
  output: number | null;
  output_change: number | null;
  hours: number | null;
  hours_change: number | null;
  employment: number | null;
  employment_change: number | null;
  unit_labor_costs: number | null;
  ulc_change: number | null;
  industry_count: number;
}

interface OverviewData {
  year: number;
  sectors: SectorSummary[];
}

interface OverviewTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  sectors: Record<string, number | null>;
}

interface OverviewTimelineData {
  measure_code: string;
  measure_text: string;
  timeline: OverviewTimelinePoint[];
  sector_names: Record<string, string>;
}

interface IndustryMetric {
  industry_code: string;
  industry_text: string;
  naics_code: string | null;
  display_level: number | null;
  labor_productivity: number | null;
  labor_productivity_change: number | null;
  output: number | null;
  output_change: number | null;
  hours: number | null;
  hours_change: number | null;
  employment: number | null;
  employment_change: number | null;
}

interface SectorAnalysisData {
  sector_code: string;
  sector_text: string;
  year: number;
  industries: IndustryMetric[];
}

interface SectorTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  industries: Record<string, number | null>;
}

interface SectorTimelineData {
  sector_code: string;
  sector_text: string;
  measure_code: string;
  measure_text: string;
  timeline: SectorTimelinePoint[];
  industry_names: Record<string, string>;
}

interface MeasureValue {
  measure_code: string;
  measure_text: string;
  value: number | null;
  change: number | null;
}

interface IndustryAnalysisData {
  industry_code: string;
  industry_text: string;
  naics_code: string | null;
  sector_code: string;
  sector_text: string;
  year: number;
  measures: MeasureValue[];
}

interface IndustryTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  measures: Record<string, number | null>;
}

interface IndustryTimelineData {
  industry_code: string;
  industry_text: string;
  timeline: IndustryTimelinePoint[];
  measure_names: Record<string, string>;
}

interface ProductivityVsCostsMetric {
  industry_code: string;
  industry_text: string;
  naics_code: string | null;
  labor_productivity: number | null;
  productivity_change: number | null;
  unit_labor_costs: number | null;
  ulc_change: number | null;
  output: number | null;
  output_change: number | null;
  compensation: number | null;
  compensation_change: number | null;
}

interface ProductivityVsCostsData {
  sector_code: string | null;
  sector_text: string | null;
  year: number;
  industries: ProductivityVsCostsMetric[];
}

interface ProductivityVsCostsTimelinePoint {
  year: number;
  period: string;
  period_name: string;
  labor_productivity: number | null;
  unit_labor_costs: number | null;
  output: number | null;
  compensation: number | null;
}

interface ProductivityVsCostsTimelineData {
  industry_code: string;
  industry_text: string;
  timeline: ProductivityVsCostsTimelinePoint[];
}

interface TopIndustry {
  rank: number;
  industry_code: string;
  industry_text: string;
  naics_code: string | null;
  sector_code: string;
  sector_text: string;
  value: number | null;
  change: number | null;
}

interface TopRankingsData {
  measure_code: string;
  measure_text: string;
  ranking_type: string;
  year: number;
  industries: TopIndustry[];
}

interface SeriesInfo {
  series_id: string;
  seasonal: string | null;
  sector_code: string | null;
  sector_text: string | null;
  industry_code: string | null;
  industry_text: string | null;
  naics_code: string | null;
  measure_code: string | null;
  measure_text: string | null;
  duration_code: string | null;
  duration_text: string | null;
  begin_year: number | null;
  end_year: number | null;
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
    series_info: SeriesInfo;
    data: DataPoint[];
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
    amber: 'from-amber-600 to-amber-400',
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


interface TimelineSelectorProps {
  timeline: { year: number; period: string; period_name: string }[];
  selectedIndex: number | null;
  onSelectIndex: (index: number) => void;
}

const TimelineSelector = ({ timeline, selectedIndex, onSelectIndex }: TimelineSelectorProps): ReactElement | null => {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="mt-4 mb-2 px-2">
      <p className="text-xs text-gray-500 mb-2">Select year (click any point):</p>
      <div className="relative h-14">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-300" />
        <div className="relative flex justify-between">
          {timeline.map((point, index) => {
            const isSelected = selectedIndex === index;
            const isLatest = index === timeline.length - 1;
            const shouldShowLabel = index % Math.max(1, Math.floor(timeline.length / 10)) === 0 || index === timeline.length - 1;

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
                    {point.year}
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
  { value: 0, label: 'All Time' },
];

const measureOptions: SelectOption[] = [
  { value: 'L00', label: 'Labor Productivity' },
  { value: 'T01', label: 'Output' },
  { value: 'L01', label: 'Hours Worked' },
  { value: 'W01', label: 'Employment' },
  { value: 'U10', label: 'Unit Labor Costs' },
  { value: 'U11', label: 'Labor Compensation' },
];

const durationOptions: SelectOption[] = [
  { value: '0', label: 'Index (2017=100)' },
  { value: '1', label: '% Change YoY' },
];

const rankingTypeOptions: SelectOption[] = [
  { value: 'highest', label: 'Highest Value' },
  { value: 'lowest', label: 'Lowest Value' },
  { value: 'fastest_growing', label: 'Fastest Growing' },
  { value: 'fastest_declining', label: 'Fastest Declining' },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function IPExplorer() {
  // Dimensions data
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [loadingDimensions, setLoadingDimensions] = useState(true);

  // Section 1: Overview
  const [overviewMeasure, setOverviewMeasure] = useState('L00');
  const [overviewDuration, setOverviewDuration] = useState('0');
  const [overviewYears, setOverviewYears] = useState(20);
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [overviewTimelineData, setOverviewTimelineData] = useState<OverviewTimelineData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(false);
  const [loadingOverviewTimeline, setLoadingOverviewTimeline] = useState(false);
  const [overviewView, setOverviewView] = useState<ViewType>('chart');
  const [overviewSelectedIndex, setOverviewSelectedIndex] = useState<number | null>(null);

  // Section 2: Sector Analysis
  const [analysisSector, setAnalysisSector] = useState('C');
  const [analysisMeasure, setAnalysisMeasure] = useState('L00');
  const [analysisDuration, setAnalysisDuration] = useState('0');
  const [analysisYears, setAnalysisYears] = useState(20);
  const [analysisData, setAnalysisData] = useState<SectorAnalysisData | null>(null);
  const [analysisTimelineData, setAnalysisTimelineData] = useState<SectorTimelineData | null>(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [loadingAnalysisTimeline, setLoadingAnalysisTimeline] = useState(false);
  const [analysisView, setAnalysisView] = useState<ViewType>('chart');
  const [selectedIndustryCodes, setSelectedIndustryCodes] = useState<string[]>([]);
  const [analysisSelectedIndex, setAnalysisSelectedIndex] = useState<number | null>(null);

  // Section 3: Industry Analysis
  const [industryCode, setIndustryCode] = useState('');
  const [industryDuration, setIndustryDuration] = useState('0');
  const [industryYears, setIndustryYears] = useState(20);
  const [industryData, setIndustryData] = useState<IndustryAnalysisData | null>(null);
  const [industryTimelineData, setIndustryTimelineData] = useState<IndustryTimelineData | null>(null);
  const [loadingIndustry, setLoadingIndustry] = useState(false);
  const [loadingIndustryTimeline, setLoadingIndustryTimeline] = useState(false);
  const [industryView, setIndustryView] = useState<ViewType>('chart');
  const [selectedMeasureCodes, setSelectedMeasureCodes] = useState<string[]>(['L00', 'U10', 'T01']);
  const [industrySelectedIndex, setIndustrySelectedIndex] = useState<number | null>(null);

  // Section 4: Productivity vs Costs
  const [pvcSector, setPvcSector] = useState('');
  const [pvcYears, setPvcYears] = useState(20);
  const [pvcIndustry, setPvcIndustry] = useState('');
  const [pvcDuration, setPvcDuration] = useState('0');
  const [pvcData, setPvcData] = useState<ProductivityVsCostsData | null>(null);
  const [pvcTimelineData, setPvcTimelineData] = useState<ProductivityVsCostsTimelineData | null>(null);
  const [loadingPvc, setLoadingPvc] = useState(false);
  const [loadingPvcTimeline, setLoadingPvcTimeline] = useState(false);
  const [pvcView, setPvcView] = useState<ViewType>('chart');
  const [pvcSelectedIndex, setPvcSelectedIndex] = useState<number | null>(null);

  // Section 5: Top Rankings
  const [rankingMeasure, setRankingMeasure] = useState('L00');
  const [rankingType, setRankingType] = useState('highest');
  const [rankingLimit, setRankingLimit] = useState(20);
  const [rankingData, setRankingData] = useState<TopRankingsData | null>(null);
  const [loadingRanking, setLoadingRanking] = useState(false);

  // Section 6: Series Explorer
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [drillSectorCode, setDrillSectorCode] = useState('');
  const [drillMeasureCode, setDrillMeasureCode] = useState('');
  const [drillDurationCode, setDrillDurationCode] = useState('');
  const [drillResults, setDrillResults] = useState<SeriesListData | null>(null);
  const [loadingDrill, setLoadingDrill] = useState(false);
  const [browseIndustryCode, setBrowseIndustryCode] = useState('');
  const [browseMeasureCode, setBrowseMeasureCode] = useState('');
  const [browseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<Record<string, SeriesDataResponse>>({});
  const [allSeriesInfo, setAllSeriesInfo] = useState<Record<string, SeriesInfo>>({});
  const [seriesTimeRange, setSeriesTimeRange] = useState(0);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');

  // Dropdown options from dimensions
  const [sectorOptions, setSectorOptions] = useState<SelectOption[]>([]);
  const [industryOptions, setIndustryOptions] = useState<SelectOption[]>([]);
  const [measureDimOptions, setMeasureDimOptions] = useState<SelectOption[]>([]);
  const [durationDimOptions, setDurationDimOptions] = useState<SelectOption[]>([]);

  // ============================================================================
  // DATA FETCHING
  // ============================================================================

  // Load dimensions on mount
  useEffect(() => {
    const fetchDimensions = async () => {
      try {
        const res = await ipResearchAPI.getDimensions<DimensionsData>();
        setDimensions(res.data);
        setSectorOptions([
          { value: '', label: 'All Sectors' },
          ...res.data.sectors.map((s) => ({ value: s.sector_code, label: s.sector_text })),
        ]);
        setIndustryOptions([
          { value: '', label: 'Select Industry' },
          ...res.data.industries.slice(0, 100).map((i) => ({ value: i.industry_code, label: `${i.industry_text} (${i.naics_code || 'N/A'})` })),
        ]);
        setMeasureDimOptions([
          { value: '', label: 'All' },
          ...res.data.measures.filter(m => m.selectable).map((m) => ({ value: m.measure_code, label: m.measure_text })),
        ]);
        setDurationDimOptions([
          { value: '', label: 'All' },
          ...res.data.durations.map((d) => ({ value: d.duration_code, label: d.duration_text })),
        ]);
        // Set default industry for Section 3
        if (res.data.industries.length > 0) {
          setIndustryCode(res.data.industries[0].industry_code);
        }
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
        const res = await ipResearchAPI.getOverview<OverviewData>();
        setOverviewData(res.data);
      } catch (err) {
        console.error('Failed to load overview:', err);
      } finally {
        setLoadingOverview(false);
      }
    };
    fetchOverview();
  }, []);

  useEffect(() => {
    const fetchOverviewTimeline = async () => {
      setLoadingOverviewTimeline(true);
      try {
        const startYear = overviewYears > 0 ? new Date().getFullYear() - overviewYears : undefined;
        const res = await ipResearchAPI.getOverviewTimeline<OverviewTimelineData>(
          overviewMeasure, overviewDuration, startYear
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
  }, [overviewMeasure, overviewDuration, overviewYears]);

  // Section 2: Sector Analysis
  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!analysisSector) return;
      setLoadingAnalysis(true);
      try {
        const res = await ipResearchAPI.getSectorAnalysis<SectorAnalysisData>(analysisSector);
        setAnalysisData(res.data);
        // Auto-select first 3 industries for timeline
        if (res.data?.industries?.length > 0 && selectedIndustryCodes.length === 0) {
          setSelectedIndustryCodes(res.data.industries.slice(0, 3).map(i => i.industry_code));
        }
      } catch (err) {
        console.error('Failed to load sector analysis:', err);
      } finally {
        setLoadingAnalysis(false);
      }
    };
    fetchAnalysis();
  }, [analysisSector]);

  useEffect(() => {
    const fetchAnalysisTimeline = async () => {
      if (!analysisSector || selectedIndustryCodes.length === 0) return;
      setLoadingAnalysisTimeline(true);
      try {
        const startYear = analysisYears > 0 ? new Date().getFullYear() - analysisYears : undefined;
        const res = await ipResearchAPI.getSectorTimeline<SectorTimelineData>(
          analysisSector, analysisMeasure, analysisDuration, selectedIndustryCodes.join(','), startYear
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
    fetchAnalysisTimeline();
  }, [analysisSector, analysisMeasure, analysisDuration, selectedIndustryCodes, analysisYears]);

  // Section 3: Industry Analysis
  useEffect(() => {
    const fetchIndustry = async () => {
      if (!industryCode) return;
      setLoadingIndustry(true);
      try {
        const res = await ipResearchAPI.getIndustryAnalysis<IndustryAnalysisData>(industryCode);
        setIndustryData(res.data);
      } catch (err) {
        console.error('Failed to load industry analysis:', err);
      } finally {
        setLoadingIndustry(false);
      }
    };
    fetchIndustry();
  }, [industryCode]);

  useEffect(() => {
    const fetchIndustryTimeline = async () => {
      if (!industryCode || selectedMeasureCodes.length === 0) return;
      setLoadingIndustryTimeline(true);
      try {
        const startYear = industryYears > 0 ? new Date().getFullYear() - industryYears : undefined;
        const res = await ipResearchAPI.getIndustryTimeline<IndustryTimelineData>(
          industryCode, industryDuration, selectedMeasureCodes.join(','), startYear
        );
        setIndustryTimelineData(res.data);
        if (res.data?.timeline?.length > 0) {
          setIndustrySelectedIndex(res.data.timeline.length - 1);
        }
      } catch (err) {
        console.error('Failed to load industry timeline:', err);
      } finally {
        setLoadingIndustryTimeline(false);
      }
    };
    fetchIndustryTimeline();
  }, [industryCode, industryDuration, selectedMeasureCodes, industryYears]);

  // Section 4: Productivity vs Costs
  useEffect(() => {
    const fetchPvc = async () => {
      setLoadingPvc(true);
      try {
        const res = await ipResearchAPI.getProductivityVsCosts<ProductivityVsCostsData>(
          pvcSector || null
        );
        setPvcData(res.data);
        // Set default industry for timeline
        if (res.data?.industries?.length > 0 && !pvcIndustry) {
          setPvcIndustry(res.data.industries[0].industry_code);
        }
      } catch (err) {
        console.error('Failed to load productivity vs costs:', err);
      } finally {
        setLoadingPvc(false);
      }
    };
    fetchPvc();
  }, [pvcSector]);

  useEffect(() => {
    const fetchPvcTimeline = async () => {
      if (!pvcIndustry) return;
      setLoadingPvcTimeline(true);
      try {
        const startYear = pvcYears > 0 ? new Date().getFullYear() - pvcYears : undefined;
        const res = await ipResearchAPI.getProductivityVsCostsTimeline<ProductivityVsCostsTimelineData>(
          pvcIndustry, pvcDuration, startYear
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
  }, [pvcIndustry, pvcDuration, pvcYears]);

  // Section 5: Top Rankings
  useEffect(() => {
    const fetchRankings = async () => {
      setLoadingRanking(true);
      try {
        const res = await ipResearchAPI.getTopRankings<TopRankingsData>(
          rankingMeasure, rankingType, undefined, rankingLimit
        );
        setRankingData(res.data);
      } catch (err) {
        console.error('Failed to load rankings:', err);
      } finally {
        setLoadingRanking(false);
      }
    };
    fetchRankings();
  }, [rankingMeasure, rankingType, rankingLimit]);

  // Fetch series data when selection changes
  useEffect(() => {
    const fetchSeriesData = async () => {
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const startYear = seriesTimeRange > 0 ? new Date().getFullYear() - seriesTimeRange : undefined;
            const res = await ipResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, startYear);
            setSeriesChartData((prev) => ({ ...prev, [seriesId]: res.data }));
          } catch (err) {
            console.error(`Failed to load series ${seriesId}:`, err);
          }
        }
      }
    };
    if (selectedSeriesIds.length > 0) fetchSeriesData();
  }, [selectedSeriesIds, seriesTimeRange]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await ipResearchAPI.getSeries<SeriesListData>({ search: searchQuery, limit: 50 });
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
      if (drillMeasureCode) params.measure_code = drillMeasureCode;
      if (drillDurationCode) params.duration_code = drillDurationCode;
      const res = await ipResearchAPI.getSeries<SeriesListData>(params);
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
      if (browseIndustryCode) params.industry_code = browseIndustryCode;
      if (browseMeasureCode) params.measure_code = browseMeasureCode;
      const res = await ipResearchAPI.getSeries<SeriesListData>(params);
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

  const toggleIndustryCode = (code: string) => {
    setSelectedIndustryCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
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
          <h1 className="text-2xl font-bold text-gray-900">Industry Productivity (IP)</h1>
          <p className="text-sm text-gray-600 mt-1">
            Annual productivity measures for 800+ industries (1987-present, {dimensions?.sectors.length || 0} sectors)
          </p>
        </div>
      </div>

      {/* Section 1: Overview */}
      <Card>
        <SectionHeader title="Sector Overview" color="blue" icon={Activity} />
        <div className="p-5">
          {/* Controls */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select label="Measure" value={overviewMeasure} onChange={setOverviewMeasure} options={measureOptions} className="w-44" />
            <Select label="Value Type" value={overviewDuration} onChange={setOverviewDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={overviewYears} onChange={(v) => setOverviewYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={overviewView} onChange={setOverviewView} />
          </div>

          {loadingOverview || loadingOverviewTimeline ? (
            <LoadingSpinner />
          ) : overviewView === 'chart' ? (
            <>
              {/* Year indicator */}
              <div className="text-sm text-gray-500 mb-4">
                {overviewSelectedIndex !== null && overviewTimelineData?.timeline?.[overviewSelectedIndex]
                  ? `Year: ${overviewTimelineData.timeline[overviewSelectedIndex].year}`
                  : `Year: ${overviewData?.year}`}
              </div>

              {/* Heatmap Grid - All Sectors */}
              {overviewData?.sectors && overviewData.sectors.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">All Sectors - {measureOptions.find(m => m.value === overviewMeasure)?.label || 'Labor Productivity'}</h4>
                  <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2">
                    {overviewData.sectors.map((sector) => {
                      // Get value based on selected measure
                      let value = sector.labor_productivity;
                      let change = sector.labor_productivity_change;
                      if (overviewMeasure === 'T01') { value = sector.output; change = sector.output_change; }
                      else if (overviewMeasure === 'L01') { value = sector.hours; change = sector.hours_change; }
                      else if (overviewMeasure === 'W01') { value = sector.employment; change = sector.employment_change; }
                      else if (overviewMeasure === 'U10') { value = sector.unit_labor_costs; change = sector.ulc_change; }

                      const hasData = value != null;
                      const bgColor = !hasData ? 'bg-gray-200' :
                        (change ?? 0) > 2 ? 'bg-green-500' :
                        (change ?? 0) > 0 ? 'bg-green-300' :
                        (change ?? 0) > -2 ? 'bg-red-300' : 'bg-red-500';
                      const textColor = !hasData ? 'text-gray-500' : 'text-white';

                      return (
                        <div
                          key={sector.sector_code}
                          className={`${bgColor} rounded-lg p-2 text-center min-h-[80px] flex flex-col justify-center`}
                          title={`${sector.sector_text}: ${hasData ? value?.toFixed(1) : 'N/A'} (${change != null ? (change >= 0 ? '+' : '') + change.toFixed(1) + '%' : 'N/A'})`}
                        >
                          <div className={`text-[10px] font-medium ${textColor} truncate`}>
                            {sector.sector_text.length > 20 ? sector.sector_text.substring(0, 17) + '...' : sector.sector_text}
                          </div>
                          <div className={`text-lg font-bold ${textColor}`}>
                            {hasData ? value?.toFixed(1) : 'N/A'}
                          </div>
                          {hasData && change != null && (
                            <div className={`text-[10px] ${textColor}`}>
                              {change >= 0 ? '+' : ''}{change.toFixed(1)}%
                            </div>
                          )}
                          <div className="text-[8px] text-gray-400 mt-1">
                            {sector.industry_count} industries
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="flex items-center justify-center gap-4 mt-3 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-green-500 rounded"></span> Growth &gt;2%</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-green-300 rounded"></span> Growth 0-2%</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-red-300 rounded"></span> Decline 0-2%</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-red-500 rounded"></span> Decline &gt;2%</span>
                    <span className="flex items-center gap-1"><span className="w-3 h-3 bg-gray-200 rounded"></span> No Data</span>
                  </div>
                </div>
              )}

              {/* Timeline Chart - All sectors with data */}
              {overviewTimelineData?.timeline && overviewTimelineData.timeline.length > 0 && (
                <>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Historical Trend (sectors with data)</h4>
                  <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={overviewTimelineData.timeline}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: '10px' }} />
                      {Object.keys(overviewTimelineData.sector_names)
                        .filter(code => {
                          // Only show sectors that have data in at least one year
                          return overviewTimelineData.timeline.some(t => t.sectors[code] != null);
                        })
                        .map((code, idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`sectors.${code}`}
                            name={overviewTimelineData.sector_names[code]}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            dot={false}
                            strokeWidth={1.5}
                            connectNulls
                          />
                        ))}
                    </LineChart>
                  </ResponsiveContainer>
                </>
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
                    <th className="px-4 py-2 text-right">Industries</th>
                  </tr>
                </thead>
                <tbody>
                  {overviewData?.sectors?.map((sector) => (
                    <tr key={sector.sector_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{sector.sector_text}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(sector.labor_productivity)}</td>
                      <td className={`px-4 py-2 text-right ${(sector.labor_productivity_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(sector.labor_productivity_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(sector.unit_labor_costs)}</td>
                      <td className={`px-4 py-2 text-right ${(sector.ulc_change ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatChange(sector.ulc_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(sector.output)}</td>
                      <td className="px-4 py-2 text-right text-gray-500">{sector.industry_count}</td>
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
          {/* Controls */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select
              label="Sector"
              value={analysisSector}
              onChange={(v) => { setAnalysisSector(v); setSelectedIndustryCodes([]); }}
              options={dimensions?.sectors.map((s) => ({ value: s.sector_code, label: s.sector_text })) || []}
              className="w-52"
            />
            <Select label="Measure" value={analysisMeasure} onChange={setAnalysisMeasure} options={measureOptions} className="w-44" />
            <Select label="Value Type" value={analysisDuration} onChange={setAnalysisDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={analysisYears} onChange={(v) => setAnalysisYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={analysisView} onChange={setAnalysisView} />
          </div>

          {/* Industry selection */}
          {analysisData?.industries && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Select industries to compare (click to toggle):</p>
              <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
                {analysisData.industries.slice(0, 20).map((ind) => (
                  <button
                    key={ind.industry_code}
                    onClick={() => toggleIndustryCode(ind.industry_code)}
                    className={`px-2 py-1 text-xs rounded ${
                      selectedIndustryCodes.includes(ind.industry_code)
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {ind.industry_text.substring(0, 30)}
                  </button>
                ))}
              </div>
            </div>
          )}

          {loadingAnalysis || loadingAnalysisTimeline ? (
            <LoadingSpinner />
          ) : analysisView === 'chart' ? (
            <>
              {/* Selected period info */}
              {analysisSelectedIndex !== null && analysisTimelineData?.timeline?.[analysisSelectedIndex] && (
                <div className="mb-4 p-3 bg-green-50 rounded-lg">
                  <div className="text-sm font-medium text-green-800 mb-2">
                    Selected: {analysisTimelineData.timeline[analysisSelectedIndex].year}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {selectedIndustryCodes.map((code) => {
                      const value = analysisTimelineData.timeline[analysisSelectedIndex]?.industries?.[code];
                      return (
                        <div key={code} className="text-xs">
                          <span className="text-gray-600">{analysisTimelineData.industry_names[code]?.substring(0, 25) || code}: </span>
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
                    <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    {selectedIndustryCodes.map((code, idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={`industries.${code}`}
                        name={analysisTimelineData.industry_names[code]?.substring(0, 25) || code}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        dot={false}
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-500 text-center py-8">Select industries to view timeline</div>
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
                    <th className="px-4 py-2 text-left">Industry</th>
                    <th className="px-4 py-2 text-left">NAICS</th>
                    <th className="px-4 py-2 text-right">Productivity</th>
                    <th className="px-4 py-2 text-right">YoY %</th>
                    <th className="px-4 py-2 text-right">Output</th>
                    <th className="px-4 py-2 text-right">Hours</th>
                    <th className="px-4 py-2 text-right">Employment</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisData?.industries?.map((ind) => (
                    <tr key={ind.industry_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2">{ind.industry_text}</td>
                      <td className="px-4 py-2 text-gray-500 font-mono text-xs">{ind.naics_code || 'N/A'}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(ind.labor_productivity)}</td>
                      <td className={`px-4 py-2 text-right ${(ind.labor_productivity_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(ind.labor_productivity_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(ind.output)}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(ind.hours)}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(ind.employment)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Section 3: Industry Analysis */}
      <Card>
        <SectionHeader title="Industry Analysis" color="purple" icon={Factory} />
        <div className="p-5">
          {/* Controls */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select
              label="Industry"
              value={industryCode}
              onChange={setIndustryCode}
              options={industryOptions}
              className="w-72"
            />
            <Select label="Value Type" value={industryDuration} onChange={setIndustryDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={industryYears} onChange={(v) => setIndustryYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={industryView} onChange={setIndustryView} />
          </div>

          {/* Measure selection */}
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">Select measures to compare:</p>
            <div className="flex flex-wrap gap-2">
              {measureOptions.map((m) => (
                <button
                  key={m.value}
                  onClick={() => toggleMeasureCode(String(m.value))}
                  className={`px-2 py-1 text-xs rounded ${
                    selectedMeasureCodes.includes(String(m.value))
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          {loadingIndustry || loadingIndustryTimeline ? (
            <LoadingSpinner />
          ) : industryView === 'chart' ? (
            <>
              {/* Industry info */}
              {industryData && (
                <div className="mb-4 p-3 bg-purple-50 rounded-lg">
                  <div className="text-sm font-medium text-purple-800">
                    {industryData.industry_text}
                  </div>
                  <div className="text-xs text-purple-600">
                    NAICS: {industryData.naics_code || 'N/A'} | Sector: {industryData.sector_text}
                  </div>
                </div>
              )}
              {industryTimelineData?.timeline && industryTimelineData.timeline.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={industryTimelineData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    {selectedMeasureCodes.map((code, idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={`measures.${code}`}
                        name={industryTimelineData.measure_names[code] || code}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        dot={false}
                        strokeWidth={2}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-500 text-center py-8">Select an industry to view data</div>
              )}
              {industryTimelineData?.timeline && industryTimelineData.timeline.length > 0 && (
                <TimelineSelector
                  timeline={industryTimelineData.timeline}
                  selectedIndex={industrySelectedIndex}
                  onSelectIndex={setIndustrySelectedIndex}
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
                    <th className="px-4 py-2 text-right">Value</th>
                    <th className="px-4 py-2 text-right">YoY %</th>
                  </tr>
                </thead>
                <tbody>
                  {industryData?.measures?.map((m) => (
                    <tr key={m.measure_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2">{m.measure_text}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(m.value)}</td>
                      <td className={`px-4 py-2 text-right ${(m.change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(m.change)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Section 4: Productivity vs Costs */}
      <Card>
        <SectionHeader title="Productivity vs Labor Costs" color="orange" icon={Activity} />
        <div className="p-5">
          {/* Controls */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select
              label="Filter by Sector"
              value={pvcSector}
              onChange={setPvcSector}
              options={sectorOptions}
              className="w-52"
            />
            <Select
              label="Industry (for timeline)"
              value={pvcIndustry}
              onChange={setPvcIndustry}
              options={[
                { value: '', label: 'Select Industry' },
                ...(pvcData?.industries?.slice(0, 50).map(i => ({ value: i.industry_code, label: i.industry_text.substring(0, 40) })) || [])
              ]}
              className="w-64"
            />
            <Select label="Value Type" value={pvcDuration} onChange={setPvcDuration} options={durationOptions} className="w-40" />
            <Select label="Time Range" value={pvcYears} onChange={(v) => setPvcYears(Number(v))} options={timeRangeOptions} className="w-36" />
            <ViewToggle value={pvcView} onChange={setPvcView} />
          </div>

          {loadingPvc || loadingPvcTimeline ? (
            <LoadingSpinner />
          ) : pvcView === 'chart' ? (
            <>
              {/* Selected period info */}
              {pvcSelectedIndex !== null && pvcTimelineData?.timeline?.[pvcSelectedIndex] && (
                <div className="mb-4 p-3 bg-orange-50 rounded-lg">
                  <div className="text-sm font-medium text-orange-800 mb-2">
                    {pvcTimelineData.industry_text} - {pvcTimelineData.timeline[pvcSelectedIndex].year}
                  </div>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-xs text-gray-600">Productivity</div>
                      <div className="text-lg font-bold text-blue-600">{formatNumber(pvcTimelineData.timeline[pvcSelectedIndex].labor_productivity)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-gray-600">Unit Labor Costs</div>
                      <div className="text-lg font-bold text-red-600">{formatNumber(pvcTimelineData.timeline[pvcSelectedIndex].unit_labor_costs)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-gray-600">Output</div>
                      <div className="text-lg font-bold text-green-600">{formatNumber(pvcTimelineData.timeline[pvcSelectedIndex].output)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xs text-gray-600">Compensation</div>
                      <div className="text-lg font-bold text-purple-600">{formatNumber(pvcTimelineData.timeline[pvcSelectedIndex].compensation)}</div>
                    </div>
                  </div>
                </div>
              )}
              {pvcTimelineData?.timeline && pvcTimelineData.timeline.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={pvcTimelineData.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="labor_productivity" name="Productivity" stroke="#3b82f6" dot={false} strokeWidth={2} />
                    <Line type="monotone" dataKey="unit_labor_costs" name="Unit Labor Costs" stroke="#ef4444" dot={false} strokeWidth={2} />
                    <Line type="monotone" dataKey="output" name="Output" stroke="#10b981" dot={false} strokeWidth={2} />
                    <Line type="monotone" dataKey="compensation" name="Compensation" stroke="#8b5cf6" dot={false} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-gray-500 text-center py-8">Select an industry to view timeline</div>
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
            <div className="overflow-x-auto max-h-96">
              <table className="min-w-full text-sm">
                <thead className="sticky top-0 bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Industry</th>
                    <th className="px-4 py-2 text-right">Productivity</th>
                    <th className="px-4 py-2 text-right">Prod. YoY</th>
                    <th className="px-4 py-2 text-right">Unit Labor Costs</th>
                    <th className="px-4 py-2 text-right">ULC YoY</th>
                    <th className="px-4 py-2 text-right">Compensation</th>
                    <th className="px-4 py-2 text-right">Comp. YoY</th>
                  </tr>
                </thead>
                <tbody>
                  {pvcData?.industries?.map((row) => (
                    <tr key={row.industry_code} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{row.industry_text}</td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.labor_productivity)}</td>
                      <td className={`px-4 py-2 text-right ${(row.productivity_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(row.productivity_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.unit_labor_costs)}</td>
                      <td className={`px-4 py-2 text-right ${(row.ulc_change ?? 0) >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {formatChange(row.ulc_change)}
                      </td>
                      <td className="px-4 py-2 text-right">{formatNumber(row.compensation)}</td>
                      <td className={`px-4 py-2 text-right ${(row.compensation_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatChange(row.compensation_change)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Section 5: Top Rankings */}
      <Card>
        <SectionHeader title="Top Rankings" color="amber" icon={Award} />
        <div className="p-5">
          {/* Controls */}
          <div className="flex flex-wrap gap-4 mb-6 items-end">
            <Select label="Measure" value={rankingMeasure} onChange={setRankingMeasure} options={measureOptions} className="w-44" />
            <Select label="Ranking Type" value={rankingType} onChange={setRankingType} options={rankingTypeOptions} className="w-44" />
            <Select
              label="Limit"
              value={rankingLimit}
              onChange={(v) => setRankingLimit(Number(v))}
              options={[{ value: 10, label: 'Top 10' }, { value: 20, label: 'Top 20' }, { value: 50, label: 'Top 50' }]}
              className="w-32"
            />
          </div>

          {loadingRanking ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Bar Chart */}
              {rankingData?.industries && rankingData.industries.length > 0 && (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={rankingData.industries.slice(0, 15)} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" tick={{ fontSize: 10 }} />
                    <YAxis dataKey="industry_text" type="category" width={200} tick={{ fontSize: 9 }} />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" name={rankingData.measure_text} />
                  </BarChart>
                </ResponsiveContainer>
              )}

              {/* Table */}
              <div className="overflow-x-auto mt-6">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="px-4 py-2 text-left">Rank</th>
                      <th className="px-4 py-2 text-left">Industry</th>
                      <th className="px-4 py-2 text-left">Sector</th>
                      <th className="px-4 py-2 text-left">NAICS</th>
                      <th className="px-4 py-2 text-right">Value</th>
                      <th className="px-4 py-2 text-right">YoY %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rankingData?.industries?.map((ind) => (
                      <tr key={ind.industry_code} className="border-t hover:bg-gray-50">
                        <td className="px-4 py-2 font-medium">#{ind.rank}</td>
                        <td className="px-4 py-2">{ind.industry_text}</td>
                        <td className="px-4 py-2 text-gray-500">{ind.sector_text}</td>
                        <td className="px-4 py-2 font-mono text-xs text-gray-500">{ind.naics_code || 'N/A'}</td>
                        <td className="px-4 py-2 text-right font-semibold">{formatNumber(ind.value)}</td>
                        <td className={`px-4 py-2 text-right ${(ind.change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatChange(ind.change)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </Card>

      {/* Section 6: Series Explorer */}
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
                <Select label="Measure" value={drillMeasureCode} onChange={setDrillMeasureCode} options={measureDimOptions} className="w-full" />
                <Select label="Value Type" value={drillDurationCode} onChange={setDrillDurationCode} options={durationDimOptions} className="w-full" />
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
                <Select label="Industry" value={browseIndustryCode} onChange={setBrowseIndustryCode} options={industryOptions} className="w-full" />
                <Select label="Measure" value={browseMeasureCode} onChange={setBrowseMeasureCode} options={measureDimOptions} className="w-full" />
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
                      <th className="px-3 py-2 text-left">Industry</th>
                      <th className="px-3 py-2 text-left">Measure</th>
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
                        <td className="px-3 py-2">{s.sector_text}</td>
                        <td className="px-3 py-2">{s.industry_text?.substring(0, 25)}</td>
                        <td className="px-3 py-2">{s.measure_text}</td>
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
                      const data = seriesChartData[seriesId]?.series[0]?.data || [];
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
                          const points = seriesChartData[id]?.series[0]?.data || [];
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
