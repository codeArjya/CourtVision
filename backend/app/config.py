# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Gemini
    GEMINI_API_KEY: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_ANON_KEY: str = ""

    # Redis
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""

    # ML
    MODEL_PATH: str = "app/ml/artifacts/courtiq_model.pkl"
    MODEL_SCALER_PATH: str = "app/ml/artifacts/scaler.pkl"
    MODEL_FEATURES_PATH: str = "app/ml/artifacts/feature_names.json"
    MIN_GAMES_FOR_PREDICTION: int = 5
    USE_ML_MODEL: bool = True

    # Scheduling
    ENABLE_SCHEDULER: bool = True
    INGEST_HOUR_UTC: int = 8
    RETRAIN_DAY: str = "monday"

    # NBA API
    NBA_API_DELAY: float = 0.7

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
