# backend/app/services/supabase_service.py
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

_local_redis_cache = {}

async def redis_get(key: str) -> str | None:
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
            .gte("created_at", cutoff)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception:
        return None

def set_cached_prediction(data: dict):
    if not supabase_client: return
    try:
        supabase_client.table("predictions").upsert(data).execute()
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
            .gte("created_at", cutoff)
            .execute()
        )
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

def set_cached_player_card(data: dict):
    if not supabase_client: return
    try:
        supabase_client.table("player_cards").upsert(data).execute()
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
        res = supabase_client.table("media_takes").select(col).eq("id", take_id).execute()
        if not res.data: return None
        
        current_val = res.data[0][col]
        upd = supabase_client.table("media_takes").update({col: current_val + 1}).eq("id", take_id).execute()
        
        if upd.data:
            res2 = supabase_client.table("media_takes").select("id as take_id, agrees, disagrees").eq("id", take_id).execute()
            if res2.data:
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

def set_take_verdict(data: dict):
    if not supabase_client: return
    try:
        supabase_client.table("take_verdicts").upsert(data).execute()
    except Exception:
        pass
