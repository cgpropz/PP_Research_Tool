from enum import Enum
from typing import Dict, List

class TierFeature(str, Enum):
    """All available features gated by tier"""
    # Free tier
    TOP_PROPS = "top_props"  # Top 10 props
    BASIC_ANALYSIS = "basic_analysis"  # Hit rate %
    TEAM_FILTERS = "team_filters"  # Filter by team
    
    # Basic tier
    ALL_PROPS = "all_props"  # All player props
    FULL_ANALYSIS = "full_analysis"  # Detailed hit rate
    SMART_PROJECTIONS = "smart_projections"  # Projection data
    ODDS_COMPARISON = "odds_comparison"  # Live odds
    PLAYER_SEARCH = "player_search"  # Search functionality
    LAST_10_TRENDS = "last_10_trends"  # Last 10 games
    
    # Pro tier
    DVP_ANALYSIS = "dvp_analysis"  # Defense vs Position
    ADVANCED_PROJECTIONS = "advanced_projections"  # AI projections
    API_ACCESS = "api_access"  # API endpoints
    PRIORITY_SUPPORT = "priority_support"
    EARLY_ACCESS = "early_access"
    CUSTOM_ALERTS = "custom_alerts"
    EXPORT_DATA = "export_data"


# Define which tiers have which features
TIER_FEATURES: Dict[str, List[TierFeature]] = {
    "free": [
        TierFeature.TOP_PROPS,
        TierFeature.BASIC_ANALYSIS,
        TierFeature.TEAM_FILTERS,
    ],
    "basic": [
        # All free features
        TierFeature.TOP_PROPS,
        TierFeature.BASIC_ANALYSIS,
        TierFeature.TEAM_FILTERS,
        # Plus basic features
        TierFeature.ALL_PROPS,
        TierFeature.FULL_ANALYSIS,
        TierFeature.SMART_PROJECTIONS,
        TierFeature.ODDS_COMPARISON,
        TierFeature.PLAYER_SEARCH,
        TierFeature.LAST_10_TRENDS,
    ],
    "pro": list(TierFeature),  # All features
}


def has_feature(tier: str, feature: TierFeature) -> bool:
    """Check if a tier has access to a feature"""
    if tier not in TIER_FEATURES:
        tier = "free"
    return feature in TIER_FEATURES[tier]


def get_feature_access(tier: str) -> Dict[str, bool]:
    """Get all feature access for a tier"""
    if tier not in TIER_FEATURES:
        tier = "free"
    
    return {feature.value: feature in TIER_FEATURES[tier] for feature in TierFeature}


def filter_card_by_tier(card: dict, tier: str) -> dict:
    """Remove fields based on user tier"""
    filtered = card.copy()
    
    # Free tier - minimal data
    if tier == "free":
        # Keep only basic fields
        keep_fields = {
            "name", "team", "opponent", "prop", "line", 
            "last_5_pct", "games", "player_id", "score"
        }
        filtered = {k: v for k, v in filtered.items() if k in keep_fields}
    
    # Basic tier - remove only advanced features
    elif tier == "basic":
        # Remove DVP and advanced projections
        filtered.pop("dvp_rank", None)
        filtered.pop("dvp_comparison", None)
        filtered.pop("advanced_score", None)
    
    # Pro tier - all data (no filtering)
    
    return filtered


def get_props_limit(tier: str) -> int:
    """Get the maximum number of props a tier can view"""
    limits = {
        "free": 10,
        "basic": 1000,
        "pro": 10000,
    }
    return limits.get(tier, 10)
