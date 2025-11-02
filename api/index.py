from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging
from typing import List, Optional

# Import all components
from services.agent_runner.routes.health import router as health_router
from services.agent_runner.routes.jobs import router as jobs_router
from services.agent_runner.routes.drafts import router as drafts_router
from services.agent_runner.routes.send import router as send_router

from services.agent_runner.memory.schemas import Campaign, Job, CreateCampaignRequest, CreateJobRequest
from services.agent_runner.memory.firestore_store import firestore_store
from services.agent_runner.config.preset_loader import preset_loader
from services.agent_runner.agents.leadgen import create_leadgen_agent

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

# Include routers
app.include_router(health_router)
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(drafts_router, prefix="/drafts", tags=["drafts"])
app.include_router(send_router, prefix="/webhooks", tags=["webhooks"])

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
@app.post("/campaigns", response_model=dict)
async def create_campaign(request: CreateCampaignRequest):
    """Create a new campaign from a preset"""
    try:
        # Load preset configuration
        preset_config = preset_loader.load_preset(request.preset)
        if not preset_config:
            raise HTTPException(status_code=400, detail=f"Preset not found: {request.preset}")
        
        # Merge with overrides
        campaign_config = preset_loader.merge_preset_with_overrides(
            request.preset, 
            {
                "model": request.model,
                "send_cap_per_run": request.sendCapPerRun
            }
        )
        
        # Create campaign ID
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"
        
        # Create campaign object
        campaign = Campaign(
            campaignId=campaign_id,
            name=campaign_config["name"],
            preset=request.preset,
            industry=campaign_config["industry"],
            geo=campaign_config["geo"],
            keywords=campaign_config["keywords"],
            model=campaign_config["model"],
            sendCapPerRun=campaign_config["send_cap_per_run"],
            dailySendCap=campaign_config["daily_send_cap"]
        )
        
        # Save to Firestore
        success = await firestore_store.create_campaign(campaign)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create campaign")
        
        logger.info(f"Created campaign: {campaign_id} with preset: {request.preset}")
        
        return {
            "campaignId": campaign_id,
            "name": campaign.name,
            "preset": campaign.preset,
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Get campaign details"""
    try:
        campaign = await firestore_store.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return campaign.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/campaigns")
async def list_campaigns():
    """List all campaigns"""
    try:
        # Note: This would need a proper Firestore query in production
        # For now, return empty list - implementation would be in M2
        return {"campaigns": []}
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced job creation with agent integration
@app.post("/jobs", response_model=dict)
async def create_job(request: CreateJobRequest, background_tasks: BackgroundTasks):
    """Create a new job and start the autonomous agent"""
    try:
        # Verify campaign exists
        campaign = await firestore_store.get_campaign(request.campaignId)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Create job ID
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        # Create job object
        job = Job(
            jobId=job_id,
            campaignId=request.campaignId,
            plannedCount=request.plannedCount,
            sentCount=0,
            costUSD=0.0,
            status="queued"
        )
        
        # Save to Firestore
        success = await firestore_store.create_job(job)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        # Load campaign configuration
        preset_config = preset_loader.load_preset(campaign.preset)
        if not preset_config:
            raise HTTPException(status_code=500, detail="Failed to load campaign configuration")
        
        # Start agent in background
        background_tasks.add_task(
            run_agent_for_job,
            job_id,
            campaign.dict(),
            preset_config,
            request.plannedCount
        )
        
        logger.info(f"Created job: {job_id} for campaign: {request.campaignId}")
        
        return {
            "jobId": job_id,
            "campaignId": request.campaignId,
            "plannedCount": request.plannedCount,
            "status": "queued"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def run_agent_for_job(job_id: str, campaign_data: dict, preset_config: dict, planned_count: int):
    """Run the autonomous agent for a job in the background"""
    try:
        logger.info(f"Starting agent for job: {job_id}")
        
        # Update job status to running
        await firestore_store.update_job_status(job_id, "running")
        
        # Create and run the agent
        agent = await create_leadgen_agent(job_id, preset_config)
        job_data = {"plannedCount": planned_count}
        
        result = await agent.run_agent_loop(job_data)
        
        if result["status"] == "completed":
            # Update job status to done
            await firestore_store.update_job_status(
                job_id, 
                "done", 
                sent_count=result.get("drafts_created", 0)
            )
            logger.info(f"Agent completed job: {job_id}. Drafts created: {result.get('drafts_created', 0)}")
        else:
            # Update job status to failed
            await firestore_store.update_job_status(job_id, "failed")
            logger.error(f"Agent failed for job: {job_id}. Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in agent execution for job {job_id}: {e}")
        await firestore_store.update_job_status(job_id, "failed")

# Additional utility endpoints
@app.get("/presets")
async def list_presets():
    """List available presets"""
    try:
        presets = preset_loader.get_available_presets()
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
