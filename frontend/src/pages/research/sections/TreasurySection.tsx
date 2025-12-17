import { useState, useEffect } from 'react';
import {
  Landmark,
  Calendar,
  DollarSign,
  BarChart3,
  Activity,
  RefreshCw,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight,
  Info,
} from 'lucide-react';
import { DataTable, NumberRenderer } from '../components/DataTable';
import { TrendChart } from '../components/TrendChart';
import api from '../../../services/api';

interface YieldCurvePoint {
  maturity: string;
  maturity_months: number;
  yield_value: number | null;
  change_1d: number | null;
  change_1w: number | null;
  change_1m: number | null;
}

interface TrendPoint {
  date: string;
  value: number;
}

interface SpreadData {
  name: string;
  spread_bps: number | null;
  change_1d?: number | null;
  change_1w?: number | null;
}

interface AuctionResult {
  security_type: string;
  security_term: string;
  auction_date: string;
  issue_date?: string | null;
  maturity_date?: string | null;
  high_yield: number | null;
  bid_to_cover: number | null;
  total_accepted: number | null;
  cusip?: string | null;
}

interface UpcomingAuction {
  security_type: string;
  security_term: string;
  announcement_date?: string | null;
  auction_date: string;
  issue_date?: string | null;
  offering_amount: number | null;
}

interface TreasuryPortalData {
  yield_curve: YieldCurvePoint[];
  yield_trend_2y: TrendPoint[];
  yield_trend_10y: TrendPoint[];
  spreads: SpreadData[];
  recent_auctions: AuctionResult[];
  upcoming_auctions: UpcomingAuction[];
  quick_studies: Array<{ id: string; title: string; description: string }>;
  last_updated: string;
}

export function TreasurySection() {
  const [data, setData] = useState<TreasuryPortalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'yields' | 'auctions' | 'upcoming'>('overview');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/api/research/portal/treasury/comprehensive');
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load Treasury data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="flex items-center justify-center">
          <RefreshCw className="w-6 h-6 animate-spin text-emerald-600 mr-3" />
          <span className="text-gray-600">Loading Treasury data...</span>
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
          <button onClick={fetchData} className="ml-4 text-emerald-600 hover:underline">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'yields', label: 'Yield Curve', icon: <Activity className="w-4 h-4" /> },
    { id: 'auctions', label: 'Recent Auctions', icon: <DollarSign className="w-4 h-4" /> },
    { id: 'upcoming', label: 'Upcoming Auctions', icon: <Calendar className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center">
              <Landmark className="w-7 h-7 mr-3" />
              U.S. Treasury Securities
            </h2>
            <p className="text-emerald-100 mt-1">
              Yield curves, spreads, and auction results
            </p>
          </div>
          <div className="text-right text-sm text-emerald-100">
            <div>Last Updated: {data.last_updated ? new Date(data.last_updated).toLocaleString() : 'N/A'}</div>
            <div className="mt-1">{data.yield_curve?.length || 0} Maturity Points</div>
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
                    ? 'border-emerald-600 text-emerald-600 bg-white'
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
          {activeTab === 'yields' && <YieldsTab data={data} />}
          {activeTab === 'auctions' && <AuctionsTab data={data} />}
          {activeTab === 'upcoming' && <UpcomingTab data={data} />}
        </div>
      </div>
    </div>
  );
}

function OverviewTab({ data }: { data: TreasuryPortalData }) {
  return (
    <div className="space-y-6">
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-amber-800 mb-2">Treasury Overview</h3>
        <p className="text-amber-700">
          Treasury yield curve data will be displayed here once the treasury_daily_rates table is populated.
        </p>
        <p className="text-amber-600 text-sm mt-2">
          Recent auctions: {data?.recent_auctions?.length || 0} |
          Upcoming auctions: {data?.upcoming_auctions?.length || 0}
        </p>
      </div>
    </div>
  );
}

function YieldsTab({ data }: { data: TreasuryPortalData }) {
  const yieldCurve = data.yield_curve || [];
  const hasYieldData = yieldCurve.length > 0;

  if (!hasYieldData) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <p className="text-amber-800">
          No yield curve data available. Treasury daily rates have not been populated yet.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Full Yield Curve Table */}
      <DataTable
        data={yieldCurve}
        title="Treasury Yield Curve"
        subtitle={`As of ${data.last_updated ? new Date(data.last_updated).toLocaleDateString() : 'Today'}`}
        maxHeight="400px"
        columns={[
          { key: 'maturity', header: 'Maturity', width: '20%' },
          {
            key: 'yield_value',
            header: 'Yield %',
            align: 'right',
            render: (v) => v != null ? <span className="font-semibold text-emerald-700">{Number(v).toFixed(2)}%</span> : <span className="text-gray-400">-</span>
          },
          {
            key: 'change_1d',
            header: '1D Chg (bps)',
            align: 'right',
            render: (v) => v != null ? (
              <span className={`flex items-center justify-end ${Number(v) > 0 ? 'text-red-600' : Number(v) < 0 ? 'text-green-600' : 'text-gray-500'}`}>
                {Number(v) > 0 ? <ArrowUpRight className="w-3 h-3 mr-1" /> : Number(v) < 0 ? <ArrowDownRight className="w-3 h-3 mr-1" /> : null}
                {Number(v) > 0 ? '+' : ''}{Number(v).toFixed(0)}
              </span>
            ) : <span className="text-gray-400">-</span>
          },
          {
            key: 'change_1w',
            header: '1W Chg (bps)',
            align: 'right',
            render: (v) => v != null ? (
              <span className={`${Number(v) > 0 ? 'text-red-600' : Number(v) < 0 ? 'text-green-600' : 'text-gray-500'}`}>
                {Number(v) > 0 ? '+' : ''}{Number(v).toFixed(0)}
              </span>
            ) : <span className="text-gray-400">-</span>
          },
          {
            key: 'change_1m',
            header: '1M Chg (bps)',
            align: 'right',
            render: (v) => v != null ? (
              <span className={`${Number(v) > 0 ? 'text-red-600' : Number(v) < 0 ? 'text-green-600' : 'text-gray-500'}`}>
                {Number(v) > 0 ? '+' : ''}{Number(v).toFixed(0)}
              </span>
            ) : <span className="text-gray-400">-</span>
          },
        ]}
      />

      {/* Visual Yield Curve */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Yield Curve Visualization</h3>
        <div className="h-64">
          <TrendChart
            data={yieldCurve.filter(y => y.yield_value != null).map(y => ({
              date: y.maturity,
              value: y.yield_value!,
            }))}
            color="#10b981"
            height={220}
            showArea={true}
            valueFormatter={(v) => v != null ? `${Number(v).toFixed(2)}%` : 'N/A'}
            dateFormatter={(d) => d.replace('-', '')}
          />
        </div>
      </div>

      {/* Rate Comparison */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {yieldCurve.filter(y => ['1-Month', '6-Month', '2-Year', '10-Year'].includes(y.maturity)).map((point) => (
          <div key={point.maturity} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="text-xs text-gray-500 uppercase tracking-wide">{point.maturity}</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">
              {point.yield_value != null ? `${Number(point.yield_value).toFixed(2)}%` : 'N/A'}
            </div>
            <div className="mt-2 space-y-1 text-xs">
              {point.change_1d != null && (
                <div className="flex justify-between">
                  <span className="text-gray-500">1D:</span>
                  <span className={Number(point.change_1d) > 0 ? 'text-red-600' : Number(point.change_1d) < 0 ? 'text-green-600' : 'text-gray-500'}>
                    {Number(point.change_1d) > 0 ? '+' : ''}{Number(point.change_1d).toFixed(0)} bps
                  </span>
                </div>
              )}
              {point.change_1w != null && (
                <div className="flex justify-between">
                  <span className="text-gray-500">1W:</span>
                  <span className={Number(point.change_1w) > 0 ? 'text-red-600' : Number(point.change_1w) < 0 ? 'text-green-600' : 'text-gray-500'}>
                    {Number(point.change_1w) > 0 ? '+' : ''}{Number(point.change_1w).toFixed(0)} bps
                  </span>
                </div>
              )}
              {point.change_1m != null && (
                <div className="flex justify-between">
                  <span className="text-gray-500">1M:</span>
                  <span className={Number(point.change_1m) > 0 ? 'text-red-600' : Number(point.change_1m) < 0 ? 'text-green-600' : 'text-gray-500'}>
                    {Number(point.change_1m) > 0 ? '+' : ''}{Number(point.change_1m).toFixed(0)} bps
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AuctionsTab({ data }: { data: TreasuryPortalData }) {
  return (
    <div className="space-y-6">
      {/* Auction Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-100">
          <div className="text-xs text-emerald-600 font-medium">Total Auctions</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{data.recent_auctions?.length || 0}</div>
          <div className="text-xs text-gray-500 mt-1">Last 30 days</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
          <div className="text-xs text-blue-600 font-medium">Avg Bid-to-Cover</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {(() => {
              const withBidCover = data.recent_auctions?.filter(a => a.bid_to_cover != null) || [];
              if (withBidCover.length === 0) return '0.00';
              const sum = withBidCover.reduce((acc, a) => acc + (a.bid_to_cover || 0), 0);
              return (sum / withBidCover.length).toFixed(2);
            })()}x
          </div>
          <div className="text-xs text-gray-500 mt-1">Recent auctions</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
          <div className="text-xs text-purple-600 font-medium">Total Accepted</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            ${((data.recent_auctions?.reduce((sum, a) => sum + (a.total_accepted || 0), 0) || 0) / 1e9).toFixed(1)}B
          </div>
          <div className="text-xs text-gray-500 mt-1">All auctions</div>
        </div>
        <div className="bg-orange-50 rounded-lg p-4 border border-orange-100">
          <div className="text-xs text-orange-600 font-medium">Avg High Yield</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {(() => {
              const withYield = data.recent_auctions?.filter(a => a.high_yield != null) || [];
              if (withYield.length === 0) return '0.00';
              const sum = withYield.reduce((acc, a) => acc + (a.high_yield || 0), 0);
              return (sum / withYield.length).toFixed(2);
            })()}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Recent auctions</div>
        </div>
      </div>

      {/* Auction Results Table */}
      <DataTable
        data={data.recent_auctions || []}
        title="Recent Auction Results"
        subtitle="Treasury securities auction results"
        maxHeight="500px"
        columns={[
          {
            key: 'security_type',
            header: 'Type',
            width: '12%',
            render: (v) => (
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                v === 'Bill' ? 'bg-blue-100 text-blue-700' :
                v === 'Note' ? 'bg-emerald-100 text-emerald-700' :
                v === 'Bond' ? 'bg-purple-100 text-purple-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {v}
              </span>
            )
          },
          { key: 'security_term', header: 'Term', width: '10%' },
          {
            key: 'auction_date',
            header: 'Auction Date',
            width: '12%',
            render: (v) => v ? new Date(v).toLocaleDateString() : <span className="text-gray-400">-</span>
          },
          {
            key: 'high_yield',
            header: 'High Yield',
            align: 'right',
            render: (v) => v != null ? <span className="font-medium">{Number(v).toFixed(3)}%</span> : <span className="text-gray-400">-</span>
          },
          {
            key: 'bid_to_cover',
            header: 'Bid/Cover',
            align: 'right',
            render: (v) => v != null ? (
              <span className={`font-medium ${Number(v) >= 2.5 ? 'text-green-600' : Number(v) < 2.0 ? 'text-red-600' : 'text-gray-700'}`}>
                {Number(v).toFixed(2)}x
              </span>
            ) : <span className="text-gray-400">-</span>
          },
          {
            key: 'total_accepted',
            header: 'Accepted ($B)',
            align: 'right',
            render: (v) => v != null ? <NumberRenderer value={v / 1e9} decimals={1} prefix="$" suffix="B" /> : <span className="text-gray-400">-</span>
          },
          {
            key: 'cusip',
            header: 'CUSIP',
            render: (v) => v ? <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{v}</code> : <span className="text-gray-400">-</span>
          },
        ]}
      />

      {/* Bid-to-Cover Explanation */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 flex items-start">
        <Info className="w-5 h-5 text-gray-400 mt-0.5 mr-3 flex-shrink-0" />
        <div className="text-sm text-gray-600">
          <p className="font-medium text-gray-700">Understanding Bid-to-Cover Ratio</p>
          <p className="mt-1">
            The bid-to-cover ratio indicates demand for Treasury securities. A ratio above 2.5x typically
            indicates strong demand, while below 2.0x may suggest weaker interest. Higher ratios generally
            result in lower yields (higher prices) for the securities.
          </p>
        </div>
      </div>
    </div>
  );
}

function UpcomingTab({ data }: { data: TreasuryPortalData }) {
  // Group by auction date
  const upcomingAuctions = data.upcoming_auctions || [];
  const groupedByDate = upcomingAuctions.reduce((acc, auction) => {
    const date = auction.auction_date;
    if (!acc[date]) acc[date] = [];
    acc[date].push(auction);
    return acc;
  }, {} as Record<string, typeof upcomingAuctions>);

  const sortedDates = Object.keys(groupedByDate).sort();

  return (
    <div className="space-y-6">
      {/* Calendar View */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Auction Schedule</h3>
        <div className="space-y-4">
          {sortedDates.slice(0, 10).map((date) => {
            const auctions = groupedByDate[date];
            const dateObj = new Date(date);
            const isToday = dateObj.toDateString() === new Date().toDateString();
            const isTomorrow = dateObj.toDateString() === new Date(Date.now() + 86400000).toDateString();

            return (
              <div
                key={date}
                className={`rounded-lg border ${
                  isToday ? 'border-emerald-300 bg-emerald-50' :
                  isTomorrow ? 'border-blue-200 bg-blue-50' :
                  'border-gray-200 bg-white'
                }`}
              >
                <div className={`px-4 py-3 border-b ${
                  isToday ? 'border-emerald-200 bg-emerald-100' :
                  isTomorrow ? 'border-blue-100 bg-blue-100' :
                  'border-gray-100 bg-gray-50'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Calendar className={`w-4 h-4 mr-2 ${
                        isToday ? 'text-emerald-600' :
                        isTomorrow ? 'text-blue-600' :
                        'text-gray-500'
                      }`} />
                      <span className="font-semibold text-gray-900">
                        {dateObj.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                      </span>
                      {isToday && <span className="ml-2 text-xs bg-emerald-600 text-white px-2 py-0.5 rounded">Today</span>}
                      {isTomorrow && <span className="ml-2 text-xs bg-blue-600 text-white px-2 py-0.5 rounded">Tomorrow</span>}
                    </div>
                    <span className="text-sm text-gray-500">{auctions.length} auction{auctions.length > 1 ? 's' : ''}</span>
                  </div>
                </div>
                <div className="divide-y divide-gray-100">
                  {auctions.map((auction, idx) => (
                    <div key={idx} className="px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors">
                      <div className="flex items-center">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold mr-3 ${
                          auction.security_type === 'Bill' ? 'bg-blue-100 text-blue-700' :
                          auction.security_type === 'Note' ? 'bg-emerald-100 text-emerald-700' :
                          auction.security_type === 'Bond' ? 'bg-purple-100 text-purple-700' :
                          auction.security_type === 'FRN' ? 'bg-orange-100 text-orange-700' :
                          auction.security_type === 'TIPS' ? 'bg-pink-100 text-pink-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {auction.security_type}
                        </span>
                        <div>
                          <span className="font-medium text-gray-900">{auction.security_term}</span>
                          {auction.offering_amount != null && (
                            <span className="ml-2 text-sm text-gray-500">
                              ${(Number(auction.offering_amount) / 1e9).toFixed(0)}B offering
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right text-sm text-gray-500">
                        {auction.issue_date && <div>Issue: {new Date(auction.issue_date).toLocaleDateString()}</div>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Full Table */}
      <DataTable
        data={upcomingAuctions}
        title="All Upcoming Auctions"
        subtitle="Treasury auction schedule"
        maxHeight="400px"
        columns={[
          {
            key: 'security_type',
            header: 'Type',
            width: '10%',
            render: (v) => (
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                v === 'Bill' ? 'bg-blue-100 text-blue-700' :
                v === 'Note' ? 'bg-emerald-100 text-emerald-700' :
                v === 'Bond' ? 'bg-purple-100 text-purple-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {v}
              </span>
            )
          },
          { key: 'security_term', header: 'Term' },
          {
            key: 'announcement_date',
            header: 'Announced',
            render: (v) => v ? new Date(v).toLocaleDateString() : <span className="text-gray-400">-</span>
          },
          {
            key: 'auction_date',
            header: 'Auction',
            render: (v) => v ? new Date(v).toLocaleDateString() : <span className="text-gray-400">-</span>
          },
          {
            key: 'issue_date',
            header: 'Issue',
            render: (v) => v ? new Date(v).toLocaleDateString() : <span className="text-gray-400">-</span>
          },
          {
            key: 'offering_amount',
            header: 'Offering',
            align: 'right',
            render: (v) => v ? <NumberRenderer value={v / 1e9} decimals={0} prefix="$" suffix="B" /> : <span className="text-gray-400">TBD</span>
          },
        ]}
      />
    </div>
  );
}

export default TreasurySection;
