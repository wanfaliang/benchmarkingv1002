import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI, tickerAPI } from '../services/api';
import { Plus, X, AlertCircle, Loader2, CheckCircle2, ArrowLeft, Sparkles, Building2 } from 'lucide-react';

/**
 * CreateAnalysis.jsx - Professional Analysis Creation Interface
 * 
 * Features:
 * - Multi-step form with validation
 * - Real-time ticker validation
 * - Beautiful UI with helpful guidance
 * - Proper error handling
 * - Navigates to analysis detail on success
 */

function cls(...classes) {
  return classes.filter(Boolean).join(" ");
}

const CreateAnalysis = () => {
  const navigate = useNavigate();

  // Form state
  const [analysisName, setAnalysisName] = useState('');
  const [years, setYears] = useState(10);
  const [companies, setCompanies] = useState([]);
  
  const [tickerInput, setTickerInput] = useState('');
  const [adding, setAdding] = useState(false);
  const [tickerError, setTickerError] = useState('');
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Validation
  const canSubmit = useMemo(
    () => companies.length > 0 && !submitting && !adding,
    [companies.length, submitting, adding]
  );

  // Add ticker (validates in background, then adds if valid)
  const addTicker = async () => {
    if (!tickerInput.trim()) {
      setTickerError('Please enter a ticker');
      return;
    }

    const ticker = tickerInput.toUpperCase().trim();

    // Check for duplicates first
    if (companies.some(c => c.ticker === ticker)) {
      setTickerError('Ticker already added');
      return;
    }

    setAdding(true);
    setTickerError('');

    try {
      const response = await tickerAPI.validate(ticker);
      
      if (response.data.valid) {
        const newCompany = {
          ticker: response.data.symbol,
          name: response.data.name
        };
        setCompanies([...companies, newCompany]);
        setTickerInput('');
        setTickerError('');
      } else {
        setTickerError(`Invalid ticker: ${ticker}`);
      }
    } catch (err) {
      console.error('Validation error:', err);
      setTickerError('Failed to validate ticker');
    } finally {
      setAdding(false);
    }
  };

  // Remove ticker from list
  const removeTicker = (ticker) => {
    setCompanies(companies.filter(c => c.ticker !== ticker));
  };

  // Handle Enter key
  const handleTickerKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTicker();
    }
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (companies.length === 0) {
      setError('Please add at least one company');
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        companies: companies,
        years_back: years
      };

      // Only add name if provided
      if (analysisName.trim()) {
        payload.name = analysisName.trim();
      }

      const response = await analysisAPI.create(payload);
      
      // Success! Show message and redirect
      setSuccess(true);
      setTimeout(() => {
        navigate(`/analysis/${response.data.analysis_id}`);
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create analysis');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100/50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-indigo-500" />
            Create New Analysis
          </h1>
          <p className="text-slate-600 mt-2">
            Configure your financial analysis with companies and historical data range.
            Analysis will begin automatically after creation.
          </p>
        </div>

        {/* Success message */}
        {success && (
          <div className="mb-6 p-4 rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-800 flex items-center gap-3 animate-in fade-in slide-in-from-top-2 duration-300">
            <CheckCircle2 className="w-5 h-5" />
            <div>
              <div className="font-medium">Analysis created successfully!</div>
              <div className="text-sm mt-0.5">Redirecting to analysis page...</div>
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
        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            {/* Basic Information */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">
                Basic Information
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Analysis Name
                    <span className="text-slate-500 font-normal ml-2">(optional)</span>
                  </label>
                  <input
                    type="text"
                    value={analysisName}
                    onChange={(e) => setAnalysisName(e.target.value)}
                    placeholder="e.g., Tech Giants Q4 2024"
                    className="w-full rounded-xl border border-slate-300 px-4 py-2.5 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-black/10 focus:border-black transition-colors"
                  />
                  <p className="text-xs text-slate-500 mt-2">
                    Leave blank to auto-generate from tickers
                  </p>
                </div>
              </div>
            </section>

            {/* Companies */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <Building2 className="w-5 h-5" />
                Companies
                <span className="text-sm font-normal text-slate-500">
                  ({companies.length} added)
                </span>
              </h2>

              {/* Ticker Input */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Add Companies
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={tickerInput}
                    onChange={(e) => {
                      setTickerInput(e.target.value.toUpperCase());
                      setTickerError('');
                    }}
                    onKeyPress={handleTickerKeyPress}
                    placeholder="Enter ticker (e.g., AAPL)"
                    disabled={adding}
                    className={cls(
                      "flex-1 rounded-xl border px-4 py-2.5 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 transition-colors",
                      tickerError 
                        ? "border-rose-300 focus:ring-rose-500/20 focus:border-rose-500"
                        : "border-slate-300 focus:ring-black/10 focus:border-black"
                    )}
                  />
                  <button
                    type="button"
                    onClick={addTicker}
                    disabled={adding || !tickerInput.trim()}
                    className={cls(
                      "px-5 py-2.5 rounded-xl font-medium transition-all shadow-sm inline-flex items-center gap-2",
                      adding || !tickerInput.trim()
                        ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                        : "bg-black text-white hover:bg-black/90 hover:shadow-md"
                    )}
                  >
                    {adding ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4" />
                        Add
                      </>
                    )}
                  </button>
                </div>
                
                {tickerError && (
                  <p className="mt-2 text-sm text-rose-600 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {tickerError}
                  </p>
                )}
              </div>

              {/* Companies List */}
              <div className="rounded-xl border border-slate-200 bg-slate-50 overflow-hidden">
                {companies.length === 0 ? (
                  <div className="px-4 py-8 text-center text-slate-500">
                    <Building2 className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                    <div className="text-sm font-medium mb-1">No companies added yet</div>
                    <div className="text-xs">Add at least one company to continue</div>
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
                            <div className="text-sm text-slate-600">{company.name}</div>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeTicker(company.ticker)}
                          className="p-2 rounded-lg border border-slate-200 text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Remove"
                        >
                          <X className="w-4 h-4" />
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
                    Historical Data Range: <span className="text-indigo-600 font-semibold">{years} years</span>
                  </label>
                  <input
                    type="range"
                    min={1}
                    max={50}
                    value={years}
                    onChange={(e) => setYears(Number(e.target.value))}
                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-black"
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>1 year</span>
                    <span>25 years</span>
                    <span>50 years</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!canSubmit}
                className={cls(
                  "px-6 py-2.5 rounded-xl font-medium transition-all shadow-sm",
                  canSubmit
                    ? "bg-black text-white hover:bg-black/90 hover:shadow-md"
                    : "bg-slate-100 text-slate-400 cursor-not-allowed"
                )}
              >
                {submitting ? 'Creating Analysis...' : 'Create Analysis'}
              </button>
            </div>
          </div>
        </form>

        {/* Footer info */}
        <div className="mt-8 p-4 rounded-xl bg-slate-100 text-sm text-slate-600">
          <div className="font-medium mb-1">What happens next?</div>
          <ul className="space-y-1 text-xs">
            <li>• Your analysis will be created and data collection will begin automatically</li>
            <li>• Collection typically takes 2-5 minutes depending on companies and date range</li>
            <li>• Analysis generation with 20+ sections will begin after collection completes</li>
            <li>• You'll receive real-time progress updates via WebSocket</li>
            <li>• Once complete, you can view comprehensive insights and interactive visualizations</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CreateAnalysis;