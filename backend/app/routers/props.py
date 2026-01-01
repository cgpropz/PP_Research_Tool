import json
import os
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.models import User
from app.schemas import PlayerCardBase, PlayerCardsListResponse
from app.auth import get_current_active_user, get_optional_user, require_subscription
from app.tier_utils import (
    has_feature, 
    TierFeature, 
    get_feature_access, 
    filter_card_by_tier,
    get_props_limit
)

router = APIRouter(prefix="/props", tags=["Player Props"])

# Path to data files (relative to backend folder)
DATA_DIR = Path(__file__).parent.parent.parent.parent  # Go up to NBA-UI-Props root


def load_player_cards() -> List[dict]:
    """Load player cards from JSON file"""
    cards_path = DATA_DIR / "PLAYER_UI_CARDS_PERFECT.json"
    if not cards_path.exists():
        return []
    
    with open(cards_path, "r") as f:
        return json.load(f)


def load_player_odds() -> List[dict]:
    """Load player odds from JSON file"""
    odds_path = DATA_DIR / "nba_player_odds.json"
    if not odds_path.exists():
        return []
    
    with open(odds_path, "r") as f:
        return json.load(f)


def load_dvp_data() -> dict:
    """Load DVP (Defense vs Position) data"""
    dvp_path = DATA_DIR / "DVP_2025_weighted.json"
    if not dvp_path.exists():
        return {}
    
    with open(dvp_path, "r") as f:
        return json.load(f)


@router.get("/cards", response_model=PlayerCardsListResponse)
async def get_player_cards(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    team: Optional[str] = None,
    prop: Optional[str] = None,
    min_score: Optional[float] = None,
    player_name: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get player prop cards with tier-based restrictions.
    
    Free users: Limited to 10 cards, basic data only
    Basic users: All cards, full analysis except DVP
    Pro users: All cards with full data including DVP
    """
    tier = current_user.subscription_tier if current_user else "free"
    cards = load_player_cards()
    
    # Apply filters (team filter available to all)
    if team and has_feature(tier, TierFeature.TEAM_FILTERS):
        cards = [c for c in cards if c.get("team", "").upper() == team.upper()]
    
    # Prop filter - basic+ only
    if prop and has_feature(tier, TierFeature.ALL_PROPS):
        cards = [c for c in cards if prop.lower() in c.get("prop", "").lower()]
    
    if min_score is not None:
        cards = [c for c in cards if (c.get("score") or 0) >= min_score]
    
    # Player search - basic+ only (but single player lookups allowed)
    if player_name and has_feature(tier, TierFeature.PLAYER_SEARCH):
        cards = [c for c in cards if player_name.lower() in c.get("name", "").lower()]
    
    # Sort by score (highest first)
    cards = sorted(cards, key=lambda x: x.get("score") or 0, reverse=True)
    
    # Get tier-based limits
    total = len(cards)
    props_limit = get_props_limit(tier)
    
    # Apply tier limits
    if tier == "free":
        cards = cards[:props_limit]
        total = min(total, props_limit)
        per_page = min(per_page, props_limit)
    
    # Pagination for paid tiers
    start = (page - 1) * per_page
    end = start + per_page
    cards = cards[start:end]
    
    # Filter card data based on tier
    cards = [filter_card_by_tier(c, tier) for c in cards]
    
    return PlayerCardsListResponse(
        cards=[PlayerCardBase(**c) for c in cards],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/cards/top", response_model=List[PlayerCardBase])
async def get_top_cards(
    limit: int = Query(10, ge=1, le=50),
    prop: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get top-rated player prop cards.
    Available to all tiers (free gets max 10).
    """
    tier = current_user.subscription_tier if current_user else "free"
    cards = load_player_cards()
    
    if prop:
        cards = [c for c in cards if prop.lower() in c.get("prop", "").lower()]
    
    # Free users limited to 10
    max_limit = 10 if tier == "free" else limit
    
    # Sort by score
    cards = sorted(cards, key=lambda x: x.get("score") or 0, reverse=True)[:max_limit]
    
    # Filter card data based on tier
    cards = [filter_card_by_tier(c, tier) for c in cards]
    
    return [PlayerCardBase(**c) for c in cards]


@router.get("/cards/player/{player_name}")
async def get_player_props(
    player_name: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get all props for a specific player with tier-based data"""
    tier = current_user.subscription_tier if current_user else "free"
    cards = load_player_cards()
    
    # Find matching cards
    player_cards = [
        c for c in cards 
        if player_name.lower().replace("-", " ") in c.get("name", "").lower()
    ]
    
    if not player_cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No props found for player: {player_name}"
        )
    
    # Filter card data based on tier
    player_cards = [filter_card_by_tier(c, tier) for c in player_cards]
    
    return player_cards


@router.get("/odds")
async def get_odds(
    player_name: Optional[str] = None,
    team: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get live odds data.
    Requires basic subscription or higher.
    """
    tier = current_user.subscription_tier if current_user else "free"
    
    if not has_feature(tier, TierFeature.ODDS_COMPARISON):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Odds comparison requires Basic subscription or higher"
        )
    
    odds = load_player_odds()
    
    if player_name:
        odds = [o for o in odds if player_name.lower() in o.get("name", "").lower()]
    
    if team:
        odds = [o for o in odds if o.get("team", "").upper() == team.upper()]
    
    return {"odds": odds[:100], "total": len(odds)}


@router.get("/dvp")
async def get_dvp(
    team: Optional[str] = None,
    position: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get Defense vs Position data.
    Requires Pro subscription.
    """
    tier = current_user.subscription_tier if current_user else "free"
    
    if not has_feature(tier, TierFeature.DVP_ANALYSIS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DVP analysis requires Pro subscription"
        )
    
    dvp = load_dvp_data()
    
    if team:
        return {team.upper(): dvp.get(team.upper(), {})}
    
    return dvp


@router.get("/features")
async def get_user_features(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get all available features for the current user's tier"""
    tier = current_user.subscription_tier if current_user else "free"
    
    return {
        "tier": tier,
        "features": get_feature_access(tier),
        "props_limit": get_props_limit(tier)
    }


@router.get("/teams")
async def get_teams():
    """Get list of all teams (public endpoint)"""
    cards = load_player_cards()
    teams = list(set(c.get("team") for c in cards if c.get("team")))
    return {"teams": sorted(teams)}


@router.get("/prop-types")
async def get_prop_types():
    """Get list of all prop types (public endpoint)"""
    cards = load_player_cards()
    props = list(set(c.get("prop") for c in cards if c.get("prop")))
    return {"props": sorted(props)}
