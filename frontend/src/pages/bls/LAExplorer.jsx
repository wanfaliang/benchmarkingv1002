import { useState, useEffect, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, X } from 'lucide-react';
import { MapContainer, TileLayer, CircleMarker, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { laResearchAPI, lnResearchAPI } from '../../services/api';
import { getLAAreaCoordinates, US_BOUNDS } from '../../utils/laAreaCoordinates';

/**
 * LA Explorer - Local Area Unemployment Statistics Explorer
 *
 * Sections:
 * 1. National Overview - Aggregated from state data
 * 2. Geographic View - Interactive map
 * 3. State Analysis - All states with rankings
 * 4. Metropolitan Areas - Metro area data
 * 5. Series Detail Explorer - Advanced queries
 */

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'];

// Reusable Components
const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
    {children}
  </div>
);

const SectionHeader = ({ title, color = 'blue' }) => {
  const colorClasses = {
    red: 'border-red-500 bg-red-50 text-red-700',
    orange: 'border-orange-500 bg-orange-50 text-orange-700',
    blue: 'border-blue-500 bg-blue-50 text-blue-700',
    green: 'border-green-500 bg-green-50 text-green-700',
    cyan: 'border-cyan-500 bg-cyan-50 text-cyan-700',
  };
  return (
    <div className={`px-5 py-3 border-b-4 ${colorClasses[color]}`}>
      <h2 className="text-xl font-bold">{title}</h2>
    </div>
  );
};

