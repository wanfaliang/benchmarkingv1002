import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Globe,
  Building2,
  LineChart,
  PieChart,
  Activity,
  DollarSign,
  Clock,
  Lock,
  Sparkles,
  Database,
  ArrowRight,
  CheckCircle2,
  Users,
  ShoppingCart,
  Briefcase,
  Target,
  Zap,
} from 'lucide-react';

interface PlaceholderSectionProps {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  features: string[];
  previewMetrics: Array<{
    label: string;
    value: string;
    change?: number;
    icon: React.ReactNode;
  }>;
  datasets: Array<{
    name: string;
    description: string;
    frequency: string;
  }>;
}

function PlaceholderSection({
  title,
  subtitle,
  icon,
  color,
  features,
  previewMetrics,
  datasets,
}: PlaceholderSectionProps) {
  const colorClasses: Record<string, { gradient: string; border: string; text: string; bg: string; light: string }> = {
    purple: {
      gradient: 'from-purple-600 to-indigo-600',
      border: 'border-purple-200',
      text: 'text-purple-600',
      bg: 'bg-purple-100',
      light: 'bg-purple-50',
    },
    orange: {
      gradient: 'from-orange-500 to-amber-500',
      border: 'border-orange-200',
      text: 'text-orange-600',
      bg: 'bg-orange-100',
      light: 'bg-orange-50',
    },
    cyan: {
      gradient: 'from-cyan-600 to-blue-600',
      border: 'border-cyan-200',
      text: 'text-cyan-600',
      bg: 'bg-cyan-100',
      light: 'bg-cyan-50',
    },
    rose: {
      gradient: 'from-rose-500 to-pink-500',
      border: 'border-rose-200',
      text: 'text-rose-600',
      bg: 'bg-rose-100',
      light: 'bg-rose-50',
    },
    indigo: {
      gradient: 'from-indigo-600 to-violet-600',
      border: 'border-indigo-200',
      text: 'text-indigo-600',
      bg: 'bg-indigo-100',
      light: 'bg-indigo-50',
    },
  };

  const colors = colorClasses[color] || colorClasses.purple;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`bg-gradient-to-r ${colors.gradient} rounded-xl p-6 text-white relative overflow-hidden`}>
        <div className="absolute right-0 top-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="relative flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center">
              {icon}
              <span className="ml-3">{title}</span>
            </h2>
            <p className="text-white/80 mt-1">{subtitle}</p>
          </div>
          <div className="flex items-center bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2">
            <Clock className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Coming Soon</span>
          </div>
        </div>
      </div>

      {/* Preview Content */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {/* Preview Banner */}
        <div className={`${colors.light} border-b ${colors.border} px-6 py-4`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Sparkles className={`w-5 h-5 ${colors.text} mr-2`} />
              <span className="font-medium text-gray-900">Preview of Available Data</span>
            </div>
            <span className="text-xs text-gray-500">Data shown for illustration purposes</span>
          </div>
        </div>

        <div className="p-6 space-y-8">
          {/* Preview Metrics */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Key Indicators</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {previewMetrics.map((metric, idx) => (
                <div
                  key={idx}
                  className="bg-gray-50 rounded-lg p-4 border border-gray-100 relative group hover:border-gray-200 transition-colors"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-100/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-lg" />
                  <div className="relative">
                    <div className="flex items-center text-gray-400 mb-2">
                      {metric.icon}
                      <span className="ml-2 text-xs uppercase tracking-wide">{metric.label}</span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{metric.value}</div>
                    {metric.change !== undefined && (
                      <div className={`flex items-center mt-1 text-xs ${metric.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {metric.change >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                        {metric.change >= 0 ? '+' : ''}{metric.change}%
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Features List */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {features.map((feature, idx) => (
                <div key={idx} className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <CheckCircle2 className={`w-5 h-5 ${colors.text} mr-3 flex-shrink-0`} />
                  <span className="text-sm text-gray-700">{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Available Datasets */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">Available Datasets</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {datasets.map((dataset, idx) => (
                <div
                  key={idx}
                  className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <Database className="w-4 h-4 text-gray-400" />
                    <span className={`text-xs ${colors.bg} ${colors.text} px-2 py-0.5 rounded`}>
                      {dataset.frequency}
                    </span>
                  </div>
                  <h4 className="font-medium text-gray-900 text-sm">{dataset.name}</h4>
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">{dataset.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Coming Soon Notice */}
          <div className={`${colors.light} border ${colors.border} rounded-lg p-6 text-center`}>
            <Lock className={`w-8 h-8 ${colors.text} mx-auto mb-3`} />
            <h3 className="text-lg font-semibold text-gray-900">Full Access Coming Soon</h3>
            <p className="text-sm text-gray-600 mt-2 max-w-md mx-auto">
              This data source is currently under development. Subscribe to updates to be notified when it becomes available.
            </p>
            <button className={`mt-4 px-6 py-2 bg-gradient-to-r ${colors.gradient} text-white rounded-lg font-medium text-sm hover:opacity-90 transition-opacity inline-flex items-center`}>
              Notify Me
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// BEA Section
export function BEASection() {
  return (
    <PlaceholderSection
      title="Bureau of Economic Analysis"
      subtitle="GDP, personal income, international trade, and regional economic data"
      icon={<Globe className="w-7 h-7" />}
      color="purple"
      features={[
        "Gross Domestic Product (GDP) releases",
        "Personal Income and Outlays",
        "International Trade in Goods and Services",
        "Regional Economic Accounts",
        "Industry Economic Accounts",
        "National Income and Product Accounts (NIPA)",
        "Fixed Assets and Consumer Durables",
        "Input-Output Accounts",
      ]}
      previewMetrics={[
        { label: "Real GDP Growth", value: "2.8%", change: 0.3, icon: <BarChart3 className="w-4 h-4" /> },
        { label: "Personal Income", value: "+0.4%", change: 0.1, icon: <DollarSign className="w-4 h-4" /> },
        { label: "PCE Inflation", value: "2.5%", change: -0.2, icon: <Activity className="w-4 h-4" /> },
        { label: "Trade Deficit", value: "$68.9B", change: -3.1, icon: <Globe className="w-4 h-4" /> },
      ]}
      datasets={[
        { name: "GDP and Components", description: "Quarterly and annual GDP estimates with detailed components", frequency: "Quarterly" },
        { name: "Personal Income by State", description: "State-level personal income and per capita income", frequency: "Quarterly" },
        { name: "Trade in Goods", description: "Monthly international trade statistics", frequency: "Monthly" },
        { name: "PCE Price Index", description: "Personal consumption expenditure price indexes", frequency: "Monthly" },
        { name: "GDP by Industry", description: "Value added and gross output by industry", frequency: "Annual" },
        { name: "Regional GDP", description: "Real GDP by state and metropolitan area", frequency: "Annual" },
      ]}
    />
  );
}

// FRED Section
export function FREDSection() {
  return (
    <PlaceholderSection
      title="Federal Reserve Economic Data"
      subtitle="800,000+ economic time series from 100+ sources"
      icon={<LineChart className="w-7 h-7" />}
      color="orange"
      features={[
        "Real-time economic data updates",
        "Federal Reserve monetary policy data",
        "Interest rates and yield curves",
        "Money supply and banking statistics",
        "Housing and real estate indicators",
        "International economic comparisons",
        "State and regional economic data",
        "Custom chart builder and downloads",
      ]}
      previewMetrics={[
        { label: "Fed Funds Rate", value: "5.33%", change: 0, icon: <Target className="w-4 h-4" /> },
        { label: "M2 Money Supply", value: "$21.0T", change: -2.1, icon: <DollarSign className="w-4 h-4" /> },
        { label: "30Y Mortgage", value: "6.89%", change: 0.12, icon: <Building2 className="w-4 h-4" /> },
        { label: "S&P/CS HPI", value: "310.2", change: 4.5, icon: <TrendingUp className="w-4 h-4" /> },
      ]}
      datasets={[
        { name: "Federal Reserve Data", description: "Fed Funds, discount rates, reserve balances", frequency: "Daily" },
        { name: "Treasury Rates", description: "Full yield curve from 1M to 30Y", frequency: "Daily" },
        { name: "Money Supply", description: "M1, M2, and monetary base aggregates", frequency: "Weekly" },
        { name: "Bank Credit", description: "Commercial bank loans and investments", frequency: "Weekly" },
        { name: "Housing Starts", description: "New residential construction data", frequency: "Monthly" },
        { name: "Industrial Production", description: "Manufacturing and mining output", frequency: "Monthly" },
      ]}
    />
  );
}

// Markets Section
export function MarketsSection() {
  return (
    <PlaceholderSection
      title="Financial Markets Data"
      subtitle="Real-time and historical market data across asset classes"
      icon={<Activity className="w-7 h-7" />}
      color="cyan"
      features={[
        "Equity indices and sector performance",
        "Fixed income and credit markets",
        "Foreign exchange rates",
        "Commodity prices and futures",
        "Volatility indices (VIX, MOVE)",
        "ETF flows and holdings",
        "Market breadth indicators",
        "Cross-asset correlations",
      ]}
      previewMetrics={[
        { label: "S&P 500", value: "5,088.80", change: 1.2, icon: <TrendingUp className="w-4 h-4" /> },
        { label: "VIX", value: "14.52", change: -8.3, icon: <Activity className="w-4 h-4" /> },
        { label: "DXY Index", value: "104.23", change: 0.5, icon: <DollarSign className="w-4 h-4" /> },
        { label: "Gold", value: "$2,024", change: 2.1, icon: <Sparkles className="w-4 h-4" /> },
      ]}
      datasets={[
        { name: "US Equity Indices", description: "S&P 500, Dow, Nasdaq, Russell indices", frequency: "Real-time" },
        { name: "Sector ETFs", description: "XLF, XLK, XLE and other sector performance", frequency: "Real-time" },
        { name: "Credit Spreads", description: "Investment grade and high yield spreads", frequency: "Daily" },
        { name: "Currency Pairs", description: "Major and emerging market FX rates", frequency: "Real-time" },
        { name: "Commodities", description: "Energy, metals, agriculture futures", frequency: "Real-time" },
        { name: "Market Sentiment", description: "Put/call ratios, fund flows, positioning", frequency: "Daily" },
      ]}
    />
  );
}

// Options Section
export function OptionsSection() {
  return (
    <PlaceholderSection
      title="Options Analytics"
      subtitle="Comprehensive options data and volatility analysis"
      icon={<PieChart className="w-7 h-7" />}
      color="rose"
      features={[
        "Options chain visualization",
        "Implied volatility surfaces",
        "Greeks calculation and analysis",
        "Options flow and unusual activity",
        "Volatility skew analysis",
        "Historical volatility comparison",
        "Options strategy builder",
        "Earnings volatility analysis",
      ]}
      previewMetrics={[
        { label: "SPY IV30", value: "14.2%", change: -5.2, icon: <Activity className="w-4 h-4" /> },
        { label: "Put/Call Ratio", value: "0.85", change: 12.0, icon: <PieChart className="w-4 h-4" /> },
        { label: "IV Percentile", value: "32%", icon: <BarChart3 className="w-4 h-4" /> },
        { label: "GEX", value: "$4.2B", change: 15.0, icon: <Zap className="w-4 h-4" /> },
      ]}
      datasets={[
        { name: "Options Chains", description: "Full options chains for US equities", frequency: "Real-time" },
        { name: "IV Term Structure", description: "Implied volatility across expirations", frequency: "Daily" },
        { name: "Volatility Surface", description: "3D visualization of IV by strike and expiry", frequency: "Daily" },
        { name: "Options Flow", description: "Large trades and unusual options activity", frequency: "Real-time" },
        { name: "Greeks Data", description: "Delta, gamma, theta, vega calculations", frequency: "Real-time" },
        { name: "Open Interest", description: "OI changes and positioning data", frequency: "Daily" },
      ]}
    />
  );
}

// Census Section
export function CensusSection() {
  return (
    <PlaceholderSection
      title="U.S. Census Bureau"
      subtitle="Population, business, and housing statistics"
      icon={<Users className="w-7 h-7" />}
      color="indigo"
      features={[
        "Population estimates and projections",
        "American Community Survey data",
        "Business and economic census",
        "Housing statistics and trends",
        "International trade data",
        "Retail sales and e-commerce",
        "Construction spending",
        "Manufacturers' shipments and inventories",
      ]}
      previewMetrics={[
        { label: "US Population", value: "335.9M", change: 0.5, icon: <Users className="w-4 h-4" /> },
        { label: "Retail Sales", value: "$709.9B", change: 3.2, icon: <ShoppingCart className="w-4 h-4" /> },
        { label: "Housing Starts", value: "1.46M", change: -4.3, icon: <Building2 className="w-4 h-4" /> },
        { label: "Business Apps", value: "432K", change: 1.8, icon: <Briefcase className="w-4 h-4" /> },
      ]}
      datasets={[
        { name: "Population Estimates", description: "National and state population by demographics", frequency: "Annual" },
        { name: "Retail Trade", description: "Monthly retail and food services sales", frequency: "Monthly" },
        { name: "New Home Sales", description: "Sales of new single-family houses", frequency: "Monthly" },
        { name: "Construction Spending", description: "Value of construction put in place", frequency: "Monthly" },
        { name: "Manufacturers' Shipments", description: "Durable goods orders and shipments", frequency: "Monthly" },
        { name: "Business Formation", description: "New business applications and high-propensity", frequency: "Weekly" },
      ]}
    />
  );
}

