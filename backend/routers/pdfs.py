"""
PDF Management and Query Router

Provides endpoints for:
- POST /api/pdfs/upload - Upload a PDF file
- GET /api/pdfs/list - List all uploaded PDFs
- GET /api/pdfs/gemini-files - List files in Gemini
- POST /api/pdfs/sync - Sync local PDFs to Gemini
- DELETE /api/pdfs/{file_name} - Delete a PDF
- POST /api/pdfs/query - Query PDFs directly
"""
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from backend.models.pdf import (
    PDFUploadResponse,
    PDFListResponse,
    GeminiFilesResponse,
    PDFSyncResponse,
    PDFQueryRequest,
    PDFQueryResponse,
    PDFDeleteResponse,
    PDFMetadata,
    GeminiFileInfo,
    PDFSource
)
from backend.services.gemini_rag_service import get_rag_service
from backend.services.pdf_manager import get_pdf_manager
from backend.config import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/pdfs", tags=["pdfs"])


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    category: str = Form(..., description="Document category: research_papers, policies, contracts, or clinical")
):
    """
    Upload a PDF file to local storage and Gemini File API.
    
    Args:
        file: PDF file to upload
        category: Document category (research_papers, policies, contracts, clinical)
        
    Returns:
        PDFUploadResponse with file metadata and Gemini file info
        
    Raises:
        HTTPException: 400 if invalid file or category, 500 if upload fails
    """
    try:
        # Validate category
        valid_categories = ["research_papers", "policies", "contracts", "clinical"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a PDF"
            )
        
        # Create category directory if it doesn't exist
        storage_path = Path(settings.pdf_storage_path) / category
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # Save file locally
        file_path = storage_path / file.filename
        
        # Check if file already exists
        if file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' already exists in category '{category}'"
            )
        
        # Write file to disk
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Saved PDF to {file_path}")
        
        # Validate PDF
        pdf_manager = get_pdf_manager()
        if not pdf_manager.validate_pdf(str(file_path)):
            # Delete invalid file
            file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file"
            )
        
        # Get file metadata
        file_info = pdf_manager._get_file_info(file_path)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract file metadata"
            )
        
        # Upload to Gemini
        rag_service = await get_rag_service()
        display_name = file_path.stem
        gemini_file_name = await rag_service.upload_pdf(str(file_path), display_name)
        
        if not gemini_file_name:
            logger.warning(f"Failed to upload {file.filename} to Gemini, but saved locally")
            return PDFUploadResponse(
                success=True,
                message=f"File saved locally but failed to upload to Gemini",
                file_metadata=PDFMetadata(**file_info),
                gemini_file=None
            )
        
        # Get Gemini file info
        import google.generativeai as genai
        gemini_file = genai.get_file(gemini_file_name)
        gemini_info = GeminiFileInfo(
            name=gemini_file.name,
            display_name=gemini_file.display_name,
            mime_type=gemini_file.mime_type,
            size_bytes=gemini_file.size_bytes,
            state=gemini_file.state.name,
            uri=gemini_file.uri
        )
        
        logger.info(f"Successfully uploaded {file.filename} to Gemini")
        
        return PDFUploadResponse(
            success=True,
            message=f"File '{file.filename}' uploaded successfully",
            file_metadata=PDFMetadata(**file_info),
            gemini_file=gemini_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload PDF: {str(e)}"
        )


@router.get("/list", response_model=PDFListResponse)
async def list_pdfs(category: Optional[str] = None):
    """
    List all uploaded PDFs from local storage.
    
    Args:
        category: Optional category filter (research_papers, policies, contracts, clinical)
        
    Returns:
        PDFListResponse with list of PDFs and metadata
        
    Raises:
        HTTPException: 500 if listing fails
    """
    try:
        pdf_manager = get_pdf_manager()
        
        # Validate category if provided
        if category and category not in pdf_manager.categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(pdf_manager.categories)}"
            )
        
        # Scan local PDFs
        pdf_files = pdf_manager.scan_local_pdfs(category)
        
        # Convert to PDFMetadata models
        pdf_metadata_list = [PDFMetadata(**pdf) for pdf in pdf_files]
        
        return PDFListResponse(
            pdfs=pdf_metadata_list,
            total=len(pdf_metadata_list),
            category=category
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing PDFs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list PDFs: {str(e)}"
        )


@router.get("/gemini-files", response_model=GeminiFilesResponse)
async def list_gemini_files():
    """
    List all files uploaded to Gemini File API.
    
    Returns:
        GeminiFilesResponse with list of files and their status
        
    Raises:
        HTTPException: 500 if listing fails
    """
    try:
        rag_service = await get_rag_service()
        
        # Get files from Gemini
        files = await rag_service.list_uploaded_files()
        
        # Convert to GeminiFileInfo models
        gemini_files = [GeminiFileInfo(**file) for file in files]
        
        return GeminiFilesResponse(
            files=gemini_files,
            total=len(gemini_files)
        )
        
    except Exception as e:
        logger.error(f"Error listing Gemini files: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Gemini files: {str(e)}"
        )


@router.post("/sync", response_model=PDFSyncResponse)
async def sync_pdfs(
    category: Optional[str] = None,
    force: bool = False
):
    """
    Sync local PDFs to Gemini File API.
    
    Scans local directories and uploads any new or modified PDFs to Gemini.
    
    Args:
        category: Optional category to sync (if None, syncs all categories)
        force: If True, re-uploads all files even if already uploaded
        
    Returns:
        PDFSyncResponse with sync results
        
    Raises:
        HTTPException: 500 if sync fails
    """
    try:
        pdf_manager = get_pdf_manager()
        
        # Validate category if provided
        if category and category not in pdf_manager.categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(pdf_manager.categories)}"
            )
        
        # Perform sync
        results = await pdf_manager.sync_pdfs_to_gemini(category, force)
        
        # Create summary message
        message = (
            f"Sync complete: {results['uploaded']} uploaded, "
            f"{results['skipped']} skipped, {results['failed']} failed"
        )
        
        return PDFSyncResponse(
            uploaded=results["uploaded"],
            skipped=results["skipped"],
            failed=results["failed"],
            errors=results["errors"],
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing PDFs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync PDFs: {str(e)}"
        )


@router.delete("/{file_name}", response_model=PDFDeleteResponse)
async def delete_pdf(file_name: str):
    """
    Delete a PDF from both local storage and Gemini File API.
    
    Args:
        file_name: Name of the file to delete (without path)
        
    Returns:
        PDFDeleteResponse with deletion status
        
    Raises:
        HTTPException: 404 if file not found, 500 if deletion fails
    """
    try:
        pdf_manager = get_pdf_manager()
        rag_service = await get_rag_service()
        
        deleted_from_local = False
        deleted_from_gemini = False
        
        # Search for file in local storage
        local_pdfs = pdf_manager.scan_local_pdfs()
        local_file = next((pdf for pdf in local_pdfs if pdf["name"] == file_name), None)
        
        if local_file:
            # Delete from local storage
            file_path = Path(local_file["path"])
            if file_path.exists():
                file_path.unlink()
                deleted_from_local = True
                logger.info(f"Deleted local file: {file_path}")
        
        # Try to delete from Gemini
        # First, find the Gemini file ID by display name
        gemini_files = await rag_service.list_uploaded_files()
        display_name = Path(file_name).stem
        gemini_file = next(
            (f for f in gemini_files if f["display_name"] == display_name),
            None
        )
        
        if gemini_file:
            deleted_from_gemini = await rag_service.delete_file(gemini_file["name"])
            if deleted_from_gemini:
                logger.info(f"Deleted Gemini file: {gemini_file['name']}")
        
        # Check if anything was deleted
        if not deleted_from_local and not deleted_from_gemini:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{file_name}' not found in local storage or Gemini"
            )
        
        message = []
        if deleted_from_local:
            message.append("local storage")
        if deleted_from_gemini:
            message.append("Gemini")
        
        return PDFDeleteResponse(
            success=True,
            message=f"File '{file_name}' deleted from {' and '.join(message)}",
            deleted_from_local=deleted_from_local,
            deleted_from_gemini=deleted_from_gemini
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete PDF: {str(e)}"
        )


@router.delete("/gemini/{gemini_file_id:path}", response_model=PDFDeleteResponse)
async def delete_gemini_file(gemini_file_id: str):
    """
    Delete a file from Gemini File API only (not local storage).
    
    This is useful for cleaning up Gemini files that don't have local copies.
    
    Args:
        gemini_file_id: Gemini file ID (e.g., 'files/abc123')
        
    Returns:
        PDFDeleteResponse with deletion status
        
    Raises:
        HTTPException: 404 if file not found, 500 if deletion fails
    """
    try:
        rag_service = await get_rag_service()
        
        # Delete from Gemini
        deleted = await rag_service.delete_file(gemini_file_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{gemini_file_id}' not found in Gemini"
            )
        
        logger.info(f"Deleted Gemini file: {gemini_file_id}")
        
        return PDFDeleteResponse(
            success=True,
            message=f"File deleted from Gemini",
            deleted_from_local=False,
            deleted_from_gemini=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Gemini file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Gemini file: {str(e)}"
        )


@router.post("/query", response_model=PDFQueryResponse)
async def query_pdfs(request: PDFQueryRequest):
    """
    Query PDFs directly using Gemini RAG.
    
    This is an alternative to the chat endpoint for direct document queries.
    
    Args:
        request: PDFQueryRequest with query text and optional file names
        
    Returns:
        PDFQueryResponse with generated response and source citations
        
    Raises:
        HTTPException: 500 if query fails
    """
    try:
        rag_service = await get_rag_service()
        
        # Query documents
        result = await rag_service.query_documents(
            query=request.query,
            file_names=request.file_names
        )
        
        # Convert sources to PDFSource models
        sources = [PDFSource(**source) for source in result.get("sources", [])]
        
        return PDFQueryResponse(
            success=result["success"],
            response=result["response"],
            sources=sources,
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error querying PDFs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query PDFs: {str(e)}"
        )