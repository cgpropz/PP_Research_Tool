from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.routers import auth, payments, props, data, admin
from app.data_service import data_service
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create scheduler
scheduler = BackgroundScheduler(timezone='America/New_York')

# Check if running in cloud
IS_CLOUD = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RENDER')

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
    
    # Run initial refresh
    logger.info("🔄 Running initial data load...")
    refresh_odds_job()
    
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

# CORS middleware - allow all origins for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile access
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
    """Manually trigger a card refresh"""
    refresh_cards_job()
    return {"message": "Card refresh triggered"}
