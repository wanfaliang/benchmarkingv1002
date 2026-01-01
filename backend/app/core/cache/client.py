"""
Redis Client with Graceful Degradation

Features:
- Connection pooling for performance
- Graceful degradation if Redis unavailable
- 5-second socket timeout to prevent blocking
- Singleton pattern for connection reuse
"""

import json
import logging
from typing import Any, Optional

import redis
from redis import Redis

from ...config import settings

logger = logging.getLogger(__name__)

# Singleton Redis client
_redis_client: Optional[Redis] = None
_connection_failed: bool = False


def get_redis_client() -> Optional[Redis]:
    """
    Get Redis client instance (singleton).

    Returns None if:
    - Caching is disabled in settings
    - Redis connection fails (graceful degradation)
    """
    global _redis_client, _connection_failed

    # Check if caching is disabled
    if not settings.CACHE_ENABLED:
        return None

    # Don't retry if connection already failed (until app restart)
    if _connection_failed:
        return None

    # Return existing client if available
    if _redis_client is not None:
        return _redis_client

    try:
        # Build connection URL
        if settings.REDIS_URL:
            client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
            )
        else:
            client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
            )

        # Test connection
        client.ping()
        _redis_client = client
        logger.info(f"Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return _redis_client

    except redis.ConnectionError as e:
        logger.warning(f"Redis connection failed, caching disabled: {e}")
        _connection_failed = True
        return None
    except Exception as e:
        logger.warning(f"Redis error, caching disabled: {e}")
        _connection_failed = True
        return None


def redis_client() -> Optional[Redis]:
    """Alias for get_redis_client()"""
    return get_redis_client()


async def cache_get(key: str) -> Optional[Any]:
    """
    Get value from cache.

    Args:
        key: Cache key

    Returns:
        Cached value (deserialized from JSON) or None
    """
    client = get_redis_client()
    if not client:
        return None

    try:
        value = client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning(f"Cache get error for {key}: {e}")
        return None


def serialize_value(value: Any) -> str:
    """Serialize value to JSON, handling Pydantic models."""
    # Handle Pydantic models (v2)
    if hasattr(value, "model_dump"):
        return json.dumps(value.model_dump(), default=str)
    # Handle Pydantic models (v1)
    if hasattr(value, "dict"):
        return json.dumps(value.dict(), default=str)
    # Handle regular dicts/lists
    return json.dumps(value, default=str)


async def cache_set(key: str, value: Any, ttl: int) -> bool:
    """
    Set value in cache with TTL.

    Args:
        key: Cache key
        value: Value to cache (will be serialized to JSON)
        ttl: Time-to-live in seconds

    Returns:
        True if successful, False otherwise
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        serialized = serialize_value(value)
        client.setex(key, ttl, serialized)
        logger.info(f"Cache SET: {key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.warning(f"Cache set error for {key}: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """
    Delete a key from cache.

    Args:
        key: Cache key to delete

    Returns:
        True if successful, False otherwise
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete error for {key}: {e}")
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern.

    Args:
        pattern: Redis pattern (e.g., "finexus:portal:bls:*")

    Returns:
        Number of keys deleted
    """
    client = get_redis_client()
    if not client:
        return 0

    try:
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache delete pattern error for {pattern}: {e}")
        return 0


def get_cache_stats() -> dict:
    """
    Get cache statistics for health check.

    Returns:
        Dict with cache status info
    """
    client = get_redis_client()

    if not client:
        return {
            "connected": False,
            "enabled": settings.CACHE_ENABLED,
            "reason": "connection_failed" if _connection_failed else "disabled",
        }

    try:
        info = client.info("stats")
        return {
            "connected": True,
            "enabled": True,
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "keys": client.dbsize(),
        }
    except Exception as e:
        return {
            "connected": False,
            "enabled": True,
            "reason": str(e),
        }
