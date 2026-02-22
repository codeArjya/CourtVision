def run_ingest():
    from app.services.nba_service import sync_recent_games
    from loguru import logger
    
    logger.info("Starting basketball game data ingestion...")
    sync_recent_games(days_back=2) 
    logger.info("Game ingestion complete.")
