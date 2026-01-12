"""
Pydantic models for PDF management endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PDFMetadata(BaseModel):
    """Metadata for a PDF file."""
    name: str = Field(..., description="File name")
    display_name: str = Field(..., description="Display name (without extension)")
    category: str = Field(..., description="Document category")
    size_bytes: int = Field(..., description="File size in bytes")
    modified_time: float = Field(..., description="Last modified timestamp")
    hash: str = Field(..., description="SHA-256 hash of file")
    path: str = Field(..., description="File path")


class GeminiFileInfo(BaseModel):
    """Information about a file in Gemini."""
    name: str = Field(..., description="Gemini file ID")
    display_name: str = Field(..., description="Display name")
    mime_type: str = Field(..., description="MIME type")
    size_bytes: int = Field(..., description="File size in bytes")
    state: str = Field(..., description="Processing state (PROCESSING, ACTIVE, FAILED)")
    uri: str = Field(..., description="File URI")


class PDFUploadResponse(BaseModel):
    """Response after uploading a PDF."""
    success: bool = Field(..., description="Whether upload was successful")
    message: str = Field(..., description="Status message")
    file_metadata: Optional[PDFMetadata] = Field(None, description="Local file metadata")
    gemini_file: Optional[GeminiFileInfo] = Field(None, description="Gemini file information")


class PDFListResponse(BaseModel):
    """Response containing list of PDFs."""
    pdfs: List[PDFMetadata] = Field(..., description="List of PDF files")
    total: int = Field(..., description="Total number of PDFs")
    category: Optional[str] = Field(None, description="Filtered category if applicable")


class GeminiFilesResponse(BaseModel):
    """Response containing list of files in Gemini."""
    files: List[GeminiFileInfo] = Field(..., description="List of files in Gemini")
    total: int = Field(..., description="Total number of files")


class PDFSyncResponse(BaseModel):
    """Response from PDF sync operation."""
    uploaded: int = Field(..., description="Number of files uploaded")
    skipped: int = Field(..., description="Number of files skipped")
    failed: int = Field(..., description="Number of files that failed")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    message: str = Field(..., description="Summary message")


class PDFQueryRequest(BaseModel):
    """Request to query PDFs."""
    query: str = Field(..., description="Query text", min_length=1)
    file_names: Optional[List[str]] = Field(None, description="Optional list of specific file IDs to query")


class PDFSource(BaseModel):
    """Source document information."""
    name: str = Field(..., description="Document name")
    file_id: str = Field(..., description="Gemini file ID")


class PDFQueryResponse(BaseModel):
    """Response from PDF query."""
    success: bool = Field(..., description="Whether query was successful")
    response: str = Field(..., description="Generated response text")
    sources: List[PDFSource] = Field(default_factory=list, description="Source documents used")
    error: Optional[str] = Field(None, description="Error message if failed")


class PDFDeleteResponse(BaseModel):
    """Response from PDF deletion."""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")
    deleted_from_local: bool = Field(..., description="Whether deleted from local storage")
    deleted_from_gemini: bool = Field(..., description="Whether deleted from Gemini")