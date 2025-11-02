import os
import openai
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.client = None
        
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI API key not configured")
    
    async def draft_email(self, lead_data: Dict[str, Any], campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Draft a personalized email using LLM"""
        if not self.client:
            return self._create_fallback_draft(lead_data, campaign_config)
        
        try:
            prompt = self._build_email_prompt(lead_data, campaign_config)
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional business development representative. Create personalized, warm, and professional outreach emails that provide value to the recipient."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            email_content = response.choices[0].message.content.strip()
            
            # Parse subject and body from response
            subject, body = self._parse_email_response(email_content)
            
            return {
                "success": True,
                "subject": subject,
                "body": body,
                "model": self.default_model,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"Error drafting email with LLM: {e}")
            # Fallback to template-based drafting
            return self._create_fallback_draft(lead_data, campaign_config)
    
    def _build_email_prompt(self, lead_data: Dict[str, Any], campaign_config: Dict[str, Any]) -> str:
        """Build prompt for email drafting"""
        industry = campaign_config.get("industry", "")
        brand_voice = campaign_config.get("brand_voice", "Professional and concise")
        from_name = campaign_config.get("from_name", "NOFA BC")
        offer = campaign_config.get("offer", "")
        
        company = lead_data.get("company", "")
        contact_name = lead_data.get("contactName", "there")
        role = lead_data.get("role", "Business Owner")
        
        prompt = f"""
Please draft a professional outreach email with the following details:

RECIPIENT:
- Name: {contact_name}
- Company: {company}
- Role: {role}

SENDER:
- Name: {from_name}
- Industry: {industry}

BRAND VOICE: {brand_voice}

SPECIFIC INSTRUCTIONS:
- Keep it concise (3-4 short paragraphs max)
- Personalize based on the recipient's company and role
- Sound warm and professional
- Provide clear value
- Include a gentle call-to-action

{"OFFER TO MENTION: " + offer if offer else "No specific offer to mention"}

FORMAT:
Subject: [Compelling subject line]

[Email body]

Please provide ONLY the email content with subject and body, no additional explanations.
"""
        return prompt
    
    def _parse_email_response(self, email_content: str) -> tuple[str, str]:
        """Parse LLM response into subject and body"""
        lines = email_content.split('\n')
        subject = "Professional Introduction"
        body_lines = []
        
        in_body = False
        for line in lines:
            line = line.strip()
            if line.startswith('Subject:') or line.startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
            elif line and not in_body and not line.startswith('Subject:'):
                in_body = True
                body_lines.append(line)
            elif in_body:
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        if not body:
            body = "I came across your business and was impressed by your work. I'd love to connect and explore potential synergies."
        
        return subject, body
    
    def _create_fallback_draft(self, lead_data: Dict[str, Any], campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback email draft when LLM is unavailable"""
        from tools.email_templates import create_generic_b2b_template, create_acupuncture_template
        
        contact_name = lead_data.get("contactName", "there")
        company = lead_data.get("company", "your company")
        industry = campaign_config.get("industry", "")
        from_name = campaign_config.get("from_name", "NOFA BC")
        
        if industry.lower() == "acupuncture":
            subject, body = create_acupuncture_template(contact_name, company, from_name)
        else:
            subject, body = create_generic_b2b_template(contact_name, company, industry, from_name)
        
        return {
            "success": True,
            "subject": subject,
            "body": body,
            "model": "fallback_template",
            "tokens_used": 0
        }
    
    async def generate_search_terms(self, campaign_config: Dict[str, Any]) -> List[str]:
        """Generate optimized search terms using LLM"""
        if not self.client:
            return self._generate_fallback_search_terms(campaign_config)
        
        try:
            industry = campaign_config.get("industry", "")
            geo = campaign_config.get("geo", {})
            keywords = campaign_config.get("keywords", [])
            
            prompt = f"""
Generate 10 specific search terms for finding businesses in the {industry} industry.

Industry: {industry}
Location: {geo.get('center_city', '')}, {geo.get('state', '')}
Keywords: {', '.join(keywords)}

Requirements:
- Include location when relevant
- Mix broad and specific terms
- Focus on business discovery
- Include service-based searches

Return only a comma-separated list of search terms, no additional text.
"""
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            terms_text = response.choices[0].message.content.strip()
            search_terms = [term.strip() for term in terms_text.split(',')]
            
            return search_terms[:10]  # Limit to 10 terms
            
        except Exception as e:
            logger.error(f"Error generating search terms with LLM: {e}")
            return self._generate_fallback_search_terms(campaign_config)
    
    def _generate_fallback_search_terms(self, campaign_config: Dict[str, Any]) -> List[str]:
        """Generate fallback search terms without LLM"""
        industry = campaign_config.get("industry", "")
        geo = campaign_config.get("geo", {})
        keywords = campaign_config.get("keywords", [])
        
        city = geo.get("center_city", "")
        state = geo.get("state", "")
        
        location = f"{city}, {state}" if city and state else state if state else ""
        
        search_terms = []
        for keyword in keywords:
            if location:
                search_terms.append(f"{industry} {keyword} {location}")
                search_terms.append(f"{keyword} services {location}")
            else:
                search_terms.append(f"{industry} {keyword}")
                search_terms.append(f"{keyword} services")
        
        return search_terms[:8]  # Limit to 8 terms

# Global LLM client instance
llm_client = LLMClient()
