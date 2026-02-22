# backend/app/services/supabase_service.py
import logging
from datetime import datetime, timedelta, timezone

import httpx
from supabase import Client, create_client

from app.config import settings

logger = logging.getLogger(__name__)

supabase_url: str = settings.SUPABASE_URL
supabase_key: str = settings.SUPABASE_SERVICE_KEY
supabase_client: Client | None = None

if supabase_url and supabase_key:
    try:
        supabase_client = create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")

_local_redis_cache: dict = {}


async def redis_get(key: str) -> str | None:
    if not settings.UPSTASH_REDIS_REST_URL:
        return _local_redis_cache.get(key)
    try:
        url = f"{settings.UPSTASH_REDIS_REST_URL}/get/{key}"
        headers = {"Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}"}
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json().get("result")
    except Exception as e:
        logger.warning(f"[redis_get] failed for key={key}: {e}")
    return None


async def redis_set(key: str, value: str, ttl: int = 30) -> bool:
    if not settings.UPSTASH_REDIS_REST_URL:
        _local_redis_cache[key] = value
        return True
    try:
        # BUG FIX: Original used a GET request with the JSON value embedded in the URL path:
        #   /set/{key}/{value}/EX/{ttl}
        # JSON values contain spaces, quotes, and braces — all of which break URL parsing
        # even when encoded, causing Upstash to reject or misparse the request.
        # Fix: Use the Upstash pipeline POST endpoint with a proper JSON body.
        url = f"{settings.UPSTASH_REDIS_REST_URL}/pipeline"
        headers = {
            "Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}",
            "Content-Type": "application/json",
        }
        # Upstash pipeline format: array of [command, arg1, arg2, ...]
        body = [["SET", key, value, "EX", str(ttl)]]
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            return resp.status_code == 200
    except Exception as e:
        logger.warning(f"[redis_set] failed for key={key}: {e}")
    return False


# ─── PREDICTIONS CRUD ──────────────────────────────────────────────
def get_cached_prediction(game_id: str) -> dict | None:
    if not supabase_client:
        return None
    try:
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
    except Exception as e:
        logger.error(f"[get_cached_prediction] {e}")
        return None


def set_cached_prediction(game_id: str, data: dict):
    if not supabase_client:
        return
    try:
        supabase_client.table("predictions").upsert({**data, "game_id": game_id}).execute()
    except Exception as e:
        logger.error(f"[set_cached_prediction] {e}")


# ─── PLAYER CARDS CRUD ─────────────────────────────────────────────
def get_cached_player_card(player_id: str, game_id: str) -> dict | None:
    if not supabase_client:
        return None
    try:
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
                "trend": c.get("trend"),
            }
        return None
    except Exception as e:
        logger.error(f"[get_cached_player_card] {e}")
        return None


def set_cached_player_card(player_id: str, game_id: str, card: dict):
    # BUG FIX: Original signature was set_cached_player_card(data: dict) — one arg.
    # player_card.py called it with THREE args: (player_id, game_id, card).
    # This caused a TypeError on every card generation, so cards were never cached
    # and Gemini was called redundantly on every single player click.
    if not supabase_client:
        return
    try:
        supabase_client.table("player_cards").upsert(
            {
                "player_id": player_id,
                "game_id": game_id,
                "report": card.get("report"),
                "projection": card.get("projection"),
                "trend": card.get("trend"),
            }
        ).execute()
    except Exception as e:
        logger.error(f"[set_cached_player_card] {e}")


# ─── TAKES CRUD ──────────────────────────────────────────────────
def get_all_takes() -> list:
    if not supabase_client:
        return []
    try:
        res = supabase_client.table("media_takes").select("*").execute()
        return res.data
    except Exception as e:
        logger.error(f"[get_all_takes] {e}")
        return []


def vote_take(take_id: str, vote: str) -> dict | None:
    if not supabase_client:
        return None
    try:
        col = "agrees" if vote == "agree" else "disagrees"
        res = supabase_client.table("media_takes").select(col).eq("id", take_id).execute()
        if not res.data:
            return None

        current_val = res.data[0][col]
        upd = (
            supabase_client
            .table("media_takes")
            .update({col: current_val + 1})
            .eq("id", take_id)
            .execute()
        )
        if upd.data:
            res2 = (
                supabase_client
                .table("media_takes")
                .select("id as take_id, agrees, disagrees")
                .eq("id", take_id)
                .execute()
            )
            if res2.data:
                return res2.data[0]
        return None
    except Exception as e:
        logger.error(f"[vote_take] {e}")
        return None


def get_take_verdict(take_id: str) -> dict | None:
    if not supabase_client:
        return None
    try:
        res = supabase_client.table("take_verdicts").select("*").eq("take_id", take_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.error(f"[get_take_verdict] {e}")
        return None


def set_take_verdict(data: dict):
    if not supabase_client:
        return
    try:
        supabase_client.table("take_verdicts").upsert(data).execute()
    except Exception as e:
        logger.error(f"[set_take_verdict] {e}")