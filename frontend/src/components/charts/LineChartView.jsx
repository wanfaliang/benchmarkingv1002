import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

/**
 * LineChartView.jsx - Line Chart Component
 * 
 * Features:
 * - Multiple Y-axis metrics
 * - Multi-company comparison
 * - Interactive tooltips
 * - Responsive design
 * - Smooth animations
 */

// Color palette for multiple lines
const COLORS = [
  "#0ea5e9", // sky-500
  "#8b5cf6", // violet-500
  "#ec4899", // pink-500
  "#f59e0b", // amber-500
  "#10b981", // emerald-500
  "#ef4444", // red-500
  "#6366f1", // indigo-500
  "#14b8a6", // teal-500
];

export default function LineChartView({ data, xAxis, yAxis, groupBy, showLegend, showGrid }) {
  // Process data for chart
  const chartData = useMemo(() => {
    if (!data || !xAxis || yAxis.length === 0) return [];

    if (!groupBy) {
      // Simple: no grouping, just aggregate by X-axis
      const grouped = {};
      
      data.forEach(row => {
        const xValue = row[xAxis];
        if (xValue === null || xValue === undefined) return;

        const key = String(xValue);
        if (!grouped[key]) {
          grouped[key] = { [xAxis]: xValue };
          yAxis.forEach(col => {
            grouped[key][col] = 0;
            grouped[key][`${col}_count`] = 0;
          });
        }

        yAxis.forEach(col => {
          const value = row[col];
          if (typeof value === 'number' && !isNaN(value)) {
            grouped[key][col] += value;
            grouped[key][`${col}_count`]++;
          }
        });
      });

      // Calculate averages
      return Object.values(grouped).map(item => {
        const result = { [xAxis]: item[xAxis] };
        yAxis.forEach(col => {
          const count = item[`${col}_count`];
          result[col] = count > 0 ? item[col] / count : null;
        });
        return result;
      }).sort((a, b) => {
        const aVal = a[xAxis];
        const bVal = b[xAxis];
        if (aVal < bVal) return -1;
        if (aVal > bVal) return 1;
        return 0;
      });
    } else {
      // Complex: group by company/sector
      const grouped = {};
      
      data.forEach(row => {
        const xValue = row[xAxis];
        const groupValue = row[groupBy];
        if (xValue === null || xValue === undefined || !groupValue) return;

        const key = String(xValue);
        if (!grouped[key]) {
          grouped[key] = { [xAxis]: xValue };
        }

        yAxis.forEach(col => {
          const value = row[col];
          if (typeof value === 'number' && !isNaN(value)) {
            const seriesKey = `${groupValue}_${col}`;
            grouped[key][seriesKey] = value;
          }
        });
      });

      return Object.values(grouped).sort((a, b) => {
        const aVal = a[xAxis];
        const bVal = b[xAxis];
        if (aVal < bVal) return -1;
        if (aVal > bVal) return 1;
        return 0;
      });
    }
  }, [data, xAxis, yAxis, groupBy]);

  // Get all series (lines) to draw
  const series = useMemo(() => {
    if (!chartData || chartData.length === 0) return [];

    if (!groupBy) {
      // Simple: one line per Y-axis metric
      return yAxis.map((col, idx) => ({
        dataKey: col,
        name: col,
        color: COLORS[idx % COLORS.length],
      }));
    } else {
      // Complex: one line per (group, metric) combination
      const seriesSet = new Set();
      chartData.forEach(item => {
        Object.keys(item).forEach(key => {
          if (key !== xAxis && !key.endsWith('_count')) {
            seriesSet.add(key);
          }
        });
      });

      return Array.from(seriesSet).map((key, idx) => ({
        dataKey: key,
        name: key,
        color: COLORS[idx % COLORS.length],
      }));
    }
  }, [chartData, xAxis, yAxis, groupBy]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3">
        <div className="font-medium text-slate-900 mb-2">{label}</div>
        {payload.map((entry, idx) => (
          <div key={idx} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-slate-600">{entry.name}:</span>
            <span className="font-medium text-slate-900">
              {typeof entry.value === 'number' 
                ? entry.value.toLocaleString(undefined, { maximumFractionDigits: 2 })
                : entry.value}
            </span>
          </div>
        ))}
      </div>
    );
  };

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-500">
        No data available for selected configuration
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />}
        <XAxis 
          dataKey={xAxis} 
          stroke="#64748b"
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          stroke="#64748b"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => {
            if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
            if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
            if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
            return value.toFixed(0);
          }}
        />
        <Tooltip content={<CustomTooltip />} />
        {showLegend && <Legend />}
        
        {series.map((s) => (
          <Line
            key={s.dataKey}
            type="monotone"
            dataKey={s.dataKey}
            name={s.name}
            stroke={s.color}
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
