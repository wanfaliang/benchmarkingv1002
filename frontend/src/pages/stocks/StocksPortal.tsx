import { useState, useEffect, ReactElement } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  stocksAPI,
  ScreenTemplate,
  ScreenResponse,
  SavedScreenSummary,
  ScreenFilter,
  UniverseFilter,
} from '../../services/api';
import {
  TrendingUp,
  Search,
  Filter,
  Plus,
  Play,
  Clock,
  Loader2,
  ChevronRight,
  BarChart3,
  Target,
  DollarSign,
  Zap,
  Shield,
  Users,
  X,
  Activity,
  Layers,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
} from 'lucide-react';

// ============================================================================
// CONSTANTS
// ============================================================================

const CATEGORY_CONFIG: Record<string, { icon: ReactElement; color: string; bg: string }> = {
  value: {
    icon: <Target className="w-4 h-4" />,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/20'
  },
  growth: {
    icon: <TrendingUp className="w-4 h-4" />,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/20'
  },
  income: {
    icon: <DollarSign className="w-4 h-4" />,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/20'
  },
  momentum: {
    icon: <Zap className="w-4 h-4" />,
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/20'
  },
  quality: {
    icon: <BarChart3 className="w-4 h-4" />,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/20'
  },
  defensive: {
    icon: <Shield className="w-4 h-4" />,
    color: 'text-slate-400',
    bg: 'bg-slate-500/10 border-slate-500/20'
  },
  sentiment: {
    icon: <Users className="w-4 h-4" />,
    color: 'text-pink-400',
    bg: 'bg-pink-500/10 border-pink-500/20'
  },
  macro: {
    icon: <Activity className="w-4 h-4" />,
    color: 'text-orange-400',
    bg: 'bg-orange-500/10 border-orange-500/20'
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatMarketCap = (value: number | undefined): string => {
  if (!value) return '—';
  if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  return `$${value.toLocaleString()}`;
};

const formatPercent = (value: number | undefined): string => {
  if (value === undefined || value === null) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

const formatTimeAgo = (dateStr: string | undefined): string => {
  if (!dateStr) return 'Never run';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

// ============================================================================
// TEMPLATE CARD COMPONENT
// ============================================================================

interface TemplateCardProps {
  template: ScreenTemplate;
  onRun: () => void;
  isLoading: boolean;
  index: number;
}

function TemplateCard({ template, onRun, isLoading, index }: TemplateCardProps): ReactElement {
  const config = CATEGORY_CONFIG[template.category] || CATEGORY_CONFIG.value;

  return (
    <div
      className="group relative bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 rounded-xl overflow-hidden card-lift animate-slide-up"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* Gradient accent line */}
      <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent ${config.color.replace('text-', 'via-')} to-transparent opacity-60 group-hover:opacity-100 transition-opacity`} />

      {/* Hover glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      <div className="relative p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className={`${config.bg} border ${config.color} p-2.5 rounded-lg shadow-lg`}>
            {config.icon}
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-[10px] font-semibold uppercase tracking-wider ${config.color} font-mono`}>
              {template.category}
            </span>
          </div>
        </div>

        {/* Content */}
        <h3 className="text-base font-semibold text-slate-100 mb-2 group-hover:text-white transition-colors" style={{ fontFamily: 'var(--font-display)' }}>
          {template.name}
        </h3>
        <p className="text-sm text-slate-400 mb-4 line-clamp-2 leading-relaxed">
          {template.description}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-800/50 rounded text-xs text-slate-400 font-mono">
              <Filter className="w-3 h-3" />
              {template.filters.length}
            </div>
          </div>
          <button
            onClick={onRun}
            disabled={isLoading}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              isLoading
                ? 'bg-slate-700 text-slate-400 cursor-wait'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 hover:border-emerald-500/50 hover:shadow-lg hover:shadow-emerald-500/10'
            }`}
          >
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5" />
            )}
            {isLoading ? 'Running...' : 'Execute'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// SAVED SCREEN ROW COMPONENT
// ============================================================================

interface SavedScreenRowProps {
  screen: SavedScreenSummary;
  onRun: () => void;
  index: number;
}

function SavedScreenRow({ screen, onRun, index }: SavedScreenRowProps): ReactElement {
  return (
    <div
      className="group flex items-center justify-between p-4 bg-slate-900/40 border border-slate-700/50 rounded-xl hover:bg-slate-800/50 hover:border-slate-600 transition-all duration-200 data-row-hover animate-slide-up"
      style={{ animationDelay: `${index * 30}ms` }}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center justify-center group-hover:border-slate-600 transition-colors">
            <Layers className="w-4 h-4 text-slate-400 group-hover:text-slate-300 transition-colors" />
          </div>
          <div>
            <h4 className="font-medium text-slate-200 truncate group-hover:text-white transition-colors" style={{ fontFamily: 'var(--font-display)' }}>
              {screen.name}
            </h4>
            <div className="flex items-center gap-3 mt-1.5">
              <span className="flex items-center gap-1.5 px-2 py-0.5 text-xs text-slate-400 bg-slate-800/50 rounded font-mono">
                <Filter className="w-3 h-3" />
                {screen.filter_count}
              </span>
              <span className="flex items-center gap-1.5 text-xs text-slate-500">
                <Clock className="w-3 h-3" />
                {formatTimeAgo(screen.last_run_at)}
              </span>
              {screen.last_result_count !== null && screen.last_result_count !== undefined && (
                <span className="text-xs text-emerald-400/80 font-mono">
                  {screen.last_result_count.toLocaleString()} matches
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="flex items-center gap-1 ml-4">
        <button
          onClick={onRun}
          className="p-2.5 text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors"
          title="Run screen"
        >
          <Play className="w-4 h-4" />
        </button>
        <Link
          to={`/stocks/screener?screen=${screen.screen_id}`}
          className="p-2.5 text-slate-400 hover:text-slate-300 hover:bg-slate-700/50 rounded-lg transition-colors"
          title="Edit screen"
        >
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}

// ============================================================================
// QUICK RESULTS PANEL
// ============================================================================

interface QuickResultsPanelProps {
  title: string;
  results: ScreenResponse | null;
  loading: boolean;
  onClose: () => void;
  onPageChange: (offset: number) => void;
  onSort: (column: string, order: 'asc' | 'desc') => void;
  offset: number;
  limit: number;
  totalCount: number | null;
  filters: ScreenFilter[];
  universe: UniverseFilter | null;
  sortBy: string;
  sortOrder: string;
}

// Column definition for sortable table
interface ColumnDef {
  key: string;
  label: string;
  sortKey: string;
  align: 'left' | 'right';
  sortable: boolean;
}

const RESULT_COLUMNS: ColumnDef[] = [
  { key: 'symbol', label: 'Symbol', sortKey: 'symbol', align: 'left', sortable: true },
  { key: 'company_name', label: 'Company', sortKey: 'company_name', align: 'left', sortable: true },
  { key: 'sector', label: 'Sector', sortKey: 'sector', align: 'left', sortable: true },
  { key: 'price', label: 'Price', sortKey: 'price', align: 'right', sortable: true },
  { key: 'price_change_pct', label: 'Chg%', sortKey: 'price_change_pct', align: 'right', sortable: true },
  { key: 'market_cap', label: 'Mkt Cap', sortKey: 'market_cap', align: 'right', sortable: true },
  { key: 'pe_ratio_ttm', label: 'P/E', sortKey: 'pe_ratio_ttm', align: 'right', sortable: true },
];

// Helper to format filter values for display
const formatFilterValue = (feature: string, value: number | string): string => {
  if (typeof value === 'string') return value;

  // Format as percentage for ratio metrics
  if (['roe', 'roic', 'gross_margin', 'net_profit_margin', 'dividend_yield'].includes(feature)) {
    return `${(value * 100).toFixed(1)}%`;
  }
  // Format as currency for market cap
  if (feature === 'market_cap') {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(0)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(0)}M`;
    return `$${value.toLocaleString()}`;
  }
  // Default number format
  return value.toLocaleString();
};

// Map feature keys to readable names
const FEATURE_NAMES: Record<string, string> = {
  // Valuation
  pe_ratio_ttm: 'P/E Ratio',
  pb_ratio: 'P/B Ratio',
  ev_to_ebitda: 'EV/EBITDA',
  peg_ratio: 'PEG Ratio',
  earnings_yield: 'Earnings Yield',
  fcf_yield: 'FCF Yield',
  // Profitability
  roe: 'ROE',
  roic: 'ROIC',
  gross_margin: 'Gross Margin',
  net_profit_margin: 'Net Margin',
  // Leverage & Dividend
  dividend_yield: 'Div Yield',
  payout_ratio: 'Payout Ratio',
  debt_to_equity: 'Debt/Equity',
  current_ratio: 'Current Ratio',
  interest_coverage: 'Int. Coverage',
  // Risk & Size
  beta: 'Beta',
  market_cap: 'Market Cap',
  // Price & 52-Week
  price: 'Price',
  price_change_pct: 'Price Change %',
  high_52w: '52-Week High',
  low_52w: '52-Week Low',
  pct_from_high: '% From 52W High',
  pct_from_low: '% From 52W Low',
  // Returns
  return_1d: '1-Day Return',
  return_1w: '1-Week Return',
  return_1m: '1-Month Return',
  return_3m: '3-Month Return',
  return_6m: '6-Month Return',
  return_ytd: 'YTD Return',
  return_1y: '1-Year Return',
  // Volume & Analyst
  volume: 'Volume',
  avg_volume: 'Avg Volume',
  relative_volume: 'Relative Volume',
  price_target_upside: 'PT Upside %',
};

function QuickResultsPanel({
  title, results, loading, onClose, onPageChange, onSort, offset, limit, totalCount,
  filters, universe, sortBy, sortOrder
}: QuickResultsPanelProps): ReactElement {
  const displayTotal = totalCount ?? results?.total_count ?? 0;
  const hasMore = results ? results.returned_count >= limit : false;
  const hasPrevious = offset > 0;

  // Handle column header click for sorting
  const handleColumnClick = (column: ColumnDef) => {
    if (!column.sortable) return;

    // Toggle order if already sorting by this column, otherwise default to desc
    const newOrder: 'asc' | 'desc' =
      sortBy === column.sortKey && sortOrder === 'desc' ? 'asc' : 'desc';
    onSort(column.sortKey, newOrder);
  };

  // Get sort icon for a column
  const getSortIcon = (column: ColumnDef) => {
    if (!column.sortable) return null;
    if (sortBy !== column.sortKey) {
      return <ArrowUpDown className="w-3 h-3 opacity-40" />;
    }
    return sortOrder === 'asc'
      ? <ArrowUp className="w-3 h-3 text-emerald-400" />
      : <ArrowDown className="w-3 h-3 text-emerald-400" />;
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl max-w-5xl w-full max-h-[85vh] overflow-hidden flex flex-col terminal-glow">
        {/* Header - Terminal style */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/80 bg-gradient-to-r from-slate-800/80 to-slate-900/80">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <div className="w-px h-5 bg-slate-700" />
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-emerald-400 terminal-pulse" />
              <h2 className="text-lg font-semibold text-slate-100" style={{ fontFamily: 'var(--font-display)' }}>{title}</h2>
            </div>
            {results && (
              <span className="px-2 py-1 text-[10px] text-slate-400 bg-slate-800 border border-slate-700 rounded font-mono">
                {results.execution_time_ms}ms
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Active Filters Display */}
        {(filters.length > 0 || universe) && (
          <div className="px-6 py-3 border-b border-slate-700/50 bg-slate-800/30">
            <div className="flex items-start gap-4">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Filter className="w-3.5 h-3.5" />
                <span className="font-medium uppercase tracking-wider">Active Filters</span>
              </div>
              <div className="flex flex-wrap gap-2 flex-1">
                {/* Universe filters */}
                {universe?.min_market_cap && (
                  <span className="px-2 py-1 text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">
                    Market Cap ≥ {formatFilterValue('market_cap', universe.min_market_cap)}
                  </span>
                )}
                {universe?.max_market_cap && (
                  <span className="px-2 py-1 text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">
                    Market Cap ≤ {formatFilterValue('market_cap', universe.max_market_cap)}
                  </span>
                )}
                {universe?.sectors && universe.sectors.length > 0 && (
                  <span className="px-2 py-1 text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded">
                    Sectors: {universe.sectors.join(', ')}
                  </span>
                )}
                {universe?.exclude_etfs && (
                  <span className="px-2 py-1 text-xs bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">
                    No ETFs
                  </span>
                )}
                {universe?.exclude_adrs && (
                  <span className="px-2 py-1 text-xs bg-slate-500/10 text-slate-400 border border-slate-500/20 rounded">
                    No ADRs
                  </span>
                )}

                {/* Screen filters */}
                {filters.map((f, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded font-mono"
                  >
                    {FEATURE_NAMES[f.feature] || f.feature} {f.operator} {formatFilterValue(f.feature, f.value as number)}
                  </span>
                ))}

                {/* Sort info */}
                {sortBy && (
                  <span className="px-2 py-1 text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded">
                    Sort: {FEATURE_NAMES[sortBy] || sortBy} ({sortOrder})
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500 mb-4" />
              <p className="text-slate-400 text-sm">Executing screen...</p>
            </div>
          ) : results && results.results.length > 0 ? (
            <div className="data-table-terminal">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-slate-800/95 backdrop-blur-sm border-b border-slate-700 z-10">
                  <tr>
                    {RESULT_COLUMNS.map((col) => (
                      <th
                        key={col.key}
                        className={`px-4 py-3.5 text-[10px] font-semibold uppercase tracking-wider ${
                          col.align === 'right' ? 'text-right' : 'text-left'
                        }`}
                      >
                        <button
                          onClick={() => handleColumnClick(col)}
                          disabled={loading || !col.sortable}
                          className={`inline-flex items-center gap-1.5 transition-colors ${
                            sortBy === col.sortKey
                              ? 'text-emerald-400'
                              : 'text-slate-400 hover:text-slate-200'
                          } ${!col.sortable ? 'cursor-default' : 'cursor-pointer'}`}
                        >
                          {col.label}
                          {getSortIcon(col)}
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {results.results.map((stock, idx) => (
                    <tr
                      key={stock.symbol}
                      className="hover:bg-slate-800/40 transition-colors data-row-hover animate-slide-up"
                      style={{ animationDelay: `${idx * 20}ms` }}
                    >
                      <td className="px-4 py-3 font-mono font-semibold text-amber-400">
                        <span className="hover:text-amber-300 transition-colors cursor-pointer">
                          {stock.symbol}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-300 truncate max-w-[200px]">
                        {stock.company_name || '—'}
                      </td>
                      <td className="px-4 py-3 text-slate-500 text-xs">
                        {stock.sector || '—'}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-slate-200 tabular-nums">
                        ${stock.price?.toFixed(2) || '—'}
                      </td>
                      <td className={`px-4 py-3 text-right font-mono font-medium tabular-nums ${
                        (stock.price_change_pct || 0) >= 0 ? 'status-positive' : 'status-negative'
                      }`}>
                        {formatPercent(stock.price_change_pct)}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-slate-300 tabular-nums">
                        {formatMarketCap(stock.market_cap)}
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-slate-300 tabular-nums">
                        {stock.pe_ratio_ttm?.toFixed(1) || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-slate-500">
              <Filter className="w-12 h-12 mb-4 opacity-30" />
              <p>No stocks match the criteria</p>
            </div>
          )}
        </div>

        {/* Footer with Pagination */}
        {results && (
          <div className="px-6 py-4 border-t border-slate-700 bg-slate-800/50">
            <div className="flex items-center justify-between">
              {/* Pagination Controls */}
              <div className="flex items-center gap-3">
                <button
                  onClick={() => onPageChange(Math.max(0, offset - limit))}
                  disabled={!hasPrevious || loading}
                  className="px-4 py-2 text-sm text-slate-300 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <span className="text-sm text-slate-400 font-mono">
                  {offset + 1} – {offset + results.returned_count}
                  {displayTotal > 0 && (
                    <span className="text-slate-500"> of {displayTotal.toLocaleString()}</span>
                  )}
                </span>
                <button
                  onClick={() => onPageChange(offset + limit)}
                  disabled={!hasMore || loading}
                  className="px-4 py-2 text-sm text-slate-300 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>

              {/* Open in Screener Link */}
              <Link
                to="/stocks/screener"
                className="text-sm text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1"
              >
                Open in Screener
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function StocksPortal(): ReactElement {
  const navigate = useNavigate();

  // State
  const [templates, setTemplates] = useState<ScreenTemplate[]>([]);
  const [templatesLoading, setTemplatesLoading] = useState(true);
  const [savedScreens, setSavedScreens] = useState<SavedScreenSummary[]>([]);
  const [savedLoading, setSavedLoading] = useState(true);

  // Quick results state
  const [runningTemplate, setRunningTemplate] = useState<string | null>(null);
  const [quickResults, setQuickResults] = useState<ScreenResponse | null>(null);
  const [quickResultsTitle, setQuickResultsTitle] = useState('');
  const [quickResultsLoading, setQuickResultsLoading] = useState(false);

  // Pagination state for quick results
  const [quickResultsOffset, setQuickResultsOffset] = useState(0);
  const [quickResultsTotalCount, setQuickResultsTotalCount] = useState<number | null>(null);
  const [currentTemplateKey, setCurrentTemplateKey] = useState<string | null>(null);
  const [currentSavedScreenId, setCurrentSavedScreenId] = useState<string | null>(null);
  const RESULTS_LIMIT = 100;

  // Filter display state for transparency
  const [currentFilters, setCurrentFilters] = useState<ScreenFilter[]>([]);
  const [currentUniverse, setCurrentUniverse] = useState<UniverseFilter | null>(null);
  const [currentSortBy, setCurrentSortBy] = useState<string>('');
  const [currentSortOrder, setCurrentSortOrder] = useState<string>('');

  // Fetch templates
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setTemplatesLoading(true);
        const response = await stocksAPI.listTemplates();
        setTemplates(response.data);
      } catch (error) {
        console.error('Failed to fetch templates:', error);
      } finally {
        setTemplatesLoading(false);
      }
    };
    fetchTemplates();
  }, []);

  // Fetch saved screens
  useEffect(() => {
    const fetchSaved = async () => {
      try {
        setSavedLoading(true);
        const response = await stocksAPI.listSavedScreens();
        setSavedScreens(response.data);
      } catch (error) {
        console.error('Failed to fetch saved screens:', error);
      } finally {
        setSavedLoading(false);
      }
    };
    fetchSaved();
  }, []);

  // Run template handler
  const handleRunTemplate = async (
    template: ScreenTemplate,
    offset: number = 0,
    sortBy?: string,
    sortOrder?: 'asc' | 'desc'
  ) => {
    setRunningTemplate(template.template_key);
    setQuickResultsLoading(true);
    setQuickResultsTitle(template.name);
    setCurrentTemplateKey(template.template_key);
    setCurrentSavedScreenId(null);

    // Use custom sort if provided, otherwise use template defaults
    const effectiveSortBy = sortBy || template.sort_by || '';
    const effectiveSortOrder = sortOrder || template.sort_order || 'desc';

    // Store filter data for transparent display
    setCurrentFilters(template.filters);
    setCurrentUniverse(template.universe || null);
    setCurrentSortBy(effectiveSortBy);
    setCurrentSortOrder(effectiveSortOrder);

    if (offset === 0) {
      setQuickResults(null);
      setQuickResultsOffset(0);
      setQuickResultsTotalCount(null);
    }

    try {
      // Include count on first page
      const includeCount = offset === 0;
      // Pass custom sort parameters if they differ from template defaults
      const customSortBy = sortBy !== undefined ? sortBy : undefined;
      const customSortOrder = sortOrder !== undefined ? sortOrder : undefined;
      const response = await stocksAPI.runTemplate(
        template.template_key,
        RESULTS_LIMIT,
        offset,
        includeCount,
        customSortBy,
        customSortOrder
      );
      setQuickResults(response.data);
      setQuickResultsOffset(offset);

      // Store total count when we get it
      if (response.data.total_count > 0) {
        setQuickResultsTotalCount(response.data.total_count);
      }
    } catch (error) {
      console.error('Failed to run template:', error);
    } finally {
      setQuickResultsLoading(false);
      setRunningTemplate(null);
    }
  };

  // Run saved screen handler
  const handleRunSaved = async (screen: SavedScreenSummary, offset: number = 0) => {
    setQuickResultsLoading(true);
    setQuickResultsTitle(screen.name);
    setCurrentSavedScreenId(screen.screen_id);
    setCurrentTemplateKey(null);

    // Saved screens don't include filter details in summary - clear for now
    // TODO: Fetch full screen details to show filters
    setCurrentFilters([]);
    setCurrentUniverse(null);
    setCurrentSortBy('');
    setCurrentSortOrder('');

    if (offset === 0) {
      setQuickResults(null);
      setQuickResultsOffset(0);
      setQuickResultsTotalCount(null);
    }

    try {
      const response = await stocksAPI.runSavedScreen(screen.screen_id, RESULTS_LIMIT, offset);
      setQuickResults(response.data);
      setQuickResultsOffset(offset);

      if (response.data.total_count > 0) {
        setQuickResultsTotalCount(response.data.total_count);
      }
    } catch (error) {
      console.error('Failed to run saved screen:', error);
    } finally {
      setQuickResultsLoading(false);
    }
  };

  // Handle page change in quick results
  const handleQuickResultsPageChange = (newOffset: number) => {
    if (currentTemplateKey) {
      const template = templates.find(t => t.template_key === currentTemplateKey);
      if (template) {
        // Preserve current sort when paginating
        handleRunTemplate(
          template,
          newOffset,
          currentSortBy || undefined,
          (currentSortOrder as 'asc' | 'desc') || undefined
        );
      }
    } else if (currentSavedScreenId) {
      const screen = savedScreens.find(s => s.screen_id === currentSavedScreenId);
      if (screen) {
        handleRunSaved(screen, newOffset);
      }
    }
  };

  // Handle sort column change in quick results
  const handleSort = (column: string, order: 'asc' | 'desc') => {
    // Reset to first page when sorting changes
    if (currentTemplateKey) {
      const template = templates.find(t => t.template_key === currentTemplateKey);
      if (template) {
        handleRunTemplate(template, 0, column, order);
      }
    }
    // TODO: Add sorting support for saved screens
  };

  // Close quick results
  const closeQuickResults = () => {
    setQuickResults(null);
    setQuickResultsTitle('');
    setQuickResultsOffset(0);
    setQuickResultsTotalCount(null);
    setCurrentTemplateKey(null);
    setCurrentSavedScreenId(null);
    setCurrentFilters([]);
    setCurrentUniverse(null);
    setCurrentSortBy('');
    setCurrentSortOrder('');
  };

  return (
    <div className="stock-screener min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Background pattern - institutional grid */}
      <div className="fixed inset-0 opacity-40 pointer-events-none">
        <div className="absolute inset-0 grid-pattern" />
        <div className="absolute inset-0" style={{
          background: 'radial-gradient(ellipse at 50% 0%, rgba(16, 185, 129, 0.08) 0%, transparent 50%)'
        }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-8">
        {/* Header - Bloomberg style */}
        <div className="flex items-start justify-between mb-10">
          <div>
            <div className="flex items-center gap-4 mb-3">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/25 terminal-glow">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-slate-950 terminal-pulse" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white tracking-tight" style={{ fontFamily: 'var(--font-display)' }}>
                  Stock Screener
                </h1>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-400/80">Terminal</span>
                  <span className="w-1 h-1 rounded-full bg-slate-600" />
                  <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500">Live Market Data</span>
                </div>
              </div>
            </div>
            <p className="text-slate-400 text-sm max-w-lg leading-relaxed">
              Institutional-grade screening with 100+ fundamental and technical filters.
              Execute pre-built strategies or build custom screens.
            </p>
          </div>
          <Link
            to="/stocks/screener"
            className="group flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white text-sm font-semibold rounded-xl hover:from-emerald-400 hover:to-cyan-400 transition-all shadow-lg shadow-emerald-500/25 terminal-glow"
          >
            <Plus className="w-4 h-4 transition-transform group-hover:rotate-90" />
            New Screen
          </Link>
        </div>

        {/* Search Bar - Terminal style */}
        <div className="mb-10">
          <div className="relative max-w-2xl group">
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-xl blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-400 transition-colors" />
              <input
                type="text"
                placeholder="Search by symbol or company name..."
                className="w-full pl-12 pr-28 py-4 bg-slate-900/80 border border-slate-700/80 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 transition-all font-mono text-sm backdrop-blur-sm"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    const value = (e.target as HTMLInputElement).value.toUpperCase();
                    if (value) {
                      navigate(`/stocks/screener?symbol=${value}`);
                    }
                  }
                }}
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                <kbd className="hidden sm:inline-flex items-center gap-1 px-2 py-1 text-[10px] font-mono text-slate-500 bg-slate-800 border border-slate-700 rounded">
                  <span>Enter</span>
                </kbd>
              </div>
            </div>
          </div>
        </div>

        {/* Flagship Templates */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-1 h-6 rounded-full bg-gradient-to-b from-emerald-400 to-cyan-500" />
                <h2 className="text-lg font-semibold text-slate-100" style={{ fontFamily: 'var(--font-display)' }}>
                  Flagship Strategies
                </h2>
              </div>
              <span className="px-2.5 py-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full uppercase tracking-wider">
                {templates.length} screens
              </span>
            </div>
            <Link
              to="/stocks/templates"
              className="group text-sm text-slate-400 hover:text-slate-200 font-medium flex items-center gap-1 transition-colors"
            >
              View all
              <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>

          {templatesLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {templates.slice(0, 8).map((template, idx) => (
                <TemplateCard
                  key={template.template_key}
                  template={template}
                  onRun={() => handleRunTemplate(template)}
                  isLoading={runningTemplate === template.template_key}
                  index={idx}
                />
              ))}
            </div>
          )}
        </section>

        {/* Saved Screens */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-1 h-6 rounded-full bg-gradient-to-b from-slate-400 to-slate-600" />
                <h2 className="text-lg font-semibold text-slate-100" style={{ fontFamily: 'var(--font-display)' }}>
                  My Screens
                </h2>
              </div>
              {savedScreens.length > 0 && (
                <span className="px-2.5 py-1 text-[10px] font-mono text-slate-400 bg-slate-700/50 border border-slate-600/50 rounded-full uppercase tracking-wider">
                  {savedScreens.length} saved
                </span>
              )}
            </div>
            <Link
              to="/stocks/screener"
              className="group text-sm text-slate-400 hover:text-slate-200 font-medium flex items-center gap-1 transition-colors"
            >
              Create new
              <Plus className="w-4 h-4 transition-transform group-hover:rotate-90" />
            </Link>
          </div>

          {savedLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
            </div>
          ) : savedScreens.length > 0 ? (
            <div className="space-y-2">
              {savedScreens.map((screen, idx) => (
                <SavedScreenRow
                  key={screen.screen_id}
                  screen={screen}
                  onRun={() => handleRunSaved(screen)}
                  index={idx}
                />
              ))}
            </div>
          ) : (
            <div className="bg-slate-900/30 border border-slate-700/50 border-dashed rounded-xl p-12 text-center">
              <div className="w-16 h-16 bg-slate-800 border border-slate-700 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Layers className="w-8 h-8 text-slate-600" />
              </div>
              <h3 className="text-lg font-medium text-slate-300 mb-2">No saved screens</h3>
              <p className="text-slate-500 text-sm mb-6 max-w-sm mx-auto">
                Create custom screening criteria and save them for quick access and monitoring.
              </p>
              <Link
                to="/stocks/screener"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-800 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 hover:bg-slate-700 hover:border-slate-600 transition-all"
              >
                <Plus className="w-4 h-4" />
                Create Your First Screen
              </Link>
            </div>
          )}
        </section>
      </div>

      {/* Quick Results Panel */}
      {(quickResults || quickResultsLoading) && (
        <QuickResultsPanel
          title={quickResultsTitle}
          results={quickResults}
          loading={quickResultsLoading}
          onClose={closeQuickResults}
          onPageChange={handleQuickResultsPageChange}
          onSort={handleSort}
          offset={quickResultsOffset}
          limit={RESULTS_LIMIT}
          totalCount={quickResultsTotalCount}
          filters={currentFilters}
          universe={currentUniverse}
          sortBy={currentSortBy}
          sortOrder={currentSortOrder}
        />
      )}
    </div>
  );
}
