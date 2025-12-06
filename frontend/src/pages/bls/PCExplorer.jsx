import { useState, useEffect, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Loader2, Factory, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';
import { pcResearchAPI } from '../../services/api';

/**
 * PC Explorer - Producer Price Index (Industry) Explorer
 *
 * PC survey measures producer prices organized by NAICS industry classification.
 * Note: For Final Demand PPI (headline numbers from press releases), see WP survey.
 *
 * Sections:
 * 1. PPI Overview - Summary of major NAICS sectors with MoM% and YoY% changes
 * 2. Sector Analysis - Detailed PPI by NAICS sector
 * 3. Industry Analysis - Detailed industry breakdown
 * 4. Product Analysis - Product-level prices within industries
 * 5. Top Movers - Biggest price gainers and losers
 * 6. Series Explorer - Search and chart specific series
 */

const CHART_COLORS = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'];

const timeRangeOptions = [
  { value: 12, label: 'Last 12 months' },
  { value: 24, label: 'Last 2 years' },
  { value: 60, label: 'Last 5 years' },
  { value: 120, label: 'Last 10 years' },
  { value: 240, label: 'Last 20 years' },
  { value: 0, label: 'All Time' },
];

// Helper functions
const formatIndex = (value) => {
  if (value === undefined || value === null) return 'N/A';
  return value.toFixed(1);
};

const formatChange = (value, suffix = '') => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}${suffix}`;
};

const formatPeriod = (periodCode) => {
  if (!periodCode) return '';
  const monthMap = {
    'M01': 'Jan', 'M02': 'Feb', 'M03': 'Mar', 'M04': 'Apr',
    'M05': 'May', 'M06': 'Jun', 'M07': 'Jul', 'M08': 'Aug',
    'M09': 'Sep', 'M10': 'Oct', 'M11': 'Nov', 'M12': 'Dec',
  };
  return monthMap[periodCode] || periodCode;
};

// Reusable Components
const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
    {children}
  </div>
);

const SectionHeader = ({ title, color = 'blue', icon: Icon }) => {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-50 text-blue-700',
    green: 'border-green-500 bg-green-50 text-green-700',
    orange: 'border-orange-500 bg-orange-50 text-orange-700',
    purple: 'border-purple-500 bg-purple-50 text-purple-700',
    cyan: 'border-cyan-500 bg-cyan-50 text-cyan-700',
    red: 'border-red-500 bg-red-50 text-red-700',
  };
  return (
    <div className={`px-5 py-3 border-b-4 ${colorClasses[color]} flex items-center gap-2`}>
      {Icon && <Icon className="w-5 h-5" />}
      <h2 className="text-xl font-bold">{title}</h2>
    </div>
  );
};

const Select = ({ label, value, onChange, options, className = '' }) => (
  <div className={className}>
    {label && <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>}
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  </div>
);

const ViewToggle = ({ value, onChange }) => (
  <div className="flex border border-gray-300 rounded-md overflow-hidden">
    <button
      onClick={() => onChange('table')}
      className={`px-3 py-1 text-sm ${value === 'table' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
    >
      Table
    </button>
    <button
      onClick={() => onChange('chart')}
      className={`px-3 py-1 text-sm ${value === 'chart' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
    >
      Chart
    </button>
  </div>
);

const TimelineSelector = ({ timeline, selectedIndex, onSelectIndex }) => {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="mt-4 mb-2 px-2">
      <p className="text-xs text-gray-500 mb-2">Select Month (click any point):</p>
      <div className="relative h-14">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-300" />
        <div className="relative flex justify-between">
          {timeline.map((point, index) => {
            const isSelected = selectedIndex === index;
            const isLatest = index === timeline.length - 1;
            const shouldShowLabel = index % Math.max(1, Math.floor(timeline.length / 8)) === 0 || index === timeline.length - 1;

            return (
              <div
                key={`${point.year}-${point.period}`}
                className="flex flex-col items-center cursor-pointer flex-1"
                onClick={() => onSelectIndex(index)}
              >
                <div
                  className={`rounded-full transition-all ${
                    isSelected
                      ? 'w-3.5 h-3.5 bg-blue-600 shadow-md'
                      : isLatest && selectedIndex === null
                      ? 'w-2.5 h-2.5 bg-blue-400'
                      : 'w-2.5 h-2.5 bg-gray-400 hover:bg-blue-400 hover:scale-110'
                  }`}
                />
                {(shouldShowLabel || isSelected) && (
                  <span className={`text-[10px] mt-1 ${isSelected ? 'text-blue-600 font-semibold' : 'text-gray-500'}`}>
                    {formatPeriod(point.period)} {point.year}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const ChangeIndicator = ({ value, suffix = '' }) => {
  if (value === undefined || value === null) {
    return <span className="text-gray-400 text-sm">N/A</span>;
  }
  const isPositive = value > 0;
  const isNegative = value < 0;
  const colorClass = isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500';
  const Icon = isPositive ? TrendingUp : isNegative ? TrendingDown : null;

  return (
    <span className={`flex items-center gap-1 text-sm font-medium ${colorClass}`}>
      {Icon && <Icon className="w-4 h-4" />}
      {formatChange(value, suffix)}
    </span>
  );
};

const LoadingSpinner = () => (
  <div className="flex justify-center items-center py-12">
    <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
  </div>
);

// Main Component
export default function PCExplorer() {
  // Dimensions
  const [dimensions, setDimensions] = useState(null);
  const [loadingDimensions, setLoadingDimensions] = useState(true);

  // Overview
  const [overview, setOverview] = useState(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [overviewTimeRange, setOverviewTimeRange] = useState(24);
  const [overviewTimeline, setOverviewTimeline] = useState(null);
  const [overviewSelectedIndex, setOverviewSelectedIndex] = useState(null);

  // Sectors
  const [sectors, setSectors] = useState(null);
  const [loadingSectors, setLoadingSectors] = useState(true);
  const [sectorTimeRange, setSectorTimeRange] = useState(24);
  const [sectorTimeline, setSectorTimeline] = useState(null);
  const [selectedSectors, setSelectedSectors] = useState([]);
  const [sectorSelectedIndex, setSectorSelectedIndex] = useState(null);

  // Industries
  const [industries, setIndustries] = useState(null);
  const [loadingIndustries, setLoadingIndustries] = useState(true);
  const [industrySector, setIndustrySector] = useState('');
  const [industryLimit, setIndustryLimit] = useState(20);
  const [industryTimeRange, setIndustryTimeRange] = useState(24);
  const [industryTimeline, setIndustryTimeline] = useState(null);
  const [industrySelectedIndex, setIndustrySelectedIndex] = useState(null);
  const [selectedIndustries, setSelectedIndustries] = useState([]);

  // Products
  const [products, setProducts] = useState(null);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [selectedProductIndustry, setSelectedProductIndustry] = useState('');
  const [productTimeRange, setProductTimeRange] = useState(24);
  const [productTimeline, setProductTimeline] = useState(null);
  const [productSelectedIndex, setProductSelectedIndex] = useState(null);
  const [selectedProducts, setSelectedProducts] = useState([]);

  // Top Movers
  const [topMovers, setTopMovers] = useState(null);
  const [loadingTopMovers, setLoadingTopMovers] = useState(true);
  const [moverPeriod, setMoverPeriod] = useState('mom');

  // Series Explorer - Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loadingSearch, setLoadingSearch] = useState(false);

  // Series Explorer - Hierarchical Drill-down
  const [drillSector, setDrillSector] = useState('');
  const [drillIndustry, setDrillIndustry] = useState('');
  const [drillProduct, setDrillProduct] = useState('');
  const [drillIndustryProducts, setDrillIndustryProducts] = useState([]);
  const [drillResults, setDrillResults] = useState(null);
  const [loadingDrill, setLoadingDrill] = useState(false);

  // Series Explorer - Paginated Browse
  const [browseIndustry, setBrowseIndustry] = useState('');
  const [browseSeasonal, setBrowseSeasonal] = useState('');
  const [browseBaseYear, setBrowseBaseYear] = useState('');
  const [browseMinStartYear, setBrowseMinStartYear] = useState('');
  const [browseLimit, setBrowseLimit] = useState(50);
  const [browseOffset, setBrowseOffset] = useState(0);
  const [browseResults, setBrowseResults] = useState(null);
  const [loadingBrowse, setLoadingBrowse] = useState(false);

  // Series Explorer - Shared
  const [selectedSeriesIds, setSelectedSeriesIds] = useState([]);
  const [seriesTimeRange, setSeriesTimeRange] = useState(24);
  const [seriesView, setSeriesView] = useState('chart');
  const [seriesChartData, setSeriesChartData] = useState({});
  const [allSeriesInfo, setAllSeriesInfo] = useState({});  // Cache for series metadata

  // Load dimensions on mount
  useEffect(() => {
    const load = async () => {
      try {
        const res = await pcResearchAPI.getDimensions();
        setDimensions(res.data);
        // Pre-select first 3 sectors if available (dimensions sectors use 'code')
        if (res.data?.sectors?.length > 0) {
          setSelectedSectors(res.data.sectors.slice(0, 3).map(s => s.code));
        }
      } catch (error) {
        console.error('Failed to load dimensions:', error);
      } finally {
        setLoadingDimensions(false);
      }
    };
    load();
  }, []);

  // Load overview
  useEffect(() => {
    const load = async () => {
      setLoadingOverview(true);
      try {
        const res = await pcResearchAPI.getOverview();
        setOverview(res.data);
      } catch (error) {
        console.error('Failed to load overview:', error);
      } finally {
        setLoadingOverview(false);
      }
    };
    load();
  }, []);

  // Load overview timeline
  useEffect(() => {
    const load = async () => {
      try {
        const res = await pcResearchAPI.getOverviewTimeline(overviewTimeRange);
        setOverviewTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setOverviewSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load overview timeline:', error);
      }
    };
    load();
  }, [overviewTimeRange]);

  // Load sectors
  useEffect(() => {
    const load = async () => {
      setLoadingSectors(true);
      try {
        const res = await pcResearchAPI.getSectors();
        setSectors(res.data);
      } catch (error) {
        console.error('Failed to load sectors:', error);
      } finally {
        setLoadingSectors(false);
      }
    };
    load();
  }, []);

  // Load sector timeline
  useEffect(() => {
    const load = async () => {
      if (selectedSectors.length === 0) return;
      try {
        const res = await pcResearchAPI.getSectorsTimeline(sectorTimeRange, selectedSectors.join(','));
        setSectorTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setSectorSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load sector timeline:', error);
      }
    };
    load();
  }, [selectedSectors, sectorTimeRange]);

  // Load industries
  useEffect(() => {
    const load = async () => {
      setLoadingIndustries(true);
      try {
        const res = await pcResearchAPI.getIndustries(industrySector || null, industryLimit);
        setIndustries(res.data);
        // Pre-select first 3 industries for timeline
        if (res.data?.industries?.length > 0 && selectedIndustries.length === 0) {
          setSelectedIndustries(res.data.industries.slice(0, 3).map(i => i.industry_code));
        }
      } catch (error) {
        console.error('Failed to load industries:', error);
      } finally {
        setLoadingIndustries(false);
      }
    };
    load();
  }, [industrySector, industryLimit]);

  // Load industry timeline
  useEffect(() => {
    const load = async () => {
      if (selectedIndustries.length === 0) return;
      try {
        const res = await pcResearchAPI.getIndustriesTimeline(selectedIndustries.join(','), industryTimeRange);
        setIndustryTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setIndustrySelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load industry timeline:', error);
      }
    };
    load();
  }, [selectedIndustries, industryTimeRange]);

  // Load products for selected industry
  useEffect(() => {
    const load = async () => {
      if (!selectedProductIndustry) {
        setProducts(null);
        return;
      }
      setLoadingProducts(true);
      try {
        const res = await pcResearchAPI.getProducts(selectedProductIndustry);
        setProducts(res.data);
        // Pre-select first 3 products
        if (res.data?.products?.length > 0) {
          setSelectedProducts(res.data.products.slice(0, 3).map(p => p.product_code));
        }
      } catch (error) {
        console.error('Failed to load products:', error);
      } finally {
        setLoadingProducts(false);
      }
    };
    load();
  }, [selectedProductIndustry]);

  // Load product timeline
  useEffect(() => {
    const load = async () => {
      if (!selectedProductIndustry || selectedProducts.length === 0) return;
      try {
        const res = await pcResearchAPI.getProductsTimeline(
          selectedProductIndustry,
          selectedProducts.join(','),
          productTimeRange
        );
        setProductTimeline(res.data);
        if (res.data?.timeline?.length > 0) {
          setProductSelectedIndex(res.data.timeline.length - 1);
        }
      } catch (error) {
        console.error('Failed to load product timeline:', error);
      }
    };
    load();
  }, [selectedProductIndustry, selectedProducts, productTimeRange]);

  // Load top movers
  useEffect(() => {
    const load = async () => {
      setLoadingTopMovers(true);
      try {
        const res = await pcResearchAPI.getTopMovers(moverPeriod, 10);
        setTopMovers(res.data);
      } catch (error) {
        console.error('Failed to load top movers:', error);
      } finally {
        setLoadingTopMovers(false);
      }
    };
    load();
  }, [moverPeriod]);

  // Load products for drill-down when industry is selected
  useEffect(() => {
    const load = async () => {
      if (!drillIndustry) {
        setDrillIndustryProducts([]);
        return;
      }
      try {
        const res = await pcResearchAPI.getProducts(drillIndustry);
        setDrillIndustryProducts(res.data?.products || []);
      } catch (error) {
        console.error('Failed to load products for drill-down:', error);
        setDrillIndustryProducts([]);
      }
    };
    load();
  }, [drillIndustry]);

  // Load paginated browse results
  useEffect(() => {
    const load = async () => {
      setLoadingBrowse(true);
      try {
        const params = { active_only: true, limit: browseLimit, offset: browseOffset };
        if (browseIndustry) params.industry_code = browseIndustry;
        if (browseSeasonal) params.seasonal_code = browseSeasonal;
        if (browseBaseYear) params.base_year = parseInt(browseBaseYear);
        if (browseMinStartYear) params.min_start_year = parseInt(browseMinStartYear);
        const res = await pcResearchAPI.getSeries(params);
        setBrowseResults(res.data);
        // Cache series info
        const newInfo = {};
        res.data?.series?.forEach(s => {
          newInfo[s.series_id] = s;
        });
        setAllSeriesInfo(prev => ({ ...prev, ...newInfo }));
      } catch (error) {
        console.error('Failed to load browse results:', error);
      } finally {
        setLoadingBrowse(false);
      }
    };
    load();
  }, [browseIndustry, browseSeasonal, browseBaseYear, browseMinStartYear, browseLimit, browseOffset]);

  // Load data for selected series
  useEffect(() => {
    const load = async () => {
      const newData = {};
      for (const seriesId of selectedSeriesIds) {
        if (!seriesChartData[seriesId]) {
          try {
            const res = await pcResearchAPI.getSeriesData(seriesId);
            newData[seriesId] = res.data;
          } catch (error) {
            console.error(`Failed to load series ${seriesId}:`, error);
          }
        }
      }
      if (Object.keys(newData).length > 0) {
        setSeriesChartData(prev => ({ ...prev, ...newData }));
      }
    };
    if (selectedSeriesIds.length > 0) {
      load();
    }
  }, [selectedSeriesIds]);

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoadingSearch(true);
    try {
      const res = await pcResearchAPI.getSeries({ search: searchQuery.trim(), limit: 100 });
      setSearchResults(res.data);
      // Cache series info for selected series chart labels
      const newInfo = {};
      res.data?.series?.forEach(s => {
        newInfo[s.series_id] = s;
      });
      setAllSeriesInfo(prev => ({ ...prev, ...newInfo }));
    } catch (error) {
      console.error('Failed to search series:', error);
    } finally {
      setLoadingSearch(false);
    }
  };

  // Drill-down handler
  const handleDrillDown = async () => {
    if (!drillSector) return;
    setLoadingDrill(true);
    try {
      const params = { limit: 200 };
      if (drillIndustry) {
        params.industry_code = drillIndustry;
        if (drillProduct) {
          params.product_code = drillProduct;
        }
      } else {
        params.sector_code = drillSector;
      }
      const res = await pcResearchAPI.getSeries(params);
      setDrillResults(res.data);
      // Cache series info
      const newInfo = {};
      res.data?.series?.forEach(s => {
        newInfo[s.series_id] = s;
      });
      setAllSeriesInfo(prev => ({ ...prev, ...newInfo }));
    } catch (error) {
      console.error('Failed to drill-down:', error);
    } finally {
      setLoadingDrill(false);
    }
  };

  // Toggle series selection (shared across all subsections)
  const toggleSeriesSelection = (seriesId) => {
    if (selectedSeriesIds.includes(seriesId)) {
      setSelectedSeriesIds(selectedSeriesIds.filter(id => id !== seriesId));
    } else if (selectedSeriesIds.length < 5) {
      setSelectedSeriesIds([...selectedSeriesIds, seriesId]);
      // Make sure we have the series info cached
      const allResults = [...(searchResults?.series || []), ...(drillResults?.series || []), ...(browseResults?.series || [])];
      const found = allResults.find(s => s.series_id === seriesId);
      if (found) {
        setAllSeriesInfo(prev => ({ ...prev, [seriesId]: found }));
      }
    }
  };

  const toggleSector = (code) => {
    setSelectedSectors(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : prev.length < 6 ? [...prev, code] : prev
    );
  };

  const toggleIndustry = (code) => {
    setSelectedIndustries(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : prev.length < 5 ? [...prev, code] : prev
    );
  };

  const toggleProduct = (code) => {
    setSelectedProducts(prev =>
      prev.includes(code)
        ? prev.filter(c => c !== code)
        : prev.length < 5 ? [...prev, code] : prev
    );
  };

  // Compute overview data for selected point (now sector-based)
  const overviewPointData = useMemo(() => {
    if (!overviewTimeline?.timeline || overviewSelectedIndex === null) return null;
    const timeline = overviewTimeline.timeline;
    const idx = overviewSelectedIndex;
    const current = timeline[idx];
    if (!current) return null;

    // Timeline now contains sectors with MoM % changes
    return {
      period_name: current.period_name,
      sectors: current.sectors || {}
    };
  }, [overviewTimeline, overviewSelectedIndex]);

  // Compute sector data for selected point
  const sectorPointData = useMemo(() => {
    if (!sectorTimeline?.timeline || sectorSelectedIndex === null) return null;
    const timeline = sectorTimeline.timeline;
    const idx = sectorSelectedIndex;
    const current = timeline[idx];
    if (!current) return null;

    const result = {};
    Object.keys(sectorTimeline.sector_names || {}).forEach(code => {
      const val = current.sectors?.[code];
      const prevMonth = idx > 0 ? timeline[idx - 1]?.sectors?.[code] : null;
      const prevYear = idx >= 12 ? timeline[idx - 12]?.sectors?.[code] : null;

      result[code] = {
        value: val,
        mom_change: prevMonth != null && val != null ? val - prevMonth : null,
        mom_pct: prevMonth != null && prevMonth !== 0 && val != null ? ((val - prevMonth) / prevMonth) * 100 : null,
        yoy_change: prevYear != null && val != null ? val - prevYear : null,
        yoy_pct: prevYear != null && prevYear !== 0 && val != null ? ((val - prevYear) / prevYear) * 100 : null,
      };
    });

    return { period_name: current.period_name, data: result };
  }, [sectorTimeline, sectorSelectedIndex]);

  // Compute industry data for selected point
  const industryPointData = useMemo(() => {
    if (!industryTimeline?.timeline || industrySelectedIndex === null) return null;
    const timeline = industryTimeline.timeline;
    const idx = industrySelectedIndex;
    const current = timeline[idx];
    if (!current) return null;

    const result = {};
    Object.keys(industryTimeline.industry_names || {}).forEach(code => {
      const val = current.industries?.[code];
      const prevMonth = idx > 0 ? timeline[idx - 1]?.industries?.[code] : null;
      const prevYear = idx >= 12 ? timeline[idx - 12]?.industries?.[code] : null;

      result[code] = {
        value: val,
        mom_change: prevMonth != null && val != null ? val - prevMonth : null,
        mom_pct: prevMonth != null && prevMonth !== 0 && val != null ? ((val - prevMonth) / prevMonth) * 100 : null,
        yoy_change: prevYear != null && val != null ? val - prevYear : null,
        yoy_pct: prevYear != null && prevYear !== 0 && val != null ? ((val - prevYear) / prevYear) * 100 : null,
      };
    });

    return { period_name: current.period_name, data: result };
  }, [industryTimeline, industrySelectedIndex]);

  // Compute product data for selected point
  const productPointData = useMemo(() => {
    if (!productTimeline?.timeline || productSelectedIndex === null) return null;
    const timeline = productTimeline.timeline;
    const idx = productSelectedIndex;
    const current = timeline[idx];
    if (!current) return null;

    const result = {};
    Object.keys(productTimeline.product_names || {}).forEach(code => {
      const val = current.products?.[code];
      const prevMonth = idx > 0 ? timeline[idx - 1]?.products?.[code] : null;
      const prevYear = idx >= 12 ? timeline[idx - 12]?.products?.[code] : null;

      result[code] = {
        value: val,
        mom_change: prevMonth != null && val != null ? val - prevMonth : null,
        mom_pct: prevMonth != null && prevMonth !== 0 && val != null ? ((val - prevMonth) / prevMonth) * 100 : null,
        yoy_change: prevYear != null && val != null ? val - prevYear : null,
        yoy_pct: prevYear != null && prevYear !== 0 && val != null ? ((val - prevYear) / prevYear) * 100 : null,
      };
    });

    return { period_name: current.period_name, data: result };
  }, [productTimeline, productSelectedIndex]);

  if (loadingDimensions) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">PC - Producer Price Index (Industry) Explorer</h1>
        <p className="text-sm text-gray-500">Explore producer prices by NAICS industry and product classification</p>
      </div>

      {/* Section 1: PPI Overview by NAICS Sector */}
      <Card>
        <SectionHeader title="Industry PPI Overview" color="blue" icon={Factory} />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-4">
            Producer prices by NAICS industry sector. For Final Demand PPI (headline numbers), see WP survey.
          </p>
          {loadingOverview ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Sector Cards - showing MoM% and YoY% prominently */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-6">
                {overview?.sectors?.map((sector) => (
                  <div key={sector.sector_code} className="p-3 rounded-lg border border-gray-200 bg-gray-50 hover:shadow-md transition-shadow">
                    <div className="flex items-start gap-2 mb-2">
                      <span className="px-1.5 py-0.5 text-[10px] font-mono font-bold bg-blue-100 text-blue-700 rounded shrink-0">
                        {sector.sector_code}
                      </span>
                      <p className="text-xs font-medium text-gray-600 line-clamp-2" title={sector.sector_name}>
                        {sector.sector_name}
                      </p>
                    </div>
                    <div className="space-y-1.5">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] text-gray-500">MoM</span>
                        <span className={`text-base font-bold ${
                          sector.mom_pct > 0 ? 'text-green-600' : sector.mom_pct < 0 ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          {sector.mom_pct != null ? `${sector.mom_pct >= 0 ? '+' : ''}${sector.mom_pct.toFixed(2)}%` : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] text-gray-500">YoY</span>
                        <span className={`text-sm font-semibold ${
                          sector.yoy_pct > 0 ? 'text-green-600' : sector.yoy_pct < 0 ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          {sector.yoy_pct != null ? `${sector.yoy_pct >= 0 ? '+' : ''}${sector.yoy_pct.toFixed(2)}%` : 'N/A'}
                        </span>
                      </div>
                    </div>
                    <p className="text-[9px] text-gray-400 mt-1.5 truncate">
                      {sector.latest_date} {sector.index_value && `• Idx: ${sector.index_value.toFixed(1)}`}
                    </p>
                  </div>
                ))}
              </div>

              {/* Timeline Chart - MoM % changes */}
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold text-gray-700">Monthly Price Changes by Sector (%)</h3>
                <Select
                  value={overviewTimeRange}
                  onChange={(v) => setOverviewTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
              </div>

              {overviewTimeline?.timeline?.length > 0 && (
                <>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={overviewTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis
                          tick={{ fontSize: 11 }}
                          domain={['auto', 'auto']}
                          tickFormatter={(v) => `${v}%`}
                        />
                        <Tooltip formatter={(value) => [value != null ? `${value.toFixed(2)}%` : 'N/A', '']} />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {Object.keys(overviewTimeline.sector_names || {}).slice(0, 6).map((code, idx) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`sectors.${code}`}
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            name={overviewTimeline.sector_names[code]}
                            strokeWidth={1.5}
                            dot={false}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <TimelineSelector
                    timeline={overviewTimeline.timeline}
                    selectedIndex={overviewSelectedIndex}
                    onSelectIndex={setOverviewSelectedIndex}
                  />
                </>
              )}

              {/* Summary table for all sectors */}
              {overview?.sectors?.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">All Sectors Summary</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3">Sector</th>
                          <th className="py-2 px-3 text-right">MoM %</th>
                          <th className="py-2 px-3 text-right">YoY %</th>
                          <th className="py-2 px-3 text-right text-gray-400">Index</th>
                        </tr>
                      </thead>
                      <tbody>
                        {overview.sectors.map((sector) => (
                          <tr key={sector.sector_code} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-2 px-3">
                              <span className="font-mono text-xs text-gray-400 mr-2">{sector.sector_code}</span>
                              {sector.sector_name}
                            </td>
                            <td className="py-2 px-3 text-right">
                              <ChangeIndicator value={sector.mom_pct} suffix="%" />
                            </td>
                            <td className="py-2 px-3 text-right">
                              <ChangeIndicator value={sector.yoy_pct} suffix="%" />
                            </td>
                            <td className="py-2 px-3 text-right text-gray-400">
                              {sector.index_value?.toFixed(1) || 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 2: Sector Analysis */}
      <Card>
        <SectionHeader title="Sector Analysis (NAICS)" color="green" icon={Factory} />
        <div className="p-5">
          {loadingSectors ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Horizontal Bar Chart - YoY % change */}
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Year-over-Year Price Change by Sector (%)</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={[...(sectors?.sectors || [])]
                      .filter(s => s.year_over_year_pct != null)
                      .sort((a, b) => (b.year_over_year_pct || 0) - (a.year_over_year_pct || 0))}
                    layout="vertical"
                    margin={{ left: 150 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis type="number" tick={{ fontSize: 11 }} domain={['auto', 'auto']} tickFormatter={(v) => `${v}%`} />
                    <YAxis type="category" dataKey="sector_name" tick={{ fontSize: 10 }} width={140} />
                    <Tooltip formatter={(value) => [`${value?.toFixed(2)}%`, 'YoY Change']} />
                    <Bar dataKey="year_over_year_pct">
                      {sectors?.sectors?.map((sector, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={(sector.year_over_year_pct || 0) >= 0 ? '#10b981' : '#ef4444'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Sector Table - % changes first */}
              <div className="flex justify-between items-center mt-6 mb-3">
                <h3 className="text-sm font-semibold text-gray-700">
                  Sector Details {sectorPointData && `- ${sectorPointData.period_name}`}
                </h3>
                <Select
                  value={sectorTimeRange}
                  onChange={(v) => setSectorTimeRange(parseInt(v))}
                  options={timeRangeOptions}
                  className="w-40"
                />
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                      <th className="py-2 px-3">Sector</th>
                      <th className="py-2 px-3 text-right">MoM %</th>
                      <th className="py-2 px-3 text-right">YoY %</th>
                      <th className="py-2 px-3 text-right text-gray-400">Index</th>
                      <th className="py-2 px-3 text-center">Compare</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sectors?.sectors?.map((sector) => {
                      const pointData = sectorPointData?.data?.[sector.sector_code];
                      return (
                        <tr key={sector.sector_code} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <span className="font-mono text-xs text-gray-400 mr-2">{sector.sector_code}</span>
                            {sector.sector_name}
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.mom_pct ?? sector.month_over_month_pct} suffix="%" />
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.yoy_pct ?? sector.year_over_year_pct} suffix="%" />
                          </td>
                          <td className="py-2 px-3 text-right text-gray-400">
                            {formatIndex(pointData?.value ?? sector.latest_value)}
                          </td>
                          <td className="py-2 px-3 text-center">
                            <button
                              onClick={() => toggleSector(sector.sector_code)}
                              className={`px-2 py-1 text-xs rounded ${
                                selectedSectors.includes(sector.sector_code)
                                  ? 'bg-green-500 text-white'
                                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                              }`}
                            >
                              {selectedSectors.includes(sector.sector_code) ? 'Selected' : 'Add'}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Sector Timeline */}
              {selectedSectors.length > 0 && sectorTimeline?.timeline?.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">Selected Sectors Timeline</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={sectorTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                        <Tooltip formatter={(value) => [value?.toFixed(1) || 'N/A', '']} />
                        <Legend />
                        {selectedSectors.map((code, index) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`sectors.${code}`}
                            stroke={CHART_COLORS[index % CHART_COLORS.length]}
                            name={sectorTimeline.sector_names?.[code] || code}
                            strokeWidth={2}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <TimelineSelector
                    timeline={sectorTimeline.timeline}
                    selectedIndex={sectorSelectedIndex}
                    onSelectIndex={setSectorSelectedIndex}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 3: Industry Analysis */}
      <Card>
        <SectionHeader title="Industry Analysis" color="orange" />
        <div className="p-5">
          {/* Filters */}
          <div className="flex gap-4 mb-4">
            <Select
              label="Sector"
              value={industrySector}
              onChange={setIndustrySector}
              options={[
                { value: '', label: 'All Sectors' },
                ...(dimensions?.sectors?.map(s => ({ value: s.code, label: `${s.code} - ${s.name}` })) || [])
              ]}
              className="w-64"
            />
            <Select
              label="Show"
              value={industryLimit}
              onChange={(v) => setIndustryLimit(parseInt(v))}
              options={[
                { value: 20, label: 'Top 20' },
                { value: 50, label: 'Top 50' },
                { value: 100, label: 'Top 100' },
              ]}
              className="w-32"
            />
            <Select
              label="Time Range"
              value={industryTimeRange}
              onChange={(v) => setIndustryTimeRange(parseInt(v))}
              options={timeRangeOptions}
              className="w-40"
            />
          </div>

          {loadingIndustries ? (
            <LoadingSpinner />
          ) : (
            <>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-gray-700">
                  Industry Details {industryPointData && `- ${industryPointData.period_name}`}
                </h3>
              </div>

              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white">
                    <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                      <th className="py-2 px-3 w-8">Chart</th>
                      <th className="py-2 px-3">Industry Code</th>
                      <th className="py-2 px-3">Industry Name</th>
                      <th className="py-2 px-3 text-right">MoM %</th>
                      <th className="py-2 px-3 text-right">YoY %</th>
                      <th className="py-2 px-3 text-right text-gray-400">Index</th>
                      <th className="py-2 px-3 text-center">Products</th>
                    </tr>
                  </thead>
                  <tbody>
                    {industries?.industries?.map((ind) => {
                      const pointData = industryPointData?.data?.[ind.industry_code];
                      return (
                        <tr key={ind.industry_code} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <input
                              type="checkbox"
                              checked={selectedIndustries.includes(ind.industry_code)}
                              onChange={() => toggleIndustry(ind.industry_code)}
                              disabled={!selectedIndustries.includes(ind.industry_code) && selectedIndustries.length >= 5}
                              className="rounded"
                            />
                          </td>
                          <td className="py-2 px-3 font-mono text-xs">{ind.industry_code}</td>
                          <td className="py-2 px-3">{ind.industry_name}</td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.mom_pct ?? ind.month_over_month_pct} suffix="%" />
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.yoy_pct ?? ind.year_over_year_pct} suffix="%" />
                          </td>
                          <td className="py-2 px-3 text-right text-gray-400">
                            {formatIndex(pointData?.value ?? ind.latest_value)}
                          </td>
                          <td className="py-2 px-3 text-center">
                            <button
                              onClick={() => setSelectedProductIndustry(ind.industry_code)}
                              className={`px-2 py-1 text-xs rounded ${
                                selectedProductIndustry === ind.industry_code
                                  ? 'bg-orange-500 text-white'
                                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                              }`}
                            >
                              View
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {industries && (
                <p className="text-xs text-gray-500 mt-2">
                  Showing {industries.industries?.length} of {industries.total_count} industries • Data as of {industries.last_updated}
                </p>
              )}

              {/* Industry Timeline Chart */}
              {selectedIndustries.length > 0 && industryTimeline?.timeline?.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">Selected Industries Timeline</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={industryTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                        <Tooltip formatter={(value) => [value?.toFixed(1) || 'N/A', '']} />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {selectedIndustries.map((code, index) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`industries.${code}`}
                            stroke={CHART_COLORS[index % CHART_COLORS.length]}
                            name={industryTimeline.industry_names?.[code] || code}
                            strokeWidth={2}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <TimelineSelector
                    timeline={industryTimeline.timeline}
                    selectedIndex={industrySelectedIndex}
                    onSelectIndex={setIndustrySelectedIndex}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 4: Product Analysis */}
      <Card>
        <SectionHeader title="Product Analysis" color="purple" />
        <div className="p-5">
          <div className="flex gap-4 mb-4">
            <Select
              label="Select Industry"
              value={selectedProductIndustry}
              onChange={(v) => {
                setSelectedProductIndustry(v);
                setSelectedProducts([]);
              }}
              options={[
                { value: '', label: 'Choose an industry...' },
                ...(industries?.industries?.map(i => ({
                  value: i.industry_code,
                  label: `${i.industry_code} - ${i.industry_name?.substring(0, 40)}...`
                })) || [])
              ]}
              className="w-96"
            />
            <Select
              label="Time Range"
              value={productTimeRange}
              onChange={(v) => setProductTimeRange(parseInt(v))}
              options={timeRangeOptions}
              className="w-40"
            />
          </div>

          {!selectedProductIndustry ? (
            <div className="text-center py-12 text-gray-500">
              <Factory className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Select an industry above to view its products</p>
            </div>
          ) : loadingProducts ? (
            <LoadingSpinner />
          ) : (
            <>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold text-gray-700">
                  Products for {products?.industry_name} {productPointData && `- ${productPointData.period_name}`}
                </h3>
              </div>

              <div className="overflow-x-auto max-h-80">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white">
                    <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                      <th className="py-2 px-3 w-8">Chart</th>
                      <th className="py-2 px-3">Product Code</th>
                      <th className="py-2 px-3">Product Name</th>
                      <th className="py-2 px-3 text-right">MoM %</th>
                      <th className="py-2 px-3 text-right">YoY %</th>
                      <th className="py-2 px-3 text-right text-gray-400">Index</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products?.products?.map((prod) => {
                      const pointData = productPointData?.data?.[prod.product_code];
                      return (
                        <tr key={prod.product_code} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <input
                              type="checkbox"
                              checked={selectedProducts.includes(prod.product_code)}
                              onChange={() => toggleProduct(prod.product_code)}
                              disabled={!selectedProducts.includes(prod.product_code) && selectedProducts.length >= 5}
                              className="rounded"
                            />
                          </td>
                          <td className="py-2 px-3 font-mono text-xs">{prod.product_code}</td>
                          <td className="py-2 px-3">{prod.product_name}</td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.mom_pct ?? prod.month_over_month_pct} suffix="%" />
                          </td>
                          <td className="py-2 px-3 text-right">
                            <ChangeIndicator value={pointData?.yoy_pct ?? prod.year_over_year_pct} suffix="%" />
                          </td>
                          <td className="py-2 px-3 text-right text-gray-400">
                            {formatIndex(pointData?.value ?? prod.latest_value)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {products && (
                <p className="text-xs text-gray-500 mt-2">
                  Showing {products.products?.length} of {products.total_count} products • Data as of {products.last_updated}
                </p>
              )}

              {/* Product Timeline Chart */}
              {selectedProducts.length > 0 && productTimeline?.timeline?.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-4">Selected Products Timeline</h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={productTimeline.timeline}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis dataKey="period_name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={70} />
                        <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                        <Tooltip formatter={(value) => [value?.toFixed(1) || 'N/A', '']} />
                        <Legend wrapperStyle={{ fontSize: '11px' }} />
                        {selectedProducts.map((code, index) => (
                          <Line
                            key={code}
                            type="monotone"
                            dataKey={`products.${code}`}
                            stroke={CHART_COLORS[index % CHART_COLORS.length]}
                            name={productTimeline.product_names?.[code] || code}
                            strokeWidth={2}
                            dot={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <TimelineSelector
                    timeline={productTimeline.timeline}
                    selectedIndex={productSelectedIndex}
                    onSelectIndex={setProductSelectedIndex}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </Card>

      {/* Section 5: Top Movers */}
      <Card>
        <SectionHeader title="Top Movers" color="red" />
        <div className="p-5">
          <div className="flex gap-4 mb-4">
            <Select
              label="Period"
              value={moverPeriod}
              onChange={setMoverPeriod}
              options={[
                { value: 'mom', label: 'Month over Month' },
                { value: 'yoy', label: 'Year over Year' },
              ]}
              className="w-48"
            />
          </div>

          {loadingTopMovers ? (
            <LoadingSpinner />
          ) : (
            <div className="grid grid-cols-2 gap-6">
              {/* Gainers */}
              <div>
                <h3 className="text-sm font-semibold text-green-700 mb-3 flex items-center gap-2">
                  <ArrowUpCircle className="w-5 h-5" />
                  Top Gainers
                </h3>
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 bg-green-50 text-left text-xs font-semibold text-gray-600 uppercase">
                        <th className="py-2 px-3">Industry/Product</th>
                        <th className="py-2 px-3 text-right">Index</th>
                        <th className="py-2 px-3 text-right">Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topMovers?.gainers?.map((mover, idx) => (
                        <tr key={`gainer-${idx}`} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <p className="font-medium text-sm">{mover.industry_name}</p>
                            {mover.product_name && (
                              <p className="text-xs text-gray-500">{mover.product_name}</p>
                            )}
                          </td>
                          <td className="py-2 px-3 text-right font-semibold">
                            {formatIndex(mover.latest_value)}
                          </td>
                          <td className="py-2 px-3 text-right">
                            <span className="text-green-600 font-semibold">
                              +{mover.change_pct?.toFixed(2)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                      {(!topMovers?.gainers || topMovers.gainers.length === 0) && (
                        <tr><td colSpan={3} className="py-4 text-center text-gray-500">No data available</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Losers */}
              <div>
                <h3 className="text-sm font-semibold text-red-700 mb-3 flex items-center gap-2">
                  <ArrowDownCircle className="w-5 h-5" />
                  Top Losers
                </h3>
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 bg-red-50 text-left text-xs font-semibold text-gray-600 uppercase">
                        <th className="py-2 px-3">Industry/Product</th>
                        <th className="py-2 px-3 text-right">Index</th>
                        <th className="py-2 px-3 text-right">Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topMovers?.losers?.map((mover, idx) => (
                        <tr key={`loser-${idx}`} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <p className="font-medium text-sm">{mover.industry_name}</p>
                            {mover.product_name && (
                              <p className="text-xs text-gray-500">{mover.product_name}</p>
                            )}
                          </td>
                          <td className="py-2 px-3 text-right font-semibold">
                            {formatIndex(mover.latest_value)}
                          </td>
                          <td className="py-2 px-3 text-right">
                            <span className="text-red-600 font-semibold">
                              {mover.change_pct?.toFixed(2)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                      {(!topMovers?.losers || topMovers.losers.length === 0) && (
                        <tr><td colSpan={3} className="py-4 text-center text-gray-500">No data available</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
          {topMovers?.last_updated && (
            <p className="text-xs text-gray-500 mt-4">Data as of {topMovers.last_updated}</p>
          )}
        </div>
      </Card>

      {/* Section 6: Series Explorer - Comprehensive Access */}
      <Card>
        <SectionHeader title="Series Explorer" color="cyan" />
        <div className="p-5">
          <p className="text-xs text-gray-500 mb-6">
            Access all PC series through search, hierarchical navigation, or paginated browsing.
            Select series to compare in charts (max 5).
          </p>

          {/* Sub-section 6A: Search-based Access */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-cyan-50 to-blue-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-cyan-800">Search Series</h3>
              <p className="text-xs text-gray-600">Find series by keyword in title, industry name, or product name</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4">
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Enter keyword (e.g., 'steel', 'petroleum', 'food manufacturing')..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || loadingSearch}
                  className="px-6 py-2 bg-cyan-600 text-white rounded-md hover:bg-cyan-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loadingSearch && <Loader2 className="w-4 h-4 animate-spin" />}
                  Search
                </button>
                {searchResults && (
                  <button
                    onClick={() => { setSearchResults(null); setSearchQuery(''); }}
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
                  >
                    Clear
                  </button>
                )}
              </div>

              {/* Search Results */}
              {searchResults && (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      Found {searchResults.total} series matching "{searchQuery}"
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-64">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Industry</th>
                          <th className="py-2 px-3">Product</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.series?.map((series) => (
                          <tr
                            key={series.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(series.series_id) ? 'bg-cyan-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(series.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(series.series_id)}
                                disabled={!selectedSeriesIds.includes(series.series_id) && selectedSeriesIds.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{series.series_id}</td>
                            <td className="py-2 px-3 text-xs">{series.industry_name || 'N/A'}</td>
                            <td className="py-2 px-3 text-xs">{series.product_name || '-'}</td>
                            <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {searchResults.total > searchResults.series.length && (
                    <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
                      Showing {searchResults.series.length} of {searchResults.total} results. Use more specific keywords or drill-down below for more results.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Sub-section 6B: Hierarchical Drill-down */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-green-800">Hierarchical Drill-down</h3>
              <p className="text-xs text-gray-600">Navigate: Sector → Industry → Product → Series</p>
            </div>
            <div className="p-4">
              <div className="grid grid-cols-4 gap-4 mb-4">
                <Select
                  label="1. Sector (NAICS)"
                  value={drillSector}
                  onChange={(v) => {
                    setDrillSector(v);
                    setDrillIndustry('');
                    setDrillProduct('');
                    setDrillResults(null);
                  }}
                  options={[
                    { value: '', label: 'Select sector...' },
                    ...(dimensions?.sectors?.map(s => ({
                      value: s.code,
                      label: `${s.code} - ${s.name}`
                    })) || [])
                  ]}
                />
                <Select
                  label="2. Industry"
                  value={drillIndustry}
                  onChange={(v) => {
                    setDrillIndustry(v);
                    setDrillProduct('');
                    setDrillResults(null);
                  }}
                  options={[
                    { value: '', label: drillSector ? 'Select industry...' : 'Select sector first' },
                    ...(drillSector ? (dimensions?.industries?.filter(i => i.sector === drillSector)?.map(i => ({
                      value: i.industry_code,
                      label: `${i.industry_code} - ${i.industry_name?.substring(0, 30)}`
                    })) || []) : [])
                  ]}
                />
                <Select
                  label="3. Product (optional)"
                  value={drillProduct}
                  onChange={(v) => {
                    setDrillProduct(v);
                    setDrillResults(null);
                  }}
                  options={[
                    { value: '', label: drillIndustry ? 'All products' : 'Select industry first' },
                    ...(drillIndustryProducts?.map(p => ({
                      value: p.product_code,
                      label: `${p.product_code} - ${p.product_name?.substring(0, 25)}`
                    })) || [])
                  ]}
                />
                <div className="flex items-end">
                  <button
                    onClick={handleDrillDown}
                    disabled={!drillSector || loadingDrill}
                    className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loadingDrill && <Loader2 className="w-4 h-4 animate-spin" />}
                    Find Series
                  </button>
                </div>
              </div>

              {/* Drill-down Results */}
              {drillResults && (
                <div className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      {drillResults.total} series in selected category
                    </span>
                  </div>
                  <div className="overflow-x-auto max-h-64">
                    <table className="w-full text-sm">
                      <thead className="sticky top-0 bg-gray-50">
                        <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                          <th className="py-2 px-3 w-8"></th>
                          <th className="py-2 px-3">Series ID</th>
                          <th className="py-2 px-3">Industry</th>
                          <th className="py-2 px-3">Product</th>
                          <th className="py-2 px-3">SA</th>
                          <th className="py-2 px-3">Period</th>
                        </tr>
                      </thead>
                      <tbody>
                        {drillResults.series?.map((series) => (
                          <tr
                            key={series.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(series.series_id) ? 'bg-green-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(series.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(series.series_id)}
                                disabled={!selectedSeriesIds.includes(series.series_id) && selectedSeriesIds.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{series.series_id}</td>
                            <td className="py-2 px-3 text-xs">{series.industry_name?.substring(0, 30) || 'N/A'}</td>
                            <td className="py-2 px-3 text-xs">{series.product_name?.substring(0, 25) || '-'}</td>
                            <td className="py-2 px-3">
                              <span className="px-1.5 py-0.5 text-xs bg-gray-100 rounded">
                                {series.seasonal_code === 'S' ? 'SA' : 'NSA'}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {drillResults.total > drillResults.series.length && (
                    <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
                      Showing {drillResults.series.length} of {drillResults.total} series. Narrow down with product filter or use Browse below.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Sub-section 6C: Paginated Browse */}
          <div className="mb-8 border border-gray-200 rounded-lg">
            <div className="px-4 py-3 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-200 rounded-t-lg">
              <h3 className="text-sm font-bold text-purple-800">Browse All Series</h3>
              <p className="text-xs text-gray-600">Paginated view of all available series with filters</p>
            </div>
            <div className="p-4">
              <div className="flex gap-4 mb-4 flex-wrap">
                <Select
                  label="Industry"
                  value={browseIndustry}
                  onChange={(v) => { setBrowseIndustry(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'All Industries' },
                    ...(dimensions?.industries?.slice(0, 100)?.map(i => ({
                      value: i.industry_code,
                      label: `${i.industry_code} - ${i.industry_name?.substring(0, 30)}`
                    })) || [])
                  ]}
                  className="w-64"
                />
                <Select
                  label="Seasonal"
                  value={browseSeasonal}
                  onChange={(v) => { setBrowseSeasonal(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'All' },
                    { value: 'S', label: 'Seasonally Adjusted' },
                    { value: 'U', label: 'Not Adjusted' },
                  ]}
                  className="w-40"
                />
                <Select
                  label="Base Year"
                  value={browseBaseYear}
                  onChange={(v) => { setBrowseBaseYear(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'Any' },
                    ...(dimensions?.base_years?.map(y => ({
                      value: y.toString(),
                      label: y.toString()
                    })) || [])
                  ]}
                  className="w-28"
                />
                <Select
                  label="Data Since"
                  value={browseMinStartYear}
                  onChange={(v) => { setBrowseMinStartYear(v); setBrowseOffset(0); }}
                  options={[
                    { value: '', label: 'Any' },
                    { value: '1980', label: '1980+' },
                    { value: '1990', label: '1990+' },
                    { value: '2000', label: '2000+' },
                    { value: '2010', label: '2010+' },
                    { value: '2020', label: '2020+' },
                  ]}
                  className="w-28"
                />
                <Select
                  label="Per Page"
                  value={browseLimit}
                  onChange={(v) => { setBrowseLimit(parseInt(v)); setBrowseOffset(0); }}
                  options={[
                    { value: 25, label: '25' },
                    { value: 50, label: '50' },
                    { value: 100, label: '100' },
                    { value: 200, label: '200' },
                  ]}
                  className="w-24"
                />
              </div>

              {/* Browse Results with Pagination */}
              <div className="border border-gray-200 rounded-lg">
                <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">
                    {browseResults ? `${browseResults.total.toLocaleString()} total series` : 'Loading...'}
                  </span>
                  {selectedSeriesIds.length > 0 && (
                    <button
                      onClick={() => setSelectedSeriesIds([])}
                      className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100"
                    >
                      Clear Selection ({selectedSeriesIds.length})
                    </button>
                  )}
                </div>
                <div className="overflow-x-auto max-h-80">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr className="border-b border-gray-200 text-left text-xs font-semibold text-gray-600 uppercase">
                        <th className="py-2 px-3 w-8"></th>
                        <th className="py-2 px-3">Series ID</th>
                        <th className="py-2 px-3">Industry</th>
                        <th className="py-2 px-3">Product</th>
                        <th className="py-2 px-3">SA</th>
                        <th className="py-2 px-3">Base</th>
                        <th className="py-2 px-3">Period</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loadingBrowse ? (
                        <tr><td colSpan={7} className="py-8 text-center"><Loader2 className="w-6 h-6 animate-spin mx-auto text-gray-400" /></td></tr>
                      ) : browseResults?.series?.length === 0 ? (
                        <tr><td colSpan={7} className="py-8 text-center text-gray-500">No series found.</td></tr>
                      ) : (
                        browseResults?.series?.map((series) => (
                          <tr
                            key={series.series_id}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedSeriesIds.includes(series.series_id) ? 'bg-purple-50' : 'hover:bg-gray-50'
                            }`}
                            onClick={() => toggleSeriesSelection(series.series_id)}
                          >
                            <td className="py-2 px-3">
                              <input
                                type="checkbox"
                                checked={selectedSeriesIds.includes(series.series_id)}
                                disabled={!selectedSeriesIds.includes(series.series_id) && selectedSeriesIds.length >= 5}
                                readOnly
                                className="rounded"
                              />
                            </td>
                            <td className="py-2 px-3 font-mono text-xs">{series.series_id}</td>
                            <td className="py-2 px-3 text-xs">{series.industry_name?.substring(0, 28) || 'N/A'}</td>
                            <td className="py-2 px-3 text-xs">{series.product_name?.substring(0, 22) || '-'}</td>
                            <td className="py-2 px-3">
                              <span className="px-1.5 py-0.5 text-xs bg-gray-100 rounded">
                                {series.seasonal_code === 'S' ? 'SA' : 'NSA'}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-xs text-gray-500">{series.base_date || '-'}</td>
                            <td className="py-2 px-3 text-xs">{series.begin_year} - {series.end_year || 'Present'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                {browseResults && browseResults.total > 0 && (
                  <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
                    <span className="text-sm text-gray-600">
                      Showing {browseOffset + 1} - {Math.min(browseOffset + browseLimit, browseResults.total)} of {browseResults.total.toLocaleString()}
                    </span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setBrowseOffset(0)}
                        disabled={browseOffset === 0}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        First
                      </button>
                      <button
                        onClick={() => setBrowseOffset(Math.max(0, browseOffset - browseLimit))}
                        disabled={browseOffset === 0}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      <span className="px-3 py-1 text-sm text-gray-600">
                        Page {Math.floor(browseOffset / browseLimit) + 1} of {Math.ceil(browseResults.total / browseLimit)}
                      </span>
                      <button
                        onClick={() => setBrowseOffset(browseOffset + browseLimit)}
                        disabled={browseOffset + browseLimit >= browseResults.total}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                      <button
                        onClick={() => setBrowseOffset(Math.floor((browseResults.total - 1) / browseLimit) * browseLimit)}
                        disabled={browseOffset + browseLimit >= browseResults.total}
                        className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Last
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Chart/Table for Selected Series */}
          {selectedSeriesIds.length > 0 && (
            <div className="border border-gray-200 rounded-lg">
              <div className="px-4 py-3 bg-gradient-to-r from-cyan-100 to-blue-100 border-b border-gray-200 flex justify-between items-center rounded-t-lg">
                <div>
                  <p className="text-sm font-bold text-cyan-800">
                    {seriesView === 'chart' ? 'Series Comparison Chart' : 'Series Data Table'}
                  </p>
                  <p className="text-xs text-gray-600">{selectedSeriesIds.length} series selected - click series above to add/remove</p>
                </div>
                <div className="flex gap-3 items-center">
                  <Select
                    value={seriesTimeRange}
                    onChange={(v) => setSeriesTimeRange(parseInt(v))}
                    options={timeRangeOptions}
                    className="w-36"
                  />
                  <ViewToggle value={seriesView} onChange={setSeriesView} />
                </div>
              </div>

              {seriesView === 'chart' ? (
                <div className="p-4 h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="period_name" type="category" allowDuplicatedCategory={false} tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={80} />
                      <YAxis tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      {selectedSeriesIds.map((seriesId, idx) => {
                        const chartData = seriesChartData[seriesId];
                        if (!chartData?.series?.[0]) return null;
                        const seriesInfo = allSeriesInfo[seriesId];
                        const label = seriesInfo
                          ? `${seriesInfo.industry_name?.substring(0, 20) || seriesId}`
                          : seriesId;
                        const filteredData = seriesTimeRange === 0
                          ? chartData.series[0].data_points
                          : chartData.series[0].data_points.slice(-seriesTimeRange);
                        return (
                          <Line
                            key={seriesId}
                            data={filteredData}
                            type="monotone"
                            dataKey="value"
                            stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                            strokeWidth={2}
                            dot={false}
                            name={label.length > 35 ? label.substring(0, 32) + '...' : label}
                          />
                        );
                      })}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-96">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-gray-50">
                      <tr className="border-b border-gray-200">
                        <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600">Period</th>
                        {selectedSeriesIds.map((seriesId) => {
                          const seriesInfo = allSeriesInfo[seriesId];
                          return (
                            <th key={seriesId} className="py-2 px-3 text-right text-xs font-semibold text-gray-600">
                              <div>{seriesInfo?.industry_name?.substring(0, 20) || seriesId}</div>
                              <div className="font-normal text-gray-400">{seriesInfo?.product_name?.substring(0, 15) || '-'}</div>
                            </th>
                          );
                        })}
                      </tr>
                    </thead>
                    <tbody>
                      {(() => {
                        const allPeriods = new Map();
                        selectedSeriesIds.forEach((seriesId) => {
                          const chartData = seriesChartData[seriesId];
                          if (!chartData?.series?.[0]) return;
                          const filteredData = seriesTimeRange === 0
                            ? chartData.series[0].data_points
                            : chartData.series[0].data_points.slice(-seriesTimeRange);
                          filteredData.forEach((dp) => {
                            const key = `${dp.year}-${dp.period}`;
                            if (!allPeriods.has(key)) {
                              allPeriods.set(key, { year: dp.year, period: dp.period, period_name: dp.period_name, values: {} });
                            }
                            allPeriods.get(key).values[seriesId] = dp.value;
                          });
                        });
                        const sortedPeriods = Array.from(allPeriods.values()).sort((a, b) => {
                          if (b.year !== a.year) return b.year - a.year;
                          return b.period.localeCompare(a.period);
                        });
                        return sortedPeriods.map((period) => (
                          <tr key={`${period.year}-${period.period}`} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-2 px-3 font-medium">{period.period_name}</td>
                            {selectedSeriesIds.map((seriesId) => (
                              <td key={seriesId} className="py-2 px-3 text-right">
                                {period.values[seriesId] != null ? period.values[seriesId].toFixed(1) : '-'}
                              </td>
                            ))}
                          </tr>
                        ));
                      })()}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
