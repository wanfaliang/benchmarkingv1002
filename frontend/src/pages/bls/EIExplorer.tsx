import { useState, useEffect, useMemo, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, Globe, ArrowUpCircle, ArrowDownCircle, Ship, Plane, LucideIcon, Search, Factory } from 'lucide-react';
import { eiResearchAPI } from '../../services/api';

/**
 * EI Explorer - Import/Export Price Index Explorer
 *
 * Tracks merchandise import and export price indexes based on:
 * - BEA End Use classification
 * - NAICS classification
 * - Harmonized System classification
 * - Country/Region of origin (imports) and destination (exports)
 * - Services trade indexes
 * - Terms of Trade
 *
 * Sections:
 * 1. Overview - All imports/exports, ex fuel, terms of trade
 * 2. Country Comparison - Price indexes by import origin / export destination
 * 3. Trade Flow - Special visualization of import/export flows by country
 * 4. Index Categories - BEA, NAICS, Harmonized System breakdowns
 * 5. Services Trade - Import/export service indexes
 * 6. Terms of Trade - Price competitiveness indexes
 * 7. Top Movers - Biggest price gainers and losers
 * 8. Series Explorer - Search and chart specific series (THREE methods stacked)
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
  all_imports?: number | null;
  all_exports?: number | null;
  imports_ex_fuel?: number | null;
  exports_ex_fuel?: number | null;
  terms_of_trade?: number | null;
  values?: Record<string, number | null>;
  [key: string]: unknown;
}

interface OverviewMetric {
  metric_name: string;
  series_id: string;
  index_code: string;
  current_value?: number | null;
  previous_value?: number | null;
  mom_change?: number | null;
  yoy_change?: number | null;
  yoy_pct_change?: number | null;
}

interface OverviewData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  all_imports?: OverviewMetric | null;
  all_exports?: OverviewMetric | null;
  imports_ex_fuel?: OverviewMetric | null;
  exports_ex_fuel?: OverviewMetric | null;
  terms_of_trade?: OverviewMetric | null;
  import_metrics: OverviewMetric[];
  export_metrics: OverviewMetric[];
  available_years: number[];
  available_periods: string[];
}

interface OverviewTimelineData {
  survey_code: string;
  data: TimelinePoint[];
}

interface CountryItem {
  country_code: string;
  country_name: string;
  current_value?: number | null;
  previous_value?: number | null;
  mom_change?: number | null;
  yoy_change?: number | null;
  yoy_pct_change?: number | null;
}

interface CountryComparisonData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  direction: string;
  industry_filter?: string | null;
  countries: CountryItem[];
}

interface CountryTimelineData {
  survey_code: string;
  direction: string;
  industry_filter?: string | null;
  countries: { country_code: string; country_name: string }[];
  data: TimelinePoint[];
}

interface TradeFlowItem {
  country_code: string;
  country_name: string;
  direction: string;
  value?: number | null;
  change?: number | null;
  pct_of_total?: number | null;
}

interface TradeFlowData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  base_country: string;
  imports: TradeFlowItem[];
  exports: TradeFlowItem[];
  total_import_index?: number | null;
  total_export_index?: number | null;
  terms_of_trade?: number | null;
}

interface TradeBalanceItem {
  country_code: string;
  country_name: string;
  import_index?: number | null;
  export_index?: number | null;
  price_differential?: number | null;
}

interface TradeBalanceData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  countries: TradeBalanceItem[];
}

interface IndexCategoryItem {
  series_id: string;
  series_name: string;
  index_code: string;
  current_value?: number | null;
  mom_change?: number | null;
  yoy_change?: number | null;
}

interface IndexCategoryData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  direction: string;
  classification: string;
  categories: IndexCategoryItem[];
}

interface ServicesItem {
  series_id: string;
  series_name: string;
  direction: string;
  current_value?: number | null;
  mom_change?: number | null;
  yoy_change?: number | null;
}

interface ServicesData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  import_services: ServicesItem[];
  export_services: ServicesItem[];
  inbound_services: ServicesItem[];
  outbound_services: ServicesItem[];
}

interface TermsOfTradeItem {
  series_id: string;
  series_name: string;
  current_value?: number | null;
  mom_change?: number | null;
  yoy_change?: number | null;
}

interface TermsOfTradeData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  terms: TermsOfTradeItem[];
}

interface TopMoverItem {
  series_id: string;
  series_name: string;
  index_code: string;
  country_region?: string | null;
  current_value?: number | null;
  change?: number | null;
  pct_change?: number | null;
}

interface TopMoversData {
  survey_code: string;
  year: number;
  period: string;
  period_name: string;
  direction: string;
  metric: string;
  top_gainers: TopMoverItem[];
  top_losers: TopMoverItem[];
}

interface SeriesInfo {
  series_id: string;
  seasonal_code?: string | null;
  index_code?: string | null;
  index_name?: string | null;
  series_name?: string | null;
  base_period?: string | null;
  series_title?: string | null;
  begin_year?: number | null;
  begin_period?: string | null;
  end_year?: number | null;
  end_period?: string | null;
  is_active?: boolean;
  country_region?: string | null;
  industry_category?: string | null;
}

interface SeriesListData {
  survey_code: string;
  total: number;
  limit: number;
  offset: number;
  series: SeriesInfo[];
}

interface DataPoint {
  year: number;
  period: string;
  period_name: string;
  value?: number | null;
  footnote_codes?: string | null;
}

interface SeriesDataItem {
  series_id: string;
  series_info: SeriesInfo;
  data_points: DataPoint[];
}

interface SeriesDataResponse {
  survey_code: string;
  series_count: number;
  total_observations: number;
  series: SeriesDataItem[];
}

interface DimensionsData {
  indexes: { index_code: string; index_name: string; category?: string }[];
  import_indexes: { index_code: string; index_name: string; category?: string }[];
  export_indexes: { index_code: string; index_name: string; category?: string }[];
  origin_countries: { country_code: string; country_name: string; series_count: number }[];
  destination_countries: { country_code: string; country_name: string; series_count: number }[];
  available_years: number[];
  available_periods: string[];
}

type ViewType = 'table' | 'chart';
type SectionColor = 'blue' | 'green' | 'orange' | 'purple' | 'cyan' | 'red' | 'indigo' | 'teal';
type MoverPeriod = 'mom_change' | 'yoy_change';

// ============================================================================
// CONSTANTS
// ============================================================================

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'];
const IMPORT_COLOR = '#ef4444';  // Red for imports
const EXPORT_COLOR = '#10b981';  // Green for exports

const timeRangeOptions: TimeRangeOption[] = [
  { value: 12, label: 'Last 12 months' },
  { value: 24, label: 'Last 2 years' },
  { value: 60, label: 'Last 5 years' },
  { value: 120, label: 'Last 10 years' },
  { value: 240, label: 'Last 20 years' },
  { value: 0, label: 'All Time' },
];

const getStartYearFromRange = (range: number): number | undefined => {
  if (range === 0) return undefined; // All time
  const currentYear = new Date().getFullYear();
  return currentYear - Math.ceil(range / 12);
};

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

const formatPeriod = (periodCode: string | undefined | null): string => {
  if (!periodCode) return '';
  const monthMap: Record<string, string> = {
    'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
    'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
    'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
    'M13': 'Annual',
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
    red: 'border-red-500 bg-red-50 text-red-700',
    indigo: 'border-indigo-500 bg-indigo-50 text-indigo-700',
    teal: 'border-teal-500 bg-teal-50 text-teal-700',
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

interface MetricCardProps {
  title: string;
  value: number | null | undefined;
  change?: number | null;
  changeLabel?: string;
  color?: 'blue' | 'green' | 'red' | 'orange' | 'purple';
  icon?: LucideIcon;
}

const MetricCard = ({ title, value, change, changeLabel = 'YoY', color = 'blue', icon: Icon }: MetricCardProps): ReactElement => {
  const colorClasses = {
    blue: 'border-blue-200 bg-blue-50',
    green: 'border-green-200 bg-green-50',
    red: 'border-red-200 bg-red-50',
    orange: 'border-orange-200 bg-orange-50',
    purple: 'border-purple-200 bg-purple-50',
  };

  return (
    <div className={`p-4 rounded-lg border ${colorClasses[color]}`}>
      <div className="flex items-center gap-2 mb-2">
        {Icon && <Icon className="w-4 h-4 text-gray-600" />}
        <span className="text-xs font-medium text-gray-600 uppercase">{title}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900">{formatIndex(value)}</div>
      {change !== undefined && (
        <div className="mt-1 flex items-center gap-2">
          <span className="text-xs text-gray-500">{changeLabel}:</span>
          <ChangeIndicator value={change} suffix="%" />
        </div>
      )}
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function EIExplorer(): ReactElement {
  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);
  const [, setLoadingDimensions] = useState(true);

  // Section 1: Overview
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeRange, setOverviewTimeRange] = useState(24);
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [overviewSelectedIndex, setOverviewSelectedIndex] = useState<number | null>(null);
  const [overviewView, setOverviewView] = useState<ViewType>('chart');

  // Section 2: Country Comparison
  const [countryDirection, setCountryDirection] = useState('import');
  const [countryComparison, setCountryComparison] = useState<CountryComparisonData | null>(null);
  const [loadingCountries, setLoadingCountries] = useState(true);
  const [countryTimeRange, setCountryTimeRange] = useState(60);
  const [countryTimeline, setCountryTimeline] = useState<CountryTimelineData | null>(null);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [countrySelectedIndex, setCountrySelectedIndex] = useState<number | null>(null);
  const [countryView, setCountryView] = useState<ViewType>('chart');

  // Section 3: Trade Flow
  const [tradeFlow, setTradeFlow] = useState<TradeFlowData | null>(null);
  const [loadingTradeFlow, setLoadingTradeFlow] = useState(true);
  const [tradeBalance, setTradeBalance] = useState<TradeBalanceData | null>(null);
  const [tradeFlowView, setTradeFlowView] = useState<ViewType>('chart');

  // Section 4: Index Categories
  const [categoryDirection, setCategoryDirection] = useState('import');
  const [categoryClassification, setCategoryClassification] = useState('BEA');
  const [categories, setCategories] = useState<IndexCategoryData | null>(null);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [categoryTimeRange, setCategoryTimeRange] = useState(24);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [categoryView, setCategoryView] = useState<ViewType>('chart');

  // Section 5: Services Trade
  const [services, setServices] = useState<ServicesData | null>(null);
  const [loadingServices, setLoadingServices] = useState(true);
  const [servicesView, setServicesView] = useState<ViewType>('table');

  // Section 6: Terms of Trade
  const [termsOfTrade, setTermsOfTrade] = useState<TermsOfTradeData | null>(null);
  const [loadingTerms, setLoadingTerms] = useState(true);
  const [termsTimeRange, setTermsTimeRange] = useState(60);
  const [termsView, setTermsView] = useState<ViewType>('chart');

  // Section 7: Top Movers
  const [topMovers, setTopMovers] = useState<TopMoversData | null>(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(true);
  const [moverDirection, setMoverDirection] = useState('all');
  const [moverMetric, setMoverMetric] = useState<MoverPeriod>('yoy_change');

  // Section 8: Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Series Explorer - Index Code Filter
  const [filterIndexCode, setFilterIndexCode] = useState('');
  const [filterResults, setFilterResults] = useState<SeriesListData | null>(null);
  const [loadingFilter, setLoadingFilter] = useState(false);
  const [filterOffset, setFilterOffset] = useState(0);
  const [filterLimit] = useState(50);

  // Series Explorer - Paginated Browse
  const [browseCountry, setBrowseCountry] = useState('');
  const [browseLimit, setBrowseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series Explorer - Shared
  const [selectedSeriesIds, setSelectedSeriesIds] = useState<string[]>([]);
  const [seriesTimeRange, setSeriesTimeRange] = useState(60);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');
  const [seriesChartData, setSeriesChartData] = useState<Record<string, SeriesDataResponse>>({});
  const [allSeriesInfo, setAllSeriesInfo] = useState<Record<string, SeriesInfo>>({});

  // Load dimensions on mount
  useEffect(() => {
    const load = async () => {
      try {
        const res = await eiResearchAPI.getDimensions();
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
        const res = await eiResearchAPI.getOverview();
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
        const startYear = getStartYearFromRange(overviewTimeRange);
        const res = await eiResearchAPI.getOverviewTimeline(startYear);
        const data = res.data as OverviewTimelineData;
        setOverviewTimeline(data);
        if (data?.data?.length > 0) {
          setOverviewSelectedIndex(data.data.length - 1);
        }
      } catch (error) {
        console.error('Failed to load overview timeline:', error);
      }
    };
    load();
  }, [overviewTimeRange]);

  // Load country comparison
  useEffect(() => {
    const load = async () => {
      setLoadingCountries(true);
      try {
        const res = await eiResearchAPI.getCountryComparison(countryDirection);
        const data = res.data as CountryComparisonData;
        setCountryComparison(data);
        // Pre-select top 5 countries
        if (data?.countries?.length > 0 && selectedCountries.length === 0) {
          setSelectedCountries(data.countries.slice(0, 5).map(c => c.country_name));
        }
      } catch (error) {
        console.error('Failed to load country comparison:', error);
      } finally {
        setLoadingCountries(false);
      }
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [countryDirection]);

  // Load country timeline
  useEffect(() => {
    const load = async () => {
      if (selectedCountries.length === 0) return;
      try {
        const startYear = getStartYearFromRange(countryTimeRange);
        const res = await eiResearchAPI.getCountryTimeline(
          selectedCountries.join(','),
          countryDirection,
          undefined,
          startYear
        );
        const data = res.data as CountryTimelineData;
        setCountryTimeline(data);
        if (data?.data?.length > 0) {
          setCountrySelectedIndex(data.data.length - 1);
        }
      } catch (error) {
        console.error('Failed to load country timeline:', error);
      }
    };
    load();
  }, [selectedCountries, countryDirection, countryTimeRange]);

  // Load trade flow
  useEffect(() => {
    const load = async () => {
      setLoadingTradeFlow(true);
      try {
        const [flowRes, balanceRes] = await Promise.all([
          eiResearchAPI.getTradeFlow(),
          eiResearchAPI.getTradeBalance()
        ]);
        setTradeFlow(flowRes.data as TradeFlowData);
        setTradeBalance(balanceRes.data as TradeBalanceData);
      } catch (error) {
        console.error('Failed to load trade flow:', error);
      } finally {
        setLoadingTradeFlow(false);
      }
    };
    load();
  }, []);

  // Load index categories
  useEffect(() => {
    const load = async () => {
      setLoadingCategories(true);
      try {
        const res = await eiResearchAPI.getCategories(categoryDirection, categoryClassification);
        const data = res.data as IndexCategoryData;
        setCategories(data);
        // Pre-select first 5 categories
        if (data?.categories?.length > 0) {
          setSelectedCategories(data.categories.slice(0, 5).map(c => c.series_id));
        }
      } catch (error) {
        console.error('Failed to load categories:', error);
      } finally {
        setLoadingCategories(false);
      }
    };
    load();
  }, [categoryDirection, categoryClassification]);

  // Load services
  useEffect(() => {
    const load = async () => {
      setLoadingServices(true);
      try {
        const res = await eiResearchAPI.getServices();
        setServices(res.data as ServicesData);
      } catch (error) {
        console.error('Failed to load services:', error);
      } finally {
        setLoadingServices(false);
      }
    };
    load();
  }, []);

  // Load terms of trade
  useEffect(() => {
    const load = async () => {
      setLoadingTerms(true);
      try {
        const res = await eiResearchAPI.getTermsOfTrade();
        setTermsOfTrade(res.data as TermsOfTradeData);
      } catch (error) {
        console.error('Failed to load terms of trade:', error);
      } finally {
        setLoadingTerms(false);
      }
    };
    load();
  }, []);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await eiResearchAPI.getTopMovers(moverDirection, moverMetric, 10);
        setTopMovers(res.data as TopMoversData);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [moverDirection, moverMetric]);

  // Load paginated browse results
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params: Record<string, unknown> = { limit: browseLimit, offset: browseOffset };
        if (browseCountry) params.country = browseCountry;
        const res = await eiResearchAPI.getSeries(params);
        setBrowseResults(res.data as SeriesListData);
      } catch (error) {
        console.error('Failed to load browse results:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    load();
  }, [browseCountry, browseLimit, browseOffset]);

  // Load series chart data when selected series change
  useEffect(() => {
    const load = async () => {
      if (selectedSeriesIds.length === 0) return;
      try {
        const startYear = getStartYearFromRange(seriesTimeRange);
        const res = await eiResearchAPI.getData(selectedSeriesIds.join(','), startYear);
        const data = res.data as SeriesDataResponse;
        const newChartData: Record<string, SeriesDataResponse> = {};
        data.series.forEach(s => {
          newChartData[s.series_id] = data;
        });
        setSeriesChartData(prev => ({ ...prev, ...newChartData }));
        // Update series info
        const newInfo: Record<string, SeriesInfo> = {};
        data.series.forEach(s => {
          newInfo[s.series_id] = s.series_info;
        });
        setAllSeriesInfo(prev => ({ ...prev, ...newInfo }));
      } catch (error) {
        console.error('Failed to load series data:', error);
      }
    };
    load();
  }, [selectedSeriesIds, seriesTimeRange]);

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await eiResearchAPI.getSeries({ search: searchQuery, limit: 50 });
      setSearchResults(res.data as SeriesListData);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  // Filter by index code handler
  const handleFilter = async () => {
    if (!filterIndexCode) return;
    setLoadingFilter(true);
    setFilterOffset(0);
    try {
      const res = await eiResearchAPI.getSeries({ index_code: filterIndexCode, limit: filterLimit, offset: 0 });
      setFilterResults(res.data as SeriesListData);
    } catch (error) {
      console.error('Filter failed:', error);
    } finally {
      setLoadingFilter(false);
    }
  };

  // Load more filter results
  const loadMoreFilterResults = async () => {
    if (!filterIndexCode) return;
    setLoadingFilter(true);
    const newOffset = filterOffset + filterLimit;
    try {
      const res = await eiResearchAPI.getSeries({ index_code: filterIndexCode, limit: filterLimit, offset: newOffset });
      const data = res.data as SeriesListData;
      setFilterResults(prev => prev ? {
        ...prev,
        series: [...prev.series, ...data.series],
        offset: newOffset
      } : data);
      setFilterOffset(newOffset);
    } catch (error) {
      console.error('Load more failed:', error);
    } finally {
      setLoadingFilter(false);
    }
  };

  // Toggle series selection
  const toggleSeriesSelection = (seriesId: string, info?: SeriesInfo) => {
    setSelectedSeriesIds(prev => {
      if (prev.includes(seriesId)) {
        return prev.filter(id => id !== seriesId);
      }
      if (prev.length >= 5) {
        return prev; // Max 5 series
      }
      return [...prev, seriesId];
    });
    if (info) {
      setAllSeriesInfo(prev => ({ ...prev, [seriesId]: info }));
    }
  };

  // Toggle country selection
  const toggleCountrySelection = (countryName: string) => {
    setSelectedCountries(prev => {
      if (prev.includes(countryName)) {
        return prev.filter(c => c !== countryName);
      }
      if (prev.length >= 8) {
        return prev; // Max 8 countries
      }
      return [...prev, countryName];
    });
  };

  // Toggle category selection
  const toggleCategorySelection = (seriesId: string) => {
    setSelectedCategories(prev => {
      if (prev.includes(seriesId)) {
        return prev.filter(id => id !== seriesId);
      }
      if (prev.length >= 8) {
        return prev;
      }
      return [...prev, seriesId];
    });
  };

  // Prepare chart data for overview timeline
  const overviewChartData = useMemo(() => {
    if (!overviewTimeline?.data) return [];
    return overviewTimeline.data.map(point => ({
      name: `${formatPeriod(point.period)} ${point.year}`,
      'All Imports': point.all_imports,
      'All Exports': point.all_exports,
      'Imports ex Fuel': point.imports_ex_fuel,
      'Exports ex Fuel': point.exports_ex_fuel,
    }));
  }, [overviewTimeline]);

  // Prepare chart data for country timeline
  const countryChartData = useMemo(() => {
    if (!countryTimeline?.data) return [];
    return countryTimeline.data.map(point => {
      const item: Record<string, unknown> = {
        name: `${formatPeriod(point.period)} ${point.year}`,
      };
      if (point.values) {
        Object.entries(point.values).forEach(([country, value]) => {
          item[country] = value;
        });
      }
      return item;
    });
  }, [countryTimeline]);

  // Prepare series chart data
  const combinedSeriesChartData = useMemo(() => {
    if (selectedSeriesIds.length === 0) return [];

    // Get all data points from all selected series
    const allPoints: Map<string, Record<string, unknown>> = new Map();

    Object.values(seriesChartData).forEach(response => {
      response.series.forEach(s => {
        if (!selectedSeriesIds.includes(s.series_id)) return;
        s.data_points.forEach(point => {
          const key = `${point.year}-${point.period}`;
          if (!allPoints.has(key)) {
            allPoints.set(key, {
              name: `${formatPeriod(point.period)} ${point.year}`,
              year: point.year,
              period: point.period,
            });
          }
          const existing = allPoints.get(key)!;
          existing[s.series_id] = point.value;
        });
      });
    });

    return Array.from(allPoints.values()).sort((a, b) => {
      if (a.year !== b.year) return (a.year as number) - (b.year as number);
      return (a.period as string).localeCompare(b.period as string);
    });
  }, [seriesChartData, selectedSeriesIds]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <Globe className="w-7 h-7 text-blue-600" />
            EI - Import/Export Price Indexes
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            International price indexes for merchandise imports and exports by classification system and country/region
          </p>
        </div>
        {overview && (
          <div className="text-right text-sm text-gray-500">
            Data as of: {overview.period_name} {overview.year}
          </div>
        )}
      </div>

      {/* Section 1: Overview */}
      <Card>
        <SectionHeader title="Import/Export Price Index Overview" color="blue" icon={Globe} />
        <div className="p-5">
          {loadingOverview ? (
            <LoadingSpinner />
          ) : overview ? (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <MetricCard
                  title="All Imports"
                  value={overview.all_imports?.current_value}
                  change={overview.all_imports?.yoy_pct_change}
                  color="red"
                  icon={Ship}
                />
                <MetricCard
                  title="All Exports"
                  value={overview.all_exports?.current_value}
                  change={overview.all_exports?.yoy_pct_change}
                  color="green"
                  icon={Plane}
                />
                <MetricCard
                  title="Imports ex Fuel"
                  value={overview.imports_ex_fuel?.current_value}
                  change={overview.imports_ex_fuel?.yoy_pct_change}
                  color="orange"
                />
                <MetricCard
                  title="Exports ex Fuel"
                  value={overview.exports_ex_fuel?.current_value}
                  change={overview.exports_ex_fuel?.yoy_pct_change}
                  color="purple"
                />
                <MetricCard
                  title="Terms of Trade"
                  value={overview.terms_of_trade?.current_value}
                  change={overview.terms_of_trade?.yoy_pct_change}
                  color="blue"
                />
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between mb-4">
                <Select
                  label="Time Range"
                  value={overviewTimeRange}
                  onChange={(v) => setOverviewTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
                <ViewToggle value={overviewView} onChange={setOverviewView} />
              </div>

              {/* Timeline Selector */}
              {overviewTimeline?.data && (
                <TimelineSelector
                  timeline={overviewTimeline.data}
                  selectedIndex={overviewSelectedIndex}
                  onSelectIndex={setOverviewSelectedIndex}
                />
              )}

              {/* Chart or Table */}
              {overviewView === 'chart' ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={overviewChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="All Imports" stroke={IMPORT_COLOR} strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="All Exports" stroke={EXPORT_COLOR} strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="Imports ex Fuel" stroke="#f59e0b" strokeWidth={1} dot={false} strokeDasharray="5 5" />
                      <Line type="monotone" dataKey="Exports ex Fuel" stroke="#8b5cf6" strokeWidth={1} dot={false} strokeDasharray="5 5" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium text-gray-600">Metric</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">Current</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">Previous</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">MoM Change</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">YoY Change</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {overview.import_metrics.concat(overview.export_metrics).map((metric, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-4 py-2 font-medium">{metric.metric_name}</td>
                          <td className="px-4 py-2 text-right">{formatIndex(metric.current_value)}</td>
                          <td className="px-4 py-2 text-right">{formatIndex(metric.previous_value)}</td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={metric.mom_change} /></td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={metric.yoy_pct_change} suffix="%" /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </Card>

      {/* Section 2: Country Comparison */}
      <Card>
        <SectionHeader title="Price Index by Country/Region" color="green" icon={Globe} />
        <div className="p-5">
          {loadingCountries ? (
            <LoadingSpinner />
          ) : countryComparison ? (
            <>
              {/* Controls */}
              <div className="flex flex-wrap items-center gap-4 mb-4">
                <Select
                  label="Direction"
                  value={countryDirection}
                  onChange={setCountryDirection}
                  options={[
                    { value: 'import', label: 'Import (by Origin)' },
                    { value: 'export', label: 'Export (by Destination)' },
                  ]}
                  className="w-48"
                />
                <Select
                  label="Time Range"
                  value={countryTimeRange}
                  onChange={(v) => setCountryTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
                <div className="ml-auto">
                  <ViewToggle value={countryView} onChange={setCountryView} />
                </div>
              </div>

              {/* Country Selection */}
              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-2">Select countries to compare (max 8, click to toggle):</p>
                <div className="flex flex-wrap gap-2">
                  {countryComparison.countries.slice(0, 20).map((country) => (
                    <button
                      key={country.country_code}
                      onClick={() => toggleCountrySelection(country.country_name)}
                      className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                        selectedCountries.includes(country.country_name)
                          ? 'bg-blue-500 text-white border-blue-500'
                          : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                      }`}
                    >
                      {country.country_name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Timeline Selector */}
              {countryTimeline?.data && (
                <TimelineSelector
                  timeline={countryTimeline.data}
                  selectedIndex={countrySelectedIndex}
                  onSelectIndex={setCountrySelectedIndex}
                />
              )}

              {/* Chart or Table */}
              {countryView === 'chart' && countryChartData.length > 0 ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={countryChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Legend />
                      {selectedCountries.map((country, idx) => (
                        <Line
                          key={country}
                          type="monotone"
                          dataKey={country}
                          stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                          strokeWidth={2}
                          dot={false}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium text-gray-600">Country/Region</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">Index Value</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">MoM</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">YoY</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">YoY %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {countryComparison.countries.map((country) => (
                        <tr
                          key={country.country_code}
                          className={`hover:bg-gray-50 cursor-pointer ${selectedCountries.includes(country.country_name) ? 'bg-blue-50' : ''}`}
                          onClick={() => toggleCountrySelection(country.country_name)}
                        >
                          <td className="px-4 py-2 font-medium">{country.country_name}</td>
                          <td className="px-4 py-2 text-right">{formatIndex(country.current_value)}</td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={country.mom_change} /></td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={country.yoy_change} /></td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={country.yoy_pct_change} suffix="%" /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </Card>

      {/* Section 3: Trade Flow Visualization */}
      <Card>
        <SectionHeader title="Trade Flow by Country" color="orange" icon={Ship} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">
            Visualize import and export price indexes by country. The chart shows the price index level and change for top trading partners.
          </p>

          {loadingTradeFlow ? (
            <LoadingSpinner />
          ) : tradeFlow ? (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <MetricCard
                  title="Total Import Index"
                  value={tradeFlow.total_import_index}
                  color="red"
                  icon={Ship}
                />
                <MetricCard
                  title="Total Export Index"
                  value={tradeFlow.total_export_index}
                  color="green"
                  icon={Plane}
                />
                <MetricCard
                  title="Terms of Trade"
                  value={tradeFlow.terms_of_trade}
                  color="blue"
                />
              </div>

              <div className="flex items-center justify-end mb-4">
                <ViewToggle value={tradeFlowView} onChange={setTradeFlowView} />
              </div>

              {tradeFlowView === 'chart' ? (
                <div className="grid grid-cols-2 gap-6">
                  {/* Imports Chart */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-red-500"></div>
                      Import Price Index by Origin
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={tradeFlow.imports.slice(0, 10)} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis type="number" tick={{ fontSize: 10 }} />
                          <YAxis type="category" dataKey="country_name" tick={{ fontSize: 10 }} width={100} />
                          <Tooltip />
                          <Bar dataKey="value" fill={IMPORT_COLOR} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Exports Chart */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-green-500"></div>
                      Export Price Index by Destination
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={tradeFlow.exports.slice(0, 10)} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis type="number" tick={{ fontSize: 10 }} />
                          <YAxis type="category" dataKey="country_name" tick={{ fontSize: 10 }} width={100} />
                          <Tooltip />
                          <Bar dataKey="value" fill={EXPORT_COLOR} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-6">
                  {/* Imports Table */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Imports by Origin</h3>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="min-w-full text-sm">
                        <thead className="bg-red-50">
                          <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-600">Country</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">Index</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">Change</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {tradeFlow.imports.map((item) => (
                            <tr key={item.country_code} className="hover:bg-gray-50">
                              <td className="px-3 py-2">{item.country_name}</td>
                              <td className="px-3 py-2 text-right">{formatIndex(item.value)}</td>
                              <td className="px-3 py-2 text-right"><ChangeIndicator value={item.change} /></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Exports Table */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Exports by Destination</h3>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="min-w-full text-sm">
                        <thead className="bg-green-50">
                          <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-600">Country</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">Index</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">Change</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {tradeFlow.exports.map((item) => (
                            <tr key={item.country_code} className="hover:bg-gray-50">
                              <td className="px-3 py-2">{item.country_name}</td>
                              <td className="px-3 py-2 text-right">{formatIndex(item.value)}</td>
                              <td className="px-3 py-2 text-right"><ChangeIndicator value={item.change} /></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Trade Balance Section */}
              {tradeBalance && tradeBalance.countries.length > 0 && (
                <div className="mt-6 pt-6 border-t">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">Trade Price Differential by Country</h3>
                  <p className="text-xs text-gray-500 mb-4">
                    Shows the difference between export and import price indexes. Positive values indicate export prices are higher than import prices.
                  </p>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={tradeBalance.countries.filter(c => c.price_differential !== null).slice(0, 15)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="country_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={80} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Bar dataKey="price_differential" name="Price Differential">
                          {tradeBalance.countries.filter(c => c.price_differential !== null).slice(0, 15).map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={entry.price_differential && entry.price_differential >= 0 ? EXPORT_COLOR : IMPORT_COLOR}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </Card>

      {/* Section 4: Index Categories */}
      <Card>
        <SectionHeader title="Index Categories (BEA/NAICS/Harmonized)" color="purple" icon={Factory} />
        <div className="p-5">
          {loadingCategories ? (
            <LoadingSpinner />
          ) : categories ? (
            <>
              {/* Controls */}
              <div className="flex flex-wrap items-center gap-4 mb-4">
                <Select
                  label="Direction"
                  value={categoryDirection}
                  onChange={setCategoryDirection}
                  options={[
                    { value: 'import', label: 'Import' },
                    { value: 'export', label: 'Export' },
                  ]}
                  className="w-32"
                />
                <Select
                  label="Classification"
                  value={categoryClassification}
                  onChange={setCategoryClassification}
                  options={[
                    { value: 'BEA', label: 'BEA End Use' },
                    { value: 'NAICS', label: 'NAICS' },
                    { value: 'Harmonized', label: 'Harmonized System' },
                  ]}
                  className="w-40"
                />
                <Select
                  label="Time Range"
                  value={categoryTimeRange}
                  onChange={(v) => setCategoryTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
                <div className="ml-auto">
                  <ViewToggle value={categoryView} onChange={setCategoryView} />
                </div>
              </div>

              {/* Category Selection */}
              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-2">Select categories to compare (max 8, click row to toggle):</p>
              </div>

              {categoryView === 'chart' ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={categories.categories.slice(0, 15)} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" tick={{ fontSize: 10 }} />
                      <YAxis type="category" dataKey="series_name" tick={{ fontSize: 9 }} width={150} />
                      <Tooltip />
                      <Bar dataKey="current_value" name="Index Value" fill={categoryDirection === 'import' ? IMPORT_COLOR : EXPORT_COLOR} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium text-gray-600">Category</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">Index</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">MoM</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">YoY</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {categories.categories.map((cat) => (
                        <tr
                          key={cat.series_id}
                          className={`hover:bg-gray-50 cursor-pointer ${selectedCategories.includes(cat.series_id) ? 'bg-purple-50' : ''}`}
                          onClick={() => toggleCategorySelection(cat.series_id)}
                        >
                          <td className="px-4 py-2">{cat.series_name}</td>
                          <td className="px-4 py-2 text-right">{formatIndex(cat.current_value)}</td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={cat.mom_change} /></td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={cat.yoy_change} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </Card>

      {/* Section 5: Services Trade */}
      <Card>
        <SectionHeader title="Services Trade Indexes" color="teal" icon={Globe} />
        <div className="p-5">
          {loadingServices ? (
            <LoadingSpinner />
          ) : services ? (
            <>
              <div className="flex justify-end mb-4">
                <ViewToggle value={servicesView} onChange={setServicesView} />
              </div>

              {servicesView === 'chart' ? (
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Import Services</h3>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={services.import_services} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis type="number" tick={{ fontSize: 10 }} />
                          <YAxis type="category" dataKey="series_name" tick={{ fontSize: 9 }} width={120} />
                          <Tooltip />
                          <Bar dataKey="current_value" fill={IMPORT_COLOR} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Export Services</h3>
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={services.export_services} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis type="number" tick={{ fontSize: 10 }} />
                          <YAxis type="category" dataKey="series_name" tick={{ fontSize: 9 }} width={120} />
                          <Tooltip />
                          <Bar dataKey="current_value" fill={EXPORT_COLOR} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Import Services</h3>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="min-w-full text-sm">
                        <thead className="bg-red-50">
                          <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-600">Service</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">Index</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">YoY</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {services.import_services.map((item) => (
                            <tr key={item.series_id} className="hover:bg-gray-50">
                              <td className="px-3 py-2">{item.series_name}</td>
                              <td className="px-3 py-2 text-right">{formatIndex(item.current_value)}</td>
                              <td className="px-3 py-2 text-right"><ChangeIndicator value={item.yoy_change} /></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Export Services</h3>
                    <div className="overflow-x-auto border rounded-lg">
                      <table className="min-w-full text-sm">
                        <thead className="bg-green-50">
                          <tr>
                            <th className="px-3 py-2 text-left font-medium text-gray-600">Service</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">Index</th>
                            <th className="px-3 py-2 text-right font-medium text-gray-600">YoY</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {services.export_services.map((item) => (
                            <tr key={item.series_id} className="hover:bg-gray-50">
                              <td className="px-3 py-2">{item.series_name}</td>
                              <td className="px-3 py-2 text-right">{formatIndex(item.current_value)}</td>
                              <td className="px-3 py-2 text-right"><ChangeIndicator value={item.yoy_change} /></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </Card>

      {/* Section 6: Terms of Trade */}
      <Card>
        <SectionHeader title="Terms of Trade" color="indigo" />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">
            Terms of trade indexes measure the ratio of export prices to import prices. Values above 100 indicate favorable terms.
          </p>

          {loadingTerms ? (
            <LoadingSpinner />
          ) : termsOfTrade ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <Select
                  label="Time Range"
                  value={termsTimeRange}
                  onChange={(v) => setTermsTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
                <ViewToggle value={termsView} onChange={setTermsView} />
              </div>

              {termsView === 'chart' ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={termsOfTrade.terms} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
                      <YAxis type="category" dataKey="series_name" tick={{ fontSize: 9 }} width={150} />
                      <Tooltip />
                      <Bar dataKey="current_value" name="Index Value" fill="#6366f1" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left font-medium text-gray-600">Term</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">Index</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">MoM</th>
                        <th className="px-4 py-2 text-right font-medium text-gray-600">YoY</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {termsOfTrade.terms.map((term) => (
                        <tr key={term.series_id} className="hover:bg-gray-50">
                          <td className="px-4 py-2">{term.series_name}</td>
                          <td className="px-4 py-2 text-right">{formatIndex(term.current_value)}</td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={term.mom_change} /></td>
                          <td className="px-4 py-2 text-right"><ChangeIndicator value={term.yoy_change} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </Card>

      {/* Section 7: Top Movers */}
      <Card>
        <SectionHeader title="Top Movers" color="red" icon={ArrowUpCircle} />
        <div className="p-5">
          <div className="flex gap-4 mb-4">
            <Select
              label="Direction"
              value={moverDirection}
              onChange={setMoverDirection}
              options={[
                { value: 'all', label: 'All' },
                { value: 'import', label: 'Imports' },
                { value: 'export', label: 'Exports' },
              ]}
              className="w-32"
            />
            <Select
              label="Period"
              value={moverMetric}
              onChange={(v) => setMoverMetric(v as MoverPeriod)}
              options={[
                { value: 'mom_change', label: 'Month-over-Month' },
                { value: 'yoy_change', label: 'Year-over-Year' },
              ]}
              className="w-44"
            />
          </div>

          {loadingTopMovers ? (
            <LoadingSpinner />
          ) : topMovers ? (
            <div className="grid grid-cols-2 gap-6">
              {/* Gainers */}
              <div>
                <h3 className="text-sm font-semibold text-green-700 mb-2 flex items-center gap-2">
                  <ArrowUpCircle className="w-4 h-4" />
                  Top Gainers
                </h3>
                <div className="space-y-2">
                  {topMovers.top_gainers.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2 bg-green-50 rounded">
                      <span className="text-sm">{item.series_name}</span>
                      <span className="text-sm font-medium text-green-600">
                        {formatChange(item.pct_change, '%')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Losers */}
              <div>
                <h3 className="text-sm font-semibold text-red-700 mb-2 flex items-center gap-2">
                  <ArrowDownCircle className="w-4 h-4" />
                  Top Losers
                </h3>
                <div className="space-y-2">
                  {topMovers.top_losers.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2 bg-red-50 rounded">
                      <span className="text-sm">{item.series_name}</span>
                      <span className="text-sm font-medium text-red-600">
                        {formatChange(item.pct_change, '%')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </Card>

      {/* Section 8: Series Explorer */}
      <Card>
        <SectionHeader title="Series Explorer" color="cyan" icon={Search} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-6">
            Access all EI series through search, index code filter, or paginated browsing.
            Select series to compare in charts (max 5).
          </p>

          {/* Sub-section 8A: Search-based Access */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-cyan-50 to-blue-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-cyan-800">Search Series</h3>
              <p className="text-xs text-gray-600">Find series by keyword in title, name, or country</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleSearch()}
                    placeholder="Enter keyword (e.g., 'Canada', 'petroleum', 'machinery')..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || loadingSearch}
                  className="px-6 py-2 bg-cyan-600 text-white rounded-md hover:bg-cyan-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
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

              {/* Search Results */}
              {searchResults && (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      Found {searchResults.total} series matching "{searchQuery}"
                    </span>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left w-8"></th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Series ID</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Index</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Name</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {searchResults.series.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`hover:bg-gray-50 cursor-pointer ${selectedSeriesIds.includes(s.series_id) ? 'bg-cyan-50' : ''}`}
                            onClick={() => toggleSeriesSelection(s.series_id, s)}
                          >
                            <td className="px-3 py-2">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(s.series_id)}
                                onChange={() => {}}
                                className="rounded"
                              />
                            </td>
                            <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                            <td className="px-3 py-2">{s.index_name}</td>
                            <td className="px-3 py-2">{s.series_name || s.series_title}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sub-section 8B: Filter by Index Code */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-blue-800">Filter by Index Code</h3>
              <p className="text-xs text-gray-600">Browse series by classification type (IR, IQ, CO, CD, etc.)</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <Select
                  label="Index Code"
                  value={filterIndexCode}
                  onChange={setFilterIndexCode}
                  options={[
                    { value: '', label: 'Select Index Code...' },
                    ...(dimensions?.indexes.map(i => ({ value: i.index_code, label: `${i.index_code} - ${i.index_name}` })) || [])
                  ]}
                  className="w-80"
                />
                <button
                  onClick={handleFilter}
                  disabled={!filterIndexCode || loadingFilter}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 self-end"
                >
                  {loadingFilter && <Loader2 className="w-4 h-4 animate-spin" />}
                  Load Series
                </button>
              </div>

              {/* Filter Results */}
              {filterResults && (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      Showing {filterResults.series.length} of {filterResults.total} series
                    </span>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left w-8"></th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Series ID</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Name</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Base Period</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {filterResults.series.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`hover:bg-gray-50 cursor-pointer ${selectedSeriesIds.includes(s.series_id) ? 'bg-blue-50' : ''}`}
                            onClick={() => toggleSeriesSelection(s.series_id, s)}
                          >
                            <td className="px-3 py-2">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(s.series_id)}
                                onChange={() => {}}
                                className="rounded"
                              />
                            </td>
                            <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                            <td className="px-3 py-2">{s.series_name || s.series_title}</td>
                            <td className="px-3 py-2">{s.base_period}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {filterResults.series.length < filterResults.total && (
                    <div className="p-2 border-t border-gray-200">
                      <button
                        onClick={loadMoreFilterResults}
                        disabled={loadingFilter}
                        className="w-full py-2 text-sm text-blue-600 hover:bg-blue-50 rounded"
                      >
                        {loadingFilter ? 'Loading...' : 'Load More'}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Sub-section 8C: Paginated Browse */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-purple-800">Browse All Series</h3>
              <p className="text-xs text-gray-600">Paginated list of all EI series with optional country filter</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <div className="flex-1">
                  <label className="block text-xs font-medium text-gray-600 mb-1">Filter by Country</label>
                  <input
                    type="text"
                    value={browseCountry}
                    onChange={(e) => { setBrowseCountry(e.target.value); setBrowseOffset(0); }}
                    placeholder="Enter country name (optional)..."
                    className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
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

              {loadingBrowse ? (
                <LoadingSpinner />
              ) : browseResults ? (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      Showing {browseOffset + 1}-{Math.min(browseOffset + browseResults.series.length, browseResults.total)} of {browseResults.total}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setBrowseOffset(Math.max(0, browseOffset - browseLimit))}
                        disabled={browseOffset === 0}
                        className="px-3 py-1 text-sm border rounded disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setBrowseOffset(browseOffset + browseLimit)}
                        disabled={browseOffset + browseResults.series.length >= browseResults.total}
                        className="px-3 py-1 text-sm border rounded disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left w-8"></th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Series ID</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Index</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Name</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-600">Years</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {browseResults.series.map((s) => (
                          <tr
                            key={s.series_id}
                            className={`hover:bg-gray-50 cursor-pointer ${selectedSeriesIds.includes(s.series_id) ? 'bg-purple-50' : ''}`}
                            onClick={() => toggleSeriesSelection(s.series_id, s)}
                          >
                            <td className="px-3 py-2">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(s.series_id)}
                                onChange={() => {}}
                                className="rounded"
                              />
                            </td>
                            <td className="px-3 py-2 font-mono text-xs">{s.series_id}</td>
                            <td className="px-3 py-2">{s.index_code}</td>
                            <td className="px-3 py-2">{s.series_name || s.series_title}</td>
                            <td className="px-3 py-2 text-xs text-gray-500">
                              {s.begin_year}-{s.end_year || 'present'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : null}
            </div>
          </div>

          {/* Selected Series Chart */}
          {selectedSeriesIds.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-3 bg-gradient-to-r from-gray-50 to-slate-50 border-b border-gray-200 rounded-t-lg flex justify-between items-center">
                <div>
                  <h3 className="text-sm font-bold text-gray-800">Selected Series Comparison</h3>
                  <p className="text-xs text-gray-600">{selectedSeriesIds.length} series selected (max 5)</p>
                </div>
                <div className="flex items-center gap-4">
                  <Select
                    label="Time Range"
                    value={seriesTimeRange}
                    onChange={(v) => setSeriesTimeRange(parseInt(v))}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <ViewToggle value={seriesView} onChange={setSeriesView} />
                  <button
                    onClick={() => setSelectedSeriesIds([])}
                    className="px-3 py-1 text-sm text-red-600 border border-red-300 rounded hover:bg-red-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                {/* Selected series pills */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {selectedSeriesIds.map((id, idx) => (
                    <span
                      key={id}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium"
                      style={{ backgroundColor: `${CHART_COLORS[idx % CHART_COLORS.length]}20`, color: CHART_COLORS[idx % CHART_COLORS.length] }}
                    >
                      {allSeriesInfo[id]?.series_name || id}
                      <button
                        onClick={() => toggleSeriesSelection(id)}
                        className="ml-1 hover:bg-gray-200 rounded-full p-0.5"
                      >
                        &times;
                      </button>
                    </span>
                  ))}
                </div>

                {seriesView === 'chart' && combinedSeriesChartData.length > 0 ? (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedSeriesChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend />
                        {selectedSeriesIds.map((id, idx) => (
                          <Line
                            key={id}
                            type="monotone"
                            dataKey={id}
                            name={allSeriesInfo[id]?.series_name || id}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            strokeWidth={2}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left font-medium text-gray-600">Period</th>
                          {selectedSeriesIds.map((id) => (
                            <th key={id} className="px-4 py-2 text-right font-medium text-gray-600">
                              {allSeriesInfo[id]?.series_name || id}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {combinedSeriesChartData.slice(-24).reverse().map((point, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-4 py-2">{point.name as string}</td>
                            {selectedSeriesIds.map((id) => (
                              <td key={id} className="px-4 py-2 text-right">
                                {formatIndex(point[id] as number | null | undefined)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
