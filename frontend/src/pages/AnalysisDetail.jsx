// frontend/src/pages/AnalysisDetail.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { analysisAPI } from '../services/api';
import { 
  TrendingUp, LogOut, ArrowLeft, Play, RefreshCw, Download,
  CheckCircle, Clock, XCircle,  Loader, ChevronRight
} from 'lucide-react';

const AnalysisDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [analysis, setAnalysis] = useState(null);
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(null);

  // Fetch analysis details
  const fetchAnalysis = useCallback(async () => {
    try {
      const response = await analysisAPI.get(id);
      setAnalysis(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load analysis');
    }
  }, [id]);

  const fetchSections = useCallback(async () => {
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

  // Polling - refresh every 3 seconds if not complete
  // Polling for analysis status (Phase A - during collecting)
  useEffect(() => {
    if (!analysis) return;
  
    const shouldPoll = analysis.status !== 'complete' && 
                       analysis.status !== 'failed' &&
                       analysis.status !== 'collection_complete' &&
                       analysis.status !== 'created';
  
    if (shouldPoll) {
      const interval = setInterval(() => {
        fetchAnalysis();
        fetchSections();
      }, 3000);
  
      return () => clearInterval(interval);
    }
  }, [analysis?.status, fetchAnalysis, fetchSections, analysis]);

  // Action handlers
  const handleStartCollection = async () => {
    setActionLoading('collection');
    try {
      await analysisAPI.startCollection(id);
      await fetchAnalysis();
    } catch (err) {
      alert('Failed to start collection: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(null);
    }
  };

  const handleStartAnalysis = async () => {
    setActionLoading('analysis');
    try {
      await analysisAPI.startAnalysis(id);
      await fetchAnalysis();
    } catch (err) {
      alert('Failed to start analysis: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(null);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset will delete all data and sections. Continue?')) return;
    setActionLoading('reset');
    try {
      await analysisAPI.reset(id);
      await Promise.all([fetchAnalysis(), fetchSections()]);
    } catch (err) {
      alert('Failed to reset: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(null);
    }
  };

  const handleRestart = async () => {
    if (!window.confirm('Restart will regenerate all sections. Continue?')) return;
    setActionLoading('restart');
    try {
      await analysisAPI.restartAnalysis(id);
      await Promise.all([fetchAnalysis(), fetchSections()]);
    } catch (err) {
      alert('Failed to restart: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(null);
    }
  };

  const handleDownload = async () => {
    setActionLoading('download');
    try {
      const response = await analysisAPI.downloadRawData(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${analysis.name || 'analysis'}_raw_data.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusIcon = (status) => {
    const icons = {
      complete: <CheckCircle size={20} style={{ color: '#10b981' }} />,
      processing: <Loader size={20} style={{ color: '#3b82f6', animation: 'spin 1s linear infinite' }} />,
      pending: <Clock size={20} style={{ color: '#6b7280' }} />,
      failed: <XCircle size={20} style={{ color: '#ef4444' }} />
    };
    return icons[status] || icons.pending;
  };

  const getStatusBadge = (status) => {
    const styles = {
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
      {/* Header */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '1rem 5%'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: '1400px',
          margin: '0 auto'
        }}>
          <div 
            onClick={() => navigate('/dashboard')}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '0.5rem', 
              fontSize: '1.5rem', 
              fontWeight: 'bold', 
              color: '#667eea',
              cursor: 'pointer'
            }}>
            <TrendingUp size={28} />
            FinanceHub
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ color: '#6b7280' }}>Welcome, {user?.full_name}</span>
            <button onClick={logout} style={{
              padding: '0.6rem 1.2rem',
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: '600'
            }}>
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </div>

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
    </div>
  );
};

export default AnalysisDetail;