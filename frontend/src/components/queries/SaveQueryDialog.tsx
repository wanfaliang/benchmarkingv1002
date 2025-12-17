import React, { useState } from "react";
import { X, Save, AlertCircle, Filter, Columns, SortAsc } from "lucide-react";

function cls(...classes: (string | boolean | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

// ============================================================================
// Types
// ============================================================================

interface QueryConfig {
  filters?: Array<{ field: string; operator: string; value: unknown }>;
  columns?: string[];
  sort_by?: string;
  sort_order?: string;
  companies?: string[];
  years?: number[];
}

interface SaveQueryPayload {
  name: string;
  description: string | null;
  data_source: string;
  query_config: QueryConfig;
  is_public: boolean;
}

interface SaveQueryDialogProps {
  onSave: (payload: SaveQueryPayload) => Promise<void>;
  onClose: () => void;
  dataSource: string;
  currentQuery?: QueryConfig;
}

// ============================================================================
// Component
// ============================================================================

export default function SaveQueryDialog({
  onSave,
  onClose,
  dataSource,
  currentQuery = {}
}: SaveQueryDialogProps): React.ReactElement {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  // Extract query details for preview
  const filterCount = currentQuery.filters?.length || 0;
  const columnCount = currentQuery.columns?.length || 0;
  const sortInfo = currentQuery.sort_by ? `${currentQuery.sort_by} (${currentQuery.sort_order || 'asc'})` : "None";

  const handleSave = async () => {
    if (!name.trim()) {
      setError("Please enter a query name");
      return;
    }

    // Validate that we have actual query content
    if (!currentQuery.filters?.length && !currentQuery.columns?.length && !currentQuery.sort_by) {
      setError("No query configuration to save. Apply some filters or customize columns first.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      await onSave({
        name: name.trim(),
        description: description.trim() || null,
        data_source: dataSource,
        query_config: currentQuery,
        is_public: isPublic,
      });

      onClose();
    } catch (err) {
      const error = err as Error;
      setError(error.message || "Failed to save query");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />

      <div className="fixed inset-0 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Save className="w-5 h-5 text-slate-700" />
              <h2 className="font-semibold text-slate-900">Save Query</h2>
            </div>
            <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-100 text-slate-700">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-4">
            {/* Data Source Info */}
            <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-sm">
              <div className="text-blue-900 font-medium mb-2">Data Source: {dataSource}</div>

              {/* Query Preview */}
              <div className="space-y-1.5 text-xs text-blue-700">
                <div className="flex items-center gap-2">
                  <Filter className="w-3.5 h-3.5" />
                  <span className="font-medium">{filterCount} filter{filterCount !== 1 ? 's' : ''}</span>
                  {filterCount > 0 && currentQuery.filters && (
                    <span className="text-blue-600">
                      ({currentQuery.filters.map(f => f.field).join(", ")})
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <Columns className="w-3.5 h-3.5" />
                  <span className="font-medium">
                    {columnCount > 0 ? `${columnCount} columns selected` : 'All columns'}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <SortAsc className="w-3.5 h-3.5" />
                  <span className="font-medium">Sort: {sortInfo}</span>
                </div>

                {((currentQuery.companies && currentQuery.companies.length > 0) || (currentQuery.years && currentQuery.years.length > 0)) && (
                  <div className="mt-2 pt-2 border-t border-blue-200">
                    {currentQuery.companies && currentQuery.companies.length > 0 && (
                      <div>Companies: {currentQuery.companies.join(", ")}</div>
                    )}
                    {currentQuery.years && currentQuery.years.length > 0 && (
                      <div>Years: {currentQuery.years.join(", ")}</div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Query Name */}
            <div>
              <label className="block text-sm font-medium text-slate-900 mb-1.5">
                Query Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., High Revenue Tech Companies"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 text-sm"
                autoFocus
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-slate-900 mb-1.5">
                Description <span className="text-slate-500 text-xs">(optional)</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what this query does..."
                rows={3}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/10 text-sm resize-none"
              />
            </div>

            {/* Public Toggle */}
            <div className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 bg-slate-50">
              <input
                type="checkbox"
                id="public"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                className="mt-0.5 rounded border-slate-300"
              />
              <div className="flex-1">
                <label htmlFor="public" className="block text-sm font-medium text-slate-900 cursor-pointer">
                  Make this query public
                </label>
                <p className="text-xs text-slate-600 mt-0.5">
                  Other users can view and use this query
                </p>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5" />
                <div className="text-sm text-rose-700">{error}</div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-end gap-2">
            <button
              onClick={onClose}
              disabled={saving}
              className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !name.trim()}
              className={cls(
                "px-4 py-2 rounded-lg bg-black text-white inline-flex items-center gap-2",
                saving || !name.trim() ? "opacity-50 cursor-not-allowed" : "hover:bg-black/90"
              )}
            >
              {saving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Query
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
