from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Stripe customer ID
    stripe_customer_id = Column(String, unique=True, nullable=True)
    
    # Subscription info
    subscription_tier = Column(String, default=SubscriptionTier.FREE)
    subscription_status = Column(String, nullable=True)
    subscription_id = Column(String, nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    api_calls = relationship("APICallLog", back_populates="user")


class APICallLog(Base):
    """Track API usage for rate limiting and analytics"""
    __tablename__ = "api_call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="api_calls")


class PlayerCard(Base):
    """Cache player card data for faster queries"""
    __tablename__ = "player_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, index=True)
    name = Column(String, index=True)
    team = Column(String)
    opponent = Column(String)
    prop = Column(String)
    line = Column(Float)
    last_5_pct = Column(Float)
    last_10_pct = Column(Float)
    last_20_pct = Column(Float)
    season_pct = Column(Float)
    avg = Column(Float)
    projection = Column(Float)
    score = Column(Float)
    data_json = Column(String)  # Full JSON data
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
