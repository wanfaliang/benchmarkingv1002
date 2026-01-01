"""
Redis Cache Module for Finexus Research Portal

Provides decorator-based caching with graceful degradation.
If Redis is unavailable, the app continues to work normally.
"""

from .client import get_redis_client, redis_client
from .decorators import cached
from .ttl import DataCategory, get_ttl
from .keys import make_cache_key

__all__ = [
    "get_redis_client",
    "redis_client",
    "cached",
    "DataCategory",
    "get_ttl",
    "make_cache_key",
]
