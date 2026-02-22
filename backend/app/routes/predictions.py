from loguru import logger
from fastapi import APIRouter
from app.services import supabase_service, nba_service, gemini_service
from app.ml.predict import predict_game

router = APIRouter()

@router.get("/predictions/{game_id}")
async def get_prediction(game_id: str):
    logger.info(f"Prediction requested for {game_id}")
    
    # 1. Check Supabase Cache
    cached = supabase_service.get_cached_prediction(game_id)
    if cached:
        logger.info(f"Supabase cache hit: predict:{game_id}")
        return cached
        
    # 2. Need Game Data (we must fetch if not provided in call)
    from app.services.nba_service import get_today_games
    games = await get_today_games()
    
    game = next((g for g in games if g["game_id"] == game_id), None)
    if not game:
        from app.data.seed_mock import MOCK_GAMES
        logger.warning(f"Game {game_id} not found in today's payload, checking mock...")
        game = next((g for g in MOCK_GAMES if g["game_id"] == game_id), None)
        if not game:
            logger.error("Could not find game info anywhere. Giving up.")
            return {"error": "Game not found"}
            
    # 3. Model branching
    from app.config import settings
    from app.ml.predict import model_loaded
    
    if settings.USE_ML_MODEL and model_loaded():
        logger.info(f"Using ML model pipeline for {game_id}...")
        try:
            # Requires fetching rolling stats for both teams
            # We mock the dictionary for now for seamless API translation
            home_stats = {"off_rtg_l10": 115.0, "def_rtg_l10": 105.0, "pace_l10": 102.1} 
            away_stats = {"off_rtg_l10": 110.0, "def_rtg_l10": 112.0, "pace_l10": 99.5}
            
            prediction = predict_game(game, home_stats, away_stats)
            supabase_service.set_cached_prediction(game_id, prediction)
            return prediction
        except Exception as e:
            logger.exception(f"ML Prediction failed: {e}. Falling back to Gemini.")
            
    # 4. Fallback to Gemini
    logger.info(f"Calling Gemini for prediction: {game_id}")
    try:
        prediction = await gemini_service.generate_prediction(game)
        # Ensure 'source' matches UI specification requirements
        prediction['source'] = 'gemini'
        supabase_service.set_cached_prediction(game_id, prediction)
        return prediction
    except Exception as e:
        logger.exception(f"Gemini generation failed: {e}")
        from app.data.seed_mock import FALLBACK_PREDICTION
        return FALLBACK_PREDICTION
