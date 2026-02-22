# backend/app/jobs/ingest_games.py
from loguru import logger
import asyncio
from app.services.nba_service import get_today_games

def run_ingest_games():
    """Daily ingest to fetch latest games and store them to DB"""
    logger.info("Starting scheduled game ingest...")
    try:
        # Wrap the async function in the synchronous APScheduler
        asyncio.run(get_today_games())
        logger.info("Scheduled game ingest completed.")
    except Exception as e:
        logger.error(f"Scheduled game ingest failed: {e}")
