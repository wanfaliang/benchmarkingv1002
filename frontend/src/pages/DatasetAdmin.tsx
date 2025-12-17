// frontend/src/pages/DatasetAdmin.tsx
import React, { useEffect, useMemo, useState, ChangeEvent } from "react";
import { RefreshCw, Trash2, Wrench, Search, Shield } from "lucide-react";

/**
 * DatasetsAdmin.tsx - Prototype admin screen
 *
 * Goals:
 * - Monitor all datasets with filters by status/owner, quick actions.
 * - Bulk operations (recollect, reindex) - endpoint paths are placeholders, adjust to your backend.
 * - Guard this route with <ProtectedRoute roles={["admin"]}>.
 */

function cls(...xs: (string | boolean | undefined | null)[]): string {
  return xs.filter(Boolean).join(" ");
}

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

type DatasetStatus = "" | "created" | "collecting" | "ready" | "failed";
type ActionKind = "recollect" | "reindex" | "delete";

interface AdminDataset {
  id: number;
  name?: string;
  status?: string;
  table_count?: number;
  tables?: unknown[];
  updated_at?: string;
  updatedAt?: string;
  _sel?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export default function DatasetsAdmin(): React.ReactElement {
  const [items, setItems] = useState<AdminDataset[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const [q, setQ] = useState("");
  const [status, setStatus] = useState<DatasetStatus>("");

  async function load(): Promise<void> {
    setRefreshing(true);
    setError(null);
    try {
      const res = await fetch(`/datasets`);
      if (!res.ok) throw new Error(`List failed: ${res.status}`);
      const data = await res.json();
      const rows: AdminDataset[] = Array.isArray(data)
        ? data
        : data.items || [];
      setItems(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setItems([]);
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo<AdminDataset[]>(() => {
    if (!items) return [];
    return items.filter((d) => {
      const okS = !status || d.status === status;
      const okQ =
        !q ||
        d.name?.toLowerCase().includes(q.toLowerCase()) ||
        String(d.id).includes(q);
      return okS && okQ;
    });
  }, [items, q, status]);

  async function action(id: number, kind: ActionKind): Promise<void> {
    try {
      // Adjust endpoints to your admin API paths
      let url = "";
      let method: "POST" | "DELETE" = "POST";
      const body = null;
      if (kind === "recollect") url = `/admin/datasets/${id}/collect`;
      if (kind === "reindex") url = `/admin/datasets/${id}/reindex`;
      if (kind === "delete") {
        url = `/admin/datasets/${id}`;
        method = "DELETE";
      }
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      if (!res.ok) throw new Error(`${kind} failed: ${res.status}`);
      await load();
      alert(`${kind} queued/successful for ${id}`);
    } catch (e) {
      alert(e instanceof Error ? e.message : String(e));
    }
  }

  async function bulk(kind: ActionKind): Promise<void> {
    const chosen = filtered.filter((d) => d._sel).map((d) => d.id);
    if (chosen.length === 0) {
      alert("Select rows first");
      return;
    }
    if (!window.confirm(`${kind} ${chosen.length} dataset(s)?`)) return;
    for (const id of chosen) {
      await action(id, kind);
    }
  }

  function toggle(id: number): void {
    setItems((prev) =>
      prev
        ? prev.map((d) => (d.id === id ? { ...d, _sel: !d._sel } : d))
        : prev
    );
  }

  function toggleAll(v: boolean): void {
    setItems((prev) => (prev ? prev.map((d) => ({ ...d, _sel: v })) : prev));
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Datasets - Admin
          </h1>
          <p className="text-slate-600 mt-1 text-sm">
            Monitor status, run maintenance jobs, and clean up datasets.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            className={cls(
              "inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-200",
              refreshing && "opacity-70"
            )}
            disabled={refreshing}
          >
            <RefreshCw
              className={cls("w-4 h-4", refreshing && "animate-spin")}
            />{" "}
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-xl border border-rose-200 bg-rose-50 text-rose-800">
          {String(error)}
        </div>
      )}

      <section className="mt-6">
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-2 top-2.5" />
            <input
              value={q}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setQ(e.target.value)
              }
              placeholder="Search by name or id"
              className="pl-8 pr-3 py-2 rounded-xl border border-slate-300"
            />
          </div>
          <select
            value={status}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              setStatus(e.target.value as DatasetStatus)
            }
            className="px-3 py-2 rounded-xl border border-slate-300"
          >
            <option value="">All statuses</option>
            <option value="created">Created</option>
            <option value="collecting">Collecting</option>
            <option value="ready">Ready</option>
            <option value="failed">Failed</option>
          </select>

          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={() => bulk("recollect")}
              className="px-3 py-2 rounded-xl border border-slate-200"
            >
              <Wrench className="w-4 h-4 inline mr-1" /> Recollect
            </button>
            <button
              onClick={() => bulk("reindex")}
              className="px-3 py-2 rounded-xl border border-slate-200"
            >
              <Shield className="w-4 h-4 inline mr-1" /> Reindex
            </button>
            <button
              onClick={() => bulk("delete")}
              className="px-3 py-2 rounded-xl border border-rose-200 text-rose-700"
            >
              <Trash2 className="w-4 h-4 inline mr-1" /> Delete
            </button>
          </div>
        </div>

        <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr className="text-left text-slate-600">
                <th className="px-4 py-3">
                  <input
                    type="checkbox"
                    onChange={(e: ChangeEvent<HTMLInputElement>) =>
                      toggleAll(e.target.checked)
                    }
                  />
                </th>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Tables</th>
                <th className="px-4 py-3 font-medium">Updated</th>
                <th className="px-4 py-3 font-medium text-right">
                  Row actions
                </th>
              </tr>
            </thead>
            <tbody>
              {(filtered || []).map((d) => (
                <tr key={d.id} className="border-t border-slate-200">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={!!d._sel}
                      onChange={() => toggle(d.id)}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium truncate" title={d.name}>
                      {d.name || `Dataset ${d.id}`}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{d.id}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {(d.status || "").toUpperCase()}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {d.table_count ?? d.tables?.length ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {formatDate(d.updated_at || d.updatedAt)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => action(d.id, "recollect")}
                        className="px-3 py-1.5 rounded-lg border border-slate-200"
                      >
                        Recollect
                      </button>
                      <button
                        onClick={() => action(d.id, "reindex")}
                        className="px-3 py-1.5 rounded-lg border border-slate-200"
                      >
                        Reindex
                      </button>
                      <button
                        onClick={() => action(d.id, "delete")}
                        className="px-3 py-1.5 rounded-lg border border-rose-200 text-rose-700"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered && filtered.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-10 text-center text-slate-500"
                  >
                    No datasets match your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatDate(x?: string): string {
  if (!x) return "—";
  try {
    const d = new Date(x);
    return d.toLocaleString();
  } catch {
    return String(x);
  }
}
