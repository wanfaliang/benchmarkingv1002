import { useState, useEffect, useMemo, ReactElement, KeyboardEvent } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, Clock, Users, Calendar, ArrowUpCircle, ArrowDownCircle, LucideIcon, ChevronRight, Search, List, GitBranch, X } from 'lucide-react';
import { tuResearchAPI } from '../../services/api';

/**
 * TU Explorer - American Time Use Survey Explorer
 *
 * ATUS provides time use data showing how people divide their time among activities:
 * - Average hours per day spent in various activities
 * - Participation rates (percent who engaged in activity)
 * - Number of persons
 *
 * Sections:
 * 1. Overview - Summary of major activities with hours per day
 * 2. Activity Analysis - Detailed activity breakdown with sub-activities
 * 3. Sex Comparison - Compare time use between males and females
 * 4. Age Comparison - Compare time use across age groups
 * 5. Labor Force Analysis - Time use by employment status
 * 6. Education Comparison - Compare time use by education level
 * 7. Race Comparison - Compare time use by race
 * 8. Day Type Comparison - Compare weekday vs weekend time use
 * 9. Top Activities - Ranked activities by time spent
 * 10. Year-over-Year Changes - Biggest changes in time use
 * 11. Series Explorer - Search, drill-down, browse
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

interface ActivitySummary {
  actcode_code: string;
  actcode_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
  yoy_change?: number | null;
  latest_year?: number | null;
}

interface OverviewData {
  activities: ActivitySummary[];
  total_persons?: number | null;
  latest_year?: number | null;
}

interface TimelinePoint {
  year: number;
  period: string;
  period_name: string;
  activities?: Record<string, number | null>;
  male?: number | null;
  female?: number | null;
  ages?: Record<string, number | null>;
  regions?: Record<string, number | null>;
  statuses?: Record<string, number | null>;  // labor force statuses
  educations?: Record<string, number | null>;
  races?: Record<string, number | null>;
  day_types?: Record<string, number | null>;
}

interface OverviewTimelineData {
  stattype: string;
  timeline: TimelinePoint[];
  activity_names: Record<string, string>;
}

interface ActivityMetric {
  actcode_code: string;
  actcode_text: string;
  display_level?: number | null;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
  yoy_change_hours?: number | null;
  yoy_change_participation?: number | null;
  latest_year?: number | null;
}

interface ActivityAnalysisData {
  parent_activity_code?: string;
  parent_activity_name?: string;
  demographic_filter?: string;
  activities: ActivityMetric[];
  total_count: number;
  latest_year?: number | null;
}

interface ActivityTimelineData {
  stattype: string;
  timeline: TimelinePoint[];
  activity_names: Record<string, string>;
}

interface SexComparison {
  sex_code: string;
  sex_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
}

interface SexComparisonData {
  actcode_code?: string;
  actcode_text?: string;
  comparisons: SexComparison[];
  latest_year?: number | null;
}

interface SexTimelineData {
  actcode_code?: string;
  actcode_text?: string;
  stattype: string;
  timeline: TimelinePoint[];
}

interface AgeComparison {
  age_code: string;
  age_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
}

interface AgeComparisonData {
  actcode_code?: string;
  actcode_text?: string;
  comparisons: AgeComparison[];
  latest_year?: number | null;
}

interface AgeTimelineData {
  actcode_code?: string;
  actcode_text?: string;
  stattype: string;
  timeline: TimelinePoint[];
  age_names: Record<string, string>;
}

interface LaborForceComparison {
  lfstat_code: string;
  lfstat_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
}

interface LaborForceComparisonData {
  actcode_code?: string;
  actcode_text?: string;
  comparisons: LaborForceComparison[];
  latest_year?: number | null;
}

interface LaborForceTimelineData {
  actcode_code?: string;
  actcode_text?: string;
  stattype: string;
  timeline: TimelinePoint[];
  status_names: Record<string, string>;
}

interface EducationComparison {
  educ_code: string;
  educ_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
}

interface EducationComparisonData {
  actcode_code?: string;
  actcode_text?: string;
  comparisons: EducationComparison[];
  latest_year?: number | null;
}

interface EducationTimelineData {
  actcode_code?: string;
  actcode_text?: string;
  stattype: string;
  timeline: TimelinePoint[];
  educ_names: Record<string, string>;
}

interface RaceComparison {
  race_code: string;
  race_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
}

interface RaceComparisonData {
  actcode_code?: string;
  actcode_text?: string;
  comparisons: RaceComparison[];
  latest_year?: number | null;
}

interface DayTypeComparison {
  pertype_code: string;
  pertype_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  avg_hours_participants?: number | null;
}

interface DayTypeComparisonData {
  actcode_code?: string;
  actcode_text?: string;
  comparisons: DayTypeComparison[];
  latest_year?: number | null;
}

interface RaceTimelineData {
  actcode_code?: string;
  actcode_text?: string;
  stattype: string;
  timeline: TimelinePoint[];
  race_names: Record<string, string>;
}

interface DayTypeTimelineData {
  actcode_code?: string;
  actcode_text?: string;
  stattype: string;
  timeline: TimelinePoint[];
  day_type_names: Record<string, string>;
}

interface TopActivity {
  actcode_code: string;
  actcode_text: string;
  avg_hours_per_day?: number | null;
  participation_rate?: number | null;
  rank: number;
}

interface TopActivitiesData {
  ranking_type: string;
  activities: TopActivity[];
  latest_year?: number | null;
}

interface ActivityChange {
  actcode_code: string;
  actcode_text: string;
  current_value?: number | null;
  prev_value?: number | null;
  change?: number | null;
  change_pct?: number | null;
}

interface YoYChangesData {
  stattype: string;
  latest_year: number;
  prev_year: number;
  gainers: ActivityChange[];
  losers: ActivityChange[];
}

interface DrilldownLevel {
  dimension: string;
  code: string;
  name: string;
  has_children: boolean;
  child_count: number;
}

interface DrilldownData {
  current_path: DrilldownLevel[];
  children: DrilldownLevel[];
  available_dimensions: string[];
  series_count: number;
}

interface SeriesInfo {
  series_id: string;
  seasonal?: string;
  stattype_code?: string;
  stattype_text?: string;
  actcode_code?: string;
  actcode_text?: string;
  sex_code?: string;
  sex_text?: string;
  age_code?: string;
  age_text?: string;
  series_title?: string;
  begin_year?: number;
  end_year?: number;
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
  value?: number | null;
}

interface SeriesDataItem {
  series_id: string;
  activity_name?: string;
  stattype_name?: string;
  demographic_group?: string;
  data_points: DataPoint[];
}

interface SeriesDataResponse {
  series: SeriesDataItem[];
}

// Map of series ID to its data response (for multi-series chart)
interface SeriesChartDataMap {
  [seriesId: string]: SeriesDataResponse;
}

// Chart data point for combined multi-series chart
interface CombinedChartDataPoint {
  period_name: string;
  sortKey: number;
  [seriesId: string]: string | number; // Dynamic keys for each series
}

interface DimensionsData {
  stat_types: Array<{ stattype_code: string; stattype_text: string }>;
  activities: Array<{ actcode_code: string; actcode_text: string; display_level?: number }>;
  sexes: Array<{ sex_code: string; sex_text: string }>;
  ages: Array<{ age_code: string; age_text: string }>;
  races: Array<{ race_code: string; race_text: string }>;
  educations: Array<{ educ_code: string; educ_text: string }>;
  marital_statuses: Array<{ maritlstat_code: string; maritlstat_text: string }>;
  labor_force_statuses: Array<{ lfstat_code: string; lfstat_text: string }>;
  origins: Array<{ orig_code: string; orig_text: string }>;
  regions: Array<{ region_code: string; region_text: string }>;
  wheres: Array<{ where_code: string; where_text: string }>;
  whos: Array<{ who_code: string; who_text: string }>;
  times_of_day: Array<{ timeday_code: string; timeday_text: string }>;
}

type ViewType = 'table' | 'chart';
type SectionColor = 'blue' | 'green' | 'orange' | 'purple' | 'cyan' | 'red';
type SeriesExplorerMethod = 'search' | 'browse' | 'drilldown';

// ============================================================================
// CONSTANTS
// ============================================================================

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'];

const timeRangeOptions: TimeRangeOption[] = [
  { value: 5, label: 'Last 5 years' },
  { value: 10, label: 'Last 10 years' },
  { value: 15, label: 'Last 15 years' },
  { value: 20, label: 'Last 20 years' },
  { value: 0, label: 'All Time' },
];

// Major activity codes - 010100 (Sleeping) added as most important to users
// The 600xxx codes are summary categories from bls_tu_actcodes with display_level=1
const MAJOR_ACTIVITY_CODES = [
  '010100',  // Sleeping
  '600013',  // Working and work-related activities
  '600023',  // Leisure and sports (includes travel)
  '600022',  // Eating and drinking (includes travel)
  '600003',  // Household activities (includes travel)
  '600018',  // Purchasing goods and services (includes travel)
  '600007',  // Caring for and helping household members
  '600010',  // Caring for and helping nonhousehold members
  '600016',  // Educational activities
  '600030',  // Organizational, civic, and religious activities
  '600033',  // Telephone calls, mail, and e-mail
  '600034',  // Other activities
];

// Static activity names for display (avoids needing to fetch before display)
const ACTIVITY_NAMES: { [code: string]: string } = {
  '010100': 'Sleeping',
  '000000': 'Total, all activities',
  '050100': 'Working',
  '120301': 'Relaxing and thinking',
  '120307': 'Playing games',
  '120308': 'Computer use for leisure',
  '120312': 'Reading for personal interest',
  '600001': 'Personal care activities',
  '600013': 'Working and work-related',
  '600023': 'Leisure and sports',
  '600022': 'Eating and drinking',
  '600003': 'Household activities',
  '600018': 'Purchasing goods/services',
  '600007': 'Caring for household members',
  '600010': 'Caring for nonhousehold members',
  '600016': 'Educational activities',
  '600024': 'Socializing and communicating',
  '600025': 'Watching TV',
  '600027': 'Sports, exercise, recreation',
  '600030': 'Civic and religious activities',
  '600033': 'Phone, mail, and e-mail',
  '600034': 'Other activities',
  '600058': 'Games and computer leisure',
  '600059': 'Other leisure and sports',
  '600085': 'Awake time',
};

// Activities that have education breakdown data available in BLS ATUS
// These activities have avg hours per day (stat=10101) broken down by specific education levels
// Note: 000000 (Total) and 050100 (Working) don't have this breakdown - they only have aggregate data
const EDUCATION_BREAKDOWN_ACTIVITIES = [
  '600001',  // Personal care activities
  '600003',  // Household activities
  '600007',  // Caring for household members
  '600010',  // Caring for nonhousehold members
  '600013',  // Working and work-related activities
  '600016',  // Educational activities
  '600018',  // Purchasing goods/services
  '600022',  // Eating and drinking
  '600023',  // Leisure and sports
  '600024',  // Socializing and communicating
  '600025',  // Watching TV
  '600027',  // Sports, exercise, recreation
  '600030',  // Civic and religious activities
  '600033',  // Phone, mail, and e-mail
  '600034',  // Other activities
  '120301',  // Relaxing and thinking
  '120307',  // Playing games
  '120308',  // Computer use for leisure
  '120312',  // Reading for personal interest
];

// Activities that have race breakdown data (same set for ATUS)
const RACE_BREAKDOWN_ACTIVITIES = [
  '600001',  // Personal care activities
  '600003',  // Household activities
  '600007',  // Caring for household members
  '600010',  // Caring for nonhousehold members
  '600013',  // Working and work-related activities
  '600016',  // Educational activities
  '600018',  // Purchasing goods/services
  '600022',  // Eating and drinking
  '600023',  // Leisure and sports
  '600024',  // Socializing and communicating
  '600025',  // Watching TV
  '600027',  // Sports, exercise, recreation
  '600030',  // Civic and religious activities
  '600033',  // Phone, mail, and e-mail
  '600034',  // Other activities
  '120301',  // Relaxing and thinking
  '120307',  // Playing games
  '120308',  // Computer use for leisure
  '120312',  // Reading for personal interest
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatHours = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return value.toFixed(2);
};

const formatPercent = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  return `${value.toFixed(1)}%`;
};

const formatChange = (value: number | undefined | null, suffix: string = ''): string => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}${suffix}`;
};

// COVID-19 data note component
const Covid2020Note = (): ReactElement => (
  <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
    <strong>Note:</strong> 2020 data is largely unavailable due to COVID-19 pandemic impact on ATUS data collection.
    The BLS suspended in-person interviews from mid-March through the end of 2020.
  </div>
);

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
  view: ViewType;
  onViewChange: (view: ViewType) => void;
}

const ViewToggle = ({ view, onViewChange }: ViewToggleProps): ReactElement => (
  <div className="flex border border-gray-300 rounded-md overflow-hidden">
    <button
      onClick={() => onViewChange('chart')}
      className={`px-3 py-1.5 text-xs font-medium ${view === 'chart' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
    >
      Chart
    </button>
    <button
      onClick={() => onViewChange('table')}
      className={`px-3 py-1.5 text-xs font-medium ${view === 'table' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
    >
      Table
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

  // Show every Nth point to avoid overcrowding (max ~15 points)
  const step = Math.max(1, Math.ceil(timeline.length / 15));
  const visibleIndices: number[] = [];
  for (let i = 0; i < timeline.length; i += step) {
    visibleIndices.push(i);
  }
  if (visibleIndices[visibleIndices.length - 1] !== timeline.length - 1) {
    visibleIndices.push(timeline.length - 1);
  }

  return (
    <div className="mt-4 mb-2 px-2">
      <p className="text-xs text-gray-500 mb-2">Select period (click any point):</p>
      <div className="relative h-14">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-300" />
        <div className="relative flex justify-between">
          {visibleIndices.map((index) => {
            const point = timeline[index];
            const isSelected = selectedIndex === index;
            return (
              <div
                key={index}
                className="flex flex-col items-center cursor-pointer group"
                onClick={() => onSelectIndex(index)}
              >
                <div
                  className={`w-3 h-3 rounded-full border-2 transition-all z-10 ${
                    isSelected
                      ? 'bg-blue-600 border-blue-600 scale-125'
                      : 'bg-white border-gray-400 group-hover:border-blue-500 group-hover:bg-blue-100'
                  }`}
                />
                <span className={`text-[10px] mt-1 whitespace-nowrap ${isSelected ? 'text-blue-600 font-semibold' : 'text-gray-500'}`}>
                  {point.period_name}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  change?: number | null;
  subtitle?: string;
}

const MetricCard = ({ title, value, change, subtitle }: MetricCardProps): ReactElement => (
  <div className="bg-gray-50 rounded-lg p-4">
    <div className="text-sm text-gray-600 mb-1">{title}</div>
    <div className="text-2xl font-bold text-gray-900">{value}</div>
    {change !== undefined && change !== null && (
      <div className={`text-sm flex items-center gap-1 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
        {change >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        {formatChange(change, ' hrs')}
      </div>
    )}
    {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
  </div>
);

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function TUExplorer(): ReactElement {
  // Section 1: Overview state
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [overviewTimeline, setOverviewTimeline] = useState<OverviewTimelineData | null>(null);
  const [overviewTimeRange, setOverviewTimeRange] = useState<number>(10);
  const [overviewView, setOverviewView] = useState<ViewType>('chart');
  const [overviewLoading, setOverviewLoading] = useState(true);
  const [overviewSelectedIndex, setOverviewSelectedIndex] = useState<number | null>(null);

  // Section 2: Activity Analysis state
  const [selectedActivity, setSelectedActivity] = useState<string>('600013');
  const [activityData, setActivityData] = useState<ActivityAnalysisData | null>(null);
  const [activityTimeline, setActivityTimeline] = useState<ActivityTimelineData | null>(null);
  const [activityTimeRange, setActivityTimeRange] = useState<number>(10);
  const [activityView, setActivityView] = useState<ViewType>('chart');
  const [activityLoading, setActivityLoading] = useState(false);
  const [activitySelectedIndex, setActivitySelectedIndex] = useState<number | null>(null);

  // Section 3: Sex Comparison state - data loaded on click
  const [sexActivities, setSexActivities] = useState<string[]>([]);  // Selected activities for comparison
  const [sexActivityData, setSexActivityData] = useState<{ [actCode: string]: SexComparisonData }>({});
  const [sexTimelineData, setSexTimelineData] = useState<{ [actCode: string]: SexTimelineData }>({});
  const [sexTimeRange, setSexTimeRange] = useState<number>(10);
  const [sexView, setSexView] = useState<ViewType>('chart');
  const [sexLoading, setSexLoading] = useState(false);

  // Section 4: Age Comparison state - data loaded on click
  const [ageActivities, setAgeActivities] = useState<string[]>([]);  // Selected activities for comparison
  const [ageActivityData, setAgeActivityData] = useState<{ [actCode: string]: AgeComparisonData }>({});
  const [ageTimelineData, setAgeTimelineData] = useState<{ [actCode: string]: AgeTimelineData }>({});
  const [ageTimeRange, setAgeTimeRange] = useState<number>(10);
  const [ageView, setAgeView] = useState<ViewType>('chart');
  const [ageLoading, setAgeLoading] = useState(false);
  const [selectedAges] = useState<string[]>(['015', '025', '035', '055']);

  // Section 5: Labor Force state - data loaded on click
  const [lfActivities, setLfActivities] = useState<string[]>([]);  // Selected activities for comparison
  const [lfActivityData, setLfActivityData] = useState<{ [actCode: string]: LaborForceComparisonData }>({});
  const [lfTimelineData, setLfTimelineData] = useState<{ [actCode: string]: LaborForceTimelineData }>({});
  const [lfTimeRange, setLfTimeRange] = useState<number>(10);
  const [lfView, setLfView] = useState<ViewType>('chart');
  const [lfLoading, setLfLoading] = useState(false);
  const [selectedLfStatuses] = useState<string[]>(['01', '20']);  // Employed, Not Employed (actual BLS codes)

  // Section 6: Education state - data loaded on click
  const [educActivities, setEducActivities] = useState<string[]>([]);  // Selected activities for comparison
  const [educActivityData, setEducActivityData] = useState<{ [actCode: string]: EducationComparisonData }>({});
  const [educTimelineData, setEducTimelineData] = useState<{ [actCode: string]: EducationTimelineData }>({});
  const [educTimeRange, setEducTimeRange] = useState<number>(10);
  const [educView, setEducView] = useState<ViewType>('chart');
  const [educLoading, setEducLoading] = useState(false);

  // Section 7: Race state - data loaded on click
  const [raceActivities, setRaceActivities] = useState<string[]>([]);  // Selected activities for comparison
  const [raceActivityData, setRaceActivityData] = useState<{ [actCode: string]: RaceComparisonData }>({});
  const [raceTimelineData, setRaceTimelineData] = useState<{ [actCode: string]: RaceTimelineData }>({});
  const [raceTimeRange, setRaceTimeRange] = useState<number>(10);
  const [raceView, setRaceView] = useState<ViewType>('chart');
  const [raceLoading, setRaceLoading] = useState(false);

  // Section 8: Day Type state - data loaded on click
  const [dayTypeActivities, setDayTypeActivities] = useState<string[]>([]);  // Selected activities for comparison
  const [dayTypeActivityData, setDayTypeActivityData] = useState<{ [actCode: string]: DayTypeComparisonData }>({});
  const [dayTypeTimelineData, setDayTypeTimelineData] = useState<{ [actCode: string]: DayTypeTimelineData }>({});
  const [dayTypeTimeRange, setDayTypeTimeRange] = useState<number>(10);
  const [dayTypeView, setDayTypeView] = useState<ViewType>('chart');
  const [dayTypeLoading, setDayTypeLoading] = useState(false);

  // Section 9: Top Activities state
  const [topActivitiesData, setTopActivitiesData] = useState<TopActivitiesData | null>(null);
  const [topRankingType, setTopRankingType] = useState<string>('most_time');
  const [topLoading, setTopLoading] = useState(false);

  // Section 10: YoY Changes state
  const [yoyData, setYoyData] = useState<YoYChangesData | null>(null);
  const [yoyLoading, setYoyLoading] = useState(false);

  // Section 11: Series Explorer state
  const [explorerMethod, setExplorerMethod] = useState<SeriesExplorerMethod>('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SeriesListData | null>(null);
  const [drilldownData, setDrilldownData] = useState<DrilldownData | null>(null);
  const [drilldownPath, setDrilldownPath] = useState<{ dimension: string; code: string }[]>([]);
  const [browseFilters, setBrowseFilters] = useState<Record<string, string>>({});
  const [browseResults, setBrowseResults] = useState<SeriesListData | null>(null);
  const [explorerLoading, setExplorerLoading] = useState(false);
  // Multi-series selection (max 5 series)
  const [selectedSeries, setSelectedSeries] = useState<string[]>([]);
  const [seriesChartData, setSeriesChartData] = useState<SeriesChartDataMap>({});
  const [seriesTimeRange, setSeriesTimeRange] = useState<number>(10);
  const [seriesView, setSeriesView] = useState<ViewType>('chart');

  // Dimensions
  const [dimensions, setDimensions] = useState<DimensionsData | null>(null);

  // Activity options for selects
  const activityOptions: SelectOption[] = dimensions?.activities
    ? dimensions.activities.filter(a => (a.display_level ?? 0) <= 1).map(a => ({
        value: a.actcode_code,
        label: a.actcode_text.substring(0, 50) + (a.actcode_text.length > 50 ? '...' : '')
      }))
    : MAJOR_ACTIVITY_CODES.map(code => ({ value: code, label: code }));

  // ============================================================================
  // DATA FETCHING
  // ============================================================================

  // Load dimensions
  useEffect(() => {
    const loadDimensions = async () => {
      try {
        const response = await tuResearchAPI.getDimensions<DimensionsData>();
        setDimensions(response.data);
      } catch (error) {
        console.error('Error loading TU dimensions:', error);
      }
    };
    loadDimensions();
  }, []);

  // Section 1: Load Overview
  useEffect(() => {
    const loadOverview = async () => {
      setOverviewLoading(true);
      try {
        const [overviewRes, timelineRes] = await Promise.all([
          tuResearchAPI.getOverview<OverviewData>(),
          tuResearchAPI.getOverviewTimeline<OverviewTimelineData>(
            overviewTimeRange === 0 ? undefined : new Date().getFullYear() - overviewTimeRange,
            undefined,
            MAJOR_ACTIVITY_CODES.slice(0, 6).join(',')
          )
        ]);
        setOverviewData(overviewRes.data);
        setOverviewTimeline(timelineRes.data);
      } catch (error) {
        console.error('Error loading TU overview:', error);
      } finally {
        setOverviewLoading(false);
      }
    };
    loadOverview();
  }, [overviewTimeRange]);

  // Section 2: Load Activity Analysis
  useEffect(() => {
    if (!selectedActivity) return;
    const loadActivityAnalysis = async () => {
      setActivityLoading(true);
      try {
        const [analysisRes, timelineRes] = await Promise.all([
          tuResearchAPI.getActivityAnalysis<ActivityAnalysisData>(selectedActivity),
          tuResearchAPI.getActivityTimeline<ActivityTimelineData>(
            selectedActivity,
            'avg_hours',
            activityTimeRange === 0 ? undefined : new Date().getFullYear() - activityTimeRange
          )
        ]);
        setActivityData(analysisRes.data);
        setActivityTimeline(timelineRes.data);
      } catch (error) {
        console.error('Error loading activity analysis:', error);
      } finally {
        setActivityLoading(false);
      }
    };
    loadActivityAnalysis();
  }, [selectedActivity, activityTimeRange]);

  // Section 3: Auto-load first activity on mount for immediate visibility
  useEffect(() => {
    const loadInitialSexData = async () => {
      const firstActivity = MAJOR_ACTIVITY_CODES[0]; // Sleeping
      setSexActivities([firstActivity]);
      setSexLoading(true);
      try {
        const startYear = sexTimeRange === 0 ? undefined : new Date().getFullYear() - sexTimeRange;
        const [compRes, timelineRes] = await Promise.all([
          tuResearchAPI.getSexComparison<SexComparisonData>(firstActivity),
          tuResearchAPI.getSexTimeline<SexTimelineData>(firstActivity, 'avg_hours', startYear)
        ]);
        setSexActivityData({ [firstActivity]: compRes.data });
        setSexTimelineData({ [firstActivity]: timelineRes.data });
      } catch (error) {
        console.error('Error loading initial sex data:', error);
      } finally {
        setSexLoading(false);
      }
    };
    loadInitialSexData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Section 4: Auto-load first activity on mount for immediate visibility
  useEffect(() => {
    const loadInitialAgeData = async () => {
      const firstActivity = MAJOR_ACTIVITY_CODES[0]; // Sleeping
      setAgeActivities([firstActivity]);
      setAgeLoading(true);
      try {
        const startYear = ageTimeRange === 0 ? undefined : new Date().getFullYear() - ageTimeRange;
        const [compRes, timelineRes] = await Promise.all([
          tuResearchAPI.getAgeComparison<AgeComparisonData>(firstActivity),
          tuResearchAPI.getAgeTimeline<AgeTimelineData>(firstActivity, selectedAges.join(','), 'avg_hours', startYear)
        ]);
        setAgeActivityData({ [firstActivity]: compRes.data });
        setAgeTimelineData({ [firstActivity]: timelineRes.data });
      } catch (error) {
        console.error('Error loading initial age data:', error);
      } finally {
        setAgeLoading(false);
      }
    };
    loadInitialAgeData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Section 5: Auto-load first activity on mount for immediate visibility
  useEffect(() => {
    const loadInitialLfData = async () => {
      const firstActivity = MAJOR_ACTIVITY_CODES[0]; // Sleeping
      setLfActivities([firstActivity]);
      setLfLoading(true);
      try {
        const startYear = lfTimeRange === 0 ? undefined : new Date().getFullYear() - lfTimeRange;
        const [compRes, timelineRes] = await Promise.all([
          tuResearchAPI.getLaborForceComparison<LaborForceComparisonData>(firstActivity),
          tuResearchAPI.getLaborForceTimeline<LaborForceTimelineData>(firstActivity, selectedLfStatuses.join(','), 'avg_hours', startYear)
        ]);
        setLfActivityData({ [firstActivity]: compRes.data });
        setLfTimelineData({ [firstActivity]: timelineRes.data });
      } catch (error) {
        console.error('Error loading initial labor force data:', error);
      } finally {
        setLfLoading(false);
      }
    };
    loadInitialLfData();
  }, [lfTimeRange]); // eslint-disable-line react-hooks/exhaustive-deps

  // Section 6: Auto-load first activity for Education
  useEffect(() => {
    const loadInitialEducData = async () => {
      const firstActivity = EDUCATION_BREAKDOWN_ACTIVITIES[0]; // Total, all activities
      setEducActivities([firstActivity]);
      setEducLoading(true);
      try {
        const startYear = educTimeRange === 0 ? undefined : new Date().getFullYear() - educTimeRange;
        const compRes = await tuResearchAPI.getEducationComparison<EducationComparisonData>(firstActivity);
        setEducActivityData({ [firstActivity]: compRes.data });
        // Also load timeline data
        const educCodes = compRes.data.comparisons?.map(c => c.educ_code).join(',') || '';
        if (educCodes) {
          const timelineRes = await tuResearchAPI.getEducationTimeline<EducationTimelineData>(firstActivity, educCodes, 'avg_hours', startYear);
          setEducTimelineData({ [firstActivity]: timelineRes.data });
        }
      } catch (error) {
        console.error('Error loading initial education data:', error);
      } finally {
        setEducLoading(false);
      }
    };
    loadInitialEducData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Section 7: Auto-load first activity for Race
  useEffect(() => {
    const loadInitialRaceData = async () => {
      const firstActivity = RACE_BREAKDOWN_ACTIVITIES[0]; // Personal care activities
      setRaceActivities([firstActivity]);
      setRaceLoading(true);
      try {
        const startYear = raceTimeRange === 0 ? undefined : new Date().getFullYear() - raceTimeRange;
        const compRes = await tuResearchAPI.getRaceComparison<RaceComparisonData>(firstActivity);
        setRaceActivityData({ [firstActivity]: compRes.data });
        // Also load timeline data
        const raceCodes = compRes.data.comparisons?.map(c => c.race_code).join(',') || '';
        if (raceCodes) {
          const timelineRes = await tuResearchAPI.getRaceTimeline<RaceTimelineData>(firstActivity, raceCodes, 'avg_hours', startYear);
          setRaceTimelineData({ [firstActivity]: timelineRes.data });
        }
      } catch (error) {
        console.error('Error loading initial race data:', error);
      } finally {
        setRaceLoading(false);
      }
    };
    loadInitialRaceData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Section 8: Auto-load first activity for Day Type
  useEffect(() => {
    const loadInitialDayTypeData = async () => {
      const firstActivity = MAJOR_ACTIVITY_CODES[0]; // Sleeping
      setDayTypeActivities([firstActivity]);
      setDayTypeLoading(true);
      try {
        const startYear = dayTypeTimeRange === 0 ? undefined : new Date().getFullYear() - dayTypeTimeRange;
        const compRes = await tuResearchAPI.getDayTypeComparison<DayTypeComparisonData>(firstActivity);
        setDayTypeActivityData({ [firstActivity]: compRes.data });
        // Also load timeline data
        const daytypeCodes = compRes.data.comparisons?.map(c => c.pertype_code).join(',') || '';
        if (daytypeCodes) {
          const timelineRes = await tuResearchAPI.getDayTypeTimeline<DayTypeTimelineData>(firstActivity, daytypeCodes, 'avg_hours', startYear);
          setDayTypeTimelineData({ [firstActivity]: timelineRes.data });
        }
      } catch (error) {
        console.error('Error loading initial day type data:', error);
      } finally {
        setDayTypeLoading(false);
      }
    };
    loadInitialDayTypeData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Section 9: Load Top Activities
  useEffect(() => {
    const loadTopActivities = async () => {
      setTopLoading(true);
      try {
        const response = await tuResearchAPI.getTopActivities<TopActivitiesData>(topRankingType);
        setTopActivitiesData(response.data);
      } catch (error) {
        console.error('Error loading top activities:', error);
      } finally {
        setTopLoading(false);
      }
    };
    loadTopActivities();
  }, [topRankingType]);

  // Section 10: Load YoY Changes
  useEffect(() => {
    const loadYoYChanges = async () => {
      setYoyLoading(true);
      try {
        const response = await tuResearchAPI.getYoYChanges<YoYChangesData>();
        setYoyData(response.data);
      } catch (error) {
        console.error('Error loading YoY changes:', error);
      } finally {
        setYoyLoading(false);
      }
    };
    loadYoYChanges();
  }, []);

  // Series Explorer: Search
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setExplorerLoading(true);
    try {
      const response = await tuResearchAPI.searchSeries<SeriesListData>(searchQuery);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error searching series:', error);
    } finally {
      setExplorerLoading(false);
    }
  };

  // Series Explorer: Drilldown
  const loadDrilldown = async (path: { dimension: string; code: string }[]) => {
    setExplorerLoading(true);
    try {
      const params: Record<string, string> = {};
      path.forEach(p => {
        if (p.dimension === 'activity') params.actcode_code = p.code;
        if (p.dimension === 'stattype') params.stattype_code = p.code;
        if (p.dimension === 'sex') params.sex_code = p.code;
        if (p.dimension === 'age') params.age_code = p.code;
      });
      const response = await tuResearchAPI.drilldownSeries<DrilldownData>(params);
      setDrilldownData(response.data);
    } catch (error) {
      console.error('Error loading drilldown:', error);
    } finally {
      setExplorerLoading(false);
    }
  };

  useEffect(() => {
    if (explorerMethod === 'drilldown') {
      loadDrilldown(drilldownPath);
    }
  }, [explorerMethod, drilldownPath]);

  // Series Explorer: Browse
  const handleBrowse = async () => {
    setExplorerLoading(true);
    try {
      const response = await tuResearchAPI.browseSeries<SeriesListData>(browseFilters);
      setBrowseResults(response.data);
    } catch (error) {
      console.error('Error browsing series:', error);
    } finally {
      setExplorerLoading(false);
    }
  };

  // Toggle series selection (max 5)
  const toggleSeriesSelection = (seriesId: string): void => {
    if (selectedSeries.includes(seriesId)) {
      setSelectedSeries(selectedSeries.filter(id => id !== seriesId));
    } else if (selectedSeries.length < 5) {
      setSelectedSeries([...selectedSeries, seriesId]);
    }
  };

  // Toggle sex activity selection (max 5) - fetch data on add
  const toggleSexActivity = async (actCode: string): Promise<void> => {
    if (sexActivities.includes(actCode)) {
      // Remove
      setSexActivities(sexActivities.filter(id => id !== actCode));
    } else if (sexActivities.length < 5) {
      // Add and fetch data if not cached
      setSexActivities([...sexActivities, actCode]);
      if (!sexActivityData[actCode]) {
        setSexLoading(true);
        try {
          const startYear = sexTimeRange === 0 ? undefined : new Date().getFullYear() - sexTimeRange;
          const [compRes, timelineRes] = await Promise.all([
            tuResearchAPI.getSexComparison<SexComparisonData>(actCode),
            tuResearchAPI.getSexTimeline<SexTimelineData>(actCode, 'avg_hours', startYear)
          ]);
          setSexActivityData(prev => ({ ...prev, [actCode]: compRes.data }));
          setSexTimelineData(prev => ({ ...prev, [actCode]: timelineRes.data }));
        } catch (error) {
          console.error(`Error loading sex data for ${actCode}:`, error);
        } finally {
          setSexLoading(false);
        }
      }
    }
  };

  // Toggle age activity selection (max 5) - fetch data on add
  const toggleAgeActivity = async (actCode: string): Promise<void> => {
    if (ageActivities.includes(actCode)) {
      // Remove
      setAgeActivities(ageActivities.filter(id => id !== actCode));
    } else if (ageActivities.length < 5) {
      // Add and fetch data if not cached
      setAgeActivities([...ageActivities, actCode]);
      if (!ageActivityData[actCode]) {
        setAgeLoading(true);
        try {
          const startYear = ageTimeRange === 0 ? undefined : new Date().getFullYear() - ageTimeRange;
          const [compRes, timelineRes] = await Promise.all([
            tuResearchAPI.getAgeComparison<AgeComparisonData>(actCode),
            tuResearchAPI.getAgeTimeline<AgeTimelineData>(actCode, selectedAges.join(','), 'avg_hours', startYear)
          ]);
          setAgeActivityData(prev => ({ ...prev, [actCode]: compRes.data }));
          setAgeTimelineData(prev => ({ ...prev, [actCode]: timelineRes.data }));
        } catch (error) {
          console.error(`Error loading age data for ${actCode}:`, error);
        } finally {
          setAgeLoading(false);
        }
      }
    }
  };

  // Toggle labor force activity selection (max 5) - fetch data on add
  const toggleLfActivity = async (actCode: string): Promise<void> => {
    if (lfActivities.includes(actCode)) {
      // Remove
      setLfActivities(lfActivities.filter(id => id !== actCode));
    } else if (lfActivities.length < 5) {
      // Add and fetch data if not cached
      setLfActivities([...lfActivities, actCode]);
      if (!lfActivityData[actCode]) {
        setLfLoading(true);
        try {
          const startYear = lfTimeRange === 0 ? undefined : new Date().getFullYear() - lfTimeRange;
          const [compRes, timelineRes] = await Promise.all([
            tuResearchAPI.getLaborForceComparison<LaborForceComparisonData>(actCode),
            tuResearchAPI.getLaborForceTimeline<LaborForceTimelineData>(actCode, selectedLfStatuses.join(','), 'avg_hours', startYear)
          ]);
          setLfActivityData(prev => ({ ...prev, [actCode]: compRes.data }));
          setLfTimelineData(prev => ({ ...prev, [actCode]: timelineRes.data }));
        } catch (error) {
          console.error(`Error loading labor force data for ${actCode}:`, error);
        } finally {
          setLfLoading(false);
        }
      }
    }
  };

  // Section 6: Education toggle
  const toggleEducActivity = async (actCode: string): Promise<void> => {
    if (educActivities.includes(actCode)) {
      setEducActivities(educActivities.filter(id => id !== actCode));
    } else if (educActivities.length < 5) {
      setEducActivities([...educActivities, actCode]);
      // Load data if not already loaded
      if (!educActivityData[actCode] || !educTimelineData[actCode]) {
        setEducLoading(true);
        try {
          const startYear = educTimeRange === 0 ? undefined : new Date().getFullYear() - educTimeRange;
          // Get comparison data if needed
          let compData = educActivityData[actCode];
          if (!compData) {
            const compRes = await tuResearchAPI.getEducationComparison<EducationComparisonData>(actCode);
            compData = compRes.data;
            setEducActivityData(prev => ({ ...prev, [actCode]: compData }));
          }
          // Get timeline data if needed
          if (!educTimelineData[actCode] && compData) {
            const educCodes = compData.comparisons?.map(c => c.educ_code).join(',') || '';
            if (educCodes) {
              const timelineRes = await tuResearchAPI.getEducationTimeline<EducationTimelineData>(actCode, educCodes, 'avg_hours', startYear);
              setEducTimelineData(prev => ({ ...prev, [actCode]: timelineRes.data }));
            }
          }
        } catch (error) {
          console.error(`Error loading education data for ${actCode}:`, error);
        } finally {
          setEducLoading(false);
        }
      }
    }
  };

  // Section 7: Race toggle
  const toggleRaceActivity = async (actCode: string): Promise<void> => {
    if (raceActivities.includes(actCode)) {
      setRaceActivities(raceActivities.filter(id => id !== actCode));
    } else if (raceActivities.length < 5) {
      setRaceActivities([...raceActivities, actCode]);
      // Load data if not already loaded
      if (!raceActivityData[actCode] || !raceTimelineData[actCode]) {
        setRaceLoading(true);
        try {
          const startYear = raceTimeRange === 0 ? undefined : new Date().getFullYear() - raceTimeRange;
          // Get comparison data if needed
          let compData = raceActivityData[actCode];
          if (!compData) {
            const compRes = await tuResearchAPI.getRaceComparison<RaceComparisonData>(actCode);
            compData = compRes.data;
            setRaceActivityData(prev => ({ ...prev, [actCode]: compData }));
          }
          // Get timeline data if needed
          if (!raceTimelineData[actCode] && compData) {
            const raceCodes = compData.comparisons?.map(c => c.race_code).join(',') || '';
            if (raceCodes) {
              const timelineRes = await tuResearchAPI.getRaceTimeline<RaceTimelineData>(actCode, raceCodes, 'avg_hours', startYear);
              setRaceTimelineData(prev => ({ ...prev, [actCode]: timelineRes.data }));
            }
          }
        } catch (error) {
          console.error(`Error loading race data for ${actCode}:`, error);
        } finally {
          setRaceLoading(false);
        }
      }
    }
  };

  // Section 8: Day Type toggle
  const toggleDayTypeActivity = async (actCode: string): Promise<void> => {
    if (dayTypeActivities.includes(actCode)) {
      setDayTypeActivities(dayTypeActivities.filter(id => id !== actCode));
    } else if (dayTypeActivities.length < 5) {
      setDayTypeActivities([...dayTypeActivities, actCode]);
      // Load data if not already loaded
      if (!dayTypeActivityData[actCode] || !dayTypeTimelineData[actCode]) {
        setDayTypeLoading(true);
        try {
          const startYear = dayTypeTimeRange === 0 ? undefined : new Date().getFullYear() - dayTypeTimeRange;
          // Get comparison data if needed
          let compData = dayTypeActivityData[actCode];
          if (!compData) {
            const compRes = await tuResearchAPI.getDayTypeComparison<DayTypeComparisonData>(actCode);
            compData = compRes.data;
            setDayTypeActivityData(prev => ({ ...prev, [actCode]: compData }));
          }
          // Get timeline data if needed
          if (!dayTypeTimelineData[actCode] && compData) {
            const daytypeCodes = compData.comparisons?.map(c => c.pertype_code).join(',') || '';
            if (daytypeCodes) {
              const timelineRes = await tuResearchAPI.getDayTypeTimeline<DayTypeTimelineData>(actCode, daytypeCodes, 'avg_hours', startYear);
              setDayTypeTimelineData(prev => ({ ...prev, [actCode]: timelineRes.data }));
            }
          }
        } catch (error) {
          console.error(`Error loading day type data for ${actCode}:`, error);
        } finally {
          setDayTypeLoading(false);
        }
      }
    }
  };

  // Combined chart data for sex comparison (Male vs Female over time)
  const combinedSexChartData = useMemo(() => {
    if (sexActivities.length === 0) return [];
    const periodMap = new Map<number, { year: number; period_name: string; [key: string]: string | number }>();

    sexActivities.forEach(actCode => {
      const timelineData = sexTimelineData[actCode]?.timeline;
      if (timelineData) {
        timelineData.forEach(point => {
          if (!periodMap.has(point.year)) {
            periodMap.set(point.year, { year: point.year, period_name: point.period_name });
          }
          const existing = periodMap.get(point.year)!;
          const actName = sexActivityData[actCode]?.actcode_text?.substring(0, 15) || actCode;
          if (point.male !== null && point.male !== undefined) {
            existing[`${actName} (M)`] = point.male;
          }
          if (point.female !== null && point.female !== undefined) {
            existing[`${actName} (F)`] = point.female;
          }
        });
      }
    });

    return Array.from(periodMap.values()).sort((a, b) => a.year - b.year);
  }, [sexActivities, sexTimelineData, sexActivityData]);

  // Combined chart data for age comparison (multiple age groups over time)
  const combinedAgeChartData = useMemo(() => {
    if (ageActivities.length === 0) return [];
    const periodMap = new Map<number, { year: number; period_name: string; [key: string]: string | number }>();

    ageActivities.forEach(actCode => {
      const timelineData = ageTimelineData[actCode]?.timeline;
      if (timelineData) {
        timelineData.forEach(point => {
          if (!periodMap.has(point.year)) {
            periodMap.set(point.year, { year: point.year, period_name: point.period_name });
          }
          const existing = periodMap.get(point.year)!;
          const actName = ageActivityData[actCode]?.actcode_text?.substring(0, 10) || actCode;
          if (point.ages) {
            Object.entries(point.ages).forEach(([ageCode, value]) => {
              if (value !== null && value !== undefined) {
                const ageName = ageTimelineData[actCode]?.age_names?.[ageCode] || ageCode;
                existing[`${actName}-${ageName.substring(0, 8)}`] = value;
              }
            });
          }
        });
      }
    });

    return Array.from(periodMap.values()).sort((a, b) => a.year - b.year);
  }, [ageActivities, ageTimelineData, ageActivityData]);

  // Combined chart data for labor force comparison (multiple labor force statuses over time)
  const combinedLfChartData = useMemo(() => {
    if (lfActivities.length === 0) return [];
    const periodMap = new Map<number, { year: number; period_name: string; [key: string]: string | number }>();

    lfActivities.forEach(actCode => {
      const timelineData = lfTimelineData[actCode]?.timeline;
      if (timelineData) {
        timelineData.forEach(point => {
          if (!periodMap.has(point.year)) {
            periodMap.set(point.year, { year: point.year, period_name: point.period_name });
          }
          const existing = periodMap.get(point.year)!;
          const actName = lfActivityData[actCode]?.actcode_text?.substring(0, 10) || actCode;
          if (point.statuses) {
            Object.entries(point.statuses).forEach(([lfCode, value]) => {
              if (value !== null && value !== undefined) {
                const lfName = lfTimelineData[actCode]?.status_names?.[lfCode] || lfCode;
                existing[`${actName}-${lfName.substring(0, 8)}`] = value;
              }
            });
          }
        });
      }
    });

    return Array.from(periodMap.values()).sort((a, b) => a.year - b.year);
  }, [lfActivities, lfTimelineData, lfActivityData]);

  // Combined chart data for education comparison (multiple education levels over time)
  const combinedEducChartData = useMemo(() => {
    if (educActivities.length === 0) return [];
    const periodMap = new Map<number, { year: number; period_name: string; [key: string]: string | number }>();

    educActivities.forEach(actCode => {
      const timelineData = educTimelineData[actCode]?.timeline;
      if (timelineData) {
        timelineData.forEach(point => {
          if (!periodMap.has(point.year)) {
            periodMap.set(point.year, { year: point.year, period_name: point.period_name });
          }
          const existing = periodMap.get(point.year)!;
          const actName = educActivityData[actCode]?.actcode_text?.substring(0, 10) || actCode;
          if (point.educations) {
            Object.entries(point.educations).forEach(([educCode, value]) => {
              if (value !== null && value !== undefined) {
                const educName = educTimelineData[actCode]?.educ_names?.[educCode] || educCode;
                existing[`${actName}-${educName.substring(0, 8)}`] = value;
              }
            });
          }
        });
      }
    });

    return Array.from(periodMap.values()).sort((a, b) => a.year - b.year);
  }, [educActivities, educTimelineData, educActivityData]);

  // Combined chart data for race comparison (multiple races over time)
  const combinedRaceChartData = useMemo(() => {
    if (raceActivities.length === 0) return [];
    const periodMap = new Map<number, { year: number; period_name: string; [key: string]: string | number }>();

    raceActivities.forEach(actCode => {
      const timelineData = raceTimelineData[actCode]?.timeline;
      if (timelineData) {
        timelineData.forEach(point => {
          if (!periodMap.has(point.year)) {
            periodMap.set(point.year, { year: point.year, period_name: point.period_name });
          }
          const existing = periodMap.get(point.year)!;
          const actName = raceActivityData[actCode]?.actcode_text?.substring(0, 10) || actCode;
          if (point.races) {
            Object.entries(point.races).forEach(([raceCode, value]) => {
              if (value !== null && value !== undefined) {
                const raceName = raceTimelineData[actCode]?.race_names?.[raceCode] || raceCode;
                existing[`${actName}-${raceName.substring(0, 8)}`] = value;
              }
            });
          }
        });
      }
    });

    return Array.from(periodMap.values()).sort((a, b) => a.year - b.year);
  }, [raceActivities, raceTimelineData, raceActivityData]);

  // Combined chart data for day type comparison (weekday vs weekend over time)
  const combinedDayTypeChartData = useMemo(() => {
    if (dayTypeActivities.length === 0) return [];
    const periodMap = new Map<number, { year: number; period_name: string; [key: string]: string | number }>();

    dayTypeActivities.forEach(actCode => {
      const timelineData = dayTypeTimelineData[actCode]?.timeline;
      if (timelineData) {
        timelineData.forEach(point => {
          if (!periodMap.has(point.year)) {
            periodMap.set(point.year, { year: point.year, period_name: point.period_name });
          }
          const existing = periodMap.get(point.year)!;
          const actName = dayTypeActivityData[actCode]?.actcode_text?.substring(0, 10) || actCode;
          if (point.day_types) {
            Object.entries(point.day_types).forEach(([daytypeCode, value]) => {
              if (value !== null && value !== undefined) {
                const daytypeName = dayTypeTimelineData[actCode]?.day_type_names?.[daytypeCode] || daytypeCode;
                existing[`${actName}-${daytypeName.substring(0, 8)}`] = value;
              }
            });
          }
        });
      }
    });

    return Array.from(periodMap.values()).sort((a, b) => a.year - b.year);
  }, [dayTypeActivities, dayTypeTimelineData, dayTypeActivityData]);

  // Load chart data for selected series
  useEffect(() => {
    const loadChartData = async (): Promise<void> => {
      const startYear = seriesTimeRange === 0 ? undefined : new Date().getFullYear() - seriesTimeRange;
      const newChartData: SeriesChartDataMap = {};
      for (const seriesId of selectedSeries) {
        if (!seriesChartData[seriesId]) {
          try {
            const response = await tuResearchAPI.getSeriesData<SeriesDataResponse>(seriesId, startYear);
            newChartData[seriesId] = response.data;
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
  }, [selectedSeries, seriesTimeRange]);

  // Combined chart data from all selected series
  const combinedChartData = useMemo((): CombinedChartDataPoint[] => {
    const periodMap = new Map<string, CombinedChartDataPoint>();
    selectedSeries.forEach(seriesId => {
      const data = seriesChartData[seriesId]?.series?.[0]?.data_points;
      if (data) {
        data.forEach(point => {
          const key = `${point.year}-${point.period}`;
          if (!periodMap.has(key)) {
            periodMap.set(key, {
              period_name: point.period_name,
              sortKey: point.year * 100 + parseInt(point.period?.substring(1) || '0')
            });
          }
          const existing = periodMap.get(key)!;
          if (point.value !== null && point.value !== undefined) {
            existing[seriesId] = point.value;
          }
        });
      }
    });
    return Array.from(periodMap.values()).sort((a, b) => a.sortKey - b.sortKey);
  }, [selectedSeries, seriesChartData]);

  // ============================================================================
  // RENDER HELPERS
  // ============================================================================

  const renderLoading = (): ReactElement => (
    <div className="flex items-center justify-center p-8">
      <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
    </div>
  );

  // ============================================================================
  // SECTION 1: OVERVIEW
  // ============================================================================

  const renderOverview = (): ReactElement => (
    <Card className="mb-6">
      <SectionHeader title="1. Time Use Overview" color="blue" icon={Clock} />
      <div className="p-5">
        {/* Controls */}
        <div className="flex items-center gap-4 mb-4 flex-wrap">
          <Select
            label="Time Range"
            value={overviewTimeRange}
            onChange={(v) => setOverviewTimeRange(parseInt(v))}
            options={timeRangeOptions}
            className="w-40"
          />
          <div className="ml-auto">
            <ViewToggle view={overviewView} onViewChange={setOverviewView} />
          </div>
        </div>

        <Covid2020Note />

        {overviewLoading ? renderLoading() : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {overviewData?.activities?.slice(0, 4).map((act) => (
                <MetricCard
                  key={act.actcode_code}
                  title={act.actcode_text.substring(0, 30)}
                  value={formatHours(act.avg_hours_per_day) + ' hrs'}
                  change={act.yoy_change}
                  subtitle={`${act.latest_year || ''}`}
                />
              ))}
            </div>

            {overviewView === 'chart' && overviewTimeline && (
              <>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={overviewTimeline.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period_name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    {Object.entries(overviewTimeline.activity_names || {}).slice(0, 6).map(([code, name], idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={`activities.${code}`}
                        name={name.substring(0, 25)}
                        stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                        strokeWidth={2}
                        dot={false}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
                <TimelineSelector
                  timeline={overviewTimeline.timeline}
                  selectedIndex={overviewSelectedIndex}
                  onSelectIndex={setOverviewSelectedIndex}
                />
                {overviewSelectedIndex !== null && overviewTimeline.timeline[overviewSelectedIndex] && (
                  <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm font-medium text-blue-700 mb-2">
                      {overviewTimeline.timeline[overviewSelectedIndex].period_name}
                    </p>
                    <div className="grid grid-cols-3 gap-2">
                      {Object.entries(overviewTimeline.timeline[overviewSelectedIndex].activities || {}).slice(0, 6).map(([code, value]) => (
                        <div key={code} className="text-xs">
                          <span className="text-gray-600">{(overviewTimeline.activity_names[code] || code).substring(0, 20)}:</span>
                          <span className="ml-1 font-medium">{formatHours(value)} hrs</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {overviewView === 'table' && overviewData && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left font-medium text-gray-600">Activity</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-600">Avg Hours/Day</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-600">YoY Change</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {overviewData.activities?.map((act) => (
                      <tr key={act.actcode_code} className="hover:bg-gray-50">
                        <td className="px-4 py-2 text-gray-900">{act.actcode_text}</td>
                        <td className="px-4 py-2 text-right font-medium">{formatHours(act.avg_hours_per_day)}</td>
                        <td className={`px-4 py-2 text-right ${(act.yoy_change ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatChange(act.yoy_change)}
                        </td>
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
  );

  // ============================================================================
  // SECTION 2: ACTIVITY ANALYSIS
  // ============================================================================

  const renderActivityAnalysis = (): ReactElement => (
    <Card className="mb-6">
      <SectionHeader title="2. Activity Analysis" color="green" icon={Calendar} />
      <div className="p-5">
        <div className="flex items-center gap-4 mb-4 flex-wrap">
          <Select
            label="Activity"
            value={selectedActivity}
            onChange={setSelectedActivity}
            options={activityOptions}
            className="w-64"
          />
          <Select
            label="Time Range"
            value={activityTimeRange}
            onChange={(v) => setActivityTimeRange(parseInt(v))}
            options={timeRangeOptions}
            className="w-40"
          />
          <div className="ml-auto">
            <ViewToggle view={activityView} onViewChange={setActivityView} />
          </div>
        </div>

        {activityLoading ? renderLoading() : (
          <>
            {activityView === 'chart' && activityTimeline && (
              <>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={activityTimeline.timeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period_name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    {Object.entries(activityTimeline.activity_names || {}).slice(0, 1).map(([code, name], idx) => (
                      <Line
                        key={code}
                        type="monotone"
                        dataKey={`activities.${code}`}
                        name={name.substring(0, 30)}
                        stroke={CHART_COLORS[idx]}
                        strokeWidth={2}
                        dot={false}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
                <TimelineSelector
                  timeline={activityTimeline.timeline}
                  selectedIndex={activitySelectedIndex}
                  onSelectIndex={setActivitySelectedIndex}
                />
              </>
            )}

            {activityView === 'table' && activityData && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left font-medium text-gray-600">Sub-Activity</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-600">Avg Hours/Day</th>
                      <th className="px-4 py-2 text-right font-medium text-gray-600">YoY Change</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {activityData.activities?.map((act) => (
                      <tr key={act.actcode_code} className="hover:bg-gray-50">
                        <td className="px-4 py-2 text-gray-900" style={{ paddingLeft: `${(act.display_level ?? 0) * 16 + 16}px` }}>
                          {act.actcode_text}
                        </td>
                        <td className="px-4 py-2 text-right font-medium">{formatHours(act.avg_hours_per_day)}</td>
                        <td className={`px-4 py-2 text-right ${(act.yoy_change_hours ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatChange(act.yoy_change_hours)}
                        </td>
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
  );

  // ============================================================================
  // SECTION 3: SEX COMPARISON
  // ============================================================================

  const renderSexComparison = (): ReactElement => {
    // Helper to get male/female values for a SELECTED activity
    const getMaleValue = (actCode: string) => {
      const data = sexActivityData[actCode];
      const male = data?.comparisons?.find(c => c.sex_code === '1');
      return male?.avg_hours_per_day;
    };
    const getFemaleValue = (actCode: string) => {
      const data = sexActivityData[actCode];
      const female = data?.comparisons?.find(c => c.sex_code === '2');
      return female?.avg_hours_per_day;
    };
    const getDiff = (actCode: string) => {
      const male = getMaleValue(actCode);
      const female = getFemaleValue(actCode);
      if (male !== undefined && male !== null && female !== undefined && female !== null) {
        return male - female;
      }
      return null;
    };

    // Get chart line keys from combinedSexChartData
    const chartLineKeys = combinedSexChartData.length > 0
      ? Object.keys(combinedSexChartData[0]).filter(k => k !== 'year' && k !== 'period_name')
      : [];

    return (
      <Card className="mb-6">
        <SectionHeader title="3. Time Use by Sex" color="purple" icon={Users} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">Click to add activities for Male vs Female comparison (max 5)</p>

          <Covid2020Note />

          {/* Activity List - click to add */}
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-2 px-3 w-8"></th>
                  <th className="py-2 px-3 text-left font-medium text-gray-600">Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {MAJOR_ACTIVITY_CODES.map((actCode) => {
                  const isSelected = sexActivities.includes(actCode);
                  return (
                    <tr
                      key={actCode}
                      className={`cursor-pointer ${isSelected ? 'bg-purple-50' : 'hover:bg-gray-50'}`}
                      onClick={() => toggleSexActivity(actCode)}
                    >
                      <td className="py-2 px-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelected && sexActivities.length >= 5}
                          readOnly
                          className="rounded"
                        />
                      </td>
                      <td className="py-2 px-3 text-gray-900">
                        {ACTIVITY_NAMES[actCode] || actCode}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Activities - show comparison data */}
          {sexActivities.length > 0 && (
            <div className="border border-gray-200 rounded-lg mt-4">
              <div className="px-4 py-3 bg-gradient-to-r from-purple-100 to-pink-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-purple-800">
                    Male vs Female Comparison
                  </p>
                  <p className="text-xs text-gray-600">{sexActivities.length}/5 activities selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={sexTimeRange.toString()}
                    onChange={(v) => {
                      setSexTimeRange(Number(v));
                      setSexTimelineData({}); // Clear cache to reload with new range
                    }}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <ViewToggle view={sexView} onViewChange={setSexView} />
                  <button
                    onClick={() => setSexActivities([])}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                {/* Selected activity tags with data */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {sexActivities.map((actCode, idx) => (
                    <div
                      key={actCode}
                      className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded border text-xs"
                      style={{ borderLeftColor: CHART_COLORS[idx % CHART_COLORS.length], borderLeftWidth: 3 }}
                    >
                      <span className="font-medium">{sexActivityData[actCode]?.actcode_text?.substring(0, 15) || actCode}</span>
                      {sexActivityData[actCode] && (
                        <span className="text-gray-500">
                          M: <span className="text-blue-600 font-medium">{formatHours(getMaleValue(actCode))}</span>
                          {' / '}
                          F: <span className="text-pink-600 font-medium">{formatHours(getFemaleValue(actCode))}</span>
                          {getDiff(actCode) !== null && (
                            <span className={getDiff(actCode)! >= 0 ? 'text-blue-600' : 'text-pink-600'}>
                              {' '}({formatChange(getDiff(actCode))})
                            </span>
                          )}
                        </span>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleSexActivity(actCode); }}
                        className="ml-1 text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>

                    {sexLoading ? renderLoading() : (
                      combinedSexChartData.length > 0 && (
                        sexView === 'chart' ? (
                          <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                              <LineChart data={combinedSexChartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                                <YAxis tick={{ fontSize: 10 }} />
                                <Tooltip />
                                <Legend wrapperStyle={{ fontSize: '10px' }} />
                                {chartLineKeys.map((key, idx) => (
                                  <Line
                                    key={key}
                                    type="monotone"
                                    dataKey={key}
                                    name={key}
                                    stroke={key.includes('(M)') ? '#3b82f6' : '#ec4899'}
                                    strokeWidth={2}
                                    strokeDasharray={idx >= 2 ? '5 5' : undefined}
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
                                  <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Year</th>
                                  {chartLineKeys.map((key) => (
                                    <th key={key} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                      {key}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {combinedSexChartData.slice().reverse().map((row) => (
                                  <tr key={row.period_name} className="border-b border-gray-100 hover:bg-gray-50">
                                    <td className="py-2 px-3 font-medium">{row.period_name}</td>
                                    {chartLineKeys.map((key) => (
                                      <td key={key} className="py-2 px-3 text-right">
                                        {row[key] != null ? (row[key] as number).toFixed(2) : '-'}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )
                      )
                    )}
              </div>
            </div>
          )}
        </div>
      </Card>
    );
  };

  // ============================================================================
  // SECTION 4: AGE COMPARISON
  // ============================================================================

  const renderAgeComparison = (): ReactElement => {
    // Age labels for display
    const ageLabels: { [key: string]: string } = {
      '015': '15-24', '025': '25-34', '035': '35-44',
      '045': '45-54', '055': '55-64', '065': '65+'
    };

    // Helper to get value for specific age group (for selected activities only)
    const getAgeValue = (actCode: string, ageCode: string) => {
      const data = ageActivityData[actCode];
      const ageComp = data?.comparisons?.find(c => c.age_code === ageCode);
      return ageComp?.avg_hours_per_day;
    };

    // Get chart line keys
    const ageChartKeys = combinedAgeChartData.length > 0
      ? Object.keys(combinedAgeChartData[0]).filter(k => k !== 'year' && k !== 'period_name')
      : [];

    return (
      <Card className="mb-6">
        <SectionHeader title="4. Time Use by Age Group" color="orange" icon={Users} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">Click to add activities for age group comparison (max 5)</p>

          <Covid2020Note />

          {/* Activity List - click to add */}
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-2 px-3 w-8"></th>
                  <th className="py-2 px-3 text-left font-medium text-gray-600">Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {MAJOR_ACTIVITY_CODES.map((actCode) => {
                  const isSelected = ageActivities.includes(actCode);
                  return (
                    <tr
                      key={actCode}
                      className={`cursor-pointer ${isSelected ? 'bg-orange-50' : 'hover:bg-gray-50'}`}
                      onClick={() => toggleAgeActivity(actCode)}
                    >
                      <td className="py-2 px-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelected && ageActivities.length >= 5}
                          readOnly
                          className="rounded"
                        />
                      </td>
                      <td className="py-2 px-3 text-gray-900">
                        {ACTIVITY_NAMES[actCode] || actCode}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Activities - show comparison data */}
          {ageActivities.length > 0 && (
            <div className="border border-gray-200 rounded-lg mt-4">
              <div className="px-4 py-3 bg-gradient-to-r from-orange-100 to-amber-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-orange-800">Age Group Comparison</p>
                  <p className="text-xs text-gray-600">{ageActivities.length}/5 activities selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={ageTimeRange.toString()}
                    onChange={(v) => {
                      setAgeTimeRange(Number(v));
                      setAgeTimelineData({}); // Clear cache to reload
                    }}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <ViewToggle view={ageView} onViewChange={setAgeView} />
                  <button
                    onClick={() => setAgeActivities([])}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                {/* Selected activity tags with age breakdown */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {ageActivities.map((actCode, idx) => (
                    <div
                      key={actCode}
                      className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded border text-xs"
                      style={{ borderLeftColor: CHART_COLORS[idx % CHART_COLORS.length], borderLeftWidth: 3 }}
                    >
                      <span className="font-medium">{ageActivityData[actCode]?.actcode_text?.substring(0, 12) || actCode}</span>
                      {ageActivityData[actCode] && (
                        <span className="text-gray-500">
                          {selectedAges.slice(0, 3).map(age => (
                            <span key={age} className="mr-1">
                              {ageLabels[age]}: <span className="font-medium">{formatHours(getAgeValue(actCode, age))}</span>
                            </span>
                          ))}
                        </span>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleAgeActivity(actCode); }}
                        className="ml-1 text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>

                {ageLoading ? renderLoading() : (
                  combinedAgeChartData.length > 0 && (
                    ageView === 'chart' ? (
                      <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={combinedAgeChartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                            <YAxis tick={{ fontSize: 10 }} />
                            <Tooltip />
                            <Legend wrapperStyle={{ fontSize: '9px' }} />
                            {ageChartKeys.map((key, idx) => (
                              <Line
                                key={key}
                                type="monotone"
                                dataKey={key}
                                name={key}
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
                              <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Year</th>
                              {ageChartKeys.map((key) => (
                                <th key={key} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {combinedAgeChartData.slice().reverse().map((row) => (
                              <tr key={row.period_name} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-2 px-3 font-medium">{row.period_name}</td>
                                {ageChartKeys.map((key) => (
                                  <td key={key} className="py-2 px-3 text-right">
                                    {row[key] != null ? (row[key] as number).toFixed(2) : '-'}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </Card>
    );
  };

  // ============================================================================
  // SECTION 5: LABOR FORCE STATUS
  // ============================================================================

  const renderLaborForce = (): ReactElement => {
    // Get labor force statuses dynamically from the comparison data
    const lfStatuses: string[] = [];
    const lfLabels: { [key: string]: string } = {};

    // Build statuses and labels from the first activity's comparison data
    const firstActCode = lfActivities.find(ac => lfActivityData[ac]?.comparisons?.length);
    if (firstActCode && lfActivityData[firstActCode]?.comparisons) {
      lfActivityData[firstActCode].comparisons.forEach(comp => {
        if (!lfStatuses.includes(comp.lfstat_code)) {
          lfStatuses.push(comp.lfstat_code);
          lfLabels[comp.lfstat_code] = comp.lfstat_text;
        }
      });
    }

    // Helper to get value for specific labor force status (for selected activities only)
    const getLfValue = (actCode: string, lfCode: string) => {
      const data = lfActivityData[actCode];
      const lfComp = data?.comparisons?.find(c => c.lfstat_code === lfCode);
      return lfComp?.avg_hours_per_day;
    };

    // Get chart line keys from combined timeline data
    const lfChartKeys = combinedLfChartData.length > 0
      ? Object.keys(combinedLfChartData[0]).filter(k => k !== 'year' && k !== 'period_name')
      : [];

    return (
      <Card className="mb-6">
        <SectionHeader title="5. Time Use by Labor Force Status" color="cyan" icon={Users} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">Click to add activities for labor force status comparison (max 5)</p>

          <Covid2020Note />

          {/* Activity List - click to add */}
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-2 px-3 w-8"></th>
                  <th className="py-2 px-3 text-left font-medium text-gray-600">Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {MAJOR_ACTIVITY_CODES.map((actCode) => {
                  const isSelected = lfActivities.includes(actCode);
                  return (
                    <tr
                      key={actCode}
                      className={`cursor-pointer ${isSelected ? 'bg-cyan-50' : 'hover:bg-gray-50'}`}
                      onClick={() => toggleLfActivity(actCode)}
                    >
                      <td className="py-2 px-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelected && lfActivities.length >= 5}
                          readOnly
                          className="rounded"
                        />
                      </td>
                      <td className="py-2 px-3 text-gray-900">
                        {ACTIVITY_NAMES[actCode] || actCode}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Activities - show comparison data */}
          {lfActivities.length > 0 && (
            <div className="border border-gray-200 rounded-lg mt-4">
              <div className="px-4 py-3 bg-gradient-to-r from-cyan-100 to-teal-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-cyan-800">Labor Force Status Comparison</p>
                  <p className="text-xs text-gray-600">{lfActivities.length}/5 activities selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={lfTimeRange.toString()}
                    onChange={(v) => {
                      setLfTimeRange(Number(v));
                      setLfTimelineData({}); // Clear cache to reload with new range
                    }}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <ViewToggle view={lfView} onViewChange={setLfView} />
                  <button
                    onClick={() => setLfActivities([])}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                {/* Selected activity tags with data */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {lfActivities.map((actCode, idx) => (
                    <div
                      key={actCode}
                      className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded border text-xs"
                      style={{ borderLeftColor: CHART_COLORS[idx % CHART_COLORS.length], borderLeftWidth: 3 }}
                    >
                      <span className="font-medium">{lfActivityData[actCode]?.actcode_text?.substring(0, 12) || actCode}</span>
                      {lfActivityData[actCode] && (
                        <span className="text-gray-500">
                          {lfStatuses.map(lf => (
                            <span key={lf} className="mr-1">
                              {lfLabels[lf]}: <span className="font-medium">{formatHours(getLfValue(actCode, lf))}</span>
                            </span>
                          ))}
                        </span>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleLfActivity(actCode); }}
                        className="ml-1 text-gray-400 hover:text-gray-600"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>

                {lfLoading ? renderLoading() : (
                  lfView === 'chart' ? (
                    <>
                      {/* Bar chart for current year comparison */}
                      <div className="h-60 mb-6">
                        <p className="text-xs text-gray-500 mb-2">Current Year Comparison</p>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={lfActivities.map(actCode => ({
                              name: lfActivityData[actCode]?.actcode_text?.substring(0, 20) || actCode,
                              ...Object.fromEntries(
                                lfStatuses.map(lfCode => [
                                  lfLabels[lfCode] || lfCode,
                                  getLfValue(actCode, lfCode)
                                ])
                              )
                            }))}
                            layout="vertical"
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" tick={{ fontSize: 10 }} />
                            <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 9 }} />
                            <Tooltip />
                            <Legend wrapperStyle={{ fontSize: '10px' }} />
                            {lfStatuses.map((lfCode, idx) => (
                              <Bar
                                key={lfCode}
                                dataKey={lfLabels[lfCode] || lfCode}
                                name={lfLabels[lfCode] || lfCode}
                                fill={CHART_COLORS[idx % CHART_COLORS.length]}
                              />
                            ))}
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Timeline chart showing historical trends */}
                      {combinedLfChartData.length > 0 && (
                        <div className="h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Trends</p>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={combinedLfChartData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                              <YAxis tick={{ fontSize: 10 }} />
                              <Tooltip />
                              <Legend wrapperStyle={{ fontSize: '10px' }} />
                              {lfChartKeys.map((key, idx) => (
                                <Line
                                  key={key}
                                  type="monotone"
                                  dataKey={key}
                                  name={key}
                                  stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                                  strokeWidth={2}
                                  dot={{ r: 2 }}
                                  connectNulls
                                />
                              ))}
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      {/* Table view */}
                      <div className="overflow-x-auto max-h-96 mb-4">
                        <p className="text-xs text-gray-500 mb-2">Current Year Data</p>
                        <table className="w-full text-sm">
                          <thead className="sticky top-0 bg-gray-50">
                            <tr className="border-b border-gray-200">
                              <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Activity</th>
                              {lfStatuses.map((lfCode) => (
                                <th key={lfCode} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                  {lfLabels[lfCode] || lfCode}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {lfActivities.map((actCode) => (
                              <tr key={actCode} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-2 px-3 font-medium">
                                  {lfActivityData[actCode]?.actcode_text?.substring(0, 30) || actCode}
                                </td>
                                {lfStatuses.map((lfCode) => (
                                  <td key={lfCode} className="py-2 px-3 text-right">
                                    {formatHours(getLfValue(actCode, lfCode))}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Timeline table */}
                      {combinedLfChartData.length > 0 && (
                        <div className="overflow-x-auto max-h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Data</p>
                          <table className="w-full text-sm">
                            <thead className="sticky top-0 bg-gray-50">
                              <tr className="border-b border-gray-200">
                                <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Year</th>
                                {lfChartKeys.map((key) => (
                                  <th key={key} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {combinedLfChartData.slice().reverse().map((row) => (
                                <tr key={row.period_name} className="border-b border-gray-100 hover:bg-gray-50">
                                  <td className="py-2 px-3 font-medium">{row.period_name}</td>
                                  {lfChartKeys.map((key) => (
                                    <td key={key} className="py-2 px-3 text-right">
                                      {row[key] != null ? (row[key] as number).toFixed(2) : '-'}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </Card>
    );
  };

  // ============================================================================
  // SECTION 6: EDUCATION COMPARISON
  // ============================================================================

  const renderEducation = (): ReactElement => {
    // Helper to get value for specific education level
    const getEducValue = (actCode: string, educCode: string) => {
      const data = educActivityData[actCode];
      const educComp = data?.comparisons?.find(c => c.educ_code === educCode);
      return educComp?.avg_hours_per_day;
    };

    // Get all education labels from first loaded activity
    const educLabels: { [key: string]: string } = {};
    const firstActData = educActivityData[educActivities[0]];
    if (firstActData?.comparisons) {
      firstActData.comparisons.forEach(c => {
        educLabels[c.educ_code] = c.educ_text.substring(0, 20);
      });
    }
    const educCodes = Object.keys(educLabels);

    return (
      <Card className="mb-6">
        <SectionHeader title="6. Time Use by Education Level" color="purple" icon={Users} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">Click to add activities for education level comparison (max 5)</p>

          <Covid2020Note />

          {/* Activity List - click to add */}
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-2 px-3 w-8"></th>
                  <th className="py-2 px-3 text-left font-medium text-gray-600">Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {EDUCATION_BREAKDOWN_ACTIVITIES.map((actCode) => {
                  const isSelected = educActivities.includes(actCode);
                  return (
                    <tr
                      key={actCode}
                      className={`cursor-pointer ${isSelected ? 'bg-purple-50' : 'hover:bg-gray-50'}`}
                      onClick={() => toggleEducActivity(actCode)}
                    >
                      <td className="py-2 px-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelected && educActivities.length >= 5}
                          readOnly
                          className="rounded"
                        />
                      </td>
                      <td className="py-2 px-3 text-gray-900">
                        {ACTIVITY_NAMES[actCode] || actCode}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Activities - show comparison data */}
          {educActivities.length > 0 && (
            <div className="border border-gray-200 rounded-lg mt-4">
              <div className="px-4 py-3 bg-gradient-to-r from-purple-100 to-pink-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-purple-800">Education Level Comparison (Adults 25+)</p>
                  <p className="text-xs text-gray-600">{educActivities.length}/5 activities selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={educTimeRange.toString()}
                    onChange={(v) => {
                      setEducTimeRange(Number(v));
                      setEducTimelineData({}); // Clear cache to reload with new range
                    }}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <ViewToggle view={educView} onViewChange={setEducView} />
                  <button
                    onClick={() => setEducActivities([])}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                {educLoading ? renderLoading() : (
                  educView === 'chart' ? (
                    <>
                      {/* Bar chart for current year comparison */}
                      <div className="h-60 mb-6">
                        <p className="text-xs text-gray-500 mb-2">Current Year Comparison</p>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={educActivities.map(actCode => ({
                              name: educActivityData[actCode]?.actcode_text?.substring(0, 20) || actCode,
                              ...Object.fromEntries(
                                educCodes.map(educCode => [
                                  educLabels[educCode] || educCode,
                                  getEducValue(actCode, educCode)
                                ])
                              )
                            }))}
                            layout="vertical"
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" tick={{ fontSize: 10 }} />
                            <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 9 }} />
                            <Tooltip />
                            <Legend wrapperStyle={{ fontSize: '10px' }} />
                            {educCodes.slice(0, 5).map((educCode, idx) => (
                              <Bar
                                key={educCode}
                                dataKey={educLabels[educCode] || educCode}
                                name={educLabels[educCode] || educCode}
                                fill={CHART_COLORS[idx % CHART_COLORS.length]}
                              />
                            ))}
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Timeline chart showing historical trends */}
                      {combinedEducChartData.length > 0 && (
                        <div className="h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Trends</p>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={combinedEducChartData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                              <YAxis tick={{ fontSize: 10 }} />
                              <Tooltip />
                              <Legend wrapperStyle={{ fontSize: '10px' }} />
                              {Object.keys(combinedEducChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key, idx) => (
                                <Line
                                  key={key}
                                  type="monotone"
                                  dataKey={key}
                                  name={key}
                                  stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                                  strokeWidth={2}
                                  dot={{ r: 2 }}
                                  connectNulls
                                />
                              ))}
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      {/* Table view - current year */}
                      <div className="overflow-x-auto max-h-64 mb-4">
                        <p className="text-xs text-gray-500 mb-2">Current Year Data</p>
                        <table className="w-full text-sm">
                          <thead className="sticky top-0 bg-gray-50">
                            <tr className="border-b border-gray-200">
                              <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Activity</th>
                              {educCodes.map((educCode) => (
                                <th key={educCode} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                  {educLabels[educCode] || educCode}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {educActivities.map((actCode) => (
                              <tr key={actCode} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-2 px-3 font-medium">
                                  {educActivityData[actCode]?.actcode_text?.substring(0, 30) || actCode}
                                </td>
                                {educCodes.map((educCode) => (
                                  <td key={educCode} className="py-2 px-3 text-right">
                                    {formatHours(getEducValue(actCode, educCode))}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Timeline table */}
                      {combinedEducChartData.length > 0 && (
                        <div className="overflow-x-auto max-h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Data</p>
                          <table className="w-full text-sm">
                            <thead className="sticky top-0 bg-gray-50">
                              <tr className="border-b border-gray-200">
                                <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Year</th>
                                {Object.keys(combinedEducChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key) => (
                                  <th key={key} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {combinedEducChartData.slice().reverse().map((row) => (
                                <tr key={row.period_name} className="border-b border-gray-100 hover:bg-gray-50">
                                  <td className="py-2 px-3 font-medium">{row.period_name}</td>
                                  {Object.keys(combinedEducChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key) => (
                                    <td key={key} className="py-2 px-3 text-right">
                                      {row[key] != null ? (row[key] as number).toFixed(2) : '-'}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </Card>
    );
  };

  // ============================================================================
  // SECTION 7: RACE COMPARISON
  // ============================================================================

  const renderRace = (): ReactElement => {
    // Helper to get value for specific race
    const getRaceValue = (actCode: string, raceCode: string) => {
      const data = raceActivityData[actCode];
      const raceComp = data?.comparisons?.find(c => c.race_code === raceCode);
      return raceComp?.avg_hours_per_day;
    };

    // Get all race labels from first loaded activity
    const raceLabels: { [key: string]: string } = {};
    const firstActData = raceActivityData[raceActivities[0]];
    if (firstActData?.comparisons) {
      firstActData.comparisons.forEach(c => {
        raceLabels[c.race_code] = c.race_text.substring(0, 15);
      });
    }
    const raceCodes = Object.keys(raceLabels);

    return (
      <Card className="mb-6">
        <SectionHeader title="7. Time Use by Race" color="orange" icon={Users} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">Click to add activities for race comparison (max 5)</p>

          <Covid2020Note />

          {/* Activity List - click to add */}
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-2 px-3 w-8"></th>
                  <th className="py-2 px-3 text-left font-medium text-gray-600">Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {RACE_BREAKDOWN_ACTIVITIES.map((actCode) => {
                  const isSelected = raceActivities.includes(actCode);
                  return (
                    <tr
                      key={actCode}
                      className={`cursor-pointer ${isSelected ? 'bg-orange-50' : 'hover:bg-gray-50'}`}
                      onClick={() => toggleRaceActivity(actCode)}
                    >
                      <td className="py-2 px-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelected && raceActivities.length >= 5}
                          readOnly
                          className="rounded"
                        />
                      </td>
                      <td className="py-2 px-3 text-gray-900">
                        {ACTIVITY_NAMES[actCode] || actCode}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Activities - show comparison data */}
          {raceActivities.length > 0 && (
            <div className="border border-gray-200 rounded-lg mt-4">
              <div className="px-4 py-3 bg-gradient-to-r from-orange-100 to-yellow-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-orange-800">Race Comparison</p>
                  <p className="text-xs text-gray-600">{raceActivities.length}/5 activities selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={raceTimeRange.toString()}
                    onChange={(v) => {
                      setRaceTimeRange(Number(v));
                      setRaceTimelineData({}); // Clear cache to reload with new range
                    }}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <ViewToggle view={raceView} onViewChange={setRaceView} />
                  <button
                    onClick={() => setRaceActivities([])}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                {raceLoading ? renderLoading() : (
                  raceView === 'chart' ? (
                    <>
                      {/* Bar chart for current year comparison */}
                      <div className="h-60 mb-6">
                        <p className="text-xs text-gray-500 mb-2">Current Year Comparison</p>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={raceActivities.map(actCode => ({
                              name: raceActivityData[actCode]?.actcode_text?.substring(0, 20) || actCode,
                              ...Object.fromEntries(
                                raceCodes.map(raceCode => [
                                  raceLabels[raceCode] || raceCode,
                                  getRaceValue(actCode, raceCode)
                                ])
                              )
                            }))}
                            layout="vertical"
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" tick={{ fontSize: 10 }} />
                            <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 9 }} />
                            <Tooltip />
                            <Legend wrapperStyle={{ fontSize: '10px' }} />
                            {raceCodes.slice(0, 5).map((raceCode, idx) => (
                              <Bar
                                key={raceCode}
                                dataKey={raceLabels[raceCode] || raceCode}
                                name={raceLabels[raceCode] || raceCode}
                                fill={CHART_COLORS[idx % CHART_COLORS.length]}
                              />
                            ))}
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Timeline chart showing historical trends */}
                      {combinedRaceChartData.length > 0 && (
                        <div className="h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Trends</p>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={combinedRaceChartData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                              <YAxis tick={{ fontSize: 10 }} />
                              <Tooltip />
                              <Legend wrapperStyle={{ fontSize: '10px' }} />
                              {Object.keys(combinedRaceChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key, idx) => (
                                <Line
                                  key={key}
                                  type="monotone"
                                  dataKey={key}
                                  name={key}
                                  stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                                  strokeWidth={2}
                                  dot={{ r: 2 }}
                                  connectNulls
                                />
                              ))}
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      {/* Table view - current year */}
                      <div className="overflow-x-auto max-h-64 mb-4">
                        <p className="text-xs text-gray-500 mb-2">Current Year Data</p>
                        <table className="w-full text-sm">
                          <thead className="sticky top-0 bg-gray-50">
                            <tr className="border-b border-gray-200">
                              <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Activity</th>
                              {raceCodes.map((raceCode) => (
                                <th key={raceCode} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                  {raceLabels[raceCode] || raceCode}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {raceActivities.map((actCode) => (
                              <tr key={actCode} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-2 px-3 font-medium">
                                  {raceActivityData[actCode]?.actcode_text?.substring(0, 30) || actCode}
                                </td>
                                {raceCodes.map((raceCode) => (
                                  <td key={raceCode} className="py-2 px-3 text-right">
                                    {formatHours(getRaceValue(actCode, raceCode))}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Timeline table */}
                      {combinedRaceChartData.length > 0 && (
                        <div className="overflow-x-auto max-h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Data</p>
                          <table className="w-full text-sm">
                            <thead className="sticky top-0 bg-gray-50">
                              <tr className="border-b border-gray-200">
                                <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Year</th>
                                {Object.keys(combinedRaceChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key) => (
                                  <th key={key} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {combinedRaceChartData.slice().reverse().map((row) => (
                                <tr key={row.period_name} className="border-b border-gray-100 hover:bg-gray-50">
                                  <td className="py-2 px-3 font-medium">{row.period_name}</td>
                                  {Object.keys(combinedRaceChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key) => (
                                    <td key={key} className="py-2 px-3 text-right">
                                      {row[key] != null ? (row[key] as number).toFixed(2) : '-'}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </Card>
    );
  };

  // ============================================================================
  // SECTION 8: DAY TYPE COMPARISON
  // ============================================================================

  const renderDayType = (): ReactElement => {
    // Helper to get value for specific day type
    const getDayTypeValue = (actCode: string, pertypeCode: string) => {
      const data = dayTypeActivityData[actCode];
      const dayTypeComp = data?.comparisons?.find(c => c.pertype_code === pertypeCode);
      return dayTypeComp?.avg_hours_per_day;
    };

    // Get all day type labels from first loaded activity
    const dayTypeLabels: { [key: string]: string } = {};
    const firstActData = dayTypeActivityData[dayTypeActivities[0]];
    if (firstActData?.comparisons) {
      firstActData.comparisons.forEach(c => {
        dayTypeLabels[c.pertype_code] = c.pertype_text;
      });
    }
    const dayTypeCodes = Object.keys(dayTypeLabels);

    return (
      <Card className="mb-6">
        <SectionHeader title="8. Time Use by Day Type (Weekday vs Weekend)" color="red" icon={Calendar} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">Click to add activities for weekday vs weekend comparison (max 5)</p>

          <Covid2020Note />

          {/* Activity List - click to add */}
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="py-2 px-3 w-8"></th>
                  <th className="py-2 px-3 text-left font-medium text-gray-600">Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {MAJOR_ACTIVITY_CODES.map((actCode) => {
                  const isSelected = dayTypeActivities.includes(actCode);
                  return (
                    <tr
                      key={actCode}
                      className={`cursor-pointer ${isSelected ? 'bg-red-50' : 'hover:bg-gray-50'}`}
                      onClick={() => toggleDayTypeActivity(actCode)}
                    >
                      <td className="py-2 px-3">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          disabled={!isSelected && dayTypeActivities.length >= 5}
                          readOnly
                          className="rounded"
                        />
                      </td>
                      <td className="py-2 px-3 text-gray-900">
                        {ACTIVITY_NAMES[actCode] || actCode}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Selected Activities - show comparison data */}
          {dayTypeActivities.length > 0 && (
            <div className="border border-gray-200 rounded-lg mt-4">
              <div className="px-4 py-3 bg-gradient-to-r from-red-100 to-rose-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-red-800">Weekday vs Weekend Comparison</p>
                  <p className="text-xs text-gray-600">{dayTypeActivities.length}/5 activities selected</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={dayTypeTimeRange.toString()}
                    onChange={(v) => {
                      setDayTypeTimeRange(Number(v));
                      setDayTypeTimelineData({}); // Clear cache to reload with new range
                    }}
                    options={timeRangeOptions}
                    className="w-40"
                  />
                  <ViewToggle view={dayTypeView} onViewChange={setDayTypeView} />
                  <button
                    onClick={() => setDayTypeActivities([])}
                    className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              <div className="p-4">
                {dayTypeLoading ? renderLoading() : (
                  dayTypeView === 'chart' ? (
                    <>
                      {/* Bar chart for current year comparison */}
                      <div className="h-60 mb-6">
                        <p className="text-xs text-gray-500 mb-2">Current Year Comparison</p>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={dayTypeActivities.map(actCode => ({
                              name: dayTypeActivityData[actCode]?.actcode_text?.substring(0, 20) || actCode,
                              ...Object.fromEntries(
                                dayTypeCodes.map(pertypeCode => [
                                  dayTypeLabels[pertypeCode] || pertypeCode,
                                  getDayTypeValue(actCode, pertypeCode)
                                ])
                              )
                            }))}
                            layout="vertical"
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis type="number" tick={{ fontSize: 10 }} />
                            <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 9 }} />
                            <Tooltip />
                            <Legend wrapperStyle={{ fontSize: '10px' }} />
                            {dayTypeCodes.map((pertypeCode, idx) => (
                              <Bar
                                key={pertypeCode}
                                dataKey={dayTypeLabels[pertypeCode] || pertypeCode}
                                name={dayTypeLabels[pertypeCode] || pertypeCode}
                                fill={CHART_COLORS[idx % CHART_COLORS.length]}
                              />
                            ))}
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Timeline chart showing historical trends */}
                      {combinedDayTypeChartData.length > 0 && (
                        <div className="h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Trends</p>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={combinedDayTypeChartData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="period_name" tick={{ fontSize: 10 }} />
                              <YAxis tick={{ fontSize: 10 }} />
                              <Tooltip />
                              <Legend wrapperStyle={{ fontSize: '10px' }} />
                              {Object.keys(combinedDayTypeChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key, idx) => (
                                <Line
                                  key={key}
                                  type="monotone"
                                  dataKey={key}
                                  name={key}
                                  stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                                  strokeWidth={2}
                                  dot={{ r: 2 }}
                                  connectNulls
                                />
                              ))}
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      {/* Table view - current year */}
                      <div className="overflow-x-auto max-h-64 mb-4">
                        <p className="text-xs text-gray-500 mb-2">Current Year Data</p>
                        <table className="w-full text-sm">
                          <thead className="sticky top-0 bg-gray-50">
                            <tr className="border-b border-gray-200">
                              <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Activity</th>
                              {dayTypeCodes.map((pertypeCode) => (
                                <th key={pertypeCode} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                  {dayTypeLabels[pertypeCode] || pertypeCode}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {dayTypeActivities.map((actCode) => (
                              <tr key={actCode} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-2 px-3 font-medium">
                                  {dayTypeActivityData[actCode]?.actcode_text?.substring(0, 30) || actCode}
                                </td>
                                {dayTypeCodes.map((pertypeCode) => (
                                  <td key={pertypeCode} className="py-2 px-3 text-right">
                                    {formatHours(getDayTypeValue(actCode, pertypeCode))}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      {/* Timeline table */}
                      {combinedDayTypeChartData.length > 0 && (
                        <div className="overflow-x-auto max-h-64">
                          <p className="text-xs text-gray-500 mb-2">Historical Data</p>
                          <table className="w-full text-sm">
                            <thead className="sticky top-0 bg-gray-50">
                              <tr className="border-b border-gray-200">
                                <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Year</th>
                                {Object.keys(combinedDayTypeChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key) => (
                                  <th key={key} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {combinedDayTypeChartData.slice().reverse().map((row) => (
                                <tr key={row.period_name} className="border-b border-gray-100 hover:bg-gray-50">
                                  <td className="py-2 px-3 font-medium">{row.period_name}</td>
                                  {Object.keys(combinedDayTypeChartData[0] || {}).filter(k => k !== 'year' && k !== 'period_name').map((key) => (
                                    <td key={key} className="py-2 px-3 text-right">
                                      {row[key] != null ? (row[key] as number).toFixed(2) : '-'}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </Card>
    );
  };

  // ============================================================================
  // SECTION 9: TOP ACTIVITIES
  // ============================================================================

  const renderTopActivities = (): ReactElement => (
    <Card className="mb-6">
      <SectionHeader title="9. Top Activities" color="green" icon={TrendingUp} />
      <div className="p-5">
        <div className="flex items-center gap-4 mb-4">
          <Select
            label="Ranking By"
            value={topRankingType}
            onChange={setTopRankingType}
            options={[
              { value: 'most_time', label: 'Most Time Spent' },
              { value: 'highest_participation', label: 'Highest Participation' }
            ]}
            className="w-48"
          />
        </div>

        {topLoading ? renderLoading() : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Rank</th>
                  <th className="px-4 py-2 text-left font-medium text-gray-600">Activity</th>
                  <th className="px-4 py-2 text-right font-medium text-gray-600">
                    {topRankingType === 'most_time' ? 'Avg Hours/Day' : 'Participation Rate'}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {topActivitiesData?.activities?.map((act) => (
                  <tr key={act.actcode_code} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-gray-900 font-medium">#{act.rank}</td>
                    <td className="px-4 py-2 text-gray-900">{act.actcode_text}</td>
                    <td className="px-4 py-2 text-right font-medium">
                      {topRankingType === 'most_time'
                        ? formatHours(act.avg_hours_per_day)
                        : formatPercent(act.participation_rate)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Card>
  );

  // ============================================================================
  // SECTION 10: YOY CHANGES
  // ============================================================================

  const renderYoYChanges = (): ReactElement => (
    <Card className="mb-6">
      <SectionHeader title="10. Year-over-Year Changes" color="cyan" icon={TrendingUp} />
      <div className="p-5">
        {yoyLoading ? renderLoading() : yoyData && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Gainers */}
            <div>
              <h3 className="text-sm font-semibold text-green-600 mb-3 flex items-center gap-2">
                <ArrowUpCircle className="w-4 h-4" />
                Biggest Increases ({yoyData.prev_year} to {yoyData.latest_year})
              </h3>
              <div className="space-y-2">
                {yoyData.gainers?.map((act) => (
                  <div key={act.actcode_code} className="flex items-center justify-between p-2 bg-green-50 rounded">
                    <span className="text-sm text-gray-900">{act.actcode_text.substring(0, 35)}</span>
                    <span className="text-sm font-medium text-green-600">{formatChange(act.change)} hrs</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Losers */}
            <div>
              <h3 className="text-sm font-semibold text-red-600 mb-3 flex items-center gap-2">
                <ArrowDownCircle className="w-4 h-4" />
                Biggest Decreases ({yoyData.prev_year} to {yoyData.latest_year})
              </h3>
              <div className="space-y-2">
                {yoyData.losers?.map((act) => (
                  <div key={act.actcode_code} className="flex items-center justify-between p-2 bg-red-50 rounded">
                    <span className="text-sm text-gray-900">{act.actcode_text.substring(0, 35)}</span>
                    <span className="text-sm font-medium text-red-600">{formatChange(act.change)} hrs</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );

  // ============================================================================
  // SECTION 11: SERIES EXPLORER
  // ============================================================================

  const renderSeriesExplorer = (): ReactElement => (
    <Card className="mb-6">
      <SectionHeader title="11. Series Explorer" color="blue" icon={Search} />
      <div className="p-5">
        {/* Method Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setExplorerMethod('search')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${
              explorerMethod === 'search' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Search className="w-4 h-4" />
            Search
          </button>
          <button
            onClick={() => setExplorerMethod('drilldown')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${
              explorerMethod === 'drilldown' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <GitBranch className="w-4 h-4" />
            Drill-down
          </button>
          <button
            onClick={() => setExplorerMethod('browse')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium ${
              explorerMethod === 'browse' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <List className="w-4 h-4" />
            Browse
          </button>
        </div>

        <p className="text-xs text-gray-500 mb-4">Click on rows to select series for comparison (max 5)</p>

        {/* Search Method */}
        {explorerMethod === 'search' && (
          <div>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleSearch()}
                placeholder="Search by activity name or series ID..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSearch}
                disabled={explorerLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {explorerLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Search'}
              </button>
            </div>

            {searchResults && (
              <div className="border border-gray-200 rounded-lg max-h-64 overflow-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-gray-50">
                    <tr className="border-b text-left text-xs font-semibold text-gray-600">
                      <th className="py-2 px-3 w-8"></th>
                      <th className="py-2 px-3">Series ID</th>
                      <th className="py-2 px-3">Activity</th>
                      <th className="py-2 px-3">Stat Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {searchResults.series?.slice(0, 20).map((s) => (
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
                        </td>
                        <td className="py-2 px-3">
                          <div className="text-xs">{s.actcode_text?.substring(0, 35)}</div>
                        </td>
                        <td className="py-2 px-3">
                          <div className="text-xs text-gray-500">{s.stattype_text?.substring(0, 25)}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Drill-down Method */}
        {explorerMethod === 'drilldown' && (
          <div>
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 mb-4 flex-wrap">
              <button
                onClick={() => setDrilldownPath([])}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Root
              </button>
              {drilldownPath.map((p, idx) => (
                <span key={idx} className="flex items-center gap-2">
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                  <button
                    onClick={() => setDrilldownPath(drilldownPath.slice(0, idx + 1))}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    {p.code}
                  </button>
                </span>
              ))}
            </div>

            {explorerLoading ? renderLoading() : drilldownData && (
              <div>
                <p className="text-sm text-gray-600 mb-3">{drilldownData.series_count} series at this level</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {drilldownData.children?.map((child) => (
                    <button
                      key={child.code}
                      onClick={() => {
                        if (child.has_children) {
                          setDrilldownPath([...drilldownPath, { dimension: child.dimension, code: child.code }]);
                        }
                      }}
                      className={`p-3 text-left rounded-lg border ${
                        child.has_children
                          ? 'border-blue-200 bg-blue-50 hover:bg-blue-100'
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <div className="text-sm font-medium text-gray-900">{child.name.substring(0, 40)}</div>
                      <div className="text-xs text-gray-500">{child.code} - {child.child_count} series</div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Browse Method */}
        {explorerMethod === 'browse' && (
          <div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {dimensions && (
                <>
                  <Select
                    label="Activity"
                    value={browseFilters.actcode_code || ''}
                    onChange={(v) => setBrowseFilters({ ...browseFilters, actcode_code: v })}
                    options={[
                      { value: '', label: 'All Activities' },
                      ...dimensions.activities.slice(0, 20).map(a => ({ value: a.actcode_code, label: a.actcode_text.substring(0, 30) }))
                    ]}
                  />
                  <Select
                    label="Stat Type"
                    value={browseFilters.stattype_code || ''}
                    onChange={(v) => setBrowseFilters({ ...browseFilters, stattype_code: v })}
                    options={[
                      { value: '', label: 'All Types' },
                      ...dimensions.stat_types.map(s => ({ value: s.stattype_code, label: s.stattype_text.substring(0, 30) }))
                    ]}
                  />
                  <Select
                    label="Sex"
                    value={browseFilters.sex_code || ''}
                    onChange={(v) => setBrowseFilters({ ...browseFilters, sex_code: v })}
                    options={[
                      { value: '', label: 'All' },
                      ...dimensions.sexes.map(s => ({ value: s.sex_code, label: s.sex_text }))
                    ]}
                  />
                  <Select
                    label="Age Group"
                    value={browseFilters.age_code || ''}
                    onChange={(v) => setBrowseFilters({ ...browseFilters, age_code: v })}
                    options={[
                      { value: '', label: 'All Ages' },
                      ...dimensions.ages.slice(0, 15).map(a => ({ value: a.age_code, label: a.age_text.substring(0, 20) }))
                    ]}
                  />
                </>
              )}
            </div>
            <button
              onClick={handleBrowse}
              disabled={explorerLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 mb-4"
            >
              {explorerLoading ? <Loader2 className="w-5 h-5 animate-spin inline" /> : 'Apply Filters'}
            </button>

            {browseResults && (
              <div className="border border-gray-200 rounded-lg max-h-64 overflow-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-gray-50">
                    <tr className="border-b text-left text-xs font-semibold text-gray-600">
                      <th className="py-2 px-3 w-8"></th>
                      <th className="py-2 px-3">Series ID</th>
                      <th className="py-2 px-3">Activity</th>
                      <th className="py-2 px-3">Demographics</th>
                    </tr>
                  </thead>
                  <tbody>
                    {browseResults.series?.slice(0, 20).map((s) => (
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
                        </td>
                        <td className="py-2 px-3">
                          <div className="text-xs">{s.actcode_text?.substring(0, 30)}</div>
                        </td>
                        <td className="py-2 px-3">
                          <div className="text-xs text-gray-500">
                            {[s.sex_text, s.age_text].filter(Boolean).join(', ').substring(0, 25)}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Selected Series Chart/Table */}
        {selectedSeries.length > 0 && (
          <div className="mt-6 border border-gray-200 rounded-lg">
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
                  onChange={(v) => {
                    setSeriesTimeRange(Number(v));
                    setSeriesChartData({}); // Clear cache to reload with new time range
                  }}
                  options={timeRangeOptions}
                  className="w-40"
                />
                <ViewToggle view={seriesView} onViewChange={setSeriesView} />
                <button
                  onClick={() => setSelectedSeries([])}
                  className="px-3 py-1 text-xs text-gray-600 border rounded hover:bg-gray-50"
                >
                  Clear All
                </button>
              </div>
            </div>
            <div className="p-4">
              {/* Selected series tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {selectedSeries.map((seriesId, idx) => {
                  const seriesInfo = seriesChartData[seriesId]?.series?.[0];
                  return (
                    <div
                      key={seriesId}
                      className="flex items-center gap-1 px-2 py-1 bg-gray-50 rounded border text-xs"
                      style={{ borderLeftColor: CHART_COLORS[idx % CHART_COLORS.length], borderLeftWidth: 3 }}
                    >
                      <span>{seriesInfo?.activity_name?.substring(0, 25) || seriesId}</span>
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
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '10px' }} />
                        {selectedSeries.map((seriesId, idx) => (
                          <Line
                            key={seriesId}
                            type="monotone"
                            dataKey={seriesId}
                            name={seriesChartData[seriesId]?.series?.[0]?.activity_name?.substring(0, 20) || seriesId}
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
                              {seriesChartData[seriesId]?.series?.[0]?.activity_name?.substring(0, 15) || seriesId}
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
                                {row[seriesId] != null ? (row[seriesId] as number).toFixed(2) : '-'}
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
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">American Time Use Survey (TU)</h1>
        <p className="text-gray-600 mt-1">
          Explore how Americans divide their time among activities. Data from BLS American Time Use Survey.
        </p>
      </div>

      {/* All Sections */}
      {renderOverview()}
      {renderActivityAnalysis()}
      {renderSexComparison()}
      {renderAgeComparison()}
      {renderLaborForce()}
      {renderEducation()}
      {renderRace()}
      {renderDayType()}
      {renderTopActivities()}
      {renderYoYChanges()}
      {renderSeriesExplorer()}
    </div>
  );
}
