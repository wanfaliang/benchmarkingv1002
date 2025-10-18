// frontend/src/pages/CreateAnalysis.jsx
// Replace the entire file with this corrected version

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI, tickerAPI } from '../services/api';
import { Plus, X,  AlertCircle, Loader } from 'lucide-react';
// simport { useAuth } from '../context/AuthContext';

const CreateAnalysis = () => {
  const navigate = useNavigate();
  // const { user, logout } = useAuth();

  const [analysisName, setAnalysisName] = useState('');
  const [years, setYears] = useState(10);
  const [companies, setCompanies] = useState([]);
  
  const [tickerInput, setTickerInput] = useState('');
  const [adding, setAdding] = useState(false);
  const [tickerError, setTickerError] = useState('');
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Add ticker (validates in background, then adds if valid)
  // Replace the addTicker function in CreateAnalysis.jsx

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
      // Fix: Backend returns 'symbol' and 'name', not 'ticker' and 'company_name'
      const newCompany = {
        ticker: response.data.symbol,  // Changed from response.data.ticker
        name: response.data.name        // Changed from response.data.company_name
      };
      console.log('Adding company:', newCompany);
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
      navigate(`/analysis/${response.data.analysis_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create analysis');
    } finally {
      setSubmitting(false);
    }
  };

  console.log('Current companies:', companies); // Debug log

  return (
    <div style={{ minHeight: '100vh', background: '#f9fafb' }}>
      {/* Header */}
      

      {/* Main Content */}
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '3rem 5%' }}>
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '0.5rem' }}>
            Create New Analysis
          </h1>
          <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
            Configure your financial analysis parameters
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{
            background: 'white',
            padding: '2.5rem',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            
            {/* Analysis Name (Optional) */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ 
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '600',
                color: '#374151',
                fontSize: '1.1rem'
              }}>
                Analysis Name (Optional)
              </label>
              <input
                type="text"
                value={analysisName}
                onChange={(e) => setAnalysisName(e.target.value)}
                placeholder="e.g., Tech Giants Q4 2024"
                style={{ 
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  outline: 'none'
                }}
              />
              <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
                Leave blank to auto-generate from tickers
              </p>
            </div>

            {/* Ticker Input */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ 
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '600',
                color: '#374151',
                fontSize: '1.1rem'
              }}>
                Add Companies *
              </label>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
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
                  style={{ 
                    flex: 1,
                    padding: '0.75rem',
                    border: `1px solid ${tickerError ? '#ef4444' : '#d1d5db'}`,
                    borderRadius: '8px',
                    fontSize: '1rem',
                    outline: 'none'
                  }}
                />
                
                <button
                  type="button"
                  onClick={addTicker}
                  disabled={adding || !tickerInput.trim()}
                  style={{
                    padding: '0.75rem 1.5rem',
                    background: adding || !tickerInput.trim() ? '#d1d5db' : '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: adding || !tickerInput.trim() ? 'not-allowed' : 'pointer',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {adding ? (
                    <>
                      <Loader size={18} className="spin" />
                      Adding...
                    </>
                  ) : (
                    <>
                      <Plus size={18} />
                      Add
                    </>
                  )}
                </button>
              </div>
              
              {tickerError && (
                <p style={{ 
                  color: '#ef4444', 
                  fontSize: '0.875rem', 
                  marginTop: '0.5rem', 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.3rem' 
                }}>
                  <AlertCircle size={16} />
                  {tickerError}
                </p>
              )}
            </div>

            {/* Selected Companies List */}
            {companies.length > 0 && (
              <div style={{ 
                marginBottom: '1.5rem',
                padding: '1.5rem',
                background: '#f9fafb',
                borderRadius: '8px',
                border: '1px solid #e5e7eb'
              }}>
                <p style={{ 
                  fontWeight: '600', 
                  marginBottom: '1rem', 
                  color: '#374151',
                  fontSize: '1rem'
                }}>
                  Selected Companies ({companies.length})
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {companies.map((company, index) => (
                    <div
                      key={`${company.ticker}-${index}`}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '1rem',
                        background: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ 
                          fontWeight: '600', 
                          color: '#1f2937',
                          fontSize: '1.1rem',
                          marginBottom: '0.25rem'
                        }}>
                          {company.ticker}
                        </div>
                        <div style={{ 
                          fontSize: '0.9rem', 
                          color: '#6b7280',
                          lineHeight: '1.4'
                        }}>
                          {company.name}
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeTicker(company.ticker)}
                        style={{
                          padding: '0.5rem',
                          background: '#fee2e2',
                          color: '#dc2626',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          flexShrink: 0,
                          marginLeft: '1rem'
                        }}
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Years Slider */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ 
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '600',
                color: '#374151',
                fontSize: '1.1rem'
              }}>
                Years of Historical Data: <span style={{ color: '#667eea' }}>{years}</span>
              </label>
              <input
                type="range"
                min="1"
                max="50"
                value={years}
                onChange={(e) => setYears(parseInt(e.target.value))}
                style={{
                  width: '100%',
                  height: '8px',
                  borderRadius: '4px',
                  outline: 'none',
                  cursor: 'pointer',
                  WebkitAppearance: 'none',
                  appearance: 'none',
                  background: `linear-gradient(to right, #667eea 0%, #667eea ${(years-1)/49*100}%, #e5e7eb ${(years-1)/49*100}%, #e5e7eb 100%)`
                }}
              />
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginTop: '0.5rem', 
                fontSize: '0.875rem', 
                color: '#6b7280' 
              }}>
                <span>1 year</span>
                <span>50 years</span>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div style={{
                background: '#fee2e2',
                color: '#dc2626',
                padding: '1rem',
                borderRadius: '8px',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <AlertCircle size={20} />
                {error}
              </div>
            )}

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                style={{
                  flex: 1,
                  padding: '1rem',
                  background: '#f3f4f6',
                  color: '#374151',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || companies.length === 0}
                style={{
                  flex: 2,
                  padding: '1rem',
                  background: submitting || companies.length === 0 ? '#d1d5db' : '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: submitting || companies.length === 0 ? 'not-allowed' : 'pointer'
                }}
              >
                {submitting ? 'Creating Analysis...' : 'Create Analysis'}
              </button>
            </div>
          </div>
        </form>
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
          input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            background: #667eea;
            cursor: pointer;
            border-radius: 50%;
          }
          input[type="range"]::-moz-range-thumb {
            width: 20px;
            height: 20px;
            background: #667eea;
            cursor: pointer;
            border-radius: 50%;
            border: none;
          }
        `}
      </style>
    </div>
  );
};

export default CreateAnalysis;