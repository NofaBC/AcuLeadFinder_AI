import httpx
import asyncio
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import time
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WebSearcher:
    def __init__(self):
        self.respect_robots = os.getenv("ROBOTS_RESPECT", "true").lower() == "true"
        self.rate_limit_delay = 1.0  # seconds between requests
        self.timeout = 30.0
        self.robots_parsers = {}
    
    async def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """Check if we're allowed to fetch this URL based on robots.txt"""
        if not self.respect_robots:
            return True
            
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = urljoin(base_url, "/robots.txt")
            
            # Check cache first
            if base_url in self.robots_parsers:
                parser = self.robots_parsers[base_url]
            else:
                parser = RobotFileParser()
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(robots_url, timeout=10.0)
                        if response.status_code == 200:
                            parser.parse(response.text.splitlines())
                        else:
                            parser.allow_all = True
                    except Exception:
                        parser.allow_all = True
                
                self.robots_parsers[base_url] = parser
            
            return parser.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.warning(f"Robots.txt check failed for {url}: {e}")
            return True
    
    async def search_google(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Mock Google search - in production, use Google Search API or SERP API"""
        # This is a mock implementation
        # In production, you would use:
        # - Google Custom Search JSON API
        # - SerpAPI
        # - Bing Search API
        
        logger.info(f"Mock searching Google for: {query}")
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        # Generate mock results
        mock_results = []
        for i in range(min(num_results, 5)):  # Limit mock results
            mock_results.append({
                "title": f"{query} Business {i+1}",
                "url": f"https://example-{query.replace(' ', '-')}-{i+1}.com",
                "snippet": f"This is a mock search result for {query}. Company provides relevant services in this industry.",
                "display_url": f"example-{query.replace(' ', '-')}-{i+1}.com"
            })
        
        return mock_results
    
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """Scrape website content with robots.txt respect"""
        if not await self.can_fetch(url):
            logger.warning(f"Skipping {url} - disallowed by robots.txt")
            return {"url": url, "content": "", "allowed": False}
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; LeadGenBot/1.0; +http://nofabc.com/bot)"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Extract potential contact information
                contact_info = {
                    "emails": self._extract_emails(clean_text),
                    "phones": self._extract_phones(clean_text),
                    "addresses": self._extract_addresses(clean_text)
                }
                
                return {
                    "url": url,
                    "content": clean_text[:5000],  # Limit content size
                    "title": soup.title.string if soup.title else "",
                    "contact_info": contact_info,
                    "allowed": True,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "content": "",
                "error": str(e),
                "allowed": True
            }
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def _extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        import re
        phone_pattern = r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        return re.findall(phone_pattern, text)
    
    def _extract_addresses(self, text: str) -> List[str]:
        """Extract potential addresses from text"""
        # Simple address detection - can be enhanced
        import re
        address_pattern = r'\d+\s+[\w\s]+,?\s*\w+[\s\w]*,?\s*[A-Z]{2}\s*\d{5}'
        return re.findall(address_pattern, text)

# Global web searcher instance
web_searcher = WebSearcher()
