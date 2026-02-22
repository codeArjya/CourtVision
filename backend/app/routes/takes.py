# backend/app/routes/takes.py
import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import gemini_service, supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


class VoteRequest(BaseModel):
    take_id: str
    vote: str


class VerdictRequest(BaseModel):
    take_id: str
    take_text: str


# BUG FIX: get_takes() and vote_take() were `def` (sync) in an async FastAPI app.
# FastAPI runs sync route handlers in a threadpool executor, which is fine for simple
# cases but means they block a worker thread for the entire Supabase round-trip.
# More critically, if supabase_client uses any async internals, calling from a sync
# context will deadlock. Changed to `async def` for consistency and safety.
@router.get("/takes")
async def get_takes():
    logger.info("Fetching takes...")
    takes = supabase_service.get_all_takes()
    if takes:
        return takes
    from app.data.seed_mock import MOCK_TAKES
    return MOCK_TAKES


@router.post("/takes/vote")
async def vote_take(req: VoteRequest):
    logger.info(f"Vote: {req.take_id} → {req.vote}")
    if req.vote not in ("agree", "disagree"):
        return {"error": "vote must be 'agree' or 'disagree'"}
    updated = supabase_service.vote_take(req.take_id, req.vote)
    if updated:
        return updated
    return {"take_id": req.take_id, "agrees": 0, "disagrees": 0}


@router.post("/takes/verdict")
async def generate_verdict(req: VerdictRequest):
    logger.info(f"Verdict requested: {req.take_id}")

    cached = supabase_service.get_take_verdict(req.take_id)
    if cached:
        return {
            "steelman": cached.get("steelman", "Supporting argument unavailable."),
            "challenge": cached.get("challenge", "Counter-argument unavailable."),
            "verdict_label": cached.get("verdict_label", "Partially supported"),
        }

    try:
        verdict = await gemini_service.generate_take_verdict(req.take_text)
        verdict["take_id"] = req.take_id
        supabase_service.set_take_verdict(verdict)
        return verdict
    except Exception as e:
        logger.error(f"Failed to generate verdict: {e}")
        return {
            "steelman": "Supporting argument unavailable.",
            "challenge": "Counter-argument unavailable.",
            "verdict_label": "Partially supported",
        }