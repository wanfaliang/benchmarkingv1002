"""
Cache Key Generation

Key pattern: {prefix}:{module}:{endpoint}:{params_hash}
Example: finexus:portal:bls:comprehensive:d41d8cd9
"""

import hashlib
import json
from typing import Any, Dict, List, Optional

from ...config import settings


def make_cache_key(
    namespace: str,
    params: Optional[Dict[str, Any]] = None,
    param_keys: Optional[List[str]] = None,
) -> str:
    """
    Generate a cache key from namespace and parameters.

    Args:
        namespace: Key namespace (e.g., "portal:bls:comprehensive")
        params: Dictionary of parameters to include in key
        param_keys: If provided, only include these keys from params

    Returns:
        Cache key string like "finexus:portal:bls:comprehensive:a1b2c3d4"
    """
    prefix = settings.CACHE_PREFIX
    base_key = f"{prefix}:{namespace}"

    if not params:
        return base_key

    # Filter to only specified param keys if provided
    if param_keys:
        filtered_params = {k: v for k, v in params.items() if k in param_keys}
    else:
        filtered_params = params

    # Remove None values and sort for consistent hashing
    clean_params = {k: v for k, v in sorted(filtered_params.items()) if v is not None}

    if not clean_params:
        return base_key

    # Create hash of parameters
    params_json = json.dumps(clean_params, sort_keys=True, default=str)
    params_hash = hashlib.md5(params_json.encode()).hexdigest()[:8]

    return f"{base_key}:{params_hash}"


def invalidate_pattern(namespace: str) -> str:
    """
    Generate a pattern for invalidating all keys in a namespace.

    Args:
        namespace: Key namespace to invalidate

    Returns:
        Pattern string for Redis SCAN/KEYS (e.g., "finexus:portal:bls:*")
    """
    prefix = settings.CACHE_PREFIX
    return f"{prefix}:{namespace}:*"
