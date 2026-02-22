from fastapi import APIRouter
from app.services import supabase_service
from app.ml.predict import get_model_status
from app.jobs.scheduler import trigger_ingest_job, trigger_retrain_job
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/trigger-ingest")
async def trigger_ingest():
    trigger_ingest_job()
    return {"status": "ingest job queued"}

@router.post("/trigger-retrain")
async def trigger_retrain():
    trigger_retrain_job()
    return {"status": "retrain job queued"}

@router.get("/model-status")
async def model_status():
    status = get_model_status()
    return status
