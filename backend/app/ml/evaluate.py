# backend/app/ml/evaluate.py
import joblib
from loguru import logger
from app.config import settings

def get_model_status() -> dict:
    """Returns metadata about the currently trained model."""
    try:
        import os
        from datetime import datetime
        if not os.path.exists(settings.MODEL_PATH):
            return {
                "status": "not_trained",
                "message": "Model artifacts not found."
            }
            
        # Get creation time
        mtime = os.path.getmtime(settings.MODEL_PATH)
        trained_at = datetime.fromtimestamp(mtime).isoformat()
        
        # Try load package for metrics
        pkg = joblib.load(settings.MODEL_PATH)
        metrics = pkg.get('metrics', {})
        
        return {
            "status": "trained",
            "trained_at": trained_at,
            "accuracy": metrics.get("accuracy", 0.0),
            "mae_home": metrics.get("home_mae", 0.0),
            "mae_away": metrics.get("away_mae", 0.0)
        }
    except Exception as e:
        logger.error(f"Error reading model status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
