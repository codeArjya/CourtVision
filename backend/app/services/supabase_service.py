import os
from supabase import create_client, Client
from app.config import settings

supabase_url: str = settings.SUPABASE_URL
supabase_key: str = settings.SUPABASE_SERVICE_KEY
supabase_client: Client | None = None

if supabase_url and supabase_key:
    try:
        supabase_client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")

# Redis mock configuration if URL and TOKEN aren't configured
# Local dictionary to act as fake Redis for caching
_local_redis_cache = {}

async def redis_get(key: str) -> str | None:
    # If no real Redis provided, use local dictionary
    if not settings.UPSTASH_REDIS_REST_URL:
        return _local_redis_cache.get(key)
        
    try:
        import httpx
        url = f"{settings.UPSTASH_REDIS_REST_URL}/get/{key}"
        headers = {"Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}"}
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("result")
    except Exception:
        pass
    return None

async def redis_set(key: str, value: str, ttl: int = 30) -> bool:
    if not settings.UPSTASH_REDIS_REST_URL:
        _local_redis_cache[key] = value
        return True
        
    try:
        import httpx
        url = f"{settings.UPSTASH_REDIS_REST_URL}/set/{key}/{value}/EX/{ttl}"
        headers = {"Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}"}
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, headers=headers)
            return resp.status_code == 200
    except Exception:
        pass
    return False

# ─── PREDICTIONS CRUD ──────────────────────────────────────────────
def get_cached_prediction(game_id: str) -> dict | None:
    if not supabase_client: return None
    try:
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        res = (
            supabase_client
            .table("predictions")
            .select("*")
            .eq("game_id", game_id)
            .gte("generated_at", cutoff)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception:
        return None

def set_cached_prediction(game_id: str, data: dict):
    if not supabase_client: return
    try:
        from datetime import datetime, timezone
        row = {
            "game_id": game_id,
            "winner": data.get("winner"),
            "confidence": data.get("confidence"),
            "score_home": data.get("score_home"),
            "score_away": data.get("score_away"),
            "key_factors": data.get("key_factors", []),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase_client.table("predictions").upsert(row).execute()
    except Exception:
        pass

# ─── PLAYER CARDS CRUD ─────────────────────────────────────────────
def get_cached_player_card(player_id: str, game_id: str) -> dict | None:
    if not supabase_client: return None
    try:
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        res = (
            supabase_client
            .table("player_cards")
            .select("*")
            .eq("player_id", player_id)
            .eq("game_id", game_id)
            .gte("generated_at", cutoff)
            .execute()
        )
        
        # Format mapping back to standard Gemini DTO
        if res.data:
            c = res.data[0]
            return {
                "report": c.get("report"),
                "projection": c.get("projection"),
                "trend": c.get("trend")
            }
        return None
    except Exception:
        return None

def set_cached_player_card(player_id: str, game_id: str, data: dict):
    if not supabase_client: return
    try:
        from datetime import datetime, timezone
        row = {
            "player_id": player_id,
            "game_id": game_id,
            "report": data.get("report"),
            "projection": data.get("projection"),
            "trend": data.get("trend"),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        # Player_cards PK is card_id out-of-box, but upsert with match helps if constraints set
        supabase_client.table("player_cards").insert(row).execute()
    except Exception:
        pass

# ─── TAKES CRUD ──────────────────────────────────────────────────
def get_all_takes() -> list:
    if not supabase_client: return []
    try:
        res = supabase_client.table("media_takes").select("*").execute()
        return res.data
    except Exception:
        return []

def vote_take(take_id: str, vote: str) -> dict | None:
    if not supabase_client: return None
    try:
        col = "agrees" if vote == "agree" else "disagrees"
        # Supabase API does not have an atomic "increment" function natively available
        # via the standard python client without an RPC call.
        # We must fetch the current row, increment, and write.
        res = supabase_client.table("media_takes").select(col).eq("id", take_id).execute()
        if not res.data: return None
        
        current_val = res.data[0][col]
        
        upd = supabase_client.table("media_takes").update({col: current_val + 1}).eq("id", take_id).execute()
        
        if upd.data:
            # Return updated counts (requiring full select again for both cols ideally but cheating by merging)
            res2 = supabase_client.table("media_takes").select("agrees, disagrees").eq("id", take_id).execute()
            return res2.data[0]
        return None
    except Exception:
        return None

def get_take_verdict(take_id: str) -> dict | None:
    if not supabase_client: return None
    try:
        res = supabase_client.table("take_verdicts").select("*").eq("take_id", take_id).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None

def set_take_verdict(take_id: str, data: dict):
    if not supabase_client: return
    try:
        from datetime import datetime, timezone
        row = {
            "take_id": take_id,
            "steelman": data.get("steelman"),
            "challenge": data.get("challenge"),
            "verdict_label": data.get("verdict_label"),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase_client.table("take_verdicts").upsert(row).execute()
    except Exception:
        pass
