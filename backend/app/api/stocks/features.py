"""Feature registry API endpoints"""
from fastapi import APIRouter, Query
from typing import List, Optional

from ...schemas.stocks import FeatureInfo, FeatureListResponse, FeatureCategory
from ...services.stocks.feature_registry import (
    FEATURE_REGISTRY,
    get_feature,
    get_features_by_category,
    get_all_categories,
    get_feature_count
)

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/", response_model=FeatureListResponse)
def list_features(
    category: Optional[FeatureCategory] = Query(None, description="Filter by category")
):
    """
    Get all available screening features.

    Optionally filter by category (valuation, profitability, etc.)
    """
    if category:
        features_data = get_features_by_category(category.value)
    else:
        features_data = [{"key": k, **v} for k, v in FEATURE_REGISTRY.items()]

    features = [
        FeatureInfo(
            key=f["key"],
            name=f["name"],
            category=f["category"],
            description=f.get("description"),
            source_table=f["source_table"],
            source_column=f["source_column"],
            data_type=f.get("data_type", "number"),
            unit=f.get("unit"),
            is_computed=f.get("is_computed", False),
            lower_is_better=f.get("lower_is_better"),
            null_handling=f.get("null_handling", "exclude")
        )
        for f in features_data
    ]

    return FeatureListResponse(
        total_count=len(features),
        features=features,
        categories=get_all_categories()
    )


@router.get("/categories")
def list_categories():
    """Get all feature categories with counts"""
    categories = get_all_categories()
    result = []

    for cat in sorted(categories):
        features = get_features_by_category(cat)
        result.append({
            "category": cat,
            "count": len(features),
            "features": [f["key"] for f in features]
        })

    return {
        "total_categories": len(categories),
        "categories": result
    }


@router.get("/{feature_key}")
def get_feature_detail(feature_key: str):
    """Get detailed information about a specific feature"""
    feature = get_feature(feature_key)

    if not feature:
        return {"error": f"Feature '{feature_key}' not found"}

    return {
        "key": feature_key,
        **feature
    }


@router.get("/stats/summary")
def get_feature_stats():
    """Get summary statistics about available features"""
    categories = get_all_categories()

    # Count by category
    by_category = {}
    for cat in categories:
        by_category[cat] = len(get_features_by_category(cat))

    # Count by source table
    by_table = {}
    for f in FEATURE_REGISTRY.values():
        table = f["source_table"]
        by_table[table] = by_table.get(table, 0) + 1

    return {
        "total_features": get_feature_count(),
        "total_categories": len(categories),
        "by_category": by_category,
        "by_source_table": by_table
    }
