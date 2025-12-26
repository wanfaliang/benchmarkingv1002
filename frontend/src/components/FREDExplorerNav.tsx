import { NavLink, useLocation } from 'react-router-dom';
import {
  Landmark,
  TrendingUp,
  Activity,
  Home,
  Calendar,
  LineChart,
  FileText,
} from 'lucide-react';

/**
 * FREDExplorerNav - Subheader navigation for FRED data explorers
 *
 * 7 FRED Explorer pages:
 * - Fed Funds Rate
 * - Yield Curve
 * - Unemployment Claims
 * - Consumer Sentiment
 * - Leading Economic Index
 * - Housing Market
 * - FRED Calendar
 */

interface FREDExplorer {
  id: string;
  path: string;
  label: string;
  title: string;
  icon: React.ReactNode;
}

const fredExplorers: FREDExplorer[] = [
  {
    id: 'fed-funds',
    path: '/research/fed-funds',
    label: 'Fed Funds',
    title: 'Federal Funds Rate',
    icon: <Landmark className="w-3.5 h-3.5" />,
  },
  {
    id: 'yield-curve',
    path: '/research/yield-curve',
    label: 'Yield Curve',
    title: 'Treasury Yield Curve',
    icon: <TrendingUp className="w-3.5 h-3.5" />,
  },
  {
    id: 'claims',
    path: '/research/claims',
    label: 'Claims',
    title: 'Unemployment Claims',
    icon: <FileText className="w-3.5 h-3.5" />,
  },
  {
    id: 'sentiment',
    path: '/research/sentiment',
    label: 'Sentiment',
    title: 'Consumer Sentiment',
    icon: <Activity className="w-3.5 h-3.5" />,
  },
  {
    id: 'leading',
    path: '/research/leading',
    label: 'Leading Index',
    title: 'Leading Economic Index & Recession',
    icon: <LineChart className="w-3.5 h-3.5" />,
  },
  {
    id: 'housing',
    path: '/research/housing',
    label: 'Housing',
    title: 'Housing Market',
    icon: <Home className="w-3.5 h-3.5" />,
  },
  {
    id: 'fred-calendar',
    path: '/research/fred-calendar',
    label: 'Calendar',
    title: 'FRED Release Calendar',
    icon: <Calendar className="w-3.5 h-3.5" />,
  },
];

export default function FREDExplorerNav() {
  const location = useLocation();

  return (
    <div className="sticky top-16 z-40 bg-white border-b border-gray-200 shadow-sm">
      <div className="px-6">
        <div className="flex items-center gap-1 py-2 overflow-x-auto">
          <span className="text-xs font-medium text-gray-500 mr-2 whitespace-nowrap">FRED Explorers:</span>
          {fredExplorers.map((explorer) => {
            const isActive = location.pathname === explorer.path ||
                             location.pathname.startsWith(explorer.path + '/');
            return (
              <NavLink
                key={explorer.id}
                to={explorer.path}
                className={`
                  inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded transition-all whitespace-nowrap
                  ${isActive
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
                title={explorer.title}
              >
                {explorer.icon}
                {explorer.label}
              </NavLink>
            );
          })}
        </div>
      </div>
    </div>
  );
}
