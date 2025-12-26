import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  Search,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Star,
} from 'lucide-react';
import { fredCalendarAPI } from '../services/api';

// Types
interface Series {
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
  observations_count: number;
}

interface ReleaseSeriesResponse {
  release_id: number;
  release_name: string;
  total: number;
  offset: number;
  limit: number;
  series: Series[];
}

interface ReleaseDatesResponse {
  release_id: number;
  name: string;
  link: string | null;
  press_release: boolean;
  series_count: number;
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

export default function FREDReleasePage() {
  const { releaseId } = useParams<{ releaseId: string }>();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const rowsPerPage = 50;

  const { data: releaseInfo, isLoading: releaseLoading } = useQuery({
    queryKey: ['fred-release-dates', releaseId],
    queryFn: async () => {
      const response = await fredCalendarAPI.getReleaseDates<ReleaseDatesResponse>(
        Number(releaseId),
        20
      );
      return response.data;
    },
    enabled: !!releaseId,
  });

  const { data: seriesData, isLoading: seriesLoading } = useQuery({
    queryKey: ['fred-release-series', releaseId, page, rowsPerPage, search],
    queryFn: async () => {
      const response = await fredCalendarAPI.getReleaseSeries<ReleaseSeriesResponse>(
        Number(releaseId),
        {
          offset: page * rowsPerPage,
          limit: rowsPerPage,
          search: search || undefined,
        }
      );
      return response.data;
    },
    enabled: !!releaseId,
  });

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    setPage(0);
  };

  const handleSeriesClick = (seriesId: string) => {
    navigate(`/research/fred-calendar/series/${seriesId}`);
  };

  const totalPages = seriesData ? Math.ceil(seriesData.total / rowsPerPage) : 0;

  if (releaseLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-[1600px] mx-auto px-4 py-6">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-xs text-gray-500 mb-3">
          <Link to="/research/fred-calendar" className="hover:text-indigo-600">
            FRED Calendar
          </Link>
          <span>/</span>
          <span className="text-gray-900 font-medium">{releaseInfo?.name || 'Release'}</span>
        </nav>

        {/* Header */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800 mb-2"
          >
            <ArrowLeft className="w-3 h-3" />
            Back
          </button>
          <h1 className="text-xl font-bold text-gray-900 mb-2">{releaseInfo?.name}</h1>
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center px-2 py-1 text-xs font-semibold bg-indigo-100 text-indigo-800 rounded">
              {releaseInfo?.series_count?.toLocaleString()} series
            </span>
            {releaseInfo?.link && (
              <a
                href={releaseInfo.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
              >
                <ExternalLink className="w-3 h-3" />
                View on FRED
              </a>
            )}
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-lg border border-gray-200 p-3 mb-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search series by ID or title..."
              value={search}
              onChange={handleSearchChange}
              className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Series Table */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          {seriesLoading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 border-b-2 border-gray-300">
                    <tr>
                      <th className="text-left p-3 font-semibold text-gray-700">Series ID</th>
                      <th className="text-left p-3 font-semibold text-gray-700">Title</th>
                      <th className="text-center p-3 font-semibold text-gray-700">Freq</th>
                      <th className="text-left p-3 font-semibold text-gray-700">Units</th>
                      <th className="text-right p-3 font-semibold text-gray-700">Obs</th>
                      <th className="text-right p-3 font-semibold text-gray-700">Last Updated</th>
                      <th className="text-center p-3 font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {seriesData?.series?.map((s, idx) => (
                      <tr
                        key={s.series_id}
                        onClick={() => handleSeriesClick(s.series_id)}
                        className={`cursor-pointer hover:bg-gray-100 transition-all ${idx % 2 === 1 ? 'bg-gray-50 shadow-[inset_0_1px_2px_rgba(0,0,0,0.05)]' : 'bg-white'}`}
                      >
                        <td className="p-3">
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-sm font-medium text-gray-900">
                              {s.series_id}
                            </span>
                            {s.popularity >= 80 && (
                              <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                            )}
                          </div>
                        </td>
                        <td className="p-3">
                          <span className="text-gray-700 line-clamp-1 max-w-[400px]">
                            {s.title || 'No title'}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <span className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded text-white ${frequencyColors[s.frequency_short] || 'bg-gray-400'}`}>
                            {s.frequency_short || s.frequency || '-'}
                          </span>
                        </td>
                        <td className="p-3">
                          <span className="text-xs text-gray-500">{s.units_short || s.units || '-'}</span>
                        </td>
                        <td className="p-3 text-right">
                          <span className="text-xs text-gray-900">
                            {s.observations_count > 0 ? s.observations_count.toLocaleString() : '-'}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <span className="text-xs text-gray-500">
                            {s.last_updated ? new Date(s.last_updated).toLocaleDateString() : '-'}
                          </span>
                        </td>
                        <td className="p-3 text-center">
                          <button
                            onClick={(e) => { e.stopPropagation(); handleSeriesClick(s.series_id); }}
                            className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
                            title="View Chart"
                          >
                            <TrendingUp className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                    {(!seriesData?.series || seriesData.series.length === 0) && (
                      <tr>
                        <td colSpan={7} className="p-8 text-center text-gray-500">
                          {search ? 'No series found matching your search' : 'No series in this release'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {seriesData && seriesData.total > rowsPerPage && (
                <div className="flex items-center justify-between px-3 py-3 border-t border-gray-200 bg-gray-50">
                  <span className="text-xs text-gray-600">
                    {seriesData.offset + 1}-{Math.min(seriesData.offset + seriesData.series.length, seriesData.total)} of {seriesData.total.toLocaleString()}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPage(Math.max(0, page - 1))}
                      disabled={page === 0}
                      className="p-1.5 text-gray-600 hover:bg-gray-200 rounded disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span className="text-xs text-gray-600">Page {page + 1} / {totalPages}</span>
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}