const Select = ({ label, value, onChange, options, className = '' }) => (
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

const ViewToggle = ({ value, onChange }) => (
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

const TimelineSelector = ({ timeline, selectedPeriod, onSelectPeriod }) => (
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

// Helper functions
const formatRate = (val) => (val != null ? `${val.toFixed(1)}%` : 'N/A');
const formatNumber = (val) => (val != null ? val.toLocaleString(undefined, { maximumFractionDigits: 0 }) : 'N/A');
const formatChange = (val) => {
  if (val == null) return 'N/A';
  const sign = val >= 0 ? '+' : '';
  return `${sign}${val.toFixed(1)}pp`;
};
const formatPeriod = (period) => {
  const monthMap = {
    'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
    'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
    'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
  };
  return monthMap[period] || period;
};

const getColorFromRate = (rate) => {
  if (rate < 3) return '#16a34a';
  if (rate < 4) return '#4ade80';
  if (rate < 5) return '#fbbf24';
  if (rate < 6) return '#fb923c';
  if (rate < 7) return '#f87171';
  return '#dc2626';
};

export default function LAExplorer() {
  // Overview state
  const [overview, setOverview] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeRange, setOverviewTimeRange] = useState(24);
  const [overviewTimeline, setOverviewTimeline] = useState(null);
  const [selectedOverviewPeriod, setSelectedOverviewPeriod] = useState(null);

  // State analysis
  const [states, setStates] = useState(null);
  const [stateTimeline, setStateTimeline] = useState(null);
  const [loadingStates, setLoadingStates] = useState(true);
  const [stateTimeRange, setStateTimeRange] = useState(24);
  const [selectedStatePeriod, setSelectedStatePeriod] = useState(null);
  const [stateView, setStateView] = useState('table');
  const [selectedStatesForTimeline, setSelectedStatesForTimeline] = useState([]);

  // Metro analysis
  const [metros, setMetros] = useState(null);
  const [metroTimeline, setMetroTimeline] = useState(null);
  const [loadingMetros, setLoadingMetros] = useState(true);
  const [metroTimeRange, setMetroTimeRange] = useState(24);
  const [selectedMetroPeriod, setSelectedMetroPeriod] = useState(null);
  const [metroView, setMetroView] = useState('table');
  const [selectedMetrosForTimeline, setSelectedMetrosForTimeline] = useState([]);
  const [metroPage, setMetroPage] = useState(0);

  // Geographic view
  const [geoTimeRange, setGeoTimeRange] = useState(24);
  const [selectedGeoPeriod, setSelectedGeoPeriod] = useState(null);
  const [geoTimeline, setGeoTimeline] = useState(null);
  const [geoMetroTimeline, setGeoMetroTimeline] = useState(null);
  const [geoOverviewTimeline, setGeoOverviewTimeline] = useState(null);
  const [loadingGeo, setLoadingGeo] = useState(false);

  // National timeline (from LN survey for comparison)
  const [nationalTimeline, setNationalTimeline] = useState(null);

  // Series explorer
  const [dimensions, setDimensions] = useState(null);
  const [selectedArea, setSelectedArea] = useState('');
  const [selectedMeasure, setSelectedMeasure] = useState('');
  const [selectedSeasonal, setSelectedSeasonal] = useState('');
  const [seriesList, setSeriesList] = useState(null);
  const [loadingSeries, setLoadingSeries] = useState(false);
  const [selectedSeriesIds, setSelectedSeriesIds] = useState([]);
  const [seriesChartData, setSeriesChartData] = useState({});
  const [seriesTimeRange, setSeriesTimeRange] = useState(60);
  const [seriesView, setSeriesView] = useState('chart');

  // Load overview
  useEffect(() => {
    const load = async () => {
      setLoadingOverview(true);
      try {
        const [overviewRes, timelineRes] = await Promise.all([
          laResearchAPI.getOverview(),
          laResearchAPI.getOverviewTimeline(overviewTimeRange)
        ]);
        setOverview(overviewRes.data);
        setOverviewTimeline(timelineRes.data);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
  }, [overviewTimeRange]);

  // Load states
  useEffect(() => {
    const load = async () => {
      setLoadingStates(true);
      try {
        const [statesRes, timelineRes] = await Promise.all([
          laResearchAPI.getStates(),
          laResearchAPI.getStatesTimeline(stateTimeRange)
        ]);
        setStates(statesRes.data);
        setStateTimeline(timelineRes.data);
      } catch (error) {
        console.error('Failed to load states:', error);
      } finally {
        setLoadingStates(false);
      }
    };
    load();
  }, [stateTimeRange]);

  // Load geographic view timeline (separate from state analysis)
  useEffect(() => {
    const load = async () => {
      setLoadingGeo(true);
      setSelectedGeoPeriod(null); // Reset selected period when time range changes
      try {
        const [stateTimelineRes, metroTimelineRes, overviewTimelineRes] = await Promise.all([
          laResearchAPI.getStatesTimeline(geoTimeRange),
          laResearchAPI.getMetrosTimeline(geoTimeRange, null, 500),
          laResearchAPI.getOverviewTimeline(geoTimeRange)
        ]);
        setGeoTimeline(stateTimelineRes.data);
        setGeoMetroTimeline(metroTimelineRes.data);
        setGeoOverviewTimeline(overviewTimelineRes.data);
      } catch (error) {
        console.error('Failed to load geo timeline:', error);
      } finally {
        setLoadingGeo(false);
      }
    };
    load();
  }, [geoTimeRange]);

  // Load metros
  useEffect(() => {
    const load = async () => {
      setLoadingMetros(true);
      try {
        const [metrosRes, timelineRes] = await Promise.all([
          laResearchAPI.getMetros(500),
          laResearchAPI.getMetrosTimeline(metroTimeRange, null, 50)
        ]);
        setMetros(metrosRes.data);
        setMetroTimeline(timelineRes.data);
      } catch (error) {
        console.error('Failed to load metros:', error);
      } finally {
        setLoadingMetros(false);
      }
    };
    load();
  }, [metroTimeRange]);

  // Load national timeline from LN survey
  useEffect(() => {
    const load = async () => {
      try {
        const res = await lnResearchAPI.getOverviewTimeline(Math.max(stateTimeRange, metroTimeRange));
        setNationalTimeline(res.data);
      } catch (error) {
        console.error('Failed to load national timeline:', error);
      }
    };
    load();
  }, [stateTimeRange, metroTimeRange]);

  // Load dimensions for series explorer
  useEffect(() => {
    laResearchAPI.getDimensions().then(res => setDimensions(res.data)).catch(console.error);
  }, []);

  // Load series list
  useEffect(() => {
    const load = async () => {
      setLoadingSeries(true);
      try {
        const params = { limit: 100, active_only: true };
        if (selectedArea) params.area_code = selectedArea;
        if (selectedMeasure) params.measure_code = selectedMeasure;
        if (selectedSeasonal) params.seasonal_code = selectedSeasonal;
        const res = await laResearchAPI.getSeries(params);
        setSeriesList(res.data);
      } catch (error) {
        console.error('Failed to load series:', error);
      } finally {
        setLoadingSeries(false);
      }
    };
    load();
  }, [selectedArea, selectedMeasure, selectedSeasonal]);

  // Load series data
  useEffect(() => {
    const load = async () => {
      const currentYear = new Date().getFullYear();
      const startYear = currentYear - Math.ceil(seriesTimeRange / 12);
      for (const seriesId of selectedSeriesIds) {
        try {
          const res = await laResearchAPI.getSeriesData(seriesId, { start_year: startYear });
          setSeriesChartData(prev => ({ ...prev, [seriesId]: res.data }));
        } catch (error) {
          console.error(`Failed to load ${seriesId}:`, error);
        }
      }
    };
    if (selectedSeriesIds.length > 0) load();
  }, [selectedSeriesIds, seriesTimeRange]);

  const timeRangeOptions = [
    { value: 12, label: 'Last 12 months' },
    { value: 24, label: 'Last 2 years' },
    { value: 60, label: 'Last 5 years' },
    { value: 120, label: 'Last 10 years' },
    { value: 9999, label: 'All Time' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">LA - Local Area Unemployment Statistics Explorer</h1>
        <p className="text-sm text-gray-600 mt-1">Explore unemployment data across states and metropolitan areas</p>
      </div>

      {/* Section 1: National Overview */}
      <Card>
        <SectionHeader title="National Overview" color="red" />
        <div className="p-5">
          <div className="flex justify-between items-start mb-4">
            <p className="text-xs text-gray-500">
              Note: Data aggregated from state-level statistics. For official national unemployment, see LN Survey.
            </p>
            <Select
              value={overviewTimeRange}
              onChange={(v) => setOverviewTimeRange(Number(v))}
              options={timeRangeOptions}
            />
          </div>
          {loadingOverview ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-red-500" /></div>
          ) : overview ? (
            <>
              {(() => {
                // Get display data - either selected period or latest
                let displayData = overview.national_unemployment;
                let displayDate = overview.national_unemployment.latest_date;
                if (selectedOverviewPeriod && overviewTimeline?.timeline) {
                  const point = overviewTimeline.timeline.find(
                    p => p.year === selectedOverviewPeriod.year && p.period === selectedOverviewPeriod.period
                  );
                  if (point) {
                    displayData = point;
                    displayDate = point.period_name;
                  }
                }
                return (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <Card className="bg-red-50 border-red-200">
                      <div className="p-4">
                        <p className="text-xs font-medium text-red-700 uppercase">Unemployment Rate</p>
                        <p className="text-xs text-gray-500">{displayDate}</p>
                        <p className="text-4xl font-bold text-red-700 mt-2">{formatRate(displayData.unemployment_rate)}</p>
                      </div>
                    </Card>
                    <Card className="bg-green-50 border-green-200">
                      <div className="p-4">
                        <p className="text-xs font-medium text-green-700 uppercase">Employment</p>
                        <p className="text-xs text-gray-500">{displayDate}</p>
                        <p className="text-3xl font-bold text-green-700 mt-2">{formatNumber(displayData.employment_level)}K</p>
                      </div>
                    </Card>
                    <Card className="bg-blue-50 border-blue-200">
                      <div className="p-4">
                        <p className="text-xs font-medium text-blue-700 uppercase">Labor Force</p>
                        <p className="text-xs text-gray-500">{displayDate}</p>
                        <p className="text-3xl font-bold text-blue-700 mt-2">{formatNumber(displayData.labor_force)}K</p>
                      </div>
                    </Card>
                  </div>
                );
              })()}

              {/* National unemployment timeline chart */}
              {overviewTimeline?.timeline?.length > 0 && (
                <Card>
                  <div className="p-4">
                    <p className="text-sm font-semibold mb-3">National Unemployment Rate Trend</p>
                    <div className="h-64">
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
                          <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                          <Tooltip formatter={(v) => [`${v?.toFixed(1)}%`, 'Unemployment Rate']} />
                          <Legend wrapperStyle={{ fontSize: '11px' }} />
                          <Line
                            type="monotone"
                            dataKey="unemployment_rate"
                            stroke="#dc2626"
                            strokeWidth={2}
                            dot={false}
                            name="Unemployment Rate"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <TimelineSelector
                      timeline={overviewTimeline.timeline}
                      selectedPeriod={selectedOverviewPeriod}
                      onSelectPeriod={setSelectedOverviewPeriod}
                    />
                  </div>
                </Card>
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
              View unemployment rates across states and metros. {selectedGeoPeriod ? `Showing: ${formatPeriod(selectedGeoPeriod.period)} ${selectedGeoPeriod.year}` : 'Showing latest data.'}
            </p>
            <div className="flex gap-2 items-center">
              <Select
                value={geoTimeRange}
                onChange={(v) => { setGeoTimeRange(Number(v)); setSelectedGeoPeriod(null); }}
                options={timeRangeOptions}
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
            <span className="text-xs font-semibold">Unemployment Rate:</span>
            {[
              { label: '< 3%', color: '#16a34a' },
              { label: '3-4%', color: '#4ade80' },
              { label: '4-5%', color: '#fbbf24' },
              { label: '5-6%', color: '#fb923c' },
              { label: '6-7%', color: '#f87171' },
              { label: '> 7%', color: '#dc2626' },
            ].map(item => (
              <div key={item.label} className="flex items-center gap-1">
                <div className="w-4 h-4 rounded-full border border-gray-300" style={{ backgroundColor: item.color }} />
                <span className="text-xs">{item.label}</span>
              </div>
            ))}
          </div>

          {loadingStates || loadingMetros || loadingGeo ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-orange-500" /></div>
          ) : (
            <>
              <div className="h-[500px] border border-gray-200 rounded-lg overflow-hidden">
                <MapContainer
                  center={[39.8283, -98.5795]}
                  zoom={4}
                  minZoom={3}
                  maxZoom={10}
                  maxBounds={US_BOUNDS}
                  style={{ height: '100%', width: '100%', background: '#f5f5f5' }}
                  scrollWheelZoom={true}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
                  />
                  <TileLayer url="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png" />

                  {/* National marker */}
                  {overview && (() => {
                    // Get historical rate if period selected
                    let nationalRate = overview.national_unemployment.unemployment_rate || 5;
                    let nationalLaborForce = overview.national_unemployment.labor_force;
                    if (selectedGeoPeriod && geoOverviewTimeline?.timeline) {
                      const point = geoOverviewTimeline.timeline.find(
                        p => p.year === selectedGeoPeriod.year && p.period === selectedGeoPeriod.period
                      );
                      if (point?.unemployment_rate !== undefined) {
                        nationalRate = point.unemployment_rate;
                        nationalLaborForce = point.labor_force;
                      }
                    }
                    return (
                      <CircleMarker
                        key={`national-${selectedGeoPeriod?.year || 'latest'}-${selectedGeoPeriod?.period || 'latest'}`}
                        center={[39.8283, -98.5795]}
                        radius={18}
                        fillColor={getColorFromRate(nationalRate)}
                        color="#ffd700"
                        weight={4}
                        fillOpacity={0.9}
                      >
                        <Popup>
                          <div className="p-1">
                            <p className="font-semibold">United States (National)</p>
                            <p className="text-sm">Unemployment: {formatRate(nationalRate)}</p>
                            <p className="text-sm">Labor Force: {formatNumber(nationalLaborForce)}K</p>
                          </div>
                        </Popup>
                      </CircleMarker>
                    );
                  })()}

                  {/* State markers - key includes period to force re-render */}
                  {states?.states?.map(state => {
                    const coords = getLAAreaCoordinates(state.area_code, state.area_name);
                    if (!coords) return null;

                    // Get historical rate if period selected
                    let rate = state.unemployment_rate || 0;
                    if (selectedGeoPeriod && geoTimeline?.timeline) {
                      const point = geoTimeline.timeline.find(p => p.year === selectedGeoPeriod.year && p.period === selectedGeoPeriod.period);
                      if (point?.states?.[state.area_code] !== undefined) {
                        rate = point.states[state.area_code];
                      }
                    }

                    const icon = L.divIcon({
                      className: '',
                      html: `<div style="width:14px;height:14px;background:${getColorFromRate(rate)};border:2px solid #1976d2;cursor:pointer;"></div>`,
                      iconSize: [14, 14],
                      iconAnchor: [7, 7],
                    });

                    // Key includes period to force marker recreation when period changes
                    const markerKey = `${state.area_code}-${selectedGeoPeriod?.year || 'latest'}-${selectedGeoPeriod?.period || 'latest'}`;

                    return (
                      <Marker
                        key={markerKey}
                        position={[coords.lat, coords.lng]}
                        icon={icon}
                        eventHandlers={{
                          click: () => {
                            if (!selectedStatesForTimeline.includes(state.area_code) && selectedStatesForTimeline.length < 10) {
                              setSelectedStatesForTimeline([...selectedStatesForTimeline, state.area_code]);
                            }
                          },
                        }}
                      >
                        <Popup>
                          <div className="p-1">
                            <p className="font-semibold">{state.area_name}</p>
                            <p className="text-sm">Unemployment: {formatRate(rate)}</p>
                            <p className="text-sm">Labor Force: {formatNumber(state.labor_force)}K</p>
                          </div>
                        </Popup>
                      </Marker>
                    );
                  })}

                  {/* Metro markers - key includes period to force re-render */}
                  {metros?.metros?.map(metro => {
                    const coords = getLAAreaCoordinates(metro.area_code, metro.area_name);
                    if (!coords) return null;

                    // Get historical rate if period selected
                    let rate = metro.unemployment_rate || 0;
                    if (selectedGeoPeriod && geoMetroTimeline?.timeline) {
                      const point = geoMetroTimeline.timeline.find(p => p.year === selectedGeoPeriod.year && p.period === selectedGeoPeriod.period);
                      if (point?.metros?.[metro.area_code] !== undefined) {
                        rate = point.metros[metro.area_code];
                      }
                    }

                    // Key includes period to force marker recreation when period changes
                    const markerKey = `${metro.area_code}-${selectedGeoPeriod?.year || 'latest'}-${selectedGeoPeriod?.period || 'latest'}`;

                    return (
                      <CircleMarker
                        key={markerKey}
                        center={[coords.lat, coords.lng]}
                        radius={8}
                        fillColor={getColorFromRate(rate)}
                        color="#7b1fa2"
                        weight={2}
                        fillOpacity={0.9}
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
                            <p className="text-sm">Unemployment: {formatRate(rate)}</p>
                            <p className="text-sm">Labor Force: {formatNumber(metro.labor_force)}K</p>
                          </div>
                        </Popup>
                      </CircleMarker>
                    );
                  })}
                </MapContainer>
              </div>

              {geoTimeline?.timeline?.length > 0 && (
                <TimelineSelector
                  timeline={geoTimeline.timeline}
                  selectedPeriod={selectedGeoPeriod}
                  onSelectPeriod={setSelectedGeoPeriod}
                />
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 3: State Analysis */}
      <Card>
        <SectionHeader title="State Analysis" color="blue" />
        <div className="p-5">
          <div className="flex justify-end items-center gap-3 mb-4">
            <Select
              value={stateTimeRange}
              onChange={(v) => { setStateTimeRange(Number(v)); setSelectedStatePeriod(null); }}
              options={timeRangeOptions}
            />
            <ViewToggle value={stateView} onChange={setStateView} />
          </div>

          {loadingStates ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>
          ) : states ? (
            <>
              {/* Rankings */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <Card>
                  <div className="p-4">
                    <p className="text-sm font-semibold text-red-600 mb-2">Highest Unemployment</p>
                    {states.rankings.highest?.map((name, idx) => (
                      <p key={idx} className="text-sm text-gray-600">{idx + 1}. {name}</p>
                    ))}
                  </div>
                </Card>
                <Card>
                  <div className="p-4">
                    <p className="text-sm font-semibold text-green-600 mb-2">Lowest Unemployment</p>
                    {states.rankings.lowest?.map((name, idx) => (
                      <p key={idx} className="text-sm text-gray-600">{idx + 1}. {name}</p>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Timeline chart with national comparison */}
              {nationalTimeline?.timeline?.length > 0 && (
                <Card className="mb-4">
                  <div className="p-4">
                    <p className="text-sm font-semibold mb-1">State Unemployment Trends vs National</p>
                    <p className="text-xs text-gray-500 mb-3">Click states in the table to add them to the chart</p>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={nationalTimeline.timeline.map(p => {
                          const statePoint = stateTimeline?.timeline?.find(sp => sp.year === p.year && sp.period === p.period);
                          return {
                            period_name: p.period_name,
                            national: p.headline_value,
                            states: statePoint?.states || {}
                          };
                        })}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} interval={Math.floor(nationalTimeline.timeline.length / 12)} />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '11px' }} />
                          <Line type="monotone" dataKey="national" stroke="#000000" strokeWidth={3} dot={false} name="National (US)" />
                          {selectedStatesForTimeline.slice(0, 10).map((areaCode, idx) => (
                            <Line
                              key={areaCode}
                              type="monotone"
                              dataKey={(point) => point.states?.[areaCode]}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={false}
                              name={stateTimeline?.state_names?.[areaCode] || areaCode}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    {stateTimeline?.timeline?.length > 0 && (
                      <TimelineSelector
                        timeline={stateTimeline.timeline}
                        selectedPeriod={selectedStatePeriod}
                        onSelectPeriod={setSelectedStatePeriod}
                      />
                    )}
                  </div>
                </Card>
              )}

              {/* State data table/chart */}
              <Card>
                <div className="px-4 py-2 border-b border-gray-200">
                  <p className="text-sm font-semibold">State Unemployment Data ({states.states.length} states)</p>
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
                          <th className="text-right py-2 px-3 font-semibold">Unemp. Rate</th>
                          <th className="text-right py-2 px-3 font-semibold">Labor Force (K)</th>
                          {!selectedStatePeriod && <th className="text-right py-2 px-3 font-semibold">M/M</th>}
                          {!selectedStatePeriod && <th className="text-right py-2 px-3 font-semibold">Y/Y</th>}
                        </tr>
                      </thead>
                      <tbody>
                        {(() => {
                          let displayStates = states.states;
                          if (selectedStatePeriod && stateTimeline?.timeline) {
                            const point = stateTimeline.timeline.find(p => p.year === selectedStatePeriod.year && p.period === selectedStatePeriod.period);
                            if (point) {
                              displayStates = states.states.map(s => ({
                                ...s,
                                unemployment_rate: point.states[s.area_code] ?? s.unemployment_rate
                              })).sort((a, b) => (b.unemployment_rate || 0) - (a.unemployment_rate || 0));
                            }
                          }
                          return displayStates.map(state => (
                            <tr
                              key={state.area_code}
                              className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${selectedStatesForTimeline.includes(state.area_code) ? 'bg-blue-50' : ''}`}
                              onClick={() => {
                                if (selectedStatesForTimeline.includes(state.area_code)) {
                                  setSelectedStatesForTimeline(selectedStatesForTimeline.filter(c => c !== state.area_code));
                                } else if (selectedStatesForTimeline.length < 10) {
                                  setSelectedStatesForTimeline([...selectedStatesForTimeline, state.area_code]);
                                }
                              }}
                            >
                              <td className="py-2 px-3">{state.area_name}</td>
                              <td className="py-2 px-3 text-right">
                                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                                  (state.unemployment_rate || 0) > 5 ? 'bg-red-100 text-red-700' :
                                  (state.unemployment_rate || 0) > 4 ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
                                }`}>
                                  {formatRate(state.unemployment_rate)}
                                </span>
                              </td>
                              <td className="py-2 px-3 text-right">{formatNumber(state.labor_force)}</td>
                              {!selectedStatePeriod && (
                                <td className="py-2 px-3 text-right">
                                  <span className="flex items-center justify-end gap-1">
                                    {state.month_over_month != null && (state.month_over_month >= 0 ? <TrendingUp className="w-4 h-4 text-red-500" /> : <TrendingDown className="w-4 h-4 text-green-500" />)}
                                    {formatChange(state.month_over_month)}
                                  </span>
                                </td>
                              )}
                              {!selectedStatePeriod && (
                                <td className="py-2 px-3 text-right">
                                  <span className="flex items-center justify-end gap-1">
                                    {state.year_over_year != null && (state.year_over_year >= 0 ? <TrendingUp className="w-4 h-4 text-red-500" /> : <TrendingDown className="w-4 h-4 text-green-500" />)}
                                    {formatChange(state.year_over_year)}
                                  </span>
                                </td>
                              )}
                            </tr>
                          ));
                        })()}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-4 h-[500px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={states.states.slice(0, 20)} layout="vertical" margin={{ left: 120 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" tick={{ fontSize: 11 }} />
                        <YAxis type="category" dataKey="area_name" tick={{ fontSize: 10 }} width={110} />
                        <Tooltip />
                        <Bar dataKey="unemployment_rate" fill="#3b82f6" name="Unemployment Rate (%)" />
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
          <div className="flex justify-end items-center gap-3 mb-4">
            <Select
              value={metroTimeRange}
              onChange={(v) => { setMetroTimeRange(Number(v)); setSelectedMetroPeriod(null); }}
              options={timeRangeOptions}
            />
            <ViewToggle value={metroView} onChange={setMetroView} />
          </div>

          {loadingMetros ? (
            <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-green-500" /></div>
          ) : metros ? (
            <>
              {/* Timeline chart */}
              {nationalTimeline?.timeline?.length > 0 && (
                <Card className="mb-4">
                  <div className="p-4">
                    <p className="text-sm font-semibold mb-1">Metro Unemployment Trends vs National</p>
                    <p className="text-xs text-gray-500 mb-3">Click metros in the table to add them to the chart</p>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={nationalTimeline.timeline.map(p => {
                          const metroPoint = metroTimeline?.timeline?.find(mp => mp.year === p.year && mp.period === p.period);
                          return {
                            period_name: p.period_name,
                            national: p.headline_value,
                            metros: metroPoint?.metros || {}
                          };
                        })}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} interval={Math.floor(nationalTimeline.timeline.length / 12)} />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Legend wrapperStyle={{ fontSize: '10px' }} />
                          <Line type="monotone" dataKey="national" stroke="#000000" strokeWidth={3} dot={false} name="National (US)" />
                          {selectedMetrosForTimeline.slice(0, 10).map((areaCode, idx) => (
                            <Line
                              key={areaCode}
                              type="monotone"
                              dataKey={(point) => point.metros?.[areaCode]}
                              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={false}
                              name={metroTimeline?.metro_names?.[areaCode]?.substring(0, 30) || areaCode}
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    {metroTimeline?.timeline?.length > 0 && (
                      <TimelineSelector
                        timeline={metroTimeline.timeline}
                        selectedPeriod={selectedMetroPeriod}
                        onSelectPeriod={setSelectedMetroPeriod}
                      />
                    )}
                  </div>
                </Card>
              )}

              {/* Metro data table/chart */}
              <Card>
                <div className="px-4 py-2 border-b border-gray-200">
                  <p className="text-sm font-semibold">Metro Area Data ({metros.total_count} metros)</p>
                  {selectedMetroPeriod && (
                    <p className="text-xs text-blue-600">Showing: {formatPeriod(selectedMetroPeriod.period)} {selectedMetroPeriod.year}</p>
                  )}
                </div>
                {metroView === 'table' ? (
                  <>
                    <div className="overflow-x-auto max-h-[500px]">
                      <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-gray-50">
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-2 px-3 font-semibold">Metro Area</th>
                            <th className="text-right py-2 px-3 font-semibold">Unemp. Rate</th>
                            <th className="text-right py-2 px-3 font-semibold">Labor Force (K)</th>
                            {!selectedMetroPeriod && <th className="text-right py-2 px-3 font-semibold">M/M</th>}
                            {!selectedMetroPeriod && <th className="text-right py-2 px-3 font-semibold">Y/Y</th>}
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
                              <td className="py-2 px-3 text-right">
                                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                                  (metro.unemployment_rate || 0) > 5 ? 'bg-red-100 text-red-700' :
                                  (metro.unemployment_rate || 0) > 4 ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'
                                }`}>
                                  {formatRate(metro.unemployment_rate)}
                                </span>
                              </td>
                              <td className="py-2 px-3 text-right">{formatNumber(metro.labor_force)}</td>
                              {!selectedMetroPeriod && (
                                <td className="py-2 px-3 text-right">
                                  <span className="flex items-center justify-end gap-1">
                                    {metro.month_over_month != null && (metro.month_over_month >= 0 ? <TrendingUp className="w-4 h-4 text-red-500" /> : <TrendingDown className="w-4 h-4 text-green-500" />)}
                                    {formatChange(metro.month_over_month)}
                                  </span>
                                </td>
                              )}
                              {!selectedMetroPeriod && (
                                <td className="py-2 px-3 text-right">
                                  <span className="flex items-center justify-end gap-1">
                                    {metro.year_over_year != null && (metro.year_over_year >= 0 ? <TrendingUp className="w-4 h-4 text-red-500" /> : <TrendingDown className="w-4 h-4 text-green-500" />)}
                                    {formatChange(metro.year_over_year)}
                                  </span>
                                </td>
                              )}
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
                      <BarChart data={metros.metros.slice(0, 20).map(m => ({ ...m, short_name: m.area_name.substring(0, 30) }))} layout="vertical" margin={{ left: 180 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" tick={{ fontSize: 11 }} />
                        <YAxis type="category" dataKey="short_name" tick={{ fontSize: 9 }} width={170} />
                        <Tooltip />
                        <Bar dataKey="unemployment_rate" fill="#10b981" name="Unemployment Rate (%)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </Card>
            </>
          ) : null}
        </div>
      </Card>

      {/* Section 5: Series Detail Explorer */}
      <Card>
        <SectionHeader title="Series Detail Explorer" color="cyan" />
        <div className="p-5">
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Select
              label="Area"
              value={selectedArea}
              onChange={setSelectedArea}
              options={[
                { value: '', label: 'All Areas' },
                ...(dimensions?.areas?.slice(0, 100).map(a => ({ value: a.area_code, label: a.area_name })) || [])
              ]}
            />
            <Select
              label="Measure"
              value={selectedMeasure}
              onChange={setSelectedMeasure}
              options={[
                { value: '', label: 'All Measures' },
                ...(dimensions?.measures?.map(m => ({ value: m.measure_code, label: m.measure_name })) || [])
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
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <p className="text-sm font-semibold">Available Series ({seriesList?.total || 0}) - Click to add to chart</p>
              {selectedSeriesIds.length > 0 && (
                <button onClick={() => setSelectedSeriesIds([])} className="text-sm text-gray-500 hover:text-gray-700">Clear All ({selectedSeriesIds.length})</button>
              )}
            </div>
            <div className="overflow-x-auto max-h-[400px] border border-gray-200 rounded-lg">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-gray-50">
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-3 font-semibold text-xs">Area</th>
                    <th className="text-left py-2 px-3 font-semibold text-xs">Measure</th>
                    <th className="text-left py-2 px-3 font-semibold text-xs">Seasonal</th>
                    <th className="text-left py-2 px-3 font-semibold text-xs">Period</th>
                  </tr>
                </thead>
                <tbody>
                  {loadingSeries ? (
                    <tr><td colSpan={4} className="py-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-cyan-500" /></td></tr>
                  ) : seriesList?.series?.map(series => (
                    <tr
                      key={series.series_id}
                      className={`border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${selectedSeriesIds.includes(series.series_id) ? 'bg-cyan-50' : ''}`}
                      onClick={() => {
                        if (selectedSeriesIds.includes(series.series_id)) {
                          setSelectedSeriesIds(selectedSeriesIds.filter(id => id !== series.series_id));
                        } else if (selectedSeriesIds.length < 5) {
                          setSelectedSeriesIds([...selectedSeriesIds, series.series_id]);
                        }
                      }}
                    >
                      <td className="py-2 px-3 text-xs">{series.area_name}</td>
                      <td className="py-2 px-3 text-xs">{series.measure_name}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 text-[10px] rounded ${series.seasonal_code === 'S' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}`}>
                          {series.seasonal_code === 'S' ? 'SA' : 'NSA'}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Selected Series Chart/Table */}
          {selectedSeriesIds.length > 0 && (
            <div>
              <div className="flex items-center justify-between gap-4 mb-4">
                <div className="flex items-center gap-4">
                  <Select
                    label="Time Range"
                    value={seriesTimeRange}
                    onChange={(v) => setSeriesTimeRange(Number(v))}
                    options={timeRangeOptions}
                  />
                  <ViewToggle value={seriesView} onChange={setSeriesView} />
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedSeriesIds.map((seriesId, idx) => (
                    <span key={seriesId} className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs" style={{ backgroundColor: `${CHART_COLORS[idx % CHART_COLORS.length]}20`, color: CHART_COLORS[idx % CHART_COLORS.length] }}>
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }} />
                      {seriesId}
                      <button onClick={() => setSelectedSeriesIds(selectedSeriesIds.filter(s => s !== seriesId))} className="ml-1 hover:opacity-70"><X className="w-3 h-3" /></button>
                    </span>
                  ))}
                </div>
              </div>

              {seriesView === 'chart' && (() => {
                const allDataLoaded = selectedSeriesIds.every(id => seriesChartData[id]);
                if (!allDataLoaded) return <div className="py-8"><Loader2 className="w-8 h-8 animate-spin mx-auto text-cyan-500" /></div>;

                const allPeriods = new Map();
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
                  const row = { period_name: p.period_name };
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
                        <YAxis />
                        <Tooltip />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {selectedSeriesIds.map((seriesId, idx) => {
                          const seriesInfo = seriesList?.series?.find(s => s.series_id === seriesId);
                          const label = seriesInfo ? `${seriesInfo.area_name} - ${seriesInfo.measure_name}` : seriesId;
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

                const allPeriods = new Map();
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
                const valueMap = {};
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
                          {selectedSeriesIds.map((seriesId, idx) => {
                            const seriesInfo = seriesList?.series?.find(s => s.series_id === seriesId);
                            return (
                              <th key={seriesId} className="text-right py-2 px-3 font-semibold min-w-[120px]" style={{ color: CHART_COLORS[idx % CHART_COLORS.length] }} title={seriesInfo?.area_name}>
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
          )}
        </div>
      </Card>

      {/* Info box */}
      <Card className="bg-blue-50 border-blue-200">
        <div className="p-4">
          <p className="text-sm text-gray-700">
            <strong>Note:</strong> LA Survey provides local area unemployment statistics including states, metropolitan areas, counties, and cities.
            State data is seasonally adjusted when available. Metro area data is typically not seasonally adjusted.
            Click on map markers or table rows to add areas to the comparison charts. Use the Series Detail Explorer for advanced data queries.
          </p>
        </div>
      </Card>
    </div>
  );
}
