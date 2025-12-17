import React from 'react';
import { NavLink, Outlet, useLocation, Navigate } from 'react-router-dom';

/**
 * BLSLayout - Compact top tab navigation for BLS survey explorers
 *
 * Surveys ordered by category (side by side):
 * - Price Indexes: CU (CPI), CW (Workers CPI), AP (Avg Price)
 * - Employment: CE (Employment), LA (Local Area), SM (State Metro), JT (JOLTS), OE (Occupation)
 * - Labor Force: LN (Labor Force), EC (Employment Cost)
 * - Other surveys to be added
 */

interface BLSSurvey {
  id: string;
  label: string;
  title: string;
  available: boolean;
}

const blsSurveys: BLSSurvey[] = [
  // Price Indexes
  { id: 'cu', label: 'CU', title: 'Consumer Price Index', available: true },
  { id: 'cw', label: 'CW', title: 'CPI for Urban Wage Earners', available: true },
  { id: 'su', label: 'SU', title: 'Chained CPI', available: true },
  { id: 'ap', label: 'AP', title: 'Average Price', available: true },
  // Employment
  { id: 'ce', label: 'CE', title: 'Employment Statistics', available: true },
  { id: 'la', label: 'LA', title: 'Local Area Unemployment', available: true },
  { id: 'sm', label: 'SM', title: 'State & Metro Employment', available: true },
  { id: 'jt', label: 'JT', title: 'Job Openings (JOLTS)', available: true },
  { id: 'oe', label: 'OE', title: 'Occupational Employment', available: true },
  // Labor Force
  { id: 'ln', label: 'LN', title: 'Labor Force Statistics', available: true },
  { id: 'ec', label: 'EC', title: 'Employment Cost Index', available: true },
  // Industry / Producer Prices / Productivity
  { id: 'pc', label: 'PC', title: 'PPI - Industry', available: true },
  { id: 'wp', label: 'WP', title: 'PPI - Commodities (Final Demand)', available: true },
  { id: 'pr', label: 'PR', title: 'Productivity', available: true },
  { id: 'ip', label: 'IP', title: 'Industry Productivity', available: true },
  // Business Dynamics
  { id: 'bd', label: 'BD', title: 'Business Employment Dynamics', available: true },
  // International
  { id: 'ei', label: 'EI', title: 'Import/Export Price', available: true },
  // Other
  { id: 'tu', label: 'TU', title: 'Time Use Survey', available: true },
];

export default function BLSLayout(): React.ReactElement {
  const location = useLocation();

  // Redirect /research/bls to /research/bls/cu
  if (location.pathname === '/research/bls' || location.pathname === '/research/bls/') {
    return <Navigate to="/research/bls/cu" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Compact Tab Navigation */}
      <div className="sticky top-16 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="px-6">
          <div className="flex items-center gap-1 py-2 overflow-x-auto">
            <span className="text-xs font-medium text-gray-500 mr-2 whitespace-nowrap">BLS Surveys:</span>
            {blsSurveys.map((survey) => (
              <NavLink
                key={survey.id}
                to={survey.available ? `/research/bls/${survey.id}` : '#'}
                onClick={(e) => !survey.available && e.preventDefault()}
                className={({ isActive }) => {
                  const base = "px-2.5 py-1 text-xs font-medium rounded transition-all whitespace-nowrap";
                  if (!survey.available) {
                    return `${base} text-gray-400 cursor-not-allowed`;
                  }
                  if (isActive) {
                    return `${base} bg-blue-600 text-white shadow-sm`;
                  }
                  return `${base} text-gray-600 hover:bg-gray-100 hover:text-gray-900`;
                }}
                title={survey.title}
              >
                {survey.label}
                {!survey.available && (
                  <span className="ml-1 text-[9px] text-gray-400">•</span>
                )}
              </NavLink>
            ))}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="px-6 py-6">
        <Outlet />
      </div>
    </div>
  );
}
