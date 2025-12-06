import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { analysisAPI, authAPI } from '../services/api';
import { Plus, Search, Clock, CheckCircle2, AlertCircle, Trash2, Edit2, X, Check, XCircle, Loader2, Grid3x3, List, BarChart3, FileText } from 'lucide-react';

/**
 * Dashboard.jsx - Professional Analysis Management Interface
 * 
 * Features:
 * - Beautiful grid/list view toggle
 * - Status-based filtering with rich indicators
 * - Search and inline name editing
 * - Email verification banner for local users
 * - Responsive design with empty states
 * - Status progress tracking
 */

function cls(...classes) {
  return classes.filter(Boolean).join(" ");
}

// ============================================================================
// STATUS CONFIGURATION
// ============================================================================

const statusConfig = {
  created: {
    label: "Created",
    color: "slate",
    icon: Clock,
    bgClass: "bg-slate-100",
    textClass: "text-slate-700",
    borderClass: "border-slate-200",
    description: "Ready to start",
  },
  collecting: {
    label: "Collecting",
    color: "blue",
    icon: Loader2,
    bgClass: "bg-blue-100",
    textClass: "text-blue-800",
    borderClass: "border-blue-200",
    description: "Gathering data",
    animate: true,
  },
  collection_complete: {
    label: "Collection Complete",
    color: "amber",
    icon: AlertCircle,
    bgClass: "bg-amber-100",
    textClass: "text-amber-800",
    borderClass: "border-amber-200",
    description: "Data ready for analysis",
  },
  generating: {
    label: "Generating",
    color: "blue",
    icon: Loader2,
    bgClass: "bg-blue-100",
    textClass: "text-blue-800",
    borderClass: "border-blue-200",
    description: "Creating analysis",
    animate: true,
  },
  complete: {
    label: "Complete",
    color: "emerald",
    icon: CheckCircle2,
    bgClass: "bg-emerald-100",
    textClass: "text-emerald-800",
    borderClass: "border-emerald-200",
    description: "Analysis ready",
  },
  failed: {
    label: "Failed",
    color: "rose",
    icon: XCircle,
    bgClass: "bg-rose-100",
    textClass: "text-rose-800",
    borderClass: "border-rose-200",
    description: "Error occurred",
  },
};

// ============================================================================
// STATUS CHIP COMPONENT
// ============================================================================

function StatusChip({ status, progress }) {
  const config = statusConfig[status] || statusConfig.created;
  const Icon = config.icon;

  return (
    <div className={cls(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border",
      config.bgClass,
      config.textClass,
      config.borderClass
    )}>
      <Icon className={cls("w-3.5 h-3.5", config.animate && "animate-spin")} />
      <span>{config.label}</span>
      {(status === "collecting" || status === "generating") && progress !== undefined && progress < 100 && (
        <span className="opacity-75">({progress}%)</span>
      )}
    </div>
  );
}

// ============================================================================
// EMPTY STATE COMPONENT
// ============================================================================

function EmptyState({ onCreate, hasFilters }) {
  if (hasFilters) {
    return (
      <div className="text-center py-16">
        <div className="mx-auto w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center">
          <Search className="w-8 h-8 text-slate-400" />
        </div>
        <h3 className="mt-4 text-lg font-medium text-slate-900">No analyses found</h3>
        <p className="mt-2 text-sm text-slate-700">Try adjusting your search query</p>
      </div>
    );
  }

  return (
    <div className="text-center py-20">
      <div className="mx-auto w-20 h-20 rounded-3xl bg-gradient-to-br from-slate-100 to-slate-50 flex items-center justify-center shadow-sm">
        <BarChart3 className="w-10 h-10 text-slate-400" />
      </div>
      <h2 className="mt-6 text-2xl font-semibold text-slate-900">No analyses yet</h2>
      <p className="mt-3 text-slate-700 max-w-md mx-auto">
        Create your first financial analysis to explore comprehensive insights with
        20+ analytical sections and interactive visualizations.
      </p>
      <button
        onClick={onCreate}
        className="mt-8 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-black text-white hover:bg-black/90 transition-colors shadow-sm"
      >
        <Plus className="w-4 h-4" />
        Create Your First Analysis
      </button>
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto text-left">
        <div className="p-4 rounded-xl border border-slate-200 bg-white">
          <FileText className="w-5 h-5 text-slate-700 mb-2" />
          <div className="text-sm font-medium text-slate-900">20+ Sections</div>
          <div className="text-xs text-slate-700 mt-1">
            Comprehensive financial and equity analysis
          </div>
        </div>
        <div className="p-4 rounded-xl border border-slate-200 bg-white">
          <BarChart3 className="w-5 h-5 text-slate-700 mb-2" />
          <div className="text-sm font-medium text-slate-900">Interactive Charts</div>
          <div className="text-xs text-slate-700 mt-1">
            Dynamic visualizations with Plotly
          </div>
        </div>
        <div className="p-4 rounded-xl border border-slate-200 bg-white">
          <CheckCircle2 className="w-5 h-5 text-slate-700 mb-2" />
          <div className="text-sm font-medium text-slate-900">Real-time Updates</div>
          <div className="text-xs text-slate-700 mt-1">
            WebSocket-powered progress tracking
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// ANALYSIS CARD COMPONENT (Grid View)
// ============================================================================

function AnalysisCard({ analysis, onOpen, onEdit, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(analysis.name || 'Untitled Analysis');

  const handleSave = async (e) => {
    e.stopPropagation();
    if (!editName.trim()) {
      alert('Name cannot be empty');
      return;
    }
    await onEdit(analysis.analysis_id, editName);
    setIsEditing(false);
  };

  const handleCancel = (e) => {
    e.stopPropagation();
    setEditName(analysis.name || 'Untitled Analysis');
    setIsEditing(false);
  };

//  const canView = analysis.status === 'complete';

  return (
    <article 
      className="group rounded-2xl border border-slate-200 bg-white p-5 hover:shadow-lg hover:border-slate-300 transition-all duration-200 cursor-pointer"
      onClick={() => onOpen(analysis)}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {isEditing ? (
            <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onClick={(e) => e.stopPropagation()}
                className="flex-1 px-2 py-1 border-2 border-black rounded-lg text-sm font-semibold focus:outline-none"
                autoFocus
              />
              <button
                onClick={handleSave}
                className="p-1.5 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600 transition-colors"
              >
                <Check className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleCancel}
                className="p-1.5 rounded-lg bg-rose-500 text-white hover:bg-rose-600 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-slate-900 truncate group-hover:text-black transition-colors">
                {analysis.name || 'Untitled Analysis'}
              </h3>
              <button
                onClick={(e) => { e.stopPropagation(); setIsEditing(true); }}
                className="opacity-0 group-hover:opacity-100 p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-all"
              >
                <Edit2 className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Companies */}
      {analysis.companies && analysis.companies.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {analysis.companies.map((company, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-xs font-medium"
            >
              {company.ticker}
            </span>
          ))}
        </div>
      )}

      {/* Status & Progress */}
      <div className="mt-4">
        <StatusChip status={analysis.status} progress={analysis.progress} />
      </div>

      {/* Progress Bar */}
      {analysis.progress !== undefined && analysis.progress < 100 && (
        <div className="mt-4">
          <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${analysis.progress}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 mt-1.5">{analysis.progress}% complete</p>
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          {formatRelative(analysis.created_at)}
        </span>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(analysis.analysis_id); }}
          className="px-2.5 py-1.5 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 transition-colors text-xs font-medium flex items-center gap-1.5"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Delete
        </button>
      </div>
    </article>
  );
}

// ============================================================================
// ANALYSIS ROW COMPONENT (List View)
// ============================================================================

function AnalysisRow({ analysis, onOpen, onEdit, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(analysis.name || 'Untitled Analysis');

  const handleSave = async (e) => {
    e.stopPropagation();
    if (!editName.trim()) {
      alert('Name cannot be empty');
      return;
    }
    await onEdit(analysis.analysis_id, editName);
    setIsEditing(false);
  };

  const handleCancel = (e) => {
    e.stopPropagation();
    setEditName(analysis.name || 'Untitled Analysis');
    setIsEditing(false);
  };

  return (
    <tr 
      className="border-b border-slate-200 hover:bg-slate-50 transition-colors cursor-pointer"
      onClick={() => onOpen(analysis)}
    >
      <td className="px-4 py-3">
        {isEditing ? (
          <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              className="flex-1 px-2 py-1 border-2 border-black rounded-lg text-sm font-medium focus:outline-none"
              autoFocus
            />
            <button
              onClick={handleSave}
              className="p-1 rounded-lg bg-emerald-500 text-white hover:bg-emerald-600"
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleCancel}
              className="p-1 rounded-lg bg-rose-500 text-white hover:bg-rose-600"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="font-medium text-slate-900">{analysis.name || 'Untitled Analysis'}</span>
            <button
              onClick={(e) => { e.stopPropagation(); setIsEditing(true); }}
              className="p-1 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-700 transition-all"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </td>
      <td className="px-4 py-3">
        <StatusChip status={analysis.status} progress={analysis.progress} />
      </td>
      <td className="px-4 py-3">
        <div className="flex flex-wrap gap-1.5">
          {analysis.companies?.map((company, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-xs font-medium"
            >
              {company.ticker}
            </span>
          ))}
        </div>
      </td>
      <td className="px-4 py-3 text-sm text-slate-700">
        {analysis.progress !== undefined && analysis.progress < 100 ? (
          <div className="flex items-center gap-2">
            <div className="flex-1 w-20 h-1.5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all"
                style={{ width: `${analysis.progress}%` }}
              />
            </div>
            <span className="text-xs">{analysis.progress}%</span>
          </div>
        ) : (
          '—'
        )}
      </td>
      <td className="px-4 py-3 text-sm text-slate-700">
        {formatRelative(analysis.created_at)}
      </td>
      <td className="px-4 py-3 text-right">
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(analysis.analysis_id); }}
          className="px-2.5 py-1.5 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 transition-colors text-xs font-medium inline-flex items-center gap-1.5"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Delete
        </button>
      </td>
    </tr>
  );
}

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

const Dashboard = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  
  const navigate = useNavigate();
  const { user } = useAuth();

  // State for verification banner
  const [showBanner, setShowBanner] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);
  const [bannerMessage, setBannerMessage] = useState('');

  // Check if user needs to verify email
  useEffect(() => {
    if (user && !user.email_verified && user.auth_provider === 'local') {
      setShowBanner(true);
    }
  }, [user]);

  // Handler for resending verification email
  const handleResendVerification = async () => {
    setResendingEmail(true);
    setBannerMessage('');
    
    try {
      await authAPI.resendVerification(user.email);
      setBannerMessage('Verification email sent! Please check your inbox.');
    } catch (error) {
      setBannerMessage(error.response?.data?.detail || 'Failed to resend email. Please try again.');
    } finally {
      setResendingEmail(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const response = await analysisAPI.list();
      setAnalyses(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load analyses');
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this analysis?')) {
      try {
        await analysisAPI.delete(id);
        setAnalyses(analyses.filter(a => a.analysis_id !== id));
      } catch (err) {
        alert('Failed to delete analysis');
      }
    }
  };

  const handleEdit = async (id, newName) => {
    try {
      await analysisAPI.updateName(id, newName);
      setAnalyses(analyses.map(a => 
        a.analysis_id === id ? { ...a, name: newName } : a
      ));
    } catch (err) {
      alert('Failed to update name');
    }
  };

  const handleOpen = (analysis) => {
    navigate(`/analysis/${analysis.analysis_id}`);
  };

  const filteredAnalyses = analyses.filter(a => 
    a.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.companies?.some(c => c.ticker.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const summary = {
    total: analyses.length,
    complete: analyses.filter(a => a.status === 'complete').length,
    generating: analyses.filter(a => a.status === 'generating').length,
    collecting: analyses.filter(a => a.status === 'collecting').length,
    collection_complete: analyses.filter(a => a.status === 'collection_complete').length,
    failed: analyses.filter(a => a.status === 'failed').length,
    created: analyses.filter(a => a.status === 'created').length,
  };

  const showEmpty = filteredAnalyses.length === 0;
  const hasFilters = searchTerm.length > 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-slate-700 animate-spin mx-auto mb-3" />
          <p className="text-slate-700 font-medium">Loading analyses...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="px-6 py-8">
        {/* Verification Banner */}
        {showBanner && (
          <div className="mb-6 rounded-2xl border-l-4 border-amber-500 bg-amber-50 p-4">
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-amber-900 mb-1">
                  📧 Email not verified
                </div>
                <div className="text-sm text-amber-800">
                  Please check your inbox and verify your email address to access all features.
                </div>
                {bannerMessage && (
                  <div className={cls(
                    "mt-2 text-sm",
                    bannerMessage.includes('Failed') ? "text-rose-700" : "text-emerald-700"
                  )}>
                    {bannerMessage}
                  </div>
                )}
              </div>
              
              <div className="flex gap-2 flex-shrink-0">
                <button
                  onClick={handleResendVerification}
                  disabled={resendingEmail}
                  className={cls(
                    "px-4 py-2 rounded-lg font-medium text-sm transition-colors",
                    resendingEmail 
                      ? "bg-amber-400 text-white cursor-not-allowed" 
                      : "bg-amber-500 text-white hover:bg-amber-600"
                  )}
                >
                  {resendingEmail ? 'Sending...' : 'Resend Email'}
                </button>
                <button
                  onClick={() => setShowBanner(false)}
                  className="px-4 py-2 rounded-lg bg-white border border-amber-200 text-amber-800 hover:bg-amber-50 transition-colors font-medium text-sm"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Financial Analyses</h1>
            <p className="text-slate-700 mt-1">Comprehensive insights across 20+ analytical sections</p>
          </div>
          <button
            onClick={() => navigate('/analysis/create')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-black text-white hover:bg-black/90 transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            New Analysis
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 flex items-center gap-3 text-rose-800">
            <XCircle className="w-5 h-5 flex-shrink-0" />
            <div className="flex-1">{error}</div>
          </div>
        )}

        {/* Summary Cards */}
        {!showEmpty && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
            <div className="p-4 rounded-xl border border-slate-200 bg-white">
              <div className="text-2xl font-bold text-slate-900">{summary.total}</div>
              <div className="text-sm text-slate-700 mt-1">Total</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-200 bg-white">
              <div className="text-2xl font-bold text-emerald-600">{summary.complete}</div>
              <div className="text-sm text-slate-700 mt-1">Complete</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-200 bg-white">
              <div className="text-2xl font-bold text-blue-600">{summary.generating}</div>
              <div className="text-sm text-slate-700 mt-1">Generating</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-200 bg-white">
              <div className="text-2xl font-bold text-blue-600">{summary.collecting}</div>
              <div className="text-sm text-slate-700 mt-1">Collecting</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-200 bg-white">
              <div className="text-2xl font-bold text-amber-600">{summary.collection_complete}</div>
              <div className="text-sm text-slate-700 mt-1">Collected</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-200 bg-white">
              <div className="text-2xl font-bold text-slate-700">{summary.created}</div>
              <div className="text-sm text-slate-700 mt-1">Created</div>
            </div>
            <div className="p-4 rounded-xl border border-slate-200 bg-white">
              <div className="text-2xl font-bold text-rose-600">{summary.failed}</div>
              <div className="text-sm text-slate-700 mt-1">Failed</div>
            </div>
          </div>
        )}

        {/* Filters & View Toggle */}
        {!showEmpty && (
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search analyses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-black/5"
              />
            </div>

            {/* View toggle */}
            <div className="flex items-center gap-1 p-1 rounded-xl border border-slate-200 bg-white">
              <button
                onClick={() => setViewMode('grid')}
                className={cls(
                  "p-2 rounded-lg transition-colors",
                  viewMode === 'grid' ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-50"
                )}
              >
                <Grid3x3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cls(
                  "p-2 rounded-lg transition-colors",
                  viewMode === 'list' ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-50"
                )}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Empty state or content */}
        {showEmpty ? (
          <EmptyState
            onCreate={() => navigate('/analysis/create')}
            hasFilters={hasFilters}
          />
        ) : viewMode === 'grid' ? (
          /* Grid view */
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredAnalyses.map((analysis) => (
              <AnalysisCard
                key={analysis.analysis_id}
                analysis={analysis}
                onOpen={handleOpen}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        ) : (
          /* List view */
          <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Analysis Name
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Companies
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredAnalyses.map((analysis) => (
                  <AnalysisRow
                    key={analysis.analysis_id}
                    analysis={analysis}
                    onOpen={handleOpen}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatRelative(dateStr) {
  if (!dateStr) return "just now";
  
  try {
    const date = new Date(dateStr);
    const now = Date.now();
    const diff = now - date.getTime();
    
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return "just now";
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    
    if (days < 30) return `${Math.floor(days / 7)}w ago`;
    
    const date_obj = new Date(dateStr);
    return date_obj.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return "—";
  }
}

export default Dashboard;