import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { authAPI } from '../services/api';

interface LocationState {
  email?: string;
}

const RegistrationSuccess: React.FC = () => {
  const location = useLocation();
  const state = location.state as LocationState | null;
  const email = state?.email;
  const [resending, setResending] = useState(false);
  const [message, setMessage] = useState('');

  const handleResend = async () => {
    if (!email) return;

    setResending(true);
    setMessage('');

    try {
      await authAPI.resendVerification(email);
      setMessage('Verification email sent! Please check your inbox.');
    } catch (error) {
      const err = error as { response?: { data?: { detail?: string } } };
      setMessage(err.response?.data?.detail || 'Failed to resend email. Please try again.');
    } finally {
      setResending(false);
    }
  };

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
          📧
        </div>

        <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>
          Check Your Email!
        </h2>

        <p style={{ color: '#6b7280', marginBottom: '1.5rem' }}>
          We've sent a verification link to:
        </p>

        <p style={{
          color: '#667eea',
          fontWeight: '600',
          marginBottom: '1.5rem',
          fontSize: '1.1rem'
        }}>
          {email}
        </p>

        <p style={{ color: '#6b7280', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
          Please click the link in the email to verify your account.
          The link will expire in 24 hours.
        </p>

        {message && (
          <div style={{
            background: message.includes('Failed') ? '#fee2e2' : '#d1fae5',
            color: message.includes('Failed') ? '#dc2626' : '#059669',
            padding: '0.75rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            fontSize: '0.9rem'
          }}>
            {message}
          </div>
        )}

        <div style={{
          borderTop: '1px solid #e5e7eb',
          paddingTop: '1.5rem',
          marginTop: '1.5rem'
        }}>
          <p style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Didn't receive the email?
          </p>

          <button
            onClick={handleResend}
            disabled={resending || !email}
            style={{
              padding: '0.75rem 1.5rem',
              background: resending ? '#9ca3af' : '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: resending ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              marginBottom: '1rem'
            }}
          >
            {resending ? 'Sending...' : 'Resend Verification Email'}
          </button>

          <div>
            <Link
              to="/login"
              style={{
                color: '#667eea',
                textDecoration: 'none',
                fontSize: '0.9rem'
              }}
            >
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegistrationSuccess;
