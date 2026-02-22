from loguru import logger
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.services import supabase_service, gemini_service

router = APIRouter()

class SeasonAvg(BaseModel):
    pts: float
    reb: float
    ast: float
    
class PlayerCardRequest(BaseModel):
    player_id: str
    player_name: str
    season_avg: SeasonAvg
    last5: List[float]
    opponent: str
    game_id: str

@router.post("/player-card")
async def generate_player_card(req: PlayerCardRequest):
    logger.info(f"Player card requested for {req.player_name} ({req.player_id}) vs {req.opponent}")
    
    # 1. Supabase cache check
    cached = supabase_service.get_cached_player_card(req.player_id, req.game_id)
    if cached:
        logger.info(f"Cache hit: player card {req.player_id}:{req.game_id}")
        return cached
        
    # 2. Gemini generation
    try:
        data = req.dict()
        card = await gemini_service.generate_player_card(data)
        
        # 3. Cache and return
        supabase_service.set_cached_player_card(req.player_id, req.game_id, card)
        return card
        
    except Exception as e:
        logger.error(f"Gemini player card failed: {e}")
        from app.data.seed_mock import FALLBACK_PLAYER_CARD
        return FALLBACK_PLAYER_CARD
