"""
TTL (Time-To-Live) Strategy for Cache

Session-based caching (15 min) for data endpoints.
User auth cached for 30 min (matches JWT expiration).
"""

from enum import Enum
from ...config import settings


class DataCategory(str, Enum):
    """Data categories with different cache TTL strategies"""

    BLS_MONTHLY = "bls_monthly"      # BLS data
    CLAIMS_WEEKLY = "claims"         # Jobless claims
    TREASURY_YIELDS = "treasury"     # Treasury data
    FRED_SERIES = "fred"             # FRED series
    AUTH = "auth"                    # User authentication
    METADATA = "metadata"            # Series info, descriptions
    DEFAULT = "default"              # Fallback


def get_ttl(category: DataCategory) -> int:
    """Get cache TTL in seconds for a data category."""
    ttl_map = {
        DataCategory.BLS_MONTHLY: settings.CACHE_TTL_BLS,
        DataCategory.CLAIMS_WEEKLY: settings.CACHE_TTL_CLAIMS,
        DataCategory.TREASURY_YIELDS: settings.CACHE_TTL_TREASURY,
        DataCategory.FRED_SERIES: settings.CACHE_TTL_FRED,
        DataCategory.AUTH: settings.CACHE_TTL_AUTH,
        DataCategory.METADATA: settings.CACHE_TTL_BLS,
        DataCategory.DEFAULT: settings.CACHE_TTL_DEFAULT,
    }

    return ttl_map.get(category, settings.CACHE_TTL_DEFAULT)
