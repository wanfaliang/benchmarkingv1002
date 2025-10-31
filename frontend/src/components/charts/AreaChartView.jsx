import React, { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

/**
 * AreaChartView.jsx - Area Chart Component
 * 
 * Features:
 * - Stacked area charts
 * - Multi-company comparison
 * - Interactive tooltips
 * - Gradient fills
 */

const COLORS = [
  "#0ea5e9", "#8b5cf6", "#ec4899", "#f59e0b", 
  "#10b981", "#ef4444", "#6366f1", "#14b8a6",
];

export default function AreaChartView({ data, xAxis, yAxis, groupBy, showLegend, showGrid }) {
  // Process data (same as line/bar charts)
  const chartData = useMemo(() => {
    if (!data || !xAxis || yAxis.length === 0) return [];

    if (!groupBy) {
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

  // Get all series
  const series = useMemo(() => {
    if (!chartData || chartData.length === 0) return [];

    if (!groupBy) {
      return yAxis.map((col, idx) => ({
        dataKey: col,
        name: col,
        color: COLORS[idx % COLORS.length],
      }));
    } else {
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
      <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <defs>
          {series.map((s, idx) => (
            <linearGradient key={s.dataKey} id={`gradient${idx}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={s.color} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={s.color} stopOpacity={0.1}/>
            </linearGradient>
          ))}
        </defs>
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
        
        {series.map((s, idx) => (
          <Area
            key={s.dataKey}
            type="monotone"
            dataKey={s.dataKey}
            name={s.name}
            stroke={s.color}
            strokeWidth={2}
            fill={`url(#gradient${idx})`}
            fillOpacity={1}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
}
