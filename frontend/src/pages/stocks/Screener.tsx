import { useState, useEffect, ReactElement, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  stocksAPI,
  ScreenFilter,
  UniverseFilter,
  ScreenRequest,
  ScreenResponse,
  StockResult,
} from '../../services/api';
import {
  ArrowLeft,
  Play,
  Save,
  Plus,
  Trash2,
  Loader2,
  ChevronDown,
  ChevronUp,
  Filter,
  X,
  Database,
  SlidersHorizontal,
  BarChart3,
  AlertCircle,
  Check,
} from 'lucide-react';

// ============================================================================
// CONSTANTS
// ============================================================================

const OPERATORS = [
  { value: '>', label: '>', desc: 'Greater than' },
  { value: '>=', label: '>=', desc: 'Greater or equal' },
  { value: '<', label: '<', desc: 'Less than' },
  { value: '<=', label: '<=', desc: 'Less or equal' },
  { value: '=', label: '=', desc: 'Equal to' },
  { value: '!=', label: '!=', desc: 'Not equal' },
];

const FEATURE_GROUPS = [
  {
    name: 'Valuation',
    features: [
      { key: 'pe_ratio_ttm', name: 'P/E Ratio (TTM)' },
      { key: 'pb_ratio', name: 'P/B Ratio' },
      { key: 'ev_to_ebitda', name: 'EV/EBITDA' },
      { key: 'peg_ratio', name: 'PEG Ratio' },
      { key: 'earnings_yield', name: 'Earnings Yield' },
      { key: 'fcf_yield', name: 'FCF Yield' },
    ],
  },
  {
    name: 'Profitability',
    features: [
      { key: 'roe', name: 'ROE' },
      { key: 'roic', name: 'ROIC' },
      { key: 'gross_margin', name: 'Gross Margin' },
      { key: 'net_profit_margin', name: 'Net Margin' },
    ],
  },
  {
    name: 'Leverage',
    features: [
      { key: 'debt_to_equity', name: 'Debt/Equity' },
      { key: 'current_ratio', name: 'Current Ratio' },
      { key: 'interest_coverage', name: 'Int. Coverage' },
    ],
  },
  {
    name: 'Dividend',
    features: [
      { key: 'dividend_yield', name: 'Dividend Yield' },
      { key: 'payout_ratio', name: 'Payout Ratio' },
    ],
  },
  {
    name: 'Risk & Size',
    features: [
      { key: 'beta', name: 'Beta' },
      { key: 'market_cap', name: 'Market Cap' },
    ],
  },
  {
    name: 'Price & 52-Week',
    features: [
      { key: 'price', name: 'Price' },
      { key: 'price_change_pct', name: 'Price Change %' },
      { key: 'high_52w', name: '52-Week High', computed: true },
      { key: 'low_52w', name: '52-Week Low', computed: true },
      { key: 'pct_from_high', name: '% From 52W High', computed: true },
      { key: 'pct_from_low', name: '% From 52W Low', computed: true },
    ],
  },
  {
    name: 'Returns',
    features: [
      { key: 'return_1d', name: '1-Day Return', computed: true },
      { key: 'return_1w', name: '1-Week Return', computed: true },
      { key: 'return_1m', name: '1-Month Return', computed: true },
      { key: 'return_3m', name: '3-Month Return', computed: true },
      { key: 'return_6m', name: '6-Month Return', computed: true },
      { key: 'return_ytd', name: 'YTD Return', computed: true },
      { key: 'return_1y', name: '1-Year Return', computed: true },
    ],
  },
  {
    name: 'Volume & Analyst',
    features: [
      { key: 'volume', name: 'Volume' },
      { key: 'avg_volume', name: 'Avg Volume' },
      { key: 'relative_volume', name: 'Relative Volume', computed: true },
      { key: 'price_target_upside', name: 'Price Target Upside %', computed: true },
    ],
  },
];

const SECTORS = [
  'Technology', 'Healthcare', 'Finance', 'Consumer Services',
  'Capital Goods', 'Energy', 'Basic Materials', 'Consumer Durables',
  'Consumer Non-Durables', 'Transportation', 'Utilities', 'Real Estate',
];

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

const formatNumber = (value: number | undefined, decimals: number = 2): string => {
  if (value === undefined || value === null) return '—';
  return value.toFixed(decimals);
};

// ============================================================================
// FILTER ROW COMPONENT
// ============================================================================

interface FilterRowProps {
  filter: ScreenFilter;
  index: number;
  onChange: (index: number, filter: ScreenFilter) => void;
  onRemove: (index: number) => void;
}

function FilterRow({ filter, index, onChange, onRemove }: FilterRowProps): ReactElement {
  return (
    <div className="flex items-center gap-3 p-3.5 bg-slate-800/40 border border-slate-700/50 rounded-xl group hover:border-slate-600 hover:bg-slate-800/60 transition-all data-row-hover animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
      <span className="w-7 h-7 flex items-center justify-center text-xs font-mono text-slate-500 bg-slate-900 border border-slate-700 rounded-lg">
        {index + 1}
      </span>

      <select
        value={filter.feature}
        onChange={(e) => onChange(index, { ...filter, feature: e.target.value })}
        className="flex-1 px-3 py-2.5 bg-slate-900/80 border border-slate-700 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 appearance-none cursor-pointer"
      >
        <option value="" className="text-slate-500">Select metric...</option>
        {FEATURE_GROUPS.map((group) => (
          <optgroup key={group.name} label={group.name} className="text-slate-400">
            {group.features.map((f) => (
              <option key={f.key} value={f.key} className="text-slate-200 bg-slate-900">
                {f.name}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      <select
        value={filter.operator}
        onChange={(e) => onChange(index, { ...filter, operator: e.target.value })}
        className="w-20 px-3 py-2.5 bg-slate-900/80 border border-slate-700 rounded-lg text-sm text-emerald-400 font-mono focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 appearance-none cursor-pointer text-center font-semibold"
      >
        {OPERATORS.map((op) => (
          <option key={op.value} value={op.value}>
            {op.label}
          </option>
        ))}
      </select>

      <input
        type="number"
        value={filter.value as number}
        onChange={(e) => onChange(index, { ...filter, value: parseFloat(e.target.value) || 0 })}
        className="w-32 px-3 py-2.5 bg-slate-900/80 border border-slate-700 rounded-lg text-sm text-slate-200 font-mono focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 text-right tabular-nums"
        placeholder="0"
        step="any"
      />

      <button
        onClick={() => onRemove(index)}
        className="p-2.5 text-slate-600 hover:text-red-400 hover:bg-red-500/10 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
        title="Remove filter"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </div>
  );
}

// ============================================================================
// UNIVERSE PANEL COMPONENT
// ============================================================================

interface UniversePanelProps {
  universe: UniverseFilter;
  onChange: (universe: UniverseFilter) => void;
}

function UniversePanel({ universe, onChange }: UniversePanelProps): ReactElement {
  const [expanded, setExpanded] = useState(true);

  const activeFilters = [
    universe.min_market_cap && 'Min Cap',
    universe.max_market_cap && 'Max Cap',
    universe.sectors?.length && `${universe.sectors.length} Sectors`,
    universe.exclude_etfs && 'No ETFs',
    universe.exclude_adrs && 'No ADRs',
  ].filter(Boolean);

  return (
    <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl overflow-hidden card-lift">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-5 hover:bg-slate-800/30 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
            <Database className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-left">
            <span className="font-medium text-slate-200 block" style={{ fontFamily: 'var(--font-display)' }}>
              Universe
            </span>
            {activeFilters.length > 0 && (
              <span className="text-xs text-slate-500 font-mono">
                {activeFilters.join(' · ')}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          {activeFilters.length > 0 && (
            <span className="px-2.5 py-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full uppercase tracking-wider">
              {activeFilters.length} active
            </span>
          )}
          <div className={`p-1.5 rounded-lg bg-slate-800/50 transition-transform ${expanded ? '' : 'rotate-180'}`}>
            <ChevronUp className="w-4 h-4 text-slate-500" />
          </div>
        </div>
      </button>

      {expanded && (
        <div className="p-4 border-t border-slate-700/50 space-y-5">
          {/* Market Cap */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Market Capitalization
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-xs text-slate-500 mb-1 block">Minimum</span>
                <select
                  value={universe.min_market_cap || ''}
                  onChange={(e) =>
                    onChange({
                      ...universe,
                      min_market_cap: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-emerald-500/50 appearance-none cursor-pointer"
                >
                  <option value="">Any</option>
                  <option value="50000000">$50M+ (Micro)</option>
                  <option value="300000000">$300M+ (Small)</option>
                  <option value="2000000000">$2B+ (Mid)</option>
                  <option value="10000000000">$10B+ (Large)</option>
                  <option value="200000000000">$200B+ (Mega)</option>
                </select>
              </div>
              <div>
                <span className="text-xs text-slate-500 mb-1 block">Maximum</span>
                <select
                  value={universe.max_market_cap || ''}
                  onChange={(e) =>
                    onChange({
                      ...universe,
                      max_market_cap: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-emerald-500/50 appearance-none cursor-pointer"
                >
                  <option value="">Any</option>
                  <option value="300000000">$300M (Micro)</option>
                  <option value="2000000000">$2B (Small)</option>
                  <option value="10000000000">$10B (Mid)</option>
                  <option value="200000000000">$200B (Large)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Sectors */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Sectors
            </label>
            <div className="flex flex-wrap gap-2">
              {SECTORS.map((sector) => {
                const isSelected = universe.sectors?.includes(sector);
                return (
                  <button
                    key={sector}
                    onClick={() => {
                      const current = universe.sectors || [];
                      const updated = isSelected
                        ? current.filter((s) => s !== sector)
                        : [...current, sector];
                      onChange({
                        ...universe,
                        sectors: updated.length > 0 ? updated : undefined,
                      });
                    }}
                    className={`px-3 py-1.5 text-xs rounded-md border transition-all ${
                      isSelected
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                        : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600 hover:text-slate-300'
                    }`}
                  >
                    {sector}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Exclusions */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Exclusions
            </label>
            <div className="flex items-center gap-6">
              <label className="flex items-center gap-2.5 cursor-pointer group">
                <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                  universe.exclude_etfs ? 'bg-emerald-500 border-emerald-500' : 'bg-slate-800 border-slate-600 group-hover:border-slate-500'
                }`}>
                  {universe.exclude_etfs && <Check className="w-3 h-3 text-white" />}
                </div>
                <input
                  type="checkbox"
                  checked={universe.exclude_etfs ?? true}
                  onChange={(e) => onChange({ ...universe, exclude_etfs: e.target.checked })}
                  className="sr-only"
                />
                <span className="text-sm text-slate-300">Exclude ETFs</span>
              </label>
              <label className="flex items-center gap-2.5 cursor-pointer group">
                <div className={`w-5 h-5 rounded border flex items-center justify-center transition-colors ${
                  universe.exclude_adrs ? 'bg-emerald-500 border-emerald-500' : 'bg-slate-800 border-slate-600 group-hover:border-slate-500'
                }`}>
                  {universe.exclude_adrs && <Check className="w-3 h-3 text-white" />}
                </div>
                <input
                  type="checkbox"
                  checked={universe.exclude_adrs ?? false}
                  onChange={(e) => onChange({ ...universe, exclude_adrs: e.target.checked })}
                  className="sr-only"
                />
                <span className="text-sm text-slate-300">Exclude ADRs</span>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// RESULTS TABLE COMPONENT
// ============================================================================

interface ResultsTableProps {
  results: StockResult[];
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  onSort: (column: string) => void;
}

function ResultsTable({ results, sortBy, sortOrder, onSort }: ResultsTableProps): ReactElement {
  const columns = [
    { key: 'symbol', label: 'Symbol', align: 'left' as const },
    { key: 'company_name', label: 'Company', align: 'left' as const },
    { key: 'sector', label: 'Sector', align: 'left' as const },
    { key: 'price', label: 'Price', align: 'right' as const },
    { key: 'price_change_pct', label: 'Chg%', align: 'right' as const },
    { key: 'market_cap', label: 'Mkt Cap', align: 'right' as const },
    { key: 'pe_ratio_ttm', label: 'P/E', align: 'right' as const },
    { key: 'roe', label: 'ROE', align: 'right' as const },
    { key: 'dividend_yield', label: 'Yield', align: 'right' as const },
  ];

  const formatValue = (key: string, value: unknown): string => {
    if (value === undefined || value === null) return '—';
    switch (key) {
      case 'price':
        return `$${(value as number).toFixed(2)}`;
      case 'price_change_pct':
        return formatPercent(value as number);
      case 'market_cap':
        return formatMarketCap(value as number);
      case 'pe_ratio_ttm':
      case 'pb_ratio':
      case 'ev_to_ebitda':
        return formatNumber(value as number, 1);
      case 'roe':
      case 'roic':
      case 'gross_margin':
      case 'net_profit_margin':
      case 'dividend_yield':
        return `${((value as number) * 100).toFixed(1)}%`;
      case 'debt_to_equity':
      case 'current_ratio':
        return formatNumber(value as number, 2);
      default:
        return String(value);
    }
  };

  return (
    <div className="overflow-x-auto data-table-terminal">
      <table className="w-full text-sm">
        <thead className="sticky top-0 bg-slate-800/95 backdrop-blur-sm border-b border-slate-700 z-10">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={`px-4 py-3.5 text-[10px] font-semibold uppercase tracking-wider cursor-pointer hover:bg-slate-700/50 transition-colors ${
                  col.align === 'right' ? 'text-right' : 'text-left'
                } ${sortBy === col.key ? 'text-emerald-400' : 'text-slate-400'}`}
                onClick={() => onSort(col.key)}
              >
                <div className={`flex items-center gap-1.5 ${col.align === 'right' ? 'justify-end' : ''}`}>
                  {col.label}
                  {sortBy === col.key && (
                    sortOrder === 'asc' ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {results.map((stock, idx) => (
            <tr
              key={stock.symbol}
              className="hover:bg-slate-800/40 transition-colors data-row-hover animate-slide-up"
              style={{ animationDelay: `${idx * 15}ms` }}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={`px-4 py-3 ${col.align === 'right' ? 'text-right font-mono tabular-nums' : ''}`}
                >
                  {col.key === 'symbol' ? (
                    <span className="font-mono font-semibold text-amber-400 hover:text-amber-300 transition-colors cursor-pointer">
                      {stock.symbol}
                    </span>
                  ) : col.key === 'company_name' ? (
                    <span className="text-slate-300 truncate block max-w-[180px]">
                      {stock.company_name || '—'}
                    </span>
                  ) : col.key === 'sector' ? (
                    <span className="text-slate-500 text-xs">
                      {stock.sector || '—'}
                    </span>
                  ) : col.key === 'price_change_pct' ? (
                    <span className={`font-medium ${
                      (stock.price_change_pct || 0) >= 0 ? 'status-positive' : 'status-negative'
                    }`}>
                      {formatValue(col.key, stock[col.key as keyof StockResult])}
                    </span>
                  ) : (
                    <span className="text-slate-300">
                      {formatValue(col.key, stock[col.key as keyof StockResult])}
                    </span>
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================================================
// SAVE SCREEN DIALOG
// ============================================================================

interface SaveDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, description: string) => void;
  saving: boolean;
}

function SaveDialog({ isOpen, onClose, onSave, saving }: SaveDialogProps): ReactElement | null {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl max-w-md w-full terminal-glow animate-slide-up">
        {/* Header with terminal dots */}
        <div className="flex items-center justify-between p-5 border-b border-slate-700/80 bg-gradient-to-r from-slate-800/50 to-slate-900/50">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <h3 className="text-lg font-semibold text-slate-100" style={{ fontFamily: 'var(--font-display)' }}>Save Screen</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          <div>
            <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-widest mb-2">
              Screen Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800/80 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 transition-all"
              placeholder="e.g., My Value Screen"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-widest mb-2">
              Description <span className="text-slate-600 font-normal normal-case">(optional)</span>
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-3 bg-slate-800/80 border border-slate-700 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-2 focus:ring-emerald-500/10 resize-none transition-all"
              placeholder="Describe what this screen finds..."
              rows={3}
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 p-5 border-t border-slate-700/80 bg-slate-800/30">
          <button
            onClick={onClose}
            className="px-5 py-2.5 text-slate-300 hover:text-slate-100 hover:bg-slate-700/50 rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(name, description)}
            disabled={!name.trim() || saving}
            className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium rounded-xl hover:from-emerald-400 hover:to-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-emerald-500/20"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Screen
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function Screener(): ReactElement {
  const [searchParams] = useSearchParams();
  const templateKey = searchParams.get('template');

  // Screen configuration state
  const [filters, setFilters] = useState<ScreenFilter[]>([]);
  const [universe, setUniverse] = useState<UniverseFilter>({
    exclude_etfs: true,
  });
  const [sortBy, setSortBy] = useState<string>('market_cap');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [limit] = useState(100);
  const [offset, setOffset] = useState(0);

  // Results state
  const [results, setResults] = useState<ScreenResponse | null>(null);
  const [totalCount, setTotalCount] = useState<number | null>(null); // Store total across pages
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Save dialog state
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  // Track if we need to run after state changes
  const [shouldRun, setShouldRun] = useState(false);

  // Load template if specified
  useEffect(() => {
    if (templateKey) {
      const loadTemplate = async () => {
        try {
          const response = await stocksAPI.getTemplate(templateKey);
          const template = response.data;
          setFilters(template.filters);
          if (template.universe) {
            setUniverse(template.universe);
          }
          setSortBy(template.sort_by);
          setSortOrder(template.sort_order);
          // Auto-run after loading template
          setShouldRun(true);
        } catch (err) {
          console.error('Failed to load template:', err);
        }
      };
      loadTemplate();
    }
  }, [templateKey]);

  // Run screen
  const runScreen = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const request: ScreenRequest = {
        filters: filters.filter((f) => f.feature && f.operator),
        universe,
        sort_by: sortBy,
        sort_order: sortOrder,
        limit,
        offset,
      };

      // Include count on first page for pagination info
      const includeCount = offset === 0;
      const response = await stocksAPI.runScreen(request, includeCount);
      setResults(response.data);

      // Store total count when we get it (first page)
      if (response.data.total_count > 0) {
        setTotalCount(response.data.total_count);
      }
    } catch (err) {
      console.error('Screen failed:', err);
      setError('Failed to run screen. Please check your filters and try again.');
    } finally {
      setLoading(false);
    }
  }, [filters, universe, sortBy, sortOrder, limit, offset]);

  // Run screen when shouldRun flag is set (after state updates)
  useEffect(() => {
    if (shouldRun && !loading) {
      setShouldRun(false);
      runScreen();
    }
  }, [shouldRun, loading, runScreen]);

  // Add filter
  const addFilter = () => {
    setFilters([...filters, { feature: '', operator: '>', value: 0 }]);
  };

  // Update filter
  const updateFilter = (index: number, filter: ScreenFilter) => {
    const updated = [...filters];
    updated[index] = filter;
    setFilters(updated);
  };

  // Remove filter
  const removeFilter = (index: number) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  // Handle sort - triggers re-run
  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
    setOffset(0); // Reset to first page when sorting changes
    setTotalCount(null); // Reset total count
    setShouldRun(true);
  };

  // Handle pagination
  const goToPage = (newOffset: number) => {
    setOffset(newOffset);
    setShouldRun(true);
  };

  // Save screen
  const saveScreen = async (name: string, description: string) => {
    setSaving(true);
    try {
      await stocksAPI.createSavedScreen({
        name,
        description,
        filters,
        universe,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setSaveDialogOpen(false);
    } catch (err) {
      console.error('Failed to save screen:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="stock-screener min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Background pattern - institutional grid */}
      <div className="fixed inset-0 opacity-40 pointer-events-none">
        <div className="absolute inset-0 grid-pattern" />
        <div className="absolute inset-0" style={{
          background: 'radial-gradient(ellipse at 50% 0%, rgba(16, 185, 129, 0.06) 0%, transparent 50%)'
        }} />
      </div>

      {/* Header - Terminal style */}
      <div className="sticky top-0 z-20 bg-slate-900/90 backdrop-blur-xl border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/stocks"
              className="p-2.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="w-px h-8 bg-slate-700/50" />
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 terminal-glow">
                  <SlidersHorizontal className="w-5 h-5 text-white" />
                </div>
                {filters.length > 0 && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-amber-500 rounded-full border-2 border-slate-900 flex items-center justify-center">
                    <span className="text-[9px] font-bold text-slate-900">{filters.length}</span>
                  </div>
                )}
              </div>
              <div>
                <h1 className="text-lg font-semibold text-white" style={{ fontFamily: 'var(--font-display)' }}>
                  Screen Builder
                </h1>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-400/80">Builder</span>
                  <span className="w-1 h-1 rounded-full bg-slate-600" />
                  <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500">
                    {filters.length} filter{filters.length !== 1 ? 's' : ''} active
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setSaveDialogOpen(true)}
              disabled={filters.length === 0}
              className="flex items-center gap-2 px-4 py-2.5 text-slate-300 bg-slate-800/80 border border-slate-700 rounded-xl hover:bg-slate-700 hover:border-slate-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
            <button
              onClick={() => {
                setOffset(0);
                setTotalCount(null);
                runScreen();
              }}
              disabled={loading}
              className="group flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium rounded-xl hover:from-emerald-400 hover:to-cyan-400 disabled:opacity-50 transition-all shadow-lg shadow-emerald-500/25 terminal-glow"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4 transition-transform group-hover:scale-110" />
              )}
              Run Screen
            </button>
          </div>
        </div>
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-6 space-y-5">
        {/* Universe Settings */}
        <UniversePanel universe={universe} onChange={setUniverse} />

        {/* Filters */}
        <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl overflow-hidden card-lift">
          <div className="flex items-center justify-between p-5 border-b border-slate-700/50">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
                <Filter className="w-4 h-4 text-slate-400" />
              </div>
              <div className="flex items-center gap-3">
                <span className="font-medium text-slate-200" style={{ fontFamily: 'var(--font-display)' }}>
                  Screening Criteria
                </span>
                {filters.length > 0 && (
                  <span className="px-2.5 py-1 text-[10px] font-mono text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-full uppercase tracking-wider">
                    {filters.length} active
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={addFilter}
              className="group flex items-center gap-2 px-4 py-2 text-sm text-emerald-400 hover:bg-emerald-500/10 rounded-xl transition-colors border border-transparent hover:border-emerald-500/30"
            >
              <Plus className="w-4 h-4 transition-transform group-hover:rotate-90" />
              Add Filter
            </button>
          </div>

          <div className="p-5">
            {filters.length > 0 ? (
              <div className="space-y-2">
                {filters.map((filter, index) => (
                  <FilterRow
                    key={index}
                    filter={filter}
                    index={index}
                    onChange={updateFilter}
                    onRemove={removeFilter}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-slate-800/80 border border-slate-700 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Filter className="w-8 h-8 text-slate-600" />
                </div>
                <p className="text-slate-300 mb-1" style={{ fontFamily: 'var(--font-display)' }}>No filters configured</p>
                <p className="text-sm text-slate-500 mb-4">Add filters to narrow down your stock universe</p>
                <button
                  onClick={addFilter}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-xl hover:bg-emerald-500/20 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Add Your First Filter
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-3 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-2xl overflow-hidden terminal-glow">
            {/* Results Header - Terminal style */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/50 bg-gradient-to-r from-slate-800/50 to-slate-900/50">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="w-px h-5 bg-slate-700" />
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 terminal-pulse" />
                  <span className="font-medium text-slate-200" style={{ fontFamily: 'var(--font-display)' }}>Results</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <span className="text-slate-400">
                    <span className="text-slate-200 font-mono tabular-nums">{results.returned_count}</span> of{' '}
                    <span className="text-slate-200 font-mono tabular-nums">{results.total_count === -1 ? '∞' : results.total_count.toLocaleString()}</span>
                  </span>
                  <span className="px-2 py-0.5 text-[10px] text-slate-400 bg-slate-800 border border-slate-700 rounded font-mono">
                    {results.execution_time_ms}ms
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <BarChart3 className="w-4 h-4" />
                <span>Sorted by <span className="text-emerald-400">{sortBy}</span> ({sortOrder})</span>
              </div>
            </div>

            {results.results.length > 0 ? (
              <>
                <ResultsTable
                  results={results.results}
                  sortBy={sortBy}
                  sortOrder={sortOrder}
                  onSort={handleSort}
                />

                {/* Pagination */}
                <div className="flex items-center justify-between px-5 py-4 border-t border-slate-700/50 bg-slate-800/30">
                  <button
                    onClick={() => goToPage(Math.max(0, offset - limit))}
                    disabled={offset === 0 || loading}
                    className="px-4 py-2 text-sm text-slate-300 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-slate-400 font-mono">
                      {offset + 1} – {offset + results.returned_count}
                    </span>
                    {totalCount && totalCount > 0 && (
                      <span className="text-xs text-slate-500">
                        of {totalCount.toLocaleString()} total
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => goToPage(offset + limit)}
                    disabled={results.returned_count < limit || loading}
                    className="px-4 py-2 text-sm text-slate-300 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-16">
                <div className="w-16 h-16 bg-slate-800 border border-slate-700 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Filter className="w-8 h-8 text-slate-600" />
                </div>
                <p className="text-lg font-medium text-slate-300 mb-2">No matches found</p>
                <p className="text-sm text-slate-500">Try adjusting your filters or broadening the universe</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Save Dialog */}
      <SaveDialog
        isOpen={saveDialogOpen}
        onClose={() => setSaveDialogOpen(false)}
        onSave={saveScreen}
        saving={saving}
      />
    </div>
  );
}
