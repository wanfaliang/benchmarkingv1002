import React from 'react';
import { NavLink, Outlet, useLocation, Navigate } from 'react-router-dom';

/**
 * BEALayout - Compact top tab navigation for BEA data explorers
 *
 * Datasets:
 * - NIPA: National Income and Product Accounts (GDP, Personal Income, Government)
 * - Regional: State and County Economic Data
 * - GDP by Industry: Industry-level GDP contributions
 * - ITA: International Trade and Investment
 * - Fixed Assets: Fixed Assets and Consumer Durables
 */

interface BEADataset {
  id: string;
  label: string;
  title: string;
  available: boolean;
}

const beaDatasets: BEADataset[] = [
  { id: 'nipa', label: 'NIPA', title: 'National Income & Product Accounts', available: true },
  { id: 'regional', label: 'Regional', title: 'State & County Economic Data', available: true },
  { id: 'gdpbyindustry', label: 'GDP by Industry', title: 'Industry-level GDP', available: true },
  { id: 'ita', label: 'Intl Trade', title: 'International Trade & Investment', available: true },
  { id: 'fixedassets', label: 'Fixed Assets', title: 'Fixed Assets & Consumer Durables', available: true },
];

export default function BEALayout(): React.ReactElement {
  const location = useLocation();

  // Redirect /research/bea to /research/bea/nipa
  if (location.pathname === '/research/bea' || location.pathname === '/research/bea/') {
    return <Navigate to="/research/bea/nipa" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Compact Tab Navigation */}
      <div className="sticky top-16 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="px-6">
          <div className="flex items-center gap-1 py-2 overflow-x-auto">
            <span className="text-xs font-medium text-gray-500 mr-2 whitespace-nowrap">BEA Data:</span>
            {beaDatasets.map((dataset) => (
              <NavLink
                key={dataset.id}
                to={dataset.available ? `/research/bea/${dataset.id}` : '#'}
                onClick={(e) => !dataset.available && e.preventDefault()}
                className={({ isActive }) => {
                  const base = "px-3 py-1.5 text-xs font-medium rounded transition-all whitespace-nowrap";
                  if (!dataset.available) {
                    return `${base} text-gray-400 cursor-not-allowed`;
                  }
                  if (isActive) {
                    return `${base} bg-emerald-600 text-white shadow-sm`;
                  }
                  return `${base} text-gray-600 hover:bg-gray-100 hover:text-gray-900`;
                }}
                title={dataset.title}
              >
                {dataset.label}
                {!dataset.available && (
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
