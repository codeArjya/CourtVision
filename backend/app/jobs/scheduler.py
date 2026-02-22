from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
import threading

scheduler = BackgroundScheduler()

def trigger_ingest_job():
    logger.info("Manual ingest job triggered")
    from app.jobs.ingest_games import run_ingest
    t = threading.Thread(target=run_ingest)
    t.start()

def trigger_retrain_job():
    logger.info("Manual retrain job triggered")
    from app.jobs.retrain import run_retrain
    t = threading.Thread(target=run_retrain)
    t.start()

def scheduled_ingest():
    logger.info("Cron: Running scheduled ingest")
    try:
        from app.jobs.ingest_games import run_ingest
        run_ingest()
    except Exception as e:
        logger.error(f"Scheduled ingest failed: {e}")

def scheduled_retrain():
    logger.info("Cron: Running scheduled retrain")
    try:
        from app.jobs.retrain import run_retrain
        run_retrain()
    except Exception as e:
        logger.error(f"Scheduled retrain failed: {e}")

def start_scheduler():
    from app.config import settings
    # Setup triggers based on env configuration
    
    # Ingest daily
    scheduler.add_job(
        scheduled_ingest,
        trigger=CronTrigger(hour=settings.INGEST_HOUR_UTC, timezone="UTC"),
        id="daily_ingest",
        replace_existing=True
    )
    
    # Retrain weekly
    scheduler.add_job(
        scheduled_retrain,
        trigger=CronTrigger(day_of_week=settings.RETRAIN_DAY, hour=settings.INGEST_HOUR_UTC + 1, timezone="UTC"),
        id="weekly_retrain",
        replace_existing=True
    )
    
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
