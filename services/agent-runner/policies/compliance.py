import os
import logging
from typing import Dict, Any, List
from memory.firestore_store import firestore_store

logger = logging.getLogger(__name__)

class Compliance:
    def __init__(self):
        self.unsubscribe_keywords = ["unsubscribe", "stop", "remove", "opt-out"]
        self.complaint_keywords = ["spam", "complaint", "abuse"]
    
    async def ensure_email_compliance(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure email content complies with regulations
        
        Args:
            email_data: Email subject and body
            
        Returns:
            Dictionary with compliance status and modified email data
        """
        try:
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            from_name = email_data.get("from_name", "")
            
            # Get compliance settings
            settings = await firestore_store.get_global_settings()
            
            # Ensure unsubscribe text is included
            if not self._has_unsubscribe_text(body, settings.unsubscribeText):
                body = self._add_unsubscribe_text(body, settings.unsubscribeText)
            
            # Ensure legal address is included
            if not self._has_legal_address(body, settings.legalAddress):
                body = self._add_legal_address(body, settings.legalAddress)
            
            # Check for misleading subject lines
            subject_compliant = self._validate_subject(subject)
            
            # Check body content for compliance issues
            body_compliant, body_issues = self._validate_body_content(body)
            
            return {
                "compliant": subject_compliant and body_compliant,
                "modified_subject": subject,
                "modified_body": body,
                "issues": body_issues,
                "subject_approved": subject_compliant,
                "body_approved": body_compliant
            }
            
        except Exception as e:
            logger.error(f"Error ensuring email compliance: {e}")
            return {
                "compliant": False,
                "modified_subject": email_data.get("subject", ""),
                "modified_body": email_data.get("body", ""),
                "issues": [f"Compliance check error: {str(e)}"],
                "subject_approved": False,
                "body_approved": False
            }
    
    def _has_unsubscribe_text(self, body: str, unsubscribe_text: str) -> bool:
        """Check if body contains unsubscribe text"""
        if not unsubscribe_text:
            return False
        
        # Check for the specific unsubscribe text or similar
        return unsubscribe_text.lower() in body.lower() or any(
            keyword in body.lower() for keyword in self.unsubscribe_keywords
        )
    
    def _add_unsubscribe_text(self, body: str, unsubscribe_text: str) -> str:
        """Add unsubscribe text to email body"""
        if not unsubscribe_text:
            unsubscribe_text = "If you'd prefer not to hear from us again, reply with 'unsubscribe'."
        
        return f"{body.rstrip()}\n\n{unsubscribe_text}"
    
    def _has_legal_address(self, body: str, legal_address: str) -> bool:
        """Check if body contains legal address"""
        if not legal_address:
            return False
        
        return legal_address in body
    
    def _add_legal_address(self, body: str, legal_address: str) -> str:
        """Add legal address to email body"""
        if not legal_address:
            legal_address = "NOFA Business Consulting, LLC --- Gaithersburg, MD"
        
        return f"{body.rstrip()}\n{legal_address}"
    
    def _validate_subject(self, subject: str) -> bool:
        """Validate subject line for compliance"""
        if not subject or len(subject.strip()) == 0:
            return False
        
        # Check for misleading phrases
        misleading_phrases = [
            "urgent", "immediate action", "final notice", "you have won", "free money",
            "guaranteed", "100% free", "no cost", "prize", "winner"
        ]
        
        subject_lower = subject.lower()
        for phrase in misleading_phrases:
            if phrase in subject_lower:
                return False
        
        # Check subject length (reasonable limit)
        if len(subject) > 150:
            return False
        
        return True
    
    def _validate_body_content(self, body: str) -> tuple[bool, List[str]]:
        """Validate body content for compliance issues"""
        issues = []
        body_lower = body.lower()
        
        # Check for spammy phrases
        spammy_phrases = [
            "make money fast", "work from home", "get rich quick", "double your",
            "risk-free", "lose weight", "miracle", "once in a lifetime"
        ]
        
        for phrase in spammy_phrases:
            if phrase in body_lower:
                issues.append(f"Contains spammy phrase: '{phrase}'")
        
        # Check for excessive capitalization
        words = body.split()
        if len(words) > 0:
            all_caps_words = [word for word in words if word.isupper() and len(word) > 2]
            if len(all_caps_words) > 3:  # More than 3 all-caps words
                issues.append("Excessive use of capitalization")
        
        # Check for misleading claims
        misleading_claims = [
            "guaranteed results", "no risk", "instant", "overnight"
        ]
        
        for claim in misleading_claims:
            if claim in body_lower:
                issues.append(f"Potentially misleading claim: '{claim}'")
        
        compliant = len(issues) == 0
        return compliant, issues
    
    async def process_unsubscribe_request(self, email: str, reason: str = "") -> bool:
        """
        Process an unsubscribe request
        
        Args:
            email: Email address to unsubscribe
            reason: Reason for unsubscribing (optional)
            
        Returns:
            Success status
        """
        try:
            # In M1, we'll log the unsubscribe request
            # In M2, implement proper unsubscribe list management
            
            logger.info(f"Unsubscribe request received for: {email}, reason: {reason}")
            
            # Log to Firestore for tracking
            from memory.schemas import RunEvent
            import uuid
            
            event = RunEvent(
                runId=str(uuid.uuid4()),
                jobId="system",
                step="compliance",
                event="unsubscribe_request",
                data={
                    "email": email,
                    "reason": reason,
                    "timestamp": self._get_current_timestamp()
                }
            )
            
            await firestore_store.log_run_event(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing unsubscribe request: {e}")
            return False
    
    async def handle_complaint(self, email: str, complaint_type: str, details: str = "") -> bool:
        """
        Handle spam complaints or other compliance issues
        
        Args:
            email: Complainant email
            complaint_type: Type of complaint
            details: Complaint details
            
        Returns:
            Success status
        """
        try:
            logger.warning(f"Complaint received from {email}: {complaint_type} - {details}")
            
            # Log complaint for tracking and analysis
            from memory.schemas import RunEvent
            import uuid
            
            event = RunEvent(
                runId=str(uuid.uuid4()),
                jobId="system", 
                step="compliance",
                event="complaint_received",
                data={
                    "email": email,
                    "complaint_type": complaint_type,
                    "details": details,
                    "timestamp": self._get_current_timestamp(),
                    "action_taken": "logged_for_review"
                }
            )
            
            await firestore_store.log_run_event(event)
            
            # In M2, implement automatic sending suspension for serious complaints
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling complaint: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance statistics and status"""
        try:
            # This would be enhanced in M2 with actual analytics
            return {
                "status": "active",
                "unsubscribe_mechanism": "reply-based",
                "legal_address_included": True,
                "opt_out_text_included": True,
                "last_audit": self._get_current_timestamp(),
                "compliance_level": "basic"  # basic, intermediate, advanced
            }
        except Exception as e:
            logger.error(f"Error getting compliance summary: {e}")
            return {"error": str(e)}

# Global compliance instance
compliance = Compliance()
