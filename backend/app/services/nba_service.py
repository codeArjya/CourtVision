# backend/app/services/nba_service.py

import httpx
from datetime import date
from app.services.supabase_service import supabase_client
from app.data.seed_mock import MOCK_GAMES
from app.services.supabase_service import redis_get, redis_set

BALLDONTLIE_BASE = "https://api.balldontlie.io/v1"

async def get_today_games() -> list:
    today = date.today().isoformat()
    
    # 1. Try Redis cache
    cached = await redis_get(f"live:games:{today}")
    if cached:
        import json
        try:
            return json.loads(cached)
        except Exception:
            pass

    # 2. Try balldontlie
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{BALLDONTLIE_BASE}/games",
                params={"dates[]": today}
            )
            resp.raise_for_status()
            raw = resp.json().get("data", [])
            games = [_transform_balldontlie_game(g) for g in raw]
            if games:
                # Upsert to Supabase
                for g in games:
                    supabase_client.table("games").upsert(g).execute()
                
                # Cache in redis
                import json
                await redis_set(f"live:games:{today}", json.dumps(games), 30)
                
                return games
    except Exception:
        pass
    
    # 3. Try Supabase
    try:
        result = supabase_client.table("games").select("*").eq("game_date", today).execute()
        if result.data:
            return result.data
    except Exception:
        pass
    
    # 4. Return mock
    return MOCK_GAMES

def _transform_balldontlie_game(raw: dict) -> dict:
    return {
        "game_id": str(raw["id"]),
        "game_date": raw["date"][:10],
        "status": _map_status(raw.get("status", "")),
        "quarter": raw.get("period"),
        "clock": raw.get("time"),
        "home_team_id": str(raw["home_team"]["id"]),
        "home_team_name": raw["home_team"]["full_name"],
        "home_team_abbr": raw["home_team"]["abbreviation"],
        "home_score": raw.get("home_team_score"),
        "away_team_id": str(raw["visitor_team"]["id"]),
        "away_team_name": raw["visitor_team"]["full_name"],
        "away_team_abbr": raw["visitor_team"]["abbreviation"],
        "away_score": raw.get("visitor_team_score"),
        "tipoff_time": None
    }

def _map_status(s: str) -> str:
    if "Final" in s: return "final"
    if s.isdigit() or "Qtr" in s or "Half" in s: return "live"
    return "upcoming"
