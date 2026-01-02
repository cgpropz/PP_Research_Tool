from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.routers import auth, payments, props, data, admin
from app.data_service import data_service
from app.database import engine, Base, SessionLocal
from app.models import User
from app.auth import get_password_hash
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create scheduler
scheduler = BackgroundScheduler(timezone='America/New_York')

# Check if running in cloud
IS_CLOUD = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER')


def create_initial_user():
    """Create the initial admin/pro user if it doesn't exist"""
    logger.info("🔐 Checking for initial user...")
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == settings.pro_user_email).first()
        if not user:
            # Create the pro user with the specified password
            hashed_password = get_password_hash("Kmh050598!")
            new_user = User(
                email=settings.pro_user_email,
                hashed_password=hashed_password,
                full_name="Pro User",
                subscription_tier="pro",
                subscription_status="active",
                is_active=True,
                is_verified=True
            )
            db.add(new_user)
            db.commit()
            logger.info(f"✅ Created initial pro user: {settings.pro_user_email}")
        else:
            logger.info(f"✅ Pro user already exists: {settings.pro_user_email}")
    except Exception as e:
        logger.error(f"❌ Error creating initial user: {e}")
        db.rollback()
    finally:
        db.close()


def refresh_odds_job():
    """Background job to refresh odds every 5 minutes"""
    logger.info("📊 Fetching latest odds...")
    try:
        from app.cloud_scheduler import fetch_odds, build_player_cards
        fetch_odds()
        build_player_cards()
        data_service.clear_cache('player_cards')
        logger.info("✅ Odds refresh completed")
    except Exception as e:
        logger.error(f"❌ Odds refresh error: {e}")

def daily_update_job():
    """Daily job for DVP and gamelogs (runs at 6 AM EST)"""
    logger.info("📆 Running daily update (DVP + Gamelogs)...")
    try:
        from app.cloud_scheduler import run_daily_update
        run_daily_update()
        data_service.clear_cache('player_cards')
        logger.info("✅ Daily update completed")
    except Exception as e:
        logger.error(f"❌ Daily update error: {e}")

def gamelog_update_job():
    """Gamelog update every 2 hours"""
    logger.info("📈 Updating gamelogs...")
    try:
        from app.cloud_scheduler import fetch_gamelogs, build_player_cards
        fetch_gamelogs()
        build_player_cards()
        data_service.clear_cache('player_cards')
        logger.info("✅ Gamelog update completed")
    except Exception as e:
        logger.error(f"❌ Gamelog update error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🏀 NBA Props API starting up...")
    logger.info(f"📚 Docs available at: {settings.api_url}/docs")
    logger.info(f"☁️ Cloud mode: {IS_CLOUD}")
    
    # Create database tables
    logger.info("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create initial admin user
    create_initial_user()
    
    # Odds refresh every 5 minutes
    scheduler.add_job(
        refresh_odds_job,
        IntervalTrigger(minutes=5),
        id='refresh_odds',
        name='Refresh odds every 5 minutes',
        replace_existing=True
    )
    
    # Daily DVP update at 6 AM EST
    scheduler.add_job(
        daily_update_job,
        CronTrigger(hour=6, minute=0),
        id='daily_update',
        name='Daily DVP and full update at 6 AM EST',
        replace_existing=True
    )
    
    # Gamelog update every 2 hours
    scheduler.add_job(
        gamelog_update_job,
        IntervalTrigger(hours=2),
        id='gamelog_update',
        name='Gamelog update every 2 hours',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("⏰ Scheduler started:")
    logger.info("   - Odds: every 5 minutes")
    logger.info("   - DVP: daily at 6 AM EST")
    logger.info("   - Gamelogs: every 2 hours")
    
    # Run initial full data load (gamelogs + odds + cards)
    logger.info("🔄 Running initial data load...")
    try:
        from app.cloud_scheduler import fetch_gamelogs, fetch_odds, fetch_schedule, build_player_cards
        # Fetch gamelogs first (required for building cards)
        fetch_gamelogs()
        fetch_schedule()
        fetch_odds()
        build_player_cards()
        data_service.clear_cache()
        logger.info("✅ Initial data load completed")
    except Exception as e:
        logger.error(f"❌ Initial data load error: {e}")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("👋 NBA Props API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="NBA Props API",
    description="API for NBA player prop betting analysis and predictions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware - explicitly list allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pp-research-tool.vercel.app",
        "https://pp-research-tool-*.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(props.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "NBA Props API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/scheduler/status")
async def scheduler_status():
    """Get scheduler status and next run time"""
    jobs = scheduler.get_jobs()
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
            }
            for job in jobs
        ]
    }


@app.post("/api/scheduler/trigger")
async def trigger_refresh():
    """Manually trigger a full data refresh using cloud_scheduler"""
    from app.cloud_scheduler import fetch_gamelogs, fetch_odds, fetch_schedule, build_player_cards
    results = {}
    
    try:
        logger.info("🔄 Manual trigger: fetching gamelogs...")
        results['gamelogs'] = fetch_gamelogs()
    except Exception as e:
        logger.error(f"❌ Gamelogs fetch error: {e}")
        results['gamelogs'] = str(e)
    
    try:
        logger.info("🔄 Manual trigger: fetching schedule...")
        results['schedule'] = fetch_schedule()
    except Exception as e:
        logger.error(f"❌ Schedule fetch error: {e}")
        results['schedule'] = str(e)
    
    try:
        logger.info("🔄 Manual trigger: fetching odds...")
        results['odds'] = fetch_odds()
    except Exception as e:
        logger.error(f"❌ Odds fetch error: {e}")
        results['odds'] = str(e)
    
    try:
        logger.info("🔄 Manual trigger: building cards...")
        results['cards'] = build_player_cards()
    except Exception as e:
        logger.error(f"❌ Card build error: {e}")
        results['cards'] = str(e)
    
    data_service.clear_cache()
    return {"message": "Manual refresh completed", "results": results}
