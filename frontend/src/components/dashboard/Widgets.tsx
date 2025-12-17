import React, { useState, useEffect, useCallback, useMemo, ReactNode } from "react";
import { BarChart3, Table as TableIcon, TrendingUp, FileText, Settings, Maximize2, RefreshCw, AlertCircle, LucideIcon } from "lucide-react";
import { datasetsAPI, formatError } from "../../services/api";
import ChartBuilder from "../charts/ChartBuilder";

// ============================================================================
// Types
// ============================================================================

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
}

interface WidgetProps {
  id: string;
  title: string;
  config: WidgetConfig;
  onConfigChange?: (id: string) => void;
  onRemove: (id: string) => void;
  isEditing: boolean;
}

interface WidgetWrapperProps {
  title: string;
  icon: LucideIcon;
  onConfigure: () => void;
  onRemove: () => void;
  isEditing: boolean;
  children: ReactNode;
  error?: string | null;
}

// ============================================================================
// WIDGET WRAPPER (Common UI for all widgets)
// ============================================================================

function WidgetWrapper({ title, icon: Icon, onConfigure, onRemove, isEditing, children, error }: WidgetWrapperProps): React.ReactElement {
  return (
    <div className="h-full flex flex-col bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between gap-2 px-4 py-3 border-b border-slate-200 bg-slate-50 react-grid-item-static">
        <div className="flex items-center gap-2 min-w-0 drag-handle">
          <Icon className="w-4 h-4 text-slate-600 flex-shrink-0" />
          <h3 className="font-medium text-slate-900 truncate">{title}</h3>
        </div>

        {isEditing && (
          <div className="flex items-center gap-1">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onConfigure();
              }}
              className="p-1.5 rounded hover:bg-slate-200 text-slate-600 transition-colors"
              title="Configure"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove();
              }}
              className="p-1.5 rounded hover:bg-rose-100 text-rose-600 transition-colors"
              title="Remove"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {error ? (
          <div className="flex items-center justify-center h-full text-rose-600">
            <div className="text-center">
              <AlertCircle className="w-8 h-8 mx-auto mb-2" />
              <div className="text-sm">{error}</div>
            </div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}

// ============================================================================
// CHART WIDGET
// ============================================================================

export function ChartWidget({ id, title, config, onConfigChange, onRemove, isEditing }: WidgetProps): React.ReactElement {
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!config.datasetId || !config.dataSource) return;

    setLoading(true);
    setError(null);

    try {
      const method = config.dataSource as keyof typeof datasetsAPI.getData;
      if (datasetsAPI.getData[method]) {
        const response = await datasetsAPI.getData[method](config.datasetId);
        const responseData = response.data as { data?: Record<string, unknown>[] };
        setData(responseData.data || null);
      }
    } catch (e) {
      setError(formatError(e as { response?: { data?: { detail?: string; message?: string } }; message?: string }));
    } finally {
      setLoading(false);
    }
  }, [config.datasetId, config.dataSource]);

  useEffect(() => {
    if (config.datasetId && config.dataSource) {
      loadData();
    }
  }, [config.datasetId, config.dataSource, loadData]);

  const handleConfigure = () => {
    if (onConfigChange) {
      onConfigChange(id);
    }
  };

  return (
    <WidgetWrapper
      title={title}
      icon={BarChart3}
      onConfigure={handleConfigure}
      onRemove={() => onRemove(id)}
      isEditing={isEditing}
      error={error}
    >
      {loading ? (
        <div className="flex items-center justify-center h-full">
          <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
        </div>
      ) : !config.datasetId ? (
        <div className="flex items-center justify-center h-full text-slate-500">
          <div className="text-center">
            <Settings className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <div className="text-sm">Click configure to set up this chart</div>
          </div>
        </div>
      ) : data && Array.isArray(data) && data.length > 0 ? (
        <ChartBuilder
          data={data}
          columns={Object.keys(data[0])}
        />
      ) : (
        <div className="flex items-center justify-center h-full text-slate-500">
          No data available
        </div>
      )}
    </WidgetWrapper>
  );
}

// ============================================================================
// TABLE WIDGET
// ============================================================================

