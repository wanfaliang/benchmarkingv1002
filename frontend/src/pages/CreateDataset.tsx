// frontend/src/pages/CreateDataset.tsx
import React, { useMemo, useState, KeyboardEvent } from "react";
import { useNavigate } from "react-router-dom";
import {
  Trash2,
  CheckCircle2,
  Shield,
  Users,
  Building2,
  ArrowLeft,
  Sparkles,
  Info,
} from "lucide-react";
import { datasetsAPI, tickerAPI, formatError } from "../services/api";

/**
 * CreateDataset.tsx - Professional Dataset Creation Interface
 *
 * Features:
 * - Multi-step form with validation
 * - Real-time ticker validation
 * - Beautiful UI with helpful guidance
 * - Proper error handling
 * - Navigates to /datasets on success
 */

function cls(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface Company {
  ticker: string;
  name: string;
  currency?: string;
  exchange?: string;
}

type Visibility = "private" | "public";

// ============================================================================
// COMPONENT
// ============================================================================

export default function CreateDataset(): React.ReactElement {
  const navigate = useNavigate();

  // Form state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [companies, setCompanies] = useState<Company[]>([]);
  const [tickerInput, setTickerInput] = useState("");
  const [yearsBack, setYearsBack] = useState(15);
  const [includeAnalyst, setIncludeAnalyst] = useState(true);
  const [includeInstitutional, setIncludeInstitutional] = useState(true);
  const [visibility, setVisibility] = useState<Visibility>("private");

  // UI state
  const [validating, setValidating] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Validation
  const canSubmit = useMemo(
    () => companies.length > 0 && !creating && !validating,
    [companies.length, creating, validating]
  );

  // Validate and add ticker
  async function validateAndAddTicker(rawTicker?: string): Promise<void> {
    const ticker = (rawTicker || tickerInput || "").trim().toUpperCase();
    if (!ticker) return;

    // Check for duplicates
    if (companies.some((c) => c.ticker.toUpperCase() === ticker)) {
      setError(`${ticker} is already added`);
      return;
    }

    setValidating(true);
    setError(null);

    try {
      const res = await tickerAPI.validate(ticker);
      const data = res.data;

      if (!data?.valid) {
        setError(`${ticker} is not a valid ticker`);
        return;
      }

      const newCompany: Company = {
        ticker: data.symbol || ticker,
        name: data.name || ticker,
        currency: data.currency,
        exchange: data.exchange,
      };

      setCompanies((prev) => [...prev, newCompany]);
      setTickerInput("");
      setError(null);
    } catch (e) {
      setError(formatError(e as Parameters<typeof formatError>[0]));
    } finally {
      setValidating(false);
    }
  }

  // Remove company
  function removeCompany(ticker: string): void {
    setCompanies((prev) => prev.filter((c) => c.ticker !== ticker));
  }

  // Create dataset
  async function handleCreate(): Promise<void> {
    if (!canSubmit) return;

    setCreating(true);
    setError(null);

    try {
      const payload = {
        name: name.trim() || `Dataset ${new Date().toLocaleString()}`,
        description: description.trim() || "",
        companies,
        years_back: Number(yearsBack) || 15,
        include_analyst: !!includeAnalyst,
        include_institutional: !!includeInstitutional,
        visibility,
      };

      const res = await datasetsAPI.create(payload);
      const created = res.data;
      const id = created?.dataset_id || created?.id;

      if (!id) {
        // No ID returned, but creation succeeded - go to list
        setSuccess(true);
        setTimeout(() => navigate("/datasets"), 1500);
        return;
      }

      // Success! Show message and redirect to list
      setSuccess(true);
      setTimeout(() => navigate("/datasets"), 1500);
    } catch (e) {
      setError(formatError(e as Parameters<typeof formatError>[0]));
    } finally {
      setCreating(false);
    }
  }

  // Handle Enter key in ticker input
  function handleTickerKeyDown(e: KeyboardEvent<HTMLInputElement>): void {
    if (e.key === "Enter") {
      e.preventDefault();
      validateAndAddTicker();
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100/50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate("/datasets")}
            className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Datasets
          </button>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-amber-500" />
            Create New Dataset
          </h1>
          <p className="text-slate-600 mt-2">
            Configure your dataset with companies, time range, and data sources.
            You'll be able to start data collection after creation.
          </p>
        </div>

        {/* Success message */}
        {success && (
          <div className="mb-6 p-4 rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-800 flex items-center gap-3 animate-in fade-in slide-in-from-top-2 duration-300">
            <CheckCircle2 className="w-5 h-5" />
            <div>
              <div className="font-medium">Dataset created successfully!</div>
              <div className="text-sm mt-0.5">
                Redirecting to datasets page...
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 rounded-xl border border-rose-200 bg-rose-50 text-rose-800">
            {error}
          </div>
        )}

        {/* Main form */}
        <div className="space-y-6">
          {/* Basic Information */}
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              Basic Information
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Dataset Name
                  <span className="text-slate-500 font-normal ml-2">
                    (optional)
                  </span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Tech Giants 2015-2025"
                  className="w-full rounded-xl border border-slate-300 px-4 py-2.5 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-black/10 focus:border-black transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Description
                  <span className="text-slate-500 font-normal ml-2">
                    (optional)
                  </span>
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  placeholder="Brief description of what this dataset contains"
                  className="w-full rounded-xl border border-slate-300 px-4 py-2.5 resize-y bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-black/10 focus:border-black transition-colors"
                />
              </div>
            </div>
          </section>

          {/* Companies */}
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                <Building2 className="w-5 h-5" />
                Companies
              </h2>
              <div className="text-sm text-slate-500">
                {companies.length}{" "}
                {companies.length === 1 ? "company" : "companies"} added
              </div>
            </div>

            {/* Ticker input */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Add Companies by Ticker
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={tickerInput}
                  onChange={(e) => setTickerInput(e.target.value.toUpperCase())}
                  onKeyDown={handleTickerKeyDown}
                  placeholder="Enter ticker (e.g., AAPL)"
                  disabled={validating}
                  className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-black/10 focus:border-black transition-colors disabled:bg-slate-50 disabled:text-slate-500"
                  style={{ textTransform: "uppercase" }}
                />
                <button
                  onClick={() => validateAndAddTicker()}
                  disabled={!tickerInput.trim() || validating}
                  className={cls(
                    "px-4 py-2.5 rounded-xl font-medium transition-colors",
                    !tickerInput.trim() || validating
                      ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                      : "bg-black text-white hover:bg-black/90"
                  )}
                >
                  {validating ? "Validating..." : "Add"}
                </button>
              </div>
              <div className="mt-2 flex items-start gap-2 text-xs text-slate-500">
                <Info className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                <span>
                  Press Enter to quickly add companies. We'll validate them
                  automatically.
                </span>
              </div>
            </div>

            {/* Companies list */}
            <div className="rounded-xl border border-slate-200 overflow-hidden">
              {companies.length === 0 ? (
                <div className="p-8 text-center text-slate-500">
                  <Building2 className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                  <div className="text-sm">No companies yet</div>
                  <div className="text-xs mt-1">
                    Add at least one company to continue
                  </div>
                </div>
              ) : (
                <ul className="divide-y divide-slate-100">
                  {companies.map((company) => (
                    <li
                      key={company.ticker}
                      className="px-4 py-3 flex items-center justify-between bg-white hover:bg-slate-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <div>
                          <div className="font-medium text-slate-900">
                            {company.ticker}
                          </div>
                          <div className="text-sm text-slate-600">
                            {company.name}
                          </div>
                          {(company.exchange || company.currency) && (
                            <div className="text-xs text-slate-400 mt-0.5">
                              {[company.exchange, company.currency]
                                .filter(Boolean)
                                .join(" · ")}
                            </div>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => removeCompany(company.ticker)}
                        className="p-2 rounded-lg border border-slate-200 text-rose-600 hover:bg-rose-50 transition-colors"
                        title="Remove"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          {/* Configuration */}
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              Configuration
            </h2>
            <div className="space-y-6">
              {/* History window */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Historical Data Range: {yearsBack} years
                </label>
                <input
                  type="range"
                  min={1}
                  max={50}
                  value={yearsBack}
                  onChange={(e) => setYearsBack(Number(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-black"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>1 year</span>
                  <span>25 years</span>
                  <span>50 years</span>
                </div>
              </div>

              {/* Data sources */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Data Sources
                </label>
                <div className="space-y-2">
                  <label className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 hover:border-slate-300 cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      checked={includeAnalyst}
                      onChange={(e) => setIncludeAnalyst(e.target.checked)}
                      className="mt-0.5"
                    />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-slate-900">
                        Analyst Estimates
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        Include analyst revenue and earnings estimates
                      </div>
                    </div>
                  </label>
                  <label className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 hover:border-slate-300 cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      checked={includeInstitutional}
                      onChange={(e) =>
                        setIncludeInstitutional(e.target.checked)
                      }
                      className="mt-0.5"
                    />
                    <div className="flex-1">
                      <div className="text-sm font-medium text-slate-900">
                        Institutional & Insider Data
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        Include institutional ownership and insider trading data
                      </div>
                    </div>
                  </label>
                </div>
              </div>

              {/* Visibility */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Visibility
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <label
                    className={cls(
                      "flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all",
                      visibility === "private"
                        ? "border-black bg-black/5"
                        : "border-slate-200 hover:border-slate-300"
                    )}
                  >
                    <input
                      type="radio"
                      name="visibility"
                      value="private"
                      checked={visibility === "private"}
                      onChange={() => setVisibility("private")}
                      className="mt-0.5"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 text-sm font-medium text-slate-900">
                        <Shield className="w-4 h-4" />
                        Private
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        Only you can access this dataset
                      </div>
                    </div>
                  </label>
                  <label
                    className={cls(
                      "flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all",
                      visibility === "public"
                        ? "border-black bg-black/5"
                        : "border-slate-200 hover:border-slate-300"
                    )}
                  >
                    <input
                      type="radio"
                      name="visibility"
                      value="public"
                      checked={visibility === "public"}
                      onChange={() => setVisibility("public")}
                      className="mt-0.5"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 text-sm font-medium text-slate-900">
                        <Users className="w-4 h-4" />
                        Public
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        Anyone with the link can view
                      </div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </section>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4">
            <button
              onClick={() => navigate("/datasets")}
              className="px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={!canSubmit}
              className={cls(
                "px-6 py-2.5 rounded-xl font-medium transition-all shadow-sm",
                canSubmit
                  ? "bg-black text-white hover:bg-black/90 hover:shadow-md"
                  : "bg-slate-100 text-slate-400 cursor-not-allowed"
              )}
            >
              {creating ? "Creating..." : "Create Dataset"}
            </button>
          </div>
        </div>

        {/* Footer info */}
        <div className="mt-8 p-4 rounded-xl bg-slate-100 text-sm text-slate-600">
          <div className="font-medium mb-1">What happens next?</div>
          <ul className="space-y-1 text-xs">
            <li>• Your dataset will be created with status "Created"</li>
            <li>• You can start data collection from the datasets page</li>
            <li>
              • Collection typically takes 2-5 minutes depending on companies
              and date range
            </li>
            <li>
              • Once ready, you'll be able to explore and visualize the data
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
