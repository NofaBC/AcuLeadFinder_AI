import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from memory.firestore_store import firestore_store

logger = logging.getLogger(__name__)

class Guardrails:
    def __init__(self):
        self.send_cap_per_run = int(os.getenv("SEND_CAP_PER_RUN", "20"))
        self.daily_send_cap = int(os.getenv("DAILY_SEND_CAP", "200"))
        self.respect_robots = os.getenv("ROBOTS_RESPECT", "true").lower() == "true"
        
    async def check_send_limits(self, job_id: str, planned_send_count: int = 1) -> Dict[str, Any]:
        """
        Check if sending emails would exceed any limits
        
        Args:
            job_id: The job ID attempting to send
            planned_send_count: Number of emails planned to send
            
        Returns:
            Dictionary with allowed status and reasons
        """
        try:
            # Get job data
            job = await firestore_store.get_job(job_id)
            if not job:
                return {"allowed": False, "reason": "Job not found"}
            
            # Check per-run cap
            sent_this_run = job.sentCount or 0
            if sent_this_run + planned_send_count > self.send_cap_per_run:
                return {
                    "allowed": False, 
                    "reason": f"Per-run send cap exceeded: {sent_this_run + planned_send_count} > {self.send_cap_per_run}"
                }
            
            # Check daily cap (this is a simplified check - in production, track across all jobs)
            # For M1, we'll use a simple approach. In M2, implement proper daily tracking
            estimated_daily_sent = sent_this_run + planned_send_count  # Simplified
            if estimated_daily_sent > self.daily_send_cap:
                return {
                    "allowed": False,
                    "reason": f"Daily send cap exceeded: {estimated_daily_sent} > {self.daily_send_cap}"
                }
            
            return {"allowed": True, "reason": "Within limits"}
            
        except Exception as e:
            logger.error(f"Error checking send limits: {e}")
            return {"allowed": False, "reason": f"Error checking limits: {str(e)}"}
    
    async def check_domain_restrictions(self, domain: str) -> Dict[str, Any]:
        """
        Check if a domain is allowed or blocked
        
        Args:
            domain: Domain to check
            
        Returns:
            Dictionary with allowed status and reason
        """
        try:
            settings = await firestore_store.get_global_settings()
            
            # Check block list first
            if domain.lower() in [d.lower() for d in settings.blockDomains]:
                return {
                    "allowed": False,
                    "reason": f"Domain {domain} is in block list"
                }
            
            # Check allow list (if allow list exists, only allowed domains can be contacted)
            if settings.allowDomains and domain.lower() not in [d.lower() for d in settings.allowDomains]:
                return {
                    "allowed": False,
                    "reason": f"Domain {domain} not in allow list"
                }
            
            # Check for common personal email domains
            personal_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]
            if domain.lower() in personal_domains:
                return {
                    "allowed": False,
                    "reason": f"Domain {domain} is a personal email domain"
                }
            
            return {"allowed": True, "reason": "Domain allowed"}
            
        except Exception as e:
            logger.error(f"Error checking domain restrictions: {e}")
            return {"allowed": False, "reason": f"Error checking domain: {str(e)}"}
    
    async def validate_lead_data(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate lead data before processing
        
        Args:
            lead_data: Lead information to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            errors = []
            warnings = []
            
            # Required field checks
            required_fields = ["company", "email", "domain"]
            for field in required_fields:
                if not lead_data.get(field):
                    errors.append(f"Missing required field: {field}")
            
            # Email validation
            email = lead_data.get("email", "")
            if email and not self._is_valid_email(email):
                errors.append(f"Invalid email format: {email}")
            
            # Domain validation
            domain = lead_data.get("domain", "")
            if domain:
                domain_check = await self.check_domain_restrictions(domain)
                if not domain_check["allowed"]:
                    errors.append(domain_check["reason"])
            
            # Confidence score check
            confidence = lead_data.get("confidence", 0)
            if confidence < 0.3:
                warnings.append("Low confidence score for lead data")
            
            # Company name sanity check
            company = lead_data.get("company", "")
            if company and len(company) < 2:
                warnings.append("Company name seems too short")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Error validating lead data: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    async def check_crawl_permission(self, url: str, user_agent: str = "LeadGenBot/1.0") -> bool:
        """
        Check if we're allowed to crawl a URL (respects robots.txt)
        
        Args:
            url: URL to check
            user_agent: User agent string
            
        Returns:
            Boolean indicating if crawling is allowed
        """
        if not self.respect_robots:
            return True
        
        try:
            from tools.web_search import web_searcher
            return await web_searcher.can_fetch(url, user_agent)
        except Exception as e:
            logger.warning(f"Error checking crawl permission for {url}: {e}")
            return True  # Default to allowed if check fails
    
    async def get_send_cap_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current send cap status for a job
        
        Args:
            job_id: Job ID to check
            
        Returns:
            Dictionary with cap status information
        """
        try:
            job = await firestore_store.get_job(job_id)
            if not job:
                return {"error": "Job not found"}
            
            sent_count = job.sentCount or 0
            planned_count = job.plannedCount or 0
            
            return {
                "job_id": job_id,
                "sent_count": sent_count,
                "planned_count": planned_count,
                "remaining_in_run": max(0, self.send_cap_per_run - sent_count),
                "remaining_daily": max(0, self.daily_send_cap - sent_count),  # Simplified
                "send_cap_per_run": self.send_cap_per_run,
                "daily_send_cap": self.daily_send_cap,
                "within_limits": sent_count < self.send_cap_per_run and sent_count < self.daily_send_cap
            }
            
        except Exception as e:
            logger.error(f"Error getting send cap status: {e}")
            return {"error": str(e)}

# Global guardrails instance
guardrails = Guardrails()
