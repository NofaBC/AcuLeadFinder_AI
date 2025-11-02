from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/sendgrid")
async def sendgrid_webhook(request: Request):
    events = await request.json()
    
    # TODO: Process SendGrid events and update draft statuses
    # For now, just acknowledge receipt
    event_count = len(events) if isinstance(events, list) else 1
    
    return {"received": True, "count": event_count}
