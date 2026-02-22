# backend/app/routes/predictions.py
import logging

import pandas as pd
from fastapi import APIRouter

from app.ml.predict import model_loaded, predict_game
from app.services import gemini_service, supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/predictions/{game_id}")
async def get_prediction(game_id: str):
    logger.info(f"Prediction requested for {game_id}")

    # BUG FIX: Removed the zfill(11) normalization — it was padding game IDs
    # with leading zeros (e.g. "18447638" → "00018447638") which never matched
    # any real game_id in the games list or Supabase, causing every prediction
    # to hit the mock fallback.
    from app.config import settings
    use_ml = getattr(settings, "USE_ML_MODEL", False)

    # 1. Check Supabase cache — skip if ML is enabled so stale wrong predictions
    #    don't get served permanently. Cache after fresh prediction instead.
    if not use_ml:
        cached = supabase_service.get_cached_prediction(game_id)
        if cached:
            logger.info(f"Cache hit for {game_id}")
            return cached

    # 2. Fetch today's games
    from app.services.nba_service import get_today_games
    games = await get_today_games()
    game = next((g for g in games if g["game_id"] == game_id), None)

    if not game:
        from app.data.seed_mock import MOCK_GAMES
        game = next((g for g in MOCK_GAMES if g["game_id"] == game_id), None)
        if not game:
            logger.error(f"Game {game_id} not found.")
            return {"error": "Game not found"}

    # 3. ML model branch
    if use_ml and model_loaded():
        logger.info(f"Using ML model for {game_id}")
        try:
            # Fetch historical games — these must have NBA official team IDs
            # (1610612XXX format) to match what features.py looks up.
            # nba_service now translates BDL IDs → NBA IDs so today's games
            # also use the correct format for consistent lookups.
            res = (
                supabase_service.supabase_client
                .table("games")
                .select("*")
                .eq("status", "final")
                .execute()
            )
            games_df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

            if games_df.empty:
                logger.warning(
                    "No historical game data in Supabase — run bootstrap scripts. "
                    "Falling back to Groq."
                )
            else:
                logger.info(f"Historical games loaded: {len(games_df)} rows, "
                            f"sample IDs: {games_df['home_team_id'].unique()[:3].tolist()}")

            prediction = predict_game(game, games_df)
            supabase_service.set_cached_prediction(game_id, prediction)
            return prediction

        except Exception as e:
            logger.exception(f"ML prediction failed, falling back to Groq: {e}")

    # 4. Groq fallback
    logger.info(f"Calling Groq for {game_id}")
    try:
        prediction = await gemini_service.generate_prediction(game)
        prediction["source"] = "groq"
        supabase_service.set_cached_prediction(game_id, prediction)
        return prediction
    except Exception as e:
        logger.exception(f"Groq prediction also failed: {e}")
        from app.data.seed_mock import FALLBACK_PREDICTION
        return FALLBACK_PREDICTION