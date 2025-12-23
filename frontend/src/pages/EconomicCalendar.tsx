import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Calendar,
  Filter,
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Clock,
  Globe,
} from 'lucide-react';
import { economicCalendarAPI } from '../services/api';

// Types
interface EconomicEvent {
  date: string;
  time: string;
  datetime: string;
  name: string;
  country: string;
  source: string;
  currency: string;
  impact: string | null;
  importance: number;
  previous: number | null;
  estimate: number | null;
  actual: number | null;
  change: number | null;
  change_pct: number | null;
  unit: string | null;
}

interface CalendarData {
  as_of: string;
  count: number;
  events: EconomicEvent[];
}

// Country options
const COUNTRIES = [
  { code: '', label: 'All Countries' },
  { code: 'US', label: 'United States' },
  { code: 'EU', label: 'European Union' },
  { code: 'UK', label: 'United Kingdom' },
  { code: 'JP', label: 'Japan' },
  { code: 'CN', label: 'China' },
  { code: 'CA', label: 'Canada' },
  { code: 'AU', label: 'Australia' },
  { code: 'DE', label: 'Germany' },
  { code: 'FR', label: 'France' },
];

// Impact filter options
const IMPACTS = [
  { value: '', label: 'All Impact Levels' },
  { value: 'High', label: 'High Impact' },
  { value: 'Medium', label: 'Medium Impact' },
  { value: 'Low', label: 'Low Impact' },
];

export default function EconomicCalendar() {
  const [events, setEvents] = useState<EconomicEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'upcoming' | 'recent'>('upcoming');
  const [country, setCountry] = useState('US');
  const [impact, setImpact] = useState('');
  const [days, setDays] = useState(30);

  useEffect(() => {
    loadEvents();
  }, [view, country, impact, days]);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const params = {
        days,
        country: country || undefined,
        impact: impact || undefined,
        limit: 100,
      };

      const res = view === 'upcoming'
        ? await economicCalendarAPI.getUpcoming<CalendarData>(params)
        : await economicCalendarAPI.getRecent<CalendarData>(params);

      setEvents(res.data.events || []);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  // Group events by date
  const eventsByDate = events.reduce((acc, event) => {
    const dateKey = event.datetime?.split('T')[0] || event.date;
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(event);
    return acc;
  }, {} as Record<string, EconomicEvent[]>);

  const sortedDates = Object.keys(eventsByDate).sort((a, b) =>
    view === 'upcoming' ? a.localeCompare(b) : b.localeCompare(a)
  );

  // Format date for display
  const formatDateHeader = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';

    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    });
  };

  // Impact styling
  const getImpactStyle = (impact: string | null) => {
    switch (impact) {
      case 'High':
        return { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-500', dot: 'bg-red-500' };
      case 'Medium':
        return { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-500', dot: 'bg-amber-500' };
      case 'Low':
        return { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-400', dot: 'bg-gray-400' };
      default:
        return { bg: 'bg-gray-50', text: 'text-gray-500', border: 'border-gray-300', dot: 'bg-gray-300' };
    }
  };

  // Format value
  const formatValue = (val: number | null, unit: string | null) => {
    if (val === null) return '--';
    let formatted = '';
    if (Math.abs(val) >= 1000000) {
      formatted = `${(val / 1000000).toFixed(2)}M`;
    } else if (Math.abs(val) >= 1000) {
      formatted = `${(val / 1000).toFixed(1)}K`;
    } else if (Math.abs(val) >= 1) {
      formatted = val.toFixed(1);
    } else {
      formatted = val.toFixed(2);
    }
    return unit ? `${formatted}${unit}` : formatted;
  };

  // Determine surprise direction
  const getSurprise = (actual: number | null, estimate: number | null) => {
    if (actual === null || estimate === null) return null;
    const diff = actual - estimate;
    if (Math.abs(diff) < 0.001) return 'inline';
    return diff > 0 ? 'beat' : 'miss';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                to="/research"
                className="text-gray-500 hover:text-gray-700 p-1 rounded-lg hover:bg-gray-100"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center gap-2">
                <Calendar className="w-6 h-6 text-indigo-600" />
                <h1 className="text-xl font-semibold text-gray-900">Economic Calendar</h1>
              </div>
            </div>

            {/* View Toggle */}
            <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setView('upcoming')}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition ${
                  view === 'upcoming'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Upcoming
              </button>
              <button
                onClick={() => setView('recent')}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition ${
                  view === 'recent'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Recent
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-gray-400" />
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                {COUNTRIES.map((c) => (
                  <option key={c.code} value={c.code}>{c.label}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={impact}
                onChange={(e) => setImpact(e.target.value)}
                className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                {IMPACTS.map((i) => (
                  <option key={i.value} value={i.value}>{i.label}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-400" />
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value={7}>Next 7 days</option>
                <option value={14}>Next 14 days</option>
                <option value={30}>Next 30 days</option>
                <option value={60}>Next 60 days</option>
              </select>
            </div>

            <div className="ml-auto text-sm text-gray-500">
              {events.length} events
            </div>
          </div>
        </div>
      </div>

      {/* Events List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading events...</div>
        ) : events.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No events found</div>
        ) : (
          <div className="space-y-6">
            {sortedDates.map((dateKey) => (
              <div key={dateKey} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                {/* Date Header */}
                <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                  <h3 className="font-medium text-gray-900">{formatDateHeader(dateKey)}</h3>
                  <p className="text-xs text-gray-500">{eventsByDate[dateKey].length} events</p>
                </div>

                {/* Events Table */}
                <div className="divide-y divide-gray-100">
                  {eventsByDate[dateKey].map((event, idx) => {
                    const impactStyle = getImpactStyle(event.impact);
                    const surprise = getSurprise(event.actual, event.estimate);

                    return (
                      <div key={idx} className="px-4 py-3 hover:bg-gray-50 transition">
                        <div className="flex items-start gap-4">
                          {/* Time & Impact */}
                          <div className="w-20 flex-shrink-0">
                            <div className="text-sm font-medium text-gray-900">{event.time}</div>
                            <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded ${impactStyle.bg} ${impactStyle.text}`}>
                              {event.impact || 'N/A'}
                            </span>
                          </div>

                          {/* Event Name & Country */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className={`w-1.5 h-1.5 rounded-full ${impactStyle.dot}`} />
                              <span className="font-medium text-gray-900">{event.name}</span>
                              <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                                {event.country}
                              </span>
                            </div>
                            {event.currency && (
                              <div className="text-xs text-gray-500 mt-0.5">{event.currency}</div>
                            )}
                          </div>

                          {/* Values: Actual, Estimate, Previous */}
                          <div className="flex items-center gap-6 text-sm">
                            {/* Actual */}
                            <div className="w-24 text-right">
                              <div className="text-xs text-gray-400">Actual</div>
                              <div className={`font-semibold ${
                                surprise === 'beat' ? 'text-emerald-600' :
                                surprise === 'miss' ? 'text-red-600' :
                                'text-gray-900'
                              }`}>
                                {formatValue(event.actual, event.unit)}
                                {surprise === 'beat' && <TrendingUp className="w-3 h-3 inline ml-1" />}
                                {surprise === 'miss' && <TrendingDown className="w-3 h-3 inline ml-1" />}
                              </div>
                            </div>

                            {/* Estimate */}
                            <div className="w-24 text-right">
                              <div className="text-xs text-gray-400">Estimate</div>
                              <div className="text-gray-700">{formatValue(event.estimate, event.unit)}</div>
                            </div>

                            {/* Previous */}
                            <div className="w-24 text-right">
                              <div className="text-xs text-gray-400">Previous</div>
                              <div className="text-gray-500">{formatValue(event.previous, event.unit)}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Legend</h4>
          <div className="flex flex-wrap gap-6 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-gray-600">High Impact</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-gray-600">Medium Impact</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-gray-400" />
              <span className="text-gray-600">Low Impact</span>
            </div>
            <div className="flex items-center gap-2 ml-6">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <span className="text-gray-600">Beat Estimate</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-red-600" />
              <span className="text-gray-600">Missed Estimate</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
