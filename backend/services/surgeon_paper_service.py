"""
Surgeon Paper Service for BioSure Analytics.

This module provides services for searching and retrieving surgeon paper data
from both internal and external collections.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

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
        This searches the external surgeon_papers collection.
        
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
    async def search_internal_by_author(
        db: AsyncIOMotorDatabase,
        author_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for surgeon papers by author name in the internal collection.
        
        Args:
            db: MongoDB database instance
            author_name: Author name to search for (partial match supported)
            limit: Maximum number of results to return (default: 20)
            
        Returns:
            List of internal surgeon paper documents matching the search criteria
        """
        try:
            logger.info(f"Searching internal surgeon papers for author: {author_name}")
            
            # Create case-insensitive regex pattern for partial matching
            search_pattern = {"$regex": author_name, "$options": "i"}
            
            # Query the internal_surgeon_papers collection
            cursor = db.internal_surgeon_papers.find(
                {"author_name": search_pattern}
            ).limit(limit)
            
            # Convert cursor to list
            papers = await cursor.to_list(length=limit)
            
            logger.info(f"Found {len(papers)} internal papers for author: {author_name}")
            
            return papers
            
        except Exception as e:
            logger.error(f"Error searching internal surgeon papers by author '{author_name}': {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    async def search_both_collections(
        db: AsyncIOMotorDatabase,
        author_name: str,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Search for surgeon papers by author in both internal and external collections.
        
        Args:
            db: MongoDB database instance
            author_name: Author name to search for
            limit: Maximum number of results per collection
            
        Returns:
            Tuple of (internal_papers, external_papers)
        """
        internal_papers = await SurgeonPaperService.search_internal_by_author(db, author_name, limit)
        external_papers = await SurgeonPaperService.search_by_author(db, author_name, limit)
        
        return internal_papers, external_papers
    
    @staticmethod
    def compare_papers(
        internal_paper: Dict[str, Any],
        external_paper: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two papers and identify differences.
        
        Args:
            internal_paper: Paper from internal collection
            external_paper: Paper from external collection
            
        Returns:
            Dictionary with comparison results including:
            - has_differences: bool
            - differences: dict of field differences
            - missing_fields: list of fields present in external but not internal
        """
        differences = {}
        missing_fields = []
        
        # Fields to compare
        compare_fields = ["title", "journal", "author_name", "affiliation", "website", "address", "email"]
        
        for field in compare_fields:
            internal_value = internal_paper.get(field, "").strip() if internal_paper.get(field) else None
            external_value = external_paper.get(field, "").strip() if external_paper.get(field) else None
            
            # Check if field is missing in internal but present in external
            if not internal_value and external_value:
                missing_fields.append(field)
                differences[field] = {
                    "internal": internal_value,
                    "external": external_value,
                    "status": "missing"
                }
            # Check if values differ
            elif internal_value != external_value and external_value:
                differences[field] = {
                    "internal": internal_value,
                    "external": external_value,
                    "status": "different"
                }
        
        return {
            "has_differences": len(differences) > 0,
            "differences": differences,
            "missing_fields": missing_fields
        }
    
    @staticmethod
    async def update_internal_paper(
        db: AsyncIOMotorDatabase,
        paper_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update an internal surgeon paper with new data.
        
        Args:
            db: MongoDB database instance
            paper_id: The _id of the paper to update
            update_data: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            from bson import ObjectId
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db.internal_surgeon_papers.update_one(
                {"_id": ObjectId(paper_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Successfully updated internal paper {paper_id}")
                return True
            else:
                logger.warning(f"No changes made to internal paper {paper_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating internal paper {paper_id}: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    async def add_to_internal_collection(
        db: AsyncIOMotorDatabase,
        paper_data: Dict[str, Any]
    ) -> bool:
        """
        Add a new paper to the internal collection.
        
        Args:
            db: MongoDB database instance
            paper_data: Dictionary of paper data
            
        Returns:
            True if insertion successful, False otherwise
        """
        try:
            # Add timestamps
            paper_data["created_at"] = datetime.utcnow()
            paper_data["updated_at"] = datetime.utcnow()
            
            result = await db.internal_surgeon_papers.insert_one(paper_data)
            
            if result.inserted_id:
                logger.info(f"Successfully added paper to internal collection: {result.inserted_id}")
                return True
            else:
                logger.warning("Failed to add paper to internal collection")
                return False
                
        except Exception as e:
            logger.error(f"Error adding paper to internal collection: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    async def get_all_papers(
        db: AsyncIOMotorDatabase,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all surgeon papers from the external database.
        
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
        Get the total count of surgeon papers in the external database.
        
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
    
    @staticmethod
    async def get_internal_paper_count(db: AsyncIOMotorDatabase) -> int:
        """
        Get the total count of surgeon papers in the internal database.
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Total number of internal surgeon papers
        """
        try:
            count = await db.internal_surgeon_papers.count_documents({})
            logger.info(f"Total internal surgeon papers in database: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting internal surgeon papers: {str(e)}", exc_info=True)
            return 0