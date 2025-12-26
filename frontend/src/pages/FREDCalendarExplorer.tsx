import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import FREDExplorerNav from '../components/FREDExplorerNav';
import {
  ChevronLeft,
  ChevronRight,
  Calendar,
  Clock,
  BarChart3,
  TrendingUp,
  Info,
} from 'lucide-react';
import { fredCalendarAPI } from '../services/api';

// Types
interface Release {
  release_id: number;
  release_name: string;
  release_date: string;
  series_count: number;
}

interface CalendarStats {
  total_dates: number;
  future_dates: number;
  historical_dates: number;
  total_releases: number;
  earliest_date: string | null;
  latest_date: string | null;
}

interface UpcomingReleasesData {
  days: number;
  start_date: string;
  end_date: string;
  count: number;
  releases: Release[];
}

interface MonthData {
  year: number;
  month: number;
  total_releases: number;
  releases_by_date: Record<string, Release[]>;
  releases: Release[];
}

// Month names
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'];
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// Helper: Get days in month
const getDaysInMonth = (year: number, month: number) => {
  return new Date(year, month, 0).getDate();
};

// Helper: Get first day of month (0 = Sunday, 1 = Monday, etc.)
const getFirstDayOfMonth = (year: number, month: number) => {
  return new Date(year, month - 1, 1).getDay();
};

// Helper: Format date for display
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr + 'T12:00:00');
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
};

// Calendar Day Component
function CalendarDay({
  day,
  isToday,
  isCurrentMonth,
  releases,
  onReleaseClick,
}: {
  day: number;
  isToday: boolean;
  isCurrentMonth: boolean;
  releases: Release[];
  onReleaseClick: (releaseId: number) => void;
}) {
  const hasReleases = releases.length > 0;

  return (
    <div
      className={`min-h-[90px] p-1 rounded border ${
        isToday
          ? 'bg-indigo-50 border-indigo-400'
          : isCurrentMonth
          ? 'bg-white border-gray-200'
          : 'bg-gray-50 border-gray-100'
      } ${!isCurrentMonth ? 'opacity-40' : ''}`}
    >
      <span
        className={`inline-block w-5 h-5 leading-5 text-center text-[11px] rounded-full ${
          isToday
            ? 'bg-indigo-600 text-white font-bold'
            : 'font-medium text-gray-700'
        }`}
      >
        {day}
      </span>
      {hasReleases && (
        <div className="mt-0.5 space-y-0.5">
          {releases.slice(0, 3).map((r, i) => (
            <div
              key={i}
              onClick={() => onReleaseClick(r.release_id)}
              className="text-[9px] leading-tight px-1 py-0.5 bg-gray-100 hover:bg-indigo-100 rounded truncate cursor-pointer transition-colors"
              title={`${r.release_name} (${r.series_count} series) - Click to view`}
            >
              {r.release_name}
            </div>
          ))}
          {releases.length > 3 && (
            <span className="text-[8px] text-gray-500 pl-0.5">+{releases.length - 3} more</span>
          )}
        </div>
      )}
    </div>
  );
}

