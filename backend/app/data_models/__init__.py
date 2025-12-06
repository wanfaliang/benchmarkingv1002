"""
Data Models Package - Models for the DATA database (read-only access)

These models map to tables in the finexus_db database which contains:
- Financial/market data (companies, prices, financial statements)
- BEA economic data (NIPA, Regional, GDP by Industry, ITA, Fixed Assets)
- BLS labor statistics (CPI, Employment, Average Prices, etc.)
- Treasury auction and rate data
"""

# Financial/Market Models
from .models import (
    Company,
    IncomeStatement,
    BalanceSheet,
    CashFlow,
    FinancialRatio,
    KeyMetric,
    PriceDaily,
    PriceMonthly,
    PriceDailyBulk,
    PeersBulk,
    EnterpriseValue,
    EmployeeHistory,
    AnalystEstimate,
    PriceTarget,
    InsiderTrading,
    InstitutionalOwnership,
    InsiderStatistics,
    DataCollectionLog,
    TableUpdateTracking,
    EconomicIndicator,
    EconomicDataRaw,
    EconomicDataMonthly,
    EconomicDataQuarterly,
    EconomicCalendar,
    EarningsCalendar,
    NasdaqScreenerProfile,
    NasdaqETFScreenerProfile,
    CompanyProfileBulk,
    PriceTargetSummaryBulk,
    RatiosTTMBulk,
    KeyMetricsTTMBulk,
)

# BEA Models
from .bea_models import (
    BEADataset,
    NIPATable,
    NIPASeries,
    NIPAData,
    RegionalTable,
    RegionalLineCode,
    RegionalGeoFips,
    RegionalData,
    GDPSummary,
    PersonalIncomeSummary,
    GDPByIndustryTable,
    GDPByIndustryIndustry,
    GDPByIndustryData,
    ITAIndicator,
    ITAArea,
    ITAData,
    FixedAssetsTable,
    FixedAssetsSeries,
    FixedAssetsData,
)

# Treasury Models
from .treasury_models import (
    TreasurySecurityType,
    TreasuryAuction,
    TreasuryAuctionReaction,
    TreasuryUpcomingAuction,
    TreasuryDailyRate,
    TreasuryAuctionSchedule,
)

# BLS Models - Reference Tables
from .bls_models import (
    BLSSurvey,
    BLSArea,
    BLSPeriod,
    BLSPeriodicity,
)

# BLS Models - Average Prices (AP)
from .bls_models import (
    APItem,
    APSeries,
    APData,
)

# BLS Models - Consumer Price Index (CU)
from .bls_models import (
    CUArea,
    CUItem,
    CUSeries,
    CUData,
    CUAspect,
)

# BLS Models - Chained CPI (CW)
from .bls_models import (
    CWArea,
    CWItem,
    CWSeries,
    CWData,
    CWAspect,
)

# BLS Models - Spending Survey (SU)
from .bls_models import (
    SUArea,
    SUItem,
    SUSeries,
    SUData,
)

# BLS Models - Local Area (LA) Employment
from .bls_models import (
    LAArea,
    LAMeasure,
    LASeries,
    LAData,
)

# BLS Models - Current Employment Statistics (CE)
from .bls_models import (
    CEIndustry,
    CEDataType,
    CESupersector,
    CESeries,
    CEData,
)

# BLS Models - Producer Price (PC)
from .bls_models import (
    PCIndustry,
    PCProduct,
    PCSeries,
    PCData,
)

# BLS Models - Wholesale Price (WP)
from .bls_models import (
    WPGroup,
    WPItem,
    WPSeries,
    WPData,
)

# BLS Models - State/Metro Employment (SM)
from .bls_models import (
    SMState,
    SMArea,
    SMSupersector,
    SMIndustry,
    SMSeries,
    SMData,
)

# BLS Models - Job Openings (JT - JOLTS)
from .bls_models import (
    JTDataElement,
    JTIndustry,
    JTState,
    JTArea,
    JTSizeClass,
    JTRateLevel,
    JTSeries,
    JTData,
)

# BLS Models - Employment Cost (EC)
from .bls_models import (
    ECCompensation,
    ECGroup,
    ECOwnership,
    ECPeriodicity,
    ECSeries,
    ECData,
)

