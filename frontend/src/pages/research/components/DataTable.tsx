import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface Column<T> {
  key: keyof T | string;
  header: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  title?: string;
  subtitle?: string;
  maxHeight?: string;
  striped?: boolean;
  compact?: boolean;
  onRowClick?: (row: T) => void;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  title,
  subtitle,
  maxHeight = '400px',
  striped = true,
  compact = false,
  onRowClick,
}: DataTableProps<T>) {
  const getValue = (row: T, key: string): any => {
    const keys = key.split('.');
    let value: any = row;
    for (const k of keys) {
      value = value?.[k];
    }
    return value;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {(title || subtitle) && (
        <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
          {title && <h3 className="text-sm font-semibold text-gray-900">{title}</h3>}
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
      )}
      <div className="overflow-auto" style={{ maxHeight }}>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className={`px-3 ${compact ? 'py-2' : 'py-3'} text-xs font-semibold text-gray-600 uppercase tracking-wide border-b border-gray-200
                    ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}`}
                  style={{ width: col.width }}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className={`${striped && rowIdx % 2 === 1 ? 'bg-gray-50/50' : ''}
                  ${onRowClick ? 'cursor-pointer hover:bg-blue-50/50' : 'hover:bg-gray-50'} transition-colors`}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col, colIdx) => {
                  const value = getValue(row, col.key as string);
                  return (
                    <td
                      key={colIdx}
                      className={`px-3 ${compact ? 'py-1.5' : 'py-2.5'} text-gray-700
                        ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}`}
                    >
                      {col.render ? col.render(value, row) : value}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length === 0 && (
        <div className="px-4 py-8 text-center text-gray-500 text-sm">
          No data available
        </div>
      )}
    </div>
  );
}

// Utility renderers
export function ChangeRenderer({ value, suffix = '' }: { value: number | null | undefined; suffix?: string }) {
  if (value === null || value === undefined) return <span className="text-gray-400">-</span>;
  const isPositive = value > 0;
  const isNegative = value < 0;
  return (
    <span className={`inline-flex items-center font-medium ${isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500'}`}>
      {isPositive ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : isNegative ? <ArrowDownRight className="w-3 h-3 mr-0.5" /> : <Minus className="w-3 h-3 mr-0.5" />}
      {isPositive ? '+' : ''}{value.toFixed(2)}{suffix}
    </span>
  );
}

export function PercentRenderer({ value, decimals = 1 }: { value: number | null | undefined; decimals?: number }) {
  if (value === null || value === undefined) return <span className="text-gray-400">-</span>;
  return <span>{value.toFixed(decimals)}%</span>;
}

export function NumberRenderer({ value, decimals = 0, prefix = '', suffix = '' }: { value: number | null | undefined; decimals?: number; prefix?: string; suffix?: string }) {
  if (value === null || value === undefined) return <span className="text-gray-400">-</span>;
  return <span>{prefix}{value.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}{suffix}</span>;
}

export function BadgeRenderer({ value, colorMap }: { value: string; colorMap?: Record<string, string> }) {
  const defaultColors: Record<string, string> = {
    default: 'bg-gray-100 text-gray-700',
  };
  const colors = { ...defaultColors, ...colorMap };
  const colorClass = colors[value] || colors.default;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colorClass}`}>
      {value}
    </span>
  );
}
