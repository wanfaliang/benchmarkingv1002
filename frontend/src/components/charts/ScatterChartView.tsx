import React, { useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ZAxis,
} from "recharts";

const COLORS = [
  "#0ea5e9", "#8b5cf6", "#ec4899", "#f59e0b",
  "#10b981", "#ef4444", "#6366f1", "#14b8a6",
];

interface ChartViewProps {
  data: Record<string, unknown>[];
  xAxis: string;
  yAxis: string[];
  groupBy?: string;
  showLegend?: boolean;
  showGrid?: boolean;
}

interface ScatterDataPoint {
  x: unknown;
  y: number;
}

interface ScatterSeries {
  name: string;
  data: ScatterDataPoint[];
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: ScatterDataPoint;
  }>;
}

export default function ScatterChartView({ data, xAxis, yAxis, groupBy, showLegend, showGrid }: ChartViewProps): React.ReactElement {
  // For scatter plot, we only use first Y-axis metric
  const yMetric = yAxis[0];

  // Process data
  const scatterData = useMemo((): ScatterSeries[] => {
    if (!data || !xAxis || !yMetric) return [];

    if (!groupBy) {
      // Single series
      return [{
        name: `${xAxis} vs ${yMetric}`,
        data: data
          .map(row => ({
            x: row[xAxis],
            y: row[yMetric] as number,
          }))
          .filter(point =>
            point.x !== null && point.x !== undefined &&
            point.y !== null && point.y !== undefined &&
            typeof point.y === 'number'
          ),
      }];
    } else {
      // Multiple series by group
      const grouped: Record<string, ScatterDataPoint[]> = {};

      data.forEach(row => {
        const groupValue = row[groupBy];
        if (!groupValue) return;

        const x = row[xAxis];
        const y = row[yMetric] as number;

        if (x !== null && x !== undefined &&
            y !== null && y !== undefined &&
            typeof y === 'number') {

          const groupKey = String(groupValue);
          if (!grouped[groupKey]) {
            grouped[groupKey] = [];
          }
          grouped[groupKey].push({ x, y });
        }
      });

      return Object.keys(grouped).map(key => ({
        name: key,
        data: grouped[key],
      }));
    }
  }, [data, xAxis, yMetric, groupBy]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: TooltipProps): React.ReactElement | null => {
    if (!active || !payload || !payload.length) return null;

    const point = payload[0].payload;
    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3">
        <div className="text-sm space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-slate-600">{xAxis}:</span>
            <span className="font-medium text-slate-900">{String(point.x)}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-slate-600">{yMetric}:</span>
            <span className="font-medium text-slate-900">
              {typeof point.y === 'number'
                ? point.y.toLocaleString(undefined, { maximumFractionDigits: 2 })
                : point.y}
            </span>
          </div>
        </div>
      </div>
    );
  };

  if (!yMetric) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-500">
        <div className="text-center">
          <div className="text-sm">Select at least one Y-axis metric</div>
          <div className="text-xs text-slate-400 mt-1">Scatter plots use the first selected metric</div>
        </div>
      </div>
    );
  }

  if (!scatterData || scatterData.length === 0 || scatterData[0].data.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-500">
        No data available for selected configuration
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={500}>
      <ScatterChart margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />}
        <XAxis
          type="number"
          dataKey="x"
          name={xAxis}
          stroke="#64748b"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name={yMetric}
          stroke="#64748b"
          style={{ fontSize: '12px' }}
          tickFormatter={(value: number) => {
            if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
            if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
            if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
            return value.toFixed(0);
          }}
        />
        <ZAxis range={[50, 400]} />
        <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
        {showLegend && <Legend />}

        {scatterData.map((series, idx) => (
          <Scatter
            key={series.name}
            name={series.name}
            data={series.data}
            fill={COLORS[idx % COLORS.length]}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  );
}
