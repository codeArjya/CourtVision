import json
from loguru import logger
from fastapi import APIRouter
from app.services import supabase_service, nba_service

router = APIRouter()

@router.get("/games")
async def get_games():
    logger.info("Fetching today's games")
    import datetime
    today = datetime.date.today().isoformat()
    redis_key = f"live:games:{today}"

    # 1. Check Redis cache
    cached = await supabase_service.redis_get(redis_key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            pass

    # 2. Fetch live data
    try:
        games = await nba_service.get_today_games()
        # Cache in Redis with short TTL for live updates
        await supabase_service.redis_set(redis_key, json.dumps(games), ttl=30)
        return games
    except Exception as e:
        logger.error(f"Failed to fetch real live games: {e}")
        from app.data.seed_mock import MOCK_GAMES
        return MOCK_GAMES
