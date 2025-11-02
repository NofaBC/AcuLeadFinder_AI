from fastapi import APIRouter, HTTPException

router = APIRouter()

# Temporary in-memory storage
drafts_db = {}

@router.post("/{draft_id}/approve")
async def approve_draft(draft_id: str):
    if draft_id not in drafts_db:
        drafts_db[draft_id] = {"draftId": draft_id, "status": "draft"}
    
    drafts_db[draft_id]["status"] = "approved"
    return {"ok": True, "draftId": draft_id}

@router.post("/{draft_id}/reject")
async def reject_draft(draft_id: str):
    if draft_id not in drafts_db:
        drafts_db[draft_id] = {"draftId": draft_id, "status": "draft"}
    
    drafts_db[draft_id]["status"] = "rejected"
    return {"ok": True, "draftId": draft_id}

@router.post("/{draft_id}/send")
async def send_draft(draft_id: str):
    if draft_id not in drafts_db:
        drafts_db[draft_id] = {"draftId": draft_id, "status": "draft"}
    
    # Simulate sending
    drafts_db[draft_id]["status"] = "sent"
    drafts_db[draft_id]["messageId"] = f"sg_demo_{draft_id}"
    
    return {
        "sent": True, 
        "messageId": drafts_db[draft_id]["messageId"], 
        "draftId": draft_id
    }
