import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Landmark,
  TrendingUp,
  BarChart3,
  Users,
  Building2,
  Globe,
  Factory,
  DollarSign,
  PieChart,
  ArrowRight,
} from 'lucide-react';

/**
 * Research Portal - Entry point for all research explorers
 *
 * Provides access to:
 * - Treasury Auction Explorer
 * - BEA Economic Data (NIPA, Regional, GDP by Industry, ITA, Fixed Assets)
 * - BLS Labor Statistics (Employment, CPI, Labor Force, Local Area)
 */

const researchModules = [
  {
    category: 'Treasury & Fixed Income',
    items: [
      {
        id: 'treasury',
        title: 'Treasury Auctions',
        description: 'Explore U.S. Treasury Notes & Bonds auction history, yields, and bid-to-cover ratios',
        icon: Landmark,
        path: '/research/treasury',
        color: 'bg-blue-500',
        available: true,
      },
    ],
  },
  {
    category: 'Economic Data (BEA)',
    items: [
      {
        id: 'nipa',
        title: 'NIPA Tables',
        description: 'National Income and Product Accounts - GDP, consumer spending, business investment',
        icon: PieChart,
        path: '/research/bea/nipa',
        color: 'bg-emerald-500',
        available: false,
      },
      {
        id: 'regional',
        title: 'Regional Economics',
        description: 'State and county level GDP, personal income, and employment data',
        icon: Globe,
        path: '/research/bea/regional',
        color: 'bg-teal-500',
        available: false,
      },
      {
        id: 'gdp-industry',
        title: 'GDP by Industry',
        description: 'Industry-level contributions to GDP across 39 industry classifications',
        icon: Factory,
        path: '/research/bea/gdp-industry',
        color: 'bg-cyan-500',
        available: false,
      },
      {
        id: 'ita',
        title: 'International Trade',
        description: 'Trade balances, exports, imports by country and category',
        icon: Globe,
        path: '/research/bea/ita',
        color: 'bg-sky-500',
        available: false,
      },
      {
        id: 'fixed-assets',
        title: 'Fixed Assets',
        description: 'Capital stock, investment, and depreciation by asset type',
        icon: Building2,
        path: '/research/bea/fixed-assets',
        color: 'bg-indigo-500',
        available: false,
      },
    ],
  },
  {
    category: 'Labor Statistics (BLS)',
    items: [
      {
        id: 'employment',
        title: 'Employment Statistics',
        description: 'Current employment, hours, and earnings by industry and supersector',
        icon: Users,
        path: '/research/bls/employment',
        color: 'bg-violet-500',
        available: false,
      },
      {
        id: 'cpi',
        title: 'Consumer Price Index',
        description: 'Inflation metrics by category and metropolitan area',
        icon: DollarSign,
        path: '/research/bls/cu',
        color: 'bg-purple-500',
        available: true,
      },
      {
        id: 'labor-force',
        title: 'Labor Force Statistics',
        description: 'Unemployment, participation rates by demographics',
        icon: BarChart3,
        path: '/research/bls/labor-force',
        color: 'bg-fuchsia-500',
        available: false,
      },
      {
        id: 'local-area',
        title: 'Local Area Unemployment',
        description: 'State and metro area unemployment rates and rankings',
        icon: TrendingUp,
        path: '/research/bls/local-area',
        color: 'bg-pink-500',
        available: false,
      },
    ],
  },
];

function ModuleCard({ item, onClick }) {
  const Icon = item.icon;

  return (
    <div
      onClick={item.available ? onClick : undefined}
      className={`relative p-5 bg-white rounded-xl border transition-all duration-200 ${
        item.available
          ? 'cursor-pointer hover:shadow-lg hover:-translate-y-1 hover:border-gray-300'
          : 'opacity-60 cursor-not-allowed'
      }`}
    >
      {!item.available && (
        <span className="absolute top-3 right-3 text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">
          Coming Soon
        </span>
      )}

      <div className={`w-12 h-12 ${item.color} rounded-xl flex items-center justify-center mb-4`}>
        <Icon className="w-6 h-6 text-white" />
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-1">{item.title}</h3>
      <p className="text-sm text-gray-600 mb-4">{item.description}</p>

      {item.available && (
        <div className="flex items-center text-blue-600 text-sm font-medium">
          Explore
          <ArrowRight className="w-4 h-4 ml-1" />
        </div>
      )}
    </div>
  );
}

export default function Research() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Research</h1>
        <p className="text-gray-600 mb-8">
          Explore economic, financial, and labor market data from official government sources
        </p>

        {/* Module Categories */}
        {researchModules.map((category) => (
          <div key={category.category} className="mb-8">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 pb-2 border-b">
              {category.category}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {category.items.map((item) => (
                <ModuleCard
                  key={item.id}
                  item={item}
                  onClick={() => navigate(item.path)}
                />
              ))}
            </div>
          </div>
        ))}

        {/* Data Sources Info */}
        <div className="mt-12 p-6 bg-white rounded-xl border">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Data Sources</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-800 mb-1">U.S. Treasury</h4>
              <p>Treasury auction results, yields, and demand metrics from Fiscal Data API</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-1">Bureau of Economic Analysis</h4>
              <p>GDP, personal income, trade, and industry data from BEA API</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-1">Bureau of Labor Statistics</h4>
              <p>Employment, inflation, and labor force data from BLS API</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
