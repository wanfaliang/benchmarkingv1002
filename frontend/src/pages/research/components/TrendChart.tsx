import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface TrendPoint {
  date: string;
  value: number;
  period?: string;
  year?: number;
}

interface TrendChartProps {
  data: TrendPoint[];
  title?: string;
  subtitle?: string;
  color?: string;
  height?: number;
  showGrid?: boolean;
  showAxis?: boolean;
  showArea?: boolean;
  valueFormatter?: (value: number) => string;
  dateFormatter?: (date: string) => string;
  referenceLine?: number;
  referenceLineLabel?: string;
}

export function TrendChart({
  data,
  title,
  subtitle,
  color = '#6366f1',
  height = 200,
  showGrid = true,
  showAxis = true,
  showArea = true,
  valueFormatter = (v) => v.toFixed(2),
  dateFormatter = (d) => d,
  referenceLine,
  referenceLineLabel,
}: TrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4" style={{ height }}>
        <div className="flex items-center justify-center h-full text-gray-400 text-sm">
          No data available
        </div>
      </div>
    );
  }

  const minValue = Math.min(...data.map(d => d.value));
  const maxValue = Math.max(...data.map(d => d.value));
  const padding = (maxValue - minValue) * 0.1;

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {(title || subtitle) && (
        <div className="px-4 py-3 border-b border-gray-100">
          {title && <h3 className="text-sm font-semibold text-gray-900">{title}</h3>}
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
      )}
      <div className="p-4">
        <ResponsiveContainer width="100%" height={height}>
          {showArea ? (
            <AreaChart data={data} margin={{ top: 5, right: 5, left: showAxis ? 0 : -20, bottom: 5 }}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
              {showAxis && (
                <>
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    tickLine={false}
                    axisLine={{ stroke: '#e5e7eb' }}
                    tickFormatter={dateFormatter}
                  />
                  <YAxis
                    domain={[minValue - padding, maxValue + padding]}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={valueFormatter}
                    width={50}
                  />
                </>
              )}
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                }}
                formatter={(value: number) => [valueFormatter(value), 'Value']}
                labelFormatter={(label) => dateFormatter(label)}
              />
              {referenceLine !== undefined && (
                <ReferenceLine
                  y={referenceLine}
                  stroke="#ef4444"
                  strokeDasharray="5 5"
                  label={referenceLineLabel ? { value: referenceLineLabel, fontSize: 10, fill: '#ef4444' } : undefined}
                />
              )}
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                fill={`${color}20`}
                strokeWidth={2}
              />
            </AreaChart>
          ) : (
            <LineChart data={data} margin={{ top: 5, right: 5, left: showAxis ? 0 : -20, bottom: 5 }}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
              {showAxis && (
                <>
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    tickLine={false}
                    axisLine={{ stroke: '#e5e7eb' }}
                    tickFormatter={dateFormatter}
                  />
                  <YAxis
                    domain={[minValue - padding, maxValue + padding]}
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={valueFormatter}
                    width={50}
                  />
                </>
              )}
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                formatter={(value: number) => [valueFormatter(value), 'Value']}
              />
              {referenceLine !== undefined && (
                <ReferenceLine y={referenceLine} stroke="#ef4444" strokeDasharray="5 5" />
              )}
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Mini sparkline for inline use
export function Sparkline({
  data,
  height = 40,
  width = 120,
  showDot = false,
}: {
  data: TrendPoint[];
  height?: number;
  width?: number;
  showDot?: boolean;
}) {
  if (!data || data.length === 0) return null;

  const trend = data.length >= 2 ? (data[data.length - 1].value > data[0].value ? 'up' : 'down') : 'flat';
  const strokeColor = trend === 'up' ? '#10b981' : trend === 'down' ? '#ef4444' : '#6b7280';

  return (
    <div style={{ width, height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <Area
            type="monotone"
            dataKey="value"
            stroke={strokeColor}
            fill={`${strokeColor}20`}
            strokeWidth={1.5}
            dot={showDot ? { r: 2, fill: strokeColor } : false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
