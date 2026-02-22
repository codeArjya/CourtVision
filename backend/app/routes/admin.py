# backend/app/routes/admin.py
from fastapi import APIRouter, BackgroundTasks
from app.ml.evaluate import get_model_status
from app.jobs.ingest_games import run_ingest_games
from app.jobs.retrain import run_retrain

router = APIRouter()

@router.post("/admin/trigger-ingest")
async def trigger_ingest(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingest_games)
    return {"status": "ingest job queued"}

@router.post("/admin/trigger-retrain")
async def trigger_retrain(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_retrain)
    return {"status": "retrain job queued"}

@router.get("/admin/model-status")
async def model_status():
    status = get_model_status()
    return status
