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
    title="Seekan-LG Autonomous LeadGen Agent",
    description="Backend for Seekan-LG Autonomous Lead Generation System", 
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
business_profiles_db = {}

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

class BusinessAnalyzer:
    def __init__(self):
        pass
    
    async def analyze_website(self, website_url: str):
        """Mock website analysis - in production, this would use real AI analysis"""
        try:
            # Simulate AI analysis
            await asyncio.sleep(2)
            
            # Mock business profile based on URL pattern
            if "consulting" in website_url.lower():
                return {
                    "company_name": "Business Consulting Pro",
                    "industry": "Business Consulting",
                    "services": ["Strategy Consulting", "Business Planning", "Process Optimization"],
                    "target_customers": "Small to medium businesses",
                    "geography": "National",
                    "value_proposition": "Helping businesses grow through strategic planning and execution",
                    "offers": ["Free initial consultation", "Customized business plans"],
                    "source": "ai_analysis",
                    "website": website_url
                }
            elif "marketing" in website_url.lower():
                return {
                    "company_name": "Digital Marketing Solutions",
                    "industry": "Digital Marketing",
                    "services": ["SEO", "Social Media Marketing", "Content Creation"],
                    "target_customers": "Startups and established businesses",
                    "geography": "Global",
                    "value_proposition": "Data-driven marketing strategies that deliver results",
                    "offers": ["Free marketing audit", "30-day trial"],
                    "source": "ai_analysis", 
                    "website": website_url
                }
            else:
                return {
                    "company_name": "Professional Services Inc",
                    "industry": "Professional Services",
                    "services": ["Business Services", "Consulting", "Support"],
                    "target_customers": "Various businesses",
                    "geography": "Multiple regions",
                    "value_proposition": "Quality services and reliable support",
                    "offers": ["Introductory discount", "Free assessment"],
                    "source": "ai_analysis",
                    "website": website_url
                }
                
        except Exception as e:
            logger.error(f"Error analyzing website {website_url}: {e}")
            return {"error": str(e)}

business_analyzer = BusinessAnalyzer()

class SeekanLGAgent:
    """Seekan-LG Autonomous Lead Generation Agent"""
    def __init__(self, job_id: str, campaign_config: dict):
        self.job_id = job_id
        self.campaign_config = campaign_config
    
    async def run_agent_loop(self, planned_count: int):
        """Run the Seekan-LG agent to generate leads and drafts"""
        try:
            logger.info(f"Seekan-LG starting for job {self.job_id}, planned: {planned_count}")
            
            # Simulate lead generation and drafting
            drafts_created = min(planned_count, 5)  # Max 5 for demo
            
            for i in range(drafts_created):
                draft_id = f"draft_{uuid.uuid4().hex[:8]}"
                drafts_db[draft_id] = {
                    "draftId": draft_id,
                    "jobId": self.job_id,
                    "leadId": f"lead_{i+1}",
                    "subject": f"Seekan-LG: Introduction - {self.campaign_config.get('industry', 'Business')}",
                    "body": self._generate_email_body(i),
                    "status": "draft",
                    "createdAt": datetime.utcnow().isoformat(),
                    "agent": "Seekan-LG"
                }
                logger.info(f"Seekan-LG created draft {draft_id} for job {self.job_id}")
            
            return {
                "status": "completed", 
                "drafts_created": drafts_created,
                "job_id": self.job_id,
                "agent": "Seekan-LG"
            }
            
        except Exception as e:
            logger.error(f"Seekan-LG agent error for job {self.job_id}: {e}")
            return {"status": "failed", "error": str(e), "agent": "Seekan-LG"}
    
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

---
Generated by Seekan-LG Autonomous Lead Generation Agent
If you'd prefer not to hear from us again, reply with 'unsubscribe'."""
        else:
            return f"""Hello,

I came across your business and was impressed by your work in {industry}.

At {from_name}, we help businesses optimize their operations and accelerate growth.

I'd love to explore if there might be synergy between our organizations.

Would you have 15 minutes for a brief chat next week?

Best regards,
{from_name}

---
Generated by Seekan-LG Autonomous Lead Generation Agent
If you'd prefer not to hear from us again, reply with 'unsubscribe'."""

