import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Users,
  DollarSign,
  Building2,
  MapPin,
  BarChart3,
  Activity,
  ChevronRight,
  RefreshCw,
  AlertCircle,
  Briefcase,
  Factory,
  ShoppingCart,
  Truck,
  Landmark,
  Heart,
  GraduationCap,
  Hotel,
  Wrench,
  Package,
  Info,
  Search,
} from 'lucide-react';
import { DataTable, ChangeRenderer, NumberRenderer } from '../components/DataTable';
import { TrendChart } from '../components/TrendChart';
import api from '../../../services/api';

interface LaborIndicator {
  id: string;
  name: string;
  value: number;
  formatted_value: string;
  change: number | null;
  change_pct: number | null;
  period: string;
  year: number;
  source: string;
  frequency: string;
}

interface IndustryEmployment {
  industry_code: string;
  industry_name: string;
  employment: number;
  employment_change: number | null;
  employment_change_pct: number | null;
  avg_hourly_earnings: number | null;
  avg_weekly_hours: number | null;
  period: string;
  year: number;
}

interface CPICategory {
  item_code: string;
  item_name: string;
  index_value: number;
  mom_change: number | null;
  yoy_change: number | null;
  weight: number | null;
  period: string;
  year: number;
}

interface RegionalUnemployment {
  area_code: string;
  area_name: string;
  unemployment_rate: number;
  rate_change: number | null;
  labor_force: number | null;
  employed: number | null;
  unemployed: number | null;
  period: string;
  year: number;
}

interface TrendPoint {
  date: string;
  value: number;
  period: string;
  year: number;
}

interface SurveyInfo {
  id: string;
  code: string;
  name: string;
  description: string;
  path: string;
  category: string;
  series_count: number | null;
  latest_period: string | null;
  latest_year: number | null;
  update_frequency: string;
  // Alternative field names from API
  survey_id?: string;
  frequency?: string;
  record_count?: number | null;
}

interface BLSPortalData {
  labor_indicators: LaborIndicator[];
  employment_by_industry: IndustryEmployment[];
  cpi_categories: CPICategory[];
  regional_unemployment: RegionalUnemployment[];
  unemployment_trend: TrendPoint[];
  cpi_trend: TrendPoint[];
  payrolls_trend: TrendPoint[];
  surveys: SurveyInfo[];
  last_updated: string;
}

const industryIcons: Record<string, React.ReactNode> = {
  'Total Nonfarm': <Building2 className="w-4 h-4" />,
  'Total Private': <Briefcase className="w-4 h-4" />,
  'Goods-producing': <Factory className="w-4 h-4" />,
  'Mining and Logging': <Package className="w-4 h-4" />,
  'Construction': <Wrench className="w-4 h-4" />,
  'Manufacturing': <Factory className="w-4 h-4" />,
  'Private Service-providing': <Users className="w-4 h-4" />,
  'Trade, Transportation, Utilities': <Truck className="w-4 h-4" />,
  'Wholesale Trade': <Package className="w-4 h-4" />,
  'Retail Trade': <ShoppingCart className="w-4 h-4" />,
  'Financial Activities': <Landmark className="w-4 h-4" />,
  'Professional and Business Services': <Briefcase className="w-4 h-4" />,
  'Education and Health Services': <GraduationCap className="w-4 h-4" />,
  'Leisure and Hospitality': <Hotel className="w-4 h-4" />,
  'Healthcare': <Heart className="w-4 h-4" />,
};

