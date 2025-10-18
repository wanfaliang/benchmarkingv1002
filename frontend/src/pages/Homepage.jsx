import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, BarChart3, PieChart, Newspaper, Database, Wrench, ArrowRight } from 'lucide-react';

const Homepage = () => {
  const navigate = useNavigate();
  
  const modules = [
    {
      icon: <TrendingUp size={32} />,
      title: 'Financial Analysis',
      description: 'Comprehensive equity research with 20+ analysis modules',
      color: '#3b82f6'
    },
    {
      icon: <BarChart3 size={32} />,
      title: 'Quantitative Trading',
      description: 'Strategy backtesting and algorithmic trading research',
      color: '#8b5cf6'
    },
    {
      icon: <PieChart size={32} />,
      title: 'Portfolio Optimization',
      description: 'Risk-return analysis and portfolio construction',
      color: '#10b981'
    },
    {
      icon: <Newspaper size={32} />,
      title: 'News & Research',
      description: 'Aggregated insights from multiple sources',
      color: '#f59e0b'
    },
    {
      icon: <Database size={32} />,
      title: 'Data Platform',
      description: 'Financial, market, and alternative data access',
      color: '#ec4899'
    },
    {
      icon: <Wrench size={32} />,
      title: 'Tools & Utilities',
      description: 'Financial calculators and analysis tools',
      color: '#6366f1'
    }
  ];

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* REMOVED OLD NAVIGATION - Now using Header component from App.js */}

      {/* Hero Section */}
      <div style={{
        textAlign: 'center',
        padding: '6rem 5% 4rem',
        color: 'white'
      }}>
        <h1 style={{
          fontSize: '3.5rem',
          fontWeight: 'bold',
          marginBottom: '1.5rem',
          lineHeight: '1.2'
        }}>
          Professional Financial<br />Intelligence Platform
        </h1>
        <p style={{
          fontSize: '1.3rem',
          marginBottom: '2.5rem',
          opacity: 0.9,
          maxWidth: '700px',
          margin: '0 auto 2.5rem'
        }}>
          Comprehensive data analysis, quantitative trading, and portfolio management tools for investment professionals
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button 
            onClick={() => navigate('/register')}
            style={{
              padding: '1rem 2.5rem',
              background: 'white',
              color: '#667eea',
              border: 'none',
              borderRadius: '10px',
              fontSize: '1.1rem',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
            onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
          >
            Get Started <ArrowRight size={20} />
          </button>
          <button 
            onClick={() => navigate('/login')}
            style={{
              padding: '1rem 2.5rem',
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '2px solid white',
              borderRadius: '10px',
              fontSize: '1.1rem',
              fontWeight: '600',
              cursor: 'pointer',
              backdropFilter: 'blur(10px)',
              transition: 'transform 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
            onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
          >
            View Demo
          </button>
        </div>
      </div>

      {/* Modules Section */}
      <div id="modules" style={{
        background: 'white',
        padding: '5rem 5%',
        borderTopLeftRadius: '40px',
        borderTopRightRadius: '40px'
      }}>
        <h2 style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          textAlign: 'center',
          marginBottom: '1rem',
          color: '#1f2937'
        }}>
          Powerful Modules
        </h2>
        <p style={{
          textAlign: 'center',
          fontSize: '1.1rem',
          color: '#6b7280',
          marginBottom: '4rem',
          maxWidth: '600px',
          margin: '0 auto 4rem'
        }}>
          Everything you need for professional financial analysis and research
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {modules.map((module, index) => (
            <div
              key={index}
              style={{
                background: 'white',
                padding: '2rem',
                borderRadius: '16px',
                border: '1px solid #e5e7eb',
                transition: 'all 0.3s',
                cursor: 'pointer',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-8px)';
                e.currentTarget.style.boxShadow = '0 20px 40px rgba(0,0,0,0.12)';
                e.currentTarget.style.borderColor = module.color;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
                e.currentTarget.style.borderColor = '#e5e7eb';
              }}
            >
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '12px',
                background: `${module.color}15`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: module.color,
                marginBottom: '1.5rem'
              }}>
                {module.icon}
              </div>
              <h3 style={{
                fontSize: '1.4rem',
                fontWeight: '600',
                marginBottom: '0.75rem',
                color: '#1f2937'
              }}>
                {module.title}
              </h3>
              <p style={{
                color: '#6b7280',
                fontSize: '1rem',
                lineHeight: '1.6'
              }}>
                {module.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div style={{
        background: '#1f2937',
        color: 'white',
        padding: '3rem 5%',
        textAlign: 'center'
      }}>
        <p style={{ opacity: 0.8 }}>
          © 2025 FinanceHub. Professional Financial Intelligence Platform.
        </p>
      </div>
    </div>
  );
};

export default Homepage;