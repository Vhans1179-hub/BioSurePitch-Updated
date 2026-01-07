"""
Surgeon Paper Service for BioSure Analytics.

This module provides services for searching and retrieving surgeon paper data.
"""
import logging
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

# Configure logging
logger = logging.getLogger(__name__)


class SurgeonPaperService:
    """Service class for surgeon paper operations."""
    
    @staticmethod
    async def search_by_author(
        db: AsyncIOMotorDatabase,
        author_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for surgeon papers by author name (case-insensitive, partial match).
        
        Args:
            db: MongoDB database instance
            author_name: Author name to search for (partial match supported)
            limit: Maximum number of results to return (default: 20)
            
        Returns:
            List of surgeon paper documents matching the search criteria
        """
        try:
            logger.info(f"Searching surgeon papers for author: {author_name}")
            
            # Create case-insensitive regex pattern for partial matching
            search_pattern = {"$regex": author_name, "$options": "i"}
            
            # Query the surgeon_papers collection
            cursor = db.surgeon_papers.find(
                {"author_name": search_pattern}
            ).limit(limit)
            
            # Convert cursor to list
            papers = await cursor.to_list(length=limit)
            
            logger.info(f"Found {len(papers)} papers for author: {author_name}")
            
            return papers
            
        except Exception as e:
            logger.error(f"Error searching surgeon papers by author '{author_name}': {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    async def get_all_papers(
        db: AsyncIOMotorDatabase,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all surgeon papers from the database.
        
        Args:
            db: MongoDB database instance
            limit: Maximum number of results to return (default: 100)
            
        Returns:
            List of all surgeon paper documents
        """
        try:
            logger.info(f"Fetching all surgeon papers (limit: {limit})")
            
            cursor = db.surgeon_papers.find().limit(limit)
            papers = await cursor.to_list(length=limit)
            
            logger.info(f"Retrieved {len(papers)} surgeon papers")
            
            return papers
            
        except Exception as e:
            logger.error(f"Error fetching all surgeon papers: {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    async def get_paper_count(db: AsyncIOMotorDatabase) -> int:
        """
        Get the total count of surgeon papers in the database.
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Total number of surgeon papers
        """
        try:
            count = await db.surgeon_papers.count_documents({})
            logger.info(f"Total surgeon papers in database: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting surgeon papers: {str(e)}", exc_info=True)
            return 0