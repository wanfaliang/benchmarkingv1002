import React, { useState, useEffect, useCallback, KeyboardEvent } from "react";
import { Settings as SettingsIcon, X, AlertCircle } from "lucide-react";
import { datasetsAPI } from "../../services/api";

// ============================================================================
// Types
// ============================================================================

interface DataSource {
  value: string;
  label: string;
  category: string;
}

interface Widget {
  id: string;
  type: 'chart' | 'table' | 'stats' | 'text';
  title: string;
  config: WidgetConfig;
}

interface WidgetConfig {
  dataMode?: 'tickers' | 'dataset';
  tickers?: string[];
  datasetId?: string;
  dataSource?: string;
  chartType?: string;
  xAxis?: string;
  yAxis?: string[];
  groupBy?: string;
  rowLimit?: number;
  metric?: string;
  aggregation?: string;
  content?: string;
  [key: string]: unknown;
}

interface Dataset {
  id: string;
  name: string;
  companies?: string[];
}

interface ConfigPanelProps {
  widget: Widget;
  onUpdate: (update: { title: string; config: WidgetConfig }) => void;
  onClose: () => void;
}

// ============================================================================
// Constants
// ============================================================================

// 19 Data Sources
const DATA_SOURCES: DataSource[] = [
  { value: "financial", label: "All Financial Data", category: "Core" },
  { value: "incomeStatements", label: "Income Statements", category: "Financials" },
  { value: "balanceSheets", label: "Balance Sheets", category: "Financials" },
  { value: "cashFlows", label: "Cash Flow Statements", category: "Financials" },
  { value: "ratios", label: "Financial Ratios", category: "Financials" },
  { value: "keyMetrics", label: "Key Metrics", category: "Financials" },
  { value: "daily", label: "Daily Prices", category: "Market Data" },
  { value: "monthly", label: "Monthly Prices", category: "Market Data" },
  { value: "enterpriseValues", label: "Enterprise Values", category: "Valuation" },
  { value: "profiles", label: "Company Profiles", category: "Company Info" },
  { value: "analystEstimates", label: "Analyst Estimates", category: "Analyst Coverage" },
  { value: "analystTargets", label: "Price Targets", category: "Analyst Coverage" },
  { value: "insiderTrading", label: "Insider Trading", category: "Ownership" },
  { value: "institutionalOwnership", label: "Institutional Ownership", category: "Ownership" },
  { value: "insiderStatistics", label: "Insider Statistics", category: "Ownership" },
  { value: "economic", label: "Economic Data (FRED)", category: "Macro" },
];

// Group by category
const DATA_SOURCE_GROUPS = DATA_SOURCES.reduce<Record<string, DataSource[]>>((acc, source) => {
  if (!acc[source.category]) acc[source.category] = [];
  acc[source.category].push(source);
  return acc;
}, {});

// ============================================================================
// Component
// ============================================================================

