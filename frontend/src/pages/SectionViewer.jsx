// frontend/src/pages/SectionViewer.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
// import { useAuth } from '../context/AuthContext';
import { analysisAPI } from '../services/api';
import { 
  ArrowLeft, ChevronLeft, ChevronRight, 
  Loader, CheckCircle, Clock, XCircle, Menu, X
} from 'lucide-react';

const SectionViewer = () => {
  const { id, sectionNum } = useParams();
  const navigate = useNavigate();
  // const { user, logout } = useAuth();

  const [htmlContent, setHtmlContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sections, setSections] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError('');

      try {
        // Fetch section HTML
        const sectionResponse = await analysisAPI.getSection(id, sectionNum);
        setHtmlContent(sectionResponse.data);

        // Fetch all sections to know prev/next
        const sectionsResponse = await analysisAPI.getSections(id);
        setSections(sectionsResponse.data.sections || []);
      } catch (err) {
        setError('Failed to load section');
        console.error('Error loading section:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, sectionNum]);

  const currentSectionNum = parseInt(sectionNum);
  const currentSection = sections.find(s => s.section_number === currentSectionNum);
  const prevSection = sections.find(s => s.section_number === currentSectionNum - 1 && s.status === 'complete');
  const nextSection = sections.find(s => s.section_number === currentSectionNum + 1 && s.status === 'complete');

  const getStatusIcon = (status, isActive) => {
    const size = 16;
    if (status === 'complete') return <CheckCircle size={size} style={{ color: '#10b981' }} />;
    if (status === 'processing') return <Loader size={size} style={{ color: '#3b82f6', animation: 'spin 1s linear infinite' }} />;
    if (status === 'failed') return <XCircle size={size} style={{ color: '#ef4444' }} />;
    return <Clock size={size} style={{ color: '#9ca3af' }} />;
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#f9fafb'
      }}>
        <Loader size={40} style={{ color: '#667eea', animation: 'spin 1s linear infinite' }} />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: '#f9fafb',
        gap: '1rem'
      }}>
        <p style={{ color: '#ef4444', fontSize: '1.1rem' }}>{error}</p>
        <button 
          onClick={() => navigate(`/analysis/${id}`)}
          style={{
            padding: '0.75rem 1.5rem',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Back to Analysis
        </button>
      </div>
    );
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#f9fafb' }}>
      {/* Top Header - Same as other pages */}
      

      {/* Navigation Bar */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexShrink: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '0.5rem',
              background: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              cursor: 'pointer',
              color: '#6b7280'
            }}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          
          <button
            onClick={() => navigate(`/analysis/${id}`)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              cursor: 'pointer',
              color: '#6b7280',
              fontWeight: '600',
              fontSize: '0.95rem'
            }}
          >
            <ArrowLeft size={18} />
            Back to Analysis
          </button>
        </div>

        <div style={{ 
          fontSize: '1.1rem', 
          fontWeight: '600', 
          color: '#1f2937',
          flex: 1,
          textAlign: 'center',
          padding: '0 2rem'
        }}>
          {currentSection ? `Section ${currentSectionNum}: ${currentSection.section_name}` : `Section ${currentSectionNum}`}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {prevSection ? (
            <button
              onClick={() => navigate(`/analysis/${id}/section/${prevSection.section_number}`)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem',
                padding: '0.5rem 1rem',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.9rem'
              }}
            >
              <ChevronLeft size={18} />
              Previous
            </button>
          ) : (
            <div style={{ width: '100px' }} />
          )}
          {nextSection ? (
            <button
              onClick={() => navigate(`/analysis/${id}/section/${nextSection.section_number}`)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem',
                padding: '0.5rem 1rem',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.9rem'
              }}
            >
              Next
              <ChevronRight size={18} />
            </button>
          ) : (
            <div style={{ width: '100px' }} />
          )}
        </div>
      </div>

      {/* Content Area with Sidebar */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Sidebar */}
        {sidebarOpen && (
          <div style={{
            width: '280px',
            background: 'white',
            borderRight: '1px solid #e5e7eb',
            overflowY: 'auto',
            flexShrink: 0
          }}>
            <div style={{ padding: '1.5rem 1rem' }}>
              <h3 style={{ 
                fontSize: '1rem', 
                fontWeight: '600', 
                marginBottom: '1rem', 
                color: '#1f2937',
                paddingLeft: '0.5rem'
              }}>
                Report Sections
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {sections.map((section) => {
                  const isActive = section.section_number === currentSectionNum;
                  const isClickable = section.status === 'complete';
                  
                  return (
                    <div
                      key={section.section_number}
                      onClick={() => isClickable && navigate(`/analysis/${id}/section/${section.section_number}`)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        padding: '0.75rem',
                        borderRadius: '8px',
                        cursor: isClickable ? 'pointer' : 'default',
                        background: isActive ? '#ede9fe' : 'transparent',
                        border: isActive ? '1px solid #a78bfa' : '1px solid transparent',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        if (isClickable && !isActive) {
                          e.currentTarget.style.background = '#f3f4f6';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isActive) {
                          e.currentTarget.style.background = 'transparent';
                        }
                      }}
                    >
                      {getStatusIcon(section.status, isActive)}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ 
                          fontSize: '0.875rem', 
                          fontWeight: isActive ? '600' : '500',
                          color: isActive ? '#7c3aed' : (isClickable ? '#1f2937' : '#9ca3af'),
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}>
                          {section.section_number}. {section.section_name}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Main Content - Section HTML */}
        <iframe
          srcDoc={htmlContent}
          style={{
            flex: 1,
            border: 'none',
            background: 'white'
          }}
          title={`Section ${sectionNum}`}
        />
      </div>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default SectionViewer;