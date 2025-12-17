import React, { useState, useMemo, useEffect } from "react";
import {
  LineChart,
  BarChart3,
  ScatterChart as ScatterIcon,
  AreaChart as AreaIcon,
  Download,
  Settings,
  Maximize2,
  X,
} from "lucide-react";
import LineChartView from "./LineChartView";
import BarChartView from "./BarChartView";
import ScatterChartView from "./ScatterChartView";
import AreaChartView from "./AreaChartView";

function cls(...classes: (string | boolean | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

// ============================================================================
// Types
// ============================================================================

interface ChartBuilderProps {
  data: Record<string, unknown>[];
  columns: string[];
}

interface ChartType {
  key: string;
  label: string;
  icon: React.FC<{ className?: string }>;
  component: React.FC<{
    data: Record<string, unknown>[];
    xAxis: string;
    yAxis: string[];
    groupBy?: string;
    showLegend?: boolean;
    showGrid?: boolean;
  }>;
}

// ============================================================================
// CHART TYPE CONFIGURATION
// ============================================================================

const CHART_TYPES: ChartType[] = [
  { key: "line", label: "Line Chart", icon: LineChart, component: LineChartView },
  { key: "bar", label: "Bar Chart", icon: BarChart3, component: BarChartView },
  { key: "scatter", label: "Scatter Plot", icon: ScatterIcon, component: ScatterChartView },
  { key: "area", label: "Area Chart", icon: AreaIcon, component: AreaChartView },
];

// ============================================================================
// CHART BUILDER COMPONENT
// ============================================================================

export default function ChartBuilder({ data, columns }: ChartBuilderProps): React.ReactElement {
  // Chart configuration
  const [chartType, setChartType] = useState("line");
  const [xAxis, setXAxis] = useState("");
  const [yAxis, setYAxis] = useState<string[]>([]);
  const [groupBy, setGroupBy] = useState("");
  const [showLegend, setShowLegend] = useState(true);
  const [showGrid, setShowGrid] = useState(true);

  // UI state
  const [showConfig, setShowConfig] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);

  // Get numeric and date columns
  const { numericColumns, dateColumns, textColumns } = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return { numericColumns: [] as string[], dateColumns: [] as string[], textColumns: [] as string[] };
    }

    const sample = data[0];
    const numeric: string[] = [];
    const dates: string[] = [];
    const text: string[] = [];

    columns.forEach(col => {
      const value = sample[col];
      if (value === null || value === undefined) return;

      // Check if date
      if (col.toLowerCase().includes('date') || col.toLowerCase().includes('year')) {
        dates.push(col);
      }
      // Check if numeric
      else if (typeof value === 'number') {
        numeric.push(col);
      }
      // Text
      else {
        text.push(col);
      }
    });

    return { numericColumns: numeric, dateColumns: dates, textColumns: text };
  }, [data, columns]);

  // Auto-select axes on mount
  useEffect(() => {
    if (!xAxis && dateColumns.length > 0) {
      setXAxis(dateColumns[0]);
    }
    if (yAxis.length === 0 && numericColumns.length > 0) {
      setYAxis([numericColumns[0]]);
    }
    if (!groupBy && textColumns.length > 0) {
      // Auto-select Symbol or Company for grouping
      const symbolCol = textColumns.find(c => c.toLowerCase() === 'symbol' || c.toLowerCase() === 'company');
      if (symbolCol) setGroupBy(symbolCol);
    }
  }, [dateColumns, numericColumns, textColumns, xAxis, yAxis.length, groupBy]);

  // Toggle Y-axis selection
  const toggleYAxis = (col: string) => {
    setYAxis(prev =>
      prev.includes(col)
        ? prev.filter(c => c !== col)
        : [...prev, col]
    );
  };

  // Get chart component
  const ChartComponent = CHART_TYPES.find(t => t.key === chartType)?.component;

  // Export chart
  const handleExport = () => {
    // This will be implemented in ChartExport.jsx
    console.log("Export chart");
  };

  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
        <BarChart3 className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <div className="text-slate-900 font-medium mb-2">No data to visualize</div>
        <div className="text-sm text-slate-600">
          Select a data source with numeric values to create charts
        </div>
      </div>
    );
  }

  return (
    <div className={cls(
      "rounded-xl border border-slate-200 bg-white overflow-hidden",
      fullscreen && "fixed inset-4 z-50 flex flex-col"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between gap-4 p-4 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-5 h-5 text-slate-600" />
          <h3 className="font-semibold text-slate-900">Chart Builder</h3>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className={cls(
              "inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors",
              showConfig ? "bg-slate-900 text-white" : "bg-white border border-slate-200 text-slate-700 hover:bg-slate-50"
            )}
          >
            <Settings className="w-4 h-4" />
            Configure
          </button>
          <button
            onClick={handleExport}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors text-sm"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={() => setFullscreen(!fullscreen)}
            className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-600 transition-colors"
          >
            {fullscreen ? <X className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className={cls("flex", fullscreen ? "flex-1 overflow-hidden" : "")}>
        {/* Configuration Panel */}
        {showConfig && (
          <div className="w-80 border-r border-slate-200 p-4 space-y-6 overflow-y-auto">
            {/* Chart Type */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Chart Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {CHART_TYPES.map((type) => {
                  const Icon = type.icon;
                  const isActive = chartType === type.key;

                  return (
                    <button
                      key={type.key}
                      onClick={() => setChartType(type.key)}
                      className={cls(
                        "flex flex-col items-center gap-2 p-3 rounded-lg border-2 transition-all",
                        isActive
                          ? "border-black bg-black text-white"
                          : "border-slate-200 hover:border-slate-300 text-slate-700"
                      )}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="text-xs font-medium">{type.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* X-Axis */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                X-Axis
              </label>
              <select
                value={xAxis}
                onChange={(e) => setXAxis(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
              >
                <option value="">Select column...</option>
                <optgroup label="Date Columns">
                  {dateColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </optgroup>
                <optgroup label="Text Columns">
                  {textColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </optgroup>
              </select>
            </div>

            {/* Y-Axis (Multiple Selection) */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Y-Axis (Multiple)
              </label>
              <div className="space-y-1 max-h-48 overflow-y-auto rounded-lg border border-slate-200 p-2">
                {numericColumns.length === 0 ? (
                  <div className="text-sm text-slate-500 text-center py-4">
                    No numeric columns available
                  </div>
                ) : (
                  numericColumns.map(col => (
                    <label
                      key={col}
                      className="flex items-center gap-2 p-2 rounded hover:bg-slate-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={yAxis.includes(col)}
                        onChange={() => toggleYAxis(col)}
                        className="rounded"
                      />
                      <span className="text-sm text-slate-700">{col}</span>
                    </label>
                  ))
                )}
              </div>
              {yAxis.length > 0 && (
                <div className="text-xs text-slate-500 mt-1">
                  {yAxis.length} {yAxis.length === 1 ? 'metric' : 'metrics'} selected
                </div>
              )}
            </div>

            {/* Group By */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Group By (Optional)
              </label>
              <select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10"
              >
                <option value="">None</option>
                {textColumns.map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
              <div className="text-xs text-slate-500 mt-1">
                Group data by company, sector, etc.
              </div>
            </div>

            {/* Display Options */}
            <div className="space-y-3 pt-4 border-t border-slate-200">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showLegend}
                  onChange={(e) => setShowLegend(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-slate-700">Show Legend</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showGrid}
                  onChange={(e) => setShowGrid(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-slate-700">Show Grid</span>
              </label>
            </div>
          </div>
        )}

        {/* Chart Display */}
        <div className={cls("flex-1 p-6", fullscreen ? "overflow-auto" : "")}>
          {!xAxis || yAxis.length === 0 ? (
            <div className="flex items-center justify-center h-96 text-slate-500">
              <div className="text-center">
                <Settings className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <div className="text-sm">Configure X and Y axes to display chart</div>
              </div>
            </div>
          ) : ChartComponent ? (
            <ChartComponent
              data={data}
              xAxis={xAxis}
              yAxis={yAxis}
              groupBy={groupBy || undefined}
              showLegend={showLegend}
              showGrid={showGrid}
            />
          ) : (
            <div className="flex items-center justify-center h-96 text-slate-500">
              Chart type not implemented
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
