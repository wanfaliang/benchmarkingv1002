import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState('');
  const hasVerified = useRef(false);

  useEffect(() => {
    const verifyToken = async () => {
      if (hasVerified.current) return;
      hasVerified.current = true;
      const token = searchParams.get('token');
      
      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link');
        return;
      }

      try {
        const response = await authAPI.verifyEmail(token);
        setStatus('success');
        setMessage(response.data.message || 'Email verified successfully!');
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
        
      } catch (error) {
        setStatus('error');
        setMessage(error.response?.data?.detail || 'Verification failed. The link may have expired.');
      }
    };

    verifyToken();
  }, [searchParams, navigate]);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        padding: '3rem',
        borderRadius: '16px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        maxWidth: '500px',
        textAlign: 'center'
      }}>
        {status === 'verifying' && (
          <>
            <div style={{
              width: '50px',
              height: '50px',
              border: '4px solid #e5e7eb',
              borderTop: '4px solid #667eea',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 1.5rem'
            }}></div>
            <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>
              Verifying your email...
            </h2>
            <p style={{ color: '#6b7280' }}>
              Please wait while we verify your email address.
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={{
              width: '60px',
              height: '60px',
              background: '#10b981',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
              fontSize: '2rem'
            }}>
              ✓
            </div>
            <h2 style={{ color: '#10b981', marginBottom: '1rem' }}>
              Email Verified! 🎉
            </h2>
            <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
              {message}
            </p>
            <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>
              Redirecting to login page...
            </p>
            <Link 
              to="/login"
              style={{
                display: 'inline-block',
                marginTop: '1rem',
                color: '#667eea',
                textDecoration: 'none',
                fontWeight: '600'
              }}
            >
              Click here if not redirected
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <div style={{
              width: '60px',
              height: '60px',
              background: '#ef4444',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
              fontSize: '2rem',
              color: 'white'
            }}>
              ✗
            </div>
            <h2 style={{ color: '#ef4444', marginBottom: '1rem' }}>
              Verification Failed
            </h2>
            <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
              {message}
            </p>
            <Link
              to="/login"
              style={{
                display: 'inline-block',
                padding: '0.75rem 1.5rem',
                background: '#667eea',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '8px',
                fontWeight: '600'
              }}
            >
              Go to Login
            </Link>
          </>
        )}
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default VerifyEmail;