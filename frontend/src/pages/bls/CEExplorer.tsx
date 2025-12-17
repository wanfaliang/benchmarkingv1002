import { useState, useEffect, useMemo, ReactElement } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, DollarSign, LucideIcon } from 'lucide-react';
import { ceResearchAPI } from '../../services/api';

/**
 * CE Explorer - Current Employment Statistics Explorer
 *
 * Sections:
 * 1. Employment Overview - Headline stats (Total Nonfarm, Private, etc.)
 * 2. Supersector Analysis - Employment by major sector
 * 3. Industry Analysis - Detailed industry breakdown
 * 4. Earnings & Hours Analysis - Wages and hours data
 * 5. Series Explorer - Search and chart specific series
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
  total_nonfarm?: number;
  total_private?: number;
  goods_producing?: number;
  service_providing?: number;
  government?: number;
  supersectors?: Record<string, number>;
  industries?: Record<string, number>;
  avg_hourly_earnings?: number;
  avg_weekly_earnings?: number;
  avg_weekly_hours?: number;
  [key: string]: unknown;
}

interface OverviewData {
  total_nonfarm?: { latest_value?: number; month_over_month?: number; year_over_year?: number; latest_date?: string };
  total_private?: { latest_value?: number; month_over_month?: number; year_over_year?: number; latest_date?: string };
  goods_producing?: { latest_value?: number; month_over_month?: number; year_over_year?: number; latest_date?: string };
  service_providing?: { latest_value?: number; month_over_month?: number; year_over_year?: number; latest_date?: string };
  government?: { latest_value?: number; month_over_month?: number; year_over_year?: number; latest_date?: string };
  [key: string]: unknown;
}

interface OverviewTimelineData {
  timeline: TimelinePoint[];
}

interface Supersector {
  supersector_code: string;
  supersector_name: string;
  latest_value?: number;
  month_over_month?: number;
  month_over_month_pct?: number;
  year_over_year?: number;
  year_over_year_pct?: number;
}

interface SupersectorsData {
  supersectors: Supersector[];
}

interface SupersectorTimelineData {
  timeline: TimelinePoint[];
  supersector_names?: Record<string, string>;
}

interface Industry {
  industry_code: string;
  industry_name: string;
  display_level: number;
  latest_value?: number;
  month_over_month?: number;
  month_over_month_pct?: number;
  year_over_year?: number;
  year_over_year_pct?: number;
  selectable?: boolean;
}

interface IndustriesData {
  industries: Industry[];
  total_count: number;
  last_updated?: string;
}

interface IndustryTimelineData {
  timeline: TimelinePoint[];
  industry_names?: Record<string, string>;
}

interface EarningsItem {
  industry_code: string;
  industry_name: string;
  avg_hourly_earnings?: number;
  avg_weekly_earnings?: number;
  avg_weekly_hours?: number;
  hourly_mom_pct?: number;
  hourly_yoy_pct?: number;
}

interface EarningsData {
  earnings: EarningsItem[];
  total_count: number;
  last_updated?: string;
}

interface EarningsTimelineData {
  timeline: TimelinePoint[];
  industry_name?: string;
}

interface SeriesInfo {
  series_id: string;
  industry_name?: string;
  data_type_text?: string;
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
  data_points: DataPoint[];
}

interface SeriesDataResponse {
  series: SeriesDataItem[];
}

interface SeriesChartDataMap {
  [seriesId: string]: SeriesDataResponse;
}

interface DimensionsData {
  supersectors?: Supersector[];
  industries?: Industry[];
  data_types?: { data_type_code: string; data_type_text: string }[];
}

interface PointDataValue {
  value: number | null;
  mom_change: number | null;
  mom_pct: number | null;
  yoy_change: number | null;
  yoy_pct: number | null;
}

interface PointData {
  period_name: string;
  data: Record<string, PointDataValue>;
  industry_name?: string;
}

type ViewType = 'table' | 'chart';
type SectionColor = 'blue' | 'green' | 'orange' | 'purple' | 'cyan';

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

const formatNumber = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}M`;
  }
  return `${value.toLocaleString()}K`;
};

const formatChange = (value: number | undefined | null, suffix: string = ''): string => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}${suffix}`;
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
  <div className="flex justify-center items-center py-12">
    <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
  </div>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function CEExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [loadingDimensions, setLoadingDimensions] = useState(true);

  // Overview
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeRange, setOverviewTimeRange] = useState(24);
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [overviewSelectedIndex, setOverviewSelectedIndex] = useState<number | null>(null);

  // Supersector
  const [supersectors, setSupersectors] = useState<SupersectorsData | null>(null);
  const [loadingSupersectors, setLoadingSupersectors] = useState(true);
  const [supersectorTimeRange, setSupersectorTimeRange] = useState(24);
  const [supersectorTimeline, setSupersectorTimeline] = useState<SupersectorTimelineData | null>(null);
  const [selectedSupersectors, setSelectedSupersectors] = useState<string[]>(['30', '20', '40']);
  const [supersectorSelectedIndex, setSupersectorSelectedIndex] = useState<number | null>(null);

  // Industries
  const [industries, setIndustries] = useState<IndustriesData | null>(null);
  const [loadingIndustries, setLoadingIndustries] = useState(true);
  const [industryDisplayLevel, setIndustryDisplayLevel] = useState('');
  const [industrySupersector, setIndustrySupersector] = useState('');
  const [industryLimit, setIndustryLimit] = useState(20);
  const [industryTimeRange, setIndustryTimeRange] = useState(24);
  const [industryTimeline, setIndustryTimeline] = useState<IndustryTimelineData | null>(null);
  const [industrySelectedIndex, setIndustrySelectedIndex] = useState<number | null>(null);
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [industryView, setIndustryView] = useState<ViewType>('table');

  // Earnings
  const [earnings, setEarnings] = useState<EarningsData | null>(null);
  const [loadingEarnings, setLoadingEarnings] = useState(true);
  const [earningsSupersector, setEarningsSupersector] = useState('');
  const [earningsLimit, setEarningsLimit] = useState(20);
  const [selectedEarningsIndustry, setSelectedEarningsIndustry] = useState<string | null>(null);
  const [earningsTimeline, setEarningsTimeline] = useState<EarningsTimelineData | null>(null);
  const [earningsTimeRange, setEarningsTimeRange] = useState(24);
  const [earningsSelectedIndex, setEarningsSelectedIndex] = useState<number | null>(null);
  const [earningsView, setEarningsView] = useState<ViewType>('table');

  // Series Explorer
  const [seriesData, setSeriesData] = useState<SeriesListData | null>(null);
  const [loadingSeries, setLoadingSeries] = useState(false);
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [selectedSupersectorFilter, setSelectedSupersectorFilter] = useState('');
  const [selectedDataTypeFilter, setSelectedDataTypeFilter] = useState('');
  const [selectedSeasonal, setSelectedSeasonal] = useState('');
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesTimeRange, setSeriesTimeRange] = useState(24);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');
  const [seriesChartData, setSeriesChartData] = useState<SeriesChartDataMap>({});

  // Load dimensions on mount
  useEffect(() => {
    const load = async () => {
      try {
        const res = await ceResearchAPI.getDimensions();
        setDimensions(res.data as DimensionsData);
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
        const res = await ceResearchAPI.getOverview();
        setOverview(res.data as OverviewData);
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
        const res = await ceResearchAPI.getOverviewTimeline(overviewTimeRange);
        const data = res.data as OverviewTimelineData;
        setOverviewTimeline(data);
        if (data?.timeline?.length > 0) {
          setOverviewSelectedIndex(data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load overview timeline:', error);
      }
    };
    load();
  }, [overviewTimeRange]);

  // Load supersectors
  useEffect(() => {
    const load = async () => {
      setLoadingSupersectors(true);
      try {
        const res = await ceResearchAPI.getSupersectors();
        setSupersectors(res.data as SupersectorsData);
      } catch (error) {
        console.error('Failed to load supersectors:', error);
      } finally {
        setLoadingSupersectors(false);
      }
    };
    load();
  }, []);

  // Load supersector timeline
  useEffect(() => {
    const load = async () => {
      if (selectedSupersectors.length === 0) return;
      try {
        const res = await ceResearchAPI.getSupersectorsTimeline({
          supersector_codes: selectedSupersectors.join(','),
          months_back: supersectorTimeRange
        });
        const data = res.data as SupersectorTimelineData;
        setSupersectorTimeline(data);
        if (data?.timeline?.length > 0) {
          setSupersectorSelectedIndex(data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load supersector timeline:', error);
      }
    };
    load();
  }, [selectedSupersectors, supersectorTimeRange]);

  // Load industries
  useEffect(() => {
    const load = async () => {
      setLoadingIndustries(true);
      try {
        const params: { limit: number; display_level?: number; supersector_code?: string } = { limit: industryLimit };
        if (industryDisplayLevel) params.display_level = parseInt(industryDisplayLevel);
        if (industrySupersector) params.supersector_code = industrySupersector;
        const res = await ceResearchAPI.getIndustries(params);
        const data = res.data as IndustriesData;
        setIndustries(data);
        // Pre-select first 3 industries for timeline
        if (data?.industries?.length > 0 && selectedIndustries.length === 0) {
          setSelectedIndustries(data.industries.slice(0, 3).map(i => i.industry_code));
        }
      } catch (error) {
        console.error('Failed to load industries:', error);
      } finally {
        setLoadingIndustries(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [industryDisplayLevel, industrySupersector, industryLimit]);
  // Note: selectedIndustries.length intentionally omitted - only auto-select on first load

  // Load industry timeline
  useEffect(() => {
    const load = async () => {
      if (selectedIndustries.length === 0) return;
      try {
        const res = await ceResearchAPI.getIndustriesTimeline(selectedIndustries, industryTimeRange);
        const data = res.data as IndustryTimelineData;
        setIndustryTimeline(data);
        if (data?.timeline?.length > 0) {
          setIndustrySelectedIndex(data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load industry timeline:', error);
      }
    };
    load();
  }, [selectedIndustries, industryTimeRange]);

  // Load earnings
  useEffect(() => {
    const load = async () => {
      setLoadingEarnings(true);
      try {
        const params: { limit: number; supersector_code?: string } = { limit: earningsLimit };
        if (earningsSupersector) params.supersector_code = earningsSupersector;
        const res = await ceResearchAPI.getEarnings(params);
        setEarnings(res.data as EarningsData);
      } catch (error) {
        console.error('Failed to load earnings:', error);
      } finally {
        setLoadingEarnings(false);
      }
    };
    load();
  }, [earningsSupersector, earningsLimit]);

  // Load earnings timeline for selected industry
  useEffect(() => {
    const load = async () => {
      if (!selectedEarningsIndustry) return;
      try {
        const res = await ceResearchAPI.getEarningsTimeline(selectedEarningsIndustry, earningsTimeRange);
        const data = res.data as EarningsTimelineData;
        setEarningsTimeline(data);
        if (data?.timeline?.length > 0) {
          setEarningsSelectedIndex(data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load earnings timeline:', error);
      }
    };
    load();
  }, [selectedEarningsIndustry, earningsTimeRange]);

  // Load series list
  useEffect(() => {
    const load = async () => {
      setLoadingSeries(true);
      try {
        const params: { active_only: boolean; limit: number; industry_code?: string; supersector_code?: string; data_type_code?: string; seasonal_code?: string } = { active_only: true, limit: 50 };
        if (selectedIndustry) params.industry_code = selectedIndustry;
        if (selectedSupersectorFilter) params.supersector_code = selectedSupersectorFilter;
        if (selectedDataTypeFilter) params.data_type_code = selectedDataTypeFilter;
        if (selectedSeasonal) params.seasonal_code = selectedSeasonal;
        const res = await ceResearchAPI.getSeries(params);
        setSeriesData(res.data as SeriesListData);
      } catch (error) {
        console.error('Failed to load series:', error);
      } finally {
        setLoadingSeries(false);
      }
    };
    load();
  }, [selectedIndustry, selectedSupersectorFilter, selectedDataTypeFilter, selectedSeasonal]);

  // Load data for selected series
  useEffect(() => {
    const load = async () => {
      const newData: SeriesChartDataMap = {};
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const res = await ceResearchAPI.getSeriesData(seriesId);
            newData[seriesId] = res.data as SeriesDataResponse;
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
  // Note: seriesChartData intentionally omitted - used as cache lookup, not trigger

  const toggleSupersector = (code: string): void => {
    setSelectedSupersectors(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : prev.length < 6 ? [...prev, code] : prev
    );
  };

  const toggleIndustry = (code: string): void => {
    setSelectedIndustries(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : prev.length < 5 ? [...prev, code] : prev
    );
  };

  // Compute overview data for selected point
  const overviewPointData = useMemo((): PointData | null => {
    if (!overviewTimeline?.timeline || overviewSelectedIndex === null) return null;
    const timeline = overviewTimeline.timeline;
    const idx = overviewSelectedIndex;
    const current = timeline[idx];
    if (!current) return null;

    const categories = ['total_nonfarm', 'total_private', 'goods_producing', 'service_providing', 'government'];
    const result: Record<string, PointDataValue> = {};

    categories.forEach(cat => {
      const val = current[cat] as number | undefined;
      const prevMonth = idx > 0 ? timeline[idx - 1]?.[cat] as number | undefined : undefined;
      const prevYear = idx >= 12 ? timeline[idx - 12]?.[cat] as number | undefined : undefined;

      result[cat] = {
        value: val ?? null,
        mom_change: prevMonth != null && val != null ? val - prevMonth : null,
        mom_pct: prevMonth != null && prevMonth !== 0 && val != null ? ((val - prevMonth) / prevMonth) * 100 : null,
        yoy_change: prevYear != null && val != null ? val - prevYear : null,
        yoy_pct: prevYear != null && prevYear !== 0 && val != null ? ((val - prevYear) / prevYear) * 100 : null,
      };
    });

    return { period_name: current.period_name, data: result };
  }, [overviewTimeline, overviewSelectedIndex]);

  // Compute industry data for selected point
  const industryPointData = useMemo((): PointData | null => {
    if (!industryTimeline?.timeline || industrySelectedIndex === null) return null;
    const timeline = industryTimeline.timeline;
    const idx = industrySelectedIndex;
    const current = timeline[idx];
    if (!current) return null;

    const result: Record<string, PointDataValue> = {};
    Object.keys(industryTimeline.industry_names || {}).forEach(code => {
      const val = current.industries?.[code];
      const prevMonth = idx > 0 ? timeline[idx - 1]?.industries?.[code] : undefined;
      const prevYear = idx >= 12 ? timeline[idx - 12]?.industries?.[code] : undefined;

      result[code] = {
        value: val ?? null,
        mom_change: prevMonth != null && val != null ? val - prevMonth : null,
        mom_pct: prevMonth != null && prevMonth !== 0 && val != null ? ((val - prevMonth) / prevMonth) * 100 : null,
        yoy_change: prevYear != null && val != null ? val - prevYear : null,
        yoy_pct: prevYear != null && prevYear !== 0 && val != null ? ((val - prevYear) / prevYear) * 100 : null,
      };
    });

    return { period_name: current.period_name, data: result };
  }, [industryTimeline, industrySelectedIndex]);

  // Compute earnings data for selected point
  const earningsPointData = useMemo((): PointData | null => {
    if (!earningsTimeline?.timeline || earningsSelectedIndex === null) return null;
    const timeline = earningsTimeline.timeline;
    const idx = earningsSelectedIndex;
    const current = timeline[idx];
    if (!current) return null;

    const fields = ['avg_hourly_earnings', 'avg_weekly_earnings', 'avg_weekly_hours'];
    const result: Record<string, PointDataValue> = {};

    fields.forEach(field => {
      const val = current[field] as number | undefined;
      const prevMonth = idx > 0 ? timeline[idx - 1]?.[field] as number | undefined : undefined;
      const prevYear = idx >= 12 ? timeline[idx - 12]?.[field] as number | undefined : undefined;

      result[field] = {
        value: val ?? null,
        mom_change: prevMonth != null && val != null ? val - prevMonth : null,
        mom_pct: prevMonth != null && prevMonth !== 0 && val != null ? ((val - prevMonth) / prevMonth) * 100 : null,
        yoy_change: prevYear != null && val != null ? val - prevYear : null,
        yoy_pct: prevYear != null && prevYear !== 0 && val != null ? ((val - prevYear) / prevYear) * 100 : null,
      };
    });

    return { period_name: current.period_name, data: result, industry_name: earningsTimeline.industry_name };
  }, [earningsTimeline, earningsSelectedIndex]);

  if (loadingDimensions) {
    return <LoadingSpinner />;
  }

  const selectableIndustries = dimensions?.industries?.filter(i => i.selectable) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">CE - Current Employment Statistics Explorer</h1>
        <p className="text-sm text-gray-500">Explore employment data by industry and supersector</p>
      </div>

      {/* Section 1: Employment Overview */}
      <Card>
        <SectionHeader title="Employment Overview" color="blue" />
        <div className="p-5">
          {loadingOverview ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Headline Metrics */}
              <div className="grid grid-cols-5 gap-4 mb-6">
                {[
                  { key: 'total_nonfarm', label: 'Total Nonfarm', color: 'blue' },
                  { key: 'total_private', label: 'Total Private', color: 'green' },
                  { key: 'goods_producing', label: 'Goods-Producing', color: 'orange' },
                  { key: 'service_providing', label: 'Service-Providing', color: 'purple' },
                  { key: 'government', label: 'Government', color: 'cyan' },
                ].map(({ key, label, color }) => {
                  const pointData = overviewPointData?.data?.[key];
                  const overviewItem = overview?.[key] as { latest_value?: number; month_over_month?: number; year_over_year?: number; latest_date?: string } | undefined;
                  return (
                    <div key={key} className="p-4 rounded-lg border border-gray-200 bg-gray-50">
                      <p className="text-xs font-medium text-gray-500 uppercase">{label}</p>
                      <p className={`text-2xl font-bold text-${color}-600 my-1`}>
                        {formatNumber(pointData?.value ?? overviewItem?.latest_value)}
                      </p>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-500">MoM</span>
                          <ChangeIndicator value={pointData?.mom_change ?? overviewItem?.month_over_month} suffix="K" />
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">YoY</span>
                          <ChangeIndicator value={pointData?.yoy_change ?? overviewItem?.year_over_year} suffix="K" />
                        </div>
                      </div>
                      <p className="text-[10px] text-gray-400 mt-2">
                        {overviewPointData?.period_name || overviewItem?.latest_date}
                      </p>
                    </div>
                  );
                })}
              </div>

              {/* Timeline Chart */}
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold text-gray-700">Employment Trends (Thousands)</h3>
                <Select
                  value={overviewTimeRange}
                  onChange={(v) => setOverviewTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
              </div>

              {overviewTimeline?.timeline?.length && overviewTimeline.timeline.length > 0 && (
                <>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={overviewTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}M`} />
                        <Tooltip formatter={(value) => [`${(value as number)?.toLocaleString()}K`, '']} />
                        <Legend />
                        <Line type="monotone" dataKey="total_nonfarm" stroke="#3b82f6" name="Total Nonfarm" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="total_private" stroke="#10b981" name="Total Private" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="goods_producing" stroke="#f59e0b" name="Goods-Producing" strokeWidth={1.5} dot={false} />
                        <Line type="monotone" dataKey="service_providing" stroke="#8b5cf6" name="Service-Providing" strokeWidth={1.5} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <TimelineSelector
                    timeline={overviewTimeline.timeline}
                    selectedIndex={overviewSelectedIndex}
                    onSelectIndex={setOverviewSelectedIndex}
                  />
                </>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 2: Supersector Analysis */}
      <Card>
        <SectionHeader title="Supersector Analysis" color="green" />
        <div className="p-5">
          {loadingSupersectors ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Horizontal Bar Chart */}
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Employment by Supersector (Thousands)</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={[...(supersectors?.supersectors || [])].sort((a, b) => (b.latest_value || 0) - (a.latest_value || 0))}
                    layout="vertical"
                    margin={{ left: 150 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => v.toLocaleString()} />
                    <YAxis type="category" dataKey="supersector_name" tick={{ fontSize: 10 }} width={140} />
                    <Tooltip formatter={(value) => [`${(value as number)?.toLocaleString()}K`, 'Employment']} />
                    <Bar dataKey="latest_value" fill="#10b981">
                      {supersectors?.supersectors?.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Supersector Table - 2D Time Series */}
              <div className="flex justify-between items-center mt-6 mb-3">
                <h3 className="text-sm font-semibold text-gray-700">
                  Supersector Employment (Thousands)
                </h3>
                <Select
                  value={supersectorTimeRange}
                  onChange={(v) => setSupersectorTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
              </div>

              <div className="overflow-x-auto max-h-[400px] border border-gray-200 rounded-lg">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-gray-50 z-10">
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 px-3 font-semibold sticky left-0 bg-gray-50 z-20 min-w-[180px]">Supersector</th>
                      <th className="py-2 px-2 text-center min-w-[60px]">Chart</th>
                      {supersectorTimeline?.timeline?.slice().reverse().map((point, idx) => (
                        <th
                          key={`${point.year}-${point.period}`}
                          className={`text-right py-2 px-2 font-semibold min-w-[75px] whitespace-nowrap ${idx === 0 ? 'bg-green-100' : ''}`}
                        >
                          {point.period_name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {supersectors?.supersectors?.map((ss) => (
                      <tr key={ss.supersector_code} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-2 px-3 font-medium sticky left-0 bg-white z-10">{ss.supersector_name}</td>
                        <td className="py-2 px-2 text-center">
                          <button
                            onClick={() => toggleSupersector(ss.supersector_code)}
                            className={`px-2 py-1 text-xs rounded ${
                              selectedSupersectors.includes(ss.supersector_code)
                                ? 'bg-green-500 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            {selectedSupersectors.includes(ss.supersector_code) ? '✓' : '+'}
                          </button>
                        </td>
                        {supersectorTimeline?.timeline?.slice().reverse().map((point, idx) => {
                          const value = point.supersectors?.[ss.supersector_code];
                          return (
                            <td
                              key={`${point.year}-${point.period}`}
                              className={`text-right py-2 px-2 font-mono text-xs ${idx === 0 ? 'bg-green-50 font-semibold text-green-700' : 'text-gray-700'}`}
                            >
                              {value != null ? value.toLocaleString() : '-'}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Supersector Timeline */}
              {selectedSupersectors.length > 0 && supersectorTimeline?.timeline?.length && supersectorTimeline.timeline.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">Selected Supersectors Timeline</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={supersectorTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => v?.toLocaleString()} />
                        <Tooltip formatter={(value) => [`${(value as number)?.toLocaleString() || 'N/A'}K`, '']} />
                        <Legend />
                        {selectedSupersectors.map((code, index) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`supersectors.${code}`}
                            stroke={CHART_COLORS[index % CHART_COLORS.length]}
                            name={supersectorTimeline.supersector_names?.[code] || code}
                            strokeWidth={2}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <TimelineSelector
                    timeline={supersectorTimeline.timeline}
                    selectedIndex={supersectorSelectedIndex}
                    onSelectIndex={setSupersectorSelectedIndex}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 3: Industry Analysis */}
      <Card>
        <SectionHeader title="Industry Analysis" color="orange" />
        <div className="p-5">
          {/* Filters */}
          <div className="flex gap-4 mb-4">
            <Select
              label="Display Level"
              value={industryDisplayLevel}
              onChange={setIndustryDisplayLevel}
              options={[
                { value: '', label: 'All Levels' },
                { value: '1', label: 'Level 1 (Broad)' },
                { value: '2', label: 'Level 2' },
                { value: '3', label: 'Level 3' },
                { value: '4', label: 'Level 4' },
                { value: '5', label: 'Level 5 (Detail)' },
              ]}
              className="w-40"
            />
            <Select
              label="Supersector"
              value={industrySupersector}
              onChange={setIndustrySupersector}
              options={[
                { value: '', label: 'All Supersectors' },
                ...(dimensions?.supersectors?.map(ss => ({ value: ss.supersector_code, label: ss.supersector_name })) || [])
              ]}
              className="w-48"
            />
            <Select
              label="Show"
              value={industryLimit}
              onChange={(v) => setIndustryLimit(parseInt(v))}
              options={[
                { value: 20, label: 'Top 20' },
                { value: 50, label: 'Top 50' },
                { value: 100, label: 'Top 100' },
              ]}
              className="w-32"
            />
            <Select
              label="Time Range"
              value={industryTimeRange}
              onChange={(v) => setIndustryTimeRange(parseInt(v))}
              options={timeRangeOptions}
              className="w-40"
            />
          </div>

          {loadingIndustries ? (
            <LoadingSpinner />
          ) : (
            <>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-gray-700">
                  Industry Details {industryPointData && `- ${industryPointData.period_name}`}
                </h3>
              </div>

              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white">
                    <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                      <th className="py-2 px-3 w-8">Chart</th>
                      <th className="py-2 px-3">Industry</th>
                      <th className="py-2 px-3 text-center">Level</th>
                      <th className="py-2 px-3 text-right">Employment</th>
                      <th className="py-2 px-3 text-right">MoM Change</th>
                      <th className="py-2 px-3 text-right">MoM %</th>
                      <th className="py-2 px-3 text-right">YoY Change</th>
                      <th className="py-2 px-3 text-right">YoY %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {industries?.industries?.map((ind) => {
                      const pointData = industryPointData?.data?.[ind.industry_code];
                      return (
                        <tr key={ind.industry_code} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <input
                              type="checkbox"
                              checked={selectedIndustries.includes(ind.industry_code)}
                              onChange={() => toggleIndustry(ind.industry_code)}
                              disabled={!selectedIndustries.includes(ind.industry_code) && selectedIndustries.length >= 5}
                              className="rounded"
                            />
                          </td>
                          <td className="py-2 px-3" style={{ paddingLeft: `${(ind.display_level - 1) * 16 + 12}px` }}>
                            {ind.industry_name}
                          </td>
                          <td className="py-2 px-3 text-center">
                            <span className="px-2 py-0.5 text-xs bg-gray-100 rounded">{ind.display_level}</span>
                          </td>
                          <td className="py-2 px-3 text-right font-semibold">
                            {(pointData?.value ?? ind.latest_value)?.toLocaleString()}K
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.mom_change ?? ind.month_over_month} suffix="K" />
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.mom_pct ?? ind.month_over_month_pct} suffix="%" />
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.yoy_change ?? ind.year_over_year} suffix="K" />
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.yoy_pct ?? ind.year_over_year_pct} suffix="%" />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {industries && (
                <p className="text-xs text-gray-500 mt-2">
                  Showing {industries.industries?.length} of {industries.total_count} industries • Data as of {industries.last_updated}
                </p>
              )}

              {/* Industry Timeline Chart/Table */}
              {selectedIndustries.length > 0 && industryTimeline?.timeline?.length && industryTimeline.timeline.length > 0 && (
                <div className="mt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-sm font-semibold text-gray-700">Selected Industries Timeline</h3>
                    <ViewToggle value={industryView} onChange={setIndustryView} />
                  </div>

                  {industryView === 'chart' ? (
                    <>
                      <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={industryTimeline.timeline}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => v?.toLocaleString()} />
                            <Tooltip formatter={(value) => [`${(value as number)?.toLocaleString() || 'N/A'}K`, '']} />
                            <Legend wrapperStyle={{ fontSize: '11px' }} />
                            {selectedIndustries.map((code, index) => (
                              <Line
                                key={code}
                                type="monotone"
                                dataKey={`industries.${code}`}
                                stroke={CHART_COLORS[index % CHART_COLORS.length]}
                                name={industryTimeline.industry_names?.[code] || code}
                                strokeWidth={2}
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
                  ) : (
                    <div className="overflow-x-auto max-h-[400px] border border-gray-200 rounded-lg">
                      <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-gray-50 z-10">
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-2 px-3 font-semibold sticky left-0 bg-gray-50 z-20 min-w-[200px]">Industry</th>
                            {industryTimeline.timeline.slice().reverse().map((point, idx) => (
                              <th
                                key={`${point.year}-${point.period}`}
                                className={`text-right py-2 px-2 font-semibold min-w-[75px] whitespace-nowrap ${idx === 0 ? 'bg-orange-100' : ''}`}
                              >
                                {point.period_name}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {selectedIndustries.map((code) => (
                            <tr key={code} className="border-b border-gray-100 hover:bg-gray-50">
                              <td className="py-2 px-3 font-medium sticky left-0 bg-white z-10">
                                {industryTimeline.industry_names?.[code] || code}
                              </td>
                              {industryTimeline.timeline.slice().reverse().map((point, idx) => {
                                const value = point.industries?.[code];
                                return (
                                  <td
                                    key={`${point.year}-${point.period}`}
                                    className={`text-right py-2 px-2 font-mono text-xs ${idx === 0 ? 'bg-orange-50 font-semibold text-orange-700' : 'text-gray-700'}`}
                                  >
                                    {value != null ? value.toLocaleString() : '-'}
                                  </td>
                                );
                              })}
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
      </Card>

      {/* Section 4: Earnings & Hours Analysis */}
      <Card>
        <SectionHeader title="Earnings & Hours Analysis" color="purple" icon={DollarSign} />
        <div className="p-5">
          {/* Filters */}
          <div className="flex gap-4 mb-4">
            <Select
              label="Supersector"
              value={earningsSupersector}
              onChange={setEarningsSupersector}
              options={[
                { value: '', label: 'All Supersectors' },
                ...(dimensions?.supersectors?.map(ss => ({ value: ss.supersector_code, label: ss.supersector_name })) || [])
              ]}
              className="w-48"
            />
            <Select
              label="Show"
              value={earningsLimit}
              onChange={(v) => setEarningsLimit(parseInt(v))}
              options={[
                { value: 20, label: 'Top 20' },
                { value: 50, label: 'Top 50' },
                { value: 100, label: 'Top 100' },
              ]}
              className="w-32"
            />
            <Select
              label="Time Range"
              value={earningsTimeRange}
              onChange={(v) => setEarningsTimeRange(parseInt(v))}
              options={timeRangeOptions}
              className="w-40"
            />
          </div>

          {loadingEarnings ? (
            <LoadingSpinner />
          ) : (
            <>
              <div className="overflow-x-auto max-h-80">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white">
                    <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                      <th className="py-2 px-3">Industry</th>
                      <th className="py-2 px-3 text-right">Hourly ($)</th>
                      <th className="py-2 px-3 text-right">Weekly ($)</th>
                      <th className="py-2 px-3 text-right">Hours/Week</th>
                      <th className="py-2 px-3 text-right">Hourly MoM</th>
                      <th className="py-2 px-3 text-right">Hourly YoY</th>
                      <th className="py-2 px-3 text-center">Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {earnings?.earnings?.map((e) => (
                      <tr
                        key={e.industry_code}
                        className={`border-b border-gray-100 cursor-pointer ${
                          selectedEarningsIndustry === e.industry_code ? 'bg-purple-50' : 'hover:bg-gray-50'
                        }`}
                        onClick={() => setSelectedEarningsIndustry(e.industry_code)}
                      >
                        <td className="py-2 px-3">{e.industry_name}</td>
                        <td className="py-2 px-3 text-right font-semibold">${e.avg_hourly_earnings?.toFixed(2) || 'N/A'}</td>
                        <td className="py-2 px-3 text-right">${e.avg_weekly_earnings?.toFixed(0) || 'N/A'}</td>
                        <td className="py-2 px-3 text-right">{e.avg_weekly_hours?.toFixed(1) || 'N/A'}</td>
                        <td className="py-2 px-3 text-right"><ChangeIndicator value={e.hourly_mom_pct} suffix="%" /></td>
                        <td className="py-2 px-3 text-right"><ChangeIndicator value={e.hourly_yoy_pct} suffix="%" /></td>
                        <td className="py-2 px-3 text-center">
                          <button
                            className={`px-2 py-1 text-xs rounded ${
                              selectedEarningsIndustry === e.industry_code
                                ? 'bg-purple-500 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            {selectedEarningsIndustry === e.industry_code ? 'Selected' : 'View'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {earnings && (
                <p className="text-xs text-gray-500 mt-2">
                  Showing {earnings.earnings?.length} of {earnings.total_count} industries • Data as of {earnings.last_updated}
                </p>
              )}

              {/* Earnings Timeline Chart/Table */}
              {selectedEarningsIndustry && earningsTimeline?.timeline?.length && earningsTimeline.timeline.length > 0 && (
                <div className="mt-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-sm font-semibold text-gray-700">
                      Earnings Trend: {earningsTimeline.industry_name}
                    </h3>
                    <ViewToggle value={earningsView} onChange={setEarningsView} />
                  </div>

                  {earningsView === 'chart' ? (
                    <>
                      {/* Point data summary */}
                      {earningsPointData && (
                        <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                          <div>
                            <p className="text-xs text-gray-500">Hourly Earnings</p>
                            <p className="font-semibold">${earningsPointData.data.avg_hourly_earnings?.value?.toFixed(2) || 'N/A'}</p>
                            <div className="flex gap-2 text-xs">
                              <span>MoM: <ChangeIndicator value={earningsPointData.data.avg_hourly_earnings?.mom_pct} suffix="%" /></span>
                            </div>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Weekly Earnings</p>
                            <p className="font-semibold">${earningsPointData.data.avg_weekly_earnings?.value?.toFixed(0) || 'N/A'}</p>
                            <div className="flex gap-2 text-xs">
                              <span>MoM: <ChangeIndicator value={earningsPointData.data.avg_weekly_earnings?.mom_pct} suffix="%" /></span>
                            </div>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Hours/Week</p>
                            <p className="font-semibold">{earningsPointData.data.avg_weekly_hours?.value?.toFixed(1) || 'N/A'}</p>
                            <div className="flex gap-2 text-xs">
                              <span>MoM: <ChangeIndicator value={earningsPointData.data.avg_weekly_hours?.mom_pct} suffix="%" /></span>
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={earningsTimeline.timeline}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                            <YAxis yAxisId="left" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
                            <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
                            <Tooltip
                              formatter={(value, name) => {
                                if (name === 'Hours/Week') return [(value as number)?.toFixed(1), name];
                                return [`$${(value as number)?.toFixed(2)}`, name];
                              }}
                            />
                            <Legend />
                            <Line yAxisId="left" type="monotone" dataKey="avg_hourly_earnings" stroke="#8b5cf6" name="Hourly Earnings" strokeWidth={2} dot={false} />
                            <Line yAxisId="right" type="monotone" dataKey="avg_weekly_hours" stroke="#10b981" name="Hours/Week" strokeWidth={2} dot={false} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>

                      <TimelineSelector
                        timeline={earningsTimeline.timeline}
                        selectedIndex={earningsSelectedIndex}
                        onSelectIndex={setEarningsSelectedIndex}
                      />
                    </>
                  ) : (
                    <div className="overflow-x-auto max-h-[300px] border border-gray-200 rounded-lg">
                      <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-gray-50 z-10">
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-2 px-3 font-semibold sticky left-0 bg-gray-50 z-20 min-w-[140px]">Metric</th>
                            {earningsTimeline.timeline.slice().reverse().map((point, idx) => (
                              <th
                                key={`${point.year}-${point.period}`}
                                className={`text-right py-2 px-2 font-semibold min-w-[80px] whitespace-nowrap ${idx === 0 ? 'bg-purple-100' : ''}`}
                              >
                                {point.period_name}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          <tr className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-2 px-3 font-medium sticky left-0 bg-white z-10">Hourly Earnings ($)</td>
                            {earningsTimeline.timeline.slice().reverse().map((point, idx) => (
                              <td
                                key={`hourly-${point.year}-${point.period}`}
                                className={`text-right py-2 px-2 font-mono text-xs ${idx === 0 ? 'bg-purple-50 font-semibold text-purple-700' : 'text-gray-700'}`}
                              >
                                {point.avg_hourly_earnings != null ? `$${point.avg_hourly_earnings.toFixed(2)}` : '-'}
                              </td>
                            ))}
                          </tr>
                          <tr className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-2 px-3 font-medium sticky left-0 bg-white z-10">Weekly Earnings ($)</td>
                            {earningsTimeline.timeline.slice().reverse().map((point, idx) => (
                              <td
                                key={`weekly-${point.year}-${point.period}`}
                                className={`text-right py-2 px-2 font-mono text-xs ${idx === 0 ? 'bg-purple-50 font-semibold text-purple-700' : 'text-gray-700'}`}
                              >
                                {point.avg_weekly_earnings != null ? `$${point.avg_weekly_earnings.toFixed(0)}` : '-'}
                              </td>
                            ))}
                          </tr>
                          <tr className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-2 px-3 font-medium sticky left-0 bg-white z-10">Hours/Week</td>
                            {earningsTimeline.timeline.slice().reverse().map((point, idx) => (
                              <td
                                key={`hours-${point.year}-${point.period}`}
                                className={`text-right py-2 px-2 font-mono text-xs ${idx === 0 ? 'bg-purple-50 font-semibold text-purple-700' : 'text-gray-700'}`}
                              >
                                {point.avg_weekly_hours != null ? point.avg_weekly_hours.toFixed(1) : '-'}
                              </td>
                            ))}
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 5: Series Explorer */}
      <Card>
        <SectionHeader title="Series Explorer" color="cyan" />
        <div className="p-5">
          {/* Filters */}
          <div className="grid grid-cols-4 gap-4 mb-4">
            <Select
              label="Industry"
              value={selectedIndustry}
              onChange={setSelectedIndustry}
              options={[
                { value: '', label: 'All Industries' },
                ...selectableIndustries.map(i => ({ value: i.industry_code, label: i.industry_name }))
              ]}
            />
            <Select
              label="Supersector"
              value={selectedSupersectorFilter}
              onChange={setSelectedSupersectorFilter}
              options={[
                { value: '', label: 'All Supersectors' },
                ...(dimensions?.supersectors?.map(ss => ({ value: ss.supersector_code, label: ss.supersector_name })) || [])
              ]}
            />
            <Select
              label="Data Type"
              value={selectedDataTypeFilter}
              onChange={setSelectedDataTypeFilter}
              options={[
                { value: '', label: 'All Data Types' },
                ...(dimensions?.data_types?.map(dt => ({
                  value: dt.data_type_code,
                  label: dt.data_type_text?.length > 40 ? dt.data_type_text.substring(0, 40) + '...' : dt.data_type_text
                })) || [])
              ]}
            />
            <Select
              label="Seasonal Adjustment"
              value={selectedSeasonal}
              onChange={setSelectedSeasonal}
              options={[
                { value: '', label: 'All' },
                { value: 'S', label: 'Seasonally Adjusted' },
                { value: 'U', label: 'Not Adjusted' },
              ]}
            />
          </div>

          {/* Series List */}
          <div className="border border-gray-200 rounded-lg mb-4">
            <div className="px-4 py-2 border-b border-gray-200 flex justify-between items-center bg-gray-50">
              <div>
                <p className="text-sm font-semibold text-gray-700">Available Series ({seriesData?.total || 0})</p>
                <p className="text-xs text-gray-500">Select series to compare (max 5)</p>
              </div>
              {selectedSeriesIds.length > 0 && (
                <button
                  onClick={() => setSelectedSeriesIds([])}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100"
                >
                  Clear All ({selectedSeriesIds.length})
                </button>
              )}
            </div>
            <div className="overflow-x-auto max-h-64">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-50">
                  <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                    <th className="py-2 px-3 w-8"></th>
                    <th className="py-2 px-3">Series ID</th>
                    <th className="py-2 px-3">Industry</th>
                    <th className="py-2 px-3">Data Type</th>
                    <th className="py-2 px-3">Seasonal</th>
                    <th className="py-2 px-3">Period</th>
                  </tr>
                </thead>
                <tbody>
                  {loadingSeries ? (
                    <tr><td colSpan={6} className="py-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-gray-400" /></td></tr>
                  ) : seriesData?.series?.length === 0 ? (
                    <tr><td colSpan={6} className="py-8 text-center text-gray-500">No series found. Try adjusting filters.</td></tr>
                  ) : (
                    seriesData?.series?.map((series) => (
                      <tr
                        key={series.series_id}
                        className={`border-b border-gray-100 cursor-pointer ${
                          selectedSeriesIds.includes(series.series_id) ? 'bg-cyan-50' : 'hover:bg-gray-50'
                        }`}
                        onClick={() => {
                          if (selectedSeriesIds.includes(series.series_id)) {
                            setSelectedSeriesIds(selectedSeriesIds.filter(id => id !== series.series_id));
                          } else if (selectedSeriesIds.length < 5) {
                            setSelectedSeriesIds([...selectedSeriesIds, series.series_id]);
                          }
                        }}
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
                        <td className="py-2 px-3 text-xs">{series.industry_name}</td>
                        <td className="py-2 px-3 text-xs">
                          {series.data_type_text && series.data_type_text.length > 30 ? series.data_type_text.substring(0, 30) + '...' : series.data_type_text || 'N/A'}
                        </td>
                        <td className="py-2 px-3">
                          <span className="px-2 py-0.5 text-xs bg-gray-100 rounded">
                            {series.seasonal_code === 'S' ? 'SA' : 'NSA'}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Chart/Table for Selected Series */}
          {selectedSeriesIds.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-2 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <div>
                  <p className="text-sm font-semibold text-gray-700">
                    {seriesView === 'chart' ? 'Series Comparison Chart' : 'Series Data Table'}
                  </p>
                  <p className="text-xs text-gray-500">{selectedSeriesIds.length} series selected</p>
                </div>
                <div className="flex gap-2 items-center">
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
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      {selectedSeriesIds.map((seriesId, idx) => {
                        const chartData = seriesChartData[seriesId];
                        if (!chartData?.series?.[0]) return null;
                        const seriesInfo = seriesData?.series?.find(s => s.series_id === seriesId);
                        const label = seriesInfo
                          ? `${seriesInfo.industry_name} - ${seriesInfo.data_type_text?.substring(0, 20) || 'N/A'}`
                          : seriesId;
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
                            name={label.length > 40 ? label.substring(0, 37) + '...' : label}
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
                          const seriesInfo = seriesData?.series?.find(s => s.series_id === seriesId);
                          return (
                            <th key={seriesId} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                              <div>{seriesInfo?.industry_name?.substring(0, 25)}</div>
                              <div className="font-normal text-gray-400">{seriesInfo?.data_type_text?.substring(0, 20) || 'N/A'}</div>
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
                            <td className="py-2 px-3 font-medium">{period.period_name}</td>
                            {selectedSeriesIds.map((seriesId) => (
                              <td key={seriesId} className="py-2 px-3 text-right">
                                {period.values[seriesId] != null ? period.values[seriesId].toLocaleString(undefined, { maximumFractionDigits: 1 }) : '-'}
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
