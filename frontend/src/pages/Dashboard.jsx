import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { analysisAPI, authAPI } from '../services/api';
import { Plus, Search, Clock, CheckCircle, AlertCircle, Trash2, Edit2, X, Check } from 'lucide-react';

const Dashboard = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState('');
  
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

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this analysis?')) {
      try {
        await analysisAPI.delete(id);
        setAnalyses(analyses.filter(a => a.analysis_id !== id));
      } catch (err) {
        alert('Failed to delete analysis');
      }
    }
  };

  const startEditName = (analysis, e) => {
    e.stopPropagation();
    setEditingId(analysis.analysis_id);
    setEditingName(analysis.name || 'Untitled Analysis');
  };

  const cancelEditName = (e) => {
    e.stopPropagation();
    setEditingId(null);
    setEditingName('');
  };

  const saveEditName = async (id, e) => {
    e.stopPropagation();
    if (!editingName.trim()) {
      alert('Name cannot be empty');
      return;
    }

    try {
      await analysisAPI.updateName(id, editingName);
      setAnalyses(analyses.map(a => 
        a.analysis_id === id ? { ...a, name: editingName } : a
      ));
      setEditingId(null);
      setEditingName('');
    } catch (err) {
      alert('Failed to update name');
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      complete: { bg: '#dcfce7', color: '#166534', icon: <CheckCircle size={16} /> },
      generating: { bg: '#dbeafe', color: '#1e40af', icon: <Clock size={16} /> },
      collecting: { bg: '#dbeafe', color: '#1e40af', icon: <Clock size={16} /> },
      collection_complete: { bg: '#fef3c7', color: '#92400e', icon: <AlertCircle size={16} /> },
      failed: { bg: '#fee2e2', color: '#991b1b', icon: <AlertCircle size={16} /> },
      created: { bg: '#f3f4f6', color: '#374151', icon: <Clock size={16} /> }
    };

    const style = styles[status] || styles.created;

    return (
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.4rem 0.8rem',
        borderRadius: '20px',
        background: style.bg,
        color: style.color,
        fontSize: '0.85rem',
        fontWeight: '600'
      }}>
        {style.icon}
        {status.replace(/_/g, ' ').toUpperCase()}
      </div>
    );
  };

  const filteredAnalyses = analyses.filter(a => 
    a.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.companies?.some(c => c.ticker.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <p style={{ fontSize: '1.2rem', color: '#667eea' }}>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--section-bg)' }}>
      {/* REMOVED OLD HEADER - Now using Header component from App.js */}

      {/* Main Content */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem 5%' }}>
        {/* Verification Banner */}
        {showBanner && (
          <div style={{
            background: '#fef3c7',
            borderLeft: '4px solid #f59e0b',
            padding: '1rem',
            marginBottom: '2rem',
            borderRadius: '8px'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1rem'
            }}>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <div style={{ 
                  fontWeight: '600', 
                  color: '#92400e',
                  marginBottom: '0.25rem' 
                }}>
                  📧 Email not verified
                </div>
                <div style={{ fontSize: '0.9rem', color: '#78350f' }}>
                  Please check your inbox and verify your email address to access all features.
                </div>
                {bannerMessage && (
                  <div style={{
                    marginTop: '0.5rem',
                    fontSize: '0.85rem',
                    color: bannerMessage.includes('Failed') ? '#dc2626' : '#059669'
                  }}>
                    {bannerMessage}
                  </div>
                )}
              </div>
              
              <div style={{ 
                display: 'flex', 
                gap: '0.5rem',
                flexShrink: 0 
              }}>
                <button
                  onClick={handleResendVerification}
                  disabled={resendingEmail}
                  style={{
                    padding: '0.5rem 1rem',
                    background: resendingEmail ? '#d97706' : '#f59e0b',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: resendingEmail ? 'not-allowed' : 'pointer',
                    fontWeight: '600',
                    fontSize: '0.9rem',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {resendingEmail ? 'Sending...' : 'Resend Email'}
                </button>
                <button
                  onClick={() => setShowBanner(false)}
                  style={{
                    padding: '0.5rem 1rem',
                    background: 'transparent',
                    color: '#92400e',
                    border: '1px solid #f59e0b',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.9rem'
                  }}
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Top Bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-color)' }}>
            My Analyses
          </h1>
          <button
            onClick={() => navigate('/analysis/create')}
            style={{
              padding: '0.8rem 1.5rem',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Plus size={20} />
            New Analysis
          </button>
        </div>

        {/* Search */}
        <div style={{ marginBottom: '2rem', position: 'relative' }}>
          <Search size={20} style={{
            position: 'absolute',
            left: '1rem',
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#9ca3af'
          }} />
          <input
            type="text"
            placeholder="Search by name or ticker..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.8rem 1rem 0.8rem 3rem',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              fontSize: '1rem',
              background: 'var(--header-bg)',
              color: 'var(--text-color)'
            }}
          />
        </div>

        {/* Error */}
        {error && (
          <div style={{
            background: '#fee2e2',
            color: '#dc2626',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1rem'
          }}>
            {error}
          </div>
        )}

        {/* Analyses Grid */}
        {filteredAnalyses.length === 0 ? (
          <div style={{
            background: 'var(--header-bg)',
            padding: '4rem',
            borderRadius: '12px',
            textAlign: 'center',
            border: '2px dashed var(--border-color)'
          }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', marginBottom: '1rem' }}>
              No analyses found
            </p>
            <button
              onClick={() => navigate('/analysis/create')}
              style={{
                padding: '0.8rem 1.5rem',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Create Your First Analysis
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '1.5rem'
          }}>
            {filteredAnalyses.map((analysis) => (
              <div
                key={analysis.analysis_id}
                style={{
                  background: 'var(--header-bg)',
                  padding: '1.5rem',
                  borderRadius: '12px',
                  border: '1px solid var(--border-color)',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
                onClick={() => navigate(`/analysis/${analysis.analysis_id}`)}
              >
                <div style={{ marginBottom: '1rem' }}>
                  {/* Name with inline editing */}
                  {editingId === analysis.analysis_id ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }} onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          flex: 1,
                          padding: '0.5rem',
                          border: '2px solid #667eea',
                          borderRadius: '6px',
                          fontSize: '1rem',
                          fontWeight: '600',
                          background: 'var(--header-bg)',
                          color: 'var(--text-color)'
                        }}
                        autoFocus
                      />
                      <button
                        onClick={(e) => saveEditName(analysis.analysis_id, e)}
                        style={{
                          padding: '0.5rem',
                          background: '#10b981',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <Check size={18} />
                      </button>
                      <button
                        onClick={cancelEditName}
                        style={{
                          padding: '0.5rem',
                          background: '#ef4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <h3 style={{ fontSize: '1.2rem', fontWeight: '600', color: 'var(--text-color)', flex: 1 }}>
                        {analysis.name || 'Untitled Analysis'}
                      </h3>
                      <button
                        onClick={(e) => startEditName(analysis, e)}
                        style={{
                          padding: '0.4rem',
                          background: 'var(--hover-bg)',
                          color: 'var(--text-secondary)',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                        title="Edit name"
                      >
                        <Edit2 size={16} />
                      </button>
                    </div>
                  )}
                  
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    {analysis.companies?.map((company, idx) => (
                      <span
                        key={idx}
                        style={{
                          padding: '0.3rem 0.7rem',
                          background: 'var(--badge-bg)',
                          borderRadius: '6px',
                          fontSize: '0.85rem',
                          fontWeight: '600',
                          color: 'var(--text-color)'
                        }}
                      >
                        {company.ticker}
                      </span>
                    ))}
                  </div>
                  {getStatusBadge(analysis.status)}
                </div>

                {analysis.progress !== undefined && analysis.progress < 100 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{
                      width: '100%',
                      height: '8px',
                      background: 'var(--border-color)',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${analysis.progress}%`,
                        height: '100%',
                        background: '#667eea',
                        transition: 'width 0.3s'
                      }} />
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                      {analysis.progress}% complete
                    </p>
                  </div>
                )}

                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingTop: '1rem',
                  borderTop: '1px solid var(--border-color)'
                }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </span>
                  <button
                    onClick={(e) => handleDelete(analysis.analysis_id, e)}
                    style={{
                      padding: '0.4rem 0.8rem',
                      background: '#fee2e2',
                      color: '#dc2626',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                      fontSize: '0.85rem'
                    }}
                  >
                    <Trash2 size={14} />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;