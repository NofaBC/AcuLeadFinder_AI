from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
import os
import sys

# Add the services directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous LeadGen Agent API",
    description="Backend for AcuLeadFinder AI and APLeadFinder AI",
    version="v1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Autonomous LeadGen Agent API",
        "version": "v1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "campaigns": "/campaigns",
            "jobs": "/jobs",
            "drafts": "/drafts",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok", "version": "v1.0", "service": "leadgen-agent"}

# Campaign endpoints
@app.post("/campaigns")
async def create_campaign(request: dict):
    """Create a new campaign from a preset"""
    try:
        preset_name = request.get("preset")
        if not preset_name:
            raise HTTPException(status_code=400, detail="Preset is required")
        
        # Simple mock response for now
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"
        
        return {
            "campaignId": campaign_id,
            "name": f"Campaign from {preset_name}",
            "preset": preset_name,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details"""
    try:
        # Mock response
        return {
            "campaignId": campaign_id,
            "name": "Test Campaign",
            "preset": "acu",
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Job endpoints
@app.post("/jobs")
async def create_job(request: dict):
    """Create a new job"""
    try:
        campaign_id = request.get("campaignId")
        planned_count = request.get("plannedCount", 5)
        
        if not campaign_id:
            raise HTTPException(status_code=400, detail="campaignId is required")
        
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        return {
            "jobId": job_id,
            "campaignId": campaign_id,
            "plannedCount": planned_count,
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    try:
        return {
            "jobId": job_id,
            "status": "running",
            "plannedCount": 5,
            "sentCount": 0,
            "createdAt": "2025-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/jobs/{job_id}/drafts")
async def list_drafts(job_id: str, status: str = "draft"):
    """List drafts for a job"""
    try:
        # Mock drafts
        drafts = [
            {
                "draftId": f"draft_{uuid.uuid4().hex[:8]}",
                "jobId": job_id,
                "subject": "Professional Introduction",
                "body": "Hello, I came across your business...",
                "status": status
            }
        ]
        return drafts
    except Exception as e:
        logger.error(f"Error listing drafts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Draft endpoints
@app.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: str):
    """Approve a draft"""
    try:
        return {"ok": True, "draftId": draft_id, "status": "approved"}
    except Exception as e:
        logger.error(f"Error approving draft: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/drafts/{draft_id}/send")
async def send_draft(draft_id: str):
    """Send a draft"""
    try:
        return {
            "sent": True, 
            "messageId": f"sg_{uuid.uuid4().hex[:8]}", 
            "draftId": draft_id
        }
    except Exception as e:
        logger.error(f"Error sending draft: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Webhook endpoints
@app.post("/webhooks/sendgrid")
async def sendgrid_webhook(request: dict):
    """Receive SendGrid webhook events"""
    try:
        events = request.get("events", [])
        return {"received": True, "count": len(events)}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Preset endpoints
@app.get("/presets")
async def list_presets():
    """List available presets"""
    try:
        return {
            "presets": {
                "acu": "AcuLeadFinder -- Potomac MD",
                "apl": "APLeadFinder -- Default"
            }
        }
    except Exception as e:
        logger.error(f"Error listing presets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/presets/{preset_name}")
async def get_preset(preset_name: str):
    """Get preset configuration"""
    try:
        if preset_name == "acu":
            return {
                "name": "AcuLeadFinder -- Potomac MD",
                "industry": "Acupuncture",
                "geo": {"radius_km": 40, "center_city": "Potomac", "state": "MD"},
                "keywords": ["acupuncture clinic", "pain relief", "stress", "anxiety", "sleep"]
            }
        elif preset_name == "apl":
            return {
                "name": "APLeadFinder -- Default", 
                "industry": "Generic B2B",
                "geo": {"radius_km": 999, "center_city": "", "state": ""},
                "keywords": ["{industry} services", "{city} business services"]
            }
        else:
            raise HTTPException(status_code=404, detail="Preset not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preset: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