// Calendar Grid Component
function CalendarGrid({ year, month, releasesByDate, onReleaseClick }: {
  year: number;
  month: number;
  releasesByDate: Record<string, Release[]>;
  onReleaseClick: (releaseId: number) => void;
}) {
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);
  const today = new Date();
  const isCurrentMonth = today.getFullYear() === year && today.getMonth() + 1 === month;
  const todayDate = today.getDate();

  // Build calendar grid
  const days: { day: number; isCurrentMonth: boolean; dateStr: string }[] = [];

  // Previous month days
  const prevMonthDays = getDaysInMonth(year, month - 1);
  for (let i = firstDay - 1; i >= 0; i--) {
    const d = prevMonthDays - i;
    const prevMonth = month === 1 ? 12 : month - 1;
    const prevYear = month === 1 ? year - 1 : year;
    days.push({
      day: d,
      isCurrentMonth: false,
      dateStr: `${prevYear}-${String(prevMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
    });
  }

  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    days.push({
      day: d,
      isCurrentMonth: true,
      dateStr: `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
    });
  }

  // Next month days to fill grid (up to 6 weeks = 42 days)
  const remaining = 42 - days.length;
  for (let d = 1; d <= remaining; d++) {
    const nextMonth = month === 12 ? 1 : month + 1;
    const nextYear = month === 12 ? year + 1 : year;
    days.push({
      day: d,
      isCurrentMonth: false,
      dateStr: `${nextYear}-${String(nextMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
    });
  }

  // Split into weeks
  const weeks: typeof days[] = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push(days.slice(i, i + 7));
  }

  return (
    <div>
      {/* Weekday headers */}
      <div className="grid grid-cols-7 gap-0.5 mb-0.5">
        {WEEKDAYS.map(day => (
          <div key={day} className="text-center text-[10px] font-semibold text-gray-500 py-0.5">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      {weeks.map((week, wi) => (
        <div key={wi} className="grid grid-cols-7 gap-0.5 mb-0.5">
          {week.map((d, di) => (
            <CalendarDay
              key={`${wi}-${di}`}
              day={d.day}
              isToday={isCurrentMonth && d.isCurrentMonth && d.day === todayDate}
              isCurrentMonth={d.isCurrentMonth}
              releases={releasesByDate[d.dateStr] || []}
              onReleaseClick={onReleaseClick}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

// Upcoming Releases Sidebar Component
function UpcomingReleases({ onReleaseClick }: { onReleaseClick: (releaseId: number) => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['fred-calendar-upcoming', 14],
    queryFn: async () => {
      const response = await fredCalendarAPI.getUpcoming<UpcomingReleasesData>(14);
      return response.data;
    },
    refetchInterval: 60000,
  });

  if (isLoading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-3 h-full">
        <div className="animate-pulse space-y-2">
          <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          <div className="h-2.5 bg-gray-200 rounded w-full"></div>
          <div className="h-2.5 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  const releases = data?.releases || [];

  // Group by date
  const byDate: Record<string, Release[]> = {};
  releases.forEach((r: Release) => {
    if (!byDate[r.release_date]) byDate[r.release_date] = [];
    byDate[r.release_date].push(r);
  });

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 h-full flex flex-col">
      <h3 className="text-xs font-semibold text-indigo-700 mb-2 flex items-center gap-1.5">
        <Clock className="w-3.5 h-3.5" />
        Upcoming Releases (14 Days)
      </h3>
      {Object.keys(byDate).length === 0 ? (
        <p className="text-xs text-gray-500">No upcoming releases</p>
      ) : (
        <div className="space-y-2 overflow-auto flex-1">
          {Object.entries(byDate).map(([date, items]) => (
            <div key={date}>
              <div className="text-[10px] font-semibold text-gray-500 mb-0.5">
                {formatDate(date)}
              </div>
              <div className="space-y-0.5">
                {items.map((r, i) => (
                  <div
                    key={i}
                    onClick={() => onReleaseClick(r.release_id)}
                    className="flex justify-between items-center py-1 px-1.5 bg-gray-50 hover:bg-indigo-50 rounded text-xs cursor-pointer transition-colors"
                  >
                    <span className="truncate mr-1.5">{r.release_name}</span>
                    <span className="text-[10px] text-gray-500 whitespace-nowrap">
                      {r.series_count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Stats Cards Component
function StatsCards({ stats }: { stats: CalendarStats | undefined }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div className="bg-indigo-600 text-white px-3 py-2 rounded-lg">
        <div className="text-xl font-bold">{stats.total_dates.toLocaleString()}</div>
        <div className="text-xs opacity-90">Total Dates</div>
      </div>
      <div className="bg-white border border-green-400 px-3 py-2 rounded-lg">
        <div className="text-lg font-bold text-green-700">{stats.future_dates.toLocaleString()}</div>
        <div className="text-xs text-green-600">Future Dates</div>
      </div>
      <div className="bg-white border border-blue-400 px-3 py-2 rounded-lg">
        <div className="text-lg font-bold text-blue-700">{stats.historical_dates.toLocaleString()}</div>
        <div className="text-xs text-blue-600">Historical</div>
      </div>
      <div className="bg-white border border-purple-400 px-3 py-2 rounded-lg">
        <div className="text-lg font-bold text-purple-700">{stats.total_releases.toLocaleString()}</div>
        <div className="text-xs text-purple-600">Total Releases</div>
      </div>
    </div>
  );
}

// About Section Component
function AboutSection() {
  return (
    <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-lg p-4 mt-4">
      <h3 className="text-sm font-semibold text-indigo-800 mb-2 flex items-center gap-2">
        <Info className="w-4 h-4" />
        About FRED Release Calendar
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-700">
        <div>
          <h4 className="font-medium text-indigo-700 mb-1">What is this?</h4>
          <p className="mb-2 text-gray-600">
            The FRED Release Calendar shows scheduled publication dates for economic data
            from the Federal Reserve Economic Data (FRED) database.
          </p>
          <h4 className="font-medium text-indigo-700 mb-1">Key Features</h4>
          <ul className="space-y-0.5 list-disc list-inside text-gray-600">
            <li>Monthly calendar view with release highlights</li>
            <li>Upcoming releases for the next 14 days</li>
            <li>Historical and future release dates</li>
          </ul>
        </div>
        <div>
          <h4 className="font-medium text-indigo-700 mb-1">Major Releases</h4>
          <div className="space-y-1.5">
            <div className="flex items-start gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-indigo-500 mt-0.5" />
              <div>
                <span className="font-medium">Employment Situation</span>
                <p className="text-[10px] text-gray-500">Monthly employment data</p>
              </div>
            </div>
            <div className="flex items-start gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-indigo-500 mt-0.5" />
              <div>
                <span className="font-medium">Consumer Price Index</span>
                <p className="text-[10px] text-gray-500">Key measure of inflation</p>
              </div>
            </div>
            <div className="flex items-start gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-indigo-500 mt-0.5" />
              <div>
                <span className="font-medium">Gross Domestic Product</span>
                <p className="text-[10px] text-gray-500">Quarterly output data</p>
              </div>
            </div>
          </div>
          <div className="mt-2">
            <a
              href="https://fred.stlouisfed.org/releases/calendar"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-600 hover:text-indigo-800 text-xs font-medium"
            >
              View on FRED website &rarr;
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

// Main Page Component
export default function FREDCalendarExplorer() {
  const navigate = useNavigate();
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);

  // Handle release click - navigate to release detail page
  const handleReleaseClick = (releaseId: number) => {
    navigate(`/research/fred-calendar/release/${releaseId}`);
  };

  // Stats query
  const { data: stats } = useQuery({
    queryKey: ['fred-calendar-stats'],
    queryFn: async () => {
      const response = await fredCalendarAPI.getStats<CalendarStats>();
      return response.data;
    },
  });

  // Month data query
  const { data: monthData, isLoading: monthLoading } = useQuery({
    queryKey: ['fred-calendar-month', year, month],
    queryFn: async () => {
      const response = await fredCalendarAPI.getMonth<MonthData>(year, month);
      return response.data;
    },
  });

  // Navigation handlers
  const goToPrevMonth = () => {
    if (month === 1) {
      setYear(year - 1);
      setMonth(12);
    } else {
      setMonth(month - 1);
    }
  };

  const goToNextMonth = () => {
    if (month === 12) {
      setYear(year + 1);
      setMonth(1);
    } else {
      setMonth(month + 1);
    }
  };

  const goToToday = () => {
    setYear(today.getFullYear());
    setMonth(today.getMonth() + 1);
  };

  const releasesByDate = monthData?.releases_by_date || {};

  return (
    <div className="min-h-screen bg-gray-50">
      {/* FRED Explorer Navigation */}
      <FREDExplorerNav />

      <div className="px-6 py-6">
        {/* Header */}
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900">FRED Release Calendar</h1>
          <p className="text-sm text-gray-600 mt-1">
            Economic data release schedule from the Federal Reserve
          </p>
        </div>

        {/* Stats */}
        <StatsCards stats={stats} />

        {/* Main content: Calendar + Sidebar */}
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Calendar */}
          <div className="flex-1 bg-white border border-gray-200 rounded-lg p-3">
            {/* Month navigation */}
            <div className="flex justify-between items-center mb-3">
              <div className="flex items-center gap-1.5">
                <button
                  onClick={goToPrevMonth}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <ChevronLeft className="w-4 h-4 text-gray-600" />
                </button>
                <h2 className="text-sm font-semibold text-gray-900 min-w-[150px] text-center">
                  {MONTHS[month - 1]} {year}
                </h2>
                <button
                  onClick={goToNextMonth}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                </button>
              </div>
              <button
                onClick={goToToday}
                className="px-2 py-1 text-xs text-indigo-600 hover:bg-indigo-50 rounded transition-colors flex items-center gap-1"
              >
                <Calendar className="w-3.5 h-3.5" />
                Today
              </button>
            </div>

            {/* Calendar grid */}
            {monthLoading ? (
              <div className="flex justify-center py-10">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            ) : (
              <CalendarGrid year={year} month={month} releasesByDate={releasesByDate} onReleaseClick={handleReleaseClick} />
            )}

            {/* Month summary */}
            {monthData && (
              <p className="text-[11px] text-gray-500 mt-2">
                {monthData.total_releases} releases scheduled in {MONTHS[month - 1]} {year}
              </p>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:w-72 lg:flex-shrink-0">
            <UpcomingReleases onReleaseClick={handleReleaseClick} />
          </div>
        </div>

        {/* About Section */}
        <AboutSection />
      </div>
    </div>
  );
}
