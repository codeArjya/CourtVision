from loguru import logger
from fastapi import APIRouter
from app.services import supabase_service, gemini_service
from app.ml.predict import predict_game, model_loaded
from app.config import settings
import pandas as pd

router = APIRouter()

@router.get("/predictions/{game_id}")
async def get_prediction(game_id: str):
    logger.info(f"Prediction requested for {game_id}")

    # 1. Check Supabase cache
    cached = supabase_service.get_cached_prediction(game_id)
    if cached:
        logger.info(f"Cache hit for {game_id}")
        return cached

    # 2. Fetch game info
    from app.services.nba_service import get_today_games
    games = await get_today_games()
    game = next((g for g in games if g["game_id"] == game_id), None)

    if not game:
        from app.data.seed_mock import MOCK_GAMES
        logger.warning(f"Game {game_id} not in today's payload, checking mock...")
        game = next((g for g in MOCK_GAMES if g["game_id"] == game_id), None)
        if not game:
            logger.error(f"Game {game_id} not found anywhere.")
            return {"error": "Game not found"}

    # 3. ML model branch
    if settings.USE_ML_MODEL and model_loaded():
        logger.info(f"Using ML model for {game_id}...")
        try:
            # Fetch historical games for rolling feature computation
            res = supabase_service.supabase_client.table("games").select("*").eq("status", "final").execute()
            games_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

            prediction = predict_game(game, games_df)
            supabase_service.set_cached_prediction(game_id, prediction)
            return prediction
        except Exception as e:
            logger.exception(f"ML prediction failed, falling back to Gemini: {e}")

    # 4. Gemini fallback
    logger.info(f"Calling Gemini for {game_id}")
    try:
        prediction = await gemini_service.generate_prediction(game)
        prediction['source'] = 'gemini'
        supabase_service.set_cached_prediction(game_id, prediction)
        return prediction
    except Exception as e:
        logger.exception(f"Gemini also failed: {e}")
        from app.data.seed_mock import FALLBACK_PREDICTION
        return FALLBACK_PREDICTION