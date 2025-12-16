"""
Chat API endpoints for BioSure Analytics.
"""
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from backend.models.chat import ChatMessageRequest, ChatMessageResponse


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


def generate_contextual_response(message: str) -> str:
    """
    Generate contextual response based on message keywords.
    
    Args:
        message: User message content
        
    Returns:
        Contextual response string based on keywords
    """
    lower_message = message.lower()
    
    # Check for keywords and return appropriate responses
    if "help" in lower_message:
        return "I'm here to help! You can ask me about dashboard features, data insights, or general questions about the platform."
    
    if "dashboard" in lower_message:
        return "The dashboard provides comprehensive analytics including cohort analysis, contract simulation, and ghost radar features. You can navigate between different sections using the sidebar."
    
    if "cohort" in lower_message:
        return "The Cohort Overview shows key metrics like retention rates, engagement scores, and user growth. You can filter by different time periods to analyze trends."
    
    if "contract" in lower_message:
        return "The Contract Simulator allows you to model different contract scenarios and see projected outcomes. It's a powerful tool for planning and forecasting."
    
    if "ghost" in lower_message or "radar" in lower_message:
        return "Ghost Radar helps identify inactive or at-risk users. It uses advanced analytics to detect patterns that might indicate user churn."
    
    if "hello" in lower_message or "hi" in lower_message:
        return "Hello! How can I assist you today?"
    
    if "thank" in lower_message:
        return "You're welcome! Feel free to ask if you need anything else."
    
    # Default response
    return "I understand. Is there anything specific you'd like to know about the dashboard or its features?"


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    Send a chat message and receive a contextual response.
    
    This endpoint accepts a user message and returns a bot response based on
    keyword matching. It maintains session continuity through session_id.
    
    Args:
        request: ChatMessageRequest containing message and optional session_id
        
    Returns:
        ChatMessageResponse with bot response, session_id, and timestamp
        
    Raises:
        HTTPException: If there's an error processing the message
    """
    try:
        # Generate or reuse session_id
        session_id = request.session_id if request.session_id else str(uuid4())
        
        # Generate contextual response based on message content
        response_text = generate_contextual_response(request.message)
        
        # Create response with current timestamp
        response = ChatMessageResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc)
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )