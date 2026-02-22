# backend/app/jobs/retrain.py
from loguru import logger
from app.ml.train import train_model
from app.ml.predict import load_model_artifacts

def run_retrain():
    """Weekly retrain of the xgboost model on the latest DB games"""
    logger.info("Starting scheduled model retrain...")
    try:
        success = train_model()
        if success:
            logger.info("Model retrained successfully. Reloading artifacts in memory...")
            load_model_artifacts()
            logger.info("Memory artifacts refreshed.")
        else:
            logger.warning("Retrain did not complete successfully (maybe not enough data).")
    except Exception as e:
        logger.error(f"Scheduled model retrain failed: {e}")
