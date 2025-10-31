import React, { useState, useEffect, useCallback } from "react";
import { Save, Play, Trash2, BookmarkCheck, Eye } from "lucide-react";
import { queriesAPI, formatError } from "../../services/api";
import ViewQueryDialog from "./ViewQueryDialog";

/**
 * SavedQueriesPanel - Shows saved queries for current data source
 * 
 * Features:
 * - Auto-loads queries for current data source
 * - Click to load/execute query
 * - View query configuration
 * - Quick delete
 * - Shows active query indicator
 * 
 * Note: Save functionality is now in the main header
 */

function cls(...classes) {
  return classes.filter(Boolean).join(" ");
}

export default function SavedQueriesPanel({
  dataSource,
  activeQueryId,
  onLoadQuery,
}) {
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewingQuery, setViewingQuery] = useState(null);

  // Load queries for current data source
  const loadQueries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // API filters by data_source on backend
      const response = await queriesAPI.list({ 
        data_source: dataSource,
        include_public: true 
      });
      setQueries(response.data || []);
    } catch (err) {
      setError(formatError(err));
      console.error("Failed to load queries:", err);
    } finally {
      setLoading(false);
    }
  }, [dataSource]);

  useEffect(() => {
    if (dataSource) {
      loadQueries();
    }
  }, [dataSource, loadQueries]);

  const handleLoadQuery = async (query) => {
    try {
      await onLoadQuery(query);
      // Reload to update usage count
      await loadQueries();
    } catch (err) {
      console.error("Failed to load query:", err);
    }
  };

  const handleViewQuery = (query, e) => {
    e.stopPropagation(); // Prevent triggering load
    setViewingQuery(query);
  };

  const handleDeleteQuery = async (queryId, e) => {
    e.stopPropagation(); // Prevent triggering load
    
    if (!window.confirm("Delete this query?")) return;

    try {
      await queriesAPI.delete(queryId);
      setQueries(queries.filter(q => q.query_id !== queryId));
    } catch (err) {
      alert("Failed to delete query: " + formatError(err));
    }
  };

  if (loading && queries.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <div className="w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin"></div>
          Loading queries...
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
        {/* Header */}
        <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookmarkCheck className="w-4 h-4 text-slate-700" />
            <h3 className="font-semibold text-slate-900 text-sm">Saved Queries</h3>
            {queries.length > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 text-xs">
                {queries.length}
              </span>
            )}
          </div>
        </div>

        {/* Query List */}
        <div className="p-3 space-y-2 max-h-64 overflow-y-auto">
          {error && (
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-sm text-rose-700">
              {error}
            </div>
          )}

          {queries.length === 0 ? (
            <div className="text-center py-6 text-slate-500 text-sm">
              <Save className="w-8 h-8 mx-auto mb-2 text-slate-300" />
              <div>No saved queries for {dataSource}</div>
              <div className="text-xs text-slate-400 mt-1">
                Apply filters and click "Save Query" in the header
              </div>
            </div>
          ) : (
            queries.map((query) => {
              const isActive = query.query_id === activeQueryId;

              return (
                <button
                  key={query.query_id}
                  onClick={() => handleLoadQuery(query)}
                  disabled={isActive}
                  className={cls(
                    "w-full px-3 py-2.5 rounded-lg text-left transition-all group",
                    isActive
                      ? "bg-black text-white cursor-default"
                      : "bg-slate-50 hover:bg-slate-100 border border-slate-200"
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className={cls(
                        "font-medium text-sm flex items-center gap-2",
                        isActive ? "text-white" : "text-slate-900"
                      )}>
                        {isActive && <Play className="w-3 h-3 flex-shrink-0" />}
                        <span className="truncate">{query.name}</span>
                      </div>
                      
                      {query.description && (
                        <div className={cls(
                          "text-xs mt-1 line-clamp-1",
                          isActive ? "text-white/80" : "text-slate-600"
                        )}>
                          {query.description}
                        </div>
                      )}

                      <div className={cls(
                        "flex items-center gap-2 text-xs mt-1.5",
                        isActive ? "text-white/70" : "text-slate-500"
                      )}>
                        {query.usage_count > 0 && (
                          <span>{query.usage_count} {query.usage_count === 1 ? 'use' : 'uses'}</span>
                        )}
                        {query.is_public && (
                          <>
                            {query.usage_count > 0 && <span>·</span>}
                            <span>Public</span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-1">
                      {/* View Button */}
                      <button
                        onClick={(e) => handleViewQuery(query, e)}
                        className={cls(
                          "p-1.5 rounded transition-colors opacity-0 group-hover:opacity-100",
                          isActive
                            ? "hover:bg-white/20 text-white"
                            : "hover:bg-blue-50 text-blue-600"
                        )}
                        title="View query configuration"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>

                      {/* Delete Button */}
                      <button
                        onClick={(e) => handleDeleteQuery(query.query_id, e)}
                        className={cls(
                          "p-1.5 rounded transition-colors opacity-0 group-hover:opacity-100",
                          isActive
                            ? "hover:bg-white/20 text-white"
                            : "hover:bg-rose-50 text-rose-600"
                        )}
                        title="Delete query"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* View Query Dialog */}
      {viewingQuery && (
        <ViewQueryDialog
          query={viewingQuery}
          onClose={() => setViewingQuery(null)}
        />
      )}
    </>
  );
}