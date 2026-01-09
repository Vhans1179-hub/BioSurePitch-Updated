"""
Chat message models for BioSure Analytics.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4


class ChatMessageRequest(BaseModel):
    """Model for incoming chat messages."""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User message content (1-1000 characters)"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for conversation continuity (UUID format)"
    )
    
    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty after stripping whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("message cannot be empty or only whitespace")
        if len(stripped) > 1000:
            raise ValueError("message cannot exceed 1000 characters")
        return stripped
    
    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate session_id is a valid UUID format if provided."""
        if v is not None:
            # Basic UUID format validation (8-4-4-4-12 hex digits)
            import re
            uuid_pattern = re.compile(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                re.IGNORECASE
            )
            if not uuid_pattern.match(v):
                raise ValueError("session_id must be a valid UUID format")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "What features does the dashboard have?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    }


class ChatMessageResponse(BaseModel):
    """Model for chat API responses."""
    
    response: str = Field(
        ...,
        description="Bot response message"
    )
    session_id: str = Field(
        ...,
        description="Session ID for conversation continuity (UUID)"
    )
    timestamp: datetime = Field(
        ...,
        description="Response timestamp in ISO8601 format"
    )
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        },
        "json_schema_extra": {
            "example": {
                "response": "The dashboard provides comprehensive analytics including cohort analysis, contract simulation, and ghost radar features.",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-15T10:30:00.000Z"
            }
        }
    }


class ChatMultiMessageResponse(BaseModel):
    """Model for chat API responses with multiple messages."""
    
    messages: list[str] = Field(
        ...,
        description="List of bot response messages to be displayed sequentially"
    )
    session_id: str = Field(
        ...,
        description="Session ID for conversation continuity (UUID)"
    )
    timestamp: datetime = Field(
        ...,
        description="Response timestamp in ISO8601 format"
    )
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        },
        "json_schema_extra": {
            "example": {
                "messages": [
                    "Here are the results...",
                    "Would you like to see more?"
                ],
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-15T10:30:00.000Z"
            }
        }
    }