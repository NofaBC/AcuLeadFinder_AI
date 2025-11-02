import re
import asyncio
from typing import Dict, Any, List, Optional
import logging
from tools.web_search import web_searcher

logger = logging.getLogger(__name__)

class LeadEnricher:
    def __init__(self):
        self.common_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    
    async def enrich_lead_from_website(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich lead information from website content"""
        try:
            contact_info = website_data.get("contact_info", {})
            content = website_data.get("content", "")
            url = website_data.get("url", "")
            
            # Extract company name from URL or content
            company_name = self._extract_company_name(url, content)
            
            # Extract potential contact person
            contact_name = self._extract_contact_name(content)
            
            # Find business email (non-generic)
            business_email = self._find_business_email(contact_info.get("emails", []), company_name)
            
            # Extract location information
            location = self._extract_location(content, website_data.get("title", ""))
            
            return {
                "company": company_name,
                "contactName": contact_name,
                "role": self._infer_role(contact_name, content),
                "email": business_email,
                "domain": self._extract_domain(url),
                "city": location.get("city", ""),
                "state": location.get("state", ""),
                "sourceUrl": url,
                "confidence": self._calculate_confidence(company_name, business_email, contact_name),
                "enrichedAt": self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error enriching lead: {e}")
            return {
                "company": "",
                "contactName": "",
                "role": "",
                "email": "",
                "domain": self._extract_domain(website_data.get("url", "")),
                "city": "",
                "state": "",
                "sourceUrl": website_data.get("url", ""),
                "confidence": 0,
                "error": str(e)
            }
    
    def _extract_company_name(self, url: str, content: str) -> str:
        """Extract company name from URL and content"""
        # Try to get from URL first
        domain = self._extract_domain(url)
        if domain and domain not in self.common_domains:
            company_from_domain = domain.replace('.com', '').replace('.org', '').replace('.net', '')
            company_from_domain = re.sub(r'[^a-zA-Z]', ' ', company_from_domain)
            company_from_domain = company_from_domain.title()
            if company_from_domain and len(company_from_domain) > 3:
                return company_from_domain
        
        # Try to extract from page title or content
        title_patterns = [
            r"Welcome to\s+([^.!?]+)",
            r"About\s+([^.!?]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Company|Corp|Inc|LLC)"
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, content[:1000])  # Search first 1000 chars
            if matches:
                return matches[0]
        
        return "Unknown Company"
    
    def _extract_contact_name(self, content: str) -> str:
        """Extract potential contact name from content"""
        # Look for common name patterns
        name_pattern = r"(?:Contact|Email|Call)\s+(?:us|me)?\s*:?\s*([A-Z][a-z]+ [A-Z][a-z]+)"
        matches = re.findall(name_pattern, content, re.IGNORECASE)
        if matches:
            return matches[0]
        
        # Look for "Name:" pattern
        name_label_pattern = r"Name:\s*([A-Z][a-z]+ [A-Z][a-z]+)"
        matches = re.findall(name_label_pattern, content)
        if matches:
            return matches[0]
        
        return ""
    
    def _find_business_email(self, emails: List[str], company_name: str) -> str:
        """Find the most likely business email from list"""
        if not emails:
            return ""
        
        # Prefer emails matching company domain
        company_domain = company_name.lower().replace(' ', '') + ".com"
        for email in emails:
            domain = email.split('@')[1] if '@' in email else ""
            if domain and domain not in self.common_domains:
                return email
        
        # Fall back to first email
        return emails[0] if emails else ""
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    def _extract_location(self, content: str, title: str) -> Dict[str, str]:
        """Extract location information from content"""
        # Simple location extraction - can be enhanced with NLP
        location_keywords = ["Potomac", "Gaithersburg", "Rockville", "Bethesda", "MD", "Maryland"]
        
        for keyword in location_keywords:
            if keyword.lower() in content.lower() or keyword.lower() in title.lower():
                if keyword in ["MD", "Maryland"]:
                    return {"state": "MD"}
                else:
                    return {"city": keyword, "state": "MD"}
        
        return {"city": "", "state": ""}
    
    def _infer_role(self, contact_name: str, content: str) -> str:
        """Infer role based on content and context"""
        if not contact_name:
            return "Business Owner"
        
        role_patterns = {
            "owner": r"\b(owner|proprietor|founder)\b",
            "manager": r"\b(manager|director|supervisor)\b",
            "doctor": r"\b(dr|doctor|physician)\b",
            "therapist": r"\b(therapist|practitioner)\b"
        }
        
        content_lower = content.lower()
        for role, pattern in role_patterns.items():
            if re.search(pattern, content_lower):
                return role.title()
        
        return "Business Owner"
    
    def _calculate_confidence(self, company: str, email: str, contact: str) -> float:
        """Calculate confidence score for enriched data"""
        score = 0.0
        if company and company != "Unknown Company":
            score += 0.4
        if email:
            score += 0.4
        if contact:
            score += 0.2
        return score
    
    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Global lead enricher instance
lead_enricher = LeadEnricher()
