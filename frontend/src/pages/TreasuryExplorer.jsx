import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { treasuryResearchAPI } from '../services/api';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowLeft,
  Info,
  X,
  Loader2,
  Calendar,
  DollarSign,
  BarChart3,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
  Legend,
} from 'recharts';

// Term colors
const TERM_COLORS = {
  '2-Year': '#667eea',
  '5-Year': '#4facfe',
  '7-Year': '#43e97b',
  '10-Year': '#f5576c',
  '20-Year': '#fa709a',
  '30-Year': '#a18cd1',
};

// Period options
const PERIOD_OPTIONS = [
  { label: '1Y', value: 1 },
  { label: '3Y', value: 3 },
  { label: '5Y', value: 5 },
  { label: '10Y', value: 10 },
  { label: '20Y', value: 20 },
];

// Format yield
const formatYield = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return `${value.toFixed(3)}%`;
};

// Format amount in billions
const formatAmount = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return `$${(value / 1e9).toFixed(1)}B`;
};

// Term Summary Card
function TermCard({ term, data, onClick, isSelected }) {
  const color = TERM_COLORS[term] || '#667eea';
  const yieldChange = data?.yield_change;
  const direction =
    yieldChange === null || yieldChange === undefined
      ? 'flat'
      : yieldChange > 0.001
        ? 'up'
        : yieldChange < -0.001
          ? 'down'
          : 'flat';

  const TrendIcon = direction === 'up' ? TrendingUp : direction === 'down' ? TrendingDown : Minus;

  return (
    <div
      onClick={onClick}
      className={`cursor-pointer p-4 bg-white rounded-lg border-t-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg ${
        isSelected ? 'ring-2 shadow-lg' : 'shadow-sm'
      }`}
      style={{
        borderTopColor: color,
        ...(isSelected && { ringColor: color }),
      }}
    >
      <h3 className="text-lg font-bold" style={{ color }}>
        {term}
      </h3>

      {data ? (
        <>
          <div className="mt-2">
            <p className="text-xs text-gray-500">Latest Yield</p>
            <p className="text-2xl font-bold text-gray-900">{formatYield(data.high_yield)}</p>
          </div>

          {yieldChange !== null && yieldChange !== undefined && (
            <div className="flex items-center gap-1 mt-1">
              <TrendIcon
                className={`w-4 h-4 ${
                  direction === 'up'
                    ? 'text-red-500'
                    : direction === 'down'
                      ? 'text-green-500'
                      : 'text-gray-400'
                }`}
              />
              <span
                className={`text-sm ${
                  direction === 'up'
                    ? 'text-red-500'
                    : direction === 'down'
                      ? 'text-green-500'
                      : 'text-gray-400'
                }`}
              >
                {yieldChange > 0 ? '+' : ''}
                {(yieldChange * 100).toFixed(1)} bps
              </span>
            </div>
          )}

          <div className="mt-3 flex gap-4 text-sm">
            <div>
              <p className="text-xs text-gray-500">Bid-to-Cover</p>
              <p className="font-medium">{data.bid_to_cover_ratio?.toFixed(2) || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Date</p>
              <p className="font-medium">{data.auction_date || 'N/A'}</p>
            </div>
          </div>
        </>
      ) : (
        <p className="text-gray-400 mt-4">No data</p>
      )}
    </div>
  );
}

// Auction Detail Modal
function AuctionDetailModal({ auction, detail, loading, onClose }) {
  if (!auction) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">
            Auction Details - {auction.security_term} ({auction.auction_date})
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-full">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4">
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : detail ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Basic Info */}
              <div>
                <h3 className="text-sm font-semibold text-blue-600 mb-2">Basic Information</h3>
                <table className="w-full text-sm">
                  <tbody>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">CUSIP</td>
                      <td className="py-2 font-mono">{detail.cusip}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Security Type</td>
                      <td className="py-2">{detail.security_type}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Term</td>
                      <td className="py-2">{detail.security_term}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Issue Date</td>
                      <td className="py-2">{detail.issue_date || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-medium text-gray-600">Maturity Date</td>
                      <td className="py-2">{detail.maturity_date || 'N/A'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Yield Info */}
              <div>
                <h3 className="text-sm font-semibold text-blue-600 mb-2">Yield Information</h3>
                <table className="w-full text-sm">
                  <tbody>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">High Yield</td>
                      <td className="py-2 font-mono">{formatYield(detail.high_yield)}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Low Yield</td>
                      <td className="py-2 font-mono">{formatYield(detail.low_yield)}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Median Yield</td>
                      <td className="py-2 font-mono">{formatYield(detail.median_yield)}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Coupon Rate</td>
                      <td className="py-2 font-mono">{formatYield(detail.coupon_rate)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-medium text-gray-600">Price per $100</td>
                      <td className="py-2 font-mono">${detail.price_per_100?.toFixed(4) || 'N/A'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Demand Info */}
              <div>
                <h3 className="text-sm font-semibold text-blue-600 mb-2">Demand Metrics</h3>
                <table className="w-full text-sm">
                  <tbody>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Offering Amount</td>
                      <td className="py-2 font-mono">{formatAmount(detail.offering_amount)}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Total Tendered</td>
                      <td className="py-2 font-mono">{formatAmount(detail.total_tendered)}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Total Accepted</td>
                      <td className="py-2 font-mono">{formatAmount(detail.total_accepted)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-medium text-gray-600">Bid-to-Cover</td>
                      <td className="py-2 font-mono font-bold text-blue-600">
                        {detail.bid_to_cover_ratio?.toFixed(2) || 'N/A'}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Bidder Breakdown */}
              <div>
                <h3 className="text-sm font-semibold text-blue-600 mb-2">Bidder Breakdown</h3>
                <table className="w-full text-sm">
                  <tbody>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Primary Dealer</td>
                      <td className="py-2 font-mono">{formatAmount(detail.primary_dealer_accepted)}</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2 font-medium text-gray-600">Direct Bidder</td>
                      <td className="py-2 font-mono">{formatAmount(detail.direct_bidder_accepted)}</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-medium text-gray-600">Indirect Bidder</td>
                      <td className="py-2 font-mono">{formatAmount(detail.indirect_bidder_accepted)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg">
              Failed to load auction details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function TreasuryExplorer() {
  const navigate = useNavigate();
  const [selectedTerm, setSelectedTerm] = useState('10-Year');
  const [periodYears, setPeriodYears] = useState(5);
  const [selectedAuction, setSelectedAuction] = useState(null);

  // Data states
  const [snapshot, setSnapshot] = useState(null);
  const [snapshotLoading, setSnapshotLoading] = useState(true);
  const [yieldHistory, setYieldHistory] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [recentAuctions, setRecentAuctions] = useState([]);
  const [auctionsLoading, setAuctionsLoading] = useState(false);
  const [upcomingAuctions, setUpcomingAuctions] = useState([]);
  const [auctionDetail, setAuctionDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Fetch snapshot
  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        setSnapshotLoading(true);
        const response = await treasuryResearchAPI.getSnapshot();
        setSnapshot(response.data);
      } catch (error) {
        console.error('Failed to fetch snapshot:', error);
      } finally {
        setSnapshotLoading(false);
      }
    };
    fetchSnapshot();
  }, []);

  // Fetch upcoming auctions
  useEffect(() => {
    const fetchUpcoming = async () => {
      try {
        const response = await treasuryResearchAPI.getUpcoming();
        setUpcomingAuctions(response.data);
      } catch (error) {
        console.error('Failed to fetch upcoming auctions:', error);
      }
    };
    fetchUpcoming();
  }, []);

  // Fetch yield history when term or period changes
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setHistoryLoading(true);
        const response = await treasuryResearchAPI.getYieldHistory(selectedTerm, periodYears);
        setYieldHistory(response.data);
      } catch (error) {
        console.error('Failed to fetch yield history:', error);
      } finally {
        setHistoryLoading(false);
      }
    };
    if (selectedTerm) {
      fetchHistory();
    }
  }, [selectedTerm, periodYears]);

  // Fetch recent auctions when term changes
  useEffect(() => {
    const fetchAuctions = async () => {
      try {
        setAuctionsLoading(true);
        const response = await treasuryResearchAPI.getAuctions({
          security_term: selectedTerm,
          limit: 20,
        });
        setRecentAuctions(response.data);
      } catch (error) {
        console.error('Failed to fetch auctions:', error);
      } finally {
        setAuctionsLoading(false);
      }
    };
    if (selectedTerm) {
      fetchAuctions();
    }
  }, [selectedTerm]);

  // Fetch auction detail
  useEffect(() => {
    const fetchDetail = async () => {
      if (!selectedAuction?.auction_id) return;
      try {
        setDetailLoading(true);
        const response = await treasuryResearchAPI.getAuctionDetail(selectedAuction.auction_id);
        setAuctionDetail(response.data);
      } catch (error) {
        console.error('Failed to fetch auction detail:', error);
        setAuctionDetail(null);
      } finally {
        setDetailLoading(false);
      }
    };
    fetchDetail();
  }, [selectedAuction?.auction_id]);

  // Get snapshot as map
  const snapshotMap = useMemo(() => {
    if (!snapshot?.data) return {};
    return Object.fromEntries(snapshot.data.map((d) => [d.security_term, d]));
  }, [snapshot]);

  // Chart data
  const chartData = useMemo(() => {
    if (!yieldHistory?.data) return [];
    return yieldHistory.data.map((d) => ({
      date: d.auction_date,
      yield: d.high_yield,
      bidToCover: d.bid_to_cover_ratio,
      amount: d.offering_amount ? d.offering_amount / 1e9 : null,
    }));
  }, [yieldHistory]);

  const color = TERM_COLORS[selectedTerm] || '#667eea';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-2">
        <button
          onClick={() => navigate('/dashboard')}
          className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Treasury Auction Explorer</h1>
      </div>
      <p className="text-gray-600 mb-6 ml-12">
        Explore U.S. Treasury Notes & Bonds auction history and yields
      </p>

      {/* Term Summary Cards */}
      <h2 className="text-lg font-semibold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1 inline-block">
        Latest Auctions by Term
      </h2>

      {snapshotLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          {['2-Year', '5-Year', '7-Year', '10-Year', '20-Year', '30-Year'].map((term) => (
            <TermCard
              key={term}
              term={term}
              data={snapshotMap[term]}
              onClick={() => setSelectedTerm(term)}
              isSelected={selectedTerm === term}
            />
          ))}
        </div>
      )}

      <hr className="my-6" />

      {/* Yield History Section */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-4">
        <h2 className="text-lg font-semibold text-blue-600 border-b-2 border-blue-600 pb-1">
          {selectedTerm} Yield History
        </h2>

        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          {PERIOD_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setPeriodYears(opt.value)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
                periodYears === opt.value
                  ? 'text-white shadow-sm'
                  : 'text-gray-600 hover:bg-gray-200'
              }`}
              style={periodYears === opt.value ? { backgroundColor: color } : {}}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {historyLoading ? (
        <div className="bg-white rounded-lg border p-8 flex justify-center mb-6">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : chartData.length === 0 ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg mb-6">
          No yield history data available for {selectedTerm}
        </div>
      ) : (
        <div className="bg-white rounded-lg border p-4 mb-6">
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                <defs>
                  <linearGradient id="yieldGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={color} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={color} stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e8e8" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: '#666' }}
                  tickLine={{ stroke: '#e0e0e0' }}
                  axisLine={{ stroke: '#e0e0e0' }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  yAxisId="yield"
                  tick={{ fontSize: 11, fill: '#666' }}
                  tickLine={{ stroke: '#e0e0e0' }}
                  axisLine={{ stroke: '#e0e0e0' }}
                  tickFormatter={(v) => `${v.toFixed(2)}%`}
                  domain={['auto', 'auto']}
                />
                <YAxis
                  yAxisId="btc"
                  orientation="right"
                  tick={{ fontSize: 11, fill: '#666' }}
                  tickLine={{ stroke: '#e0e0e0' }}
                  axisLine={{ stroke: '#e0e0e0' }}
                  domain={[0, 'auto']}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(255,255,255,0.96)',
                    border: 'none',
                    borderRadius: 12,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                    padding: '12px 16px',
                  }}
                  formatter={(value, name) => {
                    if (name === 'yield') return [`${value?.toFixed(3)}%`, 'Yield'];
                    if (name === 'bidToCover') return [value?.toFixed(2), 'Bid-to-Cover'];
                    return [value, name];
                  }}
                />
                <Legend />
                <Area
                  yAxisId="yield"
                  type="monotone"
                  dataKey="yield"
                  stroke="transparent"
                  fill="url(#yieldGradient)"
                />
                <Line
                  yAxisId="yield"
                  type="monotone"
                  dataKey="yield"
                  name="Yield"
                  stroke={color}
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 6, fill: color, stroke: '#fff', strokeWidth: 3 }}
                />
                <Line
                  yAxisId="btc"
                  type="monotone"
                  dataKey="bidToCover"
                  name="Bid-to-Cover"
                  stroke="#888"
                  strokeWidth={1.5}
                  strokeDasharray="5 5"
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Upcoming Auctions */}
      {upcomingAuctions.length > 0 && (
        <>
          <h2 className="text-lg font-semibold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1 inline-block">
            Upcoming Auctions
          </h2>
          <div className="flex flex-wrap gap-2 mb-6">
            {upcomingAuctions.map((auction) => (
              <span
                key={auction.upcoming_id}
                className="px-3 py-1.5 rounded-full text-white text-sm font-medium"
                style={{ backgroundColor: TERM_COLORS[auction.security_term] || '#667eea' }}
              >
                {auction.security_term} - {auction.auction_date}
              </span>
            ))}
          </div>
          <hr className="my-6" />
        </>
      )}

      {/* Recent Auctions Table */}
      <h2 className="text-lg font-semibold text-blue-600 mb-3 border-b-2 border-blue-600 pb-1 inline-block">
        Recent {selectedTerm} Auctions
      </h2>

      {auctionsLoading ? (
        <div className="bg-white rounded-lg border p-8 flex justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : recentAuctions.length === 0 ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">
          No auction data available for {selectedTerm}
        </div>
      ) : (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">CUSIP</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">High Yield</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Coupon</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Bid-to-Cover</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Offering</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-700">Details</th>
              </tr>
            </thead>
            <tbody>
              {recentAuctions.map((auction, idx) => (
                <tr
                  key={auction.auction_id}
                  className={`border-t hover:bg-gray-50 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
                >
                  <td className="px-4 py-3 text-sm">{auction.auction_date}</td>
                  <td className="px-4 py-3 text-sm font-mono">{auction.cusip}</td>
                  <td className="px-4 py-3 text-sm font-mono text-right">{formatYield(auction.high_yield)}</td>
                  <td className="px-4 py-3 text-sm font-mono text-right">{formatYield(auction.coupon_rate)}</td>
                  <td className="px-4 py-3 text-sm font-mono text-right">
                    {auction.bid_to_cover_ratio?.toFixed(2) || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono text-right">{formatAmount(auction.offering_amount)}</td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => setSelectedAuction(auction)}
                      className="p-1.5 hover:bg-gray-200 rounded-full transition-colors"
                    >
                      <Info className="w-4 h-4 text-gray-600" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Auction Detail Modal */}
      {selectedAuction && (
        <AuctionDetailModal
          auction={selectedAuction}
          detail={auctionDetail}
          loading={detailLoading}
          onClose={() => {
            setSelectedAuction(null);
            setAuctionDetail(null);
          }}
        />
      )}
    </div>
  );
}
