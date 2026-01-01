"""
Cache Decorators for FastAPI Endpoints

Works with both sync and async endpoints:

    @router.get("/overview")
    @cached("bls:ln:overview", category=DataCategory.BLS_MONTHLY)
    def get_overview(...):  # Sync - works!
        return data

    @router.get("/comprehensive")
    @cached("portal:bls:comprehensive", category=DataCategory.BLS_MONTHLY)
    async def get_comprehensive(...):  # Async - works!
        return data
"""

import asyncio
import functools
import inspect
import json
import logging
from typing import Callable, List, Optional

from .client import get_redis_client, serialize_value
from .keys import make_cache_key
from .ttl import DataCategory, get_ttl

logger = logging.getLogger(__name__)


def _sync_cache_get(key: str):
    """Synchronous cache get."""
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


def _sync_cache_set(key: str, value, ttl: int) -> bool:
    """Synchronous cache set."""
    client = get_redis_client()
    if not client:
        return False
    try:
        serialized = serialize_value(value)
        client.setex(key, ttl, serialized)
        print(f"[CACHE] SET: {key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.warning(f"Cache set error for {key}: {e}")
        return False


def cached(
    namespace: str,
    category: DataCategory = DataCategory.DEFAULT,
    ttl: Optional[int] = None,
    param_keys: Optional[List[str]] = None,
):
    """
    Decorator to cache endpoint responses in Redis.

    Args:
        namespace: Cache key namespace (e.g., "portal:bls:comprehensive")
        category: Data category for TTL selection
        ttl: Override TTL in seconds (uses category TTL if not provided)
        param_keys: List of parameter names to include in cache key
                   (if None, no params are included in key)

    Example:
        @cached("portal:bls:comprehensive", category=DataCategory.BLS_MONTHLY)
        async def get_comprehensive():
            ...

        @cached("bls:jt:overview", param_keys=["industry_code"])
        async def get_overview(industry_code: str = None):
            ...
    """

    def decorator(func: Callable):
        # Check if function is async or sync
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_params = {}
                if param_keys:
                    cache_params = {k: kwargs.get(k) for k in param_keys if k in kwargs}

                cache_key = make_cache_key(namespace, cache_params, param_keys)
                print(f"[CACHE] Checking key: {cache_key}")

                # Try cache (sync call is fine here)
                cached_value = _sync_cache_get(cache_key)
                if cached_value is not None:
                    print(f"[CACHE] HIT: {cache_key}")
                    return cached_value

                print(f"[CACHE] MISS: {cache_key} - calling function...")

                # Call async function
                result = await func(*args, **kwargs)
                print(f"[CACHE] Function returned, result type: {type(result)}")

                # Cache result
                cache_ttl = ttl if ttl is not None else get_ttl(category)
                _sync_cache_set(cache_key, result, cache_ttl)

                return result

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_params = {}
                if param_keys:
                    cache_params = {k: kwargs.get(k) for k in param_keys if k in kwargs}

                cache_key = make_cache_key(namespace, cache_params, param_keys)
                print(f"[CACHE] Checking key: {cache_key}")

                # Try cache
                cached_value = _sync_cache_get(cache_key)
                if cached_value is not None:
                    print(f"[CACHE] HIT: {cache_key}")
                    return cached_value

                print(f"[CACHE] MISS: {cache_key} - calling function...")

                # Call sync function
                result = func(*args, **kwargs)
                print(f"[CACHE] Function returned, result type: {type(result)}")

                # Cache result
                cache_ttl = ttl if ttl is not None else get_ttl(category)
                _sync_cache_set(cache_key, result, cache_ttl)

                return result

            return sync_wrapper

    return decorator


def cached_sync(
    namespace: str,
    category: DataCategory = DataCategory.DEFAULT,
    ttl: Optional[int] = None,
    param_keys: Optional[List[str]] = None,
):
    """
    Decorator for synchronous functions (non-async).

    Same as @cached but for sync functions.
    """
    import asyncio

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_params = {}
            if param_keys:
                cache_params = {k: kwargs.get(k) for k in param_keys if k in kwargs}

            cache_key = make_cache_key(namespace, cache_params, param_keys)

            # Try to get from cache (run async in sync context)
            loop = asyncio.new_event_loop()
            try:
                cached_value = loop.run_until_complete(cache_get(cache_key))
                if cached_value is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached_value
            finally:
                loop.close()

            logger.debug(f"Cache MISS: {cache_key}")

            # Call the actual function
            result = func(*args, **kwargs)

            # Cache the result
            cache_ttl = ttl if ttl is not None else get_ttl(category)
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(cache_set(cache_key, result, cache_ttl))
            finally:
                loop.close()

            return result

        return wrapper

    return decorator
