"""
Chat Engine for BioSure Analytics.

This module implements the main chat engine that handles intent detection,
query routing, and response generation.
"""
from typing import List, Type, Union
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.services.chat_handlers import (
    QueryHandler,
    TopHCOsHandler,
    ContractTemplatesHandler,
    ContractSimulationHandler,
    PatientStatsHandler,
    PatientOutcomesHandler,
    HCOAddressHandler,
    SurgeonPaperSearchHandler,
    PDFKnowledgeHandler,
    GeneralChatHandler,
)


class ChatEngine:
    """
    Main chat engine that processes user messages and routes them
    to appropriate handlers.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize the chat engine with database connection.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        
        # Register data query handlers in priority order
        # Handlers are checked in order, first match wins
        self.data_handlers: List[Type[QueryHandler]] = [
            TopHCOsHandler,
            HCOAddressHandler,  # HCO address lookup
            SurgeonPaperSearchHandler,  # Surgeon paper search by author
            PDFKnowledgeHandler,  # PDF document queries using Gemini RAG
            ContractSimulationHandler,  # Check simulation before templates (more specific)
            ContractTemplatesHandler,
            PatientOutcomesHandler,  # Check outcomes before general stats (more specific)
            PatientStatsHandler,
            # Future handlers can be added here
        ]
        
        # General chat handler (fallback)
        self.general_handler = GeneralChatHandler(db)
    
    async def process_message(self, message: str) -> Union[str, List[str]]:
        """
        Process a user message and generate an appropriate response.
        
        This method:
        1. Attempts to match the message against data query patterns
        2. If a match is found, routes to the appropriate data handler
        3. Otherwise, falls back to general chat handler
        
        Args:
            message: User's chat message
            
        Returns:
            Generated response - either a single string or a list of strings for multiple messages
        """
        # Try to match against data query handlers
        for handler_class in self.data_handlers:
            # Check if this handler matches the message
            if hasattr(handler_class, 'matches'):
                params = handler_class.matches(message)
                if params is not None:
                    # Create handler instance and process
                    handler = handler_class(self.db)
                    return await handler.handle(params)
        
        # No data query matched, use general chat handler
        return await self.general_handler.handle({"message": message})
    
    def register_handler(self, handler_class: Type[QueryHandler]) -> None:
        """
        Register a new data query handler.
        
        This allows for dynamic extension of the chat engine's capabilities.
        
        Args:
            handler_class: QueryHandler subclass to register
        """
        if handler_class not in self.data_handlers:
            self.data_handlers.append(handler_class)