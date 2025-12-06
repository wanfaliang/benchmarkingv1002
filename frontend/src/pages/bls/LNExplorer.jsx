import React, { useState, useEffect, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, X } from 'lucide-react';
import { lnResearchAPI } from '../../services/api';

/**
 * LN Explorer - Labor Force Statistics Explorer
 *
 * Sections:
 * 1. Overview - Headline Unemployment, LFPR, Emp-Pop Ratio with timeline
 * 2. Demographic Analysis - Unemployment by Age, Sex, Race, Education
 * 3. Occupation Analysis - Unemployment by occupation
 * 4. Industry Analysis - Unemployment by industry
 * 5. Series Detail Explorer - Search and chart specific series
 */

const formatRate = (value) => {
  if (value === undefined || value === null) return 'N/A';
  return `${value.toFixed(1)}%`;
};

const formatChange = (value) => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}pp`;
};

const formatPeriod = (periodCode) => {
  if (!periodCode) return '';
  const monthMap = {
    'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
    'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
    'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
  };
  return monthMap[periodCode] || periodCode;
};

const CHART_COLORS = [
  '#1976d2', '#2e7d32', '#d32f2f', '#f57c00', '#7b1fa2', '#0288d1',
  '#00796b', '#c2185b', '#512da8', '#0097a7', '#689f38', '#e64a19'
];

// Card component
function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm ${className}`}>
      {children}
    </div>
  );
}

// Section Header
function SectionHeader({ title, color = 'blue' }) {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-50 text-blue-700',
    purple: 'border-purple-500 bg-purple-50 text-purple-700',
    amber: 'border-amber-500 bg-amber-50 text-amber-700',
    green: 'border-green-500 bg-green-50 text-green-700',
    cyan: 'border-cyan-500 bg-cyan-50 text-cyan-700',
  };
  return (
    <div className={`px-5 py-3 border-b-2 ${colorClasses[color]}`}>
      <h2 className="text-lg font-bold">{title}</h2>
    </div>
  );
}

// Loading spinner
function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center py-12">
      <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );
}

// Select component
function Select({ label, value, onChange, options, className = '' }) {
  return (
    <div className={className}>
      {label && <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

// Timeline Selector component
function TimelineSelector({ timeline, selectedPeriod, onSelect, color = 'blue' }) {
  if (!timeline || timeline.length === 0) return null;

  const colorClasses = {
    blue: { active: 'bg-blue-600 border-blue-800', light: 'bg-blue-400', text: 'text-blue-600' },
    purple: { active: 'bg-purple-600 border-purple-800', light: 'bg-purple-400', text: 'text-purple-600' },
    amber: { active: 'bg-amber-600 border-amber-800', light: 'bg-amber-400', text: 'text-amber-600' },
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

// View Toggle component
function ViewToggle({ value, onChange }) {
  return (
    <div className="flex rounded-lg border border-gray-300 overflow-hidden">
      <button
        onClick={() => onChange('table')}
        className={`px-3 py-1.5 text-sm ${value === 'table' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
      >
        Table
      </button>
      <button
        onClick={() => onChange('chart')}
        className={`px-3 py-1.5 text-sm border-l ${value === 'chart' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
      >
        Chart
      </button>
    </div>
  );
}

// Metric Card for Overview
function MetricCard({ title, subtitle, value, mom, yoy, variant = 'red', showChanges = true }) {
  const variants = {
    red: 'bg-red-50 border-red-400',
    blue: 'bg-blue-50 border-blue-400',
    green: 'bg-green-50 border-green-400',
  };
  const textColors = {
    red: 'text-red-600',
    blue: 'text-blue-600',
    green: 'text-green-600',
  };

  return (
    <div className={`p-4 rounded-lg border-2 ${variants[variant]}`}>
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{title}</div>
      <div className="text-xs text-gray-500 mb-1">{subtitle}</div>
      <div className={`text-3xl font-bold ${textColors[variant]} my-2`}>
        {formatRate(value)}
      </div>
      {showChanges && (
        <div className="flex flex-wrap gap-2 mt-3">
          {mom !== undefined && mom !== null && (
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded-full ${mom >= 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
              {mom >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              M/M: {formatChange(mom)}
            </span>
          )}
          {yoy !== undefined && yoy !== null && (
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold rounded-full ${yoy >= 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
              {yoy >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              Y/Y: {formatChange(yoy)}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default function LNExplorer() {
  // Overview state
  const [overviewTimeRange, setOverviewTimeRange] = useState(24);
  const [selectedOverviewPeriod, setSelectedOverviewPeriod] = useState(null);
  const [overview, setOverview] = useState(null);
  const [overviewTimeline, setOverviewTimeline] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(true);

  // Demographic state
  const [demographicTimeRange, setDemographicTimeRange] = useState(24);
  const [selectedDemographicPeriod, setSelectedDemographicPeriod] = useState(null);
  const [demographics, setDemographics] = useState(null);
  const [demographicTimelines, setDemographicTimelines] = useState({});
  const [loadingDemographics, setLoadingDemographics] = useState(true);
  const [demographicView, setDemographicView] = useState('table');

  // Occupation state
  const [occupationTimeRange, setOccupationTimeRange] = useState(24);
  const [selectedOccupationPeriod, setSelectedOccupationPeriod] = useState(null);
  const [occupations, setOccupations] = useState(null);
  const [occupationTimeline, setOccupationTimeline] = useState(null);
  const [loadingOccupations, setLoadingOccupations] = useState(true);
  const [occupationView, setOccupationView] = useState('table');

  // Industry state
  const [industryTimeRange, setIndustryTimeRange] = useState(24);
  const [selectedIndustryPeriod, setSelectedIndustryPeriod] = useState(null);
  const [industries, setIndustries] = useState(null);
  const [industryTimeline, setIndustryTimeline] = useState(null);
  const [loadingIndustries, setLoadingIndustries] = useState(true);
  const [industryView, setIndustryView] = useState('table');

  // Series Explorer state
  const [dimensions, setDimensions] = useState(null);
  const [selectedLfstCode, setSelectedLfstCode] = useState('');
  const [selectedAgesCode, setSelectedAgesCode] = useState('');
  const [selectedSexsCode, setSelectedSexsCode] = useState('');
  const [selectedRaceCode, setSelectedRaceCode] = useState('');
  const [selectedSeasonal, setSelectedSeasonal] = useState('S');
  const [seriesList, setSeriesList] = useState(null);
  const [loadingSeries, setLoadingSeries] = useState(false);
  const [selectedSeries, setSelectedSeries] = useState([]);
  const [seriesChartData, setSeriesChartData] = useState({});
  const [seriesExplorerTimeRange, setSeriesExplorerTimeRange] = useState(60);
  const [seriesExplorerView, setSeriesExplorerView] = useState('chart');

  // Load overview data
  useEffect(() => {
    const loadOverview = async () => {
      setLoadingOverview(true);
      setSelectedOverviewPeriod(null);
      try {
        const [overviewRes, timelineRes] = await Promise.all([
          lnResearchAPI.getOverview(),
          lnResearchAPI.getOverviewTimeline(overviewTimeRange)
        ]);
        setOverview(overviewRes.data);
        setOverviewTimeline(timelineRes.data);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    loadOverview();
  }, [overviewTimeRange]);

  // Load demographic data
  useEffect(() => {
    const loadDemographics = async () => {
      setLoadingDemographics(true);
      setSelectedDemographicPeriod(null);
      try {
        const [demographicsRes, ageTimeline, sexTimeline, raceTimeline, educationTimeline] = await Promise.all([
          lnResearchAPI.getDemographicAnalysis(),
          lnResearchAPI.getDemographicTimeline('age', demographicTimeRange),
          lnResearchAPI.getDemographicTimeline('sex', demographicTimeRange),
          lnResearchAPI.getDemographicTimeline('race', demographicTimeRange),
          lnResearchAPI.getDemographicTimeline('education', demographicTimeRange),
        ]);
        setDemographics(demographicsRes.data);
        setDemographicTimelines({
          age: ageTimeline.data,
          sex: sexTimeline.data,
          race: raceTimeline.data,
          education: educationTimeline.data,
        });
      } catch (error) {
        console.error('Failed to load demographics:', error);
      } finally {
        setLoadingDemographics(false);
      }
    };
    loadDemographics();
  }, [demographicTimeRange]);

  // Load occupation data
  useEffect(() => {
    const loadOccupations = async () => {
      setLoadingOccupations(true);
      setSelectedOccupationPeriod(null);
      try {
        const [occupationsRes, timelineRes] = await Promise.all([
          lnResearchAPI.getOccupationAnalysis(),
          lnResearchAPI.getOccupationTimeline(occupationTimeRange)
        ]);
        setOccupations(occupationsRes.data);
        setOccupationTimeline(timelineRes.data);
      } catch (error) {
        console.error('Failed to load occupations:', error);
      } finally {
        setLoadingOccupations(false);
      }
    };
    loadOccupations();
  }, [occupationTimeRange]);

  // Load industry data
  useEffect(() => {
    const loadIndustries = async () => {
      setLoadingIndustries(true);
      setSelectedIndustryPeriod(null);
      try {
        const [industriesRes, timelineRes] = await Promise.all([
          lnResearchAPI.getIndustryAnalysis(),
          lnResearchAPI.getIndustryTimeline(industryTimeRange)
        ]);
        setIndustries(industriesRes.data);
        setIndustryTimeline(timelineRes.data);
      } catch (error) {
        console.error('Failed to load industries:', error);
      } finally {
        setLoadingIndustries(false);
      }
    };
    loadIndustries();
  }, [industryTimeRange]);

  // Load dimensions for series explorer
  useEffect(() => {
    if (!dimensions) {
      lnResearchAPI.getDimensions().then(res => setDimensions(res.data)).catch(console.error);
    }
  }, [dimensions]);

  // Load series list
  useEffect(() => {
    const loadSeries = async () => {
      setLoadingSeries(true);
      try {
        const params = { limit: 100, active_only: true };
        if (selectedLfstCode) params.lfst_code = selectedLfstCode;
        if (selectedAgesCode) params.ages_code = selectedAgesCode;
        if (selectedSexsCode) params.sexs_code = selectedSexsCode;
        if (selectedRaceCode) params.race_code = selectedRaceCode;
        if (selectedSeasonal) params.seasonal = selectedSeasonal;
        const response = await lnResearchAPI.getSeries(params);
        setSeriesList(response.data);
      } catch (error) {
        console.error('Failed to load series:', error);
      } finally {
        setLoadingSeries(false);
      }
    };
    loadSeries();
  }, [selectedLfstCode, selectedAgesCode, selectedSexsCode, selectedRaceCode, selectedSeasonal]);

  // Load chart data for selected series (reload when time range changes)
  useEffect(() => {
    const loadChartData = async () => {
      // Calculate start year based on time range
      const currentYear = new Date().getFullYear();
      const startYear = currentYear - Math.ceil(seriesExplorerTimeRange / 12);

      for (const seriesId of selectedSeries) {
        try {
          const response = await lnResearchAPI.getSeriesData(seriesId, { start_year: startYear });
          setSeriesChartData(prev => ({ ...prev, [seriesId]: response.data }));
        } catch (error) {
          console.error(`Failed to load data for ${seriesId}:`, error);
        }
      }
    };
    if (selectedSeries.length > 0) {
      loadChartData();
    }
  }, [selectedSeries, seriesExplorerTimeRange]);

  // Get overview data for selected period
  const overviewDisplayData = useMemo(() => {
    if (selectedOverviewPeriod && overviewTimeline?.timeline) {
      const point = overviewTimeline.timeline.find(
        p => p.year === selectedOverviewPeriod.year && p.period === selectedOverviewPeriod.period
      );
      if (point) {
        return {
          headline: { latest_value: point.headline_value, latest_date: point.period_name },
          lfpr: { latest_value: point.lfpr_value, latest_date: point.period_name },
          epop: { latest_value: point.epop_value, latest_date: point.period_name },
          showChanges: false,
        };
      }
    }
    return {
      headline: overview?.headline_unemployment,
      lfpr: overview?.labor_force_participation,
      epop: overview?.employment_population_ratio,
      showChanges: true,
    };
  }, [selectedOverviewPeriod, overviewTimeline, overview]);

  const timeRangeOptions = [
    { value: 12, label: 'Last 12 months' },
    { value: 24, label: 'Last 2 years' },
    { value: 60, label: 'Last 5 years' },
  ];

  // Main Dashboard View
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">LN - Labor Force Statistics Explorer</h1>
        <p className="text-sm text-gray-600 mt-1">Current Population Survey (CPS) - Unemployment & Labor Force Data</p>
      </div>

      {/* Section 1: Overview */}
      <Card>
        <SectionHeader title="Overview - Key Labor Market Indicators" color="blue" />
        <div className="p-5">
          <div className="flex gap-4 mb-5">
            <Select
              label="Time Range"
              value={overviewTimeRange}
              onChange={(v) => { setOverviewTimeRange(Number(v)); setSelectedOverviewPeriod(null); }}
              options={timeRangeOptions}
              className="w-48"
            />
          </div>

          {loadingOverview ? <LoadingSpinner /> : (
            <>
              {/* Timeline Chart */}
              {overviewTimeline?.timeline?.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Labor Market Rates Timeline</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={overviewTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis label={{ value: 'Rate (%)', angle: -90, position: 'insideLeft', fontSize: 11 }} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="headline_value" stroke="#dc2626" name="Unemployment" strokeWidth={2} dot={{ r: 2 }} />
                        <Line type="monotone" dataKey="lfpr_value" stroke="#0891b2" name="Labor Force Participation" strokeWidth={2} dot={{ r: 2 }} />
                        <Line type="monotone" dataKey="epop_value" stroke="#059669" name="Employment-Pop Ratio" strokeWidth={2} dot={{ r: 2 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <TimelineSelector
                    timeline={overviewTimeline.timeline}
                    selectedPeriod={selectedOverviewPeriod}
                    onSelect={setSelectedOverviewPeriod}
                    color="blue"
                  />
                </div>
              )}

              {/* Metric Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard
                  title="Unemployment Rate"
                  subtitle={overviewDisplayData.headline?.latest_date || ''}
                  value={overviewDisplayData.headline?.latest_value}
                  mom={overviewDisplayData.headline?.month_over_month}
                  yoy={overviewDisplayData.headline?.year_over_year}
                  variant="red"
                  showChanges={overviewDisplayData.showChanges}
                />
                <MetricCard
                  title="Labor Force Participation"
                  subtitle={overviewDisplayData.lfpr?.latest_date || ''}
                  value={overviewDisplayData.lfpr?.latest_value}
                  mom={overviewDisplayData.lfpr?.month_over_month}
                  yoy={overviewDisplayData.lfpr?.year_over_year}
                  variant="blue"
                  showChanges={overviewDisplayData.showChanges}
                />
                <MetricCard
                  title="Employment-Pop Ratio"
                  subtitle={overviewDisplayData.epop?.latest_date || ''}
                  value={overviewDisplayData.epop?.latest_value}
                  mom={overviewDisplayData.epop?.month_over_month}
                  yoy={overviewDisplayData.epop?.year_over_year}
                  variant="green"
                  showChanges={overviewDisplayData.showChanges}
                />
              </div>
            </>
          )}
        </div>
      </Card>

      {/* Section 2: Demographic Analysis */}
      <Card>
        <SectionHeader title="Demographic Analysis - Unemployment by Group" color="purple" />
        <div className="p-5">
          <div className="flex gap-4 mb-5 justify-between">
            <Select
              label="Time Range"
              value={demographicTimeRange}
              onChange={(v) => { setDemographicTimeRange(Number(v)); setSelectedDemographicPeriod(null); }}
              options={timeRangeOptions}
              className="w-48"
            />
            <ViewToggle value={demographicView} onChange={setDemographicView} />
          </div>

          {loadingDemographics ? <LoadingSpinner /> : demographics?.breakdowns?.map((breakdown, idx) => {
            const timelineData = demographicTimelines[breakdown.dimension_type];
            const selectedTimelinePoint = selectedDemographicPeriod && timelineData
              ? timelineData.timeline?.find(p => p.year === selectedDemographicPeriod.year && p.period === selectedDemographicPeriod.period)
              : timelineData?.timeline?.[timelineData.timeline.length - 1];
            const displayMetrics = selectedTimelinePoint?.metrics || breakdown.metrics;
            const displayDate = selectedTimelinePoint ? selectedTimelinePoint.period_name : null;

            return (
              <div key={idx} className="mb-8">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">{breakdown.dimension_name}</h3>

                {/* Timeline Chart */}
                {timelineData?.timeline?.length > 0 && (
                  <div className="mb-4">
                    <div className="h-56">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={timelineData.timeline}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={70} />
                          <YAxis label={{ value: 'Unemployment Rate (%)', angle: -90, position: 'insideLeft', fontSize: 10 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '10px' }} />
                          {breakdown.metrics.map((metric, i) => (
                            <Line
                              key={metric.dimension_name}
                              type="monotone"
                              dataKey={(dp) => dp.metrics?.find(m => m.dimension_name === metric.dimension_name)?.latest_value}
                              stroke={CHART_COLORS[i % CHART_COLORS.length]}
                              strokeWidth={2}
                              name={metric.dimension_name}
                              dot={{ r: 2 }}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <TimelineSelector
                      timeline={timelineData.timeline}
                      selectedPeriod={selectedDemographicPeriod}
                      onSelect={setSelectedDemographicPeriod}
                      color="purple"
                    />
                  </div>
                )}

                {displayDate && <p className="text-xs text-gray-500 mb-2">Showing data for: {displayDate}</p>}

                {demographicView === 'table' ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-2 px-3 font-semibold">Group</th>
                          <th className="text-right py-2 px-3 font-semibold">Unemployment Rate</th>
                          {!selectedDemographicPeriod && (
                            <>
                              <th className="text-right py-2 px-3 font-semibold">M/M Change</th>
                              <th className="text-right py-2 px-3 font-semibold">Y/Y Change</th>
                            </>
                          )}
                        </tr>
                      </thead>
                      <tbody>
                        {displayMetrics.map((metric, i) => (
                          <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-2 px-3">{metric.dimension_name}</td>
                            <td className="text-right py-2 px-3 font-semibold text-red-600">{formatRate(metric.latest_value)}</td>
                            {!selectedDemographicPeriod && (
                              <>
                                <td className="text-right py-2 px-3">
                                  {metric.month_over_month !== undefined && metric.month_over_month !== null && (
                                    <span className={`inline-flex items-center gap-1 font-medium ${metric.month_over_month >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                                      {metric.month_over_month >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                      {formatChange(metric.month_over_month)}
                                    </span>
                                  )}
                                </td>
                                <td className="text-right py-2 px-3">
                                  {metric.year_over_year !== undefined && metric.year_over_year !== null && (
                                    <span className={`inline-flex items-center gap-1 font-medium ${metric.year_over_year >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                                      {metric.year_over_year >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                      {formatChange(metric.year_over_year)}
                                    </span>
                                  )}
                                </td>
                              </>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={displayMetrics.map(m => ({ name: m.dimension_name, rate: m.latest_value || 0 }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={100} />
                        <YAxis label={{ value: 'Unemployment Rate (%)', angle: -90, position: 'insideLeft', fontSize: 10 }} />
                        <Tooltip />
                        <Bar dataKey="rate">
                          {displayMetrics.map((_, i) => <Cell key={`cell-${i}`} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Section 3: Occupation Analysis */}
      <Card>
        <SectionHeader title="Occupation Analysis - Unemployment by Occupation" color="amber" />
        <div className="p-5">
          <div className="flex gap-4 mb-5 justify-between">
            <Select
              label="Time Range"
              value={occupationTimeRange}
              onChange={(v) => { setOccupationTimeRange(Number(v)); setSelectedOccupationPeriod(null); }}
              options={timeRangeOptions}
              className="w-48"
            />
            <ViewToggle value={occupationView} onChange={setOccupationView} />
          </div>

          {loadingOccupations ? <LoadingSpinner /> : (
            <>
              {occupationTimeline?.timeline?.length > 0 && (
                <div className="mb-4">
                  <div className="h-56">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={occupationTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis label={{ value: 'Unemployment Rate (%)', angle: -90, position: 'insideLeft', fontSize: 10 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '9px' }} />
                        {occupations?.occupations?.map((metric, i) => (
                          <Line
                            key={metric.dimension_name}
                            type="monotone"
                            dataKey={(dp) => dp.metrics?.find(m => m.dimension_name === metric.dimension_name)?.latest_value}
                            stroke={CHART_COLORS[i % CHART_COLORS.length]}
                            strokeWidth={2}
                            name={metric.dimension_name}
                            dot={{ r: 2 }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <TimelineSelector
                    timeline={occupationTimeline.timeline}
                    selectedPeriod={selectedOccupationPeriod}
                    onSelect={setSelectedOccupationPeriod}
                    color="amber"
                  />
                </div>
              )}

              {(() => {
                const selectedTimelinePoint = selectedOccupationPeriod && occupationTimeline
                  ? occupationTimeline.timeline?.find(p => p.year === selectedOccupationPeriod.year && p.period === selectedOccupationPeriod.period)
                  : occupationTimeline?.timeline?.[occupationTimeline.timeline.length - 1];
                const displayMetrics = selectedTimelinePoint?.metrics || occupations?.occupations || [];
                const displayDate = selectedTimelinePoint ? selectedTimelinePoint.period_name : null;

                return (
                  <>
                    {displayDate && <p className="text-xs text-gray-500 mb-2">Showing data for: {displayDate}</p>}
                    {occupationView === 'table' ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-2 px-3 font-semibold">Occupation</th>
                              <th className="text-right py-2 px-3 font-semibold">Unemployment Rate</th>
                              {!selectedOccupationPeriod && (
                                <>
                                  <th className="text-right py-2 px-3 font-semibold">M/M Change</th>
                                  <th className="text-right py-2 px-3 font-semibold">Y/Y Change</th>
                                </>
                              )}
                            </tr>
                          </thead>
                          <tbody>
                            {displayMetrics.map((metric, i) => (
                              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-2 px-3">{metric.dimension_name}</td>
                                <td className="text-right py-2 px-3 font-semibold text-red-600">{formatRate(metric.latest_value)}</td>
                                {!selectedOccupationPeriod && (
                                  <>
                                    <td className="text-right py-2 px-3">
                                      {metric.month_over_month !== undefined && metric.month_over_month !== null && (
                                        <span className={`inline-flex items-center gap-1 font-medium ${metric.month_over_month >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                                          {metric.month_over_month >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                          {formatChange(metric.month_over_month)}
                                        </span>
                                      )}
                                    </td>
                                    <td className="text-right py-2 px-3">
                                      {metric.year_over_year !== undefined && metric.year_over_year !== null && (
                                        <span className={`inline-flex items-center gap-1 font-medium ${metric.year_over_year >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                                          {metric.year_over_year >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                          {formatChange(metric.year_over_year)}
                                        </span>
                                      )}
                                    </td>
                                  </>
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={displayMetrics.map(m => ({ name: m.dimension_name, rate: m.latest_value || 0 }))}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={120} />
                            <YAxis label={{ value: 'Unemployment Rate (%)', angle: -90, position: 'insideLeft', fontSize: 10 }} />
                            <Tooltip />
                            <Bar dataKey="rate">
                              {displayMetrics.map((_, i) => <Cell key={`cell-${i}`} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                  </>
                );
              })()}
            </>
          )}
        </div>
      </Card>

      {/* Section 4: Industry Analysis */}
      <Card>
        <SectionHeader title="Industry Analysis - Unemployment by Industry" color="green" />
        <div className="p-5">
          <div className="flex gap-4 mb-5 justify-between">
            <Select
              label="Time Range"
              value={industryTimeRange}
              onChange={(v) => { setIndustryTimeRange(Number(v)); setSelectedIndustryPeriod(null); }}
              options={timeRangeOptions}
              className="w-48"
            />
            <ViewToggle value={industryView} onChange={setIndustryView} />
          </div>

          {loadingIndustries ? <LoadingSpinner /> : (
            <>
              {industryTimeline?.timeline?.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">Historical Trend (Top 5 Industries)</h4>
                  <div className="h-56">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={industryTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 9 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis label={{ value: 'Unemployment Rate (%)', angle: -90, position: 'insideLeft', fontSize: 10 }} />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '9px' }} />
                        {industries?.industries?.slice(0, 5).map((metric, i) => (
                          <Line
                            key={metric.dimension_name}
                            type="monotone"
                            dataKey={(dp) => dp.metrics?.find(m => m.dimension_name === metric.dimension_name)?.latest_value}
                            stroke={CHART_COLORS[i % CHART_COLORS.length]}
                            strokeWidth={2}
                            name={metric.dimension_name}
                            dot={{ r: 2 }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <TimelineSelector
                    timeline={industryTimeline.timeline}
                    selectedPeriod={selectedIndustryPeriod}
                    onSelect={setSelectedIndustryPeriod}
                    color="green"
                  />
                </div>
              )}

              {(() => {
                const selectedTimelinePoint = selectedIndustryPeriod && industryTimeline
                  ? industryTimeline.timeline?.find(p => p.year === selectedIndustryPeriod.year && p.period === selectedIndustryPeriod.period)
                  : industryTimeline?.timeline?.[industryTimeline.timeline.length - 1];
                const displayMetrics = selectedTimelinePoint?.metrics || industries?.industries || [];
                const displayDate = selectedTimelinePoint ? selectedTimelinePoint.period_name : null;

                return (
                  <>
                    {displayDate && <p className="text-xs text-gray-500 mb-2">Showing data for: {displayDate}</p>}
                    {industryView === 'table' ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-2 px-3 font-semibold">Industry</th>
                              <th className="text-right py-2 px-3 font-semibold">Unemployment Rate</th>
                              {!selectedIndustryPeriod && (
                                <>
                                  <th className="text-right py-2 px-3 font-semibold">M/M Change</th>
                                  <th className="text-right py-2 px-3 font-semibold">Y/Y Change</th>
                                </>
                              )}
                            </tr>
                          </thead>
                          <tbody>
                            {displayMetrics.map((metric, i) => (
                              <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-2 px-3">{metric.dimension_name}</td>
                                <td className="text-right py-2 px-3 font-semibold text-red-600">{formatRate(metric.latest_value)}</td>
                                {!selectedIndustryPeriod && (
                                  <>
                                    <td className="text-right py-2 px-3">
                                      {metric.month_over_month !== undefined && metric.month_over_month !== null && (
                                        <span className={`inline-flex items-center gap-1 font-medium ${metric.month_over_month >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                                          {metric.month_over_month >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                          {formatChange(metric.month_over_month)}
                                        </span>
                                      )}
                                    </td>
                                    <td className="text-right py-2 px-3">
                                      {metric.year_over_year !== undefined && metric.year_over_year !== null && (
                                        <span className={`inline-flex items-center gap-1 font-medium ${metric.year_over_year >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                                          {metric.year_over_year >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                          {formatChange(metric.year_over_year)}
                                        </span>
                                      )}
                                    </td>
                                  </>
                                )}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={displayMetrics.map(m => ({ name: m.dimension_name, rate: m.latest_value || 0 }))}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" tick={{ fontSize: 8 }} angle={-45} textAnchor="end" height={150} />
                            <YAxis label={{ value: 'Unemployment Rate (%)', angle: -90, position: 'insideLeft', fontSize: 10 }} />
                            <Tooltip />
                            <Bar dataKey="rate" fill="#1976d2" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                  </>
                );
              })()}
            </>
          )}
        </div>
      </Card>

      {/* Section 5: Series Detail Explorer */}
      <Card>
        <SectionHeader title="Series Detail Explorer" color="cyan" />
        <div className="p-5">
          {/* Filters */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Filter Series</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <Select
                label="Labor Force Status"
                value={selectedLfstCode}
                onChange={setSelectedLfstCode}
                options={[
                  { value: '', label: 'All' },
                  ...(dimensions?.labor_force_statuses?.map(d => ({ value: d.code, label: d.text })) || [])
                ]}
              />
              <Select
                label="Age"
                value={selectedAgesCode}
                onChange={setSelectedAgesCode}
                options={[
                  { value: '', label: 'All' },
                  ...(dimensions?.ages?.map(d => ({ value: d.code, label: d.text })) || [])
                ]}
              />
              <Select
                label="Sex"
                value={selectedSexsCode}
                onChange={setSelectedSexsCode}
                options={[
                  { value: '', label: 'All' },
                  ...(dimensions?.sexes?.map(d => ({ value: d.code, label: d.text })) || [])
                ]}
              />
              <Select
                label="Race"
                value={selectedRaceCode}
                onChange={setSelectedRaceCode}
                options={[
                  { value: '', label: 'All' },
                  ...(dimensions?.races?.map(d => ({ value: d.code, label: d.text })) || [])
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
          </div>

          {/* Series List */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Available Series ({seriesList?.total || 0}) - Click to add to chart
            </h3>
            <div className="overflow-x-auto max-h-[600px] border border-gray-200 rounded-lg">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-50">
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-3 font-semibold">Series ID</th>
                    <th className="text-left py-2 px-3 font-semibold">Title</th>
                    <th className="text-left py-2 px-3 font-semibold">Seasonal</th>
                    <th className="text-center py-2 px-3 font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {loadingSeries ? (
                    <tr><td colSpan={4} className="py-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-500" /></td></tr>
                  ) : seriesList?.series?.map(series => (
                    <tr
                      key={series.series_id}
                      className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${selectedSeries.includes(series.series_id) ? 'bg-cyan-50' : ''}`}
                      onClick={() => !selectedSeries.includes(series.series_id) && setSelectedSeries([...selectedSeries, series.series_id])}
                    >
                      <td className="py-2 px-3 font-mono text-xs">{series.series_id}</td>
                      <td className="py-2 px-3 text-xs">{series.series_title}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 text-[10px] rounded ${series.seasonal === 'S' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`}>
                          {series.seasonal === 'S' ? 'SA' : 'NSA'}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-center">
                        <span className={`px-3 py-1 text-xs rounded ${selectedSeries.includes(series.series_id) ? 'bg-cyan-200 text-cyan-700' : 'bg-blue-100 text-blue-700'}`}>
                          {selectedSeries.includes(series.series_id) ? 'Selected' : 'Add'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Selected Series Visualization */}
          {selectedSeries.length > 0 && (
            <div>
              {/* Controls: Time Range, View Toggle, Selected Series */}
              <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                <div className="flex items-center gap-4">
                  <Select
                    label="Time Range"
                    value={seriesExplorerTimeRange}
                    onChange={(v) => setSeriesExplorerTimeRange(Number(v))}
                    options={[
                      { value: 12, label: 'Last 12 months' },
                      { value: 24, label: 'Last 2 years' },
                      { value: 60, label: 'Last 5 years' },
                      { value: 120, label: 'Last 10 years' },
                    ]}
                    className="w-40"
                  />
                  <ViewToggle value={seriesExplorerView} onChange={setSeriesExplorerView} />
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedSeries.map((seriesId, idx) => (
                    <span
                      key={seriesId}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs"
                      style={{ backgroundColor: `${CHART_COLORS[idx % CHART_COLORS.length]}20`, color: CHART_COLORS[idx % CHART_COLORS.length] }}
                    >
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                      {seriesId}
                      <button
                        onClick={() => setSelectedSeries(selectedSeries.filter(s => s !== seriesId))}
                        className="ml-1 hover:opacity-70"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                  {selectedSeries.length > 1 && (
                    <button
                      onClick={() => setSelectedSeries([])}
                      className="px-2 py-1 text-xs text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                    >
                      Clear All
                    </button>
                  )}
                </div>
              </div>

              {/* Chart View - Single combined chart */}
              {seriesExplorerView === 'chart' && (() => {
                // Build combined chart data
                const allDataLoaded = selectedSeries.every(id => seriesChartData[id]);
                if (!allDataLoaded) {
                  return <div className="py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto text-cyan-500" /></div>;
                }

                // Get all unique periods across all series
                const allPeriods = new Map();
                selectedSeries.forEach(seriesId => {
                  const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                  data.forEach(dp => {
                    const key = `${dp.year}-${dp.period}`;
                    if (!allPeriods.has(key)) {
                      allPeriods.set(key, {
                        period_name: `${formatPeriod(dp.period)} ${dp.year}`,
                        year: dp.year,
                        period: dp.period,
                      });
                    }
                  });
                });

                // Sort periods chronologically
                const sortedPeriods = Array.from(allPeriods.values())
                  .sort((a, b) => a.year - b.year || a.period.localeCompare(b.period));

                // Build chart data with all series values
                const combinedChartData = sortedPeriods.map(p => {
                  const row = { period_name: p.period_name };
                  selectedSeries.forEach(seriesId => {
                    const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                    const dp = data.find(d => d.year === p.year && d.period === p.period);
                    row[seriesId] = dp?.value ?? null;
                  });
                  return row;
                });

                return (
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="period_name"
                          tick={{ fontSize: 10 }}
                          angle={-45}
                          textAnchor="end"
                          height={70}
                          interval={Math.max(0, Math.floor(combinedChartData.length / 12) - 1)}
                        />
                        <YAxis />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {selectedSeries.map((seriesId, idx) => {
                          const seriesTitle = seriesChartData[seriesId]?.series?.[0]?.series_title || seriesId;
                          // Truncate long titles for legend
                          const shortTitle = seriesTitle.length > 40 ? seriesTitle.substring(0, 40) + '...' : seriesTitle;
                          return (
                            <Line
                              key={seriesId}
                              type="monotone"
                              dataKey={seriesId}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={false}
                              name={shortTitle}
                              connectNulls
                            />
                          );
                        })}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                );
              })()}

              {/* Table View - 2D table with periods as rows, series as columns */}
              {seriesExplorerView === 'table' && (() => {
                const allDataLoaded = selectedSeries.every(id => seriesChartData[id]);
                if (!allDataLoaded) {
                  return <div className="py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto text-cyan-500" /></div>;
                }

                // Get all unique periods across all series
                const allPeriods = new Map();
                selectedSeries.forEach(seriesId => {
                  const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                  data.forEach(dp => {
                    const key = `${dp.year}-${dp.period}`;
                    if (!allPeriods.has(key)) {
                      allPeriods.set(key, {
                        period_name: `${formatPeriod(dp.period)} ${dp.year}`,
                        year: dp.year,
                        period: dp.period,
                      });
                    }
                  });
                });

                // Sort periods chronologically (most recent first for table)
                const sortedPeriods = Array.from(allPeriods.values())
                  .sort((a, b) => b.year - a.year || b.period.localeCompare(a.period));

                // Build lookup for values
                const valueMap = {};
                selectedSeries.forEach(seriesId => {
                  valueMap[seriesId] = {};
                  const data = seriesChartData[seriesId]?.series?.[0]?.data_points || [];
                  data.forEach(dp => {
                    valueMap[seriesId][`${dp.year}-${dp.period}`] = dp.value;
                  });
                });

                return (
                  <div className="overflow-x-auto max-h-[500px] border border-gray-200 rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-2 px-3 font-semibold sticky left-0 bg-gray-50 z-10">Period</th>
                          {selectedSeries.map((seriesId, idx) => {
                            const seriesTitle = seriesChartData[seriesId]?.series?.[0]?.series_title || seriesId;
                            return (
                              <th
                                key={seriesId}
                                className="text-right py-2 px-3 font-semibold min-w-[120px]"
                                style={{ color: CHART_COLORS[idx % CHART_COLORS.length] }}
                                title={seriesTitle}
                              >
                                {seriesId}
                              </th>
                            );
                          })}
                        </tr>
                      </thead>
                      <tbody>
                        {sortedPeriods.map((p, rowIdx) => (
                          <tr key={`${p.year}-${p.period}`} className={`border-b border-gray-100 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                            <td className="py-2 px-3 font-medium sticky left-0 bg-inherit">{p.period_name}</td>
                            {selectedSeries.map(seriesId => {
                              const value = valueMap[seriesId][`${p.year}-${p.period}`];
                              return (
                                <td key={seriesId} className="text-right py-2 px-3 font-mono">
                                  {value !== undefined && value !== null ? value.toFixed(1) : '-'}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                );
              })()}
            </div>
          )}
        </div>
      </Card>

      {/* Info box */}
      <Card className="bg-blue-50 border-blue-200">
        <div className="p-4">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> All data is seasonally adjusted unless otherwise noted.
            Unemployment rate = (Unemployed / Labor Force) × 100.
            Labor Force Participation Rate = (Labor Force / Civilian Population) × 100.
            Click on timeline points to view data for specific months. M/M and Y/Y changes are only available for the latest period.
          </p>
        </div>
      </Card>
    </div>
  );
}
