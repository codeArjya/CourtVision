# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.routes import games, predictions, player_card, takes, admin, chat
from app.ml.predict import load_model_artifacts
from app.jobs.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CourtIQ API starting up...")
    
    try:
        load_model_artifacts()
        logger.info("ML model artifacts loaded successfully")
    except FileNotFoundError:
        logger.warning("ML model artifacts not found — predictions will use Gemini fallback. Run bootstrap + train first.")
    except Exception as e:
        logger.error(f"ML model load failed: {e}")

    if settings.ENABLE_SCHEDULER:
        start_scheduler()
        logger.info("Background scheduler started")

    yield

    if settings.ENABLE_SCHEDULER:
        stop_scheduler()
    logger.info("CourtIQ API shut down")

app = FastAPI(
    title="CourtIQ API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router,       prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(player_card.router, prefix="/api")
app.include_router(takes.router,       prefix="/api")
app.include_router(admin.router,       prefix="/api")
app.include_router(chat.router,        prefix="/api")

@app.get("/health")
def health():
    from app.ml.predict import model_loaded
    return {
        "status": "ok",
        "service": "courtiq-api",
        "ml_model_loaded": model_loaded(),
        "environment": settings.ENVIRONMENT
    }