class ContextAwareLeadGenAgent:
    """Context-aware version of Seekan-LG Agent"""
    def __init__(self, job_id: str, campaign_config: dict, business_profile: dict):
        self.job_id = job_id
        self.campaign_config = campaign_config
        self.business_profile = business_profile
    
    async def run_agent_loop(self, planned_count: int):
        """Run context-aware agent loop"""
        try:
            logger.info(f"Context-aware Seekan-LG starting for job {self.job_id}")
            
            # Use business profile for context-aware generation
            company_name = self.business_profile.get('company_name', 'Our Company')
            services = self.business_profile.get('services', ['services'])
            industry = self.business_profile.get('industry', 'Business')
            
            drafts_created = min(planned_count, 5)
            
            for i in range(drafts_created):
                draft_id = f"draft_{uuid.uuid4().hex[:8]}"
                drafts_db[draft_id] = {
                    "draftId": draft_id,
                    "jobId": self.job_id,
                    "leadId": f"lead_{i+1}",
                    "subject": f"Introduction - {company_name} {services[0] if services else 'Services'}",
                    "body": self._generate_context_aware_email(company_name, services, industry),
                    "status": "draft",
                    "createdAt": datetime.utcnow().isoformat(),
                    "agent": "Seekan-LG",
                    "context_aware": True,
                    "business_profile_used": company_name
                }
                logger.info(f"Context-aware draft {draft_id} created for {company_name}")
            
            return {
                "status": "completed",
                "drafts_created": drafts_created,
                "job_id": self.job_id,
                "agent": "Seekan-LG",
                "business_context": company_name
            }
            
        except Exception as e:
            logger.error(f"Context-aware agent error: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _generate_context_aware_email(self, company_name: str, services: list, industry: str) -> str:
        """Generate context-aware email using business profile"""
        services_text = ", ".join(services[:-1]) + f" and {services[-1]}" if len(services) > 1 else services[0] if services else "our services"
        
        return f"""Hello,

I came across your business and was impressed by your work in your industry.

At {company_name}, we specialize in {services_text} for the {industry} sector. We help businesses like yours achieve better results through our specialized expertise.

Many of our clients have seen significant improvements in their operations and growth after working with us.

Would you be open to a brief 15-minute chat next week to explore how we might help your business?

Best regards,
{company_name}

---
Generated by Seekan-LG Context-Aware Lead Generation
If you'd prefer not to hear from us again, reply with 'unsubscribe'."""

@app.get("/")
async def root():
    return {
        "message": "Seekan-LG Autonomous LeadGen Agent API",
        "version": "v1.0", 
        "status": "running",
        "agent": "Seekan-LG",
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
    return {"status": "ok", "version": "v1.0", "service": "seekan-lg-agent"}

# Business Profile Endpoints
@app.post("/business/analyze-website")
async def analyze_business_website(request: dict):
    """Analyze a business website to extract company information"""
    try:
        website_url = request.get("website_url")
        if not website_url:
            raise HTTPException(status_code=400, detail="Website URL is required")
        
        # Analyze website
        business_profile = await business_analyzer.analyze_website(website_url)
        
        if "error" in business_profile:
            raise HTTPException(status_code=400, detail=business_profile["error"])
        
        return {
            "business_profile": business_profile,
            "status": "analyzed",
            "agent": "Seekan-LG"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing website: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/business/create-profile")
async def create_business_profile(request: dict):
    """Create or update a business profile"""
    try:
        profile_data = request.get("profile_data")
        if not profile_data:
            raise HTTPException(status_code=400, detail="Profile data is required")
        
        # Validate required fields
        required_fields = ["company_name", "industry", "services"]
        for field in required_fields:
            if not profile_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Store profile
        profile_id = f"profile_{uuid.uuid4().hex[:8]}"
        business_profiles_db[profile_id] = {
            "profile_id": profile_id,
            **profile_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "profile_id": profile_id,
            "status": "created",
            "company_name": profile_data["company_name"],
            "agent": "Seekan-LG"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating business profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile creation error: {str(e)}")

@app.get("/business/profiles")
async def list_business_profiles():
    """List all business profiles"""
    try:
        return {
            "profiles": list(business_profiles_db.values()),
            "count": len(business_profiles_db),
            "agent": "Seekan-LG"
        }
    except Exception as e:
        logger.error(f"Error listing business profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
            "name": preset_config.get("name", f"Seekan-LG Campaign {preset_name}"),
            "preset": preset_name,
            "industry": preset_config.get("industry", ""),
            "config": preset_config,
            "createdAt": datetime.utcnow().isoformat(),
            "agent": "Seekan-LG",
            "businessProfileId": request.get("businessProfileId")
        }
        
        logger.info(f"Seekan-LG created campaign: {campaign_id} from preset: {preset_name}")
        
        return {
            "campaignId": campaign_id,
            "name": preset_config.get("name"),
            "preset": preset_name,
            "status": "active",
            "agent": "Seekan-LG"
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

@app.get("/campaigns")
async def list_campaigns():
    """List all campaigns"""
    try:
        return {"campaigns": list(campaigns_db.values())}
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Job endpoints
@app.post("/jobs")
async def create_job(request: dict, background_tasks: BackgroundTasks):
    """Create a new job with business profile context"""
    try:
        campaign_id = request.get("campaignId")
        planned_count = request.get("plannedCount", 5)
        business_profile_id = request.get("businessProfileId")
        
        if not campaign_id:
            raise HTTPException(status_code=400, detail="campaignId is required")
        
        # Verify campaign exists
        campaign = campaigns_db.get(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get business profile if provided
        business_profile = None
        if business_profile_id:
            business_profile = business_profiles_db.get(business_profile_id)
            if not business_profile:
                raise HTTPException(status_code=404, detail="Business profile not found")
        else:
            # For AcuLeadFinder, use default acupuncture profile
            if campaign.get("preset") == "acu":
                business_profile = {
                    "company_name": "Avicenna Acupuncture",
                    "industry": "Acupuncture",
                    "services": ["Acupuncture", "Pain Management", "Stress Reduction", "Traditional Chinese Medicine"],
                    "value_proposition": "Dr. Farahnaz Behroozi provides expert acupuncture services for pain relief, stress management, and overall wellness.",
                    "target_customers": "Healthcare professionals and wellness seekers",
                    "geography": "Potomac, MD"
                }
        
        # Create job
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        jobs_db[job_id] = {
            "jobId": job_id,
            "campaignId": campaign_id,
            "plannedCount": planned_count,
            "sentCount": 0,
            "status": "running",
            "createdAt": datetime.utcnow().isoformat(),
            "agent": "Seekan-LG",
            "businessProfileUsed": business_profile.get("company_name") if business_profile else "Generic"
        }
        
        # Start appropriate agent
        if business_profile:
            agent = ContextAwareLeadGenAgent(job_id, campaign["config"], business_profile)
            background_tasks.add_task(run_context_aware_agent, agent, planned_count, job_id)
        else:
            # Use generic agent for APLeadFinder without profile
            agent = SeekanLGAgent(job_id, campaign["config"])
            background_tasks.add_task(run_agent, agent, planned_count, job_id)
        
        logger.info(f"Seekan-LG created context-aware job: {job_id}")
        
        return {
            "jobId": job_id,
            "campaignId": campaign_id,
            "plannedCount": planned_count,
            "status": "running",
            "agent": "Seekan-LG",
            "businessContext": "enabled" if business_profile else "generic"
        }
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def run_agent(agent: SeekanLGAgent, planned_count: int, job_id: str):
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

async def run_context_aware_agent(agent: ContextAwareLeadGenAgent, planned_count: int, job_id: str):
    """Run context-aware agent in background"""
    try:
        result = await agent.run_agent_loop(planned_count)
        if result["status"] == "completed":
            jobs_db[job_id]["status"] = "completed"
            jobs_db[job_id]["sentCount"] = result["drafts_created"]
            logger.info(f"Context-aware job {job_id} completed with {result['drafts_created']} drafts")
        else:
            jobs_db[job_id]["status"] = "failed"
            logger.error(f"Context-aware job {job_id} failed: {result.get('error')}")
    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        logger.error(f"Context-aware agent crashed for job {job_id}: {e}")

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
        draft["approvedBy"] = "operator"
        
        return {"ok": True, "draftId": draft_id, "status": "approved", "agent": "Seekan-LG"}
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
        draft["sentAt"] = datetime.utcnow().isoformat()
        
        # Update job sent count
        job_id = draft["jobId"]
        if job_id in jobs_db:
            jobs_db[job_id]["sentCount"] = jobs_db[job_id].get("sentCount", 0) + 1
        
        return {
            "sent": True, 
            "messageId": draft["messageId"], 
            "draftId": draft_id,
            "agent": "Seekan-LG"
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
        
        return {"presets": presets, "agent": "Seekan-LG"}
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
        return {**preset, "agent": "Seekan-LG"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preset: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
