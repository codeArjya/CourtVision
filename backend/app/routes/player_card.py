# backend/app/routes/player_card.py
import logging
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import gemini_service, supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


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
    logger.info(f"Player card: {req.player_name} ({req.player_id}) vs {req.opponent}")

    # 1. Supabase cache check
    cached = supabase_service.get_cached_player_card(req.player_id, req.game_id)
    if cached:
        logger.info(f"Cache hit: player card {req.player_id}:{req.game_id}")
        return cached

    # 2. Gemini generation
    try:
        data = req.dict()
        card = await gemini_service.generate_player_card(data)

        # BUG FIX: Original called set_cached_player_card(req.player_id, req.game_id, card)
        # but the old function signature was set_cached_player_card(data: dict) — 1 arg.
        # This threw a TypeError silently, so player cards were NEVER cached.
        # supabase_service.py has been updated to accept (player_id, game_id, card).
        supabase_service.set_cached_player_card(req.player_id, req.game_id, card)
        return card

    except Exception as e:
        logger.error(f"Gemini player card failed: {e}")
        from app.data.seed_mock import FALLBACK_PLAYER_CARD
        return FALLBACK_PLAYER_CARD