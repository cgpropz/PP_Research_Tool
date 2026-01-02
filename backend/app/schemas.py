from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============ Auth Schemas ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    subscription_tier: str
    subscription_status: Optional[str]
    subscription_end_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


# ============ Player Card Schemas ============

class PlayerCardBase(BaseModel):
    name: str
    team: Optional[str] = None
    opponent: Optional[str] = None
    prop: Optional[str] = None
    line: Optional[float] = None
    last_5: Optional[str] = None
    last_5_pct: Optional[float] = None
    last_10: Optional[str] = None
    last_10_pct: Optional[float] = None
    last_20: Optional[str] = None
    last_20_pct: Optional[float] = None
    season: Optional[str] = None
    season_pct: Optional[float] = None
    avg: Optional[float] = None
    games: Optional[int] = None
    last_10_values: Optional[List[float]] = None
    projection: Optional[float] = None
    expected_minutes: Optional[float] = None
    player_id: Optional[int] = None
    score: Optional[float] = None
    spread: Optional[float] = None
    # New fields from cloud_scheduler
    player_name: Optional[str] = None
    player_slug: Optional[str] = None
    position: Optional[str] = None
    stat_type: Optional[str] = None
    median: Optional[float] = None
    hit_rate: Optional[float] = None
    hit_count: Optional[int] = None
    games_played: Optional[int] = None
    over_odds: Optional[int] = None
    under_odds: Optional[int] = None
    last_updated: Optional[str] = None
    dvp_rank: Optional[int] = None


class PlayerCardResponse(PlayerCardBase):
    class Config:
        from_attributes = True


class PlayerCardsListResponse(BaseModel):
    cards: List[PlayerCardBase]
    total: int
    page: int
    per_page: int


# ============ Subscription Schemas ============

class SubscriptionCreate(BaseModel):
    price_id: str


class SubscriptionResponse(BaseModel):
    subscription_id: str
    status: str
    current_period_end: datetime
    tier: str


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class PortalSessionResponse(BaseModel):
    portal_url: str


# ============ Odds Schemas ============

class OddsBook(BaseModel):
    book: str
    value: float
    overPrice: Optional[int] = None
    underPrice: Optional[int] = None


class OddsSummary(BaseModel):
    manualOU: float
    overPrice: Optional[int] = None
    underPrice: Optional[int] = None


class PlayerOddsProjection(BaseModel):
    summary: OddsSummary
    books: List[OddsBook]


class PlayerOdds(BaseModel):
    id: str
    gameId: str
    name: str
    homeTeam: str
    awayTeam: str
    team: str
    position: Optional[str] = None
    projection: dict


class PlayerOddsResponse(BaseModel):
    odds: List[PlayerOdds]
    total: int
