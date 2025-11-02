from typing import List, Dict, Any
from enum import Enum

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPlanner:
    def __init__(self, campaign_config: Dict[str, Any]):
        self.campaign_config = campaign_config
        self.steps = [
            "plan_search_terms",
            "web_search",
            "enrich_leads", 
            "draft_emails",
            "await_approval",
            "send_emails"
        ]
        self.current_step = 0
    
    def get_next_step(self, current_state: Dict[str, Any]) -> str:
        """Determine the next step based on current state"""
        if current_state.get("status") == "completed":
            return "done"
        
        # Simple linear progression for now
        if self.current_step < len(self.steps):
            next_step = self.steps[self.current_step]
            self.current_step += 1
            return next_step
        return "done"
    
    def plan_search_terms(self, job_id: str, campaign_config: Dict[str, Any]) -> List[str]:
        """Generate search terms based on campaign configuration"""
        industry = campaign_config.get("industry", "")
        geo = campaign_config.get("geo", {})
        keywords = campaign_config.get("keywords", [])
        
        search_terms = []
        
        # Generate location-based searches
        city = geo.get("center_city", "")
        state = geo.get("state", "")
        
        if city and state:
            location = f"{city}, {state}"
        elif state:
            location = state
        else:
            location = ""
        
        # Combine industry, keywords, and location
        for keyword in keywords:
            if location:
                search_terms.append(f"{keyword} {location}")
                search_terms.append(f"{industry} {keyword} {location}")
            else:
                search_terms.append(f"{industry} {keyword}")
        
        # Add generic searches
        if industry and location:
            search_terms.append(f"{industry} services {location}")
            search_terms.append(f"{industry} clinic {location}")
        
        return search_terms[:10]  # Limit to 10 terms
    
    def should_continue(self, job_data: Dict[str, Any], leads_count: int) -> bool:
        """Determine if we should continue generating leads"""
        planned_count = job_data.get("plannedCount", 0)
        sent_count = job_data.get("sentCount", 0)
        
        # Stop if we've reached planned count
        if sent_count >= planned_count:
            return False
        
        # Stop if we have enough drafts in pipeline
        if leads_count >= planned_count:
            return False
            
        return True
