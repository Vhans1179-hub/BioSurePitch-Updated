"""
Gemini RAG Service for PDF Document Processing.

This module implements the RAG (Retrieval-Augmented Generation) service using
Google's Gemini File API for document processing and querying.

Phase 1 Implementation: Core Gemini File API integration
TODO: Future Phase - Add hybrid approach with local vector DB for PHI data
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

import google.generativeai as genai

from backend.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class BaseRAGService(ABC):
    """
    Abstract base class for RAG services.
    
    This abstraction allows for future migration to hybrid approaches
    (e.g., local vector DB for PHI + Gemini for general documents).
    """
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the RAG service."""
        pass
    
    @abstractmethod
    async def upload_pdf(self, file_path: str, display_name: str) -> Optional[str]:
        """Upload a PDF document."""
        pass
    
    @abstractmethod
    async def query_documents(
        self,
        query: str,
        file_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Query documents with the given query."""
        pass
    
    @abstractmethod
    async def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """List all uploaded files."""
        pass
    
    @abstractmethod
    async def delete_file(self, file_name: str) -> bool:
        """Delete a file from storage."""
        pass


class GeminiRAGService(BaseRAGService):
    """
    Gemini File API implementation of RAG service.
    
    This service uses Google's Gemini File API for document processing,
    leveraging the long context window (up to 2M tokens) for accurate
    document-grounded responses.
    """
    
    def __init__(self):
        """Initialize the Gemini RAG service."""
        self.model = None
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.initialized = False
        
        # File processing configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.processing_timeout = 300  # 5 minutes max for file processing
    
    async def initialize(self) -> bool:
        """
        Initialize the Gemini client with API key.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if not self.api_key:
                logger.error("GEMINI_API_KEY not configured")
                return False
            
            # Configure the Gemini API
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel(self.model_name)
            
            self.initialized = True
            logger.info(f"Gemini RAG service initialized with model: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini RAG service: {str(e)}", exc_info=True)
            return False
    
    async def upload_pdf(self, file_path: str, display_name: str) -> Optional[str]:
        """
        Upload a PDF document to Gemini File API.
        
        Args:
            file_path: Path to the PDF file
            display_name: Display name for the file
            
        Returns:
            str: File name/ID if successful, None otherwise
        """
        if not self.initialized:
            logger.error("Service not initialized. Call initialize() first.")
            return None
        
        try:
            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            if not path.suffix.lower() == '.pdf':
                logger.error(f"File is not a PDF: {file_path}")
                return None
            
            logger.info(f"Uploading PDF: {display_name} from {file_path}")
            
            # Upload file to Gemini
            uploaded_file = genai.upload_file(
                path=str(path),
                display_name=display_name
            )
            
            logger.info(f"File uploaded: {uploaded_file.name}")
            
            # Wait for file to be processed
            file_name = await self.wait_for_file_processing(uploaded_file.name)
            
            if file_name:
                logger.info(f"File ready for use: {file_name}")
                return file_name
            else:
                logger.error(f"File processing failed or timed out: {display_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading PDF {file_path}: {str(e)}", exc_info=True)
            return None
    
    async def wait_for_file_processing(self, file_name: str) -> Optional[str]:
        """
        Wait for a file to be processed by Gemini.
        
        Args:
            file_name: Name/ID of the uploaded file
            
        Returns:
            str: File name if processing successful, None otherwise
        """
        try:
            start_time = time.time()
            
            while True:
                # Check if timeout exceeded
                if time.time() - start_time > self.processing_timeout:
                    logger.error(f"File processing timeout for {file_name}")
                    return None
                
                # Get file status
                file = genai.get_file(file_name)
                
                if file.state.name == "ACTIVE":
                    logger.info(f"File processing complete: {file_name}")
                    return file_name
                elif file.state.name == "FAILED":
                    logger.error(f"File processing failed: {file_name}")
                    return None
                
                # Still processing, wait before checking again
                logger.debug(f"File still processing: {file_name}, state: {file.state.name}")
                time.sleep(self.retry_delay)
                
        except Exception as e:
            logger.error(f"Error waiting for file processing {file_name}: {str(e)}", exc_info=True)
            return None
    
    async def query_documents(
        self,
        query: str,
        file_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Query documents using Gemini with document grounding.
        
        Args:
            query: User's question/query
            file_names: Optional list of specific file names to query.
                       If None, queries all uploaded files.
            
        Returns:
            Dict containing:
                - response: Generated response text
                - sources: List of source documents used
                - success: Boolean indicating success
                - error: Error message if failed
        """
        if not self.initialized:
            return {
                "response": "",
                "sources": [],
                "success": False,
                "error": "Service not initialized"
            }
        
        try:
            # Get files to query
            if file_names:
                files = [genai.get_file(name) for name in file_names]
            else:
                # Query all active files
                all_files = genai.list_files()
                files = [f for f in all_files if f.state.name == "ACTIVE"]
            
            if not files:
                return {
                    "response": "No documents available to query.",
                    "sources": [],
                    "success": True,
                    "error": None
                }
            
            logger.info(f"Querying {len(files)} document(s) with query: {query[:100]}...")
            
            # Construct prompt with document grounding
            prompt_parts = [query]
            prompt_parts.extend(files)
            
            # Generate response
            response = self.model.generate_content(prompt_parts)
            
            # Extract sources from files used
            sources = [
                {
                    "name": f.display_name or f.name,
                    "file_id": f.name
                }
                for f in files
            ]
            
            return {
                "response": response.text,
                "sources": sources,
                "success": True,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}", exc_info=True)
            return {
                "response": "",
                "sources": [],
                "success": False,
                "error": str(e)
            }
    
    async def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """
        List all files uploaded to Gemini.
        
        Returns:
            List of file information dictionaries
        """
        if not self.initialized:
            logger.error("Service not initialized")
            return []
        
        try:
            files = genai.list_files()
            
            file_list = []
            for file in files:
                file_list.append({
                    "name": file.name,
                    "display_name": file.display_name,
                    "mime_type": file.mime_type,
                    "size_bytes": file.size_bytes,
                    "state": file.state.name,
                    "uri": file.uri
                })
            
            logger.info(f"Listed {len(file_list)} files")
            return file_list
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}", exc_info=True)
            return []
    
    async def delete_file(self, file_name: str) -> bool:
        """
        Delete a file from Gemini storage.
        
        Args:
            file_name: Name/ID of the file to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if not self.initialized:
            logger.error("Service not initialized")
            return False
        
        try:
            genai.delete_file(file_name)
            logger.info(f"Deleted file: {file_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_name}: {str(e)}", exc_info=True)
            return False


# Global service instance
# TODO: Consider dependency injection pattern for better testability
_rag_service: Optional[GeminiRAGService] = None


async def get_rag_service() -> GeminiRAGService:
    """
    Get or create the global RAG service instance.
    
    Returns:
        GeminiRAGService: Initialized RAG service instance
    """
    global _rag_service
    
    if _rag_service is None:
        _rag_service = GeminiRAGService()
        await _rag_service.initialize()
    
    return _rag_service