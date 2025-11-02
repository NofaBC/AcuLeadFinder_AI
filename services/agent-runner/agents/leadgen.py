import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from .planner import TaskPlanner

class LeadGenAgent:
    def __init__(self, job_id: str, campaign_config: Dict[str, Any], tools: Any):
        self.job_id = job_id
        self.campaign_config = campaign_config
        self.tools = tools
        self.planner = TaskPlanner(campaign_config)
        self.leads_generated = 0
        self.drafts_created = 0
        
    async def run_agent_loop(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main agent loop that coordinates the lead generation process"""
        try:
            # Step 1: Plan search terms
            search_terms = self.planner.plan_search_terms(self.job_id, self.campaign_config)
            print(f"Planned search terms: {search_terms}")
            
            # Step 2: Execute web searches (mock for now)
            search_results = await self.mock_web_search(search_terms)
            
            # Step 3: Enrich leads from search results
            enriched_leads = await self.mock_enrich_leads(search_results)
            
            # Step 4: Draft emails for leads
            drafts = await self.mock_draft_emails(enriched_leads, job_data)
            
            # Update counters
            self.leads_generated = len(enriched_leads)
            self.drafts_created = len(drafts)
            
            return {
                "status": "completed",
                "leads_generated": self.leads_generated,
                "drafts_created": self.drafts_created,
                "search_terms_used": search_terms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def mock_web_search(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Mock web search - will be replaced with real implementation"""
        print(f"Mock searching for: {search_terms}")
        
        # Simulate search results
        mock_results = []
        for term in search_terms[:3]:  # Limit for demo
            mock_results.append({
                "title": f"Business related to {term}",
                "url": f"https://example.com/{term.replace(' ', '-')}",
                "snippet": f"This is a mock result for {term}",
                "search_term": term
            })
        
        await asyncio.sleep(1)  # Simulate API call
        return mock_results
    
    async def mock_enrich_leads(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mock lead enrichment - will be replaced with real implementation"""
        print("Mock enriching leads...")
        
        enriched_leads = []
        for result in search_results:
            lead = {
                "company": f"{result['search_term']} Company",
                "contactName": "John Doe",  # Mock name
                "role": "Owner/Manager",
                "email": f"contact@{result['search_term'].replace(' ', '').lower()}.com",
                "domain": f"{result['search_term'].replace(' ', '').lower()}.com",
                "city": self.campaign_config.get('geo', {}).get('center_city', 'Unknown'),
                "state": self.campaign_config.get('geo', {}).get('state', 'Unknown'),
                "sourceUrl": result['url'],
                "enrichedAt": datetime.utcnow().isoformat()
            }
            enriched_leads.append(lead)
        
        await asyncio.sleep(0.5)  # Simulate processing
        return enriched_leads
    
    async def mock_draft_emails(self, leads: List[Dict[str, Any]], job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock email drafting - will be replaced with real LLM implementation"""
        print("Mock drafting emails...")
        
        drafts = []
        for lead in leads:
            draft = {
                "jobId": self.job_id,
                "leadId": f"lead_{len(drafts) + 1}",
                "subject": f"Regarding your {self.campaign_config.get('industry', 'business')} services",
                "body": f"""Hello {lead['contactName']},

I came across {lead['company']} and was impressed by your work in {self.campaign_config.get('industry', 'your industry')}.

We specialize in helping businesses like yours optimize their operations and reach more customers.

Would you be open to a quick chat next week?

Best regards,
{self.campaign_config.get('from_name', 'NOFA BC')}""",
                "status": "draft",
                "createdAt": datetime.utcnow().isoformat()
            }
            drafts.append(draft)
        
        await asyncio.sleep(0.5)  # Simulate LLM processing
        return drafts

# Agent factory function
async def create_leadgen_agent(job_id: str, campaign_config: Dict[str, Any], tools: Any = None) -> LeadGenAgent:
    """Factory function to create a lead generation agent"""
    return LeadGenAgent(job_id, campaign_config, tools)