export default function ConfigPanel({ widget, onUpdate, onClose }: ConfigPanelProps): React.ReactElement {
  // Form state
  const [title, setTitle] = useState(widget.title);
  const [dataMode, setDataMode] = useState<'tickers' | 'dataset'>(widget.config.dataMode || "tickers");
  const [tickers, setTickers] = useState<string[]>(widget.config.tickers || []);
  const [tickerInput, setTickerInput] = useState("");
  const [datasetId, setDatasetId] = useState(widget.config.datasetId || "");
  const [dataSource, setDataSource] = useState(widget.config.dataSource || "financial");

  // Widget-specific state
  const [chartType, setChartType] = useState(widget.config.chartType || "line");
  const [xAxis] = useState(widget.config.xAxis || "");
  const [yAxis] = useState(widget.config.yAxis || []);
  const [groupBy] = useState(widget.config.groupBy || "");
  const [rowLimit, setRowLimit] = useState(widget.config.rowLimit || 50);
  const [metric, setMetric] = useState(widget.config.metric || "");
  const [aggregation, setAggregation] = useState(widget.config.aggregation || "latest");
  const [textContent, setTextContent] = useState(widget.config.content || "");

  // UI state
  const [availableDatasets, setAvailableDatasets] = useState<Dataset[]>([]);
  const [validationError, setValidationError] = useState("");
  const [, setPreviewColumns] = useState<string[]>([]);

  // Load available datasets
  useEffect(() => {
    loadDatasets();
  }, []);

  async function loadDatasets() {
    try {
      const response = await datasetsAPI.list();
      const data = response.data as { datasets?: Dataset[] } | Dataset[];
      if (Array.isArray(data)) {
        setAvailableDatasets(data);
      } else if (data.datasets) {
        setAvailableDatasets(data.datasets);
      }
    } catch (error) {
      console.error("Failed to load datasets:", error);
    }
  }

  const loadPreviewColumns = useCallback(async () => {
    try {
      if (dataMode === "dataset" && datasetId) {
        const dataSourceKey = dataSource as keyof typeof datasetsAPI.getData;
        if (datasetsAPI.getData[dataSourceKey]) {
          const response = await datasetsAPI.getData[dataSourceKey](datasetId);
          const responseData = response.data as { data?: Record<string, unknown>[] };
          if (responseData.data && responseData.data.length > 0) {
            setPreviewColumns(Object.keys(responseData.data[0]));
          }
        }
      }
    } catch (error) {
      console.error("Failed to load columns:", error);
    }
  }, [dataMode, datasetId, dataSource]);

  useEffect(() => {
    if (dataMode === "tickers" && tickers.length > 0 && dataSource) {
      loadPreviewColumns();
    } else if (dataMode === "dataset" && datasetId && dataSource) {
      loadPreviewColumns();
    }
  }, [dataMode, tickers, datasetId, dataSource, loadPreviewColumns]);

  // Handle ticker input
  const handleAddTicker = () => {
    const ticker = tickerInput.trim().toUpperCase();
    if (!ticker) return;

    if (!/^[A-Z]{1,5}$/.test(ticker)) {
      setValidationError("Invalid ticker format");
      return;
    }

    if (tickers.includes(ticker)) {
      setValidationError("Ticker already added");
      return;
    }

    setTickers([...tickers, ticker]);
    setTickerInput("");
    setValidationError("");
  };

  const handleRemoveTicker = (ticker: string) => {
    setTickers(tickers.filter(t => t !== ticker));
  };

  const handleTickerKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTicker();
    }
  };

  // Validation
  const validate = (): boolean => {
    if (!title.trim()) {
      setValidationError("Title is required");
      return false;
    }

    if (dataMode === "tickers" && tickers.length === 0) {
      setValidationError("Add at least one ticker");
      return false;
    }

    if (dataMode === "dataset" && !datasetId) {
      setValidationError("Select a dataset");
      return false;
    }

    if (!dataSource) {
      setValidationError("Select a data source");
      return false;
    }

    // Widget-specific validation
    if (widget.type === "chart") {
      if (!chartType) {
        setValidationError("Select chart type");
        return false;
      }
    }

    if (widget.type === "stats") {
      if (!metric) {
        setValidationError("Select a metric");
        return false;
      }
    }

    setValidationError("");
    return true;
  };

  // Save
  const handleSave = () => {
    if (!validate()) return;

    const config: WidgetConfig = {
      dataMode,
      tickers: dataMode === "tickers" ? tickers : undefined,
      datasetId: dataMode === "dataset" ? datasetId : undefined,
      dataSource,
    };

    // Add widget-specific config
    if (widget.type === "chart") {
      config.chartType = chartType;
      config.xAxis = xAxis;
      config.yAxis = yAxis;
      config.groupBy = groupBy;
    } else if (widget.type === "table") {
      config.rowLimit = rowLimit;
    } else if (widget.type === "stats") {
      config.metric = metric;
      config.aggregation = aggregation;
    } else if (widget.type === "text") {
      config.content = textContent;
    }

    onUpdate({ title, config });
    onClose();
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-slate-600" />
          <h3 className="font-semibold text-slate-900">Configure Widget</h3>
        </div>
        <button onClick={onClose} className="p-1 rounded hover:bg-slate-100">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Validation Error */}
        {validationError && (
          <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-rose-700">{validationError}</div>
          </div>
        )}

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Widget Title *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
            placeholder="Enter title..."
          />
        </div>

        {/* Data Mode */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">
            Data Source *
          </label>
          <div className="space-y-3">
            <label className="flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-colors hover:bg-slate-50"
              style={{ borderColor: dataMode === "tickers" ? "#000" : "#e2e8f0" }}>
              <input
                type="radio"
                checked={dataMode === "tickers"}
                onChange={() => setDataMode("tickers")}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="font-medium text-slate-900">Select Tickers</div>
                <div className="text-xs text-slate-600 mt-1">
                  Choose specific companies to analyze
                </div>
              </div>
            </label>

            <label className="flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-colors hover:bg-slate-50"
              style={{ borderColor: dataMode === "dataset" ? "#000" : "#e2e8f0" }}>
              <input
                type="radio"
                checked={dataMode === "dataset"}
                onChange={() => setDataMode("dataset")}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="font-medium text-slate-900">Use Existing Dataset</div>
                <div className="text-xs text-slate-600 mt-1">
                  Select from previously created datasets
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* Ticker Selection */}
        {dataMode === "tickers" && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Company Tickers *
            </label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={tickerInput}
                onChange={(e) => setTickerInput(e.target.value.toUpperCase())}
                onKeyPress={handleTickerKeyPress}
                placeholder="Enter ticker (e.g., AAPL)"
                className="flex-1 px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 placeholder:text-slate-400"
              />
              <button
                onClick={handleAddTicker}
                className="px-4 py-2 rounded-lg bg-black text-white hover:bg-black/90 transition-colors"
              >
                Add
              </button>
            </div>

            {/* Ticker Pills */}
            {tickers.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tickers.map(ticker => (
                  <span
                    key={ticker}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-slate-900 text-white text-sm"
                  >
                    {ticker}
                    <button
                      onClick={() => handleRemoveTicker(ticker)}
                      className="hover:bg-white/20 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Dataset Selection */}
        {dataMode === "dataset" && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Select Dataset *
            </label>
            <select
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
            >
              <option value="">Choose dataset...</option>
              {availableDatasets.map(ds => (
                <option key={ds.id} value={ds.id}>
                  {ds.name} ({ds.companies?.length || 0} companies)
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Data Type (19 Sources) */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Data Type *
          </label>
          <select
            value={dataSource}
            onChange={(e) => setDataSource(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
          >
            {Object.entries(DATA_SOURCE_GROUPS).map(([category, sources]) => (
              <optgroup key={category} label={category}>
                {sources.map(source => (
                  <option key={source.value} value={source.value}>
                    {source.label}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {/* Widget-Specific Config */}
        <div className="pt-4 border-t border-slate-200">
          <div className="text-sm font-medium text-slate-700 mb-4">
            {widget.type.charAt(0).toUpperCase() + widget.type.slice(1)} Settings
          </div>

          {/* CHART CONFIG */}
          {widget.type === "chart" && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-700 mb-2">Chart Type</label>
                <select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
                >
                  <option value="line">Line Chart</option>
                  <option value="bar">Bar Chart</option>
                  <option value="area">Area Chart</option>
                  <option value="scatter">Scatter Plot</option>
                </select>
              </div>

              <div className="text-xs text-slate-500">
                Note: X-axis, Y-axis, and grouping will be auto-configured based on available data columns
              </div>
            </div>
          )}

          {/* TABLE CONFIG */}
          {widget.type === "table" && (
            <div>
              <label className="block text-sm text-slate-700 mb-2">Row Limit</label>
              <input
                type="number"
                value={rowLimit}
                onChange={(e) => setRowLimit(parseInt(e.target.value))}
                min={10}
                max={1000}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
              />
            </div>
          )}

          {/* STATS CONFIG */}
          {widget.type === "stats" && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-700 mb-2">Metric *</label>
                <input
                  type="text"
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                  placeholder="e.g., revenue, netIncome, totalAssets"
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 placeholder:text-slate-400"
                />
              </div>

              <div>
                <label className="block text-sm text-slate-700 mb-2">Aggregation</label>
                <select
                  value={aggregation}
                  onChange={(e) => setAggregation(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
                >
                  <option value="latest">Latest</option>
                  <option value="sum">Sum</option>
                  <option value="avg">Average</option>
                  <option value="max">Maximum</option>
                  <option value="min">Minimum</option>
                </select>
              </div>
            </div>
          )}

          {/* TEXT CONFIG */}
          {widget.type === "text" && (
            <div>
              <label className="block text-sm text-slate-700 mb-2">Content</label>
              <textarea
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                rows={6}
                placeholder="Enter text content..."
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 placeholder:text-slate-400"
              />
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-200 flex items-center gap-2">
        <button
          onClick={onClose}
          className="flex-1 px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors text-slate-700"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          className="flex-1 px-4 py-2 rounded-xl bg-black text-white hover:bg-black/90 transition-colors"
        >
          Save Configuration
        </button>
      </div>
    </div>
  );
}
