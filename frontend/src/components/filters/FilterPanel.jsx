import React, { useState, useMemo, useEffect } from "react";
import { Filter, X, Plus, RefreshCw, Grid3x3 } from "lucide-react";

/**
 * FilterPanel.jsx - Advanced Filtering Component
 * 
 * Features:
 * - Column-specific filters
 * - Multiple filter types (text, number, date, range)
 * - AND/OR logic
 * - Column picker for customizing display
 * - Clear all filters
 * - Real-time filtering
 */

function cls(...classes) {
  return classes.filter(Boolean).join(" ");
}

// Filter operators
const TEXT_OPERATORS = [
  { value: "contains", label: "Contains" },
  { value: "equals", label: "Equals" },
  { value: "startsWith", label: "Starts with" },
  { value: "endsWith", label: "Ends with" },
  { value: "notContains", label: "Does not contain" },
];

const NUMBER_OPERATORS = [
  { value: "equals", label: "Equals" },
  { value: "notEquals", label: "Not equals" },
  { value: "gt", label: "Greater than" },
  { value: "gte", label: "Greater than or equal" },
  { value: "lt", label: "Less than" },
  { value: "lte", label: "Less than or equal" },
  { value: "between", label: "Between" },
];

const DATE_OPERATORS = [
  { value: "equals", label: "Equals" },
  { value: "before", label: "Before" },
  { value: "after", label: "After" },
  { value: "between", label: "Between" },
];

// ============================================================================
// SINGLE FILTER ROW COMPONENT
// ============================================================================

function FilterRow({ filter, columns, columnTypes, onChange, onRemove }) {
  const operators = useMemo(() => {
    const type = columnTypes[filter.column];
    if (type === "number") return NUMBER_OPERATORS;
    if (type === "date") return DATE_OPERATORS;
    return TEXT_OPERATORS;
  }, [filter.column, columnTypes]);

  const handleChange = (field, value) => {
    onChange({ ...filter, [field]: value });
  };

  return (
    <div className="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-white">
      {/* Column */}
      <select
        value={filter.column}
        onChange={(e) => handleChange("column", e.target.value)}
        className="flex-1 px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 text-sm"
      >
        <option value="">Select column...</option>
        {columns.map(col => (
          <option key={col} value={col}>{col}</option>
        ))}
      </select>

      {/* Operator */}
      <select
        value={filter.operator}
        onChange={(e) => handleChange("operator", e.target.value)}
        disabled={!filter.column}
        className="px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 text-sm disabled:bg-slate-50 disabled:text-slate-400"
      >
        {operators.map(op => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>

      {/* Value */}
      <input
        type={columnTypes[filter.column] === "number" ? "number" : "text"}
        value={filter.value}
        onChange={(e) => handleChange("value", e.target.value)}
        placeholder="Value..."
        disabled={!filter.column}
        className="flex-1 px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 text-sm disabled:bg-slate-50"
      />

      {/* Between second value */}
      {filter.operator === "between" && (
        <input
          type={columnTypes[filter.column] === "number" ? "number" : "text"}
          value={filter.value2 || ""}
          onChange={(e) => handleChange("value2", e.target.value)}
          placeholder="To..."
          className="flex-1 px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 text-sm"
        />
      )}

      {/* Remove */}
      <button
        onClick={onRemove}
        className="p-2 rounded-lg hover:bg-rose-50 text-rose-600 transition-colors"
        title="Remove filter"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

// ============================================================================
// MAIN FILTER PANEL COMPONENT
// ============================================================================

export default function FilterPanel({ data, columns, onFilter, onFilterUpdate }) {
  const [filters, setFilters] = useState([]);
  const [logic, setLogic] = useState("AND"); // "AND" | "OR"
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [showColumnPicker, setShowColumnPicker] = useState(false);

  // Detect column types
  const columnTypes = useMemo(() => {
    if (!data || data.length === 0) return {};

    const types = {};
    const sample = data[0];

    columns.forEach(col => {
      const value = sample[col];
      if (value === null || value === undefined) {
        types[col] = "text";
      } else if (typeof value === "number") {
        types[col] = "number";
      } else if (col.toLowerCase().includes("date") || col.toLowerCase().includes("year")) {
        types[col] = "date";
      } else {
        types[col] = "text";
      }
    });

    return types;
  }, [data, columns]);

  // Initialize selected columns (all selected by default)
  useEffect(() => {
    setSelectedColumns(columns);
  }, [columns]);

  // Add new filter
  const addFilter = () => {
    setFilters([
      ...filters,
      { id: Date.now(), column: "", operator: "contains", value: "" },
    ]);
  };

  // Update filter
  const updateFilter = (id, updated) => {
    setFilters(filters.map(f => f.id === id ? updated : f));
  };

  // Remove filter
  const removeFilter = (id) => {
    setFilters(filters.filter(f => f.id !== id));
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters([]);
    if (onFilter) onFilter(data);
    if (onFilterUpdate) onFilterUpdate([]);
  };

  // Column selection handlers
  const toggleColumn = (column) => {
    setSelectedColumns(prev => 
      prev.includes(column) 
        ? prev.filter(c => c !== column)
        : [...prev, column]
    );
  };

  const selectAllColumns = () => {
    setSelectedColumns(columns);
  };

  const clearAllColumns = () => {
    setSelectedColumns([]);
  };

  const applyColumnSelection = () => {
    if (onFilterUpdate) {
      onFilterUpdate(filters, selectedColumns.length > 0 ? selectedColumns : null);
    }
    setShowColumnPicker(false);
  };

  // Apply filters
  const applyFilters = () => {
    if (!data || filters.length === 0) {
      if (onFilter) onFilter(data);
      return;
    }

    const filtered = data.filter(row => {
      const results = filters.map(filter => {
        if (!filter.column || !filter.value) return true;

        const cellValue = row[filter.column];
        const filterValue = filter.value;
        const type = columnTypes[filter.column];

        // Handle null/undefined
        if (cellValue === null || cellValue === undefined) return false;

        // Text filters
        if (type === "text") {
          const cell = String(cellValue).toLowerCase();
          const val = String(filterValue).toLowerCase();

          switch (filter.operator) {
            case "contains": return cell.includes(val);
            case "equals": return cell === val;
            case "startsWith": return cell.startsWith(val);
            case "endsWith": return cell.endsWith(val);
            case "notContains": return !cell.includes(val);
            default: return true;
          }
        }

        // Number filters
        if (type === "number") {
          const cell = Number(cellValue);
          const val = Number(filterValue);
          if (isNaN(cell) || isNaN(val)) return false;

          switch (filter.operator) {
            case "equals": return cell === val;
            case "notEquals": return cell !== val;
            case "gt": return cell > val;
            case "gte": return cell >= val;
            case "lt": return cell < val;
            case "lte": return cell <= val;
            case "between": {
              const val2 = Number(filter.value2);
              if (isNaN(val2)) return false;
              return cell >= val && cell <= val2;
            }
            default: return true;
          }
        }

        // Date filters (simplified)
        if (type === "date") {
          const cell = String(cellValue);
          const val = String(filterValue);

          switch (filter.operator) {
            case "equals": return cell === val;
            case "before": return cell < val;
            case "after": return cell > val;
            case "between": {
              const val2 = String(filter.value2);
              return cell >= val && cell <= val2;
            }
            default: return true;
          }
        }

        return true;
      });

      // Apply AND/OR logic
      return logic === "AND" ? results.every(r => r) : results.some(r => r);
    });

    if (onFilter) onFilter(filtered);
    if (onFilterUpdate) {
      onFilterUpdate(filters);
      // Also update parent with selected columns
      if (onFilterUpdate) {
        onFilterUpdate(filters, selectedColumns.length > 0 ? selectedColumns : null);
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-slate-700" />
          <h3 className="font-semibold text-slate-900">Advanced Filters</h3>
          {filters.length > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 text-xs font-medium">
              {filters.length} active
            </span>
          )}
        </div>

        {/* Logic Toggle */}
        {filters.length > 1 && (
          <div className="flex items-center gap-1 p-1 rounded-lg border border-slate-200 bg-white">
            <button
              onClick={() => setLogic("AND")}
              className={cls(
                "px-3 py-1 rounded text-xs font-medium transition-colors",
                logic === "AND" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-50"
              )}
            >
              AND
            </button>
            <button
              onClick={() => setLogic("OR")}
              className={cls(
                "px-3 py-1 rounded text-xs font-medium transition-colors",
                logic === "OR" ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-50"
              )}
            >
              OR
            </button>
          </div>
        )}
      </div>

      {/* Filter Rows */}
      {filters.length > 0 && (
        <div className="space-y-2">
          {filters.map((filter, idx) => (
            <div key={filter.id}>
              <FilterRow
                filter={filter}
                columns={columns}
                columnTypes={columnTypes}
                onChange={(updated) => updateFilter(filter.id, updated)}
                onRemove={() => removeFilter(filter.id)}
              />
              {idx < filters.length - 1 && (
                <div className="text-center py-1">
                  <span className="px-2 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium">
                    {logic}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={addFilter}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 hover:bg-slate-50 transition-colors text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Filter
        </button>

        <button
          onClick={() => setShowColumnPicker(!showColumnPicker)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 hover:bg-slate-50 transition-colors text-sm"
        >
          <Grid3x3 className="w-4 h-4" />
          Columns ({selectedColumns.length}/{columns.length})
        </button>

        {filters.length > 0 && (
          <>
            <button
              onClick={applyFilters}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-black text-white hover:bg-black/90 transition-colors text-sm"
            >
              <Filter className="w-4 h-4" />
              Apply Filters
            </button>

            <button
              onClick={clearFilters}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 hover:bg-slate-50 transition-colors text-sm"
            >
              <RefreshCw className="w-4 h-4" />
              Clear All
            </button>
          </>
        )}
      </div>

      {/* Results Summary */}
      {filters.length > 0 && (
        <div className="text-xs text-slate-500">
          Click "Apply Filters" to see filtered results
        </div>
      )}

      {/* Column Picker */}
      {showColumnPicker && (
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-slate-900 text-sm">Select Columns to Display</h4>
            <div className="flex items-center gap-2">
              <button
                onClick={selectAllColumns}
                className="text-xs text-blue-600 hover:text-blue-700"
              >
                Select All
              </button>
              <span className="text-slate-300">|</span>
              <button
                onClick={clearAllColumns}
                className="text-xs text-slate-600 hover:text-slate-700"
              >
                Clear All
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-64 overflow-y-auto mb-3">
            {columns.map(column => (
              <label
                key={column}
                className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-slate-50 cursor-pointer text-sm"
              >
                <input
                  type="checkbox"
                  checked={selectedColumns.includes(column)}
                  onChange={() => toggleColumn(column)}
                  className="rounded border-slate-300"
                />
                <span className="text-slate-700 truncate">{column}</span>
              </label>
            ))}
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-200">
            <div className="text-xs text-slate-500">
              {selectedColumns.length} of {columns.length} columns selected
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowColumnPicker(false)}
                className="px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-sm"
              >
                Cancel
              </button>
              <button
                onClick={applyColumnSelection}
                className="px-3 py-1.5 rounded-lg bg-black text-white hover:bg-black/90 text-sm"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}