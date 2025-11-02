import os
import logging
from typing import List, Optional, Dict, Any
from google.cloud import firestore
from google.oauth2 import service_account
from .schemas import Campaign, Job, Lead, Draft, RunEvent, GlobalSettings, JobStatus, DraftStatus

logger = logging.getLogger(__name__)

class FirestoreStore:
    def __init__(self):
        self.db = self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Initialize Firestore client with environment credentials"""
        try:
            # For Vercel deployments, use service account key from environment
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
            
            if private_key and private_key != "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n":
                credentials = service_account.Credentials.from_service_account_info({
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": "firebase-adminsdk",
                    "private_key": private_key,
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "token_uri": "https://oauth2.googleapis.com/token",
                })
                return firestore.Client(credentials=credentials)
            else:
                # For local development with Firebase emulator or default credentials
                return firestore.Client()
                
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            # Return a mock client for development without Firebase
            return None
    
    # Campaign operations
    async def create_campaign(self, campaign: Campaign) -> bool:
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("campaigns").document(campaign.campaignId)
            doc_ref.set(campaign.dict())
            return True
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return False
    
    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        if not self.db:
            return None
            
        try:
            doc_ref = self.db.collection("campaigns").document(campaign_id)
            doc = doc_ref.get()
            if doc.exists:
                return Campaign(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error getting campaign: {e}")
            return None
    
    # Job operations
    async def create_job(self, job: Job) -> bool:
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("jobs").document(job.jobId)
            doc_ref.set(job.dict())
            return True
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return False
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        if not self.db:
            return None
            
        try:
            doc_ref = self.db.collection("jobs").document(job_id)
            doc = doc_ref.get()
            if doc.exists:
                return Job(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error getting job: {e}")
            return None
    
    async def update_job_status(self, job_id: str, status: JobStatus, sent_count: int = None, cost: float = None) -> bool:
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("jobs").document(job_id)
            update_data = {
                "status": status,
                "updatedAt": firestore.SERVER_TIMESTAMP
            }
            if sent_count is not None:
                update_data["sentCount"] = sent_count
            if cost is not None:
                update_data["costUSD"] = cost
                
            doc_ref.update(update_data)
            return True
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            return False
    
    # Lead operations
    async def create_lead(self, lead: Lead) -> bool:
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("leads").document(lead.leadId)
            doc_ref.set(lead.dict())
            return True
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return False
    
    async def get_leads_by_job(self, job_id: str) -> List[Lead]:
        if not self.db:
            return []
            
        try:
            leads_ref = self.db.collection("leads").where("jobId", "==", job_id)
            docs = leads_ref.stream()
            return [Lead(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting leads by job: {e}")
            return []
    
    # Draft operations
    async def create_draft(self, draft: Draft) -> bool:
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("drafts").document(draft.draftId)
            doc_ref.set(draft.dict())
            return True
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return False
    
    async def get_draft(self, draft_id: str) -> Optional[Draft]:
        if not self.db:
            return None
            
        try:
            doc_ref = self.db.collection("drafts").document(draft_id)
            doc = doc_ref.get()
            if doc.exists:
                return Draft(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error getting draft: {e}")
            return None
    
    async def get_drafts_by_job(self, job_id: str, status: Optional[DraftStatus] = None) -> List[Draft]:
        if not self.db:
            return []
            
        try:
            drafts_ref = self.db.collection("drafts").where("jobId", "==", job_id)
            if status:
                drafts_ref = drafts_ref.where("status", "==", status)
                
            docs = drafts_ref.stream()
            return [Draft(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting drafts by job: {e}")
            return []
    
    async def update_draft_status(self, draft_id: str, status: DraftStatus, reviewer: str = None, message_id: str = None) -> bool:
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("drafts").document(draft_id)
            update_data = {
                "status": status,
                "updatedAt": firestore.SERVER_TIMESTAMP
            }
            if reviewer:
                update_data["reviewer"] = reviewer
            if message_id:
                update_data["messageId"] = message_id
                
            doc_ref.update(update_data)
            return True
        except Exception as e:
            logger.error(f"Error updating draft status: {e}")
            return False
    
    # Run event operations
    async def log_run_event(self, run_event: RunEvent) -> bool:
        if not self.db:
            return False
            
        try:
            doc_ref = self.db.collection("runs").document(run_event.runId)
            doc_ref.set(run_event.dict())
            return True
        except Exception as e:
            logger.error(f"Error logging run event: {e}")
            return False
    
    # Settings operations
    async def get_global_settings(self) -> GlobalSettings:
        if not self.db:
            return GlobalSettings()
            
        try:
            doc_ref = self.db.collection("settings").document("global")
            doc = doc_ref.get()
            if doc.exists:
                return GlobalSettings(**doc.to_dict())
            else:
                # Create default settings if they don't exist
                default_settings = GlobalSettings()
                doc_ref.set(default_settings.dict())
                return default_settings
        except Exception as e:
            logger.error(f"Error getting global settings: {e}")
            return GlobalSettings()

# Global Firestore instance
firestore_store = FirestoreStore()
