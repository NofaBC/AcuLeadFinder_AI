from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    FAILED = "failed"

class DraftStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    FAILED = "failed"

class Campaign(BaseModel):
    campaignId: str
    name: str
    preset: str
    industry: str
    geo: Dict[str, Any]
    keywords: List[str]
    model: str = "gpt-4o"
    sendCapPerRun: int = 20
    dailySendCap: int = 200
    status: str = "active"
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class Job(BaseModel):
    jobId: str
    campaignId: str
    plannedCount: int
    sentCount: int = 0
    costUSD: float = 0.0
    status: JobStatus = JobStatus.QUEUED
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class Lead(BaseModel):
    leadId: str
    jobId: str
    campaignId: str
    company: str
    contactName: str
    role: str
    email: str
    domain: str
    city: str
    state: str
    sourceUrl: str
    enrichedAt: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = 0.0

class Draft(BaseModel):
    draftId: str
    jobId: str
    leadId: str
    subject: str
    body: str
    status: DraftStatus = DraftStatus.DRAFT
    reviewer: Optional[str] = None
    messageId: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class RunEvent(BaseModel):
    runId: str
    jobId: str
    step: str
    event: str
    data: Dict[str, Any]
    ts: datetime = Field(default_factory=datetime.utcnow)

class GlobalSettings(BaseModel):
    allowDomains: List[str] = []
    blockDomains: List[str] = []
    unsubscribeText: str = "If you'd prefer not to hear from us again, reply with 'unsubscribe'."
    legalAddress: str = "NOFA Business Consulting, LLC --- Gaithersburg, MD"
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

# Request and Response models
class CreateCampaignRequest(BaseModel):
    preset: str
    model: Optional[str] = "gpt-4o"
    sendCapPerRun: Optional[int] = 20

class CreateJobRequest(BaseModel):
    campaignId: str
    plannedCount: int

class ApproveDraftRequest(BaseModel):
    reviewer: Optional[str] = "system"

class SendDraftRequest(BaseModel):
    immediate: bool = True
