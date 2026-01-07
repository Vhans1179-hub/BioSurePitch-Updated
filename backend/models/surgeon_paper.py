"""
Surgeon Paper data models for BioSure Analytics.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class SurgeonPaperBase(BaseModel):
    """Base surgeon paper model with all fields."""
    
    title: str = Field(..., description="Paper title")
    journal: str = Field(..., description="Journal name")
    author_name: str = Field(..., description="Author name")
    affiliation: str = Field(..., description="Author affiliation")
    website: Optional[str] = Field(None, description="Paper or author website URL")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Advanced Surgical Techniques in Oncology",
                "journal": "Journal of Surgical Oncology",
                "author_name": "Dr. John Smith",
                "affiliation": "Harvard Medical School",
                "website": "https://example.com/paper",
            }
        }
    }


class SurgeonPaperCreate(SurgeonPaperBase):
    """Model for creating a new surgeon paper."""
    pass


class SurgeonPaperInDB(SurgeonPaperBase):
    """Surgeon paper model as stored in database with MongoDB _id."""
    
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        }
    }


class SurgeonPaperResponse(SurgeonPaperBase):
    """Model for API responses."""
    
    id: str = Field(..., alias="_id", description="MongoDB document ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        }
    }


class SurgeonPaperListResponse(BaseModel):
    """Response model for paginated surgeon paper list."""
    
    papers: list[SurgeonPaperResponse]
    total: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "papers": [],
                "total": 13
            }
        }
    }