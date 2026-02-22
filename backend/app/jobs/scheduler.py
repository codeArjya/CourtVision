# backend/app/jobs/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from app.config import settings
from app.jobs.ingest_games import run_ingest_games
from app.jobs.retrain import run_retrain

_scheduler = BackgroundScheduler()

def start_scheduler():
    if not settings.ENABLE_SCHEDULER:
        return
        
    try:
        # 1. Daily game ingestion
        _scheduler.add_job(
            run_ingest_games,
            trigger=CronTrigger(hour=settings.INGEST_HOUR_UTC, minute=0),
            id="ingest_games",
            name="Daily NBA game results ingestion",
            replace_existing=True
        )
        logger.info(f"Scheduled daily ingest at {settings.INGEST_HOUR_UTC}:00 UTC")

        # 2. Weekly retraining
        day_map = {
            "monday": "mon", "tuesday": "tue", "wednesday": "wed",
            "thursday": "thu", "friday": "fri", "saturday": "sat", "sunday": "sun"
        }
        cron_day = day_map.get(settings.RETRAIN_DAY.lower(), "mon")
        
        _scheduler.add_job(
            run_retrain,
            trigger=CronTrigger(day_of_week=cron_day, hour=settings.INGEST_HOUR_UTC + 1, minute=0), # 1 hr after ingest
            id="retrain_model",
            name="Weekly ML Model Retraining",
            replace_existing=True
        )
        logger.info(f"Scheduled weekly retrain on {cron_day} at {settings.INGEST_HOUR_UTC + 1}:00 UTC")

        _scheduler.start()
    except Exception as e:
        logger.error(f"Failed to start background scheduler: {e}")

def stop_scheduler():
    if _scheduler.running:
        _scheduler.shutdown()
        logger.info("Scheduler stopped.")