# BLS Models - Occupational Employment (OE)
from .bls_models import (
    OEAreaType,
    OEDataType,
    OEIndustry,
    OEOccupation,
    OESector,
    OEArea,
    OESeries,
    OEData,
)

# BLS Models - Productivity (PR)
from .bls_models import (
    PRClass,
    PRMeasure,
    PRDuration,
    PRSector,
    PRSeries,
    PRData,
)

# BLS Models - Industry Productivity (IP)
from .bls_models import (
    IPSector,
    IPIndustry,
    IPMeasure,
    IPDuration,
    IPType,
    IPArea,
    IPSeries,
    IPData,
)

# BLS Models - Time Use (TU)
from .bls_models import (
    TUStatType,
    TUActivityCode,
    TUSex,
)

__all__ = [
    # Financial/Market
    "Company",
    "IncomeStatement",
    "BalanceSheet",
    "CashFlow",
    "FinancialRatio",
    "KeyMetric",
    "PriceDaily",
    "PriceMonthly",
    "PriceDailyBulk",
    "PeersBulk",
    "EnterpriseValue",
    "EmployeeHistory",
    "AnalystEstimate",
    "PriceTarget",
    "InsiderTrading",
    "InstitutionalOwnership",
    "InsiderStatistics",
    "DataCollectionLog",
    "TableUpdateTracking",
    "EconomicIndicator",
    "EconomicDataRaw",
    "EconomicDataMonthly",
    "EconomicDataQuarterly",
    "EconomicCalendar",
    "EarningsCalendar",
    "NasdaqScreenerProfile",
    "NasdaqETFScreenerProfile",
    "CompanyProfileBulk",
    "PriceTargetSummaryBulk",
    "RatiosTTMBulk",
    "KeyMetricsTTMBulk",
    # BEA
    "BEADataset",
    "NIPATable",
    "NIPASeries",
    "NIPAData",
    "RegionalTable",
    "RegionalLineCode",
    "RegionalGeoFips",
    "RegionalData",
    "GDPSummary",
    "PersonalIncomeSummary",
    "GDPByIndustryTable",
    "GDPByIndustryIndustry",
    "GDPByIndustryData",
    "ITAIndicator",
    "ITAArea",
    "ITAData",
    "FixedAssetsTable",
    "FixedAssetsSeries",
    "FixedAssetsData",
    # Treasury
    "TreasurySecurityType",
    "TreasuryAuction",
    "TreasuryAuctionReaction",
    "TreasuryUpcomingAuction",
    "TreasuryDailyRate",
    "TreasuryAuctionSchedule",
    # BLS
    "BLSSurvey",
    "BLSArea",
    "BLSPeriod",
    "BLSPeriodicity",
    "APItem",
    "APSeries",
    "APData",
    "CUArea",
    "CUItem",
    "CUSeries",
    "CUData",
    "CUAspect",
    "CWArea",
    "CWItem",
    "CWSeries",
    "CWData",
    "CWAspect",
    "SUArea",
    "SUItem",
    "SUSeries",
    "SUData",
    "LAArea",
    "LAMeasure",
    "LASeries",
    "LAData",
    "CEIndustry",
    "CEDataType",
    "CESupersector",
    "CESeries",
    "CEData",
    "PCIndustry",
    "PCProduct",
    "PCSeries",
    "PCData",
    "WPGroup",
    "WPItem",
    "WPSeries",
    "WPData",
    "SMState",
    "SMArea",
    "SMSupersector",
    "SMIndustry",
    "SMSeries",
    "SMData",
    "JTDataElement",
    "JTIndustry",
    "JTState",
    "JTArea",
    "JTSizeClass",
    "JTRateLevel",
    "JTSeries",
    "JTData",
    "ECCompensation",
    "ECGroup",
    "ECOwnership",
    "ECPeriodicity",
    "ECSeries",
    "ECData",
    "OEAreaType",
    "OEDataType",
    "OEIndustry",
    "OEOccupation",
    "OESector",
    "OEArea",
    "OESeries",
    "OEData",
    "PRClass",
    "PRMeasure",
    "PRDuration",
    "PRSector",
    "PRSeries",
    "PRData",
    "IPSector",
    "IPIndustry",
    "IPMeasure",
    "IPDuration",
    "IPType",
    "IPArea",
    "IPSeries",
    "IPData",
    "TUStatType",
    "TUActivityCode",
    "TUSex",
]
