import { useState, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  ExternalLink,
  TrendingUp,
  Calendar,
  Download,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  Info,
  Star,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Brush,
} from 'recharts';
import { fredCalendarAPI } from '../services/api';

// Types
interface SeriesDetail {
  series_id: string;
  title: string;
  units: string;
  units_short: string;
  frequency: string;
  frequency_short: string;
  seasonal_adjustment: string;
  seasonal_adjustment_short: string;
  observation_start: string | null;
  observation_end: string | null;
  last_updated: string | null;
  popularity: number;
  notes: string | null;
  observations_count: number;
  releases: { release_id: number; name: string }[];
}

interface Observation {
  date: string;
  value: number | null;
}

interface ObservationsResponse {
  series_id: string;
  title: string;
  units: string;
  units_short: string;
  frequency: string;
  total: number;
  observations: Observation[];
}

// Frequency badge colors
const frequencyColors: Record<string, string> = {
  'D': 'bg-blue-500',
  'W': 'bg-purple-500',
  'M': 'bg-green-500',
  'Q': 'bg-orange-500',
  'SA': 'bg-red-500',
  'A': 'bg-amber-700',
};

// Time range options
type TimeRange = '1Y' | '5Y' | '10Y' | 'MAX';

export default function FREDSeriesPage() {
  const { seriesId } = useParams<{ seriesId: string }>();
  const navigate = useNavigate();
  const [timeRange, setTimeRange] = useState<TimeRange>('5Y');
  const [page, setPage] = useState(0);
  const rowsPerPage = 50;

  // Fetch series detail
  const { data: seriesDetail, isLoading: detailLoading } = useQuery({
    queryKey: ['fred-series-detail', seriesId],
    queryFn: async () => {
      const response = await fredCalendarAPI.getSeriesDetail<SeriesDetail>(seriesId!);
      return response.data;
    },
    enabled: !!seriesId,
  });

  // Calculate date range based on selected time range
  const getDateRange = () => {
    const now = new Date();
    let startDate: string | undefined;

    switch (timeRange) {
      case '1Y':
        startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate()).toISOString().split('T')[0];
        break;
      case '5Y':
        startDate = new Date(now.getFullYear() - 5, now.getMonth(), now.getDate()).toISOString().split('T')[0];
        break;
      case '10Y':
        startDate = new Date(now.getFullYear() - 10, now.getMonth(), now.getDate()).toISOString().split('T')[0];
        break;
      case 'MAX':
      default:
        startDate = undefined;
    }
    return startDate;
  };

  const startDate = getDateRange();

  // Fetch observations
  const { data: obsData, isLoading: obsLoading } = useQuery({
    queryKey: ['fred-series-observations', seriesId, timeRange],
    queryFn: async () => {
      const params: { start_date?: string; limit: number } = { limit: 10000 };
      if (startDate) params.start_date = startDate;
      const response = await fredCalendarAPI.getSeriesObservations<ObservationsResponse>(seriesId!, params);
      return response.data;
    },
    enabled: !!seriesId,
  });

  // Prepare chart data
  const chartData = useMemo(() => {
    return obsData?.observations
      ?.filter(o => o.value !== null)
      .map(o => ({
        date: o.date,
        value: o.value,
      })) || [];
  }, [obsData]);

  // For table pagination (reverse order - newest first)
  const tableData = useMemo(() => {
    return [...(obsData?.observations || [])].reverse();
  }, [obsData]);

  const paginatedData = tableData.slice(page * rowsPerPage, (page + 1) * rowsPerPage);
  const totalPages = Math.ceil(tableData.length / rowsPerPage);

  const handleDownloadCSV = () => {
    if (!obsData?.observations) return;
    const csv = [
      'Date,Value',
      ...obsData.observations.map(o => `${o.date},${o.value ?? ''}`),
    ].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${seriesId}_observations.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (detailLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!seriesDetail) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-gray-600">Series not found</p>
          <button
            onClick={() => navigate(-1)}
            className="mt-4 text-indigo-600 hover:text-indigo-800"
          >
            Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-[1600px] mx-auto px-4 py-6">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-xs text-gray-500 mb-3 flex-wrap">
          <Link to="/research/fred-calendar" className="hover:text-indigo-600 transition-colors">
            FRED Calendar
          </Link>
          {seriesDetail.releases[0] && (
            <>
              <span>/</span>
              <Link
                to={`/research/fred-calendar/release/${seriesDetail.releases[0].release_id}`}
                className="hover:text-indigo-600 transition-colors"
              >
                {seriesDetail.releases[0].name}
              </Link>
            </>
          )}
          <span>/</span>
          <span className="text-gray-900 font-medium font-mono">{seriesId}</span>
        </nav>

        {/* Header */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3 h-3" />
            Back
          </button>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-gray-900">
              {seriesDetail.title || seriesId}
            </h1>
            {seriesDetail.popularity >= 80 && (
              <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
            )}
          </div>
          <p className="font-mono text-sm text-indigo-600 font-semibold mb-3">
            {seriesId}
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded text-white ${
                frequencyColors[seriesDetail.frequency_short] || 'bg-gray-400'
              }`}
            >
              {seriesDetail.frequency || 'Unknown'}
            </span>
            <span className="inline-flex px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded border border-gray-200">
              {seriesDetail.units || 'No units'}
            </span>
            {seriesDetail.seasonal_adjustment_short && (
              <span className="inline-flex px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded border border-gray-200">
                {seriesDetail.seasonal_adjustment_short}
              </span>
            )}
            <a
              href={`https://fred.stlouisfed.org/series/${seriesId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 px-2 py-0.5 text-xs text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 rounded transition-colors"
            >
              <ExternalLink className="w-3 h-3" />
              View on FRED
            </a>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="bg-indigo-600 text-white px-4 py-3 rounded-lg">
            <div className="text-xl font-bold">
              {seriesDetail.observations_count.toLocaleString()}
            </div>
            <div className="text-xs opacity-90">Observations</div>
          </div>
          <div className="bg-white border border-green-400 px-4 py-3 rounded-lg">
            <div className="text-lg font-bold text-green-700">
              {seriesDetail.observation_start || 'N/A'}
            </div>
            <div className="text-xs text-green-600">Start Date</div>
          </div>
          <div className="bg-white border border-blue-400 px-4 py-3 rounded-lg">
            <div className="text-lg font-bold text-blue-700">
              {seriesDetail.observation_end || 'N/A'}
            </div>
            <div className="text-xs text-blue-600">End Date</div>
          </div>
          <div className="bg-white border border-purple-400 px-4 py-3 rounded-lg">
            <div className="text-lg font-bold text-purple-700">
              {seriesDetail.last_updated
                ? new Date(seriesDetail.last_updated).toLocaleDateString()
                : 'N/A'}
            </div>
            <div className="text-xs text-purple-600">Last Updated</div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-3">
            <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-500" />
              Time Series Chart
            </h2>
            <div className="flex items-center gap-2">
              <div className="inline-flex rounded overflow-hidden border border-gray-300">
                {(['1Y', '5Y', '10Y', 'MAX'] as TimeRange[]).map((range) => (
                  <button
                    key={range}
                    onClick={() => setTimeRange(range)}
                    className={`px-2.5 py-1 text-xs font-medium transition-colors ${
                      timeRange === range
                        ? 'bg-indigo-600 text-white'
                        : 'bg-white text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {range}
                  </button>
                ))}
              </div>
              <button
                onClick={handleDownloadCSV}
                disabled={!obsData?.observations?.length}
                className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                CSV
              </button>
            </div>
          </div>

          {obsLoading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : chartData.length === 0 ? (
            <div className="flex justify-center py-12">
              <p className="text-sm text-gray-500">No observation data available</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: '#6b7280' }}
                  tickFormatter={(val) =>
                    new Date(val).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
                  }
                  interval="preserveStartEnd"
                />
                <YAxis
                  tick={{ fontSize: 11, fill: '#6b7280' }}
                  tickFormatter={(val) => {
                    if (Math.abs(val) >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
                    if (Math.abs(val) >= 1000) return `${(val / 1000).toFixed(1)}K`;
                    return val.toFixed(1);
                  }}
                  domain={['auto', 'auto']}
                />
                <Tooltip
                  labelFormatter={(val) =>
                    new Date(val).toLocaleDateString('en-US', {
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric',
                    })
                  }
                  formatter={(value: number) => [
                    value?.toLocaleString(undefined, { maximumFractionDigits: 2 }),
                    seriesDetail.units_short || 'Value',
                  ]}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#4f46e5"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 5, fill: '#4f46e5' }}
                />
                {chartData.length > 100 && (
                  <Brush
                    dataKey="date"
                    height={30}
                    stroke="#6366f1"
                    tickFormatter={(val) =>
                      new Date(val).toLocaleDateString('en-US', { year: '2-digit' })
                    }
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Releases */}
        {seriesDetail.releases.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
            <h2 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-500" />
              Releases
            </h2>
            <div className="flex flex-wrap gap-1.5">
              {seriesDetail.releases.map((r) => (
                <Link
                  key={r.release_id}
                  to={`/research/fred-calendar/release/${r.release_id}`}
                  className="inline-flex px-2 py-1 text-xs text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded border border-indigo-200 transition-colors"
                >
                  {r.name}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Data Table */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-3 py-2 border-b border-gray-200 flex items-center justify-between bg-gray-50">
            <h2 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-indigo-500" />
              Observation Data
            </h2>
            <span className="text-xs text-gray-500">
              {tableData.length.toLocaleString()} records
            </span>
          </div>
          <div className="max-h-[350px] overflow-y-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 sticky top-0 border-b border-gray-200">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600">
                    Date
                  </th>
                  <th className="px-3 py-2 text-right text-xs font-semibold text-gray-600">
                    Value
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedData.map((obs, i) => (
                  <tr key={i} className={`hover:bg-indigo-50 ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}`}>
                    <td className="px-3 py-2 whitespace-nowrap text-gray-900">
                      {new Date(obs.date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-right font-mono text-gray-900">
                      {obs.value !== null
                        ? obs.value.toLocaleString(undefined, { maximumFractionDigits: 4 })
                        : '-'}
                    </td>
                  </tr>
                ))}
                {tableData.length === 0 && (
                  <tr>
                    <td colSpan={2} className="px-3 py-8 text-center text-gray-500">
                      No observations available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-3 py-2 border-t border-gray-200 bg-gray-50">
              <span className="text-xs text-gray-600">
                {page * rowsPerPage + 1}-{Math.min((page + 1) * rowsPerPage, tableData.length)} of {tableData.length.toLocaleString()}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="p-1.5 text-gray-600 hover:bg-gray-200 rounded disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-xs text-gray-600">
                  Page {page + 1} / {totalPages}
                </span>
                <button
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page >= totalPages - 1}
                  className="p-1.5 text-gray-600 hover:bg-gray-200 rounded disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Notes */}
        {seriesDetail.notes && (
          <div className="bg-white rounded-lg border border-gray-200 p-4 mt-4">
            <h2 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <Info className="w-4 h-4 text-indigo-500" />
              Notes
            </h2>
            <p className="text-xs text-gray-600 whitespace-pre-wrap max-h-40 overflow-y-auto">
              {seriesDetail.notes}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