export function TableWidget({ id, title, config, onConfigChange, onRemove, isEditing }: WidgetProps): React.ReactElement {
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!config.datasetId || !config.dataSource) return;

    setLoading(true);
    setError(null);

    try {
      const method = config.dataSource as keyof typeof datasetsAPI.getData;
      if (datasetsAPI.getData[method]) {
        const response = await datasetsAPI.getData[method](config.datasetId);
        const responseData = response.data as { data?: Record<string, unknown>[] };
        setData(responseData.data || null);
      }
    } catch (e) {
      setError(formatError(e as { response?: { data?: { detail?: string; message?: string } }; message?: string }));
    } finally {
      setLoading(false);
    }
  }, [config.datasetId, config.dataSource]);

  useEffect(() => {
    if (config.datasetId && config.dataSource) {
      loadData();
    }
  }, [config.datasetId, config.dataSource, loadData]);

  const handleConfigure = () => {
    if (onConfigChange) {
      onConfigChange(id);
    }
  };

  const columns = data && data.length > 0 ? Object.keys(data[0]) : [];
  const displayData = data ? data.slice(0, config.rowLimit || 50) : [];

  return (
    <WidgetWrapper
      title={title}
      icon={TableIcon}
      onConfigure={handleConfigure}
      onRemove={() => onRemove(id)}
      isEditing={isEditing}
      error={error}
    >
      {loading ? (
        <div className="flex items-center justify-center h-full">
          <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
        </div>
      ) : !config.datasetId ? (
        <div className="flex items-center justify-center h-full text-slate-500">
          <div className="text-center">
            <Settings className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <div className="text-sm">Click configure to set up this table</div>
          </div>
        </div>
      ) : displayData.length > 0 ? (
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 sticky top-0">
              <tr>
                {columns.map(col => (
                  <th key={col} className="px-3 py-2 text-left text-xs font-medium text-slate-600 border-b border-slate-200">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {displayData.map((row, idx) => (
                <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                  {columns.map(col => (
                    <td key={col} className="px-3 py-2 text-slate-700">
                      {formatValue(row[col])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {data && data.length > displayData.length && (
            <div className="text-xs text-slate-500 text-center py-2 border-t border-slate-200">
              Showing {displayData.length} of {data.length} rows
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-center h-full text-slate-500">
          No data available
        </div>
      )}
    </WidgetWrapper>
  );
}

// ============================================================================
// STATS WIDGET
// ============================================================================

export function StatsWidget({ id, title, config, onConfigChange, onRemove, isEditing }: WidgetProps): React.ReactElement {
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!config.datasetId || !config.dataSource) return;

    setLoading(true);
    setError(null);

    try {
      const method = config.dataSource as keyof typeof datasetsAPI.getData;
      if (datasetsAPI.getData[method]) {
        const response = await datasetsAPI.getData[method](config.datasetId);
        const responseData = response.data as { data?: Record<string, unknown>[] };
        setData(responseData.data || null);
      }
    } catch (e) {
      setError(formatError(e as { response?: { data?: { detail?: string; message?: string } }; message?: string }));
    } finally {
      setLoading(false);
    }
  }, [config.datasetId, config.dataSource]);

  useEffect(() => {
    if (config.datasetId && config.dataSource) {
      loadData();
    }
  }, [config.datasetId, config.dataSource, config.metric, loadData]);

  const handleConfigure = () => {
    if (onConfigChange) {
      onConfigChange(id);
    }
  };

  // Calculate stat value
  const statValue = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0 || !config.metric) {
      return null;
    }

    const metric = config.metric;
    const aggregation = config.aggregation || "latest";

    const values = data
      .map(row => row[metric])
      .filter((v): v is number => typeof v === "number" && !isNaN(v));

    if (values.length === 0) return null;

    switch (aggregation) {
      case "sum":
        return values.reduce((a, b) => a + b, 0);
      case "avg":
        return values.reduce((a, b) => a + b, 0) / values.length;
      case "max":
        return Math.max(...values);
      case "min":
        return Math.min(...values);
      case "latest":
      default:
        return values[values.length - 1];
    }
  }, [data, config.metric, config.aggregation]);

  return (
    <WidgetWrapper
      title={title}
      icon={TrendingUp}
      onConfigure={handleConfigure}
      onRemove={() => onRemove(id)}
      isEditing={isEditing}
      error={error}
    >
      {loading ? (
        <div className="flex items-center justify-center h-full">
          <RefreshCw className="w-8 h-8 text-slate-400 animate-spin" />
        </div>
      ) : !config.datasetId || !config.metric ? (
        <div className="flex items-center justify-center h-full text-slate-500">
          <div className="text-center">
            <Settings className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <div className="text-sm">Click configure to set up this stat</div>
          </div>
        </div>
      ) : statValue !== null ? (
        <div className="flex flex-col items-center justify-center h-full">
          <div className="text-4xl font-bold text-slate-900 mb-2">
            {formatValue(statValue)}
          </div>
          <div className="text-sm text-slate-600">
            {config.aggregation || "Latest"} {config.metric}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-full text-slate-500">
          No data available
        </div>
      )}
    </WidgetWrapper>
  );
}

// ============================================================================
// TEXT WIDGET
// ============================================================================

export function TextWidget({ id, title, config, onConfigChange, onRemove, isEditing }: WidgetProps): React.ReactElement {
  const handleConfigure = () => {
    if (onConfigChange) {
      onConfigChange(id);
    }
  };

  return (
    <WidgetWrapper
      title={title}
      icon={FileText}
      onConfigure={handleConfigure}
      onRemove={() => onRemove(id)}
      isEditing={isEditing}
    >
      {!config.content ? (
        <div className="flex items-center justify-center h-full text-slate-500">
          <div className="text-center">
            <Settings className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <div className="text-sm">Click configure to add text content</div>
          </div>
        </div>
      ) : (
        <div className="prose prose-sm max-w-none">
          <div className="text-slate-700 whitespace-pre-wrap">
            {config.content}
          </div>
        </div>
      )}
    </WidgetWrapper>
  );
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    if (Number.isInteger(value)) return value.toLocaleString();
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}
