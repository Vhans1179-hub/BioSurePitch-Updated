"""
PDF Manager Utilities.

This module provides helper functions for managing PDF documents,
including scanning local directories, syncing with Gemini, and
extracting metadata.
"""
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

from pypdf import PdfReader

from backend.config import settings
from backend.services.gemini_rag_service import get_rag_service

# Configure logging
logger = logging.getLogger(__name__)


class PDFManager:
    """Manager for PDF document operations."""
    
    def __init__(self):
        """Initialize the PDF manager."""
        self.storage_path = Path(settings.pdf_storage_path)
        self.categories = ["research_papers", "policies", "contracts", "clinical"]
    
    def scan_local_pdfs(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scan local PDF directory for documents.
        
        Args:
            category: Optional category to scan (e.g., 'research_papers').
                     If None, scans all categories.
        
        Returns:
            List of PDF file information dictionaries
        """
        try:
            pdf_files = []
            
            # Determine which directories to scan
            if category:
                if category not in self.categories:
                    logger.warning(f"Unknown category: {category}")
                    return []
                scan_dirs = [self.storage_path / category]
            else:
                scan_dirs = [self.storage_path / cat for cat in self.categories]
            
            # Scan each directory
            for scan_dir in scan_dirs:
                if not scan_dir.exists():
                    logger.warning(f"Directory does not exist: {scan_dir}")
                    continue
                
                # Find all PDF files
                for pdf_path in scan_dir.glob("*.pdf"):
                    try:
                        file_info = self._get_file_info(pdf_path)
                        if file_info:
                            pdf_files.append(file_info)
                    except Exception as e:
                        logger.error(f"Error processing {pdf_path}: {str(e)}")
                        continue
            
            logger.info(f"Found {len(pdf_files)} PDF files")
            return pdf_files
            
        except Exception as e:
            logger.error(f"Error scanning PDFs: {str(e)}", exc_info=True)
            return []
    
    def _get_file_info(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = pdf_path.stat()
            
            # Extract category from path
            category = pdf_path.parent.name
            
            # Calculate file hash for deduplication
            file_hash = self._calculate_file_hash(pdf_path)
            
            return {
                "path": str(pdf_path),
                "name": pdf_path.name,
                "display_name": pdf_path.stem,  # Filename without extension
                "category": category,
                "size_bytes": stat.st_size,
                "modified_time": stat.st_mtime,
                "hash": file_hash
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {pdf_path}: {str(e)}")
            return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex string of file hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    async def sync_pdfs_to_gemini(
        self,
        category: Optional[str] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Sync local PDFs to Gemini File API.
        
        Args:
            category: Optional category to sync. If None, syncs all.
            force: If True, re-uploads all files even if already uploaded
            
        Returns:
            Dictionary with sync results:
                - uploaded: Number of files uploaded
                - skipped: Number of files skipped
                - failed: Number of files that failed
                - errors: List of error messages
        """
        try:
            rag_service = await get_rag_service()
            
            # Get local PDFs
            local_pdfs = self.scan_local_pdfs(category)
            
            if not local_pdfs:
                logger.info("No local PDFs found to sync")
                return {
                    "uploaded": 0,
                    "skipped": 0,
                    "failed": 0,
                    "errors": []
                }
            
            # Get already uploaded files
            uploaded_files = await rag_service.list_uploaded_files()
            uploaded_names = {f["display_name"] for f in uploaded_files}
            
            results = {
                "uploaded": 0,
                "skipped": 0,
                "failed": 0,
                "errors": []
            }
            
            # Upload each PDF
            for pdf_info in local_pdfs:
                display_name = pdf_info["display_name"]
                
                # Skip if already uploaded (unless force=True)
                if not force and display_name in uploaded_names:
                    logger.info(f"Skipping already uploaded file: {display_name}")
                    results["skipped"] += 1
                    continue
                
                # Upload to Gemini
                logger.info(f"Uploading {display_name} from {pdf_info['category']}")
                file_name = await rag_service.upload_pdf(
                    pdf_info["path"],
                    display_name
                )
                
                if file_name:
                    results["uploaded"] += 1
                    logger.info(f"Successfully uploaded: {display_name}")
                else:
                    results["failed"] += 1
                    error_msg = f"Failed to upload: {display_name}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(
                f"Sync complete: {results['uploaded']} uploaded, "
                f"{results['skipped']} skipped, {results['failed']} failed"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error syncing PDFs: {str(e)}", exc_info=True)
            return {
                "uploaded": 0,
                "skipped": 0,
                "failed": 0,
                "errors": [str(e)]
            }
    
    def get_pdf_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Read PDF
            reader = PdfReader(str(path))
            
            # Extract metadata
            metadata = {
                "num_pages": len(reader.pages),
                "file_size": path.stat().st_size,
                "file_name": path.name
            }
            
            # Add PDF metadata if available
            if reader.metadata:
                pdf_meta = reader.metadata
                metadata.update({
                    "title": pdf_meta.get("/Title", ""),
                    "author": pdf_meta.get("/Author", ""),
                    "subject": pdf_meta.get("/Subject", ""),
                    "creator": pdf_meta.get("/Creator", ""),
                    "producer": pdf_meta.get("/Producer", ""),
                    "creation_date": pdf_meta.get("/CreationDate", ""),
                })
            
            # Extract first page text as preview (first 500 chars)
            if len(reader.pages) > 0:
                first_page_text = reader.pages[0].extract_text()
                metadata["preview"] = first_page_text[:500] if first_page_text else ""
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting PDF metadata from {file_path}: {str(e)}", exc_info=True)
            return None
    
    def validate_pdf(self, file_path: str) -> bool:
        """
        Validate that a file is a valid PDF.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        try:
            path = Path(file_path)
            
            # Check file exists
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Check extension
            if path.suffix.lower() != '.pdf':
                logger.error(f"File is not a PDF: {file_path}")
                return False
            
            # Try to read PDF
            reader = PdfReader(str(path))
            
            # Check has pages
            if len(reader.pages) == 0:
                logger.error(f"PDF has no pages: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"PDF validation failed for {file_path}: {str(e)}")
            return False


# Global manager instance
_pdf_manager: Optional[PDFManager] = None


def get_pdf_manager() -> PDFManager:
    """
    Get or create the global PDF manager instance.
    
    Returns:
        PDFManager: PDF manager instance
    """
    global _pdf_manager
    
    if _pdf_manager is None:
        _pdf_manager = PDFManager()
    
    return _pdf_manager