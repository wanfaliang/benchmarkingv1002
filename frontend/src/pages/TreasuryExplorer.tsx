import { useState, useMemo, useEffect, ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { treasuryResearchAPI } from '../services/api';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowLeft,
  X,
  Loader2,
} from 'lucide-react';
import {
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

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

type TermType = '2-Year' | '5-Year' | '7-Year' | '10-Year' | '20-Year' | '30-Year';
type DirectionType = 'up' | 'down' | 'flat';

interface TermData {
  security_term: string;
  high_yield?: number | null;
  yield_change?: number | null;
  bid_to_cover_ratio?: number | null;
  auction_date?: string;
}

interface SnapshotData {
  data: TermData[];
}

interface YieldHistoryPoint {
  auction_date: string;
  high_yield?: number | null;
  bid_to_cover_ratio?: number | null;
  offering_amount?: number | null;
}

interface YieldHistoryData {
  data: YieldHistoryPoint[];
}

interface Auction {
  auction_id: number;
  security_term: string;
  auction_date: string;
  cusip?: string;
  high_yield?: number | null;
  coupon_rate?: number | null;
  bid_to_cover_ratio?: number | null;
  offering_amount?: number | null;
}

interface UpcomingAuction {
  upcoming_id: number;
  security_term: string;
  auction_date: string;
}

interface AuctionDetail {
  cusip?: string;
  security_type?: string;
  security_term?: string;
  issue_date?: string;
  maturity_date?: string;
  high_yield?: number | null;
  low_yield?: number | null;
  median_yield?: number | null;
  coupon_rate?: number | null;
  price_per_100?: number | null;
  offering_amount?: number | null;
  total_tendered?: number | null;
  total_accepted?: number | null;
  bid_to_cover_ratio?: number | null;
  primary_dealer_accepted?: number | null;
  direct_bidder_accepted?: number | null;
  indirect_bidder_accepted?: number | null;
}

interface ChartDataPoint {
  date: string;
  yield: number | null;
  bidToCover: number | null;
  amount: number | null;
}

interface PeriodOption {
  label: string;
  value: number;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const TERM_COLORS: Record<TermType, string> = {
  '2-Year': '#667eea',
  '5-Year': '#4facfe',
  '7-Year': '#43e97b',
  '10-Year': '#f5576c',
  '20-Year': '#fa709a',
  '30-Year': '#a18cd1',
};

const PERIOD_OPTIONS: PeriodOption[] = [
  { label: '1Y', value: 1 },
  { label: '5Y', value: 5 },
  { label: '10Y', value: 10 },
  { label: '20Y', value: 20 },
  { label: '30Y', value: 30 },
  { label: '50Y', value: 50 },
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const formatYield = (value: number | undefined | null): string => {
  if (value === null || value === undefined) return 'N/A';
  return `${value.toFixed(3)}%`;
};

const formatAmount = (value: number | undefined | null): string => {
  if (value === null || value === undefined) return 'N/A';
  return `$${(value / 1e9).toFixed(1)}B`;
};

// Get color for any term (handles reopenings like "9-Year 11-Month")
const getTermColor = (term: string): string => {
  if (TERM_COLORS[term as TermType]) return TERM_COLORS[term as TermType];
  if (term.includes('9-Year') || term.includes('10-Year')) return TERM_COLORS['10-Year'];
  if (term.includes('29-Year') || term.includes('30-Year')) return TERM_COLORS['30-Year'];
  if (term.includes('19-Year') || term.includes('20-Year')) return TERM_COLORS['20-Year'];
  if (term.includes('6-Year') || term.includes('7-Year')) return TERM_COLORS['7-Year'];
  if (term.includes('4-Year') || term.includes('5-Year')) return TERM_COLORS['5-Year'];
  if (term.includes('1-Year') || term.includes('2-Year')) return TERM_COLORS['2-Year'];
  return '#667eea';
};

// ============================================================================
// UPCOMING AUCTIONS TIMELINE COMPONENT
// ============================================================================

interface UpcomingAuctionsTimelineProps {
  auctions: UpcomingAuction[];
}

function UpcomingAuctionsTimeline({ auctions }: UpcomingAuctionsTimelineProps): ReactElement | null {
  if (!auctions || auctions.length === 0) return null;

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Filter to future auctions only
  const filteredAuctions = auctions
    .filter(a => {
      const auctionDate = new Date(a.auction_date);
      return auctionDate >= today;
    })
    .sort((a, b) => new Date(a.auction_date).getTime() - new Date(b.auction_date).getTime());

  if (filteredAuctions.length === 0) return null;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatWeekday = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  // Group auctions by date
  const auctionsByDate: Record<string, UpcomingAuction[]> = {};
  filteredAuctions.forEach(a => {
    if (!auctionsByDate[a.auction_date]) {
      auctionsByDate[a.auction_date] = [];
    }
    auctionsByDate[a.auction_date].push(a);
  });

  const uniqueDates = Object.keys(auctionsByDate).sort();
  const numDates = uniqueDates.length;

  // Evenly distribute positions across the timeline (10% to 90%)
  const getPositionPercent = (dateStr: string) => {
    const dateIndex = uniqueDates.indexOf(dateStr);
    if (numDates === 1) return 50;
    return 15 + (dateIndex / (numDates - 1)) * 70;
  };

  return (
    <div className="mb-6">
      <p className="text-sm text-gray-500 font-medium mb-2">Upcoming Auctions</p>

      <div className="relative h-20 bg-gray-50 rounded-lg border border-gray-200 px-4 py-2">
        {/* Timeline base line */}
        <div className="absolute top-1/2 left-6 right-6 h-0.5 bg-gray-300 -translate-y-1/2" />

        {/* Today marker */}
        <div className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col items-center">
          <div className="w-3 h-3 rounded-full bg-blue-600 border-2 border-white shadow" />
          <span className="mt-1 text-xs font-semibold text-blue-600">Today</span>
        </div>

        {/* Auction markers - evenly distributed */}
        {uniqueDates.map((dateStr) => {
          const dateAuctions = auctionsByDate[dateStr];
          const position = getPositionPercent(dateStr);
          return (
            <div
              key={dateStr}
              className="absolute top-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
              style={{ left: `${position}%` }}
            >
              {/* Stacked dots */}
              <div className="flex gap-0.5">
                {dateAuctions.map((auction, idx) => (
                  <div
                    key={idx}
                    className="w-3 h-3 rounded-full border-2 border-white shadow cursor-pointer hover:scale-125 transition-transform"
                    style={{ backgroundColor: getTermColor(auction.security_term) }}
                    title={`${auction.security_term} - ${formatDate(dateStr)}`}
                  />
                ))}
              </div>
              <div className="mt-1 text-center">
                <p className="text-[10px] text-gray-500 leading-none">{formatWeekday(dateStr)}</p>
                <p className="text-[11px] text-gray-700 font-medium leading-none">{formatDate(dateStr).split(' ')[1]}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-3 mt-2 flex-wrap">
        {filteredAuctions.map((auction, idx) => (
          <div key={idx} className="flex items-center gap-1">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: getTermColor(auction.security_term) }}
            />
            <span className="text-xs text-gray-500">
              {auction.security_term.replace('-Year', 'Y').replace(' Month', 'M').replace('-', '')} {formatDate(auction.auction_date)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// TERM CARD COMPONENT - Compact design
// ============================================================================

interface TermCardProps {
  term: TermType;
  data?: TermData | null;
  onClick: () => void;
  isSelected: boolean;
}

function TermCard({ term, data, onClick, isSelected }: TermCardProps): ReactElement {
  const color = TERM_COLORS[term] || '#667eea';
  const yieldChange = data?.yield_change;
  const direction: DirectionType =
    yieldChange === null || yieldChange === undefined
      ? 'flat'
      : yieldChange > 0.001
        ? 'up'
        : yieldChange < -0.001
          ? 'down'
          : 'flat';

  const TrendIcon = direction === 'up' ? TrendingUp : direction === 'down' ? TrendingDown : Minus;
  const hasValidData = data && data.high_yield !== null && data.high_yield !== undefined;

  return (
    <div
      onClick={onClick}
      className={`cursor-pointer min-w-[130px] flex-1 max-w-[160px] p-3 rounded-lg border transition-all duration-150 hover:bg-gray-50 ${
        isSelected ? 'bg-gray-100 border-gray-400' : 'bg-white border-gray-200'
      }`}
    >
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-semibold text-gray-900">{term}</span>
        <div
          className={`w-2 h-2 rounded-full ${isSelected ? 'opacity-100' : 'opacity-50'}`}
          style={{ backgroundColor: color }}
        />
      </div>

      {hasValidData ? (
        <>
          <p className="text-xl font-bold text-gray-900 leading-tight">
            {formatYield(data.high_yield)}
          </p>

          <div className="flex items-center justify-between mt-1">
            {yieldChange !== null && yieldChange !== undefined ? (
              <div className="flex items-center gap-0.5">
                <TrendIcon
                  className={`w-3.5 h-3.5 ${
                    direction === 'up'
                      ? 'text-red-500'
                      : direction === 'down'
                        ? 'text-green-500'
                        : 'text-gray-400'
                  }`}
                />
                <span
                  className={`text-xs font-medium ${
                    direction === 'up'
                      ? 'text-red-500'
                      : direction === 'down'
                        ? 'text-green-500'
                        : 'text-gray-400'
                  }`}
                >
                  {yieldChange > 0 ? '+' : ''}{(yieldChange * 100).toFixed(0)}bp
                </span>
              </div>
            ) : (
              <div />
            )}
            <span className="text-xs text-gray-400">{data.auction_date?.slice(5) || ''}</span>
          </div>
        </>
      ) : (
        <p className="text-xs text-gray-400">No data</p>
      )}
    </div>
  );
}

// ============================================================================
// AUCTION EVENT CARD - Compact narrative style
// ============================================================================

interface AuctionEventCardProps {
  auction: Auction;
  previousAuction?: Auction;
  onClick: () => void;
}

function AuctionEventCard({ auction, previousAuction, onClick }: AuctionEventCardProps): ReactElement {
  const color = getTermColor(auction.security_term);

  // Calculate metrics
  const yieldChange = previousAuction?.high_yield && auction.high_yield
    ? auction.high_yield - previousAuction.high_yield
    : null;

  const bidToCover = auction.bid_to_cover_ratio;
  const demandRating = bidToCover && bidToCover >= 2.5 ? 'strong' : bidToCover && bidToCover >= 2.0 ? 'average' : bidToCover ? 'weak' : null;

  // Generate narrative
  const getNarrative = () => {
    if (!auction.high_yield) return 'Scheduled';

    const parts: string[] = [];

    if (demandRating === 'strong') {
      parts.push('Strong demand');
    } else if (demandRating === 'weak') {
      parts.push('Tepid demand');
    }

    if (yieldChange !== null) {
      if (Math.abs(yieldChange) < 0.01) {
        parts.push('yields steady');
      } else if (yieldChange > 0.05) {
        parts.push('yields jumped');
      } else if (yieldChange > 0) {
        parts.push('yields up');
      } else if (yieldChange < -0.05) {
        parts.push('yields dropped');
      } else {
        parts.push('yields down');
      }
    }

    return parts.length === 0 ? `${auction.high_yield?.toFixed(3)}%` : parts.join(', ');
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div
      onClick={onClick}
      className="p-3 rounded-lg border border-gray-200 bg-white h-full cursor-pointer hover:border-gray-300 hover:bg-gray-50 transition-all"
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-2">
        <div className="min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
            <span className="text-sm font-bold truncate">{auction.security_term}</span>
            {demandRating && (
              <span
                className={`h-4 min-w-4 px-1 text-[10px] font-bold rounded flex items-center justify-center ${
                  demandRating === 'strong'
                    ? 'bg-green-100 text-green-700'
                    : demandRating === 'weak'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-gray-200 text-gray-600'
                }`}
              >
                {demandRating === 'strong' ? '↑' : demandRating === 'weak' ? '↓' : '–'}
              </span>
            )}
          </div>
          <p className="text-[11px] text-gray-500">{formatDate(auction.auction_date)}</p>
        </div>

        {/* Yield display */}
        <div className="text-right flex-shrink-0">
          <p className="text-base font-bold leading-none">
            {auction.high_yield ? `${auction.high_yield.toFixed(3)}%` : '—'}
          </p>
          {yieldChange !== null && (
            <div className="flex items-center justify-end gap-0.5">
              {yieldChange > 0 ? (
                <TrendingUp className="w-3 h-3 text-red-500" />
              ) : yieldChange < 0 ? (
                <TrendingDown className="w-3 h-3 text-green-500" />
              ) : (
                <Minus className="w-3 h-3 text-gray-400" />
              )}
              <span
                className={`text-[10px] font-medium ${
                  yieldChange > 0 ? 'text-red-500' : yieldChange < 0 ? 'text-green-500' : 'text-gray-400'
                }`}
              >
                {yieldChange > 0 ? '+' : ''}{(yieldChange * 100).toFixed(0)}bp
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Narrative */}
      <p className="text-xs text-gray-500 italic mb-2">{getNarrative()}</p>

      {/* Metrics row */}
      <div className="flex gap-3 flex-wrap text-xs text-gray-500">
        <span><strong>B/C:</strong> {bidToCover ? bidToCover.toFixed(2) : '—'}</span>
        <span><strong>Cpn:</strong> {auction.coupon_rate ? `${auction.coupon_rate.toFixed(2)}%` : '—'}</span>
        <span><strong>Size:</strong> {auction.offering_amount ? `$${(auction.offering_amount / 1e9).toFixed(0)}B` : '—'}</span>
      </div>
    </div>
  );
}

// ============================================================================
// AUCTION DETAIL MODAL COMPONENT
// ============================================================================

interface AuctionDetailModalProps {
  auction: Auction | null;
  detail: AuctionDetail | null;
  loading: boolean;
  onClose: () => void;
}

function AuctionDetailModal({ auction, detail, loading, onClose }: AuctionDetailModalProps): ReactElement | null {
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

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function TreasuryExplorer(): ReactElement {
  const [selectedTerm, setSelectedTerm] = useState<TermType>('10-Year');
  const [periodYears, setPeriodYears] = useState(5);
  const [selectedAuction, setSelectedAuction] = useState<Auction | null>(null);
  const [showHistoryTable, setShowHistoryTable] = useState(false);

  // Data states
  const [snapshot, setSnapshot] = useState<SnapshotData | null>(null);
  const [snapshotLoading, setSnapshotLoading] = useState(true);
  const [yieldHistory, setYieldHistory] = useState<YieldHistoryData | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [recentAuctions, setRecentAuctions] = useState<Auction[]>([]);
  const [auctionsLoading, setAuctionsLoading] = useState(false);
  const [upcomingAuctions, setUpcomingAuctions] = useState<UpcomingAuction[]>([]);
  const [auctionDetail, setAuctionDetail] = useState<AuctionDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Fetch snapshot
  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        setSnapshotLoading(true);
        const response = await treasuryResearchAPI.getSnapshot();
        setSnapshot(response.data as SnapshotData);
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
        setUpcomingAuctions(response.data as UpcomingAuction[]);
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
        setYieldHistory(response.data as YieldHistoryData);
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
        setRecentAuctions(response.data as Auction[]);
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
        setAuctionDetail(response.data as AuctionDetail);
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
  const snapshotMap = useMemo((): Record<string, TermData> => {
    if (!snapshot?.data) return {};
    return Object.fromEntries(snapshot.data.map((d) => [d.security_term, d]));
  }, [snapshot]);

  // Chart data
  const chartData = useMemo((): ChartDataPoint[] => {
    if (!yieldHistory?.data) return [];
    return yieldHistory.data.map((d) => ({
      date: d.auction_date,
      yield: d.high_yield ?? null,
      bidToCover: d.bid_to_cover_ratio ?? null,
      amount: d.offering_amount ? d.offering_amount / 1e9 : null,
    }));
  }, [yieldHistory]);

  const color = TERM_COLORS[selectedTerm] || '#667eea';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-2">
        <Link
          to="/research"
          className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Treasury Auction Explorer</h1>
      </div>
      <p className="text-gray-600 mb-6 ml-12">
        Explore U.S. Treasury Notes & Bonds auction history and yields
      </p>

      {/* Upcoming Auctions Timeline */}
      <UpcomingAuctionsTimeline auctions={upcomingAuctions} />

      {/* Term Filter Cards */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-sm text-gray-500 font-medium">Select Maturity:</span>
          <span className="text-xs text-gray-400">(click to filter chart and table below)</span>
        </div>

        {snapshotLoading ? (
          <div className="flex justify-center py-4">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          </div>
        ) : (
          <div className="flex gap-3 flex-wrap">
            {(['2-Year', '5-Year', '7-Year', '10-Year', '20-Year', '30-Year'] as TermType[]).map((term) => (
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
      </div>

      <hr className="my-6" />

      {/* Yield History Section */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-4">
        <h2 className="text-lg font-semibold text-blue-600 border-b-2 border-blue-600 pb-1">
          {selectedTerm} Yield History
        </h2>

        <div className="flex items-center gap-2">
          {/* Period Toggle */}
          <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
            {PERIOD_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setPeriodYears(opt.value)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
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

          <div className="w-px h-6 bg-gray-300 mx-1" />

          {/* Chart/Table Toggle */}
          <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setShowHistoryTable(false)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                !showHistoryTable ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:bg-gray-200'
              }`}
            >
              Chart
            </button>
            <button
              onClick={() => setShowHistoryTable(true)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                showHistoryTable ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:bg-gray-200'
              }`}
            >
              Data Table
            </button>
          </div>
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
      ) : showHistoryTable ? (
        /* Data Table View */
        <div className="bg-white rounded-lg border mb-6 overflow-hidden">
          <div className="max-h-96 overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0">
                <tr className="bg-gray-100">
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">Date</th>
                  <th className="px-4 py-3 text-right font-semibold text-gray-700">High Yield</th>
                  <th className="px-4 py-3 text-right font-semibold text-gray-700">Bid-to-Cover</th>
                  <th className="px-4 py-3 text-right font-semibold text-gray-700">Offering ($B)</th>
                </tr>
              </thead>
              <tbody>
                {[...chartData].reverse().map((row, idx) => (
                  <tr key={idx} className={`border-t hover:bg-gray-50 ${idx % 2 === 0 ? '' : 'bg-gray-50'}`}>
                    <td className="px-4 py-2">{row.date}</td>
                    <td className="px-4 py-2 text-right font-mono">{row.yield ? `${row.yield.toFixed(3)}%` : '—'}</td>
                    <td className="px-4 py-2 text-right font-mono">{row.bidToCover ? row.bidToCover.toFixed(2) : '—'}</td>
                    <td className="px-4 py-2 text-right font-mono">{row.amount ? `$${row.amount.toFixed(1)}B` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="p-2 border-t bg-gray-50">
            <span className="text-xs text-gray-500">
              {chartData.length} records • {selectedTerm} • Last {periodYears} years
            </span>
          </div>
        </div>
      ) : (
        /* Chart View */
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
                  tickFormatter={(v) => `${(v as number).toFixed(2)}%`}
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
                    if (name === 'yield') return [`${(value as number)?.toFixed(3)}%`, 'Yield'];
                    if (name === 'bidToCover') return [(value as number)?.toFixed(2), 'Bid-to-Cover'];
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

      {/* Recent Auctions - Card Style */}
      <div className="mb-3">
        <h2 className="text-lg font-semibold text-blue-600 border-b-2 border-blue-600 pb-1 inline-block">
          Recent {selectedTerm} Auctions
        </h2>
        <p className="text-sm text-gray-500 mt-1">Includes reopenings and related maturities</p>
      </div>

      {auctionsLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : recentAuctions.length === 0 ? (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-lg">
          No auction data available for {selectedTerm}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentAuctions.map((auction, idx) => (
            <AuctionEventCard
              key={auction.auction_id}
              auction={auction}
              previousAuction={idx < recentAuctions.length - 1 ? recentAuctions[idx + 1] : undefined}
              onClick={() => setSelectedAuction(auction)}
            />
          ))}
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
