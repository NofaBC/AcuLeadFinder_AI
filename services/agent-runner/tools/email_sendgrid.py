import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.sg_api_key = os.getenv("SENDGRID_API_KEY")
        self.allowed_sender = os.getenv("ALLOWED_SENDER", "info@nofabusinessconsulting.com")
        self.sg_client = sendgrid.SendGridAPIClient(api_key=self.sg_api_key) if self.sg_api_key else None
        
    def can_send_email(self) -> bool:
        """Check if email sending is configured properly"""
        if not self.sg_api_key:
            logger.warning("SendGrid API key not configured")
            return False
        if not self.allowed_sender:
            logger.warning("No allowed sender email configured")
            return False
        return True
    
    async def send_email(self, to_email: str, subject: str, body: str, 
                        from_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email via SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            from_name: Sender name
            
        Returns:
            Dictionary with send result
        """
        if not self.can_send_email():
            return {
                "success": False,
                "error": "Email not configured",
                "message_id": None
            }
        
        try:
            # Create from email with name
            from_email = Email(self.allowed_sender, from_name) if from_name else Email(self.allowed_sender)
            to_email_obj = To(to_email)
            
            # Create email content
            content = Content("text/plain", body)
            
            # Create mail object
            mail = Mail(from_email, to_email_obj, subject, content)
            
            # Send email
            response = self.sg_client.send(mail)
            
            if response.status_code in [200, 202]:
                # Extract message ID from response headers
                message_id = None
                if hasattr(response, 'headers') and 'X-Message-Id' in response.headers:
                    message_id = response.headers['X-Message-Id']
                
                logger.info(f"Email sent successfully to {to_email}, message_id: {message_id}")
                return {
                    "success": True,
                    "message_id": message_id,
                    "status_code": response.status_code
                }
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return {
                    "success": False,
                    "error": f"SendGrid API error: {response.status_code}",
                    "status_code": response.status_code,
                    "message_id": None
                }
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None
            }
    
    async def send_draft_email(self, draft_data: Dict[str, Any], lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a drafted email to a lead
        
        Args:
            draft_data: Draft information including subject and body
            lead_data: Lead information including email and name
            
        Returns:
            Send result dictionary
        """
        to_email = lead_data.get("email")
        if not to_email:
            return {
                "success": False,
                "error": "No recipient email provided",
                "message_id": None
            }
        
        subject = draft_data.get("subject", "")
        body = draft_data.get("body", "")
        from_name = draft_data.get("from_name", "NOFA BC")
        
        # Ensure email is properly decorated (in case it wasn't done during drafting)
        from tools.email_templates import decorate_email
        final_subject, final_body = decorate_email(subject, body, from_name)
        
        return await self.send_email(to_email, final_subject, final_body, from_name)

# Global email sender instance
email_sender = EmailSender()
