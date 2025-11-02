import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Vector store for objection memory and semantic search.
    This is a placeholder implementation for M1.
    In M2/M3, this will be integrated with a real vector database like:
    - Pinecone
    - Weaviate  
    - Chroma
    - Qdrant
    """
    
    def __init__(self):
        self.initialized = False
        self.objection_memory = []  # In-memory storage for M1
        logger.info("VectorStore initialized (in-memory mode for M1)")
    
    async def initialize(self):
        """Initialize vector store connection"""
        # Placeholder for future vector DB initialization
        self.initialized = True
        logger.info("VectorStore connection initialized")
    
    async def store_objection_response(self, objection: str, response: str, 
                                    category: str = "general", 
                                    effectiveness: float = 0.0) -> bool:
        """
        Store an objection-response pair for future learning
        
        Args:
            objection: Customer objection text
            response: Effective response text
            category: Objection category (price, timing, need, etc.)
            effectiveness: Response effectiveness score (0-1)
        """
        try:
            objection_entry = {
                "id": f"obj_{len(self.objection_memory) + 1}",
                "objection": objection,
                "response": response,
                "category": category,
                "effectiveness": effectiveness,
                "created_at": datetime.utcnow().isoformat(),
                "usage_count": 0
            }
            
            self.objection_memory.append(objection_entry)
            logger.info(f"Stored objection-response pair: {category}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing objection response: {e}")
            return False
    
    async def find_similar_objections(self, query: str, category: str = None, 
                                    threshold: float = 0.7, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find similar objections and their responses
        
        Args:
            query: Objection text to match
            category: Filter by category
            threshold: Similarity threshold (placeholder)
            top_k: Number of results to return
            
        Returns:
            List of objection-response pairs
        """
        try:
            # Simple keyword matching for M1
            # In M2/M3, this will use proper vector similarity search
            
            query_lower = query.lower()
            results = []
            
            for entry in self.objection_memory:
                # Filter by category if specified
                if category and entry["category"] != category:
                    continue
                
                # Simple keyword matching (to be replaced with vector similarity)
                objection_text = entry["objection"].lower()
                score = self._calculate_simple_similarity(query_lower, objection_text)
                
                if score >= threshold:
                    results.append({
                        **entry,
                        "similarity_score": score
                    })
            
            # Sort by effectiveness and similarity, return top_k
            results.sort(key=lambda x: (x["effectiveness"], x["similarity_score"]), reverse=True)
            
            # Increment usage count for returned results
            for result in results[:top_k]:
                result["usage_count"] += 1
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar objections: {e}")
            return []
    
    def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (placeholder for vector similarity)
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        # Simple word overlap similarity for M1
        # In M2/M3, this will use proper embedding cosine similarity
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def get_objection_categories(self) -> List[str]:
        """Get list of unique objection categories"""
        categories = set()
        for entry in self.objection_memory:
            categories.add(entry["category"])
        return list(categories)
    
    async def update_response_effectiveness(self, objection_id: str, effectiveness: float) -> bool:
        """
        Update the effectiveness score of a response
        
        Args:
            objection_id: ID of the objection-response pair
            effectiveness: New effectiveness score (0-1)
        """
        try:
            for entry in self.objection_memory:
                if entry["id"] == objection_id:
                    entry["effectiveness"] = effectiveness
                    entry["updated_at"] = datetime.utcnow().isoformat()
                    logger.info(f"Updated effectiveness for {objection_id}: {effectiveness}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating response effectiveness: {e}")
            return False
    
    async def get_most_effective_responses(self, category: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most effective responses by category or overall
        
        Args:
            category: Filter by category
            top_k: Number of results to return
            
        Returns:
            List of most effective objection-response pairs
        """
        try:
            filtered_entries = self.objection_memory
            
            if category:
                filtered_entries = [entry for entry in filtered_entries if entry["category"] == category]
            
            # Sort by effectiveness and usage count
            filtered_entries.sort(key=lambda x: (x["effectiveness"], x["usage_count"]), reverse=True)
            
            return filtered_entries[:top_k]
            
        except Exception as e:
            logger.error(f"Error getting most effective responses: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        total_entries = len(self.objection_memory)
        categories = await self.get_objection_categories()
        
        category_counts = {}
        for category in categories:
            category_counts[category] = len([
                entry for entry in self.objection_memory 
                if entry["category"] == category
            ])
        
        avg_effectiveness = sum(
            entry["effectiveness"] for entry in self.objection_memory
        ) / total_entries if total_entries > 0 else 0
        
        total_usage = sum(entry["usage_count"] for entry in self.objection_memory)
        
        return {
            "total_entries": total_entries,
            "categories": categories,
            "category_counts": category_counts,
            "average_effectiveness": round(avg_effectiveness, 2),
            "total_usage": total_usage,
            "store_type": "in_memory",
            "initialized": self.initialized
        }

# Global vector store instance
vector_store = VectorStore()

# Pre-populate with some common objection responses for M1
DEFAULT_OBJECTION_RESPONSES = [
    {
        "objection": "I'm too busy right now",
        "response": "I completely understand being busy. Would a quick 10-minute call next week work better? I'll make sure to respect your time.",
        "category": "timing",
        "effectiveness": 0.8
    },
    {
        "objection": "We already have a provider",
        "response": "That's great you have a system in place. Many of our clients initially worked with other providers but found our approach offered additional benefits. Would you be open to a quick comparison?",
        "category": "competition", 
        "effectiveness": 0.7
    },
    {
        "objection": "It's too expensive",
        "response": "I understand cost is important. Many clients find the ROI makes it worthwhile. Could I share some case studies showing how others have benefited?",
        "category": "price",
        "effectiveness": 0.75
    },
    {
        "objection": "I need to think about it",
        "response": "Of course, take your time. Would it help if I shared some additional information about how this has helped similar businesses in your industry?",
        "category": "hesitation",
        "effectiveness": 0.6
    }
]

# Initialize with default responses
async def initialize_vector_store():
    """Initialize vector store with default responses"""
    for response in DEFAULT_OBJECTION_RESPONSES:
        await vector_store.store_objection_response(
            objection=response["objection"],
            response=response["response"],
            category=response["category"],
            effectiveness=response["effectiveness"]
        )
    logger.info("Vector store initialized with default objection responses")
