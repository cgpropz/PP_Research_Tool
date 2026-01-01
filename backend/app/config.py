from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    # Database - Use SQLite locally, Postgres in cloud
    database_url: str = os.environ.get(
        'DATABASE_URL',
        os.environ.get('DATABASE_PRIVATE_URL', 'sqlite:///./nba_props.db')
    )
    
    # JWT
    secret_key: str = os.environ.get('SECRET_KEY', 'your-super-secret-key-change-in-production')
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days
    
    # Stripe (optional)
    stripe_secret_key: str = os.environ.get('STRIPE_SECRET_KEY', '')
    stripe_publishable_key: str = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    stripe_webhook_secret: str = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    stripe_price_id: str = os.environ.get('STRIPE_PRICE_ID', '')
    
    # App URLs
    frontend_url: str = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    api_url: str = os.environ.get('API_URL', 'http://localhost:8000')
    debug: bool = os.environ.get('DEBUG', 'true').lower() == 'true'
    
    # Pro user (host account with unlimited access)
    pro_user_email: str = os.environ.get('PRO_USER_EMAIL', 'cgpropz@gmail.com')
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Fix Railway postgres URL format
        if self.database_url and self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
