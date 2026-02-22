# backend/app/routes/takes.py
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger
from app.services import supabase_service, gemini_service

router = APIRouter()

class VoteRequest(BaseModel):
    take_id: str
    vote: str

class VerdictRequest(BaseModel):
    take_id: str
    take_text: str

@router.get("/takes")
def get_takes():
    logger.info("Fetching takes payload...")
    takes = supabase_service.get_all_takes()
    if takes:
        return takes
    from app.data.seed_mock import MOCK_TAKES
    return MOCK_TAKES

@router.post("/takes/vote")
def vote_take(req: VoteRequest):
    logger.info(f"Vote received for {req.take_id}: {req.vote}")
    updated = supabase_service.vote_take(req.take_id, req.vote)
    if updated: return updated
    return {"take_id": req.take_id, "agrees": 0, "disagrees": 0}

@router.post("/takes/verdict")
async def generate_verdict(req: VerdictRequest):
    logger.info(f"Verdict requested: {req.take_id}")
    cached = supabase_service.get_take_verdict(req.take_id)
    if cached:
        return {
            "steelman": cached.get("steelman", "Supporting argument unavailable."),
            "challenge": cached.get("challenge", "Counter-argument unavailable."),
            "verdict_label": cached.get("verdict_label", "Partially supported")
        }
    
    try:
        verdict = await gemini_service.generate_take_verdict(req.take_text)
        verdict["take_id"] = req.take_id
        supabase_service.set_take_verdict(verdict)
        return verdict
    except Exception as e:
        logger.error(f"Failed to generate explicit verdict: {e}")
        return {
            "steelman": "Supporting argument unavailable.",
            "challenge": "Counter-argument unavailable.",
            "verdict_label": "Partially supported"
        }
