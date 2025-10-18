import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const UserMenu = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  if (!user) return null;

  // Get user display name or email
  const displayName = user.full_name || user.email.split('@')[0];
  const initials = user.full_name 
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : user.email[0].toUpperCase();

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsOpen(false);
  };

  const handleMenuClick = (path) => {
    navigate(path);
    setIsOpen(false);
  };

  return (
    <div style={{ position: 'relative' }} ref={menuRef}>
      {/* User Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '0.5rem 0.75rem',
          background: 'transparent',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          cursor: 'pointer',
          transition: 'all 0.2s',
          color: 'var(--text-color)'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'var(--hover-bg)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
      >
        {/* Avatar */}
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: user.avatar_url ? `url(${user.avatar_url})` : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: '600',
          fontSize: '0.875rem'
        }}>
          {!user.avatar_url && initials}
        </div>

        {/* Name - Desktop only */}
        <span style={{
          fontWeight: '500',
          fontSize: '0.95rem',
          display: 'none',
          '@media (min-width: 768px)': { display: 'block' }
        }} className="desktop-only">
          {displayName}
        </span>

        {/* Dropdown Arrow */}
        <svg 
          width="16" 
          height="16" 
          viewBox="0 0 16 16" 
          fill="none"
          style={{ 
            transition: 'transform 0.2s',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)'
          }}
        >
          <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 0.5rem)',
          right: 0,
          width: '280px',
          background: 'var(--dropdown-bg)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.15)',
          zIndex: 1000,
          overflow: 'hidden'
        }}>
          {/* User Info Header */}
          <div style={{
            padding: '1rem',
            borderBottom: '1px solid var(--border-color)',
            background: 'var(--section-bg)'
          }}>
            <div style={{ fontWeight: '600', fontSize: '0.95rem', marginBottom: '0.25rem' }}>
              {user.full_name || 'User'}
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              {user.email}
            </div>
            {user.auth_provider === 'google' && (
              <div style={{
                display: 'inline-block',
                marginTop: '0.5rem',
                padding: '0.25rem 0.5rem',
                background: 'var(--badge-bg)',
                borderRadius: '4px',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)'
              }}>
                Google Account
              </div>
            )}
          </div>

          {/* Menu Items */}
          <div style={{ padding: '0.5rem 0' }}>
            <MenuItem 
              icon="👤"
              label="Account Settings"
              onClick={() => handleMenuClick('/account-settings')}
            />
            <MenuItem 
              icon="💳"
              label="Manage Subscription"
              onClick={() => handleMenuClick('/subscription')}
            />
            <MenuItem 
              icon="⚙️"
              label="User Settings"
              onClick={() => handleMenuClick('/user-settings')}
            />

            {/* Theme Toggle */}
            <div
              onClick={toggleTheme}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                cursor: 'pointer',
                transition: 'background 0.2s',
                fontSize: '0.95rem'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--hover-bg)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <span>{theme === 'light' ? '🌙' : '☀️'}</span>
              <span>Theme: {theme === 'light' ? 'Light' : 'Dark'}</span>
              <span style={{ 
                marginLeft: 'auto', 
                padding: '0.25rem 0.5rem',
                background: 'var(--badge-bg)',
                borderRadius: '4px',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)'
              }}>
                {theme === 'light' ? 'Switch to Dark' : 'Switch to Light'}
              </span>
            </div>
          </div>

          {/* Logout */}
          <div style={{
            borderTop: '1px solid var(--border-color)',
            padding: '0.5rem 0'
          }}>
            <MenuItem 
              icon="🚪"
              label="Log Out"
              onClick={handleLogout}
              danger
            />
          </div>
        </div>
      )}

      <style>{`
        @media (min-width: 768px) {
          .desktop-only {
            display: block !important;
          }
        }
      `}</style>
    </div>
  );
};

// Helper component for menu items
const MenuItem = ({ icon, label, onClick, danger }) => (
  <div
    onClick={onClick}
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '0.75rem 1rem',
      cursor: 'pointer',
      transition: 'background 0.2s',
      fontSize: '0.95rem',
      color: danger ? '#dc2626' : 'var(--text-color)'
    }}
    onMouseEnter={(e) => e.currentTarget.style.background = danger ? '#fee2e2' : 'var(--hover-bg)'}
    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
  >
    <span style={{ fontSize: '1.25rem' }}>{icon}</span>
    <span>{label}</span>
  </div>
);

export default UserMenu;