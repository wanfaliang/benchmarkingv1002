import React from "react";
import { X, Eye, Filter, Columns, SortAsc, Calendar, Building2, Database } from "lucide-react";

function cls(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function ViewQueryDialog({ query, onClose }) {
  if (!query) return null;

  const config = query.query_config || {};
  const filterCount = config.filters?.length || 0;
  const columnCount = config.columns?.length || 0;
  const sortInfo = config.sort_by ? `${config.sort_by} (${config.sort_order || 'asc'})` : "None";

  // Helper to render operator in readable format
  const formatOperator = (operator) => {
    const operatorMap = {
      eq: "equals",
      ne: "not equals",
      gt: "greater than",
      gte: "greater than or equal",
      lt: "less than",
      lte: "less than or equal",
      in: "in",
      between: "between",
      contains: "contains"
    };
    return operatorMap[operator] || operator;
  };

  // Helper to format filter value
  const formatValue = (value) => {
    if (Array.isArray(value)) {
      return value.join(", ");
    }
    if (typeof value === "object" && value !== null) {
      return JSON.stringify(value);
    }
    return String(value);
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />

      <div className="fixed inset-0 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <Eye className="w-5 h-5 text-slate-700 flex-shrink-0" />
              <h2 className="font-semibold text-slate-900 truncate">{query.name}</h2>
            </div>
            <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-100 text-slate-700 flex-shrink-0">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content - Scrollable */}
          <div className="px-6 py-4 space-y-4 overflow-y-auto flex-1">
            {/* Query Metadata */}
            <div className="space-y-3">
              {query.description && (
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
                    Description
                  </label>
                  <p className="text-sm text-slate-700">{query.description}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
                    Data Source
                  </label>
                  <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                    <Database className="w-4 h-4 text-slate-600" />
                    <span className="text-sm font-medium text-slate-900">{query.data_source}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
                    Visibility
                  </label>
                  <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                    <div className={cls(
                      "w-2 h-2 rounded-full",
                      query.is_public ? "bg-green-500" : "bg-slate-400"
                    )} />
                    <span className="text-sm font-medium text-slate-900">
                      {query.is_public ? "Public" : "Private"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
                    Usage Count
                  </label>
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-sm font-medium text-slate-900">{query.usage_count || 0} times</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
                    Last Used
                  </label>
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-sm text-slate-700">
                      {query.last_used_at 
                        ? new Date(query.last_used_at).toLocaleDateString()
                        : "Never"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-slate-200" />

            {/* Query Configuration */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900 text-sm">Query Configuration</h3>

              {/* Filters */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Filter className="w-4 h-4 text-slate-600" />
                  <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Filters ({filterCount})
                  </label>
                </div>
                
                {filterCount === 0 ? (
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-500">
                    No filters applied
                  </div>
                ) : (
                  <div className="space-y-2">
                    {config.filters.map((filter, idx) => (
                      <div key={idx} className="px-3 py-2 rounded-lg bg-blue-50 border border-blue-200">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium text-blue-900">{filter.field}</span>
                          <span className="text-blue-600">{formatOperator(filter.operator)}</span>
                          <span className="font-mono text-blue-800">{formatValue(filter.value)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Companies Filter */}
              {config.companies && config.companies.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Building2 className="w-4 h-4 text-slate-600" />
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Companies ({config.companies.length})
                    </label>
                  </div>
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                    <div className="flex flex-wrap gap-1.5">
                      {config.companies.map((company, idx) => (
                        <span key={idx} className="px-2 py-1 rounded bg-slate-200 text-slate-700 text-xs font-medium">
                          {company}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Years Filter */}
              {config.years && config.years.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-slate-600" />
                    <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Years ({config.years.length})
                    </label>
                  </div>
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                    <div className="flex flex-wrap gap-1.5">
                      {config.years.map((year, idx) => (
                        <span key={idx} className="px-2 py-1 rounded bg-slate-200 text-slate-700 text-xs font-medium">
                          {year}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Columns */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Columns className="w-4 h-4 text-slate-600" />
                  <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Columns {columnCount > 0 ? `(${columnCount} selected)` : '(All)'}
                  </label>
                </div>
                
                {columnCount === 0 ? (
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-500">
                    All columns included
                  </div>
                ) : (
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                    <div className="flex flex-wrap gap-1.5">
                      {config.columns.map((col, idx) => (
                        <span key={idx} className="px-2 py-1 rounded bg-slate-200 text-slate-700 text-xs font-mono">
                          {col}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Sort */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <SortAsc className="w-4 h-4 text-slate-600" />
                  <label className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Sort Order
                  </label>
                </div>
                <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
                  <span className="text-sm text-slate-700">{sortInfo}</span>
                </div>
              </div>

              {/* Pagination */}
              {(config.limit || config.offset > 0) && (
                <div>
                  <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">
                    Pagination
                  </label>
                  <div className="px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-700">
                    {config.limit && <div>Limit: {config.limit} rows</div>}
                    {config.offset > 0 && <div>Offset: {config.offset} rows</div>}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-end flex-shrink-0">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-black text-white hover:bg-black/90 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  );
}