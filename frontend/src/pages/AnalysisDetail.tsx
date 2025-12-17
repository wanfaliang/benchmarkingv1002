// frontend/src/pages/AnalysisDetail.tsx
import React, { useState, useEffect, useCallback, CSSProperties } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import {
  ArrowLeft, Play, RefreshCw, Download,
  CheckCircle, Clock, XCircle, Loader, ChevronRight
} from 'lucide-react';
import type { Analysis, AnalysisSection, AnalysisStatus, SectionStatus } from '../types';

/**
 * AnalysisDetail.tsx - Analysis Detail View with Polling
 *
 * Features:
 * - View analysis status and progress
 * - Start collection/analysis
 * - Download raw data
 * - Navigate to section viewer
 * - Polling-based progress updates
 */

type ActionType = 'collection' | 'analysis' | 'reset' | 'restart' | 'download' | null;

interface StatusStyle {
  bg: string;
  color: string;
}

const AnalysisDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [sections, setSections] = useState<AnalysisSection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState<ActionType>(null);
  const [showCollectionModal, setShowCollectionModal] = useState(false);

  // Fetch analysis details
  const fetchAnalysis = useCallback(async () => {
    if (!id) return;
    try {
      const response = await analysisAPI.get(id);
      setAnalysis(response.data as Analysis);
      setError('');
    } catch {
      setError('Failed to load analysis');
    }
  }, [id]);

  const fetchSections = useCallback(async () => {
    if (!id) return;
    try {
      const response = await analysisAPI.getSections(id);
      setSections(response.data.sections || []);
    } catch (err) {
      console.error('Failed to load sections:', err);
    }
  }, [id]);

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      await Promise.all([fetchAnalysis(), fetchSections()]);
      setLoading(false);
    };
    loadData();
  }, [id, fetchAnalysis, fetchSections]);

  useEffect(() => {
    if (analysis?.status === 'collection_complete' && showCollectionModal) {
      setShowCollectionModal(false);
    }
  }, [analysis?.status, showCollectionModal]);

  // Polling for analysis status
  useEffect(() => {
    if (!analysis) return undefined;

    const shouldPoll = analysis.status !== 'complete' &&
      analysis.status !== 'failed' &&
      analysis.status !== 'collection_complete' &&
      analysis.status !== 'created';

    if (shouldPoll) {
      const interval = setInterval(() => {
        fetchAnalysis();
        fetchSections();
      }, 1500);

      return () => clearInterval(interval);
    }
    return undefined;
  }, [analysis?.status, fetchAnalysis, fetchSections, analysis]);

  // Action handlers
  const handleStartCollection = async () => {
    if (!id) return;
    setActionLoading('collection');
    setShowCollectionModal(true);
    try {
      await analysisAPI.startCollection(id);
      await fetchAnalysis();
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      alert('Failed to start collection: ' + (error.response?.data?.detail || error.message));
      setShowCollectionModal(false);
    } finally {
      setActionLoading(null);
    }
  };

  const handleStartAnalysis = async () => {
    if (!id) return;
    setActionLoading('analysis');
    try {
      await analysisAPI.startAnalysis(id);
      await fetchAnalysis();
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      alert('Failed to start analysis: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(null);
    }
  };

  const handleReset = async () => {
    if (!id) return;
    if (!window.confirm('Reset will delete all data and sections. Continue?')) return;
    setActionLoading('reset');
    try {
      await analysisAPI.reset(id);
      await Promise.all([fetchAnalysis(), fetchSections()]);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      alert('Failed to reset: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(null);
    }
  };

  const handleRestart = async () => {
    if (!id) return;
    if (!window.confirm('Restart will regenerate all sections. Continue?')) return;
    setActionLoading('restart');
    try {
      await analysisAPI.restartAnalysis(id);
      await Promise.all([fetchAnalysis(), fetchSections()]);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      alert('Failed to restart: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownload = async () => {
    if (!id || !analysis) return;
    setActionLoading('download');
    try {
      const response = await analysisAPI.downloadRawData(id);
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${analysis.name || 'analysis'}_raw_data.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      alert('Failed to download: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusIcon = (status: SectionStatus): React.ReactElement => {
    const iconStyle: CSSProperties = { animation: status === 'processing' ? 'spin 1s linear infinite' : undefined };
    const icons: Record<SectionStatus, React.ReactElement> = {
      complete: <CheckCircle size={20} style={{ color: '#10b981' }} />,
      processing: <Loader size={20} style={{ color: '#3b82f6', ...iconStyle }} />,
      pending: <Clock size={20} style={{ color: '#6b7280' }} />,
      failed: <XCircle size={20} style={{ color: '#ef4444' }} />
    };
    return icons[status] || icons.pending;
  };

  const getStatusBadge = (status: AnalysisStatus): React.ReactElement => {
    const styles: Record<AnalysisStatus, StatusStyle> = {
      complete: { bg: '#dcfce7', color: '#166534' },
      generating: { bg: '#dbeafe', color: '#1e40af' },
      collecting: { bg: '#dbeafe', color: '#1e40af' },
      collection_complete: { bg: '#fef3c7', color: '#92400e' },
      failed: { bg: '#fee2e2', color: '#991b1b' },
      created: { bg: '#f3f4f6', color: '#374151' }
    };
    const style = styles[status] || styles.created;
    return (
      <span style={{
        padding: '0.4rem 0.8rem',
        borderRadius: '20px',
        background: style.bg,
        color: style.color,
        fontSize: '0.85rem',
        fontWeight: '600'
      }}>
        {status.replace(/_/g, ' ').toUpperCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Loader size={40} style={{ color: '#667eea', animation: 'spin 1s linear infinite' }} />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: '#ef4444', marginBottom: '1rem' }}>{error || 'Analysis not found'}</p>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const completedSections = sections.filter(s => s.status === 'complete').length;
  const progressPercent = sections.length > 0 ? (completedSections / sections.length * 100) : 0;

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 5%' }}>
        {/* Back Button */}
        <button
          onClick={() => navigate('/dashboard')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            background: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: '1.5rem',
            color: '#6b7280',
            fontWeight: '600'
          }}
        >
          <ArrowLeft size={18} />
          Back to Dashboard
        </button>

        {/* Analysis Info */}
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          marginBottom: '1.5rem',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
            <div>
              <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '0.5rem' }}>
                {analysis.name || 'Untitled Analysis'}
              </h1>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                {analysis.companies?.map((company, idx) => (
                  <span key={idx} style={{
                    padding: '0.3rem 0.7rem',
                    background: '#f3f4f6',
                    borderRadius: '6px',
                    fontSize: '0.9rem',
                    fontWeight: '600',
                    color: '#374151'
                  }}>
                    {company.ticker}
                  </span>
                ))}
                <span style={{
                  padding: '0.3rem 0.7rem',
                  background: '#ede9fe',
                  borderRadius: '6px',
                  fontSize: '0.9rem',
                  fontWeight: '600',
                  color: '#6b21a8'
                }}>
                  {analysis.years_back} years
                </span>
              </div>
            </div>
            {getStatusBadge(analysis.status)}
          </div>

          {/* Progress Bar */}
          {analysis.status !== 'created' && analysis.status !== 'complete' && (
            <div style={{ marginTop: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: '600', color: '#374151' }}>
                  {analysis.phase === 'A' ? 'Data Collection' : 'Generating Sections'}
                </span>
                <span style={{ fontSize: '0.9rem', fontWeight: '600', color: '#667eea' }}>
                  {analysis.phase === 'B' ? `${completedSections}/${sections.length}` : `${analysis.progress}%`}
                </span>
              </div>
              <div style={{
                width: '100%',
                height: '12px',
                background: '#e5e7eb',
                borderRadius: '6px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${analysis.phase === 'B' ? progressPercent : analysis.progress}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #667eea, #764ba2)',
                  transition: 'width 0.5s'
                }} />
              </div>
            </div>
          )}

          {/* Metadata */}
          <div style={{
            marginTop: '1.5rem',
            paddingTop: '1.5rem',
            borderTop: '1px solid #e5e7eb',
            display: 'flex',
            gap: '2rem',
            fontSize: '0.875rem',
            color: '#6b7280'
          }}>
            <div>
              <strong>Created:</strong> {new Date(analysis.created_at).toLocaleString()}
            </div>
            {analysis.started_at && (
              <div>
                <strong>Started:</strong> {new Date(analysis.started_at).toLocaleString()}
              </div>
            )}
            {analysis.completed_at && (
              <div>
                <strong>Completed:</strong> {new Date(analysis.completed_at).toLocaleString()}
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{
          background: 'white',
          padding: '1.5rem',
          borderRadius: '12px',
          marginBottom: '1.5rem',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '1rem', color: '#1f2937' }}>
            Actions
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
            {analysis.status === 'created' && (
              <button
                onClick={handleStartCollection}
                disabled={actionLoading === 'collection'}
                style={{
                  padding: '0.75rem 1.25rem',
                  background: actionLoading === 'collection' ? '#d1d5db' : '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: actionLoading === 'collection' ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                {actionLoading === 'collection' ? <Loader size={18} className="spin" /> : <Play size={18} />}
                Start Collection
              </button>
            )}

            {analysis.status === 'collection_complete' && (
              <button
                onClick={handleStartAnalysis}
                disabled={actionLoading === 'analysis'}
                style={{
                  padding: '0.75rem 1.25rem',
                  background: actionLoading === 'analysis' ? '#d1d5db' : '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: actionLoading === 'analysis' ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                {actionLoading === 'analysis' ? <Loader size={18} className="spin" /> : <Play size={18} />}
                Start Analysis
              </button>
            )}

            {(analysis.status === 'collection_complete' || analysis.status === 'complete') && (
              <>
                <button
                  onClick={handleDownload}
                  disabled={actionLoading === 'download'}
                  style={{
                    padding: '0.75rem 1.25rem',
                    background: actionLoading === 'download' ? '#d1d5db' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: '600',
                    cursor: actionLoading === 'download' ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  {actionLoading === 'download' ? <Loader size={18} className="spin" /> : <Download size={18} />}
                  Download Data
                </button>

                <button
                  onClick={handleRestart}
                  disabled={actionLoading === 'restart'}
                  style={{
                    padding: '0.75rem 1.25rem',
                    background: actionLoading === 'restart' ? '#d1d5db' : '#f59e0b',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontWeight: '600',
                    cursor: actionLoading === 'restart' ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  {actionLoading === 'restart' ? <Loader size={18} className="spin" /> : <RefreshCw size={18} />}
                  Restart Analysis
                </button>
              </>
            )}

            <button
              onClick={handleReset}
              disabled={actionLoading === 'reset'}
              style={{
                padding: '0.75rem 1.25rem',
                background: actionLoading === 'reset' ? '#d1d5db' : '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: actionLoading === 'reset' ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              {actionLoading === 'reset' ? <Loader size={18} className="spin" /> : <RefreshCw size={18} />}
              Reset
            </button>
          </div>
        </div>

        {/* Sections List */}
        {sections.length > 0 && (
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '12px',
            border: '1px solid #e5e7eb'
          }}>
            <h3 style={{ fontSize: '1.3rem', fontWeight: '600', marginBottom: '1.5rem', color: '#1f2937' }}>
              Report Sections ({completedSections}/{sections.length} Complete)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {sections.map((section) => (
                <div
                  key={section.section_number}
                  onClick={() => section.status === 'complete' && navigate(`/analysis/${id}/section/${section.section_number}`)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '1rem',
                    background: section.status === 'complete' ? '#f9fafb' : 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    cursor: section.status === 'complete' ? 'pointer' : 'default',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    if (section.status === 'complete') {
                      e.currentTarget.style.background = '#f3f4f6';
                      e.currentTarget.style.borderColor = '#667eea';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = section.status === 'complete' ? '#f9fafb' : 'white';
                    e.currentTarget.style.borderColor = '#e5e7eb';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
                    {getStatusIcon(section.status)}
                    <div>
                      <div style={{ fontWeight: '600', color: '#1f2937', marginBottom: '0.25rem' }}>
                        Section {section.section_number}: {section.section_name}
                      </div>
                      {section.error_message && (
                        <div style={{ fontSize: '0.875rem', color: '#ef4444' }}>
                          Error: {section.error_message}
                        </div>
                      )}
                      {section.processing_time && (
                        <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                          Processing time: {section.processing_time.toFixed(2)}s
                        </div>
                      )}
                    </div>
                  </div>
                  {section.status === 'complete' && (
                    <ChevronRight size={20} style={{ color: '#667eea' }} />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          .spin {
            animation: spin 1s linear infinite;
          }
        `}
      </style>
      {showCollectionModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-8 text-center">
            {/* Animated loader with background */}
            <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center mb-4">
              <Loader className="w-8 h-8 text-indigo-600 animate-spin" />
            </div>

            {/* Title with proper contrast */}
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              Collecting Data...
            </h3>

            {/* Description */}
            <p className="text-slate-600 text-sm mb-6">
              This may take several minutes. You can close this window and check progress from the dashboard.
            </p>

            {/* Close button */}
            <button
              onClick={() => setShowCollectionModal(false)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisDetail;
