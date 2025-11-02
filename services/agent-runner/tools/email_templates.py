from typing import Tuple
import os

def get_opt_out_text() -> str:
    """Get the opt-out text from environment or use default"""
    custom_text = os.getenv("OPT_OUT_TEXT", "")
    if custom_text:
        return custom_text
    return "If you'd prefer not to hear from us again, reply with 'unsubscribe'."

def get_legal_text() -> str:
    """Get the legal text from environment or use default"""
    custom_text = os.getenv("LEGAL_TEXT", "")
    if custom_text:
        return custom_text
    return "NOFA Business Consulting, LLC --- Gaithersburg, MD"

def decorate_email(subject: str, body: str, from_name: str = "") -> Tuple[str, str]:
    """
    Decorate email with proper footer and compliance text
    
    Args:
        subject: Original email subject
        body: Original email body
        from_name: Sender name for signature
    
    Returns:
        Tuple of (subject, decorated_body)
    """
    # Ensure body ends with proper spacing
    clean_body = body.rstrip()
    
    # Add signature if from_name provided
    if from_name and not clean_body.endswith(from_name):
        if not clean_body.endswith('\n\n'):
            if clean_body.endswith('\n'):
                clean_body += '\n'
            else:
                clean_body += '\n\n'
        clean_body += f"Best regards,\n{from_name}"
    
    # Add compliance footer
    footer = f"\n\n{get_opt_out_text()}\n{get_legal_text()}"
    
    return subject, clean_body + footer

def create_acupuncture_template(contact_name: str, company: str, from_name: str = "Dr. Farahnaz Behroozi") -> Tuple[str, str]:
    """Create acupuncture-specific email template"""
    subject = f"Professional Introduction - Avicenna Acupuncture"
    
    body = f"""Dear {contact_name},

I hope this message finds you well. I'm reaching out from Avicenna Acupuncture, serving the Potomac community with traditional Chinese medicine approaches.

I noticed {company} and appreciate your dedication to community wellness. Many of our patients find significant relief from:
• Chronic pain conditions
• Stress and anxiety management
• Sleep disorders
• Digestive issues

We're currently offering $30 off initial consultations for healthcare professionals in our community.

Would you be interested in learning more about how acupuncture could benefit you or your patients?

Warm regards,"""

    return decorate_email(subject, body, from_name)

def create_generic_b2b_template(contact_name: str, company: str, industry: str = "", from_name: str = "NOFA BC") -> Tuple[str, str]:
    """Create generic B2B email template"""
    industry_text = f" in the {industry} industry" if industry else ""
    
    subject = f"Connection Request - {company}"
    
    body = f"""Hello {contact_name},

I came across {company}{industry_text} and was impressed by your work. 

At NOFA Business Consulting, we help businesses optimize their operations and accelerate growth through strategic planning and process improvement.

I'd love to learn more about your business challenges and explore if there might be synergy between our organizations.

Would you have 15 minutes for a brief chat next week?

Best regards,"""

    return decorate_email(subject, body, from_name)
