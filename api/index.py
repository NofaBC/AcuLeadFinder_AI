from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
import os
import sys
import json
import asyncio
from datetime import datetime

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

# In-memory storage for development (replace with Firestore later)
campaigns_db = {}
jobs_db = {}
drafts_db = {}

class PresetLoader:
    def __init__(self):
        self.presets_dir = os.path.join(os.path.dirname(__file__), "..", "services", "agent-runner", "config", "presets")
    
    def load_preset(self, preset_name: str):
        """Load preset configuration"""
        try:
            preset_file = os.path.join(self.presets_dir, f"{preset_name}.json")
            if os.path.exists(preset_file):
                with open(preset_file, 'r') as f:
                    return json.load(f)
            else:
                logger.error(f"Preset file not found: {preset_file}")
                return None
        except Exception as e:
            logger.error(f"Error loading preset {preset_name}: {e}")
            return None

preset_loader = PresetLoader()

class LeadGenAgent:
    """Simplified agent for M1"""
    def __init__(self, job_id: str, campaign_config: dict):
        self.job_id = job_id
        self.campaign_config = campaign_config
    
    async def run_agent_loop(self, planned_count: int):
        """Run the agent to generate leads and drafts"""
        try:
            logger.info(f"Starting agent for job {self.job_id}, planned: {planned_count}")
            
            # Simulate lead generation and drafting
            drafts_created = min(planned_count, 5)  # Max 5 for demo
            
            for i in range(drafts_created):
                draft_id = f"draft_{uuid.uuid4().hex[:8]}"
                drafts_db[draft_id] = {
                    "draftId": draft_id,
                    "jobId": self.job_id,
                    "leadId": f"lead_{i+1}",
                    "subject": f"Introduction - {self.campaign_config.get('industry', 'Business')}",
                    "body": self._generate_email_body(i),
                    "status": "draft",
                    "createdAt": datetime.utcnow().isoformat()
                }
                logger.info(f"Created draft {draft_id} for job {self.job_id}")
            
            return {
                "status": "completed", 
                "drafts_created": drafts_created,
                "job_id": self.job_id
            }
            
        except Exception as e:
            logger.error(f"Agent error for job {self.job_id}: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _generate_email_body(self, index: int) -> str:
        """Generate email body based on campaign configuration"""
        industry = self.campaign_config.get('industry', '')
        from_name = self.campaign_config.get('from_name', 'NOFA BC')
        
        if industry.lower() == 'acupuncture':
            return f"""Hello,

I hope this message finds you well. I'm reaching out from {from_name}, serving the community with traditional Chinese medicine approaches.

Many of our patients find significant relief from chronic pain, stress, and sleep issues through acupuncture.

We're currently offering a special introductory offer for healthcare professionals.

Would you be interested in learning more?

Best regards,
{from_name}

If you'd prefer not to hear from us again, reply with 'unsubscribe'."""
        else:
            return f"""Hello,

I came across your business and was impressed by your work in {industry}.

At {from_name}, we help businesses optimize their operations and accelerate growth.

I'd love to explore if there might be synergy between our organizations.

Would you have 15 minutes for a brief chat next week?

Best regards,
{from_name}

If you'd prefer not to hear from us again, reply with 'unsubscribe'."""

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
        
        # Load preset configuration
        preset_config = preset_loader.load_preset(preset_name)
        if not preset_config:
            raise HTTPException(status_code=400, detail=f"Preset not found: {preset_name}")
        
        # Create campaign
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"
        campaigns_db[campaign_id] = {
            "campaignId": campaign_id,
            "name": preset_config.get("name", f"Campaign {preset_name}"),
            "preset": preset_name,
            "industry": preset_config.get("industry", ""),
            "config": preset_config,
            "createdAt": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Created campaign: {campaign_id} from preset: {preset_name}")
        
        return {
            "campaignId": campaign_id,
            "name": preset_config.get("name"),
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
        campaign = campaigns_db.get(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Job endpoints
@app.post("/jobs")
async def create_job(request: dict, background_tasks: BackgroundTasks):
    """Create a new job and start the autonomous agent"""
    try:
        campaign_id = request.get("campaignId")
        planned_count = request.get("plannedCount", 5)
        
        if not campaign_id:
            raise HTTPException(status_code=400, detail="campaignId is required")
        
        # Verify campaign exists
        campaign = campaigns_db.get(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Create job
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        jobs_db[job_id] = {
            "jobId": job_id,
            "campaignId": campaign_id,
            "plannedCount": planned_count,
            "sentCount": 0,
            "status": "running",
            "createdAt": datetime.utcnow().isoformat()
        }
        
        # Start agent in background
        agent = LeadGenAgent(job_id, campaign["config"])
        background_tasks.add_task(run_agent, agent, planned_count, job_id)
        
        logger.info(f"Created job: {job_id} for campaign: {campaign_id}")
        
        return {
            "jobId": job_id,
            "campaignId": campaign_id,
            "plannedCount": planned_count,
            "status": "running"
        }
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def run_agent(agent: LeadGenAgent, planned_count: int, job_id: str):
    """Run agent in background"""
    try:
        result = await agent.run_agent_loop(planned_count)
        if result["status"] == "completed":
            jobs_db[job_id]["status"] = "completed"
            jobs_db[job_id]["sentCount"] = result["drafts_created"]
            logger.info(f"Job {job_id} completed with {result['drafts_created']} drafts")
        else:
            jobs_db[job_id]["status"] = "failed"
            logger.error(f"Job {job_id} failed: {result.get('error')}")
    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        logger.error(f"Agent crashed for job {job_id}: {e}")

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    try:
        job = jobs_db.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/jobs/{job_id}/drafts")
async def list_drafts(job_id: str, status: str = "draft"):
    """List drafts for a job"""
    try:
        job_drafts = [
            draft for draft in drafts_db.values() 
            if draft["jobId"] == job_id and (not status or draft["status"] == status)
        ]
        return job_drafts
    except Exception as e:
        logger.error(f"Error listing drafts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Draft endpoints
@app.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: str):
    """Approve a draft"""
    try:
        draft = drafts_db.get(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        draft["status"] = "approved"
        draft["updatedAt"] = datetime.utcnow().isoformat()
        
        return {"ok": True, "draftId": draft_id, "status": "approved"}
    except Exception as e:
        logger.error(f"Error approving draft: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/drafts/{draft_id}/send")
async def send_draft(draft_id: str):
    """Send a draft"""
    try:
        draft = drafts_db.get(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        # Simulate sending
        draft["status"] = "sent"
        draft["messageId"] = f"sg_{uuid.uuid4().hex[:8]}"
        draft["updatedAt"] = datetime.utcnow().isoformat()
        
        # Update job sent count
        job_id = draft["jobId"]
        if job_id in jobs_db:
            jobs_db[job_id]["sentCount"] = jobs_db[job_id].get("sentCount", 0) + 1
        
        return {
            "sent": True, 
            "messageId": draft["messageId"], 
            "draftId": draft_id
        }
    except Exception as e:
        logger.error(f"Error sending draft: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Preset endpoints
@app.get("/presets")
async def list_presets():
    """List available presets"""
    try:
        presets = {}
        for preset_file in ["acu", "apl"]:
            config = preset_loader.load_preset(preset_file)
            if config:
                presets[preset_file] = config.get("name", preset_file)
        
        return {"presets": presets}
    except Exception as e:
        logger.error(f"Error listing presets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/presets/{preset_name}")
async def get_preset(preset_name: str):
    """Get preset configuration"""
    try:
        preset = preset_loader.load_preset(preset_name)
        if not preset:
            raise HTTPException(status_code=404, detail="Preset not found")
        return preset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preset: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