export function BLSSection() {
  const [data, setData] = useState<BLSPortalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'employment' | 'inflation' | 'regional' | 'surveys'>('overview');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/api/research/portal/bls/comprehensive');
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load BLS data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mr-3" />
          <span className="text-gray-600">Loading BLS data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-red-200 p-8">
        <div className="flex items-center justify-center text-red-600">
          <AlertCircle className="w-6 h-6 mr-3" />
          <span>{error}</span>
          <button onClick={fetchData} className="ml-4 text-blue-600 hover:underline">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'employment', label: 'Employment', icon: <Users className="w-4 h-4" /> },
    { id: 'inflation', label: 'Inflation & Prices', icon: <DollarSign className="w-4 h-4" /> },
    { id: 'regional', label: 'Regional Data', icon: <MapPin className="w-4 h-4" /> },
    { id: 'surveys', label: 'Survey Browser', icon: <Search className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center">
              <Building2 className="w-7 h-7 mr-3" />
              Bureau of Labor Statistics
            </h2>
            <p className="text-blue-100 mt-1">
              Employment, inflation, productivity, and compensation data
            </p>
          </div>
          <div className="text-right text-sm text-blue-100">
            <div>Last Updated: {new Date(data.last_updated).toLocaleString()}</div>
            <div className="mt-1">{data.surveys.length} Active Surveys</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200 bg-gray-50">
          <nav className="flex -mb-px overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'border-blue-600 text-blue-600 bg-white'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                {tab.icon}
                <span className="ml-2">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && <OverviewTab data={data} />}
          {activeTab === 'employment' && <EmploymentTab data={data} />}
          {activeTab === 'inflation' && <InflationTab data={data} />}
          {activeTab === 'regional' && <RegionalTab data={data} />}
          {activeTab === 'surveys' && <SurveysTab data={data} />}
        </div>
      </div>
    </div>
  );
}

function OverviewTab({ data }: { data: BLSPortalData }) {
  const indicators = data?.labor_indicators || [];
  const headlines = indicators.slice(0, 6);

  return (
    <div className="space-y-6">
      {/* Key Indicators Grid */}
      {headlines.length > 0 ? (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Economic Indicators</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {headlines.map((indicator) => (
              <div
                key={indicator.id}
                className="bg-gray-50 rounded-lg p-4 border border-gray-100 hover:border-blue-200 transition-colors"
              >
                <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
                  {indicator.name}
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {indicator.formatted_value || (indicator.value != null ? String(indicator.value) : 'N/A')}
                </div>
                <div className="flex items-center mt-2 text-xs">
                  {indicator.change != null && (
                    <span className={`flex items-center ${indicator.change > 0 ? 'text-green-600' : indicator.change < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                      {indicator.change > 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : indicator.change < 0 ? <TrendingDown className="w-3 h-3 mr-1" /> : null}
                      {indicator.change > 0 ? '+' : ''}{Number(indicator.change).toFixed(1)} MoM
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {indicator.period} {indicator.year}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p className="text-amber-800 text-sm">No labor indicators available.</p>
        </div>
      )}

      {/* Trend Charts */}
      {(data?.unemployment_trend?.length > 0 || data?.cpi_trend?.length > 0 || data?.payrolls_trend?.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {data.unemployment_trend?.length > 0 && (
            <TrendChart
              data={data.unemployment_trend}
              title="Unemployment Rate"
              subtitle="Seasonally adjusted, 36-month trend"
              color="#ef4444"
              height={180}
              valueFormatter={(v) => v != null ? `${Number(v).toFixed(1)}%` : 'N/A'}
              dateFormatter={(d) => {
                const parts = d?.split('-') || [];
                return parts.length >= 2 ? `${parts[1]}/${parts[0]?.slice(2)}` : d;
              }}
            />
          )}
          {data.cpi_trend?.length > 0 && (
            <TrendChart
              data={data.cpi_trend}
              title="CPI All Items"
              subtitle="Index value trend"
              color="#f59e0b"
              height={180}
              valueFormatter={(v) => v != null ? Number(v).toFixed(1) : 'N/A'}
              dateFormatter={(d) => {
                const parts = d?.split('-') || [];
                return parts.length >= 2 ? `${parts[1]}/${parts[0]?.slice(2)}` : d;
              }}
            />
          )}
          {data.payrolls_trend?.length > 0 && (
            <TrendChart
              data={data.payrolls_trend}
              title="Nonfarm Payrolls"
              subtitle="Total employment (thousands)"
              color="#10b981"
              height={180}
              valueFormatter={(v) => v != null ? `${(Number(v) / 1000).toFixed(1)}M` : 'N/A'}
              dateFormatter={(d) => {
                const parts = d?.split('-') || [];
                return parts.length >= 2 ? `${parts[1]}/${parts[0]?.slice(2)}` : d;
              }}
            />
          )}
        </div>
      )}

      {/* Indicators Table */}
      {indicators.length > 0 && (
        <DataTable
          data={indicators}
          title="All Labor Market Indicators"
          subtitle={`${indicators.length} indicators from multiple BLS surveys`}
          maxHeight="400px"
          columns={[
            { key: 'name', header: 'Indicator', width: '30%' },
            { key: 'source', header: 'Survey', width: '10%', render: (v) => <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{v}</code> },
            {
              key: 'formatted_value',
              header: 'Value',
              align: 'right',
              render: (v) => <span className="font-semibold">{v || 'N/A'}</span>
            },
            {
              key: 'change',
              header: 'Change',
              align: 'right',
              render: (v) => <ChangeRenderer value={v} />
            },
            {
              key: 'period',
              header: 'Period',
              align: 'center',
              render: (v, row) => <span className="text-gray-500">{v} {row.year}</span>
            },
          ]}
        />
      )}
    </div>
  );
}

function EmploymentTab({ data }: { data: BLSPortalData }) {
  const industries = data?.employment_by_industry || [];

  if (industries.length === 0) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <p className="text-amber-800">No employment by industry data available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Employment Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {industries.slice(0, 4).map((ind) => (
          <div key={ind.industry_code} className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-100">
            <div className="flex items-center text-blue-600 mb-2">
              {industryIcons[ind.industry_name] || <Building2 className="w-4 h-4" />}
              <span className="ml-2 text-sm font-medium">{ind.industry_name}</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {ind.employment != null ? (ind.employment / 1000).toFixed(1) : 'N/A'}M
            </div>
            <div className="flex items-center justify-between mt-2 text-xs">
              {ind.employment_change != null && (
                <span className={`flex items-center ${ind.employment_change > 0 ? 'text-green-600' : ind.employment_change < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                  {ind.employment_change > 0 ? '+' : ''}{ind.employment_change}K MoM
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Employment by Industry Table */}
      <DataTable
        data={industries}
        title="Employment by Industry"
        subtitle="Current Employment Statistics (CES) - All employees, thousands, seasonally adjusted"
        maxHeight="500px"
        columns={[
          {
            key: 'industry_name',
            header: 'Industry',
            width: '25%',
            render: (v) => (
              <div className="flex items-center">
                <span className="text-gray-400 mr-2">{industryIcons[v] || <Building2 className="w-4 h-4" />}</span>
                <span className="font-medium">{v}</span>
              </div>
            )
          },
          { key: 'industry_code', header: 'Code', width: '10%', render: (v) => <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{v}</code> },
          {
            key: 'employment',
            header: 'Employment (000s)',
            align: 'right',
            render: (v) => <NumberRenderer value={v} decimals={0} />
          },
          {
            key: 'employment_change',
            header: 'MoM Change',
            align: 'right',
            render: (v) => <ChangeRenderer value={v} suffix="K" />
          },
          {
            key: 'avg_hourly_earnings',
            header: 'Avg Hourly $',
            align: 'right',
            render: (v) => v != null ? <NumberRenderer value={v} decimals={2} prefix="$" /> : <span className="text-gray-400">-</span>
          },
          {
            key: 'avg_weekly_hours',
            header: 'Avg Weekly Hrs',
            align: 'right',
            render: (v) => v != null ? <NumberRenderer value={v} decimals={1} /> : <span className="text-gray-400">-</span>
          },
        ]}
      />

      {/* Payroll Trend */}
      {data?.payrolls_trend?.length > 0 && (
        <TrendChart
          data={data.payrolls_trend}
          title="Nonfarm Payrolls Trend"
          subtitle="Total employment (thousands)"
          color="#3b82f6"
          height={220}
          valueFormatter={(v) => v != null ? `${(Number(v) / 1000).toFixed(1)}M` : 'N/A'}
          dateFormatter={(d) => {
            const parts = d?.split('-') || [];
            return parts.length >= 2 ? `${parts[1]}/${parts[0]?.slice(2)}` : d;
          }}
        />
      )}
    </div>
  );
}

function InflationTab({ data }: { data: BLSPortalData }) {
  const cpiCategories = data?.cpi_categories || [];
  const indicators = data?.labor_indicators || [];

  // Find CPI values from indicators
  const cpiAllItems = indicators.find(i => i.id === 'cpi_yoy');
  const cpiCore = indicators.find(i => i.id === 'cpi_core_yoy');
  const ppi = indicators.find(i => i.id === 'ppi_yoy');

  return (
    <div className="space-y-6">
      {/* Inflation Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-lg p-5 border border-orange-100">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-orange-600 font-medium">CPI All Items YoY</div>
              <div className="text-3xl font-bold text-gray-900 mt-1">
                {cpiAllItems?.formatted_value || (cpiAllItems?.value != null ? `${cpiAllItems.value}%` : 'N/A')}
              </div>
            </div>
            <Activity className="w-10 h-10 text-orange-300" />
          </div>
          <div className="mt-3 text-xs text-gray-500">
            Consumer Price Index for All Urban Consumers
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg p-5 border border-yellow-100">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-yellow-600 font-medium">Core CPI YoY</div>
              <div className="text-3xl font-bold text-gray-900 mt-1">
                {cpiCore?.formatted_value || (cpiCore?.value != null ? `${cpiCore.value}%` : 'N/A')}
              </div>
            </div>
            <Activity className="w-10 h-10 text-yellow-300" />
          </div>
          <div className="mt-3 text-xs text-gray-500">
            Excluding food and energy
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-5 border border-purple-100">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-purple-600 font-medium">PPI Final Demand</div>
              <div className="text-3xl font-bold text-gray-900 mt-1">
                {ppi?.formatted_value || (ppi?.value != null ? `${ppi.value}%` : 'N/A')}
              </div>
            </div>
            <Activity className="w-10 h-10 text-purple-300" />
          </div>
          <div className="mt-3 text-xs text-gray-500">
            Producer Price Index
          </div>
        </div>
      </div>

      {/* CPI by Category Table */}
      {cpiCategories.length > 0 && (
        <DataTable
          data={cpiCategories}
          title="CPI by Category"
          subtitle="Consumer Price Index components with monthly and annual changes"
          maxHeight="450px"
          columns={[
            { key: 'item_name', header: 'Category', width: '35%' },
            { key: 'item_code', header: 'Item Code', width: '12%', render: (v) => <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{v}</code> },
            {
              key: 'index_value',
              header: 'Index Value',
              align: 'right',
              render: (v) => <NumberRenderer value={v} decimals={3} />
            },
            {
              key: 'mom_change',
              header: 'MoM %',
              align: 'right',
              render: (v) => <ChangeRenderer value={v} suffix="%" />
            },
            {
              key: 'yoy_change',
              header: 'YoY %',
              align: 'right',
              render: (v) => <ChangeRenderer value={v} suffix="%" />
            },
          ]}
        />
      )}

      {/* CPI Trend Chart */}
      {data?.cpi_trend?.length > 0 && (
        <TrendChart
          data={data.cpi_trend}
          title="CPI Index Value Trend"
          subtitle="All Items, U.S. City Average"
          color="#f59e0b"
          height={220}
          valueFormatter={(v) => v != null ? Number(v).toFixed(1) : 'N/A'}
          dateFormatter={(d) => {
            const parts = d?.split('-') || [];
            return parts.length >= 2 ? `${parts[1]}/${parts[0]?.slice(2)}` : d;
          }}
        />
      )}
    </div>
  );
}

function RegionalTab({ data }: { data: BLSPortalData }) {
  const regionalData = data?.regional_unemployment || [];

  if (regionalData.length === 0) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <p className="text-amber-800">No regional unemployment data available.</p>
      </div>
    );
  }

  // Sort by unemployment rate for rankings
  const sortedByRate = [...regionalData].sort((a, b) => (a.unemployment_rate || 0) - (b.unemployment_rate || 0));
  const lowestRates = sortedByRate.slice(0, 5);
  const highestRates = sortedByRate.slice(-5).reverse();

  return (
    <div className="space-y-6">
      {/* Top/Bottom States */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-green-50 rounded-lg p-5 border border-green-100">
          <h4 className="text-sm font-semibold text-green-800 mb-3 flex items-center">
            <TrendingDown className="w-4 h-4 mr-2" />
            Lowest Unemployment Rates
          </h4>
          <div className="space-y-2">
            {lowestRates.map((state, idx) => (
              <div key={state.area_code} className="flex items-center justify-between py-2 border-b border-green-100 last:border-0">
                <div className="flex items-center">
                  <span className="w-6 h-6 rounded-full bg-green-200 text-green-800 text-xs font-bold flex items-center justify-center mr-3">
                    {idx + 1}
                  </span>
                  <span className="font-medium text-gray-900">{state.area_name}</span>
                </div>
                <span className="font-bold text-green-700">
                  {state.unemployment_rate != null ? `${Number(state.unemployment_rate).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-red-50 rounded-lg p-5 border border-red-100">
          <h4 className="text-sm font-semibold text-red-800 mb-3 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" />
            Highest Unemployment Rates
          </h4>
          <div className="space-y-2">
            {highestRates.map((state, idx) => (
              <div key={state.area_code} className="flex items-center justify-between py-2 border-b border-red-100 last:border-0">
                <div className="flex items-center">
                  <span className="w-6 h-6 rounded-full bg-red-200 text-red-800 text-xs font-bold flex items-center justify-center mr-3">
                    {regionalData.length - idx}
                  </span>
                  <span className="font-medium text-gray-900">{state.area_name}</span>
                </div>
                <span className="font-bold text-red-700">
                  {state.unemployment_rate != null ? `${Number(state.unemployment_rate).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Full Regional Table */}
      <DataTable
        data={regionalData}
        title="State Unemployment Data"
        subtitle="Local Area Unemployment Statistics (LAUS) - Seasonally adjusted"
        maxHeight="500px"
        columns={[
          { key: 'area_name', header: 'State/Area', width: '20%' },
          { key: 'area_code', header: 'Code', width: '8%', render: (v) => <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{v?.slice(-2) || v}</code> },
          {
            key: 'unemployment_rate',
            header: 'Rate %',
            align: 'right',
            render: (v) => (
              <span className={`font-semibold ${v != null && v < 4 ? 'text-green-600' : v != null && v > 5 ? 'text-red-600' : 'text-yellow-600'}`}>
                {v != null ? `${Number(v).toFixed(1)}%` : 'N/A'}
              </span>
            )
          },
          {
            key: 'rate_change',
            header: 'Change',
            align: 'right',
            render: (v) => <ChangeRenderer value={v} suffix="%" />
          },
          {
            key: 'period',
            header: 'Period',
            align: 'center',
            render: (v, row) => <span className="text-gray-500">{v} {row.year}</span>
          },
          {
            key: 'labor_force',
            header: 'Labor Force',
            align: 'right',
            render: (v) => <NumberRenderer value={v / 1000} decimals={0} suffix="K" />
          },
        ]}
      />

      {/* Unemployment Trend */}
      <TrendChart
        data={data.unemployment_trend}
        title="National Unemployment Rate Trend"
        subtitle="36-month historical trend"
        color="#ef4444"
        height={220}
        valueFormatter={(v) => `${v.toFixed(1)}%`}
        dateFormatter={(d) => {
          const [year, month] = d.split('-');
          return `${month}/${year.slice(2)}`;
        }}
      />
    </div>
  );
}

function SurveysTab({ data }: { data: BLSPortalData }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSurveys = data.surveys.filter(s =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (s.survey_id || s.code).toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Search surveys by name, ID, or description..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Survey Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSurveys.map((survey) => {
          const surveyId = survey.survey_id || survey.code;
          const freq = survey.frequency || survey.update_frequency;
          const recordCount = survey.record_count ?? survey.series_count;

          return (
            <div
              key={surveyId}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <code className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded font-semibold">
                      {surveyId}
                    </code>
                    <span className={`ml-2 text-xs px-2 py-0.5 rounded ${
                      freq === 'Monthly' ? 'bg-green-100 text-green-700' :
                      freq === 'Quarterly' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-purple-100 text-purple-700'
                    }`}>
                      {freq}
                    </span>
                  </div>
                  <h4 className="font-semibold text-gray-900 mt-2 group-hover:text-blue-600 transition-colors">
                    {survey.name}
                  </h4>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                    {survey.description}
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-blue-500 transition-colors flex-shrink-0 ml-2" />
              </div>
              <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                <span>{recordCount?.toLocaleString() || 'N/A'} records</span>
                <span>Latest: {survey.latest_period || 'N/A'}</span>
              </div>
            </div>
          );
        })}
      </div>

      {filteredSurveys.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Search className="w-12 h-12 mx-auto text-gray-300 mb-3" />
          <p>No surveys found matching "{searchTerm}"</p>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
        <Info className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
        <div className="text-sm text-blue-800">
          <p className="font-medium">About BLS Surveys</p>
          <p className="mt-1 text-blue-600">
            The Bureau of Labor Statistics collects data through various surveys covering employment,
            unemployment, prices, compensation, productivity, and more. Click on any survey card to
            explore its data in detail.
          </p>
        </div>
      </div>
    </div>
  );
}

export default BLSSection;
