from fastapi import APIRouter, HTTPException
from typing import List, Optional

router = APIRouter()

# Temporary in-memory storage for development
jobs_db = {}
drafts_db = {}

@router.post("")
async def create_job(payload: dict):
    job_id = f"job_{len(jobs_db) + 1}"
    jobs_db[job_id] = {
        "jobId": job_id,
        "campaignId": payload.get("campaignId"),
        "plannedCount": payload.get("plannedCount", 0),
        "status": "queued",
        "createdAt": "2025-01-01T00:00:00Z",  # TODO: Use actual timestamp
        "sentCount": 0,
        "costUSD": 0.0
    }
    return {"jobId": job_id}

@router.get("/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

@router.get("/{job_id}/drafts")
async def list_drafts(job_id: str, status: Optional[str] = "draft"):
    # Filter drafts by job_id and optional status
    job_drafts = [
        draft for draft in drafts_db.values() 
        if draft.get("jobId") == job_id and (status is None or draft.get("status") == status)
    ]
    return job_drafts
