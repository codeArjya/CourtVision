from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger
from app.services import supabase_service, gemini_service

router = APIRouter(prefix="/takes", tags=["Takes"])

class VoteRequest(BaseModel):
    take_id: str
    vote: str

class VerdictRequest(BaseModel):
    take_id: str
    take_text: str

@router.get("/")
def get_takes():
    logger.info("Fetching takes payload...")
    takes = supabase_service.get_all_takes()
    if takes:
        return takes
    from app.data.seed_mock import MOCK_TAKES
    return MOCK_TAKES

@router.post("/vote")
def vote_take(req: VoteRequest):
    logger.info(f"Vote received for {req.take_id}: {req.vote}")
    updated = supabase_service.vote_take(req.take_id, req.vote)
    if updated: return updated
    return {"status": "error"}

@router.post("/verdict")
async def generate_verdict(req: VerdictRequest):
    logger.info(f"Verdict requested: {req.take_id}")
    cached = supabase_service.get_take_verdict(req.take_id)
    if cached: return cached
    
    try:
        verdict = await gemini_service.generate_take_verdict(req.take_text)
        supabase_service.set_take_verdict(req.take_id, verdict)
        return verdict
    except Exception as e:
        logger.error(f"Failed to generate explicit verdict: {e}")
        return {
            "steelman": "Could not contact specific AI service for support",
            "challenge": "Could not contact specific AI service for detraction",
            "verdict_label": "Partially supported"
        }
