"""
Chat API endpoints for BioSure Analytics.
"""
from datetime import datetime, timezone
from uuid import uuid4
from typing import Union
from fastapi import APIRouter, HTTPException
from backend.models.chat import ChatMessageRequest, ChatMessageResponse, ChatMultiMessageResponse
from backend.database import get_database
from backend.services.chat_engine import ChatEngine


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/message", response_model=Union[ChatMessageResponse, ChatMultiMessageResponse])
async def send_chat_message(request: ChatMessageRequest):
    """
    Send a chat message and receive a contextual response.
    
    This endpoint accepts a user message and returns a bot response using
    the ChatEngine for intent detection and query routing. It supports both
    general chat queries and data-driven queries (e.g., "show me top 5 HCOs
    with highest ghost patients").
    
    The response can be either a single message (ChatMessageResponse) or
    multiple messages (ChatMultiMessageResponse) depending on the query type.
    
    Args:
        request: ChatMessageRequest containing message and optional session_id
        
    Returns:
        ChatMessageResponse or ChatMultiMessageResponse with bot response(s), session_id, and timestamp
        
    Raises:
        HTTPException: If there's an error processing the message
    """
    try:
        # Generate or reuse session_id
        session_id = request.session_id if request.session_id else str(uuid4())
        
        # Get database connection
        db = await get_database()
        
        # Initialize chat engine
        chat_engine = ChatEngine(db)
        
        # Process message through chat engine
        response_data = await chat_engine.process_message(request.message)
        
        # Check if response is a list (multiple messages) or string (single message)
        if isinstance(response_data, list):
            # Multiple messages - return ChatMultiMessageResponse
            response = ChatMultiMessageResponse(
                messages=response_data,
                session_id=session_id,
                timestamp=datetime.now(timezone.utc)
            )
        else:
            # Single message - return ChatMessageResponse
            response = ChatMessageResponse(
                response=response_data,
                session_id=session_id,
                timestamp=datetime.now(timezone.utc)
            )
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )