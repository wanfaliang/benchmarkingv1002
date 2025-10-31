import React, { useState, useEffect, useMemo, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {ArrowLeft,  Database,  TrendingUp,  DollarSign,  Users,  Briefcase,  BarChart3,  LineChart as LineChartIcon,  PieChart,  Download,  RefreshCw,  Search,  Grid3x3,  Table as TableIcon,
  ChevronDown,  Loader2,  AlertCircle, ChevronLeft, ChevronRight, Filter as FilterIcon, BookmarkCheck, Save} from "lucide-react";
import { datasetsAPI, queriesAPI, formatError } from "../services/api";
import ChartBuilder from "../components/charts/ChartBuilder";
import FilterPanel from "../components/filters/FilterPanel";
import SavedQueriesPanel from "../components/queries/SavedQueriesPanel";
import SaveQueryDialog from "../components/queries/SaveQueryDialog";

/**
 * DatasetExplorer.jsx - Space-Optimized Professional Data Exploration Interface
 * 
 * Layout improvements:
 * - Collapsible left sidebar for data sources
 * - Compact single-row header with inline stats
 * - Collapsible filter and query panels
 * - Maximized table/chart viewing area
 * - All original functionality preserved including column picker
 */

function cls(...classes) {
  return classes.filter(Boolean).join(" ");
}

// ============================================================================
// DATA SOURCES CONFIGURATION
// ============================================================================

const DATA_SOURCES = [
  // Financial Statements
  {
    category: "Financial Statements",
    sources: [
      { key: "financial", label: "All Financial Data", icon: Database, method: "financial", description: "Comprehensive financial panel" },
      { key: "is", label: "Income Statement", icon: TrendingUp, method: "incomeStatement", description: "Revenue, expenses, net income" },
      { key: "bs", label: "Balance Sheet", icon: DollarSign, method: "balanceSheet", description: "Assets, liabilities, equity" },
      { key: "cf", label: "Cash Flow", icon: BarChart3, method: "cashFlow", description: "Operating, investing, financing" },
    ],
  },
  // Metrics & Ratios
  {
    category: "Metrics & Ratios",
    sources: [
      { key: "ratios", label: "Financial Ratios", icon: PieChart, method: "ratios", description: "P/E, ROE, debt ratios" },
      { key: "metrics", label: "Key Metrics", icon: LineChartIcon, method: "keyMetrics", description: "Market cap, margins, growth" },
      { key: "ev", label: "Enterprise Value", icon: DollarSign, method: "enterpriseValue", description: "EV calculations over time" },
    ],
  },
  // Market Data
  {
    category: "Market Data",
    sources: [
      { key: "daily", label: "Daily Prices", icon: LineChartIcon, method: "pricesDaily", description: "OHLC daily data" },
      { key: "monthly", label: "Monthly Prices", icon: BarChart3, method: "pricesMonthly", description: "Month-end prices" },
      { key: "sp500d", label: "S&P 500 Daily", icon: TrendingUp, method: "sp500Daily", description: "Index daily prices" },
      { key: "sp500m", label: "S&P 500 Monthly", icon: TrendingUp, method: "sp500Monthly", description: "Index monthly prices" },
    ],
  },
  // Ownership & Insider
  {
    category: "Ownership & Insider",
    sources: [
      { key: "institutional", label: "Institutional", icon: Briefcase, method: "institutional", description: "Institutional holdings" },
      { key: "insider", label: "Insider Trading", icon: Users, method: "insider", description: "Insider transactions" },
      { key: "insiderstat", label: "Insider Stats", icon: Users, method: "insiderStats", description: "Aggregated statistics" },
    ],
  },
  // Company & Economic
  {
    category: "Company & Economic",
    sources: [
      { key: "profiles", label: "Company Profiles", icon: Briefcase, method: "profiles", description: "Company information" },
      { key: "employees", label: "Employee History", icon: Users, method: "employeeHistory", description: "Headcount over time" },
      { key: "economic", label: "Economic Indicators", icon: TrendingUp, method: "economic", description: "GDP, CPI, rates" },
    ],
  },
  // Analyst Coverage
  {
    category: "Analyst Coverage",
    sources: [
      { key: "analyst", label: "Analyst Estimates", icon: BarChart3, method: "analystEstimates", description: "Revenue/earnings estimates" },
      { key: "targets", label: "Price Targets", icon: TrendingUp, method: "analystTargets", description: "Price target consensus" },
      { key: "coverage", label: "Analyst Coverage", icon: Users, method: "analystCoverage", description: "Coverage summary & statistics" },
    ],
  },
];

// Flatten for easy lookup
const DATA_SOURCE_MAP = {};
DATA_SOURCES.forEach(category => {
  category.sources.forEach(source => {
    DATA_SOURCE_MAP[source.key] = source;
  });
});

// ============================================================================
// OPERATOR MAPPING (Frontend ↔ Backend)
// ============================================================================

const OPERATOR_MAP_TO_BACKEND = {
  'contains': 'contains',
  'equals': 'eq',
  'startsWith': 'contains',
  'endsWith': 'contains',
  'notContains': 'ne',
  'gt': 'gt',
  'gte': 'gte',
  'lt': 'lt',
  'lte': 'lte',
  'between': 'between',
  'before': 'lt',
  'after': 'gt',
  'notEquals': 'ne'
};

// ============================================================================
// COMPACT DATA SOURCE PICKER (COLLAPSIBLE SIDEBAR)
// ============================================================================

function DataSourcePicker({ activeSource, onSelect, isCollapsed, onToggle }) {
  const [expandedCategory, setExpandedCategory] = useState(DATA_SOURCES[0].category);

  return (
    <div className={cls(
      "h-full bg-white border-r border-slate-200 transition-all duration-300 flex flex-col",
      isCollapsed ? "w-12" : "w-64"
    )}>
      {/* Collapse Toggle */}
      <div className="p-2 border-b border-slate-200 flex items-center justify-between">
        {!isCollapsed && <span className="text-xs font-semibold text-slate-700 px-2">DATA SOURCES</span>}
        <button
          onClick={onToggle}
          className="p-1.5 rounded hover:bg-slate-100 transition-colors"
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4 text-slate-600" /> : <ChevronLeft className="w-4 h-4 text-slate-600" />}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {isCollapsed ? (
          // Collapsed: Show icons only
          <div className="p-1 space-y-1">
            {DATA_SOURCES.flatMap(category => category.sources).map(source => {
              const Icon = source.icon;
              const isActive = activeSource === source.key;
              return (
                <button
                  key={source.key}
                  onClick={() => onSelect(source.key)}
                  className={cls(
                    "w-full p-2 rounded transition-colors",
                    isActive ? "bg-black text-white" : "text-slate-600 hover:bg-slate-100"
                  )}
                  title={source.label}
                >
                  <Icon className="w-4 h-4 mx-auto" />
                </button>
              );
            })}
          </div>
        ) : (
          // Expanded: Show full categories
          <div className="p-2 space-y-1">
            {DATA_SOURCES.map((category) => (
              <div key={category.category} className="rounded-lg border border-slate-200 overflow-hidden">
                {/* Category Header */}
                <button
                  onClick={() => setExpandedCategory(expandedCategory === category.category ? null : category.category)}
                  className="w-full px-2 py-1.5 flex items-center justify-between bg-slate-50 hover:bg-slate-100 transition-colors"
                >
                  <span className="font-medium text-slate-900 text-xs">{category.category}</span>
                  <ChevronDown
                    className={cls(
                      "w-3 h-3 text-slate-700 transition-transform",
                      expandedCategory === category.category && "rotate-180"
                    )}
                  />
                </button>

                {/* Sources */}
                {expandedCategory === category.category && (
                  <div className="p-1 space-y-0.5">
                    {category.sources.map((source) => {
                      const Icon = source.icon;
                      const isActive = activeSource === source.key;

                      return (
                        <button
                          key={source.key}
                          onClick={() => onSelect(source.key)}
                          className={cls(
                            "w-full px-2 py-1.5 rounded text-left transition-all",
                            isActive
                              ? "bg-black text-white"
                              : "hover:bg-slate-50 text-slate-700"
                          )}
                        >
                          <div className="flex items-start gap-1.5">
                            <Icon className={cls("w-3 h-3 flex-shrink-0 mt-0.5", isActive ? "text-white" : "text-slate-500")} />
                            <div className="flex-1 min-w-0">
                              <div className={cls("text-xs font-medium", isActive ? "text-white" : "text-slate-900")}>
                                {source.label}
                              </div>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// COMPACT STATS BADGES
// ============================================================================

function StatsBadge({ label, value, icon: Icon }) {
  return (
    <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-slate-100 border border-slate-200">
      <Icon className="w-3 h-3 text-slate-600" />
      <span className="text-xs text-slate-700">
        <span className="font-semibold">{value}</span> {label}
      </span>
    </div>
  );
}

// ============================================================================
// FULL DATA TABLE COMPONENT WITH SEARCH
// ============================================================================

function DataTable({ data, columns }) {
  const [sortKey, setSortKey] = useState(null);
  const [sortOrder, setSortOrder] = useState("asc");
  const [searchQuery, setSearchQuery] = useState("");

  // Filter data by search
  const filteredData = useMemo(() => {
    if (!searchQuery) return data;

    const query = searchQuery.toLowerCase();
    return data.filter(row => {
      return Object.values(row).some(value => 
        String(value).toLowerCase().includes(query)
      );
    });
  }, [data, searchQuery]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortKey) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      // Handle null/undefined
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return sortOrder === "asc" ? 1 : -1;
      if (bVal == null) return sortOrder === "asc" ? -1 : 1;

      // Compare
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
      }

      const aStr = String(aVal);
      const bStr = String(bVal);
      return sortOrder === "asc" 
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr);
    });
  }, [filteredData, sortKey, sortOrder]);

  const handleSort = (column) => {
    if (sortKey === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortKey(column);
      setSortOrder("asc");
    }
  };

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        <Database className="w-12 h-12 mx-auto mb-3 text-slate-300" />
        <div>No data to display</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search data..."
          className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-black/10 text-sm"
        />
      </div>

      {/* Table */}
      <div className="rounded-lg border border-slate-200 overflow-hidden bg-white">
        <div className="overflow-x-auto relative" style={{ maxHeight: 'calc(100vh - 200px)' }}>
          <table className="w-full text-sm">
            <thead className="bg-slate-100 border-b-2 border-slate-300 sticky top-0 z-10 shadow-sm">
              <tr>
                {columns.map((column) => {
                  const isNumeric = isNumericColumn(data, column);
                  return (
                    <th
                      key={column}
                      onClick={() => handleSort(column)}
                      className={cls(
                        "px-3 py-2 font-semibold text-slate-900 cursor-pointer hover:bg-slate-200 transition-colors",
                        "min-w-[100px] max-w-[200px]",
                        "bg-slate-100", // Ensure background stays solid when scrolling
                        isNumeric ? "text-right" : "text-left"
                      )}
                      title={column}
                    >
                      <div className={cls(
                        "flex items-center gap-2",
                        isNumeric ? "justify-end" : "justify-start"
                      )}>
                        <span className="truncate text-xs">{column}</span>
                        {sortKey === column && (
                          <span className="text-slate-600 flex-shrink-0">
                            {sortOrder === "asc" ? "↑" : "↓"}
                          </span>
                        )}
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedData.map((row, idx) => (
                <tr key={idx} className={cls(
                  "hover:bg-blue-50 transition-colors",
                  idx % 2 === 0 ? "bg-white" : "bg-slate-50"
                )}>
                  {columns.map((column) => {
                    const isNumeric = typeof row[column] === "number";
                    return (
                      <td 
                        key={column} 
                        className={cls(
                          "px-3 py-2 text-slate-700 text-xs",
                          isNumeric ? "text-right tabular-nums" : "text-left"
                        )}
                      >
                        {formatValue(row[column], column)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Results info */}
      <div className="text-xs text-slate-500 text-center">
        Showing {sortedData.length} of {data.length} rows
      </div>
    </div>
  );
}

// ============================================================================
// STATS CARD COMPONENT (for mobile fallback)
// ============================================================================

function StatsCard({ label, value, icon: Icon, color = "slate" }) {
  const colors = {
    slate: "bg-slate-50 text-slate-700 border-slate-200",
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-200",
  };

  return (
    <div className={cls("rounded-lg border p-3", colors[color])}>
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4" />
        <div>
          <div className="text-xs font-medium opacity-75">{label}</div>
          <div className="text-lg font-bold mt-0.5">{value}</div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function DatasetExplorer() {
  const { id: datasetId } = useParams();
  const navigate = useNavigate();

  // Dataset state
  const [dataset, setDataset] = useState(null);
  const [datasetLoading, setDatasetLoading] = useState(true);
  const [datasetError, setDatasetError] = useState(null);

  // Data source state
  const [activeSource, setActiveSource] = useState("financial");
  const [data, setData] = useState(null);
  const [columns, setColumns] = useState([]);
  const [dataLoading, setDataLoading] = useState(false);
  const [dataError, setDataError] = useState(null);

  // Filter & query state
  const [filteredData, setFilteredData] = useState(null);
  const [activeQueryId, setActiveQueryId] = useState(null);
  const [savedQueries, setSavedQueries] = useState([]);
  
  // Structured query state for backend
  const [currentQuery, setCurrentQuery] = useState({
    filters: [],
    columns: null,
    companies: null,
    years: null,
    sort_by: null,
    sort_order: "asc",
    limit: null,
    offset: 0
  });

  // UI state
  const [viewMode, setViewMode] = useState("table");
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [filtersPanelOpen, setFiltersPanelOpen] = useState(false);
  const [queriesPanelOpen, setQueriesPanelOpen] = useState(false);

  // Compute stats
  const stats = useMemo(() => {
    if (!data || !Array.isArray(data)) return null;

    const displayData = filteredData || data;
    const companies = new Set();
    displayData.forEach(row => {
      const identifier = row.Symbol || row.symbol || row.Company || row.company;
      if (identifier) companies.add(identifier);
    });

    return {
      totalRows: displayData.length,
      totalColumns: columns.length,
      companies: companies.size || "—",
    };
  }, [data, filteredData, columns]);

  // Load dataset info
  useEffect(() => {
    const loadDataset = async () => {
      try {
        setDatasetLoading(true);
        setDatasetError(null);
        const response = await datasetsAPI.get(datasetId);
        setDataset(response.data);
      } catch (err) {
        setDatasetError(formatError(err));
      } finally {
        setDatasetLoading(false);
      }
    };
    loadDataset();
  }, [datasetId]);

  // Load data when source changes
  useEffect(() => {
    const loadData = async () => {
      if (dataset?.status !== "ready") return;
      
      try {
        setDataLoading(true);
        setDataError(null);
        setFilteredData(null);
        setActiveQueryId(null);
        
        setCurrentQuery({
          filters: [],
          columns: null,
          companies: null,
          years: null,
          sort_by: null,
          sort_order: "asc",
          limit: null,
          offset: 0
        });

        const sourceConfig = DATA_SOURCE_MAP[activeSource];
        if (!sourceConfig) {
          throw new Error("Invalid data source");
        }

        const response = await datasetsAPI.getData[sourceConfig.method](datasetId);
        const result = response.data;
        
        if (result && result.data) {
          setData(result.data);
          setColumns(result.columns || []);
        } else if (Array.isArray(result)) {
          setData(result);
          setColumns(result.length > 0 ? Object.keys(result[0]) : []);
        } else {
          throw new Error("Unexpected data format");
        }
      } catch (err) {
        setDataError(formatError(err));
        setData(null);
        setColumns([]);
      } finally {
        setDataLoading(false);
      }
    };
    loadData();
  }, [activeSource, dataset?.status, datasetId]);

  // Load saved queries when data source changes
  useEffect(() => {
    const loadQueries = async () => {
      if (!activeSource) return;
      try {
        const response = await queriesAPI.list({ 
          data_source: activeSource,
          include_public: true 
        });
        setSavedQueries(response.data || []);
      } catch (err) {
        console.error('Failed to load queries:', err);
      }
    };
    loadQueries();
  }, [activeSource]);

  // Manual data reload
  const loadDataManually = async () => {
    setDataLoading(true);
    setDataError(null);
    setFilteredData(null);
    setActiveQueryId(null);

    try {
      setCurrentQuery({
        filters: [],
        columns: null,
        companies: null,
        years: null,
        sort_by: null,
        sort_order: "asc",
        limit: null,
        offset: 0
      });

      const sourceConfig = DATA_SOURCE_MAP[activeSource];
      if (!sourceConfig) {
        throw new Error("Invalid data source");
      }

      const response = await datasetsAPI.getData[sourceConfig.method](datasetId);
      const result = response.data;
      
      if (result && result.data) {
        setData(result.data);
        setColumns(result.columns || []);
      } else if (Array.isArray(result)) {
        setData(result);
        setColumns(result.length > 0 ? Object.keys(result[0]) : []);
      } else {
        throw new Error("Unexpected data format");
      }
    } catch (err) {
      setDataError(formatError(err));
      setData(null);
      setColumns([]);
    } finally {
      setDataLoading(false);
    }
  };

  // Handle filter updates from FilterPanel
  const handleFilterUpdate = useCallback((filters, selectedColumns) => {
    // Convert FilterPanel format to backend query format
    const structuredFilters = filters
      .filter(f => f.column && f.value)
      .map(f => {
        const filter = {
          field: f.column,
          operator: OPERATOR_MAP_TO_BACKEND[f.operator] || 'eq',
          value: f.value
        };
        
        if (f.operator === 'between' && f.value2) {
          filter.value2 = f.value2;
        }
        
        return filter;
      });
    
    setCurrentQuery(prev => ({
      ...prev,
      filters: structuredFilters,
      columns: selectedColumns || prev.columns
    }));
  }, []);

  const handleSaveQuery = async (queryData) => {
    try {
      const payload = {
        ...queryData,
        data_source: activeSource,
        query_config: currentQuery
      };
      
      await queriesAPI.create(payload);
      setShowSaveDialog(false);
      
      // Refresh queries list
      const response = await queriesAPI.list({ 
        data_source: activeSource,
        include_public: true 
      });
      setSavedQueries(response.data || []);
      setQueriesPanelOpen(true);
    } catch (err) {
      alert("Failed to save query: " + formatError(err));
    }
  };

  const handleLoadQuery = async (query) => {
    try {
      const response = await queriesAPI.execute(query.query_id, datasetId);
      setFilteredData(response.data.data);
      setActiveQueryId(query.query_id);
      
      // Update currentQuery from loaded query
      setCurrentQuery(query.query_config || {
        filters: query.filters || [],
        columns: query.columns || null,
        companies: null,
        years: null,
        sort_by: null,
        sort_order: "asc",
        limit: null,
        offset: 0
      });
      
      setFiltersPanelOpen(false);
    } catch (err) {
      alert("Failed to load query: " + formatError(err));
    }
  };

  const handleExport = () => {
    const exportData = filteredData || data;
    if (!exportData) return;

    const exportColumns = currentQuery.columns && currentQuery.columns.length > 0 
      ? currentQuery.columns 
      : columns;

    const csv = [
      exportColumns.join(","),
      ...exportData.map(row => 
        exportColumns.map(col => JSON.stringify(row[col] ?? "")).join(",")
      )
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${activeSource}_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (datasetLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
      </div>
    );
  }

  if (datasetError) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-rose-500 mx-auto mb-3" />
          <div className="text-slate-900 font-medium mb-1">Failed to load dataset</div>
          <div className="text-sm text-slate-700">{datasetError}</div>
        </div>
      </div>
    );
  }

  const sourceInfo = DATA_SOURCE_MAP[activeSource];

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      {/* Top Header Bar */}
      <header className="bg-white border-b border-slate-200 px-4 py-2.5">
        <div className="flex items-center justify-between gap-4">
          {/* Left: Back + Title + Stats */}
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <button
              onClick={() => navigate("/datasets")}
              className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors flex-shrink-0"
              title="Back to Datasets"
            >
              <ArrowLeft className="w-4 h-4 text-slate-700" />
            </button>
            
            <div className="flex items-center gap-2 min-w-0">
              <div className="flex items-center gap-2 min-w-0">
                {sourceInfo && <sourceInfo.icon className="w-4 h-4 text-slate-700 flex-shrink-0" />}
                <div className="min-w-0">
                  <h1 className="text-sm font-semibold text-slate-900 truncate">
                    {sourceInfo?.label || activeSource}
                  </h1>
                </div>
              </div>
              
              {/* Inline Stats */}
              {stats && (
                <div className="hidden md:flex items-center gap-2 ml-2">
                  <StatsBadge label="rows" value={stats.totalRows.toLocaleString()} icon={Database} />
                  <StatsBadge label="cols" value={stats.totalColumns} icon={Grid3x3} />
                  <StatsBadge label="companies" value={stats.companies} icon={Briefcase} />
                </div>
              )}
            </div>
          </div>

          {/* Right: View Mode + Actions + Panel Toggles */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Filter Panel Toggle */}
            <button
              onClick={() => setFiltersPanelOpen(!filtersPanelOpen)}
              className={cls(
                "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors text-xs font-medium",
                filtersPanelOpen 
                  ? "bg-black text-white" 
                  : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
              )}
            >
              <FilterIcon className="w-3.5 h-3.5" />
              Filters
            </button>

            {/* Saved Queries Panel Toggle */}
            <button
              onClick={() => setQueriesPanelOpen(!queriesPanelOpen)}
              className={cls(
                "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors text-xs font-medium",
                queriesPanelOpen 
                  ? "bg-black text-white" 
                  : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
              )}
            >
              <BookmarkCheck className="w-3.5 h-3.5" />
              Saved Queries
            </button>

            {/* Save Query Button */}
            <button
              onClick={() => setShowSaveDialog(true)}
              disabled={!data || (currentQuery.filters.length === 0 && (!currentQuery.columns || currentQuery.columns.length === 0))}
              className={cls(
                "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors text-xs font-medium",
                "bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
              )}
              title="Save current query configuration"
            >
              <Save className="w-3.5 h-3.5" />
              Save Query
            </button>

            {/* View Mode */}
            <div className="flex items-center gap-0.5 border border-slate-200 rounded-lg p-0.5 bg-white">
              <button
                onClick={() => setViewMode("table")}
                className={cls(
                  "p-1.5 rounded transition-colors",
                  viewMode === "table" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-50"
                )}
                title="Table View"
              >
                <TableIcon className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setViewMode("chart")}
                className={cls(
                  "p-1.5 rounded transition-colors",
                  viewMode === "chart" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-50"
                )}
                title="Chart View"
              >
                <BarChart3 className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setViewMode("raw")}
                className={cls(
                  "p-1.5 rounded transition-colors",
                  viewMode === "raw" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-50"
                )}
                title="Raw JSON"
              >
                <Database className="w-3.5 h-3.5" />
              </button>
            </div>

            <button
              onClick={loadDataManually}
              disabled={dataLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-900 hover:bg-slate-50 transition-colors disabled:opacity-50 text-xs"
            >
              <RefreshCw className={cls("w-3.5 h-3.5", dataLoading && "animate-spin")} />
              Refresh
            </button>

            <button
              onClick={handleExport}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-black text-white hover:bg-black/90 transition-colors text-xs"
            >
              <Download className="w-3.5 h-3.5" />
              Export
            </button>
          </div>
        </div>

        {/* Mobile Stats (shown below header on mobile) */}
        {stats && (
          <div className="md:hidden mt-3 grid grid-cols-3 gap-2">
            <StatsCard label="Rows" value={stats.totalRows.toLocaleString()} icon={Database} color="slate" />
            <StatsCard label="Columns" value={stats.totalColumns} icon={Grid3x3} color="emerald" />
            <StatsCard label="Companies" value={stats.companies} icon={Briefcase} color="blue" />
          </div>
        )}
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Data Sources */}
        <DataSourcePicker
          activeSource={activeSource}
          onSelect={setActiveSource}
          isCollapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Collapsible Panels */}
          {(filtersPanelOpen || queriesPanelOpen) && (
            <div className="border-b border-slate-200 bg-white p-3 space-y-3">
              {/* Filter Panel */}
              {filtersPanelOpen && !activeQueryId && Array.isArray(data) && (
                <div className="space-y-2">
                  {/* Column selection status indicator */}
                  {currentQuery.columns && currentQuery.columns.length > 0 && currentQuery.columns.length < columns.length && (
                    <div className="px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center gap-2 text-xs">
                        <Grid3x3 className="w-3.5 h-3.5 text-blue-700" />
                        <span className="text-blue-900 font-medium">
                          {currentQuery.columns.length} of {columns.length} columns selected
                        </span>
                        <button
                          onClick={() => setCurrentQuery(prev => ({ ...prev, columns: null }))}
                          className="ml-auto text-blue-700 hover:text-blue-900 underline"
                        >
                          Show all columns
                        </button>
                      </div>
                    </div>
                  )}
                  
                  <FilterPanel
                    data={data}
                    columns={columns}
                    onFilter={setFilteredData}
                    onFilterUpdate={handleFilterUpdate}
                  />
                </div>
              )}

              {/* Saved Query Active Indicator */}
              {filtersPanelOpen && activeQueryId && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-blue-900">📊 Saved query active</span>
                      <span className="text-xs text-blue-700">Viewing filtered data</span>
                    </div>
                    <button 
                      onClick={() => {
                        setActiveQueryId(null);
                        setFilteredData(null);
                        loadDataManually();
                      }}
                      className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors text-xs font-medium"
                    >
                      Clear & Set Filters
                    </button>
                  </div>
                </div>
              )}

              {/* Saved Queries Panel */}
              {queriesPanelOpen && dataset?.status === "ready" && (
                <SavedQueriesPanel
                  dataSource={activeSource}
                  savedQueries={savedQueries}
                  activeQueryId={activeQueryId}
                  onLoadQuery={handleLoadQuery}
                />
              )}
            </div>
          )}

          {/* Data Display Area */}
          <div className="flex-1 overflow-auto p-4">
            {dataLoading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
              </div>
            ) : dataError ? (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-rose-500 mx-auto mb-3" />
                <div className="text-slate-900 font-medium mb-1">Failed to load data</div>
                <div className="text-sm text-slate-700">{dataError}</div>
              </div>
            ) : !data ? (
              <div className="text-center py-12 text-slate-500">
                <Database className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <div>No data available</div>
              </div>
            ) : (
              <>
                {/* Data Display */}
                {viewMode === "table" && Array.isArray(data) && (
                  <DataTable 
                    data={filteredData || data} 
                    columns={currentQuery.columns && currentQuery.columns.length > 0 ? currentQuery.columns : columns} 
                  />
                )}

                {viewMode === "chart" && Array.isArray(data) && (
                  <ChartBuilder 
                    data={filteredData || data} 
                    columns={currentQuery.columns && currentQuery.columns.length > 0 ? currentQuery.columns : columns} 
                  />
                )}

                {viewMode === "raw" && (
                  <div className="rounded-lg border border-slate-200 bg-slate-900 p-4 overflow-auto">
                    <pre className="text-xs text-slate-100 font-mono">
                      {JSON.stringify(data, null, 2)}
                    </pre>
                  </div>
                )}
              </>
            )}
          </div>
        </main>
      </div>

      {/* Save Query Dialog */}
      {showSaveDialog && (
        <SaveQueryDialog
          onSave={handleSaveQuery}
          onClose={() => setShowSaveDialog(false)}
          dataSource={activeSource}
          currentQuery={currentQuery}
          hasFilters={currentQuery.filters.length > 0}
        />
      )}
    </div>
  );
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatValue(value, columnName = '') {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    // Don't format year/date columns
    const isYearOrDate = columnName && (
      columnName.toLowerCase().includes('year') ||
      columnName.toLowerCase().includes('date') ||
      (value >= 1900 && value <= 2100 && Number.isInteger(value))
    );
    
    if (isYearOrDate) {
      return value.toString();
    }
    
    // Format large numbers with K, M, B suffixes
    const absValue = Math.abs(value);
    if (absValue >= 1e9) {
      return (value / 1e9).toFixed(2) + "B";
    } else if (absValue >= 1e6) {
      return (value / 1e6).toFixed(2) + "M";
    } else if (absValue >= 1e3) {
      return (value / 1e3).toFixed(2) + "K";
    } else if (Number.isInteger(value)) {
      return value.toLocaleString();
    } else {
      return value.toFixed(2);
    }
  }
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}

function isNumericColumn(data, column) {
  // Check if column contains mostly numbers
  const sample = data.slice(0, 100);
  const numericCount = sample.filter(row => typeof row[column] === "number").length;
  return numericCount > sample.length * 0.5;
}