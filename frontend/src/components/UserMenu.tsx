import React, { useState, useRef, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { User, CreditCard, Settings, LogOut, Sun, Moon, ChevronDown } from 'lucide-react';

function cls(...classes: (string | boolean | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

interface MenuItemProps {
  icon: ReactNode;
  label: string;
  onClick: () => void;
  danger?: boolean;
}

const MenuItem: React.FC<MenuItemProps> = ({ icon, label, onClick, danger = false }) => (
  <div className="px-2 py-1">
    <button
      onClick={onClick}
      className={cls(
        "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm font-medium",
        danger
          ? "text-rose-600 hover:bg-rose-50"
          : "text-slate-700 hover:bg-slate-50"
      )}
    >
      <span className={danger ? "text-rose-600" : "text-slate-600"}>
        {icon}
      </span>
      <span>{label}</span>
    </button>
  </div>
);

// User type is imported from types/index.ts via AuthContext

const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
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

  const handleMenuClick = (path: string) => {
    navigate(path);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={menuRef}>
      {/* User Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-3 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors group"
      >
        {/* Avatar */}
        <div className="relative">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={displayName}
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-white font-semibold text-sm">
              {initials}
            </div>
          )}
          {/* Online indicator */}
          <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-white"></div>
        </div>

        {/* Name - Desktop only */}
        <span className="hidden md:block font-medium text-slate-700 text-sm">
          {displayName}
        </span>

        {/* Dropdown Arrow */}
        <ChevronDown className={cls(
          "w-4 h-4 text-slate-400 transition-transform",
          isOpen && "rotate-180"
        )} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-72 bg-white border border-slate-200 rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {/* User Info Header */}
          <div className="px-4 py-3 border-b border-slate-100 bg-slate-50">
            <div className="font-semibold text-slate-900 text-sm mb-1">
              {user.full_name || 'User'}
            </div>
            <div className="text-xs text-slate-500">
              {user.email}
            </div>
            {user.auth_provider === 'google' && (
              <div className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-white border border-slate-200 rounded-md text-xs text-slate-600">
                <svg className="w-3 h-3" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google Account
              </div>
            )}
          </div>

          {/* Menu Items */}
          <div className="py-2">
            <MenuItem
              icon={<User className="w-4 h-4" />}
              label="Account Settings"
              onClick={() => handleMenuClick('/account-settings')}
            />
            <MenuItem
              icon={<CreditCard className="w-4 h-4" />}
              label="Manage Subscription"
              onClick={() => handleMenuClick('/subscription')}
            />
            <MenuItem
              icon={<Settings className="w-4 h-4" />}
              label="User Settings"
              onClick={() => handleMenuClick('/user-settings')}
            />

            {/* Theme Toggle */}
            <div className="px-2 py-1">
              <button
                onClick={toggleTheme}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors text-sm"
              >
                <div className="flex items-center gap-3">
                  {theme === 'light' ? (
                    <Moon className="w-4 h-4 text-slate-600" />
                  ) : (
                    <Sun className="w-4 h-4 text-slate-600" />
                  )}
                  <span className="text-slate-700 font-medium">
                    {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {/* Toggle Switch */}
                  <div className={cls(
                    "relative w-10 h-5 rounded-full transition-colors",
                    theme === 'dark' ? "bg-blue-600" : "bg-slate-300"
                  )}>
                    <div className={cls(
                      "absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform shadow-sm",
                      theme === 'dark' ? "left-5" : "left-0.5"
                    )}></div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Logout */}
          <div className="border-t border-slate-100 py-2">
            <MenuItem
              icon={<LogOut className="w-4 h-4" />}
              label="Log Out"
              onClick={handleLogout}
              danger
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
